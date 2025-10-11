"""
Shopify Webhooks Router - Phase 2B

Real-time event processing from Shopify:
- orders/paid → Record purchase in Neo4j, update WORLD MODEL
- orders/cancelled → Update Neo4j, adjust recommendations
- customers/create → Add to user graph
- customers/update → Sync profile changes
- products/update → Sync catalog changes

Closes the data loop: Content → Commerce → Analytics → Personalization
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging
import json

from services.shopify_connector import get_shopify_connector
from services.neo4j_service import get_neo4j_service
from models.api_models import WebhookResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Webhook Verification & Base Handler
# ============================================================================

async def verify_shopify_webhook(request: Request) -> bool:
    """
    Verify Shopify webhook HMAC signature

    Args:
        request: FastAPI request object

    Returns:
        True if signature is valid

    Raises:
        HTTPException if verification fails
    """
    hmac_header = request.headers.get("X-Shopify-Hmac-SHA256")

    if not hmac_header:
        logger.error("Missing HMAC header in webhook")
        raise HTTPException(status_code=401, detail="Missing HMAC signature")

    body = await request.body()

    shopify = get_shopify_connector()
    is_valid = shopify.verify_webhook(body, hmac_header)

    if not is_valid:
        logger.error("Invalid Shopify webhook signature")
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    return True


# ============================================================================
# Order Webhooks (Critical for Closed-Loop)
# ============================================================================

@router.post("/shopify/orders-paid", response_model=WebhookResponse)
async def handle_order_paid(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle orders/paid webhook

    This is the MOST CRITICAL webhook for closed-loop analytics.
    When a user makes a purchase, we:
    1. Record the purchase in Neo4j graph
    2. Link purchased products to user
    3. Update user's taste profile based on purchase
    4. Trigger recommendation engine refresh
    5. Calculate content-to-commerce attribution

    Closes the loop: User viewed content → Clicked product → Purchased
    """
    await verify_shopify_webhook(request)

    try:
        payload = await request.json()

        logger.info(f"📦 Order paid: {payload.get('order_number')} - ${payload.get('total_price')}")

        # Process in background to avoid blocking webhook response
        background_tasks.add_task(process_order_paid, payload)

        return WebhookResponse(
            success=True,
            message="Order paid webhook received",
            webhook_id=payload.get("id")
        )

    except Exception as e:
        logger.error(f"Order paid webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_order_paid(order_data: Dict[str, Any]):
    """
    Background task to process paid order

    This implements the closed-loop learning:
    1. Record purchase in graph
    2. Update user profile
    3. Adjust WORLD MODEL weights
    4. Recalculate recommendations
    """
    try:
        neo4j = get_neo4j_service()

        order_id = str(order_data["id"])
        customer_id = str(order_data.get("customer", {}).get("id"))
        total_price = float(order_data["total_price"])
        line_items = order_data.get("line_items", [])

        logger.info(f"Processing order {order_id} for customer {customer_id}")

        # 1. Record purchase in Neo4j
        purchase_query = """
        MERGE (u:User {shopify_id: $customer_id})
        ON CREATE SET
            u.user_id = 'shopify_' + $customer_id,
            u.created_at = datetime(),
            u.total_purchases = 0,
            u.lifetime_value_usd = 0.0

        CREATE (purchase:Purchase {
            purchase_id: $purchase_id,
            shopify_order_id: $order_id,
            total_amount: $total_amount,
            currency: $currency,
            timestamp: datetime(),
            order_number: $order_number
        })

        CREATE (u)-[:MADE_PURCHASE]->(purchase)

        SET u.total_purchases = u.total_purchases + 1,
            u.lifetime_value_usd = u.lifetime_value_usd + $total_amount,
            u.last_purchase_at = datetime()

        RETURN u, purchase
        """

        with neo4j.driver.session(database="nerdx") as session:
            result = session.run(
                purchase_query,
                customer_id=customer_id,
                purchase_id=f"purchase_{order_id}",
                order_id=order_id,
                total_amount=total_price,
                currency=order_data.get("currency", "USD"),
                order_number=order_data.get("order_number")
            )
            result.single()

        # 2. Link purchased products
        for item in line_items:
            product_id = str(item.get("product_id"))
            variant_id = str(item.get("variant_id"))
            quantity = item.get("quantity", 1)
            price = float(item.get("price", 0))

            product_link_query = """
            MATCH (purchase:Purchase {purchase_id: $purchase_id})
            MERGE (p:Product {shopify_id: $product_id})
            ON CREATE SET
                p.product_id = 'shopify_' + $product_id,
                p.name = $product_title

            CREATE (purchase)-[:CONTAINS {
                quantity: $quantity,
                price: $price,
                variant_id: $variant_id
            }]->(p)

            // Update product popularity
            SET p.total_purchases = coalesce(p.total_purchases, 0) + $quantity,
                p.last_purchased_at = datetime()

            RETURN p
            """

            with neo4j.driver.session(database="nerdx") as session:
                session.run(
                    product_link_query,
                    purchase_id=f"purchase_{order_id}",
                    product_id=product_id,
                    product_title=item.get("title", "Unknown"),
                    quantity=quantity,
                    price=price,
                    variant_id=variant_id
                )

        # 3. Update taste profile based on purchase
        # (This would use ML to infer preferences from purchased products)
        await update_taste_profile_from_purchase(customer_id, line_items)

        # 4. Calculate attribution (which content led to this purchase?)
        await calculate_content_attribution(customer_id, order_id)

        logger.info(f"✅ Successfully processed order {order_id}")

    except Exception as e:
        logger.error(f"Error processing order {order_id}: {e}")
        # Don't raise - we don't want to fail the webhook
        # Log error and alert monitoring system


@router.post("/shopify/orders-cancelled", response_model=WebhookResponse)
async def handle_order_cancelled(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle orders/cancelled webhook

    Update Neo4j to mark purchase as cancelled
    Adjust lifetime value
    """
    await verify_shopify_webhook(request)

    try:
        payload = await request.json()

        logger.info(f"❌ Order cancelled: {payload.get('order_number')}")

        background_tasks.add_task(process_order_cancelled, payload)

        return WebhookResponse(
            success=True,
            message="Order cancelled webhook received",
            webhook_id=payload.get("id")
        )

    except Exception as e:
        logger.error(f"Order cancelled webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_order_cancelled(order_data: Dict[str, Any]):
    """Mark purchase as cancelled in Neo4j"""
    try:
        neo4j = get_neo4j_service()
        order_id = str(order_data["id"])
        refund_amount = float(order_data["total_price"])

        cancel_query = """
        MATCH (u:User)-[:MADE_PURCHASE]->(purchase:Purchase {shopify_order_id: $order_id})
        SET purchase.status = 'cancelled',
            purchase.cancelled_at = datetime(),
            u.lifetime_value_usd = u.lifetime_value_usd - $refund_amount
        RETURN purchase
        """

        with neo4j.driver.session(database="nerdx") as session:
            result = session.run(cancel_query, order_id=order_id, refund_amount=refund_amount)
            if result.single():
                logger.info(f"✅ Marked order {order_id} as cancelled")
            else:
                logger.warning(f"Order {order_id} not found in database")

    except Exception as e:
        logger.error(f"Error processing cancelled order: {e}")


# ============================================================================
# Customer Webhooks
# ============================================================================

@router.post("/shopify/customers-create", response_model=WebhookResponse)
async def handle_customer_create(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle customers/create webhook

    Add new customer to Neo4j user graph
    """
    await verify_shopify_webhook(request)

    try:
        payload = await request.json()

        logger.info(f"👤 New customer: {payload.get('email')}")

        background_tasks.add_task(process_customer_create, payload)

        return WebhookResponse(
            success=True,
            message="Customer create webhook received",
            webhook_id=payload.get("id")
        )

    except Exception as e:
        logger.error(f"Customer create webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_customer_create(customer_data: Dict[str, Any]):
    """Add new customer to Neo4j"""
    try:
        neo4j = get_neo4j_service()

        customer_query = """
        MERGE (u:User {shopify_id: $customer_id})
        ON CREATE SET
            u.user_id = 'shopify_' + $customer_id,
            u.email = $email,
            u.name = $name,
            u.first_name = $first_name,
            u.last_name = $last_name,
            u.accepts_marketing = $accepts_marketing,
            u.created_at = datetime(),
            u.total_purchases = 0,
            u.lifetime_value_usd = 0.0,
            u.source = 'shopify'

        RETURN u
        """

        with neo4j.driver.session(database="nerdx") as session:
            session.run(
                customer_query,
                customer_id=str(customer_data["id"]),
                email=customer_data.get("email"),
                name=f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip(),
                first_name=customer_data.get("first_name"),
                last_name=customer_data.get("last_name"),
                accepts_marketing=customer_data.get("accepts_marketing", False)
            )

        logger.info(f"✅ Added customer {customer_data['id']} to Neo4j")

    except Exception as e:
        logger.error(f"Error processing customer create: {e}")


@router.post("/shopify/customers-update", response_model=WebhookResponse)
async def handle_customer_update(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle customers/update webhook

    Sync customer profile changes
    """
    await verify_shopify_webhook(request)

    try:
        payload = await request.json()

        logger.info(f"👤 Customer updated: {payload.get('email')}")

        background_tasks.add_task(process_customer_update, payload)

        return WebhookResponse(
            success=True,
            message="Customer update webhook received",
            webhook_id=payload.get("id")
        )

    except Exception as e:
        logger.error(f"Customer update webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_customer_update(customer_data: Dict[str, Any]):
    """Update customer in Neo4j"""
    try:
        neo4j = get_neo4j_service()

        update_query = """
        MATCH (u:User {shopify_id: $customer_id})
        SET u.email = $email,
            u.name = $name,
            u.accepts_marketing = $accepts_marketing,
            u.updated_at = datetime()
        RETURN u
        """

        with neo4j.driver.session(database="nerdx") as session:
            result = session.run(
                update_query,
                customer_id=str(customer_data["id"]),
                email=customer_data.get("email"),
                name=f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip(),
                accepts_marketing=customer_data.get("accepts_marketing", False)
            )

            if result.single():
                logger.info(f"✅ Updated customer {customer_data['id']}")

    except Exception as e:
        logger.error(f"Error processing customer update: {e}")


# ============================================================================
# Product Webhooks
# ============================================================================

@router.post("/shopify/products-update", response_model=WebhookResponse)
async def handle_product_update(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle products/update webhook

    Sync product catalog changes
    """
    await verify_shopify_webhook(request)

    try:
        payload = await request.json()

        logger.info(f"📦 Product updated: {payload.get('title')}")

        background_tasks.add_task(process_product_update, payload)

        return WebhookResponse(
            success=True,
            message="Product update webhook received",
            webhook_id=payload.get("id")
        )

    except Exception as e:
        logger.error(f"Product update webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_product_update(product_data: Dict[str, Any]):
    """Update product in Neo4j"""
    try:
        neo4j = get_neo4j_service()

        update_query = """
        MERGE (p:Product {shopify_id: $product_id})
        ON CREATE SET
            p.product_id = 'shopify_' + $product_id,
            p.created_at = datetime()
        SET p.name = $name,
            p.description = $description,
            p.product_type = $product_type,
            p.vendor = $vendor,
            p.is_available = $is_available,
            p.updated_at = datetime()
        RETURN p
        """

        with neo4j.driver.session(database="nerdx") as session:
            session.run(
                update_query,
                product_id=str(product_data["id"]),
                name=product_data.get("title"),
                description=product_data.get("body_html", ""),
                product_type=product_data.get("product_type"),
                vendor=product_data.get("vendor"),
                is_available=product_data.get("status") == "active"
            )

        logger.info(f"✅ Updated product {product_data['id']}")

    except Exception as e:
        logger.error(f"Error processing product update: {e}")


# ============================================================================
# Helper Functions for Closed-Loop Analytics
# ============================================================================

async def update_taste_profile_from_purchase(
    customer_id: str,
    line_items: List[Dict[str, Any]]
):
    """
    Update user's taste profile based on purchased products

    This is where ML/AI learns from purchases to improve recommendations
    """
    try:
        neo4j = get_neo4j_service()

        # Extract flavor profiles from purchased products
        flavor_query = """
        MATCH (u:User {shopify_id: $customer_id})
        MATCH (p:Product)
        WHERE p.shopify_id IN $product_ids
        AND p.flavor_profile IS NOT NULL

        WITH u, collect(p.flavor_profile) as flavors
        SET u.purchased_flavors = flavors,
            u.taste_profile_updated_at = datetime()

        RETURN u
        """

        product_ids = [str(item["product_id"]) for item in line_items]

        with neo4j.driver.session(database="nerdx") as session:
            session.run(flavor_query, customer_id=customer_id, product_ids=product_ids)

        logger.info(f"Updated taste profile for customer {customer_id}")

    except Exception as e:
        logger.error(f"Error updating taste profile: {e}")


async def calculate_content_attribution(customer_id: str, order_id: str):
    """
    Calculate which content/interactions led to this purchase

    This is THE KEY to measuring content-to-commerce effectiveness

    Tracks: User viewed content → Clicked product → Made purchase
    """
    try:
        neo4j = get_neo4j_service()

        attribution_query = """
        MATCH (u:User {shopify_id: $customer_id})
        MATCH (u)-[:VIEWED]->(content:Content)-[:FEATURES]->(p:Product)
        MATCH (purchase:Purchase {shopify_order_id: $order_id})-[:CONTAINS]->(p)
        WHERE content.viewed_at > datetime() - duration('P7D')  // Last 7 days

        CREATE (content)-[:ATTRIBUTED_TO]->(purchase)

        SET content.conversion_count = coalesce(content.conversion_count, 0) + 1,
            content.last_conversion_at = datetime()

        RETURN content, p
        """

        with neo4j.driver.session(database="nerdx") as session:
            result = session.run(
                attribution_query,
                customer_id=customer_id,
                order_id=order_id
            )

            attributions = list(result)
            if attributions:
                logger.info(f"📊 Attributed {len(attributions)} content pieces to order {order_id}")
            else:
                logger.info(f"No content attribution found for order {order_id}")

    except Exception as e:
        logger.error(f"Error calculating attribution: {e}")


# ============================================================================
# Webhook Management Endpoints
# ============================================================================

@router.get("/shopify/webhooks/list")
async def list_webhooks():
    """List all registered Shopify webhooks"""
    try:
        shopify = get_shopify_connector()
        webhooks = shopify.list_webhooks()

        return {
            "success": True,
            "count": len(webhooks),
            "webhooks": webhooks
        }

    except Exception as e:
        logger.error(f"Failed to list webhooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shopify/webhooks/register")
async def register_webhooks(callback_url: str):
    """Register all Shopify webhooks"""
    try:
        shopify = get_shopify_connector()
        webhooks = shopify.register_webhooks(callback_url)

        return {
            "success": True,
            "message": f"Registered {len(webhooks)} webhooks",
            "webhooks": webhooks
        }

    except Exception as e:
        logger.error(f"Failed to register webhooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))
