"""
ContentStrategyAgent - AI 기반 협력 개요서 자동 생성
LLM 활용 (Claude, Gemini)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json

from .base_agent import BaseAgent, AgentState
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


logger = logging.getLogger(__name__)


class ContentStrategyAgent(BaseAgent):
    """
    콘텐츠 전략 에이전트

    책임:
    - 공명 지수 상위 10% 브랜드에 대한 협력 개요서 자동 생성
    - LLM 기반 창의적 파트너십 아이디어 도출
    - NotebookLM 포맷 데이터 생성
    """

    def __init__(self, agent_id: str = "content_strategy_001"):
        super().__init__(agent_id, "ContentStrategyAgent")
        self.anthropic_api_key = settings.anthropic_api_key
        self.gemini_api_key = settings.gemini_api_key

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        작업 실행

        Args:
            task: {
                "task_type": "generate_brief" | "generate_batch_briefs",
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

            if task_type == "generate_brief":
                result = await self._generate_brief(parameters)
            elif task_type == "generate_batch_briefs":
                result = await self._generate_batch_briefs(parameters)
            elif task_type == "prepare_notebooklm_data":
                result = await self._prepare_notebooklm_data(parameters)
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

    async def _generate_brief(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        단일 브랜드에 대한 협력 개요서 생성

        Args:
            parameters: {
                "anchor_brand": Dict (예: NERD),
                "target_brand": Dict,
                "resonance_data": Dict (공명 분석 결과)
            }

        Returns:
            협력 개요서
        """
        anchor_brand = parameters.get("anchor_brand", {})
        target_brand = parameters.get("target_brand", {})
        resonance_data = parameters.get("resonance_data", {})

        anchor_name = anchor_brand.get("brand_name", "NERD")
        target_name = target_brand.get("brand_name", "Unknown")
        resonance_index = resonance_data.get("resonance_index", 0)

        logger.info(f"[{self.agent_id}] Generating collaboration brief: {anchor_name} x {target_name}")

        # LLM 프롬프트 구성
        prompt = self._construct_brief_prompt(anchor_brand, target_brand, resonance_data)

        # LLM API 호출 (Mock - 실제로는 Claude/Gemini API)
        brief_content = await self._call_llm(prompt)

        # 협력 개요서 구조화
        brief = {
            "title": f"{anchor_name} x {target_name} 협력 제안서",
            "anchor_brand": anchor_name,
            "target_brand": target_name,
            "resonance_index": resonance_index,
            "tier": resonance_data.get("tier", "TIER2"),
            "executive_summary": brief_content.get("executive_summary"),
            "partnership_ideas": brief_content.get("partnership_ideas", []),
            "expected_outcomes": brief_content.get("expected_outcomes", []),
            "next_steps": brief_content.get("next_steps", []),
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": self.agent_id
        }

        logger.info(f"[{self.agent_id}] Brief generated with {len(brief['partnership_ideas'])} ideas")

        return brief

    def _construct_brief_prompt(
        self,
        anchor_brand: Dict,
        target_brand: Dict,
        resonance_data: Dict
    ) -> str:
        """LLM 프롬프트 생성"""
        prompt = f"""
당신은 전략적 브랜드 파트너십 전문가입니다. 다음 두 브랜드 간의 협력 제안서를 작성하세요.

**기준 브랜드 (Anchor)**:
- 브랜드명: {anchor_brand.get('brand_name')}
- 기업명: {anchor_brand.get('company_name')}
- 카테고리: {', '.join(anchor_brand.get('nice_classification', []))}
- 특징: 한국 전통주 프리미엄 브랜드, AI 기반 커머스

**타겟 브랜드 (Target)**:
- 브랜드명: {target_brand.get('brand_name')}
- 기업명: {target_brand.get('company_name')}
- 카테고리: {', '.join(target_brand.get('nice_classification', []))}
- 재무 데이터: {target_brand.get('financial_data', {})}

**공명 분석 결과**:
- 공명 지수: {resonance_data.get('resonance_index')}
- TIER: {resonance_data.get('tier')}
- 핵심 공명 요인: {resonance_data.get('component_scores', {})}

**요구사항**:
1. 간결한 Executive Summary (2-3문장)
2. 구체적인 파트너십 아이디어 2-3가지
   - 각 아이디어는 실행 가능하고 측정 가능한 것
   - 양측 브랜드에게 Win-Win 가치 제공
3. 예상 성과 (정량적 + 정성적)
4. Next Steps (구체적 액션 아이템)

협력 제안서를 JSON 형식으로 작성하세요.
"""
        return prompt

    async def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """
        LLM API 호출 (Claude 또는 Gemini)

        Args:
            prompt: 프롬프트

        Returns:
            LLM 응답 (구조화된 JSON)
        """
        # 실제 구현 시 Anthropic Claude API 호출
        # import anthropic
        # client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        # response = client.messages.create(
        #     model="claude-3-sonnet-20240229",
        #     max_tokens=2000,
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return json.loads(response.content[0].text)

        # Mock 응답
        mock_response = {
            "executive_summary": "두 브랜드는 '프리미엄 라이프스타일' 영역에서 높은 공명도를 보입니다. 타겟 고객층이 겹치며, 브랜드 가치가 정렬되어 시너지 창출이 가능합니다.",
            "partnership_ideas": [
                {
                    "title": "공동 한정판 제품 출시",
                    "description": "양사의 브랜드 아이덴티티를 결합한 프리미엄 한정판 제품 (예: 전통주 x 디자인 콜라보)",
                    "timeline": "3개월",
                    "budget_estimate": "50M KRW"
                },
                {
                    "title": "Cross-Promotion 캠페인",
                    "description": "서로의 고객 베이스를 활용한 디지털 마케팅 캠페인 (소셜 미디어, 이메일)",
                    "timeline": "2개월",
                    "budget_estimate": "30M KRW"
                },
                {
                    "title": "브랜드 경험 이벤트",
                    "description": "VIP 고객 대상 브랜드 스토리 경험 이벤트 (팝업 스토어, 테이스팅)",
                    "timeline": "1개월",
                    "budget_estimate": "20M KRW"
                }
            ],
            "expected_outcomes": [
                "브랜드 인지도 20% 향상 (6개월 내)",
                "Cross-selling을 통한 매출 15% 증가",
                "신규 고객 확보 1,000명 이상",
                "SNS 인게이지먼트 30% 증가"
            ],
            "next_steps": [
                "1주차: 양사 마케팅팀 킥오프 미팅",
                "2주차: 협력 범위 및 예산 확정",
                "3주차: 법무 검토 및 계약서 초안 작성",
                "4주차: 캠페인 크리에이티브 개발 시작"
            ]
        }

        return mock_response

    async def _generate_batch_briefs(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        다수 브랜드에 대한 협력 개요서 일괄 생성

        Args:
            parameters: {
                "anchor_brand": Dict,
                "target_brands": List[Dict],
                "resonance_results": List[Dict]
            }

        Returns:
            협력 개요서 리스트
        """
        anchor_brand = parameters.get("anchor_brand", {})
        target_brands = parameters.get("target_brands", [])
        resonance_results = parameters.get("resonance_results", [])

        logger.info(f"[{self.agent_id}] Generating {len(target_brands)} collaboration briefs")

        briefs = []
        for i, target_brand in enumerate(target_brands):
            resonance_data = resonance_results[i] if i < len(resonance_results) else {}

            brief = await self._generate_brief({
                "anchor_brand": anchor_brand,
                "target_brand": target_brand,
                "resonance_data": resonance_data
            })

            briefs.append(brief)

        logger.info(f"[{self.agent_id}] Generated {len(briefs)} briefs")

        return briefs

    async def _prepare_notebooklm_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        NotebookLM에 최적화된 데이터 형식으로 변환

        Args:
            parameters: {
                "brand_data": Dict,
                "resonance_data": Dict,
                "brief": Dict
            }

        Returns:
            NotebookLM 형식 데이터
        """
        brand_data = parameters.get("brand_data", {})
        resonance_data = parameters.get("resonance_data", {})
        brief = parameters.get("brief", {})

        logger.info(f"[{self.agent_id}] Preparing NotebookLM data")

        # 엔티티 추출 (브랜드, 인물, 장소, 개념)
        entities = {
            "brands": [
                brand_data.get("brand_name"),
                brief.get("anchor_brand")
            ],
            "companies": [
                brand_data.get("company_name")
            ],
            "concepts": [
                "브랜드 공명",
                "파트너십",
                "공동 마케팅"
            ],
            "locations": [
                "대한민국"
            ]
        }

        # 관계 그래프 (Triples: Subject - Predicate - Object)
        relationships = [
            {
                "subject": brand_data.get("brand_name"),
                "predicate": "has_resonance_with",
                "object": brief.get("anchor_brand"),
                "score": resonance_data.get("resonance_index")
            },
            {
                "subject": brand_data.get("brand_name"),
                "predicate": "belongs_to_tier",
                "object": resonance_data.get("tier")
            },
            {
                "subject": brand_data.get("brand_name"),
                "predicate": "owned_by",
                "object": brand_data.get("company_name")
            }
        ]

        # NotebookLM 구조화 데이터
        notebooklm_data = {
            "document_type": "brand_collaboration_analysis",
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "source": "Project Sonar",
                "version": "1.0"
            },
            "entities": entities,
            "relationships": relationships,
            "content": {
                "brand_profile": brand_data,
                "resonance_analysis": resonance_data,
                "collaboration_brief": brief
            },
            "suggested_prompts": [
                f"{brand_data.get('brand_name')}의 핵심 강점은 무엇인가요?",
                f"공명 지수 상위 3개 요인을 설명해주세요",
                f"제안된 파트너십 아이디어 중 가장 실행 가능한 것은?",
                f"{brand_data.get('brand_name')}와 경쟁하는 브랜드는?"
            ]
        }

        logger.info(f"[{self.agent_id}] NotebookLM data prepared with {len(entities['brands'])} brands")

        return notebooklm_data


# Singleton instance
content_strategy_agent = ContentStrategyAgent()
