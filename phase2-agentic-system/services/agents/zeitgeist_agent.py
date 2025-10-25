"""
Zeitgeist Agent (시대정신 에이전트) - Market Analyst
Phase 3A: Market Analysis & Trend Detection

Capabilities:
- Real-time trend detection from social media
- NERDX platform data analysis
- Product opportunity identification
- Weekly trend reporting
- Consumer sentiment tracking
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
import json

from .base_agent import BaseAgent, AgentCapability, AgentResponse

logger = logging.getLogger(__name__)


class TrendSignal(str, Enum):
    """Trend signal strength"""
    EMERGING = "emerging"  # < 1K mentions
    GROWING = "growing"    # 1K-10K mentions
    TRENDING = "trending"  # 10K-100K mentions
    VIRAL = "viral"        # > 100K mentions


class TrendCategory(str, Enum):
    """Product trend categories"""
    FLAVOR = "flavor"              # Flavor profiles
    INGREDIENT = "ingredient"      # Ingredients (honey, herbs, etc.)
    STYLE = "style"                # Beverage styles (natural wine, craft beer)
    PAIRING = "pairing"            # Food pairing trends
    OCCASION = "occasion"          # Consumption occasions
    PACKAGING = "packaging"        # Package design trends
    SUSTAINABILITY = "sustainability"  # Eco-friendly trends


class MarketTrend(BaseModel):
    """Individual market trend"""
    trend_id: str
    name: str
    category: TrendCategory
    signal: TrendSignal
    confidence: float  # 0.0-1.0
    description: str
    mentions_count: int
    growth_rate: float  # Weekly growth %
    peak_date: Optional[datetime] = None
    geographic_focus: List[str] = []  # Countries/regions
    related_keywords: List[str] = []
    sentiment_score: float = 0.5  # -1.0 to 1.0
    opportunity_score: float = 0.0  # 0.0-1.0


class MarketOpportunity(BaseModel):
    """Product opportunity derived from trends"""
    opportunity_id: str
    title: str
    description: str
    category: str
    target_segment: str
    market_size_estimate: str
    competition_level: str  # low, medium, high
    time_sensitivity: str  # immediate, short-term, long-term
    supporting_trends: List[str]  # Trend IDs
    confidence: float  # 0.0-1.0
    recommended_actions: List[str]


class WeeklyTrendReport(BaseModel):
    """Weekly trend report"""
    report_id: str
    week_start: datetime
    week_end: datetime
    top_trends: List[MarketTrend]
    opportunities: List[MarketOpportunity]
    key_insights: List[str]
    market_summary: str
    recommendation_summary: str
    generated_at: datetime = datetime.utcnow()


class ZeitgeistAgent(BaseAgent):
    """
    Zeitgeist Agent - Market Intelligence & Trend Detection

    The "시대정신" agent that captures the spirit of the times by analyzing:
    - NERDX platform behavior (views, purchases, searches)
    - Social media conversations (TikTok, Instagram, X)
    - E-commerce signals (Shopify trends)
    - Korean cultural calendar & seasonal patterns
    - Global beverage industry trends

    Output: Actionable market insights for NERD brand product development
    """

    def __init__(self, agent_id: str = "zeitgeist-001", world_model_url: Optional[str] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="zeitgeist",
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.PREDICTION
            ],
            world_model_url=world_model_url
        )

        # Trend detection thresholds
        self.emerging_threshold = 1000
        self.growing_threshold = 10000
        self.trending_threshold = 100000

    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        parameters: Dict[str, Any]
    ) -> AgentResponse:
        """
        Execute Zeitgeist task

        Task Types:
        - analyze_trends: Detect current market trends
        - identify_opportunities: Find product opportunities
        - generate_weekly_report: Create comprehensive weekly report
        - analyze_platform_data: Analyze NERDX platform behavior
        """
        start_time = datetime.utcnow()

        try:
            if task_type == "analyze_trends":
                result = await self.analyze_trends(parameters)
            elif task_type == "identify_opportunities":
                result = await self.identify_opportunities(parameters)
            elif task_type == "generate_weekly_report":
                result = await self.generate_weekly_report(parameters)
            elif task_type == "analyze_platform_data":
                result = await self.analyze_platform_data(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return self.create_response(
                task_id=task_id,
                status="success",
                confidence=result.get("confidence", 0.8),
                result=result,
                processing_time_ms=int(processing_time)
            )

        except Exception as e:
            logger.error(f"Zeitgeist task {task_id} failed: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return self.create_response(
                task_id=task_id,
                status="failed",
                confidence=0.0,
                result={},
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )

    async def analyze_trends(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze current market trends

        Parameters:
            - categories: List of trend categories to focus on
            - days_back: Number of days to analyze (default: 7)
            - min_confidence: Minimum confidence threshold

        Returns:
            List of detected trends with metadata
        """
        self.validate_capability(AgentCapability.ANALYSIS)

        categories = parameters.get("categories", list(TrendCategory))
        days_back = parameters.get("days_back", 7)
        min_confidence = parameters.get("min_confidence", 0.6)

        logger.info(f"Analyzing trends for {days_back} days across {len(categories)} categories")

        # 1. Gather data from World Model
        platform_trends = await self._get_platform_trends(days_back)

        # 2. Analyze social media signals (simulated for now)
        social_trends = await self._analyze_social_media(categories, days_back)

        # 3. Detect e-commerce trends
        ecommerce_trends = await self._analyze_ecommerce_trends(days_back)

        # 4. Synthesize trends using Claude
        synthesized_trends = await self._synthesize_trends(
            platform_trends,
            social_trends,
            ecommerce_trends,
            min_confidence
        )

        return {
            "trends": [t.model_dump() for t in synthesized_trends],
            "total_trends": len(synthesized_trends),
            "analysis_period_days": days_back,
            "confidence": 0.85,
            "data_sources": ["nerdx_platform", "social_media", "ecommerce"]
        }

    async def identify_opportunities(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify product opportunities from trends

        Parameters:
            - trend_data: List of trends to analyze (optional)
            - min_opportunity_score: Minimum opportunity score threshold
            - max_opportunities: Maximum number of opportunities to return

        Returns:
            List of ranked product opportunities
        """
        self.validate_capability(AgentCapability.PREDICTION)

        trend_data = parameters.get("trend_data")
        min_score = parameters.get("min_opportunity_score", 0.7)
        max_opportunities = parameters.get("max_opportunities", 5)

        # If no trends provided, fetch recent trends
        if not trend_data:
            trends_result = await self.analyze_trends({"days_back": 14})
            trend_data = trends_result["trends"]

        logger.info(f"Identifying opportunities from {len(trend_data)} trends")

        # Use Claude to identify opportunities
        opportunities = await self._identify_product_opportunities(
            trend_data,
            min_score
        )

        # Rank and filter
        ranked_opportunities = sorted(
            opportunities,
            key=lambda x: x.confidence,
            reverse=True
        )[:max_opportunities]

        return {
            "opportunities": [opp.model_dump() for opp in ranked_opportunities],
            "total_opportunities": len(ranked_opportunities),
            "confidence": 0.80,
            "analysis_basis": f"{len(trend_data)} market trends"
        }

    async def generate_weekly_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive weekly trend report

        Parameters:
            - week_start: Start date (optional, defaults to last Monday)
            - include_opportunities: Include product opportunities (default: True)

        Returns:
            Full weekly report with trends, opportunities, and insights
        """
        week_start = parameters.get("week_start")
        if not week_start:
            # Default to last Monday
            today = datetime.utcnow()
            week_start = today - timedelta(days=today.weekday())

        week_end = week_start + timedelta(days=7)

        logger.info(f"Generating weekly report for {week_start.date()} to {week_end.date()}")

        # Analyze trends for the week
        trends_result = await self.analyze_trends({"days_back": 7})
        trends = [MarketTrend(**t) for t in trends_result["trends"]]

        # Identify opportunities
        opportunities = []
        if parameters.get("include_opportunities", True):
            opp_result = await self.identify_opportunities({"trend_data": trends_result["trends"]})
            opportunities = [MarketOpportunity(**o) for o in opp_result["opportunities"]]

        # Generate key insights using Claude
        key_insights = await self._generate_key_insights(trends, opportunities)

        # Generate summaries
        market_summary = await self._generate_market_summary(trends)
        recommendation_summary = await self._generate_recommendation_summary(opportunities)

        report = WeeklyTrendReport(
            report_id=f"zeitgeist-report-{week_start.strftime('%Y%m%d')}",
            week_start=week_start,
            week_end=week_end,
            top_trends=trends[:10],  # Top 10 trends
            opportunities=opportunities,
            key_insights=key_insights,
            market_summary=market_summary,
            recommendation_summary=recommendation_summary
        )

        return {
            "report": report.model_dump(),
            "confidence": 0.85,
            "generated_at": datetime.utcnow().isoformat()
        }

    async def analyze_platform_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze NERDX platform behavior

        Parameters:
            - days_back: Analysis period
            - metrics: Specific metrics to analyze

        Returns:
            Platform behavior insights
        """
        days_back = parameters.get("days_back", 30)
        metrics = parameters.get("metrics", ["views", "purchases", "searches"])

        logger.info(f"Analyzing NERDX platform data for {days_back} days")

        # Get analytics from World Model
        try:
            analytics_data = await self.call_world_model(
                f"/api/v1/analytics/platform-overview?days_back={days_back}"
            )
        except Exception as e:
            logger.warning(f"Could not fetch platform analytics: {e}")
            analytics_data = {}

        # Analyze patterns using Claude
        analysis = await self._analyze_platform_patterns(analytics_data, metrics)

        return {
            "platform_insights": analysis,
            "analysis_period_days": days_back,
            "confidence": 0.75
        }

    # Helper methods

    async def _get_platform_trends(self, days_back: int) -> List[Dict[str, Any]]:
        """Fetch trends from NERDX platform (World Model)"""
        try:
            response = await self.call_world_model(
                f"/api/v1/analytics/trends?days_back={days_back}"
            )
            return response.get("trends", [])
        except Exception as e:
            logger.warning(f"Could not fetch platform trends: {e}")
            return []

    async def _analyze_social_media(
        self,
        categories: List[TrendCategory],
        days_back: int
    ) -> List[Dict[str, Any]]:
        """
        Analyze social media trends (TikTok, Instagram, X)

        Note: This is a placeholder. In production, integrate with:
        - TikTok Creator Marketplace API
        - Instagram Graph API
        - X (Twitter) API v2
        """
        # Simulated social media trends for demo
        simulated_trends = [
            {
                "keyword": "natural wine",
                "category": "style",
                "mentions": 45000,
                "growth_rate": 125.5,
                "sentiment": 0.75
            },
            {
                "keyword": "honey flavored drinks",
                "category": "flavor",
                "mentions": 12000,
                "growth_rate": 89.2,
                "sentiment": 0.85
            },
            {
                "keyword": "korean traditional alcohol",
                "category": "style",
                "mentions": 28000,
                "growth_rate": 156.3,
                "sentiment": 0.82
            }
        ]

        logger.info(f"Analyzed social media: {len(simulated_trends)} trending topics")
        return simulated_trends

    async def _analyze_ecommerce_trends(self, days_back: int) -> List[Dict[str, Any]]:
        """Analyze e-commerce trends from Shopify"""
        try:
            response = await self.call_world_model(
                f"/api/v1/analytics/product-analytics?days_back={days_back}"
            )
            return response.get("top_products", [])
        except Exception as e:
            logger.warning(f"Could not fetch e-commerce trends: {e}")
            return []

    async def _synthesize_trends(
        self,
        platform_trends: List[Dict[str, Any]],
        social_trends: List[Dict[str, Any]],
        ecommerce_trends: List[Dict[str, Any]],
        min_confidence: float
    ) -> List[MarketTrend]:
        """Synthesize trends from multiple sources using Claude"""

        synthesis_prompt = f"""
You are a market intelligence analyst for a premium beverage brand (Korean craft alcohol).

Analyze these data sources and identify the top market trends:

**NERDX Platform Trends:**
{json.dumps(platform_trends, indent=2)}

**Social Media Trends:**
{json.dumps(social_trends, indent=2)}

**E-commerce Trends:**
{json.dumps(ecommerce_trends, indent=2)}

Identify 5-10 key market trends that are relevant for premium beverage product development.

For each trend, provide:
1. Trend name (concise, descriptive)
2. Category (flavor, ingredient, style, pairing, occasion, packaging, sustainability)
3. Signal strength (emerging/growing/trending/viral based on mentions)
4. Confidence score (0.0-1.0)
5. Description (2-3 sentences)
6. Growth rate estimate (%)
7. Related keywords
8. Opportunity score for NERD brand (0.0-1.0)

Return as JSON array of trends.
"""

        try:
            response_text = await self.call_claude(
                prompt=synthesis_prompt,
                system_prompt="You are an expert market analyst specializing in beverage industry trends."
            )

            # Parse Claude's response
            # Extract JSON from response (handle markdown code blocks)
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                trends_data = json.loads(json_match.group(1))
            else:
                # Try to parse entire response as JSON
                trends_data = json.loads(response_text)

            # Convert to MarketTrend objects
            market_trends = []
            for i, trend_data in enumerate(trends_data):
                trend = MarketTrend(
                    trend_id=f"trend-{datetime.utcnow().strftime('%Y%m%d')}-{i:03d}",
                    name=trend_data.get("name", "Unknown Trend"),
                    category=TrendCategory(trend_data.get("category", "flavor")),
                    signal=TrendSignal(trend_data.get("signal", "emerging")),
                    confidence=trend_data.get("confidence", 0.5),
                    description=trend_data.get("description", ""),
                    mentions_count=trend_data.get("mentions_count", 0),
                    growth_rate=trend_data.get("growth_rate", 0.0),
                    related_keywords=trend_data.get("related_keywords", []),
                    sentiment_score=trend_data.get("sentiment_score", 0.5),
                    opportunity_score=trend_data.get("opportunity_score", 0.0)
                )

                if trend.confidence >= min_confidence:
                    market_trends.append(trend)

            return market_trends

        except Exception as e:
            logger.error(f"Trend synthesis failed: {e}")
            # Return empty list on failure
            return []

    async def _identify_product_opportunities(
        self,
        trends: List[Dict[str, Any]],
        min_score: float
    ) -> List[MarketOpportunity]:
        """Identify product opportunities using Claude"""

        opportunity_prompt = f"""
You are a product strategist for NERD, a premium Korean beverage brand.

Based on these market trends, identify concrete product opportunities:

**Market Trends:**
{json.dumps(trends, indent=2)}

**NERD Brand Profile:**
- Premium positioning (Moët Hennessy style)
- Korean heritage (makgeolli, soju, Korean spirits)
- Innovation-driven (like craft breweries + luxury)
- Target: Sophisticated millennials & Gen Z
- Values: Heritage, Craftsmanship, Storytelling

Identify 3-5 product opportunities that:
1. Align with detected trends
2. Fit NERD's brand positioning
3. Have clear market demand
4. Are feasible to produce

For each opportunity, provide:
- Title (concise product concept name)
- Description (what it is, why it's exciting)
- Category (which beverage category)
- Target segment (who will buy this)
- Market size estimate (small/medium/large)
- Competition level (low/medium/high)
- Time sensitivity (immediate/short-term/long-term)
- Supporting trend IDs
- Confidence score (0.0-1.0)
- Recommended next actions (3-5 bullet points)

Return as JSON array of opportunities.
"""

        try:
            response_text = await self.call_claude(
                prompt=opportunity_prompt,
                system_prompt="You are an expert product strategist in the premium beverage industry."
            )

            # Parse response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                opportunities_data = json.loads(json_match.group(1))
            else:
                opportunities_data = json.loads(response_text)

            # Convert to MarketOpportunity objects
            opportunities = []
            for i, opp_data in enumerate(opportunities_data):
                opp = MarketOpportunity(
                    opportunity_id=f"opp-{datetime.utcnow().strftime('%Y%m%d')}-{i:03d}",
                    title=opp_data.get("title", "Untitled Opportunity"),
                    description=opp_data.get("description", ""),
                    category=opp_data.get("category", "beverage"),
                    target_segment=opp_data.get("target_segment", "general"),
                    market_size_estimate=opp_data.get("market_size_estimate", "medium"),
                    competition_level=opp_data.get("competition_level", "medium"),
                    time_sensitivity=opp_data.get("time_sensitivity", "short-term"),
                    supporting_trends=opp_data.get("supporting_trends", []),
                    confidence=opp_data.get("confidence", 0.5),
                    recommended_actions=opp_data.get("recommended_actions", [])
                )

                if opp.confidence >= min_score:
                    opportunities.append(opp)

            return opportunities

        except Exception as e:
            logger.error(f"Opportunity identification failed: {e}")
            return []

    async def _generate_key_insights(
        self,
        trends: List[MarketTrend],
        opportunities: List[MarketOpportunity]
    ) -> List[str]:
        """Generate key insights from trends and opportunities"""

        insights = [
            f"Detected {len(trends)} active market trends across multiple categories",
            f"Identified {len(opportunities)} product opportunities with high confidence",
        ]

        # Add trend-specific insights
        viral_trends = [t for t in trends if t.signal == TrendSignal.VIRAL]
        if viral_trends:
            insights.append(f"🔥 {len(viral_trends)} viral trends detected - immediate action recommended")

        # Add high-opportunity insights
        top_opps = [o for o in opportunities if o.confidence > 0.85]
        if top_opps:
            insights.append(f"💡 {len(top_opps)} high-confidence opportunities ready for development")

        return insights

    async def _generate_market_summary(self, trends: List[MarketTrend]) -> str:
        """Generate natural language market summary"""

        summary_prompt = f"""
Summarize these market trends in 2-3 paragraphs for brand executives:

{json.dumps([t.model_dump() for t in trends[:5]], indent=2)}

Focus on:
- Overall market direction
- Key consumer preferences
- Competitive landscape insights
- Strategic implications for a premium Korean beverage brand
"""

        try:
            summary = await self.call_claude(prompt=summary_prompt, max_tokens=500)
            return summary
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Market summary unavailable due to analysis error."

    async def _generate_recommendation_summary(
        self,
        opportunities: List[MarketOpportunity]
    ) -> str:
        """Generate recommendations summary"""

        if not opportunities:
            return "No high-confidence opportunities identified this week."

        rec_prompt = f"""
Summarize these product opportunities for brand leadership:

{json.dumps([o.model_dump() for o in opportunities[:3]], indent=2)}

Provide:
- Top 3 recommended actions
- Priority order
- Expected impact
- Resource requirements
"""

        try:
            summary = await self.call_claude(prompt=rec_prompt, max_tokens=400)
            return summary
        except Exception as e:
            logger.error(f"Recommendation summary failed: {e}")
            return "Recommendations unavailable due to analysis error."

    async def _analyze_platform_patterns(
        self,
        analytics_data: Dict[str, Any],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Analyze NERDX platform behavior patterns"""

        # Use Claude to identify patterns
        pattern_prompt = f"""
Analyze this NERDX platform data and identify behavioral patterns:

{json.dumps(analytics_data, indent=2)}

Focus on these metrics: {', '.join(metrics)}

Identify:
1. User behavior patterns
2. Content preferences
3. Purchase drivers
4. Seasonal trends
5. Opportunity areas

Return as structured JSON.
"""

        try:
            response = await self.call_claude(prompt=pattern_prompt, max_tokens=1000)

            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                patterns = json.loads(json_match.group(1))
            else:
                patterns = json.loads(response)

            return patterns

        except Exception as e:
            logger.error(f"Platform pattern analysis failed: {e}")
            return {"error": str(e)}


# Singleton instance
_zeitgeist_agent = None

def get_zeitgeist_agent(world_model_url: Optional[str] = None) -> ZeitgeistAgent:
    """Get singleton Zeitgeist agent instance"""
    global _zeitgeist_agent
    if _zeitgeist_agent is None:
        _zeitgeist_agent = ZeitgeistAgent(world_model_url=world_model_url)
    return _zeitgeist_agent
