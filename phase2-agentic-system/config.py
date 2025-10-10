"""
Configuration for Phase 2: Agentic System
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Phase 2 settings"""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8002
    api_environment: str = "development"

    # OpenAI Sora
    openai_api_key: str
    sora_model: str = "sora-2"
    sora_api_endpoint: str = "https://api.openai.com/v1/video"

    # Storage
    storage_provider: Literal["aws", "gcp", "local"] = "aws"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = "nerdx-videos"
    aws_region: str = "us-west-2"

    # CDN
    cdn_base_url: str = "https://cdn.nerdx.com"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 1

    # Phase 1 Integration
    phase1_api_url: str = "http://localhost:8001"

    # Video Processing
    max_video_duration: int = 120
    video_quality: str = "high"
    video_resolution: str = "1920x1080"

    # CAMEO Settings
    cameo_max_queue_size: int = 100
    cameo_processing_timeout: int = 600

    # Rate Limiting
    max_cameo_per_user_per_day: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
