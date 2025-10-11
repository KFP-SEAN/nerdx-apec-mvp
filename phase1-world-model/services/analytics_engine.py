"""
Unified Analytics Engine
Phase 2C: Analytical Core

Aggregates and analyzes data from multiple sources:
- Shopify (commerce data)
- Sentiment Analyzer (UGC sentiment)
- Trend Tracker (external trends)
- Neo4j (graph interactions)
- Platform interactions (views, clicks, conversions)

Provides unified dashboards and insights
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from services.neo4j_service import get_neo4j_service
from services.shopify_connector import get_shopify_connector
from services.sentiment_analyzer import get_sentiment_analyzer
from services.trend_tracker import get_trend_tracker

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics"""
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    SENTIMENT = "sentiment"
    GROWTH = "growth"
    RETENTION = "retention"


class TimeGranularity(str, Enum):
    """Time granularity for analytics"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class AnalyticsEngine:
    """
    Unified Analytics Engine

    Key Features:
    - Multi-source data aggregation
    - Real-time dashboards
    - Predictive analytics
    - Cohort analysis
    - Attribution modeling
    - A/B test analysis
    """

    def __init__(self):
        self.neo4j = get_neo4j_service()
        self.shopify = get_shopify_connector()
        self.sentiment = get_sentiment_analyzer()
        self.trends = get_trend_tracker()

    async def get_platform_overview(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get high-level platform metrics

        Args:
            days_back: Days to analyze

        Returns:
            Platform overview metrics
        """
        try:
            since = datetime.utcnow() - timedelta(days=days_back)

            # Get Shopify analytics
            shopify_analytics = self.shopify.get_sales_analytics(
                start_date=since,
                end_date=datetime.utcnow()
            )

            # Get graph metrics from Neo4j
            graph_metrics = await self._get_graph_metrics(days_back)

            # Get sentiment overview
            sentiment_overview = await self._get_sentiment_overview(days_back)

            # Get trend summary
            trend_summary = await self._get_trend_summary()

            return {
                "period": {
                    "start_date": since.isoformat(),
                    "end_date": datetime.utcnow().isoformat(),
                    "days": days_back
                },
                "revenue": {
                    "total": shopify_analytics.get("total_sales", 0),
                    "average_order_value": shopify_analytics.get("average_order_value", 0),
                    "orders_count": shopify_analytics.get("orders_count", 0),
                    "growth_rate": self._calculate_growth_rate(shopify_analytics)
                },
                "engagement": {
                    "total_views": graph_metrics.get("total_views", 0),
                    "total_clicks": graph_metrics.get("total_clicks", 0),
                    "total_interactions": graph_metrics.get("total_interactions", 0),
                    "active_users": graph_metrics.get("active_users", 0)
                },
                "conversion": {
                    "conversion_rate": self._calculate_conversion_rate(
                        graph_metrics.get("total_clicks", 1),
                        shopify_analytics.get("orders_count", 0)
                    ),
                    "content_attribution_rate": graph_metrics.get("attribution_rate", 0),
                    "top_converting_content": graph_metrics.get("top_content", [])
                },
                "sentiment": sentiment_overview,
                "trends": trend_summary,
                "alerts": await self._generate_alerts(graph_metrics, shopify_analytics)
            }

        except Exception as e:
            logger.error(f"Platform overview error: {e}")
            return {"error": str(e)}

    async def get_product_analytics(
        self,
        product_id: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive product analytics

        Args:
            product_id: Product identifier
            days_back: Days to analyze

        Returns:
            Product analytics report
        """
        try:
            since = datetime.utcnow() - timedelta(days=days_back)

            # Get product performance from graph
            performance = await self._get_product_performance(product_id, days_back)

            # Get product sentiment
            sentiment = await self.sentiment.analyze_product_sentiment(
                product_id,
                days_back=days_back
            )

            # Get related trends
            related_trends = await self._get_product_trends(product_id)

            return {
                "product_id": product_id,
                "period_days": days_back,
                "performance": performance,
                "sentiment": sentiment,
                "trends": related_trends,
                "recommendations": self._generate_product_recommendations(
                    performance, sentiment, related_trends
                )
            }

        except Exception as e:
            logger.error(f"Product analytics error: {e}")
            return {"product_id": product_id, "error": str(e)}

    async def get_content_analytics(
        self,
        content_id: Optional[str] = None,
        days_back: int = 30,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get content performance analytics

        Args:
            content_id: Specific content (None = all content)
            days_back: Days to analyze
            limit: Max number of content pieces

        Returns:
            Content analytics report
        """
        try:
            since = datetime.utcnow() - timedelta(days=days_back)

            # Query content performance from Neo4j
            if content_id:
                # Single content piece
                query = """
                MATCH (c:Content {content_id: $content_id})
                OPTIONAL MATCH (c)-[:VIEWED]-(u:User)
                OPTIONAL MATCH (c)-[:ATTRIBUTED_TO]->(p:Purchase)
                RETURN c,
                       count(DISTINCT u) as unique_viewers,
                       count(DISTINCT p) as conversions,
                       sum(p.total_amount) as attributed_revenue
                """
                params = {"content_id": content_id}
            else:
                # Top content pieces
                query = """
                MATCH (c:Content)
                WHERE c.published_at > $since
                OPTIONAL MATCH (c)-[:VIEWED]-(u:User)
                OPTIONAL MATCH (c)-[:ATTRIBUTED_TO]->(p:Purchase)
                WITH c,
                     count(DISTINCT u) as unique_viewers,
                     count(DISTINCT p) as conversions,
                     sum(p.total_amount) as attributed_revenue
                ORDER BY attributed_revenue DESC
                LIMIT $limit
                RETURN c, unique_viewers, conversions, attributed_revenue
                """
                params = {"since": since, "limit": limit}

            results = self.neo4j.execute_query(query, **params)

            # Format results
            content_data = []
            for record in results:
                content = record["c"]
                content_data.append({
                    "content_id": content.get("content_id"),
                    "title": content.get("title"),
                    "content_type": content.get("content_type"),
                    "views": content.get("views", 0),
                    "clicks": content.get("clicks", 0),
                    "conversions": record.get("conversions", 0),
                    "attributed_revenue": record.get("attributed_revenue", 0),
                    "conversion_rate": self._calculate_conversion_rate(
                        content.get("clicks", 1),
                        record.get("conversions", 0)
                    ),
                    "engagement_score": content.get("engagement_score", 0),
                    "roi": self._calculate_content_roi(
                        record.get("attributed_revenue", 0),
                        content.get("production_cost", 0)
                    )
                })

            return {
                "period_days": days_back,
                "content_count": len(content_data),
                "content": content_data,
                "aggregates": self._calculate_content_aggregates(content_data)
            }

        except Exception as e:
            logger.error(f"Content analytics error: {e}")
            return {"error": str(e)}

    async def get_user_cohort_analysis(
        self,
        cohort_definition: str = "signup_month",
        metric: str = "retention_rate"
    ) -> Dict[str, Any]:
        """
        Perform cohort analysis

        Args:
            cohort_definition: How to group users (signup_month, first_purchase_month)
            metric: What to measure (retention_rate, ltv, purchase_frequency)

        Returns:
            Cohort analysis data
        """
        try:
            # Query Neo4j for cohort data
            query = """
            MATCH (u:User)
            WITH u,
                 date(u.created_at).month as cohort_month,
                 date(u.created_at).year as cohort_year
            OPTIONAL MATCH (u)-[:MADE_PURCHASE]->(p:Purchase)
            RETURN cohort_year, cohort_month,
                   count(DISTINCT u) as cohort_size,
                   count(DISTINCT p) as total_purchases,
                   sum(p.total_amount) as total_revenue
            ORDER BY cohort_year, cohort_month
            """

            results = self.neo4j.execute_query(query)

            # Format cohort data
            cohorts = []
            for record in results:
                cohort_id = f"{record['cohort_year']}-{record['cohort_month']:02d}"
                cohorts.append({
                    "cohort_id": cohort_id,
                    "cohort_size": record["cohort_size"],
                    "total_purchases": record["total_purchases"],
                    "total_revenue": record["total_revenue"],
                    "avg_revenue_per_user": record["total_revenue"] / record["cohort_size"]
                        if record["cohort_size"] > 0 else 0
                })

            return {
                "cohort_definition": cohort_definition,
                "metric": metric,
                "cohorts": cohorts,
                "insights": self._generate_cohort_insights(cohorts)
            }

        except Exception as e:
            logger.error(f"Cohort analysis error: {e}")
            return {"error": str(e)}

    async def get_attribution_report(
        self,
        days_back: int = 30,
        model: str = "last_touch"
    ) -> Dict[str, Any]:
        """
        Generate attribution report

        Args:
            days_back: Days to analyze
            model: Attribution model (last_touch, first_touch, linear, time_decay)

        Returns:
            Attribution report
        """
        try:
            since = datetime.utcnow() - timedelta(days=days_back)

            # Query attribution data from Neo4j
            query = """
            MATCH (c:Content)-[:ATTRIBUTED_TO]->(p:Purchase)
            WHERE p.timestamp > $since
            RETURN c.content_id as content_id,
                   c.title as title,
                   c.content_type as content_type,
                   count(DISTINCT p) as attributed_purchases,
                   sum(p.total_amount) as attributed_revenue
            ORDER BY attributed_revenue DESC
            """

            results = self.neo4j.execute_query(query, since=since)

            # Format attribution data
            attributions = []
            for record in results:
                attributions.append({
                    "content_id": record["content_id"],
                    "title": record["title"],
                    "content_type": record["content_type"],
                    "attributed_purchases": record["attributed_purchases"],
                    "attributed_revenue": record["attributed_revenue"]
                })

            total_attributed = sum(a["attributed_revenue"] for a in attributions)

            return {
                "period_days": days_back,
                "attribution_model": model,
                "total_attributed_revenue": total_attributed,
                "attributions": attributions,
                "top_channels": self._analyze_top_channels(attributions)
            }

        except Exception as e:
            logger.error(f"Attribution report error: {e}")
            return {"error": str(e)}

    async def get_predictive_analytics(
        self,
        prediction_type: str,
        horizon_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate predictive analytics

        Args:
            prediction_type: What to predict (revenue, churn, ltv)
            horizon_days: Days to forecast

        Returns:
            Prediction results
        """
        try:
            # This would use ML models in production
            # For now, return structure
            return {
                "prediction_type": prediction_type,
                "horizon_days": horizon_days,
                "forecast": [],
                "confidence_intervals": {},
                "model_accuracy": 0.0
            }

        except Exception as e:
            logger.error(f"Predictive analytics error: {e}")
            return {"error": str(e)}

    # Helper methods

    async def _get_graph_metrics(self, days_back: int) -> Dict[str, Any]:
        """Get metrics from Neo4j graph"""
        try:
            since = datetime.utcnow() - timedelta(days=days_back)

            query = """
            MATCH (u:User)
            WHERE u.last_active > $since
            WITH count(DISTINCT u) as active_users

            MATCH (i:Interaction)
            WHERE i.timestamp > $since
            WITH active_users,
                 count(DISTINCT i) as total_interactions,
                 sum(CASE WHEN i.event_type = 'view' THEN 1 ELSE 0 END) as views,
                 sum(CASE WHEN i.event_type = 'click' THEN 1 ELSE 0 END) as clicks

            MATCH (c:Content)-[:ATTRIBUTED_TO]->(p:Purchase)
            WHERE p.timestamp > $since
            WITH active_users, total_interactions, views, clicks,
                 count(DISTINCT c) as attributed_content_count,
                 count(DISTINCT p) as attributed_purchase_count

            RETURN active_users, total_interactions, views, clicks,
                   attributed_content_count, attributed_purchase_count
            """

            result = self.neo4j.execute_query(query, since=since)

            if result:
                record = result[0]
                return {
                    "active_users": record.get("active_users", 0),
                    "total_interactions": record.get("total_interactions", 0),
                    "total_views": record.get("views", 0),
                    "total_clicks": record.get("clicks", 0),
                    "attribution_rate": self._calculate_conversion_rate(
                        record.get("clicks", 1),
                        record.get("attributed_purchase_count", 0)
                    ),
                    "top_content": []
                }

            return {}

        except Exception as e:
            logger.error(f"Graph metrics error: {e}")
            return {}

    async def _get_sentiment_overview(self, days_back: int) -> Dict[str, Any]:
        """Get sentiment overview"""
        # Placeholder - in production, aggregate from sentiment data
        return {
            "overall_score": 0.0,
            "trend": "stable",
            "distribution": {}
        }

    async def _get_trend_summary(self) -> Dict[str, Any]:
        """Get trend summary"""
        try:
            trends = await self.trends.detect_trends()
            return {
                "trending_count": len([t for t in trends if t.signal.value == "trending"]),
                "emerging_count": len([t for t in trends if t.signal.value == "emerging"]),
                "top_trend": trends[0].title if trends else None
            }
        except:
            return {}

    async def _get_product_performance(
        self,
        product_id: str,
        days_back: int
    ) -> Dict[str, Any]:
        """Get product performance metrics"""
        # Placeholder
        return {
            "views": 0,
            "clicks": 0,
            "purchases": 0,
            "revenue": 0
        }

    async def _get_product_trends(self, product_id: str) -> List[Dict[str, Any]]:
        """Get trends related to product"""
        # Placeholder
        return []

    def _calculate_growth_rate(self, analytics: Dict[str, Any]) -> float:
        """Calculate growth rate"""
        # Placeholder - in production, compare periods
        return 0.0

    def _calculate_conversion_rate(self, clicks: int, conversions: int) -> float:
        """Calculate conversion rate"""
        if clicks == 0:
            return 0.0
        return (conversions / clicks) * 100

    def _calculate_content_roi(self, revenue: float, cost: float) -> float:
        """Calculate ROI"""
        if cost == 0:
            return 0.0
        return ((revenue - cost) / cost) * 100

    def _calculate_content_aggregates(
        self,
        content_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate aggregate metrics"""
        if not content_data:
            return {}

        return {
            "total_views": sum(c["views"] for c in content_data),
            "total_clicks": sum(c["clicks"] for c in content_data),
            "total_conversions": sum(c["conversions"] for c in content_data),
            "total_revenue": sum(c["attributed_revenue"] for c in content_data),
            "avg_conversion_rate": sum(c["conversion_rate"] for c in content_data) / len(content_data),
            "best_performing_type": self._find_best_content_type(content_data)
        }

    def _find_best_content_type(
        self,
        content_data: List[Dict[str, Any]]
    ) -> str:
        """Find best performing content type"""
        type_revenue = {}
        for content in content_data:
            content_type = content["content_type"]
            type_revenue[content_type] = type_revenue.get(content_type, 0) + content["attributed_revenue"]

        if not type_revenue:
            return "none"

        return max(type_revenue, key=type_revenue.get)

    async def _generate_alerts(
        self,
        graph_metrics: Dict[str, Any],
        shopify_analytics: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate alerts based on metrics"""
        alerts = []

        # Check for sentiment shifts
        sentiment_shifts = await self.sentiment.detect_sentiment_shift(
            "platform", "overall", threshold=0.3
        )
        if sentiment_shifts:
            alerts.append({
                "level": sentiment_shifts["alert_level"],
                "message": f"Sentiment shift detected: {sentiment_shifts['direction']} ({sentiment_shifts['shift_magnitude']:.2f})"
            })

        # Check conversion rate
        conversion_rate = graph_metrics.get("attribution_rate", 0)
        if conversion_rate < 1.0:  # Less than 1%
            alerts.append({
                "level": "warning",
                "message": f"Low conversion rate detected: {conversion_rate:.2f}%"
            })

        return alerts

    def _generate_product_recommendations(
        self,
        performance: Dict[str, Any],
        sentiment: Dict[str, Any],
        trends: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate product recommendations"""
        recommendations = []

        # Example recommendation logic
        if performance.get("clicks", 0) > 100 and performance.get("purchases", 0) < 5:
            recommendations.append("High interest but low conversion - consider pricing or product positioning")

        if sentiment.get("overall_sentiment", {}).get("score", 0) < -0.3:
            recommendations.append("Negative sentiment detected - investigate customer feedback")

        return recommendations

    def _generate_cohort_insights(
        self,
        cohorts: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate cohort insights"""
        insights = []

        if len(cohorts) >= 2:
            latest = cohorts[-1]
            previous = cohorts[-2]

            if latest["avg_revenue_per_user"] > previous["avg_revenue_per_user"]:
                insights.append("Recent cohorts showing higher revenue per user")
            else:
                insights.append("Recent cohorts underperforming vs previous cohorts")

        return insights

    def _analyze_top_channels(
        self,
        attributions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze top performing channels"""
        channel_revenue = {}
        for attr in attributions:
            channel = attr["content_type"]
            channel_revenue[channel] = channel_revenue.get(channel, 0) + attr["attributed_revenue"]

        channels = [
            {"channel": channel, "revenue": revenue}
            for channel, revenue in channel_revenue.items()
        ]
        channels.sort(key=lambda x: x["revenue"], reverse=True)

        return channels


# Singleton instance
_analytics_engine = None

def get_analytics_engine() -> AnalyticsEngine:
    """Get singleton AnalyticsEngine instance"""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AnalyticsEngine()
    return _analytics_engine
