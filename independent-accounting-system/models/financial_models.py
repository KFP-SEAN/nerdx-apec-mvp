"""
재무 데이터 모델
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal


class RevenueRecord(BaseModel):
    """매출 기록"""
    record_id: str = Field(..., description="기록 ID")
    cell_id: str = Field(..., description="셀 ID")

    # Salesforce 연동
    salesforce_opportunity_id: Optional[str] = None
    salesforce_account_id: Optional[str] = None

    # 매출 정보
    revenue_date: date = Field(..., description="매출 일자")
    revenue_amount: Decimal = Field(..., description="매출 금액")
    currency: str = Field(default="KRW", description="통화")

    # 제품/서비스 정보
    product_name: Optional[str] = None
    product_category: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None

    # 메타데이터
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CostRecord(BaseModel):
    """비용 기록 (COGS - Cost of Goods Sold)"""
    record_id: str = Field(..., description="기록 ID")
    cell_id: str = Field(..., description="셀 ID")

    # Odoo 연동
    odoo_invoice_id: Optional[int] = None
    odoo_invoice_line_id: Optional[int] = None

    # 비용 정보
    cost_date: date = Field(..., description="비용 발생 일자")
    cost_amount: Decimal = Field(..., description="비용 금액")
    currency: str = Field(default="KRW", description="통화")

    # 비용 분류
    cost_category: str = Field(..., description="비용 카테고리")  # COGS, Operating, etc.
    cost_type: Optional[str] = None  # Materials, Labor, Overhead, etc.

    # 제품/서비스 연결
    related_product: Optional[str] = None
    related_revenue_id: Optional[str] = None

    # 메타데이터
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DailyFinancialSummary(BaseModel):
    """일간 재무 요약"""
    cell_id: str
    summary_date: date

    # 매출
    total_revenue: Decimal = Field(default=Decimal("0"), description="총 매출")
    revenue_count: int = Field(default=0, description="매출 건수")

    # 비용
    total_cogs: Decimal = Field(default=Decimal("0"), description="총 매출원가")
    cogs_count: int = Field(default=0, description="비용 건수")

    # 수익성
    gross_profit: Decimal = Field(default=Decimal("0"), description="매출총이익")
    gross_profit_margin: float = Field(default=0.0, description="매출총이익률")

    # 통화
    currency: str = "KRW"

    # 메타데이터
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class MonthlyFinancialSummary(BaseModel):
    """월간 재무 요약"""
    cell_id: str
    year: int
    month: int

    # 매출
    total_revenue: Decimal = Field(default=Decimal("0"))
    revenue_count: int = Field(default=0)
    avg_daily_revenue: Decimal = Field(default=Decimal("0"))

    # 비용
    total_cogs: Decimal = Field(default=Decimal("0"))
    cogs_count: int = Field(default=0)
    avg_daily_cogs: Decimal = Field(default=Decimal("0"))

    # 수익성
    gross_profit: Decimal = Field(default=Decimal("0"))
    gross_profit_margin: float = Field(default=0.0)

    # 목표 대비
    revenue_target: Optional[Decimal] = None
    revenue_achievement_rate: Optional[float] = None

    gross_profit_target: Optional[Decimal] = None
    gross_profit_achievement_rate: Optional[float] = None

    # 통화
    currency: str = "KRW"

    # 메타데이터
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class FinancialMetrics(BaseModel):
    """재무 지표"""
    cell_id: str
    period_start: date
    period_end: date

    # 핵심 지표
    total_revenue: Decimal
    total_cogs: Decimal
    gross_profit: Decimal
    gross_profit_margin: float

    # 추세 분석
    revenue_growth_rate: Optional[float] = None  # 전 기간 대비
    profit_growth_rate: Optional[float] = None

    # 추가 분석
    top_products: Optional[List[Dict[str, Any]]] = None
    revenue_by_category: Optional[Dict[str, Decimal]] = None

    generated_at: datetime = Field(default_factory=datetime.utcnow)
