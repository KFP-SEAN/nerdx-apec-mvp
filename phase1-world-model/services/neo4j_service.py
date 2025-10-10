"""
Neo4j Database Service
Handles all graph database operations
"""
from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jService:
    """Neo4j database service for World Model"""

    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        logger.info(f"Connected to Neo4j at {settings.neo4j_uri}")

    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def verify_connection(self) -> bool:
        """Verify Neo4j connection"""
        try:
            with self.driver.session(database=settings.neo4j_database) as session:
                result = session.run("RETURN 1 as num")
                return result.single()["num"] == 1
        except Exception as e:
            logger.error(f"Neo4j connection failed: {e}")
            return False

    # Product Operations

    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        query = """
        MATCH (p:Product {product_id: $product_id})
        RETURN p
        """
        with self.driver.session(database=settings.neo4j_database) as session:
            result = session.run(query, product_id=product_id)
            record = result.single()
            if record:
                return dict(record["p"])
            return None

    def search_products(
        self,
        query: Optional[str] = None,
        product_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        is_apec_limited: Optional[bool] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search products with filters"""

        conditions = ["p.is_available = 'true'"]
        params = {"limit": limit, "offset": offset}

        if query:
            conditions.append("(p.name CONTAINS $query OR p.description CONTAINS $query)")
            params["query"] = query

        if product_type:
            conditions.append("p.product_type = $product_type")
            params["product_type"] = product_type

        if min_price is not None:
            conditions.append("p.price_usd >= $min_price")
            params["min_price"] = min_price

        if max_price is not None:
            conditions.append("p.price_usd <= $max_price")
            params["max_price"] = max_price

        if is_apec_limited is not None:
            conditions.append("p.is_apec_limited = $is_apec_limited")
            params["is_apec_limited"] = "true" if is_apec_limited else "false"

        where_clause = " AND ".join(conditions)

        cypher = f"""
        MATCH (p:Product)
        WHERE {where_clause}
        RETURN p
        ORDER BY p.is_featured DESC, p.created_at DESC
        SKIP $offset
        LIMIT $limit
        """

        with self.driver.session(database=settings.neo4j_database) as session:
            result = session.run(cypher, **params)
            return [dict(record["p"]) for record in result]

    def get_product_with_relationships(self, product_id: str) -> Dict[str, Any]:
        """Get product with all its relationships"""
        query = """
        MATCH (p:Product {product_id: $product_id})
        OPTIONAL MATCH (p)-[:MADE_FROM]->(i:Ingredient)
        OPTIONAL MATCH (p)-[:HAS_STORY]->(l:Lore)
        OPTIONAL MATCH (p)-[:SIMILAR_TO]->(s:Product)
        RETURN p,
               collect(DISTINCT i) as ingredients,
               collect(DISTINCT l) as lore,
               collect(DISTINCT s) as similar_products
        """
        with self.driver.session(database=settings.neo4j_database) as session:
            result = session.run(query, product_id=product_id)
            record = result.single()
            if record:
                return {
                    "product": dict(record["p"]),
                    "ingredients": [dict(i) for i in record["ingredients"] if i],
                    "lore": [dict(l) for l in record["lore"] if l],
                    "similar_products": [dict(s) for s in record["similar_products"] if s]
                }
            return {}

    # Recommendation Operations

    def get_personalized_recommendations(
        self, user_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get personalized product recommendations using collaborative filtering"""
        query = """
        MATCH (u:User {user_id: $user_id})-[:PURCHASED]->(p:Product)
        MATCH (p)<-[:PURCHASED]-(other:User)
        MATCH (other)-[:PURCHASED]->(rec:Product)
        WHERE NOT (u)-[:PURCHASED]->(rec)
        AND rec.is_available = 'true'
        WITH rec, COUNT(DISTINCT other) as score
        RETURN rec
        ORDER BY score DESC, rec.is_featured DESC
        LIMIT $limit
        """
        with self.driver.session(database=settings.neo4j_database) as session:
            result = session.run(query, user_id=user_id, limit=limit)
            return [dict(record["rec"]) for record in result]

    def get_similar_products(
        self, product_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar products based on shared ingredients"""
        query = """
        MATCH (p:Product {product_id: $product_id})-[:MADE_FROM]->(i:Ingredient)
        MATCH (similar:Product)-[:MADE_FROM]->(i)
        WHERE similar.product_id <> $product_id
        AND similar.is_available = 'true'
        WITH similar, COUNT(DISTINCT i) as common_ingredients
        RETURN similar
        ORDER BY common_ingredients DESC, similar.is_featured DESC
        LIMIT $limit
        """
        with self.driver.session(database=settings.neo4j_database) as session:
            result = session.run(query, product_id=product_id, limit=limit)
            return [dict(record["similar"]) for record in result]

    # User Operations

    def get_or_create_user(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Get existing user or create new one"""
        query = """
        MERGE (u:User {user_id: $user_id})
        ON CREATE SET
            u.created_at = datetime(),
            u.last_active = datetime(),
            u.membership_tier = 'free',
            u.total_purchases = 0,
            u.lifetime_value_usd = 0.0,
            u.cameo_count = 0
        ON MATCH SET
            u.last_active = datetime()
        SET u += $props
        RETURN u
        """
        with self.driver.session(database=settings.neo4j_database) as session:
            result = session.run(query, user_id=user_id, props=kwargs)
            record = result.single()
            return dict(record["u"]) if record else {}

    def update_user_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> bool:
        """Update user preferences"""
        query = """
        MATCH (u:User {user_id: $user_id})
        SET u += $preferences
        RETURN u
        """
        with self.driver.session(database=settings.neo4j_database) as session:
            result = session.run(query, user_id=user_id, preferences=preferences)
            return result.single() is not None

    def record_interaction(
        self,
        user_id: str,
        event_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record user interaction"""
        query = """
        MATCH (u:User {user_id: $user_id})
        CREATE (i:Interaction {
            interaction_id: randomUUID(),
            user_id: $user_id,
            event_type: $event_type,
            entity_type: $entity_type,
            entity_id: $entity_id,
            timestamp: datetime(),
            metadata: $metadata
        })
        SET u.last_active = datetime()
        """
        with self.driver.session(database=settings.neo4j_database) as session:
            session.run(
                query,
                user_id=user_id,
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                metadata=metadata or {}
            )
            return True

    # Lore Operations

    def get_lore_by_id(self, lore_id: str) -> Optional[Dict[str, Any]]:
        """Get lore by ID"""
        query = """
        MATCH (l:Lore {lore_id: $lore_id})
        SET l.view_count = coalesce(l.view_count, 0) + 1
        RETURN l
        """
        with self.driver.session(database=settings.neo4j_database) as session:
            result = session.run(query, lore_id=lore_id)
            record = result.single()
            return dict(record["l"]) if record else None

    def get_lore_for_product(self, product_id: str) -> List[Dict[str, Any]]:
        """Get all lore related to a product"""
        query = """
        MATCH (p:Product {product_id: $product_id})-[:HAS_STORY]->(l:Lore)
        RETURN l
        ORDER BY l.created_at DESC
        """
        with self.driver.session(database=settings.neo4j_database) as session:
            result = session.run(query, product_id=product_id)
            return [dict(record["l"]) for record in result]

    # Initialization

    def initialize_schema(self):
        """Create indexes and constraints"""
        constraints = [
            "CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE",
            "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
            "CREATE CONSTRAINT lore_id IF NOT EXISTS FOR (l:Lore) REQUIRE l.lore_id IS UNIQUE",
            "CREATE CONSTRAINT ingredient_id IF NOT EXISTS FOR (i:Ingredient) REQUIRE i.ingredient_id IS UNIQUE",
            "CREATE CONSTRAINT region_id IF NOT EXISTS FOR (r:Region) REQUIRE r.region_id IS UNIQUE",
        ]

        indexes = [
            "CREATE INDEX product_name IF NOT EXISTS FOR (p:Product) ON (p.name)",
            "CREATE INDEX product_type IF NOT EXISTS FOR (p:Product) ON (p.product_type)",
            "CREATE INDEX user_email IF NOT EXISTS FOR (u:User) ON (u.email)",
            "CREATE INDEX interaction_user IF NOT EXISTS FOR (i:Interaction) ON (i.user_id)",
            "CREATE INDEX interaction_timestamp IF NOT EXISTS FOR (i:Interaction) ON (i.timestamp)",
        ]

        with self.driver.session(database=settings.neo4j_database) as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created constraint: {constraint[:50]}...")
                except Exception as e:
                    logger.warning(f"Constraint creation failed (might already exist): {e}")

            for index in indexes:
                try:
                    session.run(index)
                    logger.info(f"Created index: {index[:50]}...")
                except Exception as e:
                    logger.warning(f"Index creation failed (might already exist): {e}")


# Singleton instance
_neo4j_service: Optional[Neo4jService] = None


def get_neo4j_service() -> Neo4jService:
    """Get Neo4j service singleton"""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
    return _neo4j_service
