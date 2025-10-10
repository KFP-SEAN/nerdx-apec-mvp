"""
Neo4j Graph Models for NERDX World Model

Represents the knowledge graph structure:
- Products (NERD alcohol products)
- Ingredients (rice, nuruk, water sources)
- Lore (stories, cultural context)
- Users (personalization)
- Interactions (preferences, history)
"""
from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    FloatProperty,
    DateTimeProperty,
    JSONProperty,
    RelationshipTo,
    RelationshipFrom,
    UniqueIdProperty,
)
from datetime import datetime


class Product(StructuredNode):
    """NERD Product Node"""

    uid = UniqueIdProperty()
    product_id = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
    name_ko = StringProperty()
    product_type = StringProperty(required=True)  # makgeolli, soju, spritz

    # Details
    description = StringProperty()
    description_ko = StringProperty()
    abv = FloatProperty()  # Alcohol by volume
    volume_ml = IntegerProperty()

    # Pricing
    price_krw = IntegerProperty()
    price_usd = FloatProperty()

    # Inventory
    stock_quantity = IntegerProperty(default=0)
    is_available = StringProperty(default="true")

    # Special flags
    is_apec_limited = StringProperty(default="false")
    is_featured = StringProperty(default="false")

    # Metadata
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)

    # Tags and categories
    tags = JSONProperty()
    flavor_profile = JSONProperty()

    # Relationships
    made_from = RelationshipTo('Ingredient', 'MADE_FROM')
    has_story = RelationshipTo('Lore', 'HAS_STORY')
    purchased_by = RelationshipFrom('User', 'PURCHASED')
    similar_to = RelationshipTo('Product', 'SIMILAR_TO')


class Ingredient(StructuredNode):
    """Ingredient Node (rice, nuruk, water, etc.)"""

    uid = UniqueIdProperty()
    ingredient_id = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
    name_ko = StringProperty()
    ingredient_type = StringProperty(required=True)  # grain, fermentation_starter, water, fruit

    # Origin
    origin_region = StringProperty()
    origin_region_ko = StringProperty()
    farm_name = StringProperty()

    # Characteristics
    characteristics = JSONProperty()
    flavor_contribution = StringProperty()

    # Sustainability
    organic_certified = StringProperty(default="false")
    sustainability_score = FloatProperty()

    # Metadata
    created_at = DateTimeProperty(default_now=True)

    # Relationships
    used_in = RelationshipFrom('Product', 'MADE_FROM')
    sourced_from = RelationshipTo('Region', 'SOURCED_FROM')


class Lore(StructuredNode):
    """Cultural stories and brand lore"""

    uid = UniqueIdProperty()
    lore_id = StringProperty(unique_index=True, required=True)
    title = StringProperty(required=True)
    title_ko = StringProperty()

    # Content
    story_text = StringProperty()
    story_text_ko = StringProperty()
    story_type = StringProperty()  # origin, tradition, innovation, cultural

    # Context
    historical_period = StringProperty()
    cultural_significance = StringProperty()

    # Media
    media_urls = JSONProperty()  # images, videos

    # Engagement
    view_count = IntegerProperty(default=0)
    share_count = IntegerProperty(default=0)

    # Metadata
    created_at = DateTimeProperty(default_now=True)
    author = StringProperty()

    # Relationships
    related_to_product = RelationshipFrom('Product', 'HAS_STORY')
    related_to_region = RelationshipTo('Region', 'TAKES_PLACE_IN')
    read_by = RelationshipFrom('User', 'READ')


class Region(StructuredNode):
    """Korean regions (for sourcing, cultural context)"""

    uid = UniqueIdProperty()
    region_id = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
    name_ko = StringProperty()

    # Geography
    province = StringProperty()
    coordinates = JSONProperty()  # {lat, lng}

    # Characteristics
    climate = StringProperty()
    specialty_ingredients = JSONProperty()
    cultural_notes = StringProperty()

    # Tourism
    unesco_site = StringProperty(default="false")
    tourist_attractions = JSONProperty()

    # Relationships
    ingredients_from = RelationshipFrom('Ingredient', 'SOURCED_FROM')
    stories_from = RelationshipFrom('Lore', 'TAKES_PLACE_IN')


class User(StructuredNode):
    """User node for personalization"""

    uid = UniqueIdProperty()
    user_id = StringProperty(unique_index=True, required=True)

    # Profile
    name = StringProperty()
    email = StringProperty(unique_index=True)

    # Preferences
    taste_preferences = JSONProperty()  # sweet, dry, fruity, etc.
    dietary_restrictions = JSONProperty()

    # Engagement
    membership_tier = StringProperty(default="free")  # free, premium, vip
    total_purchases = IntegerProperty(default=0)
    lifetime_value_usd = FloatProperty(default=0.0)

    # CAMEO
    cameo_count = IntegerProperty(default=0)
    last_cameo_created = DateTimeProperty()

    # Metadata
    created_at = DateTimeProperty(default_now=True)
    last_active = DateTimeProperty(default_now=True)
    language_preference = StringProperty(default="en")  # en, ko, zh, ja

    # Relationships
    purchased = RelationshipTo('Product', 'PURCHASED')
    prefers = RelationshipTo('Product', 'PREFERS')
    read = RelationshipTo('Lore', 'READ')
    interacted_with = RelationshipTo('User', 'INTERACTED_WITH')


class Interaction(StructuredNode):
    """User interaction events"""

    uid = UniqueIdProperty()
    interaction_id = StringProperty(unique_index=True, required=True)
    user_id = StringProperty(required=True, index=True)

    # Event details
    event_type = StringProperty(required=True)  # view, click, purchase, cameo_create, share
    entity_type = StringProperty()  # product, lore, cameo
    entity_id = StringProperty()

    # Context
    session_id = StringProperty()
    user_agent = StringProperty()
    ip_address = StringProperty()

    # Engagement metrics
    duration_seconds = IntegerProperty()
    conversion_value_usd = FloatProperty()

    # Metadata
    timestamp = DateTimeProperty(default_now=True)
    metadata = JSONProperty()


# Utility functions for common queries

def get_product_recommendations(user_id: str, limit: int = 5):
    """Get personalized product recommendations"""
    # This would use Cypher queries for collaborative filtering
    pass


def get_user_taste_profile(user_id: str):
    """Build user taste profile from interactions"""
    pass


def find_similar_products(product_id: str, limit: int = 5):
    """Find similar products based on ingredients and lore"""
    pass
