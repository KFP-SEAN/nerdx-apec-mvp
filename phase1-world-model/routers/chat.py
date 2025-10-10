"""
Chat API Router - Maeju AI Agent
"""
from fastapi import APIRouter, HTTPException
import logging
from typing import Optional

from models.api_models import ChatRequest, ChatResponse, ProductResponse
from agents.maeju_agent import get_maeju_agent
from services.neo4j_service import get_neo4j_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat_with_maeju(request: ChatRequest):
    """
    Chat with Maeju AI storytelling agent

    This endpoint allows users to have conversations with Maeju,
    who will help them discover products through stories and recommendations.
    """
    try:
        neo4j = get_neo4j_service()
        maeju = get_maeju_agent()

        # Get or create user
        user = neo4j.get_or_create_user(request.user_id)

        # Get user context and available products
        user_context = {
            "taste_preferences": user.get("taste_preferences"),
            "membership_tier": user.get("membership_tier"),
            "total_purchases": user.get("total_purchases", 0)
        }

        # Get some products for context
        available_products = neo4j.search_products(limit=20)

        # Get conversation response from Maeju
        response = await maeju.chat(
            user_message=request.message,
            user_id=request.user_id,
            user_context=user_context,
            available_products=available_products
        )

        # Get recommended products details if any
        suggested_products = []
        if response.get("product_recommendations"):
            for product_id in response["product_recommendations"]:
                product = neo4j.get_product(product_id)
                if product:
                    suggested_products.append(ProductResponse(**_convert_product(product)))

        # Record interaction
        neo4j.record_interaction(
            user_id=request.user_id,
            event_type="chat",
            entity_type="maeju",
            metadata={
                "message": request.message[:100],  # Truncate for storage
                "session_id": request.session_id
            }
        )

        return ChatResponse(
            session_id=request.session_id or response.get("conversation_id", "default"),
            message=response.get("message", ""),
            suggested_products=suggested_products
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")


@router.post("/analyze-preferences")
async def analyze_taste_preferences(user_id: str, taste_description: str):
    """
    Analyze user's taste preferences from natural language description

    Example: "I like sweet drinks with fruity flavors, not too strong"
    """
    try:
        maeju = get_maeju_agent()
        preferences = maeju.analyze_taste_preferences(taste_description)

        # Update user preferences in database
        neo4j = get_neo4j_service()
        neo4j.update_user_preferences(
            user_id=user_id,
            preferences={"taste_preferences": preferences}
        )

        return {
            "user_id": user_id,
            "analyzed_preferences": preferences,
            "message": "Your taste preferences have been updated!"
        }

    except Exception as e:
        logger.error(f"Preference analysis error: {e}")
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
        "tags": product.get("tags"),
        "flavor_profile": product.get("flavor_profile")
    }
