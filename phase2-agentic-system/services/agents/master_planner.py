"""
Master Planner Agent - Orchestrator & Coordinator
Phase 3A: Planner-Executor-Critic Architecture

Capabilities:
- Goal decomposition into tasks
- Multi-agent workflow orchestration
- Task dependency management
- Result evaluation & feedback (Critic)
- Continuous learning & optimization
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
import json
import asyncio

from .base_agent import BaseAgent, AgentCapability, AgentResponse
from .zeitgeist_agent import get_zeitgeist_agent
from .bard_agent import get_bard_agent

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GoalStatus(str, Enum):
    """Goal status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class Task(BaseModel):
    """Individual task"""
    task_id: str
    goal_id: str
    agent_type: str  # zeitgeist, bard, alchemist, etc.
    task_type: str   # analyze_trends, generate_story, etc.
    parameters: Dict[str, Any]
    dependencies: List[str] = []  # Task IDs that must complete first
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retries: int = 0
    max_retries: int = 2


class Goal(BaseModel):
    """High-level goal to achieve"""
    goal_id: str
    title: str
    description: str
    objective: str  # launch_product, create_campaign, analyze_market, etc.
    parameters: Dict[str, Any]
    tasks: List[Task] = []
    status: GoalStatus = GoalStatus.ACTIVE
    confidence: float = 0.0
    created_at: datetime = datetime.utcnow()
    target_completion: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = {}


class WorkflowTemplate(BaseModel):
    """Pre-defined workflow templates"""
    template_id: str
    name: str
    description: str
    objective: str
    task_sequence: List[Dict[str, Any]]  # Template task definitions


class CriticFeedback(BaseModel):
    """Critic evaluation of task results"""
    task_id: str
    quality_score: float  # 0.0-1.0
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    approved: bool
    requires_revision: bool = False


class MasterPlanner(BaseAgent):
    """
    Master Planner - Orchestration Engine

    Implements the Planner-Executor-Critic model:

    1. **PLANNER**: Breaks down high-level goals into tasks
    2. **EXECUTOR**: Routes tasks to specialized agents
    3. **CRITIC**: Evaluates results and provides feedback

    Capabilities:
    - Goal management & decomposition
    - Task scheduling & dependency management
    - Multi-agent coordination
    - Quality control & feedback loops
    - Learning from past executions
    """

    def __init__(self, agent_id: str = "master-planner-001", world_model_url: Optional[str] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="master_planner",
            capabilities=[
                AgentCapability.COORDINATION,
                AgentCapability.ANALYSIS,
                AgentCapability.OPTIMIZATION
            ],
            world_model_url=world_model_url
        )

        # Active goals and tasks
        self.active_goals: Dict[str, Goal] = {}
        self.completed_goals: Dict[str, Goal] = {}

        # Agent registry
        self.agents = {}

        # Workflow templates
        self.workflow_templates = self._load_workflow_templates()

    async def initialize(self):
        """Initialize planner and agents"""
        logger.info("Initializing Master Planner")

        # Initialize specialized agents
        self.agents["zeitgeist"] = get_zeitgeist_agent(self.world_model_url)
        self.agents["bard"] = get_bard_agent(self.world_model_url)

        logger.info(f"Loaded {len(self.agents)} specialized agents")

    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        parameters: Dict[str, Any]
    ) -> AgentResponse:
        """
        Execute planner task

        Task Types:
        - create_goal: Create new goal
        - execute_goal: Execute goal workflow
        - get_goal_status: Check goal progress
        - cancel_goal: Cancel active goal
        - evaluate_task: Critic evaluation
        """
        start_time = datetime.utcnow()

        try:
            if task_type == "create_goal":
                result = await self.create_goal(parameters)
            elif task_type == "execute_goal":
                result = await self.execute_goal(parameters)
            elif task_type == "get_goal_status":
                result = await self.get_goal_status(parameters)
            elif task_type == "cancel_goal":
                result = await self.cancel_goal(parameters)
            elif task_type == "evaluate_task":
                result = await self.evaluate_task_result(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return self.create_response(
                task_id=task_id,
                status="success",
                confidence=result.get("confidence", 0.9),
                result=result,
                processing_time_ms=int(processing_time)
            )

        except Exception as e:
            logger.error(f"Master Planner task {task_id} failed: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return self.create_response(
                task_id=task_id,
                status="failed",
                confidence=0.0,
                result={},
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )

    async def create_goal(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and decompose goal into tasks

        Parameters:
            - title: Goal title
            - description: Goal description
            - objective: Goal type (launch_product, create_campaign, etc.)
            - parameters: Objective-specific parameters
            - use_template: Use predefined workflow template (optional)
            - target_completion_days: Days to complete (optional)

        Returns:
            Created goal with task breakdown
        """
        self.validate_capability(AgentCapability.COORDINATION)

        title = parameters.get("title", "Untitled Goal")
        description = parameters.get("description", "")
        objective = parameters.get("objective", "general")
        obj_parameters = parameters.get("parameters", {})
        use_template = parameters.get("use_template")
        target_days = parameters.get("target_completion_days", 14)

        logger.info(f"Creating goal: {title} (objective: {objective})")

        # Generate goal ID
        goal_id = f"goal-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        # Decompose goal into tasks
        if use_template and use_template in self.workflow_templates:
            tasks = self._apply_workflow_template(
                goal_id,
                use_template,
                obj_parameters
            )
        else:
            tasks = await self._decompose_goal_into_tasks(
                goal_id,
                objective,
                obj_parameters
            )

        # Create goal object
        goal = Goal(
            goal_id=goal_id,
            title=title,
            description=description,
            objective=objective,
            parameters=obj_parameters,
            tasks=tasks,
            status=GoalStatus.ACTIVE,
            target_completion=datetime.utcnow() + timedelta(days=target_days)
        )

        # Store goal
        self.active_goals[goal_id] = goal

        logger.info(f"Goal {goal_id} created with {len(tasks)} tasks")

        return {
            "goal": goal.model_dump(),
            "total_tasks": len(tasks),
            "confidence": 0.9
        }

    async def execute_goal(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute goal workflow

        Parameters:
            - goal_id: Goal to execute
            - async_mode: Execute tasks asynchronously (default: True)

        Returns:
            Execution results
        """
        self.validate_capability(AgentCapability.COORDINATION)

        goal_id = parameters.get("goal_id")
        async_mode = parameters.get("async_mode", True)

        if goal_id not in self.active_goals:
            raise ValueError(f"Goal {goal_id} not found")

        goal = self.active_goals[goal_id]

        logger.info(f"Executing goal: {goal.title} ({len(goal.tasks)} tasks)")

        # Execute tasks based on dependencies
        if async_mode:
            results = await self._execute_tasks_async(goal)
        else:
            results = await self._execute_tasks_sequential(goal)

        # Update goal status
        all_completed = all(t.status == TaskStatus.COMPLETED for t in goal.tasks)
        any_failed = any(t.status == TaskStatus.FAILED for t in goal.tasks)

        if all_completed:
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.utcnow()
            goal.results = results

            # Move to completed goals
            self.completed_goals[goal_id] = goal
            del self.active_goals[goal_id]

            logger.info(f"Goal {goal_id} completed successfully")

        elif any_failed:
            logger.warning(f"Goal {goal_id} has failed tasks")

        return {
            "goal_id": goal_id,
            "status": goal.status,
            "completed_tasks": sum(1 for t in goal.tasks if t.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for t in goal.tasks if t.status == TaskStatus.FAILED),
            "results": results,
            "confidence": goal.confidence
        }

    async def get_goal_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get goal execution status"""

        goal_id = parameters.get("goal_id")

        # Check active goals first
        if goal_id in self.active_goals:
            goal = self.active_goals[goal_id]
        elif goal_id in self.completed_goals:
            goal = self.completed_goals[goal_id]
        else:
            raise ValueError(f"Goal {goal_id} not found")

        task_statuses = {}
        for task in goal.tasks:
            task_statuses[task.task_id] = task.status

        return {
            "goal": goal.model_dump(),
            "task_statuses": task_statuses,
            "progress_percentage": self._calculate_progress(goal)
        }

    async def cancel_goal(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel active goal"""

        goal_id = parameters.get("goal_id")

        if goal_id not in self.active_goals:
            raise ValueError(f"Goal {goal_id} not found or already completed")

        goal = self.active_goals[goal_id]
        goal.status = GoalStatus.CANCELLED

        # Move to completed (cancelled) goals
        self.completed_goals[goal_id] = goal
        del self.active_goals[goal_id]

        logger.info(f"Goal {goal_id} cancelled")

        return {
            "goal_id": goal_id,
            "status": "cancelled",
            "cancelled_at": datetime.utcnow().isoformat()
        }

    async def evaluate_task_result(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate task result (Critic function)

        Parameters:
            - task_id: Task to evaluate
            - result: Task result
            - quality_threshold: Minimum acceptable quality (default: 0.7)

        Returns:
            Critic feedback
        """
        self.validate_capability(AgentCapability.ANALYSIS)

        task_id = parameters.get("task_id")
        result = parameters.get("result", {})
        quality_threshold = parameters.get("quality_threshold", 0.7)

        logger.info(f"Evaluating task {task_id}")

        # Use Claude to evaluate quality
        feedback = await self._critic_evaluate(task_id, result, quality_threshold)

        return {
            "feedback": feedback.model_dump(),
            "approved": feedback.approved,
            "quality_score": feedback.quality_score
        }

    # Helper methods

    async def _decompose_goal_into_tasks(
        self,
        goal_id: str,
        objective: str,
        parameters: Dict[str, Any]
    ) -> List[Task]:
        """
        Decompose goal into tasks using Claude

        This is the PLANNER function - intelligent task decomposition
        """

        decomposition_prompt = f"""
You are a strategic planner for an AI-powered CPG brand (NERD).

Decompose this goal into a sequence of tasks:

**Objective**: {objective}
**Parameters**: {json.dumps(parameters, indent=2)}

**Available Agents**:
1. Zeitgeist Agent (Market Analyst)
   - analyze_trends: Detect market trends
   - identify_opportunities: Find product opportunities
   - generate_weekly_report: Create trend report
   - analyze_platform_data: Analyze NERDX platform

2. Bard Agent (Creative Director)
   - generate_brand_story: Create brand narrative
   - create_campaign: Full campaign planning
   - atomize_content: Content atomization
   - generate_content_piece: Single content piece
   - influencer_brief: Collaboration guidelines

Create a task sequence that:
1. Follows logical dependencies (e.g., trends → opportunities → products → campaigns)
2. Assigns tasks to appropriate agents
3. Sets priorities
4. Defines clear parameters for each task

Return as JSON array:
[
    {{
        "agent_type": "zeitgeist",
        "task_type": "analyze_trends",
        "parameters": {{}},
        "dependencies": [],
        "priority": "high"
    }},
    ...
]
"""

        try:
            response = await self.call_claude(
                prompt=decomposition_prompt,
                system_prompt="You are an expert in strategic planning and task decomposition."
            )

            # Parse task sequence
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                tasks_data = json.loads(json_match.group(1))
            else:
                tasks_data = json.loads(response)

            # Convert to Task objects
            tasks = []
            for i, task_data in enumerate(tasks_data):
                task = Task(
                    task_id=f"{goal_id}-task-{i:03d}",
                    goal_id=goal_id,
                    agent_type=task_data.get("agent_type", "zeitgeist"),
                    task_type=task_data.get("task_type", "analyze_trends"),
                    parameters=task_data.get("parameters", {}),
                    dependencies=task_data.get("dependencies", []),
                    priority=TaskPriority(task_data.get("priority", "medium"))
                )
                tasks.append(task)

            return tasks

        except Exception as e:
            logger.error(f"Goal decomposition failed: {e}")
            # Return basic fallback task
            return [
                Task(
                    task_id=f"{goal_id}-task-000",
                    goal_id=goal_id,
                    agent_type="zeitgeist",
                    task_type="analyze_trends",
                    parameters=parameters
                )
            ]

    def _apply_workflow_template(
        self,
        goal_id: str,
        template_id: str,
        parameters: Dict[str, Any]
    ) -> List[Task]:
        """Apply predefined workflow template"""

        template = self.workflow_templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        tasks = []
        for i, task_def in enumerate(template.task_sequence):
            # Merge template parameters with provided parameters
            task_params = {**task_def.get("parameters", {}), **parameters}

            task = Task(
                task_id=f"{goal_id}-task-{i:03d}",
                goal_id=goal_id,
                agent_type=task_def["agent_type"],
                task_type=task_def["task_type"],
                parameters=task_params,
                dependencies=task_def.get("dependencies", []),
                priority=TaskPriority(task_def.get("priority", "medium"))
            )
            tasks.append(task)

        logger.info(f"Applied template '{template.name}' with {len(tasks)} tasks")

        return tasks

    async def _execute_tasks_async(self, goal: Goal) -> Dict[str, Any]:
        """
        Execute tasks asynchronously (parallel where possible)

        This is the EXECUTOR function - intelligent task execution
        """

        results = {}
        pending_tasks = {t.task_id: t for t in goal.tasks}

        while pending_tasks:
            # Find tasks ready to execute (dependencies satisfied)
            ready_tasks = [
                task for task in pending_tasks.values()
                if all(dep_id not in pending_tasks for dep_id in task.dependencies)
            ]

            if not ready_tasks:
                # No tasks ready - check if deadlock
                logger.error("Task deadlock detected")
                break

            # Execute ready tasks in parallel
            logger.info(f"Executing {len(ready_tasks)} tasks in parallel")

            task_coroutines = [
                self._execute_single_task(task)
                for task in ready_tasks
            ]

            task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)

            # Process results
            for task, result in zip(ready_tasks, task_results):
                if isinstance(result, Exception):
                    task.status = TaskStatus.FAILED
                    task.error_message = str(result)
                    logger.error(f"Task {task.task_id} failed: {result}")
                else:
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.completed_at = datetime.utcnow()
                    results[task.task_id] = result
                    logger.info(f"Task {task.task_id} completed")

                # Remove from pending
                del pending_tasks[task.task_id]

        return results

    async def _execute_tasks_sequential(self, goal: Goal) -> Dict[str, Any]:
        """Execute tasks sequentially"""

        results = {}

        for task in goal.tasks:
            try:
                result = await self._execute_single_task(task)
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = datetime.utcnow()
                results[task.task_id] = result
                logger.info(f"Task {task.task_id} completed")

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                logger.error(f"Task {task.task_id} failed: {e}")

                # Stop on first failure in sequential mode
                break

        return results

    async def _execute_single_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute single task by routing to appropriate agent

        This is the core EXECUTOR logic
        """

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()

        logger.info(f"Executing task {task.task_id}: {task.agent_type}.{task.task_type}")

        # Get the agent
        agent = self.agents.get(task.agent_type)
        if not agent:
            raise ValueError(f"Agent {task.agent_type} not found")

        # Execute task
        response = await agent.execute_task(
            task_id=task.task_id,
            task_type=task.task_type,
            parameters=task.parameters
        )

        if response.status != "success":
            raise Exception(response.error_message or "Task execution failed")

        return response.result

    async def _critic_evaluate(
        self,
        task_id: str,
        result: Dict[str, Any],
        quality_threshold: float
    ) -> CriticFeedback:
        """
        Evaluate task result quality (CRITIC function)

        Uses Claude to assess quality and provide feedback
        """

        critic_prompt = f"""
You are a quality control critic for an AI agent system.

Evaluate this task result:

**Task ID**: {task_id}
**Result**: {json.dumps(result, indent=2)}

Evaluate on:
1. Completeness (did it answer the task?)
2. Quality (is it well-crafted?)
3. Relevance (is it on-target?)
4. Actionability (can we use it?)

Quality Threshold: {quality_threshold}

Provide:
- Quality score (0.0-1.0)
- Strengths (what's good)
- Weaknesses (what's lacking)
- Improvement suggestions
- Approval decision (approve if score >= threshold)

Return as JSON:
{{
    "quality_score": 0.85,
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "improvement_suggestions": ["...", "..."],
    "approved": true
}}
"""

        try:
            response = await self.call_claude(
                prompt=critic_prompt,
                system_prompt="You are an expert quality evaluator."
            )

            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                feedback_data = json.loads(json_match.group(1))
            else:
                feedback_data = json.loads(response)

            feedback = CriticFeedback(
                task_id=task_id,
                quality_score=feedback_data.get("quality_score", 0.5),
                strengths=feedback_data.get("strengths", []),
                weaknesses=feedback_data.get("weaknesses", []),
                improvement_suggestions=feedback_data.get("improvement_suggestions", []),
                approved=feedback_data.get("approved", False),
                requires_revision=not feedback_data.get("approved", False)
            )

            return feedback

        except Exception as e:
            logger.error(f"Critic evaluation failed: {e}")
            # Return neutral feedback on error
            return CriticFeedback(
                task_id=task_id,
                quality_score=0.5,
                strengths=[],
                weaknesses=["Evaluation failed"],
                improvement_suggestions=[],
                approved=False
            )

    def _calculate_progress(self, goal: Goal) -> float:
        """Calculate goal progress percentage"""

        if not goal.tasks:
            return 0.0

        completed_count = sum(1 for t in goal.tasks if t.status == TaskStatus.COMPLETED)
        return (completed_count / len(goal.tasks)) * 100.0

    def _load_workflow_templates(self) -> Dict[str, WorkflowTemplate]:
        """Load predefined workflow templates"""

        templates = {
            "new_product_launch": WorkflowTemplate(
                template_id="new_product_launch",
                name="New Product Launch Workflow",
                description="End-to-end workflow for launching a new product",
                objective="launch_product",
                task_sequence=[
                    {
                        "agent_type": "zeitgeist",
                        "task_type": "analyze_trends",
                        "parameters": {"days_back": 30},
                        "priority": "high"
                    },
                    {
                        "agent_type": "zeitgeist",
                        "task_type": "identify_opportunities",
                        "parameters": {"min_opportunity_score": 0.75},
                        "dependencies": ["zeitgeist.analyze_trends"],
                        "priority": "high"
                    },
                    {
                        "agent_type": "bard",
                        "task_type": "generate_brand_story",
                        "parameters": {"storytelling_style": "luxury"},
                        "dependencies": ["zeitgeist.identify_opportunities"],
                        "priority": "medium"
                    },
                    {
                        "agent_type": "bard",
                        "task_type": "create_campaign",
                        "parameters": {"campaign_objective": "product_launch"},
                        "dependencies": ["bard.generate_brand_story"],
                        "priority": "medium"
                    }
                ]
            ),
            "seasonal_campaign": WorkflowTemplate(
                template_id="seasonal_campaign",
                name="Seasonal Campaign Workflow",
                description="Create seasonal marketing campaign",
                objective="create_campaign",
                task_sequence=[
                    {
                        "agent_type": "zeitgeist",
                        "task_type": "analyze_platform_data",
                        "parameters": {"days_back": 90},
                        "priority": "medium"
                    },
                    {
                        "agent_type": "bard",
                        "task_type": "create_campaign",
                        "parameters": {},
                        "dependencies": ["zeitgeist.analyze_platform_data"],
                        "priority": "high"
                    },
                    {
                        "agent_type": "bard",
                        "task_type": "atomize_content",
                        "parameters": {},
                        "dependencies": ["bard.create_campaign"],
                        "priority": "medium"
                    }
                ]
            )
        }

        return templates


# Singleton instance
_master_planner = None

async def get_master_planner(world_model_url: Optional[str] = None) -> MasterPlanner:
    """Get singleton Master Planner instance"""
    global _master_planner
    if _master_planner is None:
        _master_planner = MasterPlanner(world_model_url=world_model_url)
        await _master_planner.initialize()
    return _master_planner
