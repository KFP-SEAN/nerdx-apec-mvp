"""
CAMEO Service - Personalized video generation pipeline
"""
import asyncio
import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import base64
import io
from PIL import Image

import redis.asyncio as aioredis
import httpx

from config import settings
from models.cameo_models import (
    CAMEORequest,
    CAMEOResponse,
    VideoStatus,
    VideoStatusResponse,
    SoraVideoRequest,
    QueueStatus,
    RateLimitInfo,
)
from services.sora_service import sora_service, SoraServiceError
from services.storage_service import storage_service, StorageServiceError

logger = logging.getLogger(__name__)


class CAMEOServiceError(Exception):
    """Base exception for CAMEO service errors"""
    pass


class RateLimitExceeded(CAMEOServiceError):
    """User has exceeded rate limit"""
    pass


class QueueFullError(CAMEOServiceError):
    """Queue is full"""
    pass


class CAMEOService:
    """Service for managing CAMEO personalized video generation pipeline"""

    def __init__(self):
        """Initialize CAMEO service"""
        self.redis_client: Optional[aioredis.Redis] = None
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        logger.info("Initialized CAMEOService")

    async def initialize(self):
        """Initialize async components"""
        try:
            self.redis_client = await aioredis.from_url(
                f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis for queue management")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise CAMEOServiceError(f"Redis connection failed: {str(e)}")

    async def close(self):
        """Close connections and cleanup"""
        if self.redis_client:
            await self.redis_client.close()

        # Cancel all processing tasks
        for task_id, task in self.processing_tasks.items():
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled processing task: {task_id}")

    async def create_cameo_video(
        self,
        request: CAMEORequest
    ) -> CAMEOResponse:
        """
        Create a personalized CAMEO video

        Args:
            request: CAMEO video request

        Returns:
            CAMEOResponse with job details

        Raises:
            RateLimitExceeded: If user has exceeded daily limit
            QueueFullError: If queue is full
        """
        try:
            # Check rate limit
            await self._check_rate_limit(request.user_id)

            # Check queue capacity
            queue_size = await self._get_queue_size()
            if queue_size >= settings.cameo_max_queue_size:
                raise QueueFullError("Video generation queue is full. Please try again later.")

            # Generate unique job ID
            job_id = f"job_{uuid.uuid4().hex[:12]}"

            logger.info(f"[{job_id}] Creating CAMEO video for user {request.user_id}")

            # Process and validate user face image
            face_image_url = await self._process_face_image(
                request.user_face_image,
                job_id,
                request.user_id
            )

            # Create job metadata
            job_data = {
                "job_id": job_id,
                "user_id": request.user_id,
                "status": VideoStatus.QUEUED,
                "progress": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "request": request.model_dump(),
                "face_image_url": face_image_url,
            }

            # Store job in Redis
            await self._store_job(job_id, job_data)

            # Add to processing queue
            await self._enqueue_job(job_id)

            # Increment user's daily count
            await self._increment_daily_count(request.user_id)

            # Start async processing
            task = asyncio.create_task(self._process_video_generation(job_id))
            self.processing_tasks[job_id] = task

            # Estimate completion time
            estimated_time = await sora_service.estimate_generation_time(
                request.duration or 10,
                request.quality.value,
                request.resolution or "1920x1080"
            )

            # Get queue position
            queue_position = await self._get_queue_position(job_id)

            logger.info(
                f"[{job_id}] CAMEO video queued successfully. "
                f"Position: {queue_position}, Estimated time: {estimated_time}s"
            )

            return CAMEOResponse(
                job_id=job_id,
                user_id=request.user_id,
                status=VideoStatus.QUEUED,
                message="Video generation queued successfully",
                created_at=datetime.utcnow(),
                estimated_completion_time=estimated_time + (queue_position * 60),
                queue_position=queue_position
            )

        except RateLimitExceeded:
            raise
        except QueueFullError:
            raise
        except Exception as e:
            logger.error(f"Error creating CAMEO video: {e}")
            raise CAMEOServiceError(f"Failed to create video: {str(e)}")

    async def _process_video_generation(self, job_id: str):
        """
        Background task to process video generation

        Args:
            job_id: Job identifier
        """
        try:
            logger.info(f"[{job_id}] Starting video generation process")

            # Get job data
            job_data = await self._get_job(job_id)
            if not job_data:
                logger.error(f"[{job_id}] Job not found")
                return

            request_data = job_data["request"]
            cameo_request = CAMEORequest(**request_data)

            # Update status to processing
            await self._update_job_status(
                job_id,
                VideoStatus.PROCESSING,
                progress=10,
                message="Processing face image and preparing prompt"
            )

            # Create enhanced prompt with CAMEO template
            enhanced_prompt = sora_service.create_enhanced_prompt(
                base_prompt=cameo_request.prompt,
                template=cameo_request.template.value,
                face_description=f"person with face from image {job_data['face_image_url']}"
            )

            # Update status
            await self._update_job_status(
                job_id,
                VideoStatus.PROCESSING,
                progress=20,
                message="Generating video with Sora 2"
            )

            # Create Sora request
            sora_request = SoraVideoRequest(
                prompt=enhanced_prompt,
                duration=cameo_request.duration or 10,
                resolution=cameo_request.resolution or "1920x1080",
                quality=cameo_request.quality.value,
                guidance_scale=7.5,
            )

            # Generate video with Sora
            sora_response = await sora_service.generate_video(sora_request, job_id)

            # Update status
            await self._update_job_status(
                job_id,
                VideoStatus.RENDERING,
                progress=50,
                message="Rendering video"
            )

            # Poll for completion (in real implementation, use webhooks)
            video_url = await self._wait_for_video_completion(
                sora_response.video_id,
                job_id
            )

            # Download video from Sora
            await self._update_job_status(
                job_id,
                VideoStatus.RENDERING,
                progress=70,
                message="Downloading generated video"
            )

            video_data = await sora_service.download_video(video_url, job_id)

            # Upload to storage
            await self._update_job_status(
                job_id,
                VideoStatus.UPLOADING,
                progress=80,
                message="Uploading to CDN"
            )

            metadata = {
                "user_id": cameo_request.user_id,
                "template": cameo_request.template.value,
                "duration": cameo_request.duration,
                "quality": cameo_request.quality.value,
                "resolution": cameo_request.resolution,
            }

            cdn_url = await storage_service.upload_video(
                video_data,
                job_id,
                cameo_request.user_id,
                metadata
            )

            # Generate thumbnail (simplified - in production, extract from video)
            thumbnail_url = await self._generate_thumbnail(
                video_data,
                job_id,
                cameo_request.user_id
            )

            # Update final status
            await self._update_job_status(
                job_id,
                VideoStatus.COMPLETED,
                progress=100,
                message="Video generation completed successfully",
                video_url=cdn_url,
                thumbnail_url=thumbnail_url,
                file_size=len(video_data),
                completed_at=datetime.utcnow().isoformat()
            )

            logger.info(f"[{job_id}] Video generation completed successfully")

        except SoraServiceError as e:
            logger.error(f"[{job_id}] Sora service error: {e}")
            await self._update_job_status(
                job_id,
                VideoStatus.FAILED,
                progress=0,
                message=f"Video generation failed: {str(e)}",
                error_message=str(e)
            )

        except StorageServiceError as e:
            logger.error(f"[{job_id}] Storage service error: {e}")
            await self._update_job_status(
                job_id,
                VideoStatus.FAILED,
                progress=0,
                message=f"Upload failed: {str(e)}",
                error_message=str(e)
            )

        except Exception as e:
            logger.error(f"[{job_id}] Unexpected error during video generation: {e}")
            await self._update_job_status(
                job_id,
                VideoStatus.FAILED,
                progress=0,
                message=f"Unexpected error: {str(e)}",
                error_message=str(e)
            )

        finally:
            # Remove from processing tasks
            if job_id in self.processing_tasks:
                del self.processing_tasks[job_id]

            # Remove from queue
            await self._dequeue_job(job_id)

    async def get_video_status(self, job_id: str) -> VideoStatusResponse:
        """
        Get the status of a video generation job

        Args:
            job_id: Job identifier

        Returns:
            VideoStatusResponse with current status
        """
        try:
            job_data = await self._get_job(job_id)
            if not job_data:
                raise CAMEOServiceError(f"Job {job_id} not found")

            request_data = job_data.get("request", {})

            return VideoStatusResponse(
                job_id=job_id,
                user_id=job_data["user_id"],
                status=VideoStatus(job_data["status"]),
                progress=job_data.get("progress", 0),
                message=job_data.get("message", ""),
                created_at=datetime.fromisoformat(job_data["created_at"]),
                updated_at=datetime.fromisoformat(job_data["updated_at"]),
                completed_at=datetime.fromisoformat(job_data["completed_at"]) if job_data.get("completed_at") else None,
                video_url=job_data.get("video_url"),
                thumbnail_url=job_data.get("thumbnail_url"),
                duration=request_data.get("duration"),
                file_size=job_data.get("file_size"),
                error_message=job_data.get("error_message"),
                metadata={
                    "template": request_data.get("template"),
                    "quality": request_data.get("quality"),
                    "resolution": request_data.get("resolution"),
                }
            )

        except Exception as e:
            logger.error(f"Error getting video status: {e}")
            raise CAMEOServiceError(f"Failed to get status: {str(e)}")

    async def get_user_videos(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> List[VideoStatusResponse]:
        """
        Get all videos for a user

        Args:
            user_id: User identifier
            page: Page number
            page_size: Items per page

        Returns:
            List of VideoStatusResponse
        """
        try:
            # Get all job IDs for user
            pattern = f"job:*"
            cursor = 0
            user_jobs = []

            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )

                for key in keys:
                    job_data = await self._get_job(key.split(":")[1])
                    if job_data and job_data["user_id"] == user_id:
                        user_jobs.append(job_data)

                if cursor == 0:
                    break

            # Sort by creation date (newest first)
            user_jobs.sort(
                key=lambda x: x["created_at"],
                reverse=True
            )

            # Paginate
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_jobs = user_jobs[start_idx:end_idx]

            # Convert to VideoStatusResponse
            videos = []
            for job_data in paginated_jobs:
                request_data = job_data.get("request", {})
                videos.append(
                    VideoStatusResponse(
                        job_id=job_data["job_id"],
                        user_id=job_data["user_id"],
                        status=VideoStatus(job_data["status"]),
                        progress=job_data.get("progress", 0),
                        message=job_data.get("message", ""),
                        created_at=datetime.fromisoformat(job_data["created_at"]),
                        updated_at=datetime.fromisoformat(job_data["updated_at"]),
                        completed_at=datetime.fromisoformat(job_data["completed_at"]) if job_data.get("completed_at") else None,
                        video_url=job_data.get("video_url"),
                        thumbnail_url=job_data.get("thumbnail_url"),
                        duration=request_data.get("duration"),
                        file_size=job_data.get("file_size"),
                        error_message=job_data.get("error_message"),
                        metadata={
                            "template": request_data.get("template"),
                            "quality": request_data.get("quality"),
                            "resolution": request_data.get("resolution"),
                        }
                    )
                )

            return videos

        except Exception as e:
            logger.error(f"Error getting user videos: {e}")
            raise CAMEOServiceError(f"Failed to get videos: {str(e)}")

    async def cancel_video(self, job_id: str, user_id: str) -> bool:
        """
        Cancel a video generation job

        Args:
            job_id: Job identifier
            user_id: User identifier (for authorization)

        Returns:
            True if cancelled successfully
        """
        try:
            job_data = await self._get_job(job_id)
            if not job_data:
                raise CAMEOServiceError(f"Job {job_id} not found")

            if job_data["user_id"] != user_id:
                raise CAMEOServiceError("Unauthorized to cancel this job")

            current_status = VideoStatus(job_data["status"])
            if current_status in [VideoStatus.COMPLETED, VideoStatus.FAILED, VideoStatus.CANCELLED]:
                return False

            # Cancel processing task
            if job_id in self.processing_tasks:
                self.processing_tasks[job_id].cancel()

            # Update status
            await self._update_job_status(
                job_id,
                VideoStatus.CANCELLED,
                progress=0,
                message="Video generation cancelled by user"
            )

            # Remove from queue
            await self._dequeue_job(job_id)

            logger.info(f"[{job_id}] Video generation cancelled")
            return True

        except Exception as e:
            logger.error(f"Error cancelling video: {e}")
            return False

    async def get_rate_limit_info(self, user_id: str) -> RateLimitInfo:
        """
        Get rate limit information for a user

        Args:
            user_id: User identifier

        Returns:
            RateLimitInfo with quota details
        """
        try:
            daily_count = await self._get_daily_count(user_id)
            max_per_day = settings.max_cameo_per_user_per_day
            remaining = max(0, max_per_day - daily_count)

            # Calculate reset time (midnight UTC)
            now = datetime.utcnow()
            tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

            return RateLimitInfo(
                user_id=user_id,
                videos_generated_today=daily_count,
                max_videos_per_day=max_per_day,
                remaining_quota=remaining,
                reset_at=tomorrow
            )

        except Exception as e:
            logger.error(f"Error getting rate limit info: {e}")
            raise CAMEOServiceError(f"Failed to get rate limit info: {str(e)}")

    async def get_queue_status(self) -> QueueStatus:
        """
        Get current queue status

        Returns:
            QueueStatus with queue metrics
        """
        try:
            total_jobs = await self._get_queue_size()

            # Count jobs by status
            pending_count = 0
            processing_count = 0
            completed_count = 0
            failed_count = 0

            pattern = "job:*"
            cursor = 0

            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )

                for key in keys:
                    job_data = await self._get_job(key.split(":")[1])
                    if job_data:
                        status = VideoStatus(job_data["status"])
                        if status == VideoStatus.PENDING or status == VideoStatus.QUEUED:
                            pending_count += 1
                        elif status == VideoStatus.PROCESSING or status == VideoStatus.RENDERING:
                            processing_count += 1
                        elif status == VideoStatus.COMPLETED:
                            completed_count += 1
                        elif status == VideoStatus.FAILED:
                            failed_count += 1

                if cursor == 0:
                    break

            return QueueStatus(
                total_jobs=total_jobs,
                pending_jobs=pending_count,
                processing_jobs=processing_count,
                completed_jobs=completed_count,
                failed_jobs=failed_count,
                average_processing_time=None  # Calculate from historical data
            )

        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            raise CAMEOServiceError(f"Failed to get queue status: {str(e)}")

    # Private helper methods

    async def _check_rate_limit(self, user_id: str):
        """Check if user has exceeded rate limit"""
        daily_count = await self._get_daily_count(user_id)
        if daily_count >= settings.max_cameo_per_user_per_day:
            raise RateLimitExceeded(
                f"Daily limit of {settings.max_cameo_per_user_per_day} videos exceeded"
            )

    async def _get_daily_count(self, user_id: str) -> int:
        """Get user's daily video count"""
        key = f"rate_limit:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
        count = await self.redis_client.get(key)
        return int(count) if count else 0

    async def _increment_daily_count(self, user_id: str):
        """Increment user's daily video count"""
        key = f"rate_limit:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
        await self.redis_client.incr(key)
        await self.redis_client.expire(key, 86400)  # Expire after 24 hours

    async def _store_job(self, job_id: str, job_data: Dict[str, Any]):
        """Store job data in Redis"""
        key = f"job:{job_id}"
        await self.redis_client.set(key, json.dumps(job_data))
        await self.redis_client.expire(key, 604800)  # Expire after 7 days

    async def _get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data from Redis"""
        key = f"job:{job_id}"
        data = await self.redis_client.get(key)
        return json.loads(data) if data else None

    async def _update_job_status(
        self,
        job_id: str,
        status: VideoStatus,
        progress: int = 0,
        message: str = "",
        **kwargs
    ):
        """Update job status"""
        job_data = await self._get_job(job_id)
        if job_data:
            job_data["status"] = status.value
            job_data["progress"] = progress
            job_data["message"] = message
            job_data["updated_at"] = datetime.utcnow().isoformat()
            job_data.update(kwargs)
            await self._store_job(job_id, job_data)

    async def _enqueue_job(self, job_id: str):
        """Add job to processing queue"""
        await self.redis_client.rpush("video_queue", job_id)

    async def _dequeue_job(self, job_id: str):
        """Remove job from processing queue"""
        await self.redis_client.lrem("video_queue", 0, job_id)

    async def _get_queue_size(self) -> int:
        """Get current queue size"""
        return await self.redis_client.llen("video_queue")

    async def _get_queue_position(self, job_id: str) -> int:
        """Get job position in queue"""
        queue = await self.redis_client.lrange("video_queue", 0, -1)
        try:
            return queue.index(job_id) + 1
        except ValueError:
            return 0

    async def _process_face_image(
        self,
        face_image: str,
        job_id: str,
        user_id: str
    ) -> str:
        """Process and upload user face image"""
        try:
            # If it's a URL, return as-is
            if face_image.startswith("http://") or face_image.startswith("https://"):
                return face_image

            # Decode base64 image
            if face_image.startswith("data:image/"):
                # Extract base64 data
                header, encoded = face_image.split(",", 1)
                image_data = base64.b64decode(encoded)
            else:
                image_data = base64.b64decode(face_image)

            # Upload to storage
            object_key = f"faces/{user_id}/{job_id}.jpg"
            # Simplified - in production, validate and resize image
            face_url = f"{settings.cdn_base_url}/{object_key}"

            return face_url

        except Exception as e:
            logger.error(f"[{job_id}] Error processing face image: {e}")
            raise CAMEOServiceError(f"Invalid face image: {str(e)}")

    async def _wait_for_video_completion(
        self,
        video_id: str,
        job_id: str,
        timeout: int = 600
    ) -> str:
        """Wait for Sora video generation to complete"""
        start_time = asyncio.get_event_loop().time()

        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise CAMEOServiceError("Video generation timeout")

            status_response = await sora_service.check_generation_status(video_id, job_id)

            if status_response.status == "completed" and status_response.video_url:
                return status_response.video_url
            elif status_response.status == "failed":
                raise CAMEOServiceError("Sora video generation failed")

            await asyncio.sleep(5)  # Poll every 5 seconds

    async def _generate_thumbnail(
        self,
        video_data: bytes,
        job_id: str,
        user_id: str
    ) -> str:
        """Generate thumbnail from video (simplified implementation)"""
        try:
            # In production, extract frame from video using ffmpeg
            # For now, return empty or placeholder
            thumbnail_url = f"{settings.cdn_base_url}/thumbnails/{user_id}/{job_id}.jpg"
            return thumbnail_url
        except Exception as e:
            logger.error(f"[{job_id}] Error generating thumbnail: {e}")
            return ""


# Singleton instance
cameo_service = CAMEOService()
