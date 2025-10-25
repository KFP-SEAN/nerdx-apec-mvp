"""
Configuration for NERDX Independent Accounting System
독립채산제 시스템 설정
"""
from pydantic_settings import BaseSettings
from typing import Literal, Optional


class Settings(BaseSettings):
    """Independent Accounting System settings"""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8003
    api_environment: str = "development"

    # Salesforce Integration
    salesforce_instance_url: str = ""
    salesforce_username: str = ""
    salesforce_password: str = ""
    salesforce_security_token: str = ""
    salesforce_consumer_key: str = ""
    salesforce_consumer_secret: str = ""

    # Odoo ERP Integration
    odoo_url: str = ""
    odoo_db: str = ""
    odoo_username: str = ""
    odoo_password: str = ""

    # PostgreSQL Database
    database_url: str = "postgresql://user:pass@localhost:5432/nerdx_accounting"

    # Redis for caching
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 2

    # Email Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True

    # Daily Report Configuration
    report_generation_hour: int = 6  # 오전 6시에 일간 리포트 생성
    report_timezone: str = "Asia/Seoul"

    # Cell Configuration
    default_currency: str = "KRW"
    gross_profit_margin_target: float = 0.30  # 30% 목표

    # Helios Integration (옵션)
    use_helios: bool = False
    helios_api_url: str = "http://localhost:8002"

    model_config = {
        "extra": "allow",
        "env_file": ".env",
        "case_sensitive": False
    }


settings = Settings()
