"""
Recommendations API Router
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging

from models.api_models import RecommendationResponse, ProductResponse
from services.neo4j_service import get_neo4j_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{user_id}", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    user_id: str,
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations")
):
    """
    Get personalized product recommendations for a user

    Uses collaborative filtering based on purchase history
    and taste preferences.
    """
    try:
        neo4j = get_neo4j_service()

        # Ensure user exists
        user = neo4j.get_or_create_user(user_id)

        # Get recommendations
        recommendations = neo4j.get_personalized_recommendations(user_id, limit=limit)

        if not recommendations:
            # Fallback to featured products if no personalized recs
            recommendations = neo4j.search_products(
                is_apec_limited=None,
                limit=limit
            )
            reason = "Featured products for new members"
            confidence = 0.5
        else:
            reason = "Based on your taste preferences and similar users' choices"
            confidence = 0.85

        products = [ProductResponse(**_convert_product(p)) for p in recommendations]

        return RecommendationResponse(
            products=products,
            reason=reason,
            confidence_score=confidence
        )

    except Exception as e:
        logger.error(f"Error generating recommendations for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _convert_product(product: dict) -> dict:
    """Convert Neo4j product to API model"""
    return {
        "product_id": product.get("product_id"),
        "name": product.get("name"),
        "name_ko": product.get("name_ko"),
        "product_type": product.get("product_type"),
        "description": product.get("description"),
        "description_ko": product.get("description_ko"),
        "abv": product.get("abv"),
        "volume_ml": product.get("volume_ml"),
        "price_krw": product.get("price_krw"),
        "price_usd": product.get("price_usd"),
        "is_available": product.get("is_available") == "true",
        "is_apec_limited": product.get("is_apec_limited") == "true",
        "is_featured": product.get("is_featured") == "true",
        "tags": product.get("tags"),
        "flavor_profile": product.get("flavor_profile")
    }
