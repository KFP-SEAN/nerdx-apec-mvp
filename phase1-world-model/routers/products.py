"""
Products API Router
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from models.api_models import (
    ProductResponse,
    ProductQueryRequest,
    ErrorResponse
)
from services.neo4j_service import get_neo4j_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=List[ProductResponse])
async def get_products(
    query: Optional[str] = Query(None, description="Search query"),
    product_type: Optional[str] = Query(None, description="Product type filter"),
    min_price: Optional[float] = Query(None, description="Minimum price (USD)"),
    max_price: Optional[float] = Query(None, description="Maximum price (USD)"),
    is_apec_limited: Optional[bool] = Query(None, description="APEC limited edition only"),
    limit: int = Query(10, ge=1, le=50, description="Results limit"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Get products with optional filters
    """
    try:
        neo4j = get_neo4j_service()
        products = neo4j.search_products(
            query=query,
            product_type=product_type,
            min_price=min_price,
            max_price=max_price,
            is_apec_limited=is_apec_limited,
            limit=limit,
            offset=offset
        )

        return [ProductResponse(**_convert_product(p)) for p in products]

    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """
    Get single product by ID with full details
    """
    try:
        neo4j = get_neo4j_service()
        product_data = neo4j.get_product_with_relationships(product_id)

        if not product_data or not product_data.get("product"):
            raise HTTPException(status_code=404, detail="Product not found")

        product = product_data["product"]
        return ProductResponse(**_convert_product(product))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}/similar", response_model=List[ProductResponse])
async def get_similar_products(
    product_id: str,
    limit: int = Query(5, ge=1, le=20)
):
    """
    Get similar products based on shared ingredients
    """
    try:
        neo4j = get_neo4j_service()
        similar = neo4j.get_similar_products(product_id, limit=limit)

        return [ProductResponse(**_convert_product(p)) for p in similar]

    except Exception as e:
        logger.error(f"Error fetching similar products: {e}")
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
        "stock_quantity": product.get("stock_quantity"),
        "is_available": product.get("is_available") == "true",
        "is_apec_limited": product.get("is_apec_limited") == "true",
        "is_featured": product.get("is_featured") == "true",
        "tags": product.get("tags"),
        "flavor_profile": product.get("flavor_profile"),
        "created_at": product.get("created_at")
    }
