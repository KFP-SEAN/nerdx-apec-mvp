"""
Users API Router
"""
from fastapi import APIRouter, HTTPException
import logging

from models.api_models import (
    UserProfileResponse,
    UserPreferenceUpdate,
    InteractionEvent
)
from services.neo4j_service import get_neo4j_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str):
    """Get user profile"""
    try:
        neo4j = get_neo4j_service()
        user = neo4j.get_or_create_user(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserProfileResponse(
            user_id=user.get("user_id"),
            name=user.get("name"),
            email=user.get("email"),
            taste_preferences=user.get("taste_preferences"),
            membership_tier=user.get("membership_tier", "free"),
            total_purchases=user.get("total_purchases", 0),
            lifetime_value_usd=user.get("lifetime_value_usd", 0.0),
            cameo_count=user.get("cameo_count", 0),
            last_cameo_created=user.get("last_cameo_created"),
            created_at=user.get("created_at"),
            last_active=user.get("last_active"),
            language_preference=user.get("language_preference", "en")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/preferences")
async def update_preferences(user_id: str, update: UserPreferenceUpdate):
    """Update user preferences"""
    try:
        neo4j = get_neo4j_service()

        preferences = {}
        if update.taste_preferences:
            preferences["taste_preferences"] = update.taste_preferences
        if update.dietary_restrictions:
            preferences["dietary_restrictions"] = update.dietary_restrictions
        if update.language_preference:
            preferences["language_preference"] = update.language_preference

        success = neo4j.update_user_preferences(user_id, preferences)

        if not success:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "message": "Preferences updated successfully",
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/interactions")
async def track_interaction(user_id: str, event: InteractionEvent):
    """Track user interaction event"""
    try:
        neo4j = get_neo4j_service()

        success = neo4j.record_interaction(
            user_id=user_id,
            event_type=event.event_type.value,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            metadata=event.metadata
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to record interaction")

        return {
            "message": "Interaction recorded",
            "user_id": user_id,
            "event_type": event.event_type
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
