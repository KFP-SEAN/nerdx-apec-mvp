"""
Cell (셀) 관리 데이터 모델
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CellType(str, Enum):
    """셀 유형"""
    DOMESTIC = "domestic"  # 국내 셀
    GLOBAL = "global"      # 글로벌 셀
    NEW_MARKET = "new_market"  # 신규시장 셀
    PRODUCT = "product"  # 제품 셀
    MARKETING = "marketing"  # 마케팅 셀
    SALES = "sales"  # 영업 셀


class CellStatus(str, Enum):
    """셀 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Cell(BaseModel):
    """셀 정보"""
    cell_id: str = Field(..., description="셀 고유 ID")
    cell_name: str = Field(..., description="셀 이름")
    cell_type: CellType = Field(..., description="셀 유형")

    # 셀 매니저 정보
    manager_name: str = Field(..., description="셀 매니저 이름")
    manager_email: str = Field(..., description="셀 매니저 이메일")
    manager_phone: Optional[str] = None

    # Salesforce 매핑
    salesforce_account_ids: List[str] = Field(default_factory=list, description="Salesforce 계정 ID 리스트")
    salesforce_opportunity_filters: Optional[dict] = None

    # Odoo 매핑 (Analytic Account)
    odoo_analytic_account_id: Optional[int] = None
    odoo_analytic_account_code: Optional[str] = None

    # 목표 설정
    monthly_revenue_target: Optional[float] = None
    monthly_gross_profit_target: Optional[float] = None
    gross_profit_margin_target: Optional[float] = None

    # 상태
    status: CellStatus = CellStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CellCreateRequest(BaseModel):
    """셀 생성 요청"""
    cell_name: str
    cell_type: CellType
    manager_name: str
    manager_email: str
    manager_phone: Optional[str] = None
    salesforce_account_ids: List[str] = []
    monthly_revenue_target: Optional[float] = None
    monthly_gross_profit_target: Optional[float] = None


class CellUpdateRequest(BaseModel):
    """셀 업데이트 요청"""
    cell_name: Optional[str] = None
    manager_name: Optional[str] = None
    manager_email: Optional[str] = None
    manager_phone: Optional[str] = None
    salesforce_account_ids: Optional[List[str]] = None
    monthly_revenue_target: Optional[float] = None
    monthly_gross_profit_target: Optional[float] = None
    status: Optional[CellStatus] = None


class CellListResponse(BaseModel):
    """셀 목록 응답"""
    total: int
    cells: List[Cell]
    page: int = 1
    page_size: int = 20
