# NERDX 독립채산제 시스템 (Independent Accounting System)

> Salesforce CRM + Odoo ERP 통합 기반 셀별 P&L 추적 및 일간 리포트 자동화 시스템

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/nerdx)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)

---

## 🚀 Overview

NERDX 독립채산제 시스템은 영업 셀(Cell)별로 매출과 비용을 독립적으로 추적하고, 매출총이익(Gross Profit)을 자동으로 계산하여 일간 리포트로 이메일 발송하는 완전 자동화 시스템입니다.

### ✨ Key Features

- 🏢 **셀 기반 독립채산제** - 국내셀, 글로벌셀, 신규시장셀 등 영업 조직별 P&L 관리
- 💰 **실시간 재무 추적** - Salesforce 매출 + Odoo 원가 자동 동기화
- 📊 **자동 리포트 생성** - 매일 아침 6시 자동 생성 및 이메일 발송
- 🎯 **목표 대비 분석** - 월간 목표 대비 달성률 자동 계산
- 📈 **MTD 누적 분석** - 월간 누적(Month-To-Date) 실적 추적

---

## 📋 Quick Start

```bash
# 1. Navigate to project directory
cd nerdx-apec-mvp/independent-accounting-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Initialize database
python -c "from database import init_db; init_db()"

# 5. Run application
python main.py

# 6. Open API docs
open http://localhost:8003/docs
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   NERDX Independent Accounting v1.0.0   │
├─────────────────────────────────────────┤
│                                          │
│  📊 Cell Management                     │
│  - 국내셀 (Domestic Cell)                │
│  - 글로벌셀 (Global Cell)                │
│  - 신규시장셀 (New Market Cell)          │
│                                          │
│  💰 Financial Tracking                  │
│  - Salesforce → Revenue (매출)          │
│  - Odoo → COGS (매출원가)               │
│  - Auto Calculation → Gross Profit      │
│                                          │
│  📧 Daily Report Automation             │
│  - Morning 6AM Auto Generation          │
│  - Email Delivery to Cell Managers      │
│  - MTD Summary & Target Analysis        │
│                                          │
└─────────────────────────────────────────┘
         ↕                    ↕
   Salesforce CRM        Odoo ERP
```

---

## 📦 Project Structure

```
independent-accounting-system/
├── main.py                    # FastAPI application
├── config.py                  # Configuration
├── database.py                # SQLAlchemy models & DB setup
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
│
├── models/                    # Pydantic data models
│   ├── cell_models.py        # Cell 관리 모델
│   ├── financial_models.py   # 재무 데이터 모델
│   └── report_models.py      # 리포트 모델
│
├── services/                  # Business logic services
│   ├── integrations/         # External system integrations
│   │   ├── salesforce_service.py  # Salesforce CRM
│   │   └── odoo_service.py        # Odoo ERP
│   ├── cell_manager/         # Cell management
│   │   └── cell_service.py
│   ├── financial_tracker/    # Financial tracking
│   │   └── financial_service.py
│   ├── report_generator/     # Report generation
│   │   └── daily_report_service.py
│   └── email_sender/         # Email delivery
│       └── email_service.py
│
├── routers/                   # FastAPI routers
│   ├── cells.py              # Cell management endpoints
│   ├── financial.py          # Financial endpoints
│   └── reports.py            # Report endpoints
│
└── tests/                     # Integration tests
    └── test_integration.py
```

---

## 🔌 API Endpoints (13)

### Cell Management (5)
```bash
POST   /api/v1/cells/                    # Create cell
GET    /api/v1/cells/{cell_id}           # Get cell
GET    /api/v1/cells/                    # List cells
PUT    /api/v1/cells/{cell_id}           # Update cell
DELETE /api/v1/cells/{cell_id}           # Delete cell
```

### Financial Tracking (4)
```bash
POST /api/v1/financial/sync/{cell_id}/revenue        # Sync revenue from Salesforce
POST /api/v1/financial/sync/{cell_id}/costs          # Sync costs from Odoo
GET  /api/v1/financial/summary/daily/{cell_id}       # Get daily summary
GET  /api/v1/financial/summary/monthly/{cell_id}     # Get monthly summary (MTD)
```

### Reports (3)
```bash
GET  /api/v1/reports/daily/{cell_id}           # Get daily report data
POST /api/v1/reports/daily/{cell_id}/send      # Generate and send report
POST /api/v1/reports/test-email                # Send test email
```

### System (1)
```bash
GET  /health                                     # Health check
```

---

## 💡 Usage Examples

### 1. Create New Cell

```python
import httpx

response = httpx.post(
    "http://localhost:8003/api/v1/cells/",
    json={
        "cell_name": "국내셀 - 서울",
        "cell_type": "domestic",
        "manager_name": "김철수",
        "manager_email": "kim@nerdx.com",
        "salesforce_account_ids": ["001XXXXXXXX"],
        "monthly_revenue_target": 100000000,
        "monthly_gross_profit_target": 30000000
    }
)

cell = response.json()
print(f"Created cell: {cell['cell_id']}")
```

### 2. Sync Daily Revenue and Costs

```python
from datetime import date

cell_id = "cell-abc123"
target_date = date.today()

# Sync revenue from Salesforce
httpx.post(
    f"http://localhost:8003/api/v1/financial/sync/{cell_id}/revenue",
    params={"target_date": target_date.isoformat()}
)

# Sync costs from Odoo
httpx.post(
    f"http://localhost:8003/api/v1/financial/sync/{cell_id}/costs",
    params={"target_date": target_date.isoformat()}
)
```

### 3. Generate and Send Daily Report

```python
# Automatically generate report and send via email
response = httpx.post(
    f"http://localhost:8003/api/v1/reports/daily/{cell_id}/send",
    params={"report_date": target_date.isoformat()}
)

print(response.json())
# {"message": "Daily report sent successfully", ...}
```

### 4. Get Monthly Summary (MTD)

```python
response = httpx.get(
    f"http://localhost:8003/api/v1/financial/summary/monthly/{cell_id}",
    params={"year": 2025, "month": 10}
)

summary = response.json()
print(f"MTD Revenue: {summary['total_revenue']:,.0f} KRW")
print(f"MTD Gross Profit: {summary['gross_profit']:,.0f} KRW")
print(f"Target Achievement: {summary['revenue_achievement_rate']:.1f}%")
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Test specific module
pytest tests/test_integration.py::test_cell_creation -v

# Test with coverage
pytest tests/ --cov=services --cov-report=html
```

---

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options:

```bash
# Required
SALESFORCE_USERNAME=your_username@domain.com
SALESFORCE_PASSWORD=your_password
ODOO_URL=https://your-odoo.com
DATABASE_URL=postgresql://user:pass@localhost:5432/nerdx_accounting

# Email (Resend API - Railway Compatible)
RESEND_API_KEY=re_your_resend_api_key
SMTP_FROM_EMAIL=noreply@yourdomain.com

# Optional
REPORT_GENERATION_HOUR=6  # Daily report at 6 AM
REPORT_TIMEZONE=Asia/Seoul
DEFAULT_CURRENCY=KRW
```

**📧 Email Configuration:**
This system uses **Resend API** for email delivery, which is Railway-compatible (SMTP ports are blocked on Railway).
See [RAILWAY_EMAIL_SETUP.md](./RAILWAY_EMAIL_SETUP.md) for detailed setup instructions.

---

## 📊 Key Concepts

### 1. Cell (셀)

영업 조직의 최소 단위로, 독립적인 P&L을 관리합니다.

- **국내셀 (Domestic)**: 국내 시장 영업 조직
- **글로벌셀 (Global)**: 해외 시장 영업 조직
- **신규시장셀 (New Market)**: 신규 진출 시장 영업 조직

### 2. Analytic Account (분석 계정)

Odoo ERP의 표준 기능으로, 셀별로 비용을 분리 추적합니다.

각 셀 생성 시 자동으로 Odoo Analytic Account가 생성됩니다:
- 국내셀: `CELL-DOM-XXXXXX`
- 글로벌셀: `CELL-GLO-XXXXXX`
- 신규시장셀: `CELL-NEW-XXXXXX`

### 3. Gross Profit (매출총이익)

```
매출총이익 = 매출 (Revenue) - 매출원가 (COGS)
매출총이익률 = 매출총이익 / 매출 × 100
```

**MVP Scope**: 매출원가(COGS)만 추적하며, 운영비용(OPEX)는 Phase 2에서 추가됩니다.

### 4. Daily Report (일간 리포트)

매일 자동 생성되어 셀 매니저에게 이메일로 발송됩니다:

- 당일 실적 (매출, 원가, 총이익)
- 월간 누적 (MTD)
- 목표 대비 달성률
- 전일 대비 증감
- 주요 매출/비용 항목

---

## 🚀 Deployment

### Docker (권장)

```bash
# Build image
docker build -t nerdx-accounting:1.0.0 .

# Run container
docker run -p 8003:8003 \
  --env-file .env \
  nerdx-accounting:1.0.0
```

### Production Checklist

- [ ] .env 파일 보안 설정 완료
- [ ] PostgreSQL 데이터베이스 생성
- [ ] Salesforce API 자격증명 확인
- [ ] Odoo API 접근 권한 확인
- [ ] **Resend API 설정 및 도메인 인증** (see [RAILWAY_EMAIL_SETUP.md](./RAILWAY_EMAIL_SETUP.md))
- [ ] 이메일 전송 테스트 (`python test_email.py your_email@example.com`)
- [ ] 일간 리포트 스케줄러 설정
- [ ] 모니터링 대시보드 구성

---

## 📚 Documentation

- **API Docs**: http://localhost:8003/docs (Swagger UI)
- **ReDoc**: http://localhost:8003/redoc
- **PRD 문서**: `[KFP] NERDX 독립채산제 시스템 마스터플랜.md`

---

## 🤝 Integration Guide

### Salesforce CRM

매출 데이터는 Salesforce Opportunity에서 가져옵니다:

- **Stage**: `Closed Won` 상태만 매출로 인식
- **CloseDate**: 매출 발생 일자
- **Amount**: 매출 금액
- **Account**: 셀에 할당된 Account ID로 필터링

### Odoo ERP

비용 데이터는 Odoo Vendor Bills에서 가져옵니다:

- **Analytic Account**: 셀별 분석 계정으로 필터링
- **Invoice Date**: 비용 발생 일자
- **Subtotal**: 비용 금액 (세전)
- **State**: `posted` 상태만 인식

---

## 🛠️ Technology Stack

- **Backend**: FastAPI 0.104+
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0+
- **CRM**: Salesforce (simple-salesforce)
- **ERP**: Odoo (XML-RPC)
- **Email**: Resend API (Railway-compatible HTTP-based email)
- **Cache**: Redis 5.0+ (optional)
- **Testing**: pytest, httpx

---

## 📄 License

Proprietary - NERDX APEC MVP Project

---

## 👥 Team

- **Implementation**: Claude Code (Opus 4.1) + Helios Orchestration
- **Requirements**: NERD Development Team
- **PRD**: KFP Product Team

---

## 📞 Support

- **API Documentation**: http://localhost:8003/docs
- **Health Check**: http://localhost:8003/health
- **Issues**: Create an issue in the repository

---

**Version**: 1.0.0
**Status**: ✅ Ready for Testing
**Last Updated**: 2025-10-25

---

Made with ❤️ by NERD Development Team
