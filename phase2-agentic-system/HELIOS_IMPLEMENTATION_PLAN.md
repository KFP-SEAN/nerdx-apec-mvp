# Helios 오케스트레이션 시스템: 구현 계획서

## 📋 문서 개요

**프로젝트**: Helios - Claude Max 기반 오케스트레이션 시스템
**기반 PRD**: `[KFP] Claude Max 기반 오케스트레이션 시스템 마스터플랜.pdf`
**기존 시스템**: NERDX Phase 3B AutoDev System
**작성일**: 2025년 10월 25일
**버전**: 1.0.0

---

## 🎯 프로젝트 목표

기존 AutoDev 시스템을 **Claude Max 요금제에 최적화**된 Helios 오케스트레이션 시스템으로 확장:

### 핵심 차별점

| 구분 | 기존 AutoDev | Helios 시스템 |
|-----|-------------|--------------|
| **API 사용량 관리** | 단순 사용 | 5시간 창 예산 관리 |
| **모델 선택** | 고정 (Claude/Gemini) | 동적 경제적 라우팅 |
| **컨텍스트 관리** | 기본 | 최소 실행 가능 컨텍스트 |
| **캐싱** | 없음 | L1/L2/L3 다층 캐싱 |
| **스케줄링** | 단순 큐 | Rate-Aware 하이브리드 스케줄링 |
| **병렬화** | 제한적 | 10+ 프로젝트 동시 실행 |

---

## 🏗️ 아키텍처 확장 설계

### 1. 기존 AutoDev 시스템 구조

```
┌─────────────────────────────────────────┐
│     AutoDev Orchestrator                 │
│  - Workflow Management                   │
│  - Task Coordination                     │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐       ┌───▼────┐
│  PRD   │       │  QA    │
│ Agent  │◄──────┤ Agent  │
│(Gemini)│       │(Hybrid)│
└───┬────┘       └───▲────┘
    │                │
    │           ┌────┴────┐
    │           │  Code   │
    └──────────►│  Agent  │
                │(Claude) │
                └─────────┘
```

### 2. Helios 확장 아키텍처

```
┌────────────────────────────────────────────────────────────┐
│          HELIOS ORCHESTRATOR (Enhanced)                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  🎯 RESOURCE GOVERNOR                                │ │
│  │  - 5시간 창 예산 추적                                 │ │
│  │  - 사용량 모니터링 (Opus/Sonnet)                     │ │
│  │  - 동적 스로틀링                                      │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  💰 ECONOMIC ROUTER                                  │ │
│  │  - 작업별 비용-편익 분석                              │ │
│  │  - Opus/Sonnet 동적 선택                             │ │
│  │  - 작업 메타데이터 기반 라우팅                         │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  📊 HYBRID SCHEDULER                                 │ │
│  │  - 작업 종속성 DAG 관리                               │ │
│  │  - 우선순위 기반 스케줄링                             │ │
│  │  - 10+ 프로젝트 병렬 실행                             │ │
│  │  - 자원 가용성 고려                                   │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼───────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  Architect    │  │    Coder    │  │   Reviewer  │
│   Agent       │  │    Agent    │  │    Agent    │
│  (Opus 우선)  │  │(Sonnet 기본)│  │  (Opus 우선)│
└───────────────┘  └─────────────┘  └─────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
        ┌─────────────────▼─────────────────┐
        │   SHARED CONTEXT & MEMORY BUS     │
        │  ┌────────────────────────────┐   │
        │  │  L1: Claude Prompt Cache   │   │
        │  │  L2: Exact Match Cache     │   │
        │  │  L3: Semantic Cache (RAG)  │   │
        │  └────────────────────────────┘   │
        │  ┌────────────────────────────┐   │
        │  │  Vector DB (Pinecone)      │   │
        │  │  Redis (State Management)  │   │
        │  └────────────────────────────┘   │
        └───────────────────────────────────┘
```

---

## 🔧 구현 로드맵

### Phase 1: 기반 인프라 구축 (Week 1-2)

#### 1.1 Resource Governor 구현

**파일**: `services/orchestrator/resource_governor.py`

```python
class ResourceGovernor:
    """
    Claude Max 사용량 예산 관리자

    - 5시간 창 내 토큰 사용량 추적
    - Opus/Sonnet 사용 비율 모니터링
    - 동적 스로틀링 (예산 80% 도달 시)
    """

    def __init__(self):
        self.window_duration = 5 * 60 * 60  # 5 hours
        self.max_capacity = 900  # 세션당 약 900 메시지
        self.opus_limit_pct = 0.50  # Opus 50% 제한

    async def track_usage(self, model: str, tokens: int) -> UsageMetrics:
        """사용량 추적"""

    async def check_budget(self) -> BudgetStatus:
        """현재 예산 상태 확인"""

    async def should_throttle(self) -> bool:
        """스로틀링 필요 여부"""
```

**구현 요구사항**:
- Redis에 5시간 창 사용량 저장
- Opus/Sonnet 별도 추적
- 실시간 예산 상태 API

#### 1.2 Economic Router 구현

**파일**: `services/orchestrator/economic_router.py`

```python
class EconomicRouter:
    """
    작업별 모델 선택 경제적 라우터

    Rules:
    - Architectural reasoning → Opus
    - Boilerplate code → Sonnet
    - Code review → Opus
    - Unit test generation → Sonnet
    """

    TASK_MODEL_MAP = {
        'architectural_reasoning': 'opus',
        'high_level_planning': 'opus',
        'code_review': 'opus',
        'boilerplate_generation': 'sonnet',
        'unit_test': 'sonnet',
        'refactoring': 'sonnet',
    }

    async def route_task(
        self,
        task: Task,
        budget_status: BudgetStatus
    ) -> Model:
        """작업을 적절한 모델로 라우팅"""

        # Cost-benefit analysis
        task_type = task.metadata.get('task_type')
        recommended_model = self.TASK_MODEL_MAP.get(task_type, 'sonnet')

        # Budget constraint
        if budget_status.opus_budget_pct > 80:
            # Opus 예산 부족 시 Sonnet으로 다운그레이드
            return 'sonnet'

        return recommended_model
```

#### 1.3 Hybrid Scheduler 구현

**파일**: `services/orchestrator/hybrid_scheduler.py`

```python
class HybridScheduler:
    """
    하이브리드 작업 스케줄러

    고려 요소:
    1. 작업 종속성 (DAG)
    2. 자원 가용성 (예산)
    3. 작업 우선순위
    4. 병렬성 (독립 작업)
    """

    async def schedule_tasks(
        self,
        task_graph: DAG,
        priorities: Dict[str, int],
        budget: BudgetStatus
    ) -> ExecutionPlan:
        """작업 스케줄링 알고리즘"""

        # 1. 위상 정렬 (Topological Sort)
        sorted_tasks = self.topological_sort(task_graph)

        # 2. 병렬 실행 가능 작업 식별
        parallel_groups = self.identify_parallel_tasks(task_graph)

        # 3. 우선순위 및 예산 고려 스케줄링
        execution_plan = self.optimize_schedule(
            parallel_groups,
            priorities,
            budget
        )

        return execution_plan
```

---

### Phase 2: 캐싱 시스템 구축 (Week 3)

#### 2.1 다층 캐싱 아키텍처

**파일**: `services/cache/multi_layer_cache.py`

```python
class MultiLayerCache:
    """
    L1: Claude Native Prompt Cache
    L2: Exact Match Cache (Redis)
    L3: Semantic Cache (Vector DB)
    """

    def __init__(self):
        self.l1_cache = ClaudePromptCache()
        self.l2_cache = RedisExactCache()
        self.l3_cache = SemanticCache(vector_db=pinecone_client)

    async def get(self, key: str, context: str) -> Optional[CacheHit]:
        """캐시 조회 (L1 → L2 → L3)"""

        # L1: Claude Prompt Cache (90% 비용 절감)
        if result := await self.l1_cache.get(key):
            return CacheHit(level='L1', data=result)

        # L2: Exact Match (Redis)
        if result := await self.l2_cache.get(key):
            return CacheHit(level='L2', data=result)

        # L3: Semantic Match (Vector DB)
        if result := await self.l3_cache.semantic_search(context):
            return CacheHit(level='L3', data=result)

        return None
```

#### 2.2 프롬프트 압축 모듈

**파일**: `services/optimization/prompt_compressor.py`

```python
from llmlingua import PromptCompressor

class HeliosPromptCompressor:
    """
    LLMLingua 기반 프롬프트 압축

    - 최대 20배 압축
    - 비용 및 지연 시간 감소
    """

    def __init__(self):
        self.compressor = PromptCompressor()

    async def compress(
        self,
        prompt: str,
        target_length: Optional[int] = None
    ) -> CompressedPrompt:
        """프롬프트 압축"""

        compressed = self.compressor.compress_prompt(
            prompt,
            target_token=target_length,
            condition_compare=True,
            reorder_context="sort"
        )

        return CompressedPrompt(
            original=prompt,
            compressed=compressed['compressed_prompt'],
            compression_ratio=len(prompt) / len(compressed['compressed_prompt'])
        )
```

---

### Phase 3: 전문 에이전트 확장 (Week 4-5)

#### 3.1 ArchitectAgent (Opus 전용)

**파일**: `services/agents/architect_agent.py`

```python
class ArchitectAgent(BaseAgent):
    """
    고수준 아키텍처 설계 에이전트

    Model: Claude Opus (복잡한 추론 필요)
    Tasks:
    - 프로젝트 계획 분해
    - DAG 생성
    - 의존성 분석
    """

    def __init__(self):
        super().__init__(
            agent_id="architect-001",
            primary_model="opus",
            task_types=["architectural_reasoning", "planning"]
        )

    async def decompose_project(
        self,
        prd: PRD
    ) -> TaskGraph:
        """프로젝트를 작업 DAG로 분해"""

        prompt = self._build_decomposition_prompt(prd)

        response = await self.claude_client.messages.create(
            model="claude-opus-4",
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert software architect..."
        )

        task_graph = self._parse_task_graph(response.content)
        return task_graph
```

#### 3.2 Code AnalysisAgent (Sonnet)

**파일**: `services/agents/code_analysis_agent.py`

```python
class CodeAnalysisAgent(BaseAgent):
    """
    코드베이스 분석 에이전트

    Model: Claude Sonnet (대규모 컨텍스트 검색)
    Tasks:
    - 종속성 그래프 구축
    - 코드 검색
    - 영향 분석
    """

    def __init__(self):
        super().__init__(
            agent_id="codeanalysis-001",
            primary_model="sonnet",
            tools=[StaticAnalysisTool(), DependencyGraphTool()]
        )

    async def build_dependency_graph(
        self,
        codebase_path: str
    ) -> DependencyGraph:
        """소프트웨어 종속성 그래프 생성"""

        # Static analysis
        graph = await self.tools['static_analysis'].analyze(codebase_path)
        return graph
```

#### 3.3 CoderAgent (Sonnet 기본, Opus 선택적)

**파일**: `services/agents/coder_agent.py` (기존 확장)

```python
class CoderAgent(BaseAgent):
    """
    코드 구현 에이전트 (Enhanced)

    Model: Sonnet (기본), Opus (복잡한 알고리즘)
    Features:
    - 컨텍스트 격리
    - 최소 실행 가능 컨텍스트 로딩
    """

    async def implement_task(
        self,
        task: Task,
        context: MinimalContext  # RAG로 최소화된 컨텍스트
    ) -> Implementation:
        """작업 구현"""

        # Economic routing
        model = await self.economic_router.route_task(task)

        # Context from RAG (minimal)
        relevant_context = await self.context_bus.retrieve(
            task_id=task.id,
            max_tokens=5000  # 최소 컨텍스트
        )

        # Implementation
        code = await self.generate_code(model, task, relevant_context)

        return Implementation(code=code, model_used=model)
```

---

### Phase 4: 모니터링 및 관찰 가능성 (Week 6)

#### 4.1 KPI 대시보드 구현

**파일**: `routers/helios_metrics.py`

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
token_usage = Counter(
    'helios_token_usage_total',
    'Total token usage',
    ['model', 'window']
)

project_cost = Histogram(
    'helios_project_cost_dollars',
    'Project cost in dollars'
)

task_latency = Histogram(
    'helios_task_latency_seconds',
    'Task completion latency',
    ['agent_type']
)

cache_hit_rate = Gauge(
    'helios_cache_hit_rate',
    'Cache hit rate',
    ['cache_level']
)

opus_sonnet_ratio = Gauge(
    'helios_opus_sonnet_ratio',
    'Opus to Sonnet usage ratio'
)

@router.get("/api/v1/helios/metrics")
async def get_helios_metrics():
    """Helios 시스템 메트릭"""

    return {
        "token_usage": {
            "total_5h_window": await get_5h_usage(),
            "opus_pct": await get_opus_percentage(),
            "sonnet_pct": await get_sonnet_percentage()
        },
        "cost": {
            "current_project": await get_current_project_cost(),
            "projected_monthly": await get_monthly_projection()
        },
        "performance": {
            "avg_task_latency": await get_avg_task_latency(),
            "cache_hit_rate": await get_cache_hit_rates()
        },
        "agent_metrics": {
            "success_rate": await get_agent_success_rates()
        }
    }
```

#### 4.2 모니터링 대시보드 (Grafana)

**파일**: `infrastructure/grafana/helios_dashboard.json`

**패널**:
1. **총 토큰 소비량 (5시간 창)** - Gauge
2. **프로젝트당 비용** - Graph over time
3. **평균 작업 지연 시간** - Bar chart by agent
4. **캐시 적중률 (L1/L2/L3)** - Pie chart
5. **Opus 대 Sonnet 사용 비율** - Pie chart
6. **에이전트 성공/실패율** - Bar chart

---

## 📊 구현 우선순위

### High Priority (Week 1-2)
1. ✅ Resource Governor
2. ✅ Economic Router
3. ✅ Hybrid Scheduler
4. ✅ 기본 메트릭 수집

### Medium Priority (Week 3-4)
5. ✅ Multi-layer Caching (L1/L2/L3)
6. ✅ ArchitectAgent 구현
7. ✅ Code AnalysisAgent 구현
8. ✅ 프롬프트 압축 모듈

### Low Priority (Week 5-6)
9. ⏳ 고급 모니터링 대시보드
10. ⏳ E2E 성능 최적화
11. ⏳ 병렬 프로젝트 실행 테스트

---

## 🎯 성공 지표

### 목표 KPI

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **토큰 사용량 최적화** | 5시간 창 90% 미만 사용 | Resource Governor |
| **Opus 사용 비율** | 50% 미만 | Economic Router |
| **캐시 적중률** | L2+L3 > 40% | Cache Service |
| **평균 작업 지연** | < 30초 | Prometheus |
| **프로젝트 비용** | 기존 대비 30% 절감 | Cost Tracking |

### 성능 벤치마크

| 작업 | 현재 AutoDev | Helios 목표 |
|------|--------------|-------------|
| PRD 생성 | 60초 | 40초 (캐싱) |
| 코드 구현 | 600초 | 450초 (컨텍스트 최적화) |
| 코드 리뷰 | 120초 | 90초 (캐싱) |
| **전체 워크플로우** | 1200초 | **900초** |

---

## 🔐 보안 및 품질

### 보안 요구사항
- API 키 회전 (매 30일)
- Secrets Manager 사용 (AWS Secrets Manager)
- Redis 암호화 전송 (TLS)
- 코드 실행 샌드박스 (Docker isolation)

### 품질 게이트 (기존 유지)
- SonarQube 코드 커버리지 ≥80%
- Snyk 보안 스캔 (Critical/High: 0)
- 코드 중복 <3%
- 보안 등급: A

---

## 📁 디렉토리 구조

```
phase2-agentic-system/
├── services/
│   ├── orchestrator/
│   │   ├── resource_governor.py       # NEW
│   │   ├── economic_router.py         # NEW
│   │   ├── hybrid_scheduler.py        # NEW
│   │   └── helios_orchestrator.py     # NEW
│   ├── cache/
│   │   ├── multi_layer_cache.py       # NEW
│   │   ├── claude_prompt_cache.py     # NEW
│   │   ├── redis_exact_cache.py       # NEW
│   │   └── semantic_cache.py          # NEW
│   ├── agents/
│   │   ├── architect_agent.py         # NEW
│   │   ├── code_analysis_agent.py     # NEW
│   │   ├── coder_agent.py             # ENHANCED
│   │   └── reviewer_agent.py          # ENHANCED
│   └── optimization/
│       └── prompt_compressor.py       # NEW
├── routers/
│   └── helios_metrics.py              # NEW
├── models/
│   ├── task_graph.py                  # NEW
│   ├── budget.py                      # NEW
│   └── cache_models.py                # NEW
├── infrastructure/
│   └── grafana/
│       └── helios_dashboard.json      # NEW
├── tests/
│   ├── test_resource_governor.py      # NEW
│   ├── test_economic_router.py        # NEW
│   └── test_caching.py                # NEW
└── HELIOS_IMPLEMENTATION_PLAN.md      # THIS FILE
```

---

## 🚀 배포 전략

### 단계적 롤아웃

#### Stage 1: Canary (10% traffic)
- Resource Governor 활성화
- 메트릭 수집 시작
- 모니터링

#### Stage 2: Beta (50% traffic)
- Economic Router 활성화
- Caching 활성화
- 성능 비교 분석

#### Stage 3: Full Production (100%)
- 모든 Helios 기능 활성화
- 기존 AutoDev 시스템 폐기
- 지속적인 최적화

---

## 📚 참고 자료

- **PRD**: `[KFP] Claude Max 기반 오케스트레이션 시스템 마스터플랜.pdf`
- **Claude Max Docs**: https://support.claude.com/en/articles/11014257
- **Microsoft Agent Framework**: https://microsoft.github.io/autogen/
- **LLMLingua**: https://github.com/microsoft/LLMLingua
- **SonarQube AI**: https://www.sonarsource.com/products/sonarqube/

---

**작성자**: Claude Opus 4.1
**마지막 업데이트**: 2025-10-25
**상태**: ✅ 설계 완료 - 구현 준비 완료
