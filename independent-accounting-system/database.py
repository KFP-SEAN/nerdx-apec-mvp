"""
Database configuration and models using SQLAlchemy
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, Date, DateTime, Boolean, Numeric, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

# Create engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()


# Database Models
class CellDB(Base):
    """Cell database model"""
    __tablename__ = "cells"

    cell_id = Column(String(100), primary_key=True, index=True)
    cell_name = Column(String(200), nullable=False)
    cell_type = Column(String(50), nullable=False)

    # Manager info
    manager_name = Column(String(200), nullable=False)
    manager_email = Column(String(200), nullable=False, index=True)
    manager_phone = Column(String(50))

    # Salesforce mapping
    salesforce_account_ids = Column(JSON, default=list)
    salesforce_opportunity_filters = Column(JSON)

    # Odoo mapping
    odoo_analytic_account_id = Column(Integer)
    odoo_analytic_account_code = Column(String(50))

    # Targets
    monthly_revenue_target = Column(Numeric(15, 2))
    monthly_gross_profit_target = Column(Numeric(15, 2))
    gross_profit_margin_target = Column(Float)

    # Status
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RevenueRecordDB(Base):
    """Revenue record database model"""
    __tablename__ = "revenue_records"

    revenue_id = Column(String(100), primary_key=True, index=True)
    cell_id = Column(String(100), nullable=False, index=True)

    # Salesforce
    salesforce_opportunity_id = Column(String(100), index=True)
    salesforce_account_id = Column(String(100), index=True)

    # Revenue
    revenue_date = Column(Date, nullable=False, index=True)
    revenue_amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default="KRW")

    # Product/Service
    product_name = Column(String(200))
    product_category = Column(String(100))
    quantity = Column(Integer)
    unit_price = Column(Numeric(15, 2))

    # Metadata
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CostRecordDB(Base):
    """Cost record database model"""
    __tablename__ = "cost_records"

    cost_id = Column(String(100), primary_key=True, index=True)
    cell_id = Column(String(100), nullable=False, index=True)

    # Odoo
    odoo_invoice_id = Column(Integer, index=True)
    odoo_invoice_line_id = Column(Integer)

    # Cost
    cost_date = Column(Date, nullable=False, index=True)
    cost_amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default="KRW")

    # Category
    cost_category = Column(String(100), nullable=False)
    cost_type = Column(String(100))

    # Relations
    related_product = Column(String(200))
    related_revenue_id = Column(String(100))

    # Metadata
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DailyFinancialSummaryDB(Base):
    """Daily financial summary database model"""
    __tablename__ = "daily_financial_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cell_id = Column(String(100), nullable=False, index=True)
    summary_date = Column(Date, nullable=False, index=True)

    # Revenue
    total_revenue = Column(Numeric(15, 2), default=0)
    revenue_count = Column(Integer, default=0)

    # Costs
    total_cogs = Column(Numeric(15, 2), default=0)
    cogs_count = Column(Integer, default=0)

    # Profitability
    gross_profit = Column(Numeric(15, 2), default=0)
    gross_profit_margin = Column(Float, default=0.0)

    # Currency
    currency = Column(String(10), default="KRW")

    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)


class ReportScheduleDB(Base):
    """Report schedule database model"""
    __tablename__ = "report_schedules"

    schedule_id = Column(String(100), primary_key=True, index=True)
    cell_id = Column(String(100), nullable=False, index=True)

    # Schedule
    enabled = Column(Boolean, default=True)
    send_hour = Column(Integer, default=6)
    send_minute = Column(Integer, default=0)
    timezone = Column(String(50), default="Asia/Seoul")

    # Recipients
    recipients = Column(JSON, default=list)

    # Template
    template_id = Column(String(100), default="default")

    # Options
    include_pdf_attachment = Column(Boolean, default=False)
    include_excel_attachment = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReportGenerationLogDB(Base):
    """Report generation log database model"""
    __tablename__ = "report_generation_logs"

    log_id = Column(String(100), primary_key=True, index=True)
    cell_id = Column(String(100), nullable=False, index=True)
    report_date = Column(Date, nullable=False, index=True)

    # Execution
    execution_time = Column(DateTime, nullable=False)
    generation_status = Column(String(20), nullable=False)
    execution_duration_seconds = Column(Float)

    # Email delivery
    emails_sent = Column(Integer, default=0)
    emails_failed = Column(Integer, default=0)

    # Errors
    error_message = Column(Text)
    error_details = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


# Create all tables
def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


# Dependency for FastAPI
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
