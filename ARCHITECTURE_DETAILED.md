# NERDX APEC MVP - 시스템 아키텍처 (상세본)

> **최종 업데이트**: 2025-10-27
> **버전**: 1.0
> **대상 독자**: 개발자, 시스템 아키텍트, DevOps 엔지니어

---

## 목차
1. [시스템 개요](#시스템-개요)
2. [서비스별 상세 설계](#서비스별-상세-설계)
3. [데이터베이스 설계](#데이터베이스-설계)
4. [API 명세](#api-명세)
5. [배포 아키텍처](#배포-아키텍처)
6. [보안 설계](#보안-설계)
7. [성능 최적화](#성능-최적화)
8. [모니터링 & 로깅](#모니터링--로깅)

---

## 시스템 개요

### 전체 구성도

```
┌─────────────────────────────────────────────────────────────────┐
│                         사용자 레이어                              │
├─────────────────────────────────────────────────────────────────┤
│  👥 고객          👨‍💼 영업팀        👨‍💻 관리자      🤖 자동화      │
│  (Web/Mobile)    (CRM)           (Dashboard)   (GitHub Actions) │
└──────┬────────────────┬───────────────┬──────────────┬──────────┘
       │                │               │              │
       ▼                ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        프레젠테이션 레이어                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │  Next.js 14    │  │ Shopify        │  │ API Documentation│  │
│  │  (Frontend)    │  │ (Storefront)   │  │ (Swagger/ReDoc)  │  │
│  │  Port: 3000    │  │                │  │  /docs           │  │
│  └────────┬───────┘  └────────┬───────┘  └──────────┬───────┘  │
│           │                   │                      │          │
└───────────┼───────────────────┼──────────────────────┼──────────┘
            │                   │                      │
            ▼                   ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         비즈니스 로직 레이어                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              FastAPI Services (Python 3.11+)               │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │                                                            │ │
│  │  1. Independent Accounting System (Port 8003)             │ │
│  │     ├── routers/                                          │ │
│  │     │   ├── revenue.py          # 매출 API                │ │
│  │     │   ├── expense.py          # 비용 API                │ │
│  │     │   ├── reports.py          # 리포트 API              │ │
│  │     │   └── cells.py            # 셀 관리 API             │ │
│  │     ├── services/                                         │ │
│  │     │   ├── salesforce_service.py                        │ │
│  │     │   ├── odoo_service.py                              │ │
│  │     │   ├── email_service.py    # Resend 통합            │ │
│  │     │   └── report_generator.py                          │ │
│  │     ├── models/                                           │ │
│  │     │   ├── cell_models.py      # Cell, Revenue, Expense │ │
│  │     │   └── report_models.py    # DailyReport            │ │
│  │     └── database.py             # PostgreSQL 연결         │ │
│  │                                                            │ │
│  │  2. Warm Lead Generation (Port 8004)                      │ │
│  │     ├── routers/                                          │ │
│  │     │   ├── lead_scoring.py     # NBRS 스코어링 API       │ │
│  │     │   └── lead_report.py      # Lead 리포트 API         │ │
│  │     ├── services/                                         │ │
│  │     │   ├── nbrs_engine.py      # NBRS 계산 엔진          │ │
│  │     │   ├── lead_report_service.py                       │ │
│  │     │   └── salesforce_client.py                         │ │
│  │     ├── integrations/                                     │ │
│  │     │   └── helios_client.py    # 데이터 enrichment      │ │
│  │     └── models/                                           │ │
│  │         └── nbrs_models.py      # NBRSResult, LeadTier   │ │
│  │                                                            │ │
│  │  3. Agentic AI System (Port 8002)                         │ │
│  │     ├── routers/                                          │ │
│  │     │   ├── autodev.py          # AutoDev API            │ │
│  │     │   ├── agents.py           # CPG Agents API          │ │
│  │     │   └── workflows.py        # Workflow API            │ │
│  │     ├── services/                                         │ │
│  │     │   ├── gemini_service.py   # Gemini 2.0 통합        │ │
│  │     │   ├── claude_service.py   # Claude Sonnet 통합     │ │
│  │     │   ├── sora_service.py     # Sora 2 통합            │ │
│  │     │   └── cameo_service.py    # CAMEO 비디오 생성      │ │
│  │     └── agents/                                           │ │
│  │         ├── prd_agent.py        # PRD 생성 (Gemini)      │ │
│  │         ├── code_agent.py       # 코드 생성 (Claude)     │ │
│  │         ├── qa_agent.py         # 코드 리뷰 (Hybrid)     │ │
│  │         └── orchestrator.py     # 에이전트 조율           │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           Node.js Services (Express.js)                    │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │                                                            │ │
│  │  4. Shopify Custom App (Port 3001)                         │ │
│  │     ├── routes/                                            │ │
│  │     │   ├── webhooks.js         # Shopify Webhook 처리    │ │
│  │     │   ├── ar-access.js        # AR 콘텐츠 액세스        │ │
│  │     │   └── orders.js           # 주문 관리               │ │
│  │     ├── services/                                          │ │
│  │     │   ├── neo4j.js            # Neo4j 연결              │ │
│  │     │   ├── redis.js            # Redis 캐시              │ │
│  │     │   └── jwt.js              # JWT 토큰 생성           │ │
│  │     └── middleware/                                        │ │
│  │         ├── hmac-verify.js      # HMAC 검증               │ │
│  │         └── rate-limit.js       # Rate Limiting           │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────┬────────────────┬────────────────┬──────────┬─────────┘
           │                │                │          │
           ▼                ▼                ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│                          데이터 레이어                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PostgreSQL   │  │   Neo4j      │  │    Redis     │          │
│  │   (15+)      │  │   (5+)       │  │    (7+)      │          │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤          │
│  │ • Cells      │  │ • Customers  │  │ • Sessions   │          │
│  │ • Revenues   │  │ • Products   │  │ • Tokens     │          │
│  │ • Expenses   │  │ • Purchases  │  │ • Rate Limit │          │
│  │ • Reports    │  │ • Relationships│ │ • Idempotency│         │
│  │ • Leads      │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
└──────────┬────────────────┬────────────────┬──────────┬─────────┘
           │                │                │          │
           ▼                ▼                ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       외부 서비스 레이어                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │ Salesforce │  │    Odoo    │  │  Shopify   │  │  Resend  │ │
│  │    CRM     │  │    ERP     │  │  Commerce  │  │   Email  │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │   Claude   │  │   Gemini   │  │   Sora 2   │  │  Helios  │ │
│  │  Sonnet 4.5│  │   2.0 Flash│  │   Video    │  │   Model  │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 서비스별 상세 설계

### 1. Independent Accounting System (독립채산제)

#### 서비스 개요
- **포트**: 8003
- **프레임워크**: FastAPI 0.104+
- **데이터베이스**: PostgreSQL
- **외부 연동**: Salesforce (매출), Odoo (원가), Resend (이메일)

#### 핵심 기능

##### 1.1 Cell 관리
```python
# models/cell_models.py
class Cell(Base):
    cell_id: UUID          # 셀 고유 ID
    cell_type: CellType    # domestic, global, new_market, product, marketing, sales
    cell_name: str         # 셀 이름
    manager: str           # 담당자
    monthly_target: int    # 월간 목표 (KRW)
    created_at: datetime
```

##### 1.2 매출 추적
```python
# models/cell_models.py
class Revenue(Base):
    revenue_id: UUID
    cell_id: UUID          # FK → Cell
    source: str            # salesforce, odoo
    amount_krw: int        # 매출액 (KRW)
    revenue_date: date
    opportunity_id: str    # Salesforce Opportunity ID
    description: str
```

##### 1.3 비용 추적
```python
# models/cell_models.py
class Expense(Base):
    expense_id: UUID
    cell_id: UUID          # FK → Cell
    category: ExpenseCategory  # cogs, marketing, rd, operations
    amount_krw: int        # 비용액 (KRW)
    expense_date: date
    vendor: str
    description: str
```

##### 1.4 일간 리포트
```python
# services/report_generator.py
class ReportGenerator:
    def generate_daily_report(cell_id: UUID, report_date: date) -> HTML:
        # 1. Salesforce에서 매출 조회
        revenues = salesforce_service.get_closed_won_opportunities(cell_id, date)

        # 2. Odoo에서 원가 조회
        expenses = odoo_service.get_expenses(cell_id, date)

        # 3. Gross Profit 계산
        gross_profit = sum(revenues) - sum(expenses)
        gross_margin = (gross_profit / sum(revenues)) * 100

        # 4. MTD (Month-To-Date) 계산
        mtd_revenues = get_mtd_revenues(cell_id, date)
        mtd_expenses = get_mtd_expenses(cell_id, date)

        # 5. 목표 대비 달성률
        target = cell.monthly_target
        achievement_rate = (mtd_revenues / target) * 100

        # 6. HTML 리포트 생성
        return render_html_report(data)
```

#### API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/v1/revenues` | 매출 기록 생성 |
| GET | `/api/v1/revenues/cell/{cell_id}` | 셀별 매출 조회 |
| POST | `/api/v1/expenses` | 비용 기록 생성 |
| GET | `/api/v1/expenses/cell/{cell_id}` | 셀별 비용 조회 |
| GET | `/api/v1/reports/daily/cell-{cell_id}` | 일간 리포트 조회 |
| POST | `/api/v1/reports/daily/cell-{cell_id}/send` | 일간 리포트 이메일 발송 |
| GET | `/api/v1/cells` | 모든 셀 조회 |

#### 자동화 워크플로우

```yaml
# .github/workflows/daily-report.yml
name: Daily Report Automation

on:
  schedule:
    - cron: '0 21 * * *'  # UTC 21:00 = KST 06:00
  workflow_dispatch:

jobs:
  send-daily-reports:
    runs-on: ubuntu-latest
    steps:
      - name: Send Financial Daily Reports
        run: |
          REPORT_DATE=$(date -d "yesterday" +%Y-%m-%d)
          curl -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=$REPORT_DATE"

      - name: Send Lead Daily Report
        run: |
          curl -X POST "https://warm-lead-generation-production.up.railway.app/api/v1/lead-report/send?email=sean@koreafnbpartners.com"
```

---

### 2. Warm Lead Generation (웜리드 발굴)

#### 서비스 개요
- **포트**: 8004
- **프레임워크**: FastAPI 0.104+
- **알고리즘**: NBRS (NERD Brand Resonance Score)
- **외부 연동**: Salesforce (Lead 관리), Helios (데이터 enrichment)

#### NBRS 계산 알고리즘

```python
# services/nbrs_engine.py
class NBRSEngine:
    # Weight Distribution
    WEIGHT_BRAND_AFFINITY = 0.40      # 40%
    WEIGHT_MARKET_POSITIONING = 0.35  # 35%
    WEIGHT_DIGITAL_PRESENCE = 0.25    # 25%

    def calculate_nbrs(lead_data: dict) -> NBRSResult:
        # Pillar 1: Brand Affinity (40%)
        brand_affinity = calculate_brand_affinity(
            past_interaction_score=lead_data.get('past_interaction', 0),
            email_engagement_score=lead_data.get('email_engagement', 0),
            meeting_history_score=lead_data.get('meeting_history', 0),
            relationship_duration_score=lead_data.get('relationship_duration', 0),
            nps_score=lead_data.get('nps', 0)
        )

        # Pillar 2: Market Positioning (35%)
        market_positioning = calculate_market_positioning(
            annual_revenue_krw=lead_data.get('revenue', 0),
            employee_count=lead_data.get('employees', 0),
            marketing_budget_krw=lead_data.get('budget', 0),
            target_industry_match=lead_data.get('industry_match', False),
            pain_point_alignment=lead_data.get('pain_point_score', 0)
        )

        # Pillar 3: Digital Presence (25%)
        digital_presence = calculate_digital_presence(
            website_traffic_monthly=lead_data.get('traffic', 0),
            social_media_followers=lead_data.get('followers', 0),
            content_engagement_score=lead_data.get('engagement', 0),
            modern_website=lead_data.get('modern_site', False),
            marketing_automation=lead_data.get('has_automation', False)
        )

        # Final NBRS Score (0-100)
        nbrs_score = (
            brand_affinity * WEIGHT_BRAND_AFFINITY +
            market_positioning * WEIGHT_MARKET_POSITIONING +
            digital_presence * WEIGHT_DIGITAL_PRESENCE
        )

        # Tier Classification
        tier = classify_tier(nbrs_score)
        # TIER1: 80-100, TIER2: 60-79, TIER3: 40-59, TIER4: 0-39

        return NBRSResult(
            lead_id=lead_data['id'],
            nbrs_score=nbrs_score,
            tier=tier,
            brand_affinity_score=brand_affinity,
            market_positioning_score=market_positioning,
            digital_presence_score=digital_presence
        )
```

#### Salesforce 통합

```python
# integrations/salesforce_client.py
class SalesforceClient:
    def update_lead_with_nbrs(lead_id: str, nbrs_result: NBRSResult):
        # Update Lead fields
        sf.Lead.update(lead_id, {
            'NBRS_Score__c': nbrs_result.nbrs_score,
            'NBRS_Tier__c': nbrs_result.tier,
            'Brand_Affinity_Score__c': nbrs_result.brand_affinity_score,
            'Market_Positioning_Score__c': nbrs_result.market_positioning_score,
            'Digital_Presence_Score__c': nbrs_result.digital_presence_score,
            'Priority_Rank__c': nbrs_result.priority_rank,
            'Next_Action__c': nbrs_result.next_action
        })

        # Publish Platform Event
        sf.NBRS_Update__e.insert({
            'Lead_Id__c': lead_id,
            'NBRS_Score__c': nbrs_result.nbrs_score,
            'Tier__c': nbrs_result.tier
        })
```

#### API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/v1/lead-scoring/calculate` | NBRS 점수 계산 |
| POST | `/api/v1/lead-scoring/enrich-and-score` | Helios enrichment + NBRS 계산 |
| POST | `/api/v1/lead-scoring/batch-score` | 배치 스코어링 |
| GET | `/api/v1/lead-scoring/top-leads` | 상위 10% Lead 조회 |
| GET | `/api/v1/lead-scoring/by-tier/{tier}` | TIER별 Lead 조회 |
| GET | `/api/v1/lead-scoring/stats` | 스코어링 통계 |
| POST | `/api/v1/lead-report/send` | Lead 리포트 이메일 발송 |

---

### 3. Agentic AI System

#### 서비스 개요
- **포트**: 8002
- **프레임워크**: FastAPI 0.104+
- **AI 모델**: Claude Sonnet 4.5, Gemini 2.0 Flash, Sora 2
- **용도**: 자동 코드 생성, PRD 작성, 비디오 콘텐츠 생성

#### 에이전트 구조

```python
# services/agents/base_agent.py
class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.confidence = 0.0

    @abstractmethod
    async def execute_task(self, task: Task) -> AgentResult:
        pass

# services/agents/prd_agent.py (Gemini)
class PRDAgent(BaseAgent):
    async def execute_task(self, task: Task) -> AgentResult:
        prompt = f"""
        Generate a PRD for: {task.title}
        Description: {task.description}
        """
        response = await gemini_service.generate(prompt)
        return AgentResult(content=response, confidence=0.85)

# services/agents/code_agent.py (Claude)
class CodeAgent(BaseAgent):
    async def execute_task(self, task: Task) -> AgentResult:
        prompt = f"""
        Implement this feature: {task.prd}
        Stack: {task.tech_stack}
        """
        response = await claude_service.generate(prompt)
        return AgentResult(content=response, confidence=0.90)

# services/agents/qa_agent.py (Multi-agent)
class QAAgent(BaseAgent):
    async def execute_task(self, task: Task) -> AgentResult:
        # 3가지 AI 모델로 코드 리뷰
        claude_review = await claude_service.review(task.code)
        gemini_review = await gemini_service.review(task.code)
        gpt4_review = await openai_service.review(task.code)

        # 결과 통합
        consensus = merge_reviews([claude_review, gemini_review, gpt4_review])
        return AgentResult(content=consensus, confidence=0.88)
```

#### AutoDev Workflow

```python
# services/agents/autodev_orchestrator.py
class AutoDevOrchestrator:
    async def feature_development_workflow(issue: GitHubIssue) -> PullRequest:
        # Step 1: PRD 생성 (Gemini)
        prd = await prd_agent.execute_task(Task(
            title=issue.title,
            description=issue.body
        ))

        # Step 2: 코드 생성 (Claude)
        code = await code_agent.execute_task(Task(
            prd=prd.content,
            tech_stack="Python, FastAPI"
        ))

        # Step 3: 코드 리뷰 (Multi-agent)
        review = await qa_agent.execute_task(Task(
            code=code.content
        ))

        # Step 4: PR 생성
        pr = await github_service.create_pull_request(
            title=f"feat: {issue.title}",
            body=f"## PRD\n{prd.content}\n\n## Code Review\n{review.content}",
            code=code.content
        )

        return pr
```

---

### 4. Shopify Custom App

#### 서비스 개요
- **포트**: 3001
- **프레임워크**: Express.js (Node.js)
- **데이터베이스**: Neo4j (그래프 DB), Redis (캐시)
- **외부 연동**: Shopify (주문, 제품)

#### 주문 처리 워크플로우

```javascript
// routes/webhooks.js
app.post('/webhooks/orders/create', async (req, res) => {
    // 1. HMAC 검증
    const isValid = verifyShopifyHMAC(req.headers, req.body);
    if (!isValid) {
        return res.status(401).send('Unauthorized');
    }

    // 2. 멱등성 체크 (Redis)
    const orderId = req.body.id;
    const isProcessed = await redis.get(`order:${orderId}`);
    if (isProcessed) {
        return res.status(200).send('Already processed');
    }

    // 3. Neo4j에 관계 저장
    await neo4j.run(`
        MATCH (c:Customer {email: $email})
        MATCH (p:Product {id: $productId})
        CREATE (c)-[:PURCHASED {
            orderId: $orderId,
            purchaseDate: datetime(),
            amount: $amount
        }]->(p)
    `, {
        email: req.body.customer.email,
        productId: req.body.line_items[0].product_id,
        orderId: orderId,
        amount: req.body.total_price
    });

    // 4. JWT 토큰 생성 (90일 유효)
    const token = jwt.sign(
        { customerId: req.body.customer.id, productId: req.body.line_items[0].product_id },
        process.env.JWT_SECRET,
        { expiresIn: '90d' }
    );

    // 5. AR 액세스 이메일 발송
    await sendARAccessEmail(req.body.customer.email, token);

    // 6. Redis에 처리 완료 표시
    await redis.setex(`order:${orderId}`, 86400, 'processed');

    res.status(200).send('OK');
});
```

#### AR 콘텐츠 액세스

```javascript
// routes/ar-access.js
app.get('/ar/:productId', async (req, res) => {
    // 1. JWT 검증
    const token = req.query.token;
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
    } catch (err) {
        return res.status(401).send('Invalid or expired token');
    }

    // 2. Neo4j에서 구매 관계 확인
    const result = await neo4j.run(`
        MATCH (c:Customer {id: $customerId})-[:PURCHASED]->(p:Product {id: $productId})
        RETURN p
    `, {
        customerId: decoded.customerId,
        productId: req.params.productId
    });

    if (result.records.length === 0) {
        return res.status(403).send('Not purchased');
    }

    // 3. AR 콘텐츠 제공
    res.render('ar-viewer', {
        productId: req.params.productId,
        modelUrl: `/models/${req.params.productId}.glb`
    });
});
```

---

## 데이터베이스 설계

### PostgreSQL 스키마

#### Accounting System

```sql
-- Cells Table
CREATE TABLE cells (
    cell_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cell_type VARCHAR(20) NOT NULL CHECK (cell_type IN ('domestic', 'global', 'new_market', 'product', 'marketing', 'sales')),
    cell_name VARCHAR(100) NOT NULL,
    manager VARCHAR(100),
    monthly_target BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Revenues Table
CREATE TABLE revenues (
    revenue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cell_id UUID NOT NULL REFERENCES cells(cell_id),
    source VARCHAR(50) NOT NULL,
    amount_krw BIGINT NOT NULL,
    revenue_date DATE NOT NULL,
    opportunity_id VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cell_date (cell_id, revenue_date)
);

-- Expenses Table
CREATE TABLE expenses (
    expense_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cell_id UUID NOT NULL REFERENCES cells(cell_id),
    category VARCHAR(50) NOT NULL CHECK (category IN ('cogs', 'marketing', 'rd', 'operations', 'overhead')),
    amount_krw BIGINT NOT NULL,
    expense_date DATE NOT NULL,
    vendor VARCHAR(200),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cell_date (cell_id, expense_date)
);

-- Daily Reports Table
CREATE TABLE daily_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cell_id UUID NOT NULL REFERENCES cells(cell_id),
    report_date DATE NOT NULL,
    total_revenue BIGINT NOT NULL,
    total_expense BIGINT NOT NULL,
    gross_profit BIGINT NOT NULL,
    gross_margin DECIMAL(5,2),
    mtd_revenue BIGINT,
    mtd_expense BIGINT,
    mtd_gross_profit BIGINT,
    target_achievement_rate DECIMAL(5,2),
    html_content TEXT,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (cell_id, report_date)
);
```

### Neo4j 그래프 스키마

```cypher
// Node Types
(:Customer {
    id: String,
    email: String,
    firstName: String,
    lastName: String,
    createdAt: DateTime
})

(:Product {
    id: String,
    title: String,
    handle: String,
    hasAR: Boolean,
    arModelUrl: String
})

(:Order {
    id: String,
    orderNumber: String,
    totalPrice: Float,
    createdAt: DateTime
})

// Relationships
(:Customer)-[:PURCHASED {
    orderId: String,
    purchaseDate: DateTime,
    amount: Float,
    arAccessToken: String,
    tokenExpiresAt: DateTime
}]->(:Product)

(:Customer)-[:PLACED]->(:Order)
(:Order)-[:CONTAINS]->(:Product)
```

---

## API 명세

### OpenAPI 문서 위치
- Independent Accounting: http://localhost:8003/docs
- Warm Lead Generation: http://localhost:8004/docs
- Agentic AI System: http://localhost:8002/docs

### 주요 API 예시

#### 1. Daily Report API

**Request:**
```http
POST /api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-26
Content-Type: application/json
```

**Response:**
```json
{
  "message": "Report sent successfully",
  "cell_id": "5ca00d505e2b",
  "report_date": "2025-10-26",
  "recipient": "sean@koreafnbpartners.com",
  "metrics": {
    "total_revenue": 15000000,
    "total_expense": 8000000,
    "gross_profit": 7000000,
    "gross_margin": 46.67
  }
}
```

#### 2. NBRS Calculation API

**Request:**
```http
POST /api/v1/lead-scoring/calculate
Content-Type: application/json

{
  "lead_id": "00Q1234567890AB",
  "company_name": "NERDHOUSE BUKCHON",
  "brand_affinity": {
    "past_interaction_score": 100,
    "email_engagement_score": 80,
    "meeting_history_score": 90
  },
  "market_positioning": {
    "annual_revenue_krw": 50000000000,
    "employee_count": 250,
    "marketing_budget_krw": 500000000
  },
  "digital_presence": {
    "website_traffic_monthly": 50000,
    "social_media_followers": 10000
  }
}
```

**Response:**
```json
{
  "lead_id": "00Q1234567890AB",
  "company_name": "NERDHOUSE BUKCHON",
  "nbrs_score": 95.83,
  "tier": "TIER1",
  "brand_affinity_score": 100.0,
  "market_positioning_score": 88.4,
  "digital_presence_score": 99.5,
  "next_action": "Immediate sales engagement - Top priority",
  "priority_rank": 1,
  "calculated_at": "2025-10-26T18:50:29Z"
}
```

---

## 배포 아키텍처

### Railway 배포 구성

```yaml
# Production Services on Railway
services:
  - name: nerdx-accounting-system
    port: 8003
    plan: Hobby
    region: asia-southeast1
    environment:
      - DATABASE_URL: ${{ Railway.PostgreSQL }}
      - SALESFORCE_INSTANCE_URL: ${{ secrets.SF_URL }}
      - ODOO_URL: ${{ secrets.ODOO_URL }}
      - RESEND_API_KEY: ${{ secrets.RESEND_KEY }}

  - name: warm-lead-generation
    port: 8004
    plan: Hobby
    region: asia-southeast1
    root_directory: warm-lead-generation
    environment:
      - DATABASE_URL: ${{ Railway.PostgreSQL }}
      - SALESFORCE_CONSUMER_KEY: ${{ secrets.SF_KEY }}
      - SALESFORCE_CONSUMER_SECRET: ${{ secrets.SF_SECRET }}
      - RESEND_API_KEY: ${{ secrets.RESEND_KEY }}

  - name: phase2-agentic-system
    port: 8002
    plan: Hobby
    region: asia-southeast1
    environment:
      - ANTHROPIC_API_KEY: ${{ secrets.CLAUDE_KEY }}
      - GEMINI_API_KEY: ${{ secrets.GEMINI_KEY }}
      - OPENAI_API_KEY: ${{ secrets.OPENAI_KEY }}
      - REDIS_URL: ${{ Railway.Redis }}

  - name: shopify-custom-app
    port: 3001
    plan: Hobby
    region: asia-southeast1
    environment:
      - NEO4J_URI: ${{ secrets.NEO4J_URI }}
      - REDIS_URL: ${{ Railway.Redis }}
      - JWT_SECRET: ${{ secrets.JWT_SECRET }}
      - SHOPIFY_WEBHOOK_SECRET: ${{ secrets.SHOPIFY_SECRET }}
```

### Vercel 배포 (Frontend)

```json
// vercel.json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "env": {
    "NEXT_PUBLIC_SHOPIFY_DOMAIN": "@shopify_domain",
    "NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN": "@shopify_token",
    "NEXT_PUBLIC_SHOPIFY_APP_URL": "https://nerdx-shopify-app.railway.app"
  }
}
```

---

## 보안 설계

### 인증 & 권한

#### 1. JWT 토큰 (AR 액세스)
```javascript
// 발급
const token = jwt.sign(
    { customerId, productId },
    process.env.JWT_SECRET,
    { expiresIn: '90d', algorithm: 'HS256' }
);

// 검증
const decoded = jwt.verify(token, process.env.JWT_SECRET);
```

#### 2. OAuth2 (Salesforce)
```python
# Password Grant Flow
token_response = requests.post(
    "https://login.salesforce.com/services/oauth2/token",
    data={
        "grant_type": "password",
        "client_id": os.getenv("SALESFORCE_CONSUMER_KEY"),
        "client_secret": os.getenv("SALESFORCE_CONSUMER_SECRET"),
        "username": os.getenv("SALESFORCE_USERNAME"),
        "password": f"{password}{security_token}"
    }
)
access_token = token_response.json()["access_token"]
```

#### 3. HMAC (Shopify Webhook)
```javascript
function verifyShopifyHMAC(headers, body) {
    const hmac = headers['x-shopify-hmac-sha256'];
    const hash = crypto
        .createHmac('sha256', process.env.SHOPIFY_WEBHOOK_SECRET)
        .update(body, 'utf8')
        .digest('base64');
    return crypto.timingSafeEqual(
        Buffer.from(hmac),
        Buffer.from(hash)
    );
}
```

### Rate Limiting

```python
# FastAPI Rate Limiting (Redis)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/lead-scoring/calculate")
@limiter.limit("100/minute")
async def calculate_nbrs(request: Request, data: CalculateRequest):
    ...
```

---

## 성능 최적화

### 1. 데이터베이스 인덱싱

```sql
-- Accounting System
CREATE INDEX idx_revenues_cell_date ON revenues(cell_id, revenue_date);
CREATE INDEX idx_expenses_cell_date ON expenses(cell_id, expense_date);
CREATE INDEX idx_reports_cell_date ON daily_reports(cell_id, report_date);

-- Composite Index for MTD queries
CREATE INDEX idx_revenues_cell_month ON revenues(cell_id, EXTRACT(YEAR FROM revenue_date), EXTRACT(MONTH FROM revenue_date));
```

### 2. Redis 캐싱

```python
# Lead Scoring Cache
@redis_cache(expire=3600)  # 1 hour
async def get_lead_scores(cell_id: str) -> List[NBRSResult]:
    return await db.query(Lead).filter(Lead.cell_id == cell_id).all()

# Shopify Order Cache
@redis_cache(expire=300)  # 5 minutes
async def get_order(order_id: str) -> Order:
    return await shopify.get_order(order_id)
```

### 3. 비동기 처리

```python
# FastAPI Async Endpoints
@app.post("/api/v1/lead-scoring/batch-score")
async def batch_score_leads(lead_ids: List[str]):
    # 병렬 처리
    tasks = [calculate_nbrs_async(lead_id) for lead_id in lead_ids]
    results = await asyncio.gather(*tasks)
    return results
```

---

## 모니터링 & 로깅

### Structured Logging

```python
import logging
import json

logger = logging.getLogger(__name__)

# Structured Log Format
logger.info(json.dumps({
    "timestamp": datetime.now().isoformat(),
    "service": "accounting-system",
    "level": "INFO",
    "event": "report_generated",
    "cell_id": cell_id,
    "report_date": report_date,
    "metrics": {
        "revenue": total_revenue,
        "expense": total_expense,
        "gross_profit": gross_profit
    }
}))
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "accounting-system",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "database": await check_database(),
            "salesforce": await check_salesforce(),
            "odoo": await check_odoo()
        }
    }
```

---

## 부록

### 환경 변수 목록

#### Independent Accounting System
```env
# API
API_HOST=0.0.0.0
API_PORT=8003
API_ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://...

# Salesforce
SALESFORCE_INSTANCE_URL=https://...
SALESFORCE_USERNAME=...
SALESFORCE_PASSWORD=...
SALESFORCE_SECURITY_TOKEN=...
SALESFORCE_CONSUMER_KEY=...
SALESFORCE_CONSUMER_SECRET=...

# Odoo
ODOO_URL=https://...
ODOO_DB=...
ODOO_USERNAME=...
ODOO_PASSWORD=...

# Email
RESEND_API_KEY=re_...
SMTP_FROM_EMAIL=reports@nerdx.com
```

#### Warm Lead Generation
```env
# API
API_HOST=0.0.0.0
API_PORT=8004

# Salesforce
SALESFORCE_CONSUMER_KEY=...
SALESFORCE_CONSUMER_SECRET=...
SALESFORCE_USERNAME=...
SALESFORCE_PASSWORD=...
SALESFORCE_SECURITY_TOKEN=...
SALESFORCE_INSTANCE_URL=...

# Email
RESEND_API_KEY=re_...
SMTP_FROM_EMAIL=leads@nerdx.com

# NBRS Thresholds
NBRS_THRESHOLD_TIER1=80.0
NBRS_THRESHOLD_TIER2=60.0
NBRS_THRESHOLD_TIER3=40.0
```

---

**작성자**: Claude Code
**날짜**: 2025-10-27
**버전**: 1.0
**문서 유형**: 상세 설계서
