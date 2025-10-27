"""
Project Sonar Configuration
AI 브랜드 공명 분석 시스템 설정
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Project Sonar 환경 변수 설정"""

    # API Configuration
    api_environment: str = os.getenv("API_ENVIRONMENT", "development")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8005"))

    # WIPO API
    wipo_api_url: str = os.getenv("WIPO_API_URL", "https://www.wipo.int/branddb/en/")
    wipo_api_key: Optional[str] = os.getenv("WIPO_API_KEY")

    # KIS (한국신용평가정보) API
    kis_api_url: str = os.getenv("KIS_API_URL", "https://api.kis.co.kr")
    kis_api_key: Optional[str] = os.getenv("KIS_API_KEY")
    kis_api_secret: Optional[str] = os.getenv("KIS_API_SECRET")

    # 국내 뉴스 API (예: Naver News API)
    news_api_url: str = os.getenv("NEWS_API_URL", "https://openapi.naver.com/v1/search/news.json")
    news_api_client_id: Optional[str] = os.getenv("NEWS_API_CLIENT_ID")
    news_api_client_secret: Optional[str] = os.getenv("NEWS_API_CLIENT_SECRET")

    # Google Cloud (NotebookLM, Google Docs)
    google_credentials_path: Optional[str] = os.getenv("GOOGLE_CREDENTIALS_PATH")
    google_project_id: Optional[str] = os.getenv("GOOGLE_PROJECT_ID")

    # AI Models
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")

    # Database (PostgreSQL for structured data)
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/project_sonar"
    )

    # Redis (Feature Store, Cache)
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "2"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")

    # Neo4j (Brand Relationship Graph)
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: Optional[str] = os.getenv("NEO4J_PASSWORD")

    # MLOps
    mlflow_tracking_uri: Optional[str] = os.getenv("MLFLOW_TRACKING_URI")
    model_registry_path: str = os.getenv("MODEL_REGISTRY_PATH", "./models")

    # NBRS 2.0 Model Configuration
    nbrs_model_version: str = "2.0.0"
    nbrs_update_frequency: str = "daily"  # daily, weekly
    nbrs_min_data_points: int = 100

    # Multi-Armed Bandits (MAB) Configuration
    mab_epsilon: float = 0.1  # Exploration rate
    mab_window_size: int = 1000  # Recent data window

    # KPI Thresholds
    target_automation_rate: float = 0.95  # 95%
    target_learning_speed: float = 0.05  # 5% weekly AUC improvement
    target_resonance_ltv_cac: float = 5.0  # 5:1 ratio

    # T2D3 Growth Targets (ARR in 억 원)
    t2d3_year1_target: int = 60   # 60억 (현재 MRR 5억 * 12개월)
    t2d3_year2_target: int = 180  # Triple
    t2d3_year3_target: int = 540  # Triple
    t2d3_year4_target: int = 1080 # Double
    t2d3_year5_target: int = 2160 # Double
    t2d3_year6_target: int = 4320 # Double

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
