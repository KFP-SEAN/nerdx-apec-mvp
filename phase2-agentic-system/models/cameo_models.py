"""
Pydantic models for CAMEO requests and responses
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VideoStatus(str, Enum):
    """Video generation status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    RENDERING = "rendering"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoQuality(str, Enum):
    """Video quality options"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class CameoTemplate(str, Enum):
    """Available CAMEO templates"""
    SAM_ALTMAN_APEC = "sam_altman_apec"
    SAM_ALTMAN_FIRESIDE = "sam_altman_fireside"
    CUSTOM = "custom"


class CAMEORequest(BaseModel):
    """Request model for CAMEO video generation"""
    user_id: str = Field(..., description="Unique user identifier")
    user_face_image: str = Field(..., description="Base64 encoded user face image or URL")
    template: CameoTemplate = Field(
        default=CameoTemplate.SAM_ALTMAN_APEC,
        description="CAMEO template to use"
    )
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Video generation prompt"
    )
    duration: Optional[int] = Field(
        default=10,
        ge=5,
        le=120,
        description="Video duration in seconds"
    )
    quality: VideoQuality = Field(
        default=VideoQuality.HIGH,
        description="Video quality"
    )
    resolution: Optional[str] = Field(
        default="1920x1080",
        description="Video resolution"
    )
    audio_enabled: bool = Field(
        default=True,
        description="Enable audio in video"
    )
    custom_parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional custom parameters"
    )

    @validator("user_face_image")
    def validate_image(cls, v):
        """Validate user face image format"""
        if not v:
            raise ValueError("User face image is required")

        # Check if it's a URL or base64
        if v.startswith("http://") or v.startswith("https://"):
            return v
        elif v.startswith("data:image/"):
            return v
        else:
            # Assume base64 encoded
            if len(v) < 100:
                raise ValueError("Invalid image data")
            return v

    @validator("resolution")
    def validate_resolution(cls, v):
        """Validate resolution format"""
        if v and "x" not in v:
            raise ValueError("Resolution must be in format WIDTHxHEIGHT (e.g., 1920x1080)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "user_face_image": "https://example.com/face.jpg",
                "template": "sam_altman_apec",
                "prompt": "Create a professional video of me discussing AI innovations at APEC",
                "duration": 30,
                "quality": "high",
                "resolution": "1920x1080",
                "audio_enabled": True
            }
        }


class CAMEOResponse(BaseModel):
    """Response model for CAMEO video generation"""
    job_id: str = Field(..., description="Unique job identifier")
    user_id: str = Field(..., description="User identifier")
    status: VideoStatus = Field(..., description="Current status")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    estimated_completion_time: Optional[int] = Field(
        None,
        description="Estimated completion time in seconds"
    )
    queue_position: Optional[int] = Field(
        None,
        description="Position in queue"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_abc123",
                "user_id": "user_123",
                "status": "queued",
                "message": "Video generation queued successfully",
                "created_at": "2025-10-10T12:00:00Z",
                "estimated_completion_time": 120,
                "queue_position": 3
            }
        }


class VideoStatusResponse(BaseModel):
    """Response model for video status check"""
    job_id: str = Field(..., description="Job identifier")
    user_id: str = Field(..., description="User identifier")
    status: VideoStatus = Field(..., description="Current status")
    progress: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Processing progress percentage"
    )
    message: str = Field(..., description="Current status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(
        None,
        description="Completion timestamp"
    )
    video_url: Optional[str] = Field(
        None,
        description="CDN URL of generated video"
    )
    thumbnail_url: Optional[str] = Field(
        None,
        description="CDN URL of video thumbnail"
    )
    duration: Optional[int] = Field(
        None,
        description="Actual video duration in seconds"
    )
    file_size: Optional[int] = Field(
        None,
        description="Video file size in bytes"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if failed"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_abc123",
                "user_id": "user_123",
                "status": "completed",
                "progress": 100,
                "message": "Video generated successfully",
                "created_at": "2025-10-10T12:00:00Z",
                "updated_at": "2025-10-10T12:02:30Z",
                "completed_at": "2025-10-10T12:02:30Z",
                "video_url": "https://cdn.nerdx.com/videos/job_abc123.mp4",
                "thumbnail_url": "https://cdn.nerdx.com/thumbnails/job_abc123.jpg",
                "duration": 30,
                "file_size": 15728640,
                "metadata": {
                    "template": "sam_altman_apec",
                    "quality": "high",
                    "resolution": "1920x1080"
                }
            }
        }


class VideoListResponse(BaseModel):
    """Response model for listing user videos"""
    user_id: str = Field(..., description="User identifier")
    total_videos: int = Field(..., description="Total number of videos")
    videos: List[VideoStatusResponse] = Field(..., description="List of videos")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=10, description="Items per page")
    total_pages: int = Field(..., description="Total pages")


class RateLimitInfo(BaseModel):
    """Rate limiting information"""
    user_id: str = Field(..., description="User identifier")
    videos_generated_today: int = Field(..., description="Videos generated today")
    max_videos_per_day: int = Field(..., description="Maximum videos per day")
    remaining_quota: int = Field(..., description="Remaining quota")
    reset_at: datetime = Field(..., description="Quota reset timestamp")


class SoraVideoRequest(BaseModel):
    """Internal model for Sora API requests"""
    prompt: str = Field(..., description="Video generation prompt")
    duration: int = Field(default=10, ge=5, le=120)
    resolution: str = Field(default="1920x1080")
    quality: str = Field(default="high")
    num_frames: Optional[int] = Field(None, description="Number of frames")
    guidance_scale: Optional[float] = Field(
        default=7.5,
        ge=1.0,
        le=20.0,
        description="Prompt adherence strength"
    )
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class SoraVideoResponse(BaseModel):
    """Internal model for Sora API responses"""
    video_id: str = Field(..., description="Sora video identifier")
    status: str = Field(..., description="Generation status")
    video_url: Optional[str] = Field(None, description="Video URL")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    duration: Optional[int] = Field(None, description="Video duration")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class QueueStatus(BaseModel):
    """Queue status information"""
    total_jobs: int = Field(..., description="Total jobs in queue")
    pending_jobs: int = Field(..., description="Pending jobs")
    processing_jobs: int = Field(..., description="Processing jobs")
    completed_jobs: int = Field(..., description="Completed jobs")
    failed_jobs: int = Field(..., description="Failed jobs")
    average_processing_time: Optional[float] = Field(
        None,
        description="Average processing time in seconds"
    )


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "error": "RateLimitExceeded",
                "message": "You have exceeded the maximum number of videos per day",
                "details": {
                    "max_videos_per_day": 5,
                    "videos_generated_today": 5
                },
                "timestamp": "2025-10-10T12:00:00Z"
            }
        }
