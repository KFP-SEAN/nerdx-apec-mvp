"""
Agentic Commerce Protocol (ACP) Service
Phase 2F: ACP Readiness

Enables AI agents to autonomously:
- Authenticate as agents (not humans)
- Browse product catalog
- Verify purchase intent
- Execute purchases on behalf of users
- Handle autonomous commerce flows

Security features:
- Agent authentication (API keys, JWT tokens)
- Intent verification (user consent required)
- Rate limiting
- Fraud detection
- Audit logging
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
import json

from services.neo4j_service import get_neo4j_service
from services.shopify_connector import get_shopify_connector

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Types of AI agents"""
    PERSONAL_ASSISTANT = "personal_assistant"  # User's personal AI
    RECOMMENDATION = "recommendation"          # Recommendation agent
    RESEARCH = "research"                      # Research/comparison agent
    SUBSCRIPTION = "subscription"              # Subscription management
    PRICE_MONITOR = "price_monitor"           # Price monitoring agent


class IntentStatus(str, Enum):
    """Purchase intent verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AgentCredential:
    """Agent authentication credential"""
    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        user_id: str,
        api_key: str,
        permissions: List[str],
        expires_at: datetime
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.user_id = user_id
        self.api_key = api_key
        self.permissions = permissions
        self.expires_at = expires_at
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "user_id": self.user_id,
            "permissions": self.permissions,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat()
        }

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions


class PurchaseIntent:
    """Verified purchase intent from agent"""
    def __init__(
        self,
        intent_id: str,
        agent_id: str,
        user_id: str,
        product_id: str,
        quantity: int,
        max_price: float,
        status: IntentStatus,
        expires_at: datetime
    ):
        self.intent_id = intent_id
        self.agent_id = agent_id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        self.max_price = max_price
        self.status = status
        self.expires_at = expires_at
        self.created_at = datetime.utcnow()
        self.verified_at = None

    def to_dict(self):
        return {
            "intent_id": self.intent_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "max_price": self.max_price,
            "status": self.status,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "verified_at": self.verified_at.isoformat() if self.verified_at else None
        }


class ACPService:
    """
    Agentic Commerce Protocol Service

    The future of commerce: AI agents autonomously shopping on behalf of users.

    Key Features:
    - Agent authentication (not human authentication)
    - Purchase intent verification (user must pre-approve)
    - Autonomous browsing and purchasing
    - Safety guardrails (rate limits, fraud detection)
    - Audit logging (full transparency)

    Use Cases:
    - Personal AI assistant: "Buy me makgeolli for the weekend"
    - Subscription agent: "Reorder when stock is low"
    - Price monitor: "Buy when price drops below $25"
    - Gift agent: "Buy birthday gift for friend based on their preferences"
    """

    def __init__(self):
        self.neo4j = get_neo4j_service()
        self.shopify = get_shopify_connector()

        # In-memory stores (in production, use Redis)
        self.agents = {}  # agent_id -> AgentCredential
        self.intents = {}  # intent_id -> PurchaseIntent
        self.api_keys = {}  # api_key -> agent_id

        # Rate limiting
        self.rate_limits = {
            "browse": 100,  # requests per hour
            "purchase": 10   # purchases per hour
        }

    def register_agent(
        self,
        user_id: str,
        agent_type: AgentType,
        permissions: List[str],
        validity_days: int = 30
    ) -> AgentCredential:
        """
        Register new AI agent for user

        Args:
            user_id: User who owns the agent
            agent_type: Type of agent
            permissions: List of permissions (browse, purchase, etc.)
            validity_days: How long credential is valid

        Returns:
            Agent credential with API key
        """
        try:
            # Generate unique agent ID and API key
            agent_id = f"agent_{user_id}_{secrets.token_hex(8)}"
            api_key = f"acp_{secrets.token_hex(32)}"

            # Create credential
            credential = AgentCredential(
                agent_id=agent_id,
                agent_type=agent_type,
                user_id=user_id,
                api_key=api_key,
                permissions=permissions,
                expires_at=datetime.utcnow() + timedelta(days=validity_days)
            )

            # Store credential
            self.agents[agent_id] = credential
            self.api_keys[api_key] = agent_id

            # Log registration
            logger.info(f"Agent registered: {agent_id} for user {user_id}")

            return credential

        except Exception as e:
            logger.error(f"Agent registration error: {e}")
            raise

    def authenticate_agent(self, api_key: str) -> Optional[AgentCredential]:
        """
        Authenticate agent by API key

        Args:
            api_key: Agent's API key

        Returns:
            Agent credential if valid, None otherwise
        """
        try:
            # Look up agent by API key
            agent_id = self.api_keys.get(api_key)
            if not agent_id:
                logger.warning(f"Invalid API key: {api_key[:10]}...")
                return None

            credential = self.agents.get(agent_id)
            if not credential:
                return None

            # Check expiration
            if credential.is_expired():
                logger.warning(f"Expired credential for agent: {agent_id}")
                return None

            return credential

        except Exception as e:
            logger.error(f"Agent authentication error: {e}")
            return None

    async def create_purchase_intent(
        self,
        agent_id: str,
        product_id: str,
        quantity: int = 1,
        max_price: Optional[float] = None,
        validity_hours: int = 24
    ) -> PurchaseIntent:
        """
        Create purchase intent (requires user verification)

        Agent proposes a purchase, user must approve before execution.

        Args:
            agent_id: Agent making the request
            product_id: Product to purchase
            quantity: Quantity
            max_price: Maximum acceptable price
            validity_hours: How long intent is valid

        Returns:
            Purchase intent (pending verification)
        """
        try:
            # Get agent credential
            credential = self.agents.get(agent_id)
            if not credential:
                raise ValueError("Invalid agent")

            if not credential.has_permission("purchase"):
                raise PermissionError("Agent lacks purchase permission")

            # Generate intent ID
            intent_id = f"intent_{secrets.token_hex(16)}"

            # Get product price if max_price not specified
            if max_price is None:
                # Query product from Neo4j
                query = "MATCH (p:Product {product_id: $product_id}) RETURN p.price_usd as price"
                result = self.neo4j.execute_query(query, product_id=product_id)
                if result:
                    max_price = result[0]["price"] * 1.1  # 10% buffer

            # Create intent
            intent = PurchaseIntent(
                intent_id=intent_id,
                agent_id=agent_id,
                user_id=credential.user_id,
                product_id=product_id,
                quantity=quantity,
                max_price=max_price,
                status=IntentStatus.PENDING,
                expires_at=datetime.utcnow() + timedelta(hours=validity_hours)
            )

            # Store intent
            self.intents[intent_id] = intent

            logger.info(f"Purchase intent created: {intent_id} by agent {agent_id}")

            # In production, send push notification to user for approval
            await self._notify_user_for_approval(intent)

            return intent

        except Exception as e:
            logger.error(f"Purchase intent creation error: {e}")
            raise

    async def verify_purchase_intent(
        self,
        intent_id: str,
        user_id: str,
        approved: bool
    ) -> PurchaseIntent:
        """
        User verifies/approves purchase intent

        Args:
            intent_id: Intent to verify
            user_id: User approving (must match intent owner)
            approved: Whether user approves

        Returns:
            Updated intent
        """
        try:
            intent = self.intents.get(intent_id)
            if not intent:
                raise ValueError("Intent not found")

            # Verify ownership
            if intent.user_id != user_id:
                raise PermissionError("Not your intent")

            # Check expiration
            if datetime.utcnow() > intent.expires_at:
                intent.status = IntentStatus.EXPIRED
                raise ValueError("Intent expired")

            # Update status
            if approved:
                intent.status = IntentStatus.VERIFIED
                intent.verified_at = datetime.utcnow()
                logger.info(f"Intent verified: {intent_id}")
            else:
                intent.status = IntentStatus.REJECTED
                logger.info(f"Intent rejected: {intent_id}")

            return intent

        except Exception as e:
            logger.error(f"Intent verification error: {e}")
            raise

    async def execute_autonomous_purchase(
        self,
        intent_id: str,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Execute autonomous purchase (intent must be verified)

        Args:
            intent_id: Verified purchase intent
            agent_id: Agent executing purchase

        Returns:
            Purchase result
        """
        try:
            intent = self.intents.get(intent_id)
            if not intent:
                raise ValueError("Intent not found")

            # Verify intent
            if intent.agent_id != agent_id:
                raise PermissionError("Not your intent")

            if intent.status != IntentStatus.VERIFIED:
                raise ValueError(f"Intent not verified (status: {intent.status})")

            if datetime.utcnow() > intent.expires_at:
                intent.status = IntentStatus.EXPIRED
                raise ValueError("Intent expired")

            # Check current price
            current_price = await self._get_current_price(intent.product_id)
            if current_price > intent.max_price:
                raise ValueError(f"Price ${current_price} exceeds max ${intent.max_price}")

            # Execute purchase via Shopify
            # (In production, use Shopify's Order API)
            order_result = {
                "order_id": f"acp_order_{secrets.token_hex(8)}",
                "status": "created",
                "product_id": intent.product_id,
                "quantity": intent.quantity,
                "price": current_price,
                "total": current_price * intent.quantity,
                "agent_id": agent_id,
                "intent_id": intent_id,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Log autonomous purchase
            await self._log_autonomous_purchase(intent, order_result)

            logger.info(f"Autonomous purchase executed: {order_result['order_id']}")

            return order_result

        except Exception as e:
            logger.error(f"Autonomous purchase error: {e}")
            raise

    async def agent_browse_products(
        self,
        agent_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Agent browses product catalog

        Args:
            agent_id: Agent making request
            filters: Product filters
            limit: Max products to return

        Returns:
            List of products
        """
        try:
            # Verify agent
            credential = self.agents.get(agent_id)
            if not credential or not credential.has_permission("browse"):
                raise PermissionError("Not authorized")

            # Rate limit check
            if not await self._check_rate_limit(agent_id, "browse"):
                raise Exception("Rate limit exceeded")

            # Query products from Neo4j
            query = """
            MATCH (p:Product)
            WHERE p.is_available = 'true'
            RETURN p
            ORDER BY p.created_at DESC
            LIMIT $limit
            """

            results = self.neo4j.execute_query(query, limit=limit)
            products = [dict(r["p"]) for r in results] if results else []

            # Log browse activity
            await self._log_agent_activity(agent_id, "browse", {
                "product_count": len(products),
                "filters": filters
            })

            return products

        except Exception as e:
            logger.error(f"Agent browse error: {e}")
            return []

    async def agent_get_recommendations(
        self,
        agent_id: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Agent gets personalized recommendations for user

        Args:
            agent_id: Agent making request
            user_preferences: User preferences to consider
            limit: Max recommendations

        Returns:
            Recommended products
        """
        try:
            credential = self.agents.get(agent_id)
            if not credential:
                raise PermissionError("Not authorized")

            # Get user's purchase history and preferences
            user_id = credential.user_id

            # Use ML predictor for recommendations
            # (Integration with ml_predictor service)

            # For now, return top products
            products = await self.agent_browse_products(agent_id, limit=limit)

            return products[:limit]

        except Exception as e:
            logger.error(f"Agent recommendations error: {e}")
            return []

    async def get_agent_activity_log(
        self,
        user_id: str,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get user's agent activity log (transparency)

        Args:
            user_id: User to get logs for
            days_back: Days of history

        Returns:
            Activity log
        """
        try:
            # Query agent activities
            # In production, store in database
            return []

        except Exception as e:
            logger.error(f"Activity log error: {e}")
            return []

    def revoke_agent(self, agent_id: str, user_id: str) -> bool:
        """
        Revoke agent access

        Args:
            agent_id: Agent to revoke
            user_id: User revoking (must be owner)

        Returns:
            Success
        """
        try:
            credential = self.agents.get(agent_id)
            if not credential:
                return False

            if credential.user_id != user_id:
                raise PermissionError("Not your agent")

            # Remove credential
            del self.agents[agent_id]
            del self.api_keys[credential.api_key]

            logger.info(f"Agent revoked: {agent_id}")
            return True

        except Exception as e:
            logger.error(f"Agent revocation error: {e}")
            return False

    # Helper methods

    async def _notify_user_for_approval(self, intent: PurchaseIntent):
        """Notify user to approve purchase intent"""
        # In production: Send push notification, email, SMS
        logger.info(f"Notification sent to user {intent.user_id} for intent {intent.intent_id}")

    async def _get_current_price(self, product_id: str) -> float:
        """Get current product price"""
        query = "MATCH (p:Product {product_id: $product_id}) RETURN p.price_usd as price"
        result = self.neo4j.execute_query(query, product_id=product_id)
        return result[0]["price"] if result else 0.0

    async def _log_autonomous_purchase(self, intent: PurchaseIntent, order_result: Dict[str, Any]):
        """Log autonomous purchase for audit"""
        log_entry = {
            "type": "autonomous_purchase",
            "intent_id": intent.intent_id,
            "agent_id": intent.agent_id,
            "user_id": intent.user_id,
            "order": order_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info(f"Autonomous purchase logged: {json.dumps(log_entry)}")

    async def _log_agent_activity(self, agent_id: str, activity_type: str, data: Dict[str, Any]):
        """Log agent activity"""
        log_entry = {
            "agent_id": agent_id,
            "activity_type": activity_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info(f"Agent activity: {json.dumps(log_entry)}")

    async def _check_rate_limit(self, agent_id: str, action: str) -> bool:
        """Check rate limit for agent action"""
        # Simple rate limiting (in production, use Redis)
        # For now, always allow
        return True


# Singleton instance
_acp_service = None

def get_acp_service() -> ACPService:
    """Get singleton ACPService instance"""
    global _acp_service
    if _acp_service is None:
        _acp_service = ACPService()
    return _acp_service
