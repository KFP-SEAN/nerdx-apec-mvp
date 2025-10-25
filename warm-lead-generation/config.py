"""
Configuration for NERDX Warm Lead Generation System
NERD12 웜리드 발굴 시스템 설정
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Warm Lead Generation System settings"""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", 8004))
    api_environment: str = "development"

    # Salesforce Integration
    salesforce_instance_url: str = ""
    salesforce_username: str = ""
    salesforce_password: str = ""
    salesforce_security_token: str = ""
    salesforce_consumer_key: str = ""
    salesforce_consumer_secret: str = ""

    # PostgreSQL Database
    database_url: str = "postgresql://user:pass@localhost:5432/nerdx_warm_leads"

    # Redis for caching
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 3

    # Helios Integration
    helios_api_url: str = "http://localhost:8002"
    helios_api_key: str = ""

    # NBRS Configuration
    nbrs_weight_brand_affinity: float = 0.40  # 40% - 브랜드 친화도
    nbrs_weight_market_positioning: float = 0.35  # 35% - 시장 포지셔닝
    nbrs_weight_digital_presence: float = 0.25  # 25% - 디지털 존재감

    # Lead Scoring Thresholds
    nbrs_threshold_tier1: float = 80.0  # Tier 1: 80-100 (Top priority)
    nbrs_threshold_tier2: float = 60.0  # Tier 2: 60-79 (High priority)
    nbrs_threshold_tier3: float = 40.0  # Tier 3: 40-59 (Medium priority)

    # AEO (Answer Engine Optimization) Configuration
    aeo_enabled: bool = True
    aeo_update_interval_hours: int = 24

    # Target Revenue Goal
    target_monthly_revenue_krw: int = 500_000_000  # 5억원 MRR 목표

    model_config = {
        "extra": "allow",
        "env_file": ".env",
        "case_sensitive": False
    }


settings = Settings()
