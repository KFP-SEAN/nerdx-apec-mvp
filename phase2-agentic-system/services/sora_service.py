"""
Sora 2 API Service for video generation
"""
import asyncio
import logging
from typing import Optional, Dict, Any
import httpx
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from config import settings
from models.cameo_models import SoraVideoRequest, SoraVideoResponse

logger = logging.getLogger(__name__)


class SoraServiceError(Exception):
    """Base exception for Sora service errors"""
    pass


class SoraRateLimitError(SoraServiceError):
    """Rate limit exceeded"""
    pass


class SoraGenerationError(SoraServiceError):
    """Video generation failed"""
    pass


class SoraService:
    """Service for interacting with OpenAI Sora 2 API"""

    def __init__(self):
        """Initialize Sora service"""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.sora_model
        self.endpoint = settings.sora_api_endpoint
        self.timeout = httpx.Timeout(300.0, connect=60.0)
        logger.info(f"Initialized SoraService with model: {self.model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
    )
    async def generate_video(
        self,
        request: SoraVideoRequest,
        job_id: str
    ) -> SoraVideoResponse:
        """
        Generate video using Sora 2 API

        Args:
            request: Sora video request parameters
            job_id: Unique job identifier for tracking

        Returns:
            SoraVideoResponse with video details

        Raises:
            SoraRateLimitError: If rate limit is exceeded
            SoraGenerationError: If generation fails
        """
        try:
            logger.info(f"[{job_id}] Starting video generation with Sora 2")
            logger.debug(f"[{job_id}] Prompt: {request.prompt[:100]}...")

            # Prepare request payload
            payload = {
                "model": self.model,
                "prompt": request.prompt,
                "duration": request.duration,
                "resolution": request.resolution,
                "quality": request.quality,
            }

            if request.guidance_scale:
                payload["guidance_scale"] = request.guidance_scale
            if request.seed:
                payload["seed"] = request.seed
            if request.num_frames:
                payload["num_frames"] = request.num_frames

            logger.debug(f"[{job_id}] Sora API payload: {payload}")

            # Note: This is a conceptual implementation as Sora 2 API may differ
            # Adjust based on actual OpenAI Sora API when available
            response = await self._call_sora_api(payload, job_id)

            logger.info(f"[{job_id}] Video generation initiated successfully")

            return SoraVideoResponse(
                video_id=response.get("id", job_id),
                status=response.get("status", "processing"),
                video_url=response.get("video_url"),
                thumbnail_url=response.get("thumbnail_url"),
                duration=response.get("duration"),
                metadata={
                    "model": self.model,
                    "prompt": request.prompt,
                    "resolution": request.resolution,
                    "quality": request.quality,
                }
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error(f"[{job_id}] Rate limit exceeded")
                raise SoraRateLimitError("Sora API rate limit exceeded")
            elif e.response.status_code >= 500:
                logger.error(f"[{job_id}] Sora API server error: {e}")
                raise SoraGenerationError(f"Sora API server error: {e.response.status_code}")
            else:
                logger.error(f"[{job_id}] Sora API request failed: {e}")
                raise SoraGenerationError(f"Video generation failed: {str(e)}")

        except Exception as e:
            logger.error(f"[{job_id}] Unexpected error during video generation: {e}")
            raise SoraGenerationError(f"Unexpected error: {str(e)}")

    async def _call_sora_api(self, payload: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        """
        Internal method to call Sora API

        Note: This is a conceptual implementation. Update based on actual Sora API spec.
        """
        try:
            # Using httpx for direct API calls
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                }

                response = await client.post(
                    f"{self.endpoint}/generations",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.error(f"[{job_id}] Sora API request timed out")
            raise SoraGenerationError("API request timed out")

    async def check_generation_status(
        self,
        video_id: str,
        job_id: str
    ) -> SoraVideoResponse:
        """
        Check the status of a video generation

        Args:
            video_id: Sora video identifier
            job_id: Internal job identifier

        Returns:
            Updated SoraVideoResponse
        """
        try:
            logger.debug(f"[{job_id}] Checking generation status for video: {video_id}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                }

                response = await client.get(
                    f"{self.endpoint}/generations/{video_id}",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

            return SoraVideoResponse(
                video_id=data.get("id", video_id),
                status=data.get("status", "processing"),
                video_url=data.get("video_url"),
                thumbnail_url=data.get("thumbnail_url"),
                duration=data.get("duration"),
                metadata=data.get("metadata", {})
            )

        except Exception as e:
            logger.error(f"[{job_id}] Error checking generation status: {e}")
            raise SoraGenerationError(f"Failed to check status: {str(e)}")

    async def download_video(
        self,
        video_url: str,
        job_id: str
    ) -> bytes:
        """
        Download generated video from Sora

        Args:
            video_url: URL of the generated video
            job_id: Job identifier for logging

        Returns:
            Video content as bytes
        """
        try:
            logger.info(f"[{job_id}] Downloading video from: {video_url}")

            async with httpx.AsyncClient(timeout=httpx.Timeout(600.0)) as client:
                response = await client.get(video_url)
                response.raise_for_status()

                video_data = response.content
                logger.info(f"[{job_id}] Downloaded {len(video_data)} bytes")

                return video_data

        except Exception as e:
            logger.error(f"[{job_id}] Error downloading video: {e}")
            raise SoraGenerationError(f"Failed to download video: {str(e)}")

    async def cancel_generation(
        self,
        video_id: str,
        job_id: str
    ) -> bool:
        """
        Cancel an ongoing video generation

        Args:
            video_id: Sora video identifier
            job_id: Internal job identifier

        Returns:
            True if cancelled successfully
        """
        try:
            logger.info(f"[{job_id}] Cancelling video generation: {video_id}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                }

                response = await client.post(
                    f"{self.endpoint}/generations/{video_id}/cancel",
                    headers=headers
                )
                response.raise_for_status()

            logger.info(f"[{job_id}] Video generation cancelled successfully")
            return True

        except Exception as e:
            logger.error(f"[{job_id}] Error cancelling generation: {e}")
            return False

    def create_enhanced_prompt(
        self,
        base_prompt: str,
        template: str,
        face_description: Optional[str] = None
    ) -> str:
        """
        Create an enhanced prompt for CAMEO-style videos

        Args:
            base_prompt: User's base prompt
            template: Template name (e.g., "sam_altman_apec")
            face_description: Optional face description

        Returns:
            Enhanced prompt with template-specific details
        """
        template_prompts = {
            "sam_altman_apec": (
                "Professional video in the style of an APEC summit presentation. "
                "High-quality corporate setting with modern staging and professional lighting. "
                "Speaker in business casual attire presenting to an executive audience. "
            ),
            "sam_altman_fireside": (
                "Intimate fireside chat setting with warm, conversational lighting. "
                "Casual yet professional atmosphere, sitting in a comfortable modern chair. "
                "Natural, engaging conversation style with subtle gestures. "
            ),
        }

        template_prefix = template_prompts.get(template, "")

        enhanced = f"{template_prefix}{base_prompt}"

        if face_description:
            enhanced = f"{enhanced} Featuring {face_description}."

        # Add quality enhancers
        enhanced += (
            " Cinematic quality, professional color grading, "
            "sharp focus, natural lighting, 4K resolution."
        )

        logger.debug(f"Enhanced prompt: {enhanced}")
        return enhanced

    async def estimate_generation_time(
        self,
        duration: int,
        quality: str,
        resolution: str
    ) -> int:
        """
        Estimate video generation time in seconds

        Args:
            duration: Video duration in seconds
            quality: Video quality
            resolution: Video resolution

        Returns:
            Estimated time in seconds
        """
        # Base time estimation (rough approximation)
        base_time = duration * 2  # 2 seconds per video second

        # Quality multipliers
        quality_multipliers = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5,
            "maximum": 2.0,
        }

        # Resolution multipliers
        resolution_multipliers = {
            "1280x720": 0.8,
            "1920x1080": 1.0,
            "2560x1440": 1.5,
            "3840x2160": 2.5,
        }

        quality_mult = quality_multipliers.get(quality, 1.0)
        resolution_mult = resolution_multipliers.get(resolution, 1.0)

        estimated_time = int(base_time * quality_mult * resolution_mult)

        logger.debug(
            f"Estimated generation time: {estimated_time}s "
            f"(duration={duration}, quality={quality}, resolution={resolution})"
        )

        return estimated_time

    async def health_check(self) -> bool:
        """
        Check if Sora API is accessible

        Returns:
            True if API is healthy
        """
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                headers = {
                    "Authorization": f"Bearer {settings.openai_api_key}",
                }
                response = await client.get(
                    f"{self.endpoint}/health",
                    headers=headers
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Sora API health check failed: {e}")
            return False


# Singleton instance
sora_service = SoraService()
