"""
Shopify Connector Service - Phase 2B

Bidirectional integration with Shopify:
- PULL: Sync products, customers, orders from Shopify → NERDX
- PUSH: Manage products on behalf of creators from NERDX → Shopify
- WEBHOOKS: Real-time event processing (orders, customers)

Implements closed-loop data pipeline for WORLD MODEL analytics
"""
import shopify
from shopify import Shop, Product, Customer, Order, Webhook
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import hmac
import hashlib

from config import settings

logger = logging.getLogger(__name__)


class ShopifyConnector:
    """
    Shopify API connector for NERDX WORLD MODEL

    Provides:
    - Product catalog sync
    - Customer data sync
    - Order tracking
    - Webhook management
    """

    def __init__(self):
        """Initialize Shopify API connection"""
        if not settings.shopify_shop_url or not settings.shopify_access_token:
            raise ValueError("Shopify credentials not configured")

        # Configure Shopify API
        self.shop_url = settings.shopify_shop_url
        self.api_version = settings.shopify_api_version

        shopify.ShopifyResource.set_site(
            f"https://{self.shop_url}/admin/api/{self.api_version}"
        )
        shopify.ShopifyResource.set_headers({
            "X-Shopify-Access-Token": settings.shopify_access_token
        })

        logger.info(f"Shopify connector initialized for {self.shop_url}")

    # ============================================================================
    # PULL: Shopify → NERDX Data Sync
    # ============================================================================

    def get_shop_info(self) -> Dict[str, Any]:
        """Get shop information"""
        try:
            shop = Shop.current()
            return {
                "name": shop.name,
                "email": shop.email,
                "domain": shop.domain,
                "currency": shop.currency,
                "timezone": shop.timezone,
                "plan": shop.plan_name
            }
        except Exception as e:
            logger.error(f"Failed to get shop info: {e}")
            raise

    def sync_products(
        self,
        limit: int = 250,
        updated_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Sync products from Shopify

        Args:
            limit: Max products per request
            updated_after: Only sync products updated after this time

        Returns:
            List of product data dicts
        """
        try:
            params = {"limit": limit, "status": "active"}

            if updated_after:
                params["updated_at_min"] = updated_after.isoformat()

            products = Product.find(**params)

            synced_products = []
            for product in products:
                product_data = self._transform_product(product)
                synced_products.append(product_data)

            logger.info(f"Synced {len(synced_products)} products from Shopify")
            return synced_products

        except Exception as e:
            logger.error(f"Product sync failed: {e}")
            raise

    def _transform_product(self, shopify_product: Product) -> Dict[str, Any]:
        """Transform Shopify product to NERDX format"""
        return {
            "shopify_id": str(shopify_product.id),
            "product_id": f"shopify_{shopify_product.id}",
            "name": shopify_product.title,
            "description": shopify_product.body_html,
            "product_type": shopify_product.product_type,
            "vendor": shopify_product.vendor,
            "tags": shopify_product.tags.split(", ") if shopify_product.tags else [],
            "price_usd": float(shopify_product.variants[0].price) if shopify_product.variants else 0.0,
            "inventory": shopify_product.variants[0].inventory_quantity if shopify_product.variants else 0,
            "is_available": shopify_product.status == "active",
            "images": [img.src for img in shopify_product.images] if shopify_product.images else [],
            "variants": [
                {
                    "id": str(v.id),
                    "title": v.title,
                    "price": float(v.price),
                    "sku": v.sku,
                    "inventory": v.inventory_quantity
                }
                for v in shopify_product.variants
            ] if shopify_product.variants else [],
            "metafields": self._get_product_metafields(shopify_product.id),
            "synced_at": datetime.utcnow().isoformat()
        }

    def _get_product_metafields(self, product_id: int) -> Dict[str, Any]:
        """Get product metafields (ar_enabled, apec_limited, etc.)"""
        try:
            metafields = shopify.Metafield.find(
                resource="products",
                resource_id=product_id
            )

            return {
                mf.key: mf.value
                for mf in metafields
                if mf.namespace == "nerdx"
            }
        except Exception as e:
            logger.warning(f"Failed to get metafields for product {product_id}: {e}")
            return {}

    def sync_customers(
        self,
        limit: int = 250,
        updated_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Sync customers from Shopify

        Args:
            limit: Max customers per request
            updated_after: Only sync customers updated after this time

        Returns:
            List of customer data dicts
        """
        try:
            params = {"limit": limit}

            if updated_after:
                params["updated_at_min"] = updated_after.isoformat()

            customers = Customer.find(**params)

            synced_customers = []
            for customer in customers:
                customer_data = self._transform_customer(customer)
                synced_customers.append(customer_data)

            logger.info(f"Synced {len(synced_customers)} customers from Shopify")
            return synced_customers

        except Exception as e:
            logger.error(f"Customer sync failed: {e}")
            raise

    def _transform_customer(self, shopify_customer: Customer) -> Dict[str, Any]:
        """Transform Shopify customer to NERDX format"""
        return {
            "shopify_id": str(shopify_customer.id),
            "user_id": f"shopify_{shopify_customer.id}",
            "email": shopify_customer.email,
            "name": f"{shopify_customer.first_name} {shopify_customer.last_name}",
            "first_name": shopify_customer.first_name,
            "last_name": shopify_customer.last_name,
            "phone": shopify_customer.phone,
            "accepts_marketing": shopify_customer.accepts_marketing,
            "email_marketing_consent": shopify_customer.email_marketing_consent,
            "tags": shopify_customer.tags.split(", ") if shopify_customer.tags else [],
            "total_spent": float(shopify_customer.total_spent) if shopify_customer.total_spent else 0.0,
            "orders_count": shopify_customer.orders_count or 0,
            "created_at": shopify_customer.created_at,
            "updated_at": shopify_customer.updated_at,
            "synced_at": datetime.utcnow().isoformat()
        }

    def sync_orders(
        self,
        limit: int = 250,
        status: str = "any",
        created_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Sync orders from Shopify

        Args:
            limit: Max orders per request
            status: Order status filter (open, closed, cancelled, any)
            created_after: Only sync orders created after this time

        Returns:
            List of order data dicts
        """
        try:
            params = {"limit": limit, "status": status, "financial_status": "paid"}

            if created_after:
                params["created_at_min"] = created_after.isoformat()

            orders = Order.find(**params)

            synced_orders = []
            for order in orders:
                order_data = self._transform_order(order)
                synced_orders.append(order_data)

            logger.info(f"Synced {len(synced_orders)} orders from Shopify")
            return synced_orders

        except Exception as e:
            logger.error(f"Order sync failed: {e}")
            raise

    def _transform_order(self, shopify_order: Order) -> Dict[str, Any]:
        """Transform Shopify order to NERDX format"""
        return {
            "shopify_id": str(shopify_order.id),
            "order_id": f"shopify_{shopify_order.id}",
            "order_number": shopify_order.order_number,
            "customer_shopify_id": str(shopify_order.customer.id) if shopify_order.customer else None,
            "email": shopify_order.email,
            "total_price": float(shopify_order.total_price),
            "subtotal_price": float(shopify_order.subtotal_price),
            "total_tax": float(shopify_order.total_tax),
            "currency": shopify_order.currency,
            "financial_status": shopify_order.financial_status,
            "fulfillment_status": shopify_order.fulfillment_status,
            "line_items": [
                {
                    "product_id": str(item.product_id),
                    "variant_id": str(item.variant_id),
                    "title": item.title,
                    "quantity": item.quantity,
                    "price": float(item.price),
                    "sku": item.sku
                }
                for item in shopify_order.line_items
            ],
            "created_at": shopify_order.created_at,
            "updated_at": shopify_order.updated_at,
            "processed_at": shopify_order.processed_at,
            "synced_at": datetime.utcnow().isoformat()
        }

    # ============================================================================
    # PUSH: NERDX → Shopify Product Management
    # ============================================================================

    def create_product(
        self,
        title: str,
        description: str,
        product_type: str,
        vendor: str = "NERDX",
        price: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create product in Shopify on behalf of creator

        Args:
            title: Product title
            description: Product description
            product_type: Product type (makgeolli, soju, etc.)
            vendor: Creator/vendor name
            price: Product price
            **kwargs: Additional product attributes

        Returns:
            Created product data
        """
        try:
            product = Product()
            product.title = title
            product.body_html = description
            product.product_type = product_type
            product.vendor = vendor
            product.status = kwargs.get("status", "draft")
            product.tags = ", ".join(kwargs.get("tags", []))

            # Create variant with price
            variant = shopify.Variant()
            variant.price = str(price)
            variant.inventory_management = "shopify"
            variant.inventory_policy = "deny"
            product.variants = [variant]

            # Save product
            success = product.save()

            if success:
                logger.info(f"Created product in Shopify: {product.id}")
                return self._transform_product(product)
            else:
                raise Exception(f"Failed to create product: {product.errors.full_messages()}")

        except Exception as e:
            logger.error(f"Product creation failed: {e}")
            raise

    def update_product_inventory(
        self,
        product_id: str,
        variant_id: str,
        quantity: int
    ) -> bool:
        """
        Update product inventory

        Args:
            product_id: Shopify product ID
            variant_id: Shopify variant ID
            quantity: New inventory quantity

        Returns:
            Success boolean
        """
        try:
            variant = shopify.Variant.find(variant_id)
            variant.inventory_quantity = quantity
            success = variant.save()

            if success:
                logger.info(f"Updated inventory for variant {variant_id}: {quantity}")
            else:
                logger.error(f"Inventory update failed: {variant.errors.full_messages()}")

            return success

        except Exception as e:
            logger.error(f"Inventory update error: {e}")
            return False

    # ============================================================================
    # WEBHOOKS: Real-time Event Processing
    # ============================================================================

    def register_webhooks(self, callback_url: str) -> List[Dict[str, Any]]:
        """
        Register webhooks for real-time events

        Args:
            callback_url: Base URL for webhook callbacks

        Returns:
            List of registered webhooks
        """
        webhook_topics = [
            "orders/paid",
            "orders/cancelled",
            "customers/create",
            "customers/update",
            "products/create",
            "products/update"
        ]

        registered = []

        for topic in webhook_topics:
            try:
                webhook = Webhook()
                webhook.topic = topic
                webhook.address = f"{callback_url}/api/v1/webhooks/shopify/{topic.replace('/', '-')}"
                webhook.format = "json"

                if webhook.save():
                    logger.info(f"Registered webhook: {topic}")
                    registered.append({
                        "id": webhook.id,
                        "topic": topic,
                        "address": webhook.address
                    })
                else:
                    logger.error(f"Failed to register {topic}: {webhook.errors.full_messages()}")

            except Exception as e:
                logger.error(f"Webhook registration error for {topic}: {e}")

        return registered

    def list_webhooks(self) -> List[Dict[str, Any]]:
        """List all registered webhooks"""
        try:
            webhooks = Webhook.find()
            return [
                {
                    "id": wh.id,
                    "topic": wh.topic,
                    "address": wh.address,
                    "created_at": wh.created_at
                }
                for wh in webhooks
            ]
        except Exception as e:
            logger.error(f"Failed to list webhooks: {e}")
            return []

    def verify_webhook(self, data: bytes, hmac_header: str) -> bool:
        """
        Verify Shopify webhook signature

        Args:
            data: Raw webhook payload
            hmac_header: HMAC from X-Shopify-Hmac-SHA256 header

        Returns:
            True if signature is valid
        """
        try:
            secret = settings.shopify_webhook_secret.encode('utf-8')
            computed_hmac = hmac.new(
                secret,
                data,
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(computed_hmac, hmac_header)

        except Exception as e:
            logger.error(f"Webhook verification error: {e}")
            return False

    # ============================================================================
    # ANALYTICS: ShopifyQL Queries
    # ============================================================================

    def get_sales_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get sales analytics using ShopifyQL

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Sales analytics data
        """
        # Note: ShopifyQL requires Shopify Plus
        # For MVP, we use order aggregation
        try:
            orders = Order.find(
                created_at_min=start_date.isoformat(),
                created_at_max=end_date.isoformat(),
                status="any",
                financial_status="paid"
            )

            total_sales = sum(float(order.total_price) for order in orders)
            total_orders = len(orders)
            average_order_value = total_sales / total_orders if total_orders > 0 else 0

            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "total_sales": total_sales,
                "total_orders": total_orders,
                "average_order_value": average_order_value,
                "currency": orders[0].currency if orders else "USD"
            }

        except Exception as e:
            logger.error(f"Analytics query failed: {e}")
            return {}


# Singleton instance
_shopify_connector: Optional[ShopifyConnector] = None


def get_shopify_connector() -> ShopifyConnector:
    """Get Shopify connector singleton"""
    global _shopify_connector
    if _shopify_connector is None:
        _shopify_connector = ShopifyConnector()
    return _shopify_connector
