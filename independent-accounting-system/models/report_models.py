"""
일간 리포트 데이터 모델
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, datetime
from decimal import Decimal


class DailyReportData(BaseModel):
    """일간 리포트 데이터"""
    # 기본 정보
    cell_id: str
    cell_name: str
    report_date: date
    currency: str = "KRW"

    # 매출 데이터
    daily_revenue: Decimal = Field(description="당일 매출")
    revenue_count: int = Field(description="매출 건수")
    top_revenue_items: List[Dict] = Field(default_factory=list, description="주요 매출 항목")

    # 비용 데이터
    daily_cogs: Decimal = Field(description="당일 매출원가")
    cogs_count: int = Field(description="비용 건수")
    major_cost_items: List[Dict] = Field(default_factory=list, description="주요 비용 항목")

    # 수익성 지표
    gross_profit: Decimal = Field(description="매출총이익")
    gross_profit_margin: float = Field(description="매출총이익률 (%)")

    # 월간 누적 (MTD - Month To Date)
    mtd_revenue: Decimal = Field(description="월간 누적 매출")
    mtd_cogs: Decimal = Field(description="월간 누적 원가")
    mtd_gross_profit: Decimal = Field(description="월간 누적 총이익")
    mtd_gross_profit_margin: float = Field(description="월간 누적 이익률 (%)")

    # 목표 대비
    monthly_revenue_target: Optional[Decimal] = None
    revenue_achievement_rate: Optional[float] = None
    monthly_profit_target: Optional[Decimal] = None
    profit_achievement_rate: Optional[float] = None

    # 전일/전월 비교
    prev_day_revenue: Optional[Decimal] = None
    revenue_change_rate: Optional[float] = None
    prev_day_profit: Optional[Decimal] = None
    profit_change_rate: Optional[float] = None

    # 메타데이터
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = "system"


class DailyReportEmail(BaseModel):
    """일간 리포트 이메일"""
    # 수신자
    recipient_email: str = Field(..., description="수신자 이메일")
    recipient_name: str = Field(..., description="수신자 이름")

    # 이메일 내용
    subject: str = Field(..., description="이메일 제목")
    html_body: str = Field(..., description="HTML 본문")
    text_body: Optional[str] = None

    # 첨부파일 (옵션)
    attachments: List[Dict] = Field(default_factory=list)

    # 리포트 데이터 (참조용)
    report_data: DailyReportData


class DailyReportTemplate(BaseModel):
    """일간 리포트 템플릿"""
    template_id: str
    template_name: str = "기본 일간 리포트"

    # 템플릿 설정
    include_charts: bool = True
    include_top_items: bool = True
    top_items_count: int = 5

    # 섹션 포함 여부
    include_mtd_summary: bool = True
    include_target_comparison: bool = True
    include_prev_comparison: bool = True

    # 스타일 설정
    theme: str = "default"  # default, modern, minimal
    logo_url: Optional[str] = None


class ReportSchedule(BaseModel):
    """리포트 스케줄 설정"""
    schedule_id: str
    cell_id: str

    # 스케줄 설정
    enabled: bool = True
    send_hour: int = Field(6, description="발송 시간 (24시간 형식)")
    send_minute: int = Field(0, description="발송 분")
    timezone: str = "Asia/Seoul"

    # 수신자 목록
    recipients: List[Dict] = Field(
        default_factory=list,
        description="수신자 리스트: [{'email': 'user@example.com', 'name': 'User Name'}]"
    )

    # 템플릿
    template_id: str = "default"

    # 추가 옵션
    include_pdf_attachment: bool = False
    include_excel_attachment: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReportGenerationLog(BaseModel):
    """리포트 생성 로그"""
    log_id: str
    cell_id: str
    report_date: date

    # 실행 정보
    execution_time: datetime
    generation_status: str  # success, failed, partial
    execution_duration_seconds: float

    # 발송 정보
    emails_sent: int = 0
    emails_failed: int = 0

    # 에러 정보
    error_message: Optional[str] = None
    error_details: Optional[Dict] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
