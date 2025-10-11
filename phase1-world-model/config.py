"""
Configuration management for Phase 1: World Model
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_environment: str = "development"
    api_debug: bool = True

    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "nerdx"

    # OpenAI Configuration (Maeju agent)
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.7

    # Claude Configuration (Phase 2: Structured tasks)
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7

    # Gemini Configuration (Phase 2: Creative tasks)
    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"
    gemini_max_tokens: int = 8192
    gemini_temperature: float = 0.7

    # Shopify Configuration (Phase 2)
    shopify_shop_url: str = ""
    shopify_access_token: str = ""
    shopify_api_version: str = "2025-01"
    shopify_webhook_secret: str = ""

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8001"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
