"""
Analytics API Router
Phase 2C: Analytical Core

Endpoints for:
- Platform overview metrics
- Product analytics
- Content analytics
- Sentiment analysis
- Trend tracking
- Cohort analysis
- Attribution reports
- Predictive analytics
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from services.analytics_engine import get_analytics_engine
from services.sentiment_analyzer import get_sentiment_analyzer
from services.trend_tracker import get_trend_tracker, TrendCategory

router = APIRouter()


@router.get("/overview")
async def get_platform_overview(
    days_back: int = Query(30, ge=1, le=365, description="Days to analyze")
):
    """
    Get platform overview metrics

    Returns high-level metrics across:
    - Revenue (Shopify)
    - Engagement (Platform)
    - Conversion (Attribution)
    - Sentiment (UGC)
    - Trends (External)
    """
    analytics = get_analytics_engine()
    return await analytics.get_platform_overview(days_back=days_back)


@router.get("/products/{product_id}")
async def get_product_analytics(
    product_id: str,
    days_back: int = Query(30, ge=1, le=365)
):
    """
    Get comprehensive product analytics

    Includes:
    - Performance metrics (views, clicks, purchases)
    - Sentiment analysis from UGC
    - Related market trends
    - Recommendations
    """
    analytics = get_analytics_engine()
    return await analytics.get_product_analytics(
        product_id=product_id,
        days_back=days_back
    )


@router.get("/content")
async def get_content_analytics(
    content_id: Optional[str] = None,
    days_back: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get content performance analytics

    Measures:
    - Views, clicks, conversions
    - Attributed revenue
    - ROI
    - Content-to-commerce effectiveness

    If content_id is provided, returns single content.
    Otherwise, returns top performing content.
    """
    analytics = get_analytics_engine()
    return await analytics.get_content_analytics(
        content_id=content_id,
        days_back=days_back,
        limit=limit
    )


@router.get("/sentiment/analyze")
async def analyze_sentiment(
    text: str = Query(..., description="Text to analyze"),
    context: Optional[str] = None
):
    """
    Analyze sentiment of text

    Uses Gemini for multi-lingual sentiment analysis.

    Returns:
    - Sentiment label (very_positive to very_negative)
    - Score (-1.0 to 1.0)
    - Confidence (0.0 to 1.0)
    - Emotions detected
    - Key phrases
    """
    import json
    sentiment_analyzer = get_sentiment_analyzer()

    context_dict = None
    if context:
        try:
            context_dict = json.loads(context)
        except:
            context_dict = {"context": context}

    result = await sentiment_analyzer.analyze_text(text, context_dict)
    return result.to_dict()


@router.get("/sentiment/products/{product_id}")
async def get_product_sentiment(
    product_id: str,
    days_back: int = Query(30, ge=1, le=365),
    min_samples: int = Query(5, ge=1)
):
    """
    Get aggregated sentiment for a product

    Analyzes:
    - Product reviews
    - Comments mentioning product
    - Chat messages about product

    Returns:
    - Overall sentiment
    - Sentiment distribution
    - Top emotions
    - Key themes
    - Trend (increasing/decreasing/stable)
    """
    sentiment_analyzer = get_sentiment_analyzer()
    return await sentiment_analyzer.analyze_product_sentiment(
        product_id=product_id,
        days_back=days_back,
        min_samples=min_samples
    )


@router.get("/sentiment/shifts")
async def detect_sentiment_shifts(
    entity_type: str = Query(..., description="Entity type: product, creator, brand"),
    entity_id: str = Query(..., description="Entity identifier"),
    threshold: float = Query(0.3, ge=0.0, le=1.0, description="Alert threshold")
):
    """
    Detect significant sentiment shifts

    Compares recent sentiment (7 days) vs baseline (30 days).
    Useful for:
    - Product quality issues
    - PR crises
    - Viral positive feedback

    Returns alert if shift exceeds threshold.
    """
    sentiment_analyzer = get_sentiment_analyzer()
    result = await sentiment_analyzer.detect_sentiment_shift(
        entity_type=entity_type,
        entity_id=entity_id,
        threshold=threshold
    )

    if result:
        return result
    else:
        return {"message": "No significant sentiment shift detected"}


@router.get("/trends")
async def get_trends(
    categories: Optional[List[str]] = Query(None, description="Trend categories to filter"),
    min_confidence: float = Query(0.6, ge=0.0, le=1.0)
):
    """
    Get current market trends

    Detects trends across categories:
    - product: New product types
    - flavor: Flavor preferences
    - culture: Cultural movements
    - seasonal: Seasonal patterns
    - lifestyle: Lifestyle trends
    - health: Health/wellness trends
    - sustainability: Sustainability trends

    Returns:
    - Trend signal (emerging, growing, trending, viral)
    - Growth rate
    - Sentiment
    - Related products
    """
    trend_tracker = get_trend_tracker()

    # Convert string categories to enum
    category_enums = None
    if categories:
        category_enums = [TrendCategory(cat) for cat in categories]

    trends = await trend_tracker.detect_trends(
        categories=category_enums,
        min_confidence=min_confidence
    )

    return {
        "trends_count": len(trends),
        "trends": [t.to_dict() for t in trends]
    }


@router.get("/trends/seasonal")
async def get_seasonal_predictions(
    months_ahead: int = Query(3, ge=1, le=12)
):
    """
    Predict seasonal trends

    Based on:
    - Korean cultural calendar
    - Historical patterns
    - Seasonal weather
    - Cultural events

    Returns monthly predictions.
    """
    trend_tracker = get_trend_tracker()
    return await trend_tracker.predict_seasonal_trends(months_ahead=months_ahead)


@router.get("/trends/report")
async def get_trend_report(
    days_back: int = Query(7, ge=1, le=30)
):
    """
    Comprehensive trend report

    Includes:
    - Current trends (all categories)
    - Seasonal forecast
    - Product opportunities
    - Actionable recommendations
    """
    trend_tracker = get_trend_tracker()
    return await trend_tracker.get_trend_report(days_back=days_back)


@router.get("/trends/opportunities")
async def get_product_opportunities(
    min_confidence: float = Query(0.7, ge=0.0, le=1.0)
):
    """
    Identify new product opportunities

    Analyzes current trends to suggest:
    - New product concepts
    - Target audiences
    - Market size estimates
    - Development effort
    - Time to market
    """
    trend_tracker = get_trend_tracker()
    opportunities = await trend_tracker.identify_product_opportunities(
        min_confidence=min_confidence
    )
    return {"opportunities": opportunities}


@router.get("/trends/competitor/{competitor_name}")
async def track_competitor(
    competitor_name: str,
    days_back: int = Query(30, ge=1, le=90)
):
    """
    Track competitor activity

    Analyzes:
    - Recent launches
    - Marketing campaigns
    - Price changes
    - Market share
    - Customer sentiment
    - Differentiators vs NERDX
    """
    trend_tracker = get_trend_tracker()
    return await trend_tracker.track_competitor(
        competitor_name=competitor_name,
        days_back=days_back
    )


@router.get("/cohorts")
async def get_cohort_analysis(
    cohort_definition: str = Query("signup_month", description="How to group users"),
    metric: str = Query("retention_rate", description="What to measure")
):
    """
    Perform cohort analysis

    Cohort definitions:
    - signup_month: By signup month
    - first_purchase_month: By first purchase month

    Metrics:
    - retention_rate: User retention
    - ltv: Lifetime value
    - purchase_frequency: Purchase frequency
    """
    analytics = get_analytics_engine()
    return await analytics.get_user_cohort_analysis(
        cohort_definition=cohort_definition,
        metric=metric
    )


@router.get("/attribution")
async def get_attribution_report(
    days_back: int = Query(30, ge=1, le=365),
    model: str = Query("last_touch", description="Attribution model")
):
    """
    Generate attribution report

    Attribution models:
    - last_touch: Last content before purchase
    - first_touch: First content in journey
    - linear: Equal credit to all touchpoints
    - time_decay: More credit to recent touchpoints

    Shows which content drives purchases.
    """
    analytics = get_analytics_engine()
    return await analytics.get_attribution_report(
        days_back=days_back,
        model=model
    )


@router.get("/predictions/{prediction_type}")
async def get_predictions(
    prediction_type: str = Query(..., description="What to predict: revenue, churn, ltv"),
    horizon_days: int = Query(30, ge=7, le=90)
):
    """
    Generate predictive analytics

    Prediction types:
    - revenue: Future revenue forecast
    - churn: User churn prediction
    - ltv: Lifetime value prediction

    Returns forecast with confidence intervals.
    """
    analytics = get_analytics_engine()
    return await analytics.get_predictive_analytics(
        prediction_type=prediction_type,
        horizon_days=horizon_days
    )


@router.get("/dashboard")
async def get_dashboard_data(
    days_back: int = Query(30, ge=1, le=365)
):
    """
    Get all data for unified dashboard

    Returns:
    - Platform overview
    - Top content performance
    - Current trends
    - Recent alerts
    - Key recommendations

    Optimized single endpoint for dashboard loading.
    """
    analytics = get_analytics_engine()
    trend_tracker = get_trend_tracker()

    # Fetch data in parallel (conceptually - await each)
    overview = await analytics.get_platform_overview(days_back=days_back)
    content = await analytics.get_content_analytics(days_back=days_back, limit=5)
    trends = await trend_tracker.detect_trends(min_confidence=0.7)

    return {
        "overview": overview,
        "top_content": content.get("content", []),
        "trends": [t.to_dict() for t in trends[:5]],
        "last_updated": datetime.utcnow().isoformat()
    }
