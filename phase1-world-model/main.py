"""
Phase 1: World Model API
FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from config import settings
from services.neo4j_service import get_neo4j_service
from routers import products, chat, users, recommendations
from models.api_models import HealthCheckResponse, ErrorResponse

# Logging setup
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Phase 1: World Model API")

    # Initialize Neo4j
    neo4j_service = get_neo4j_service()
    if neo4j_service.verify_connection():
        logger.info("✅ Neo4j connection verified")
        # Initialize schema
        neo4j_service.initialize_schema()
    else:
        logger.error("❌ Neo4j connection failed")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Phase 1: World Model API")
    neo4j_service.close()


# Create FastAPI app
app = FastAPI(
    title="NERDX APEC MVP - Phase 1: World Model",
    description="Knowledge graph and AI storytelling API for NERDX platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    logger.info(f"📨 {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"✅ {request.method} {request.url.path} "
        f"completed in {process_time:.2f}s with status {response.status_code}"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc) if settings.api_debug else "An unexpected error occurred"
        ).dict()
    )


# Include routers
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])


# Root endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NERDX APEC MVP - Phase 1: World Model API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    neo4j_service = get_neo4j_service()
    neo4j_status = "healthy" if neo4j_service.verify_connection() else "unhealthy"

    return HealthCheckResponse(
        status="healthy" if neo4j_status == "healthy" else "degraded",
        version="1.0.0",
        services={
            "neo4j": neo4j_status,
            "api": "healthy"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level=settings.log_level.lower()
    )
