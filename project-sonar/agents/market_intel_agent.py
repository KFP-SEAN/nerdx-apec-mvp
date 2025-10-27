"""
MarketIntelAgent - 시장 분석 및 브랜드 데이터 수집
WIPO, KIS, 뉴스 API 통합
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import httpx
from bs4 import BeautifulSoup

from .base_agent import BaseAgent, AgentState
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


logger = logging.getLogger(__name__)


class MarketIntelAgent(BaseAgent):
    """
    시장 인텔리전스 에이전트

    책임:
    - WIPO 글로벌 브랜드 데이터베이스에서 대한민국 브랜드 데이터 수집
    - KIS (한국신용평가정보)에서 기업 재무 데이터 수집
    - 국내 뉴스 API에서 브랜드 멘션 및 시장 감성 데이터 수집
    """

    def __init__(self, agent_id: str = "market_intel_001"):
        super().__init__(agent_id, "MarketIntelAgent")
        self.wipo_api_url = settings.wipo_api_url
        self.kis_api_url = settings.kis_api_url
        self.news_api_url = settings.news_api_url

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        작업 실행

        Args:
            task: {
                "task_type": "collect_brand_data" | "enrich_brand" | "monitor_news",
                "parameters": {
                    "country": "KR",
                    "brand_name": Optional[str],
                    "company_name": Optional[str],
                    "time_range": Optional[str]
                }
            }

        Returns:
            작업 결과
        """
        start_time = datetime.utcnow()
        task_type = task.get("task_type")
        parameters = task.get("parameters", {})

        try:
            self.update_state(AgentState.WORKING)

            if task_type == "collect_brand_data":
                result = await self._collect_brand_data(parameters)
            elif task_type == "enrich_brand":
                result = await self._enrich_brand(parameters)
            elif task_type == "monitor_news":
                result = await self._monitor_news(parameters)
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

    async def _collect_brand_data(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        WIPO에서 대한민국 브랜드 데이터 수집

        Args:
            parameters: {
                "country": "KR",
                "limit": int (default 100)
            }

        Returns:
            브랜드 데이터 리스트
        """
        country = parameters.get("country", "KR")
        limit = parameters.get("limit", 100)

        logger.info(f"[{self.agent_id}] Collecting brand data for country: {country}")

        # WIPO API 연동 (실제 구현 시 API 키 및 엔드포인트 필요)
        # 여기서는 Mock 데이터 반환
        brands = await self._fetch_wipo_brands(country, limit)

        # 각 브랜드에 대해 KIS 데이터 enrichment
        enriched_brands = []
        for brand in brands:
            try:
                financial_data = await self._fetch_kis_data(brand.get("company_name"))
                brand["financial_data"] = financial_data
                enriched_brands.append(brand)
            except Exception as e:
                logger.warning(f"Failed to enrich brand {brand.get('brand_name')}: {e}")
                enriched_brands.append(brand)

        logger.info(f"[{self.agent_id}] Collected {len(enriched_brands)} brands")

        return enriched_brands

    async def _fetch_wipo_brands(self, country: str, limit: int) -> List[Dict[str, Any]]:
        """WIPO API에서 브랜드 데이터 조회 (Mock)"""
        # 실제 구현 시 WIPO API 호출
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(self.wipo_api_url, params={"country": country})
        #     return response.json()

        # Mock 데이터
        mock_brands = [
            {
                "brand_id": f"WIPO-KR-{i:05d}",
                "brand_name": f"한국브랜드{i}",
                "company_name": f"(주)한국기업{i}",
                "nice_classification": ["35", "41", "43"],  # 니스 분류
                "registration_date": (datetime.now() - timedelta(days=i*30)).isoformat(),
                "status": "Active",
                "owner": f"대표자{i}",
                "country": "KR"
            }
            for i in range(1, min(limit + 1, 101))
        ]

        return mock_brands

    async def _fetch_kis_data(self, company_name: str) -> Dict[str, Any]:
        """
        KIS API에서 기업 재무 데이터 조회

        Args:
            company_name: 기업명

        Returns:
            재무 데이터
        """
        # 실제 구현 시 KIS API 호출
        # async with httpx.AsyncClient() as client:
        #     headers = {"Authorization": f"Bearer {settings.kis_api_key}"}
        #     response = await client.get(
        #         f"{self.kis_api_url}/companies/{company_name}",
        #         headers=headers
        #     )
        #     return response.json()

        # Mock 데이터
        return {
            "company_name": company_name,
            "annual_revenue_krw": 50_000_000_000,  # 500억
            "employee_count": 250,
            "industry_code": "47",  # 소매업
            "credit_rating": "A+",
            "business_stability_score": 85.5,
            "founded_year": 2015,
            "market_cap_krw": 150_000_000_000  # 1,500억
        }

    async def _enrich_brand(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        특정 브랜드에 대한 enrichment

        Args:
            parameters: {
                "brand_name": str,
                "company_name": str
            }

        Returns:
            Enriched 브랜드 데이터
        """
        brand_name = parameters.get("brand_name")
        company_name = parameters.get("company_name")

        logger.info(f"[{self.agent_id}] Enriching brand: {brand_name}")

        # 1. WIPO 데이터
        wipo_data = await self._fetch_wipo_brands("KR", 1)

        # 2. KIS 재무 데이터
        financial_data = await self._fetch_kis_data(company_name)

        # 3. 뉴스 데이터
        news_data = await self._monitor_news({"brand_name": brand_name, "days": 30})

        enriched_data = {
            "brand_name": brand_name,
            "company_name": company_name,
            "wipo_data": wipo_data[0] if wipo_data else {},
            "financial_data": financial_data,
            "news_data": news_data,
            "enriched_at": datetime.utcnow().isoformat()
        }

        return enriched_data

    async def _monitor_news(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        뉴스 API에서 브랜드 멘션 및 감성 분석

        Args:
            parameters: {
                "brand_name": str,
                "days": int (default 7)
            }

        Returns:
            뉴스 데이터 및 감성 분석
        """
        brand_name = parameters.get("brand_name")
        days = parameters.get("days", 7)

        logger.info(f"[{self.agent_id}] Monitoring news for: {brand_name} ({days} days)")

        # 실제 구현 시 Naver News API 호출
        # async with httpx.AsyncClient() as client:
        #     headers = {
        #         "X-Naver-Client-Id": settings.news_api_client_id,
        #         "X-Naver-Client-Secret": settings.news_api_client_secret
        #     }
        #     response = await client.get(
        #         self.news_api_url,
        #         headers=headers,
        #         params={"query": brand_name, "display": 100}
        #     )
        #     news_items = response.json().get("items", [])

        # Mock 데이터
        news_items = [
            {
                "title": f"{brand_name} 신제품 출시, 시장 반응 뜨겁다",
                "description": "업계 관계자들은 긍정적 평가",
                "pub_date": (datetime.now() - timedelta(days=i)).isoformat(),
                "link": f"https://news.example.com/{i}",
                "sentiment": "positive"
            }
            for i in range(min(days, 10))
        ]

        # 감성 분석 (간단한 키워드 기반)
        positive_count = sum(1 for item in news_items if "긍정" in item["description"] or "성장" in item["title"])
        negative_count = sum(1 for item in news_items if "부정" in item["description"] or "하락" in item["title"])
        neutral_count = len(news_items) - positive_count - negative_count

        sentiment_score = (positive_count - negative_count) / max(len(news_items), 1) * 100

        return {
            "brand_name": brand_name,
            "total_mentions": len(news_items),
            "sentiment_analysis": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
                "sentiment_score": round(sentiment_score, 2)
            },
            "recent_headlines": news_items[:5],
            "period_days": days,
            "analyzed_at": datetime.utcnow().isoformat()
        }

    async def get_brand_profile(self, brand_name: str, company_name: str) -> Dict[str, Any]:
        """
        브랜드의 종합 프로필 생성 (public 메서드)

        Args:
            brand_name: 브랜드명
            company_name: 기업명

        Returns:
            종합 브랜드 프로필
        """
        task = {
            "task_id": f"profile_{brand_name}_{datetime.utcnow().timestamp()}",
            "task_type": "enrich_brand",
            "parameters": {
                "brand_name": brand_name,
                "company_name": company_name
            }
        }

        result = await self.execute_task(task)
        return result.get("result", {})


# Singleton instance
market_intel_agent = MarketIntelAgent()
