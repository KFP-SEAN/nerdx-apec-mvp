"""
OrchestratorAgent - 마스터 플래너 및 작업 오케스트레이션
관리형 오케스트레이션 패턴 (Managerial Orchestration Pattern)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio

from .base_agent import BaseAgent, AgentState, AgentMessage, AgentMessageType
from .market_intel_agent import market_intel_agent
from .resonance_modeling_agent import resonance_modeling_agent
from .content_strategy_agent import content_strategy_agent

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    오케스트레이터 에이전트 (Master Planner)

    책임:
    - 상위 목표를 구체적 작업으로 분해 (Goal Decomposition)
    - 전문 에이전트에게 작업 위임 (Task Assignment)
    - 작업 결과 평가 및 피드백 (Critic)
    - 전체 워크플로우 관리
    """

    def __init__(self, agent_id: str = "orchestrator_001"):
        super().__init__(agent_id, "OrchestratorAgent")

        # 작업자 에이전트 등록
        self.worker_agents = {
            "market_intel": market_intel_agent,
            "resonance_modeling": resonance_modeling_agent,
            "content_strategy": content_strategy_agent
        }

        # 워크플로우 정의
        self.workflows = {
            "find_top_resonant_brands": self._workflow_find_top_brands,
            "generate_partnership_pipeline": self._workflow_partnership_pipeline
        }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        작업 실행 (워크플로우 실행)

        Args:
            task: {
                "task_type": "execute_workflow",
                "parameters": {
                    "workflow_name": str,
                    "goal": str,
                    ...
                }
            }

        Returns:
            워크플로우 실행 결과
        """
        start_time = datetime.utcnow()
        task_type = task.get("task_type")
        parameters = task.get("parameters", {})

        try:
            self.update_state(AgentState.WORKING)

            if task_type == "execute_workflow":
                workflow_name = parameters.get("workflow_name")
                if workflow_name not in self.workflows:
                    raise ValueError(f"Unknown workflow: {workflow_name}")

                workflow_func = self.workflows[workflow_name]
                result = await workflow_func(parameters)

            elif task_type == "decompose_goal":
                result = await self._decompose_goal(parameters)

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

    async def _decompose_goal(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        목표를 실행 가능한 작업으로 분해

        Args:
            parameters: {
                "goal": str (예: "대한민국 상위 10% 공명 브랜드 발굴")
            }

        Returns:
            작업 리스트
        """
        goal = parameters.get("goal")

        logger.info(f"[{self.agent_id}] Decomposing goal: {goal}")

        # 간단한 규칙 기반 분해 (실제로는 LLM 사용 가능)
        if "공명 브랜드 발굴" in goal:
            tasks = [
                {
                    "task_id": "task_001",
                    "agent": "market_intel",
                    "task_type": "collect_brand_data",
                    "description": "대한민국 브랜드 데이터 수집",
                    "parameters": {"country": "KR", "limit": 100}
                },
                {
                    "task_id": "task_002",
                    "agent": "resonance_modeling",
                    "task_type": "rank_brands",
                    "description": "브랜드 공명 지수 계산 및 랭킹",
                    "parameters": {}  # 이전 작업 결과 사용
                },
                {
                    "task_id": "task_003",
                    "agent": "content_strategy",
                    "task_type": "generate_batch_briefs",
                    "description": "상위 10% 브랜드에 대한 협력 개요서 생성",
                    "parameters": {}  # 이전 작업 결과 사용
                }
            ]
        else:
            tasks = []

        logger.info(f"[{self.agent_id}] Decomposed into {len(tasks)} tasks")

        return tasks

    async def _workflow_find_top_brands(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        워크플로우: 상위 10% 공명 브랜드 발굴

        Steps:
        1. MarketIntelAgent: 브랜드 데이터 수집
        2. ResonanceModelingAgent: 공명 지수 계산 및 랭킹
        3. ContentStrategyAgent: 협력 개요서 생성

        Args:
            parameters: {
                "anchor_brand": Dict (예: NERD),
                "target_country": str (default "KR")
            }

        Returns:
            워크플로우 결과
        """
        anchor_brand = parameters.get("anchor_brand", {
            "brand_name": "NERD",
            "company_name": "NERDX",
            "nice_classification": ["33", "35", "43"],
            "country": "KR"
        })
        target_country = parameters.get("target_country", "KR")

        logger.info(f"[{self.agent_id}] Executing workflow: find_top_resonant_brands")

        workflow_result = {
            "workflow_name": "find_top_resonant_brands",
            "started_at": datetime.utcnow().isoformat(),
            "steps": []
        }

        try:
            # Step 1: 브랜드 데이터 수집
            logger.info(f"[{self.agent_id}] Step 1/3: Collecting brand data...")
            step1_task = {
                "task_id": "step1",
                "task_type": "collect_brand_data",
                "parameters": {"country": target_country, "limit": 50}
            }
            step1_result = await market_intel_agent.execute_task(step1_task)

            if step1_result["status"] != "success":
                raise Exception(f"Step 1 failed: {step1_result.get('error')}")

            brands = step1_result["result"]
            workflow_result["steps"].append({
                "step": 1,
                "description": "Brand data collection",
                "status": "success",
                "brands_collected": len(brands)
            })

            # Step 2: 공명 지수 계산 및 랭킹
            logger.info(f"[{self.agent_id}] Step 2/3: Calculating resonance scores...")
            step2_task = {
                "task_id": "step2",
                "task_type": "rank_brands",
                "parameters": {
                    "anchor_brand": anchor_brand,
                    "target_brands": brands
                }
            }
            step2_result = await resonance_modeling_agent.execute_task(step2_task)

            if step2_result["status"] != "success":
                raise Exception(f"Step 2 failed: {step2_result.get('error')}")

            top_brands = step2_result["result"]
            workflow_result["steps"].append({
                "step": 2,
                "description": "Resonance scoring and ranking",
                "status": "success",
                "top_brands_count": len(top_brands)
            })

            # Step 3: 협력 개요서 생성
            logger.info(f"[{self.agent_id}] Step 3/3: Generating collaboration briefs...")
            step3_task = {
                "task_id": "step3",
                "task_type": "generate_batch_briefs",
                "parameters": {
                    "anchor_brand": anchor_brand,
                    "target_brands": [tb for tb in brands if tb["brand_name"] in [r["target_brand"] for r in top_brands]],
                    "resonance_results": top_brands
                }
            }
            step3_result = await content_strategy_agent.execute_task(step3_task)

            if step3_result["status"] != "success":
                raise Exception(f"Step 3 failed: {step3_result.get('error')}")

            briefs = step3_result["result"]
            workflow_result["steps"].append({
                "step": 3,
                "description": "Collaboration brief generation",
                "status": "success",
                "briefs_generated": len(briefs)
            })

            # 최종 결과
            workflow_result["status"] = "success"
            workflow_result["completed_at"] = datetime.utcnow().isoformat()
            workflow_result["final_output"] = {
                "top_resonant_brands": top_brands,
                "collaboration_briefs": briefs,
                "total_brands_analyzed": len(brands),
                "top_10_percent_count": len(top_brands)
            }

            logger.info(f"[{self.agent_id}] Workflow completed successfully")

        except Exception as e:
            logger.error(f"[{self.agent_id}] Workflow failed: {e}")
            workflow_result["status"] = "failure"
            workflow_result["error"] = str(e)
            workflow_result["completed_at"] = datetime.utcnow().isoformat()

        return workflow_result

    async def _workflow_partnership_pipeline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        워크플로우: 파트너십 파이프라인 생성 (전체 프로세스)

        Steps:
        1. 브랜드 데이터 수집
        2. 공명 분석
        3. 협력 개요서 생성
        4. NotebookLM 데이터 준비
        5. Google Docs 내보내기 (준비)

        Args:
            parameters: {
                "anchor_brand": Dict,
                "target_country": str
            }

        Returns:
            전체 파이프라인 결과
        """
        logger.info(f"[{self.agent_id}] Executing workflow: partnership_pipeline")

        # find_top_brands 워크플로우 재사용
        top_brands_result = await self._workflow_find_top_brands(parameters)

        if top_brands_result["status"] != "success":
            return top_brands_result

        # NotebookLM 데이터 준비
        logger.info(f"[{self.agent_id}] Preparing NotebookLM data...")
        briefs = top_brands_result["final_output"]["collaboration_briefs"]
        top_brands = top_brands_result["final_output"]["top_resonant_brands"]

        notebooklm_outputs = []
        for i, brief in enumerate(briefs):
            resonance_data = top_brands[i] if i < len(top_brands) else {}

            notebooklm_task = {
                "task_id": f"notebooklm_{i}",
                "task_type": "prepare_notebooklm_data",
                "parameters": {
                    "brand_data": brief,
                    "resonance_data": resonance_data,
                    "brief": brief
                }
            }
            notebooklm_result = await content_strategy_agent.execute_task(notebooklm_task)

            if notebooklm_result["status"] == "success":
                notebooklm_outputs.append(notebooklm_result["result"])

        # 최종 결과
        pipeline_result = {
            "workflow_name": "partnership_pipeline",
            "status": "success",
            "final_output": {
                **top_brands_result["final_output"],
                "notebooklm_data": notebooklm_outputs,
                "export_ready": True
            },
            "completed_at": datetime.utcnow().isoformat()
        }

        logger.info(f"[{self.agent_id}] Partnership pipeline completed")

        return pipeline_result

    async def evaluate_workflow_quality(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        워크플로우 품질 평가 (Critic)

        Args:
            workflow_result: 워크플로우 실행 결과

        Returns:
            품질 평가 결과
        """
        logger.info(f"[{self.agent_id}] Evaluating workflow quality...")

        # 간단한 평가 기준
        quality_metrics = {
            "completion_rate": 0.0,
            "data_quality": 0.0,
            "execution_time": 0.0,
            "overall_score": 0.0
        }

        # Completion Rate
        total_steps = len(workflow_result.get("steps", []))
        successful_steps = sum(1 for step in workflow_result.get("steps", []) if step.get("status") == "success")
        quality_metrics["completion_rate"] = successful_steps / max(total_steps, 1)

        # Data Quality (간단한 휴리스틱)
        final_output = workflow_result.get("final_output", {})
        top_brands_count = final_output.get("top_10_percent_count", 0)
        briefs_count = len(final_output.get("collaboration_briefs", []))

        quality_metrics["data_quality"] = min(1.0, (top_brands_count + briefs_count) / 20)

        # Overall Score
        quality_metrics["overall_score"] = (
            quality_metrics["completion_rate"] * 0.5 +
            quality_metrics["data_quality"] * 0.5
        )

        evaluation = {
            "workflow_name": workflow_result.get("workflow_name"),
            "quality_metrics": quality_metrics,
            "passed": quality_metrics["overall_score"] >= 0.8,
            "recommendations": []
        }

        if quality_metrics["overall_score"] < 0.8:
            evaluation["recommendations"].append("워크플로우 재실행 권장")

        if quality_metrics["data_quality"] < 0.7:
            evaluation["recommendations"].append("데이터 수집 단계 개선 필요")

        logger.info(f"[{self.agent_id}] Quality score: {quality_metrics['overall_score']:.2f}")

        return evaluation


# Singleton instance
orchestrator_agent = OrchestratorAgent()
