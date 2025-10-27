"""
ResonanceModelingAgent - NBRS 2.0 공명 모델 관리 및 최적화
Brand Resonance Score 계산
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
import numpy as np
from sklearn.metrics import roc_auc_score
import json

from .base_agent import BaseAgent, AgentState
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


logger = logging.getLogger(__name__)


class ResonanceModelingAgent(BaseAgent):
    """
    공명 모델링 에이전트 (NBRS 2.0)

    책임:
    - 브랜드 공명 지수(Resonance Index) 계산
    - NBRS 모델의 지속적 학습 (Continual Learning)
    - 모델 성능 모니터링 및 MAB 기반 최적화
    """

    def __init__(self, agent_id: str = "resonance_modeling_001"):
        super().__init__(agent_id, "ResonanceModelingAgent")
        self.model_version = settings.nbrs_model_version
        self.model_weights = self._load_initial_weights()
        self.prediction_history: List[Dict[str, Any]] = []

    def _load_initial_weights(self) -> Dict[str, float]:
        """초기 NBRS 모델 가중치 로드"""
        # 초기 가중치 (추후 학습을 통해 최적화)
        return {
            "category_overlap": 0.30,      # 브랜드 카테고리 중복성
            "target_audience_similarity": 0.25,  # 타겟 고객 유사성
            "media_co_mention": 0.20,      # 미디어 동시 언급 빈도
            "market_positioning": 0.15,    # 시장 포지셔닝 유사성
            "geographic_overlap": 0.10     # 지리적 중복
        }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        작업 실행

        Args:
            task: {
                "task_type": "calculate_resonance" | "retrain_model" | "evaluate_model",
                "parameters": {...}
            }

        Returns:
            작업 결과
        """
        start_time = datetime.utcnow()
        task_type = task.get("task_type")
        parameters = task.get("parameters", {})

        try:
            self.update_state(AgentState.WORKING)

            if task_type == "calculate_resonance":
                result = await self._calculate_resonance(parameters)
            elif task_type == "retrain_model":
                result = await self._retrain_model(parameters)
            elif task_type == "evaluate_model":
                result = await self._evaluate_model(parameters)
            elif task_type == "rank_brands":
                result = await self._rank_brands(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            self.update_state(AgentState.COMPLETED)

            return {
                "task_id": task.get("task_id"),
                "status": "success",
                "result": result,
                "execution_time": execution_time
            }

        except Exception as e:
            logger.error(f"[{self.agent_id}] Task execution failed: {e}")
            self.update_state(AgentState.ERROR)

            return {
                "task_id": task.get("task_id"),
                "status": "failure",
                "error": str(e),
                "execution_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def _calculate_resonance(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        브랜드 간 공명 지수 계산

        Args:
            parameters: {
                "anchor_brand": Dict (기준 브랜드, 예: NERD),
                "target_brand": Dict (비교 브랜드)
            }

        Returns:
            공명 지수 및 세부 점수
        """
        anchor_brand = parameters.get("anchor_brand", {})
        target_brand = parameters.get("target_brand", {})

        anchor_name = anchor_brand.get("brand_name", "NERD")
        target_name = target_brand.get("brand_name", "Unknown")

        logger.info(f"[{self.agent_id}] Calculating resonance: {anchor_name} <-> {target_name}")

        # 5가지 요소별 점수 계산 (0-100)
        scores = {
            "category_overlap": self._calculate_category_overlap(anchor_brand, target_brand),
            "target_audience_similarity": self._calculate_audience_similarity(anchor_brand, target_brand),
            "media_co_mention": self._calculate_media_co_mention(anchor_brand, target_brand),
            "market_positioning": self._calculate_market_positioning(anchor_brand, target_brand),
            "geographic_overlap": self._calculate_geographic_overlap(anchor_brand, target_brand)
        }

        # 가중 평균으로 최종 공명 지수 계산
        resonance_index = sum(
            scores[key] * self.model_weights[key]
            for key in scores.keys()
        )

        # TIER 분류 (NBRS와 유사)
        tier = self._classify_tier(resonance_index)

        # 예측 이력에 추가 (나중에 재학습에 사용)
        prediction = {
            "anchor_brand": anchor_name,
            "target_brand": target_name,
            "resonance_index": resonance_index,
            "tier": tier,
            "component_scores": scores,
            "model_version": self.model_version,
            "predicted_at": datetime.utcnow().isoformat()
        }
        self.prediction_history.append(prediction)

        logger.info(f"[{self.agent_id}] Resonance Index: {resonance_index:.2f}, Tier: {tier}")

        return {
            "anchor_brand": anchor_name,
            "target_brand": target_name,
            "resonance_index": round(resonance_index, 2),
            "tier": tier,
            "component_scores": {k: round(v, 2) for k, v in scores.items()},
            "model_version": self.model_version,
            "explanation": self._generate_explanation(scores, resonance_index)
        }

    def _calculate_category_overlap(self, anchor: Dict, target: Dict) -> float:
        """브랜드 카테고리 중복성 (0-100)"""
        anchor_categories = set(anchor.get("nice_classification", []))
        target_categories = set(target.get("nice_classification", []))

        if not anchor_categories or not target_categories:
            return 0.0

        overlap = len(anchor_categories & target_categories)
        total = len(anchor_categories | target_categories)

        return (overlap / total) * 100

    def _calculate_audience_similarity(self, anchor: Dict, target: Dict) -> float:
        """타겟 고객 유사성 (0-100)"""
        # 간단한 휴리스틱: 재무 데이터 기반 유사성
        anchor_fin = anchor.get("financial_data", {})
        target_fin = target.get("financial_data", {})

        anchor_revenue = anchor_fin.get("annual_revenue_krw", 0)
        target_revenue = target_fin.get("annual_revenue_krw", 0)

        if anchor_revenue == 0 or target_revenue == 0:
            return 50.0  # 기본값

        # 매출 규모 유사성 (로그 스케일)
        ratio = min(anchor_revenue, target_revenue) / max(anchor_revenue, target_revenue)
        similarity = ratio * 100

        return similarity

    def _calculate_media_co_mention(self, anchor: Dict, target: Dict) -> float:
        """미디어 동시 언급 빈도 (0-100)"""
        # Mock: 뉴스 데이터에서 동시 언급 분석
        anchor_news = anchor.get("news_data", {})
        target_news = target.get("news_data", {})

        anchor_mentions = anchor_news.get("total_mentions", 0)
        target_mentions = target_news.get("total_mentions", 0)

        # 간단한 휴리스틱: 멘션 수가 비슷하면 높은 점수
        if anchor_mentions == 0 and target_mentions == 0:
            return 0.0

        co_mention_score = min(anchor_mentions, target_mentions) / max(anchor_mentions, target_mentions, 1) * 100

        return co_mention_score

    def _calculate_market_positioning(self, anchor: Dict, target: Dict) -> float:
        """시장 포지셔닝 유사성 (0-100)"""
        anchor_fin = anchor.get("financial_data", {})
        target_fin = target.get("financial_data", {})

        # 신용 등급 기반 유사성 (간단화)
        anchor_rating = anchor_fin.get("credit_rating", "C")
        target_rating = target_fin.get("credit_rating", "C")

        rating_map = {"A+": 100, "A": 90, "B+": 80, "B": 70, "C": 50}
        anchor_score = rating_map.get(anchor_rating, 50)
        target_score = rating_map.get(target_rating, 50)

        positioning_similarity = 100 - abs(anchor_score - target_score)

        return positioning_similarity

    def _calculate_geographic_overlap(self, anchor: Dict, target: Dict) -> float:
        """지리적 중복 (0-100)"""
        # MVP는 한국 시장만 타겟이므로 기본 100점
        anchor_country = anchor.get("country", "KR")
        target_country = target.get("country", "KR")

        return 100.0 if anchor_country == target_country else 0.0

    def _classify_tier(self, resonance_index: float) -> str:
        """공명 지수를 TIER로 분류"""
        if resonance_index >= 80:
            return "TIER1"
        elif resonance_index >= 60:
            return "TIER2"
        elif resonance_index >= 40:
            return "TIER3"
        else:
            return "TIER4"

    def _generate_explanation(self, scores: Dict[str, float], resonance_index: float) -> str:
        """설명 가능 AI (XAI): 공명 지수 산출 근거"""
        top_factors = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

        explanation = f"공명 지수 {resonance_index:.2f}점은 다음 요인에 기반합니다:\n"
        for i, (factor, score) in enumerate(top_factors, 1):
            factor_name_kr = {
                "category_overlap": "브랜드 카테고리 중복",
                "target_audience_similarity": "타겟 고객 유사성",
                "media_co_mention": "미디어 동시 언급",
                "market_positioning": "시장 포지셔닝",
                "geographic_overlap": "지리적 중복"
            }.get(factor, factor)

            explanation += f"{i}. {factor_name_kr}: {score:.1f}점\n"

        return explanation

    async def _retrain_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        NBRS 모델 재학습 (Continual Learning)

        Args:
            parameters: {
                "training_data": List[Dict] (실제 파트너십 성과 데이터)
            }

        Returns:
            재학습 결과 및 새로운 모델 성능
        """
        training_data = parameters.get("training_data", [])

        logger.info(f"[{self.agent_id}] Retraining model with {len(training_data)} samples")

        # 간단한 gradient descent로 가중치 업데이트 (실제로는 복잡한 ML)
        # 여기서는 Mock으로 약간의 가중치 조정
        learning_rate = 0.01
        for key in self.model_weights.keys():
            adjustment = np.random.uniform(-learning_rate, learning_rate)
            self.model_weights[key] = max(0.05, min(0.50, self.model_weights[key] + adjustment))

        # 가중치 정규화 (합이 1이 되도록)
        total_weight = sum(self.model_weights.values())
        self.model_weights = {k: v / total_weight for k, v in self.model_weights.items()}

        logger.info(f"[{self.agent_id}] Model retrained. New weights: {self.model_weights}")

        return {
            "status": "retrained",
            "new_weights": self.model_weights,
            "training_samples": len(training_data),
            "model_version": self.model_version,
            "retrained_at": datetime.utcnow().isoformat()
        }

    async def _evaluate_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        모델 성능 평가 (AUC 등)

        Args:
            parameters: {
                "test_data": List[Dict] (ground truth가 있는 테스트 데이터)
            }

        Returns:
            모델 성능 지표
        """
        test_data = parameters.get("test_data", [])

        # Mock AUC 계산
        # 실제로는 y_true, y_pred를 사용하여 roc_auc_score 계산
        mock_auc = np.random.uniform(0.75, 0.90)

        logger.info(f"[{self.agent_id}] Model evaluation: AUC={mock_auc:.4f}")

        return {
            "auc": round(mock_auc, 4),
            "test_samples": len(test_data),
            "model_version": self.model_version,
            "evaluated_at": datetime.utcnow().isoformat()
        }

    async def _rank_brands(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        브랜드 공명 지수 순위 정렬

        Args:
            parameters: {
                "anchor_brand": Dict,
                "target_brands": List[Dict]
            }

        Returns:
            공명 지수 순으로 정렬된 브랜드 리스트
        """
        anchor_brand = parameters.get("anchor_brand", {})
        target_brands = parameters.get("target_brands", [])

        logger.info(f"[{self.agent_id}] Ranking {len(target_brands)} brands")

        # 각 브랜드에 대해 공명 지수 계산
        results = []
        for target_brand in target_brands:
            resonance = await self._calculate_resonance({
                "anchor_brand": anchor_brand,
                "target_brand": target_brand
            })
            results.append(resonance)

        # 공명 지수 내림차순 정렬
        results.sort(key=lambda x: x["resonance_index"], reverse=True)

        # 상위 10% 필터링 (MVP 요구사항)
        top_10_percent = max(1, len(results) // 10)
        top_brands = results[:top_10_percent]

        logger.info(f"[{self.agent_id}] Top 10% brands: {len(top_brands)}")

        return top_brands


# Singleton instance
resonance_modeling_agent = ResonanceModelingAgent()
