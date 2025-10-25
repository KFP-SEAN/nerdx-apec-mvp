"""
Helios Economic Router

Intelligent model selection between Claude Opus and Sonnet based on:
1. Task complexity analysis
2. Current budget constraints
3. Historical performance data
4. Economic cost-benefit optimization

Key Features:
- Task complexity scoring
- Dynamic Opus/Sonnet routing
- Performance-based learning
- Cost-efficiency optimization
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import re

from models.helios.usage_models import (
    ModelType,
    TaskResourceRequest,
    BudgetStatus
)

logger = logging.getLogger(__name__)


class TaskComplexity(str, Enum):
    """Task complexity levels"""
    TRIVIAL = "trivial"          # 1-2 points
    SIMPLE = "simple"            # 3-4 points
    MODERATE = "moderate"        # 5-6 points
    COMPLEX = "complex"          # 7-8 points
    VERY_COMPLEX = "very_complex"  # 9-10 points


class EconomicRouter:
    """
    Economic routing engine for Opus/Sonnet selection

    Decision factors (weighted):
    1. Task complexity (40%) - Intrinsic task difficulty
    2. Budget availability (30%) - Current budget constraints
    3. Historical performance (20%) - Past success rates
    4. User priority (10%) - Explicit priority settings
    """

    def __init__(self):
        """Initialize Economic Router"""
        self.complexity_weights = {
            # Task type patterns
            "task_type": {
                "prd_generation": 7,      # PRD requires deep thinking
                "code_generation": 8,     # Code requires precision
                "code_review": 6,         # Review requires analysis
                "documentation": 4,       # Docs are simpler
                "testing": 5,             # Testing is moderate
                "refactoring": 7,         # Refactoring requires insight
            },

            # Complexity indicators in prompts
            "keywords": {
                "complex": 2, "complicated": 2, "sophisticated": 2,
                "advanced": 2, "intricate": 2,
                "simple": -1, "basic": -1, "straightforward": -1,
                "multi-step": 2, "multi-stage": 2,
                "comprehensive": 1, "detailed": 1,
                "quick": -1, "simple": -1, "minor": -1,
            },

            # Estimated effort
            "estimated_messages": {
                "1-5": 2,      # Short tasks
                "6-20": 4,     # Medium tasks
                "21-50": 6,    # Long tasks
                "51+": 8,      # Very long tasks
            }
        }

        # Performance tracking (task_type -> {model -> success_rate})
        self.performance_history: Dict[str, Dict[str, float]] = {}

        # Economic thresholds
        self.opus_threshold_score = 6.5  # Score >= 6.5 suggests Opus
        self.sonnet_threshold_score = 4.5  # Score < 4.5 suggests Sonnet
        # 4.5 <= score < 6.5 is the hybrid zone

        logger.info("Economic Router initialized")

    def analyze_task_complexity(self, request: TaskResourceRequest) -> tuple[float, TaskComplexity]:
        """
        Analyze task complexity and return a score (1-10)

        Args:
            request: Task resource request

        Returns:
            Tuple of (complexity_score, complexity_level)
        """
        score = 5.0  # Start at medium

        # 1. Task type analysis (40% weight)
        agent_type = request.agent_type.lower()
        for pattern, weight in self.complexity_weights["task_type"].items():
            if pattern in agent_type:
                score += (weight - 5) * 0.4
                logger.debug(f"Task type '{agent_type}' matched '{pattern}': +{(weight - 5) * 0.4}")
                break

        # 2. Keyword analysis in task description (20% weight)
        # (This would analyze the prompt if available, for now using defaults)
        # In real implementation, we'd analyze request context

        # 3. Estimated effort (30% weight)
        messages = request.estimated_messages
        if messages <= 5:
            score += (2 - 5) * 0.3
        elif messages <= 20:
            score += (4 - 5) * 0.3
        elif messages <= 50:
            score += (6 - 5) * 0.3
        else:
            score += (8 - 5) * 0.3

        # 4. Explicit priority signal (10% weight)
        # High priority often indicates complexity
        if request.priority >= 8:
            score += 1.0 * 0.1
        elif request.priority <= 3:
            score -= 1.0 * 0.1

        # Clamp score to 1-10 range
        score = max(1.0, min(10.0, score))

        # Determine complexity level
        if score < 3:
            complexity = TaskComplexity.TRIVIAL
        elif score < 5:
            complexity = TaskComplexity.SIMPLE
        elif score < 7:
            complexity = TaskComplexity.MODERATE
        elif score < 9:
            complexity = TaskComplexity.COMPLEX
        else:
            complexity = TaskComplexity.VERY_COMPLEX

        logger.info(f"Task complexity analysis: score={score:.2f}, level={complexity}")
        return score, complexity

    def recommend_model(
        self,
        request: TaskResourceRequest,
        budget_status: BudgetStatus,
        force_constraints: bool = True
    ) -> tuple[ModelType, float, str]:
        """
        Recommend optimal model based on economic analysis

        Args:
            request: Task resource request
            budget_status: Current budget status
            force_constraints: Whether to enforce budget constraints

        Returns:
            Tuple of (recommended_model, confidence, reasoning)
        """
        # 1. Analyze task complexity
        complexity_score, complexity_level = self.analyze_task_complexity(request)

        # 2. Check if Opus is explicitly required
        if request.requires_opus:
            return (
                ModelType.OPUS,
                1.0,
                f"Opus explicitly required (complexity: {complexity_level})"
            )

        # 3. Budget constraint analysis
        budget_factor = self._analyze_budget_constraints(budget_status)

        # 4. Historical performance analysis
        performance_factor = self._analyze_historical_performance(request.agent_type)

        # 5. Compute weighted decision score
        decision_score = (
            complexity_score * 0.4 +
            budget_factor * 0.3 +
            performance_factor * 0.2 +
            request.priority * 0.1
        )

        logger.debug(f"Decision factors: complexity={complexity_score:.2f}, "
                    f"budget={budget_factor:.2f}, performance={performance_factor:.2f}, "
                    f"priority={request.priority}")

        # 6. Make recommendation
        if decision_score >= self.opus_threshold_score:
            # Recommend Opus
            if force_constraints and budget_status.is_throttling:
                # Budget throttling - recommend Sonnet instead
                return (
                    ModelType.SONNET,
                    0.7,
                    f"Opus recommended (score={decision_score:.2f}) but throttled to Sonnet due to budget"
                )
            else:
                confidence = min(1.0, (decision_score - self.opus_threshold_score) / 3.5 + 0.6)
                return (
                    ModelType.OPUS,
                    confidence,
                    f"Opus recommended: {complexity_level} task (score={decision_score:.2f})"
                )

        elif decision_score <= self.sonnet_threshold_score:
            # Recommend Sonnet
            confidence = min(1.0, (self.sonnet_threshold_score - decision_score) / 3.5 + 0.6)
            return (
                ModelType.SONNET,
                confidence,
                f"Sonnet sufficient: {complexity_level} task (score={decision_score:.2f})"
            )

        else:
            # Hybrid zone - prefer Sonnet for cost efficiency unless high complexity
            if complexity_score >= 7.0 and not budget_status.is_throttling:
                return (
                    ModelType.OPUS,
                    0.6,
                    f"Hybrid zone: Opus preferred for {complexity_level} task (score={decision_score:.2f})"
                )
            else:
                return (
                    ModelType.SONNET,
                    0.7,
                    f"Hybrid zone: Sonnet for cost efficiency (score={decision_score:.2f})"
                )

    def _analyze_budget_constraints(self, budget_status: BudgetStatus) -> float:
        """
        Analyze current budget constraints

        Returns score 0-10 where:
        - 10 = abundant budget, prefer Opus
        - 5 = moderate budget
        - 0 = tight budget, prefer Sonnet
        """
        if not budget_status.current_window:
            return 5.0

        usage_pct = budget_status.current_window.get_usage_percentage()

        # Map usage percentage to budget factor (inverse relationship)
        if usage_pct < 40:
            # Abundant budget
            return 9.0
        elif usage_pct < 60:
            # Good budget
            return 7.0
        elif usage_pct < 80:
            # Moderate budget
            return 5.0
        elif usage_pct < 95:
            # Tight budget
            return 2.0
        else:
            # Critical budget
            return 0.0

    def _analyze_historical_performance(self, agent_type: str) -> float:
        """
        Analyze historical performance for this agent type

        Returns score 0-10 where:
        - 10 = Opus historically much better
        - 5 = Similar performance
        - 0 = Sonnet historically sufficient
        """
        if agent_type not in self.performance_history:
            return 5.0  # No data, neutral

        history = self.performance_history[agent_type]
        opus_success = history.get("opus", 0.0)
        sonnet_success = history.get("sonnet", 0.0)

        # If both have similar success rates, prefer Sonnet (cost efficiency)
        diff = opus_success - sonnet_success

        if diff > 0.2:
            # Opus significantly better
            return 8.0
        elif diff > 0.1:
            # Opus moderately better
            return 6.5
        elif diff > -0.1:
            # Similar performance
            return 5.0
        elif diff > -0.2:
            # Sonnet moderately better
            return 3.5
        else:
            # Sonnet significantly better (rare but possible for simple tasks)
            return 2.0

    def record_task_outcome(
        self,
        agent_type: str,
        model_used: ModelType,
        success: bool,
        complexity_score: float
    ):
        """
        Record task outcome for learning

        Args:
            agent_type: Type of agent
            model_used: Which model was used
            success: Whether task succeeded
            complexity_score: Complexity score of the task
        """
        if agent_type not in self.performance_history:
            self.performance_history[agent_type] = {
                "opus": 0.5,  # Start at 50% assumed success
                "sonnet": 0.5
            }

        model_key = "opus" if model_used == ModelType.OPUS else "sonnet"
        current_rate = self.performance_history[agent_type][model_key]

        # Update with exponential moving average (alpha = 0.2)
        new_value = 1.0 if success else 0.0
        updated_rate = current_rate * 0.8 + new_value * 0.2

        self.performance_history[agent_type][model_key] = updated_rate

        logger.info(f"Updated performance history for {agent_type}/{model_key}: "
                   f"{current_rate:.3f} -> {updated_rate:.3f}")

    def get_routing_stats(self) -> Dict[str, Any]:
        """
        Get routing statistics

        Returns:
            Dictionary with routing stats and performance history
        """
        return {
            "performance_history": self.performance_history,
            "thresholds": {
                "opus_threshold": self.opus_threshold_score,
                "sonnet_threshold": self.sonnet_threshold_score,
            },
            "complexity_weights": self.complexity_weights
        }

    def explain_decision(
        self,
        request: TaskResourceRequest,
        budget_status: BudgetStatus
    ) -> Dict[str, Any]:
        """
        Provide detailed explanation of routing decision

        Args:
            request: Task resource request
            budget_status: Current budget status

        Returns:
            Detailed explanation dictionary
        """
        complexity_score, complexity_level = self.analyze_task_complexity(request)
        budget_factor = self._analyze_budget_constraints(budget_status)
        performance_factor = self._analyze_historical_performance(request.agent_type)

        recommended_model, confidence, reasoning = self.recommend_model(
            request, budget_status, force_constraints=True
        )

        decision_score = (
            complexity_score * 0.4 +
            budget_factor * 0.3 +
            performance_factor * 0.2 +
            request.priority * 0.1
        )

        return {
            "recommended_model": recommended_model.value,
            "confidence": confidence,
            "reasoning": reasoning,
            "complexity": {
                "score": complexity_score,
                "level": complexity_level.value
            },
            "factors": {
                "complexity_score": complexity_score,
                "complexity_weight": 0.4,
                "budget_factor": budget_factor,
                "budget_weight": 0.3,
                "performance_factor": performance_factor,
                "performance_weight": 0.2,
                "priority": request.priority,
                "priority_weight": 0.1
            },
            "decision_score": decision_score,
            "thresholds": {
                "opus": self.opus_threshold_score,
                "sonnet": self.sonnet_threshold_score
            },
            "budget_status": {
                "usage_percentage": budget_status.current_window.get_usage_percentage() if budget_status.current_window else 0,
                "is_throttling": budget_status.is_throttling,
                "budget_health": budget_status.budget_health
            }
        }
