"""
Phase 2: Agentic System - FastAPI Application
CAMEO personalized video generation service with Sora 2 integration
"""
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from config import settings
from models.cameo_models import (
    CAMEORequest,
    CAMEOResponse,
    VideoStatusResponse,
    VideoListResponse,
    RateLimitInfo,
    QueueStatus,
    ErrorResponse,
)
from services.cameo_service import cameo_service, CAMEOServiceError, RateLimitExceeded, QueueFullError
from services.sora_service import sora_service
from services.storage_service import storage_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
video_generation_counter = Counter(
    'video_generation_total',
    'Total number of video generation requests',
    ['status']
)
video_generation_duration = Histogram(
    'video_generation_duration_seconds',
    'Video generation duration',
    buckets=[30, 60, 120, 300, 600]
)
api_request_counter = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Phase 2: Agentic System API")
    logger.info(f"Environment: {settings.api_environment}")
    logger.info(f"Sora Model: {settings.sora_model}")
    logger.info(f"Storage Provider: {settings.storage_provider}")

    # Initialize services
    try:
        await cameo_service.initialize()
        logger.info("CAMEO service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize CAMEO service: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Phase 2 API")
    await cameo_service.close()


app = FastAPI(
    title="NERDX APEC MVP - Phase 2: Agentic System",
    description="CAMEO personalized video generation with Sora 2 integration",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request, exc: RateLimitExceeded):
    """Handle rate limit exceptions"""
    api_request_counter.labels(
        method=request.method,
        endpoint=request.url.path,
        status=429
    ).inc()

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(
            error="RateLimitExceeded",
            message=str(exc),
            details={"max_videos_per_day": settings.max_cameo_per_user_per_day}
        ).model_dump()
    )


@app.exception_handler(QueueFullError)
async def queue_full_exception_handler(request, exc: QueueFullError):
    """Handle queue full exceptions"""
    api_request_counter.labels(
        method=request.method,
        endpoint=request.url.path,
        status=503
    ).inc()

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(
            error="QueueFull",
            message=str(exc),
            details={"max_queue_size": settings.cameo_max_queue_size}
        ).model_dump()
    )


@app.exception_handler(CAMEOServiceError)
async def cameo_service_exception_handler(request, exc: CAMEOServiceError):
    """Handle CAMEO service exceptions"""
    api_request_counter.labels(
        method=request.method,
        endpoint=request.url.path,
        status=500
    ).inc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="ServiceError",
            message=str(exc)
        ).model_dump()
    )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "phase2-agentic-system"}


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check including dependencies"""
    health_status = {
        "service": "phase2-agentic-system",
        "status": "healthy",
        "checks": {}
    }

    # Check Sora API
    try:
        sora_healthy = await sora_service.health_check()
        health_status["checks"]["sora_api"] = "healthy" if sora_healthy else "unhealthy"
    except Exception as e:
        health_status["checks"]["sora_api"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check Storage
    try:
        storage_healthy = await storage_service.health_check()
        health_status["checks"]["storage"] = "healthy" if storage_healthy else "unhealthy"
    except Exception as e:
        health_status["checks"]["storage"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        await cameo_service.redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")


# CAMEO endpoints
@app.post(
    "/api/v1/cameo/generate",
    response_model=CAMEOResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def generate_cameo_video(request: CAMEORequest):
    """
    Generate a personalized CAMEO video

    This endpoint queues a video generation request that will be processed asynchronously.
    Use the returned job_id to check the status of the generation.

    - **user_id**: Unique identifier for the user
    - **user_face_image**: Base64 encoded image or URL of user's face
    - **template**: CAMEO template to use (e.g., "sam_altman_apec")
    - **prompt**: Description of the video to generate
    - **duration**: Video duration in seconds (5-120)
    - **quality**: Video quality (low, medium, high, maximum)
    """
    try:
        logger.info(f"Received CAMEO generation request from user {request.user_id}")

        response = await cameo_service.create_cameo_video(request)

        video_generation_counter.labels(status="queued").inc()

        api_request_counter.labels(
            method="POST",
            endpoint="/api/v1/cameo/generate",
            status=202
        ).inc()

        return response

    except (RateLimitExceeded, QueueFullError):
        raise
    except Exception as e:
        logger.error(f"Error generating CAMEO video: {e}")
        video_generation_counter.labels(status="error").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get(
    "/api/v1/cameo/status/{job_id}",
    response_model=VideoStatusResponse
)
async def get_video_status(job_id: str):
    """
    Get the status of a video generation job

    Returns detailed information about the current state of the video generation,
    including progress percentage, CDN URLs (when completed), and any error messages.
    """
    try:
        logger.debug(f"Status check for job {job_id}")

        status_response = await cameo_service.get_video_status(job_id)

        api_request_counter.labels(
            method="GET",
            endpoint="/api/v1/cameo/status",
            status=200
        ).inc()

        return status_response

    except CAMEOServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get(
    "/api/v1/cameo/videos/{user_id}",
    response_model=VideoListResponse
)
async def list_user_videos(
    user_id: str,
    page: int = 1,
    page_size: int = 10
):
    """
    List all videos for a specific user

    Returns a paginated list of all video generation jobs for the specified user,
    ordered by creation date (newest first).
    """
    try:
        logger.debug(f"Listing videos for user {user_id} (page={page}, size={page_size})")

        videos = await cameo_service.get_user_videos(user_id, page, page_size)

        # Calculate total pages
        total_videos = len(videos)
        total_pages = (total_videos + page_size - 1) // page_size

        api_request_counter.labels(
            method="GET",
            endpoint="/api/v1/cameo/videos",
            status=200
        ).inc()

        return VideoListResponse(
            user_id=user_id,
            total_videos=total_videos,
            videos=videos,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error listing user videos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post(
    "/api/v1/cameo/cancel/{job_id}",
    status_code=status.HTTP_200_OK
)
async def cancel_video_generation(job_id: str, user_id: str):
    """
    Cancel a video generation job

    Cancels an ongoing or queued video generation. Completed videos cannot be cancelled.
    """
    try:
        logger.info(f"Cancellation requested for job {job_id} by user {user_id}")

        success = await cameo_service.cancel_video(job_id, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel this job (already completed, failed, or cancelled)"
            )

        video_generation_counter.labels(status="cancelled").inc()

        api_request_counter.labels(
            method="POST",
            endpoint="/api/v1/cameo/cancel",
            status=200
        ).inc()

        return {"message": "Video generation cancelled successfully", "job_id": job_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling video: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get(
    "/api/v1/cameo/rate-limit/{user_id}",
    response_model=RateLimitInfo
)
async def get_rate_limit_info(user_id: str):
    """
    Get rate limit information for a user

    Returns current quota usage and remaining capacity for video generation.
    """
    try:
        rate_limit_info = await cameo_service.get_rate_limit_info(user_id)

        api_request_counter.labels(
            method="GET",
            endpoint="/api/v1/cameo/rate-limit",
            status=200
        ).inc()

        return rate_limit_info

    except Exception as e:
        logger.error(f"Error getting rate limit info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get(
    "/api/v1/cameo/queue/status",
    response_model=QueueStatus
)
async def get_queue_status():
    """
    Get current queue status

    Returns information about the video generation queue including number of
    pending, processing, completed, and failed jobs.
    """
    try:
        queue_status = await cameo_service.get_queue_status()

        api_request_counter.labels(
            method="GET",
            endpoint="/api/v1/cameo/queue/status",
            status=200
        ).inc()

        return queue_status

    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Admin endpoints
@app.get("/api/v1/admin/storage/stats")
async def get_storage_stats():
    """Get storage statistics (admin only)"""
    try:
        stats = await storage_service.get_storage_stats()

        api_request_counter.labels(
            method="GET",
            endpoint="/api/v1/admin/storage/stats",
            status=200
        ).inc()

        return stats

    except Exception as e:
        logger.error(f"Error getting storage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/admin/config")
async def get_config():
    """Get current configuration (admin only)"""
    return {
        "api_environment": settings.api_environment,
        "sora_model": settings.sora_model,
        "storage_provider": settings.storage_provider,
        "max_video_duration": settings.max_video_duration,
        "video_quality": settings.video_quality,
        "video_resolution": settings.video_resolution,
        "cameo_max_queue_size": settings.cameo_max_queue_size,
        "max_cameo_per_user_per_day": settings.max_cameo_per_user_per_day,
    }


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "NERDX APEC MVP - Phase 2: Agentic System",
        "version": "1.0.0",
        "description": "CAMEO personalized video generation with Sora 2",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "generate_video": "POST /api/v1/cameo/generate",
            "video_status": "GET /api/v1/cameo/status/{job_id}",
            "list_videos": "GET /api/v1/cameo/videos/{user_id}",
            "queue_status": "GET /api/v1/cameo/queue/status",
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_environment == "development",
        log_level="info"
    )
