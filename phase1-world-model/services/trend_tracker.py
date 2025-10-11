"""
Trend Tracker Service
Phase 2C: Analytical Core

Tracks external trends and market signals from:
- Social media (Twitter, Instagram, Reddit)
- News articles
- Google Trends
- Industry reports
- Competitor activity

Identifies emerging trends before they go mainstream
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio

from agents.gemini_agent import GeminiAgent

logger = logging.getLogger(__name__)


class TrendCategory(str, Enum):
    """Trend categories"""
    PRODUCT = "product"
    FLAVOR = "flavor"
    CULTURE = "culture"
    SEASONAL = "seasonal"
    LIFESTYLE = "lifestyle"
    HEALTH = "health"
    SUSTAINABILITY = "sustainability"


class TrendSignal(str, Enum):
    """Trend signal strength"""
    EMERGING = "emerging"  # Just starting, < 1000 mentions
    GROWING = "growing"    # Gaining traction, 1K-10K mentions
    TRENDING = "trending"  # Hot topic, 10K-100K mentions
    VIRAL = "viral"        # Explosive, > 100K mentions
    DECLINING = "declining"  # Past peak


class Trend:
    """
    Represents a detected trend
    """
    def __init__(
        self,
        trend_id: str,
        title: str,
        category: TrendCategory,
        signal: TrendSignal,
        description: str,
        keywords: List[str],
        mention_count: int,
        growth_rate: float,  # % growth per day
        sentiment_score: float,
        confidence: float,
        sources: List[str],
        related_products: List[str] = None,
        first_seen: datetime = None,
        last_updated: datetime = None
    ):
        self.trend_id = trend_id
        self.title = title
        self.category = category
        self.signal = signal
        self.description = description
        self.keywords = keywords
        self.mention_count = mention_count
        self.growth_rate = growth_rate
        self.sentiment_score = sentiment_score
        self.confidence = confidence
        self.sources = sources
        self.related_products = related_products or []
        self.first_seen = first_seen or datetime.utcnow()
        self.last_updated = last_updated or datetime.utcnow()

    def to_dict(self):
        return {
            "trend_id": self.trend_id,
            "title": self.title,
            "category": self.category,
            "signal": self.signal,
            "description": self.description,
            "keywords": self.keywords,
            "mention_count": self.mention_count,
            "growth_rate": self.growth_rate,
            "sentiment_score": self.sentiment_score,
            "confidence": self.confidence,
            "sources": self.sources,
            "related_products": self.related_products,
            "first_seen": self.first_seen.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }


class TrendTracker:
    """
    Tracks external trends using multiple data sources

    Key Features:
    - Multi-source trend detection (social, news, search)
    - Trend prediction before mainstream
    - Product opportunity identification
    - Competitor monitoring
    - Seasonal trend forecasting
    """

    def __init__(self):
        self.gemini = GeminiAgent()

        # Trend tracking keywords for Korean alcohol market
        self.base_keywords = [
            "makgeolli", "막걸리",
            "soju", "소주",
            "korean alcohol", "한국술",
            "traditional drink", "전통주",
            "rice wine", "쌀술",
            "fermented beverage", "발효주",
            "craft alcohol", "수제술"
        ]

        # Additional trend keywords by category
        self.category_keywords = {
            TrendCategory.FLAVOR: [
                "fruity", "sparkling", "carbonated",
                "sweet", "dry", "sour",
                "fruit-infused", "seasonal flavor"
            ],
            TrendCategory.CULTURE: [
                "korean wave", "hallyu", "한류",
                "k-culture", "korean food",
                "traditional culture", "heritage"
            ],
            TrendCategory.HEALTH: [
                "probiotic", "gut health", "유산균",
                "low alcohol", "wellness",
                "natural fermentation", "자연발효"
            ],
            TrendCategory.SUSTAINABILITY: [
                "organic", "local sourcing", "친환경",
                "sustainable", "eco-friendly",
                "farm-to-bottle", "로컬"
            ]
        }

    async def detect_trends(
        self,
        categories: Optional[List[TrendCategory]] = None,
        min_confidence: float = 0.6
    ) -> List[Trend]:
        """
        Detect current trends across categories

        Args:
            categories: Specific categories to track (None = all)
            min_confidence: Minimum confidence threshold

        Returns:
            List of detected trends
        """
        try:
            categories = categories or list(TrendCategory)
            all_trends = []

            # In production, this would query actual APIs
            # For now, we'll use AI to simulate trend detection
            for category in categories:
                trends = await self._detect_category_trends(category)
                all_trends.extend(trends)

            # Filter by confidence
            filtered_trends = [
                t for t in all_trends
                if t.confidence >= min_confidence
            ]

            # Sort by signal strength and growth rate
            filtered_trends.sort(
                key=lambda t: (
                    self._signal_priority(t.signal),
                    t.growth_rate
                ),
                reverse=True
            )

            logger.info(f"Detected {len(filtered_trends)} trends")
            return filtered_trends

        except Exception as e:
            logger.error(f"Trend detection error: {e}")
            return []

    async def _detect_category_trends(
        self,
        category: TrendCategory
    ) -> List[Trend]:
        """
        Detect trends for specific category using Gemini

        Args:
            category: Trend category to analyze

        Returns:
            List of trends for this category
        """
        try:
            # Build keyword list for this category
            keywords = self.base_keywords + self.category_keywords.get(category, [])

            # Use Gemini to analyze trends (simulated)
            prompt = f"""
Analyze current trends in the Korean alcohol market, specifically focusing on: {category.value}

Keywords to consider: {', '.join(keywords)}

Based on current market signals, identify 2-3 emerging or growing trends.

For each trend, provide:
1. Title: Brief, catchy trend name
2. Description: 2-3 sentences explaining the trend
3. Keywords: 5-7 relevant keywords
4. Mention estimate: Rough number of mentions/discussions
5. Growth rate: Estimated daily growth percentage
6. Sentiment: How positive is the trend? (-1.0 to 1.0)
7. Confidence: How confident are you this is a real trend? (0.0 to 1.0)
8. Related products: Which NERDX products could leverage this trend?

Return JSON array:
[
  {{
    "title": "Sparkling Makgeolli Renaissance",
    "description": "Carbonated makgeolli is seeing renewed interest...",
    "keywords": ["sparkling", "carbonated", "modern", "young consumers"],
    "mention_count": 5000,
    "growth_rate": 15.5,
    "sentiment_score": 0.75,
    "confidence": 0.85,
    "related_products": ["spritz", "modern makgeolli"]
  }}
]
"""

            result = await self.gemini.generate(
                prompt=prompt,
                temperature=0.7
            )

            # Parse response
            import json
            response_text = result.get("text", "")
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            trend_data = json.loads(json_str)

            # Create Trend objects
            trends = []
            for i, data in enumerate(trend_data):
                # Determine signal based on mention count
                signal = self._calculate_signal(data["mention_count"])

                trend = Trend(
                    trend_id=f"trend_{category}_{i}_{datetime.utcnow().timestamp()}",
                    title=data["title"],
                    category=category,
                    signal=signal,
                    description=data["description"],
                    keywords=data["keywords"],
                    mention_count=data["mention_count"],
                    growth_rate=data["growth_rate"],
                    sentiment_score=data["sentiment_score"],
                    confidence=data["confidence"],
                    sources=["gemini_analysis"],  # In production: real sources
                    related_products=data.get("related_products", [])
                )
                trends.append(trend)

            return trends

        except Exception as e:
            logger.error(f"Category trend detection error for {category}: {e}")
            return []

    def _calculate_signal(self, mention_count: int) -> TrendSignal:
        """Calculate trend signal based on mention count"""
        if mention_count < 1000:
            return TrendSignal.EMERGING
        elif mention_count < 10000:
            return TrendSignal.GROWING
        elif mention_count < 100000:
            return TrendSignal.TRENDING
        else:
            return TrendSignal.VIRAL

    def _signal_priority(self, signal: TrendSignal) -> int:
        """Priority ranking for sorting"""
        priority = {
            TrendSignal.VIRAL: 5,
            TrendSignal.TRENDING: 4,
            TrendSignal.GROWING: 3,
            TrendSignal.EMERGING: 2,
            TrendSignal.DECLINING: 1
        }
        return priority.get(signal, 0)

    async def predict_seasonal_trends(
        self,
        months_ahead: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Predict seasonal trends for upcoming months

        Args:
            months_ahead: Number of months to forecast

        Returns:
            List of predicted seasonal trends
        """
        try:
            # Use Gemini to predict seasonal trends
            prompt = f"""
Based on Korean cultural calendar, seasonal patterns, and alcohol consumption trends,
predict the top trends for the next {months_ahead} months.

Consider:
- Traditional Korean holidays and festivals
- Seasonal weather patterns
- Historical consumption data
- Cultural events

For each month, identify 2-3 key trends.

Return JSON:
[
  {{
    "month": "2025-11",
    "season": "Late Fall",
    "trends": [
      {{
        "title": "Warming Makgeolli Cocktails",
        "description": "Hot makgeolli drinks for cold weather",
        "opportunity": "Launch heated serving suggestions",
        "confidence": 0.8
      }}
    ]
  }}
]
"""

            result = await self.gemini.generate(
                prompt=prompt,
                temperature=0.7
            )

            # Parse response
            import json
            response_text = result.get("text", "")
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            predictions = json.loads(json_str)
            return predictions

        except Exception as e:
            logger.error(f"Seasonal trend prediction error: {e}")
            return []

    async def track_competitor(
        self,
        competitor_name: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Track competitor activity and market position

        Args:
            competitor_name: Name of competitor
            days_back: Days to analyze

        Returns:
            Competitor intelligence report
        """
        try:
            # Use Gemini to analyze competitor (simulated)
            prompt = f"""
Analyze the market activity of {competitor_name} in the Korean alcohol market
over the past {days_back} days.

Provide:
1. Recent product launches or announcements
2. Marketing campaigns or partnerships
3. Price changes
4. Market share trends
5. Customer sentiment
6. Key differentiators vs NERDX
7. Threats and opportunities

Return JSON format with structured data.
"""

            result = await self.gemini.generate(
                prompt=prompt,
                temperature=0.5
            )

            # In production, parse and structure the response
            return {
                "competitor": competitor_name,
                "period_days": days_back,
                "analysis": result.get("text", ""),
                "last_updated": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Competitor tracking error: {e}")
            return {"competitor": competitor_name, "error": str(e)}

    async def identify_product_opportunities(
        self,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Identify new product opportunities based on trends

        Args:
            min_confidence: Minimum confidence for recommendations

        Returns:
            List of product opportunities
        """
        try:
            # Detect current trends
            trends = await self.detect_trends(min_confidence=min_confidence)

            # Use Gemini to generate product ideas
            trends_summary = "\n".join([
                f"- {t.title}: {t.description} (Growth: {t.growth_rate}%/day)"
                for t in trends[:5]  # Top 5 trends
            ])

            prompt = f"""
Based on these current market trends:

{trends_summary}

Suggest 3-5 new product opportunities for NERDX.

For each opportunity:
1. Product concept name
2. Description (2-3 sentences)
3. Target audience
4. Key features
5. Estimated market size
6. Development effort (low/medium/high)
7. Time to market (weeks)
8. Confidence score (0.0 to 1.0)

Return JSON array.
"""

            result = await self.gemini.generate(
                prompt=prompt,
                temperature=0.8  # Higher for creativity
            )

            # Parse response
            import json
            response_text = result.get("text", "")
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            opportunities = json.loads(json_str)
            return opportunities

        except Exception as e:
            logger.error(f"Product opportunity identification error: {e}")
            return []

    async def get_trend_report(
        self,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Generate comprehensive trend report

        Args:
            days_back: Days to analyze

        Returns:
            Comprehensive trend report
        """
        try:
            # Detect trends across all categories
            trends = await self.detect_trends()

            # Predict seasonal trends
            seasonal = await self.predict_seasonal_trends()

            # Identify opportunities
            opportunities = await self.identify_product_opportunities()

            return {
                "report_date": datetime.utcnow().isoformat(),
                "period_days": days_back,
                "summary": {
                    "total_trends": len(trends),
                    "viral_trends": len([t for t in trends if t.signal == TrendSignal.VIRAL]),
                    "emerging_trends": len([t for t in trends if t.signal == TrendSignal.EMERGING])
                },
                "top_trends": [t.to_dict() for t in trends[:10]],
                "seasonal_forecast": seasonal,
                "product_opportunities": opportunities,
                "recommendations": self._generate_recommendations(trends, opportunities)
            }

        except Exception as e:
            logger.error(f"Trend report generation error: {e}")
            return {"error": str(e)}

    def _generate_recommendations(
        self,
        trends: List[Trend],
        opportunities: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Viral/trending alerts
        viral = [t for t in trends if t.signal in [TrendSignal.VIRAL, TrendSignal.TRENDING]]
        if viral:
            recommendations.append(
                f"URGENT: {len(viral)} viral/trending topics detected. Consider immediate content response."
            )

        # High-growth emerging trends
        high_growth = [t for t in trends if t.signal == TrendSignal.EMERGING and t.growth_rate > 20]
        if high_growth:
            recommendations.append(
                f"OPPORTUNITY: {len(high_growth)} fast-growing emerging trends. Early positioning recommended."
            )

        # Product opportunities
        if opportunities:
            recommendations.append(
                f"PRODUCT: {len(opportunities)} new product opportunities identified for development."
            )

        return recommendations


# Singleton instance
_trend_tracker = None

def get_trend_tracker() -> TrendTracker:
    """Get singleton TrendTracker instance"""
    global _trend_tracker
    if _trend_tracker is None:
        _trend_tracker = TrendTracker()
    return _trend_tracker
