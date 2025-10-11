"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums

class ProductType(str, Enum):
    MAKGEOLLI = "makgeolli"
    SOJU = "soju"
    SPRITZ = "spritz"
    MIXED = "mixed"


class MembershipTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"


class EventType(str, Enum):
    VIEW = "view"
    CLICK = "click"
    PURCHASE = "purchase"
    CAMEO_CREATE = "cameo_create"
    SHARE = "share"
    CHAT = "chat"


# Request Models

class ChatRequest(BaseModel):
    """Chat with Maeju AI request"""
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Conversation session ID")
    language: Optional[str] = Field("en", description="Response language (en, ko, zh, ja)")


class ProductQueryRequest(BaseModel):
    """Query products request"""
    query: Optional[str] = Field(None, description="Search query")
    product_type: Optional[ProductType] = Field(None, description="Filter by product type")
    min_price: Optional[float] = Field(None, description="Minimum price (USD)")
    max_price: Optional[float] = Field(None, description="Maximum price (USD)")
    is_apec_limited: Optional[bool] = Field(None, description="APEC limited edition only")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    limit: int = Field(10, ge=1, le=50, description="Number of results")
    offset: int = Field(0, ge=0, description="Pagination offset")


class UserPreferenceUpdate(BaseModel):
    """Update user preferences"""
    user_id: str
    taste_preferences: Optional[Dict[str, Any]] = None
    dietary_restrictions: Optional[List[str]] = None
    language_preference: Optional[str] = None


class InteractionEvent(BaseModel):
    """Track user interaction"""
    user_id: str
    event_type: EventType
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Response Models

class ProductResponse(BaseModel):
    """Product information response"""
    product_id: str
    name: str
    name_ko: Optional[str] = None
    product_type: str
    description: Optional[str] = None
    description_ko: Optional[str] = None
    abv: Optional[float] = None
    volume_ml: Optional[int] = None
    price_krw: Optional[int] = None
    price_usd: Optional[float] = None
    stock_quantity: Optional[int] = None
    is_available: bool = True
    is_apec_limited: bool = False
    is_featured: bool = False
    tags: Optional[List[str]] = None
    flavor_profile: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class IngredientResponse(BaseModel):
    """Ingredient information"""
    ingredient_id: str
    name: str
    name_ko: Optional[str] = None
    ingredient_type: str
    origin_region: Optional[str] = None
    origin_region_ko: Optional[str] = None
    characteristics: Optional[Dict[str, Any]] = None
    organic_certified: bool = False


class LoreResponse(BaseModel):
    """Lore/story response"""
    lore_id: str
    title: str
    title_ko: Optional[str] = None
    story_text: Optional[str] = None
    story_text_ko: Optional[str] = None
    story_type: Optional[str] = None
    historical_period: Optional[str] = None
    media_urls: Optional[Dict[str, Any]] = None
    view_count: int = 0
    share_count: int = 0
    created_at: Optional[datetime] = None


class ChatResponse(BaseModel):
    """Chat response from Maeju AI"""
    session_id: str
    message: str
    suggested_products: Optional[List[ProductResponse]] = None
    related_lore: Optional[List[LoreResponse]] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RecommendationResponse(BaseModel):
    """Product recommendation response"""
    products: List[ProductResponse]
    reason: str
    confidence_score: float = Field(ge=0.0, le=1.0)


class UserProfileResponse(BaseModel):
    """User profile information"""
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    taste_preferences: Optional[Dict[str, Any]] = None
    membership_tier: str = "free"
    total_purchases: int = 0
    lifetime_value_usd: float = 0.0
    cameo_count: int = 0
    last_cameo_created: Optional[datetime] = None
    created_at: datetime
    last_active: datetime
    language_preference: str = "en"


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebhookResponse(BaseModel):
    """Shopify webhook response"""
    success: bool
    message: str
    webhook_id: Optional[str] = None
