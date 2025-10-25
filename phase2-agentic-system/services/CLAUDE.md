# Services Directory

## Purpose

Core business logic and service implementations for the Agentic CPG Ecosystem and AutoDev system.

## Structure

```
services/
├── agents/              # AI agent implementations
│   ├── base_agent.py    # Base agent class
│   ├── prd_agent.py     # PRD generation (Gemini)
│   ├── code_agent.py    # Code implementation (Claude)
│   ├── qa_agent.py      # Quality assurance (Hybrid)
│   ├── autodev_orchestrator.py  # Workflow orchestration
│   ├── zeitgeist_agent.py       # Market analysis
│   ├── bard_agent.py            # Brand storytelling
│   └── master_planner.py        # Multi-agent orchestration
├── gemini_service.py    # Gemini API integration
├── cameo_service.py     # CAMEO video generation
├── sora_service.py      # Sora 2 integration
└── storage_service.py   # File storage (S3/GCS/local)
```

## Agent Base Class

### BaseAgent (base_agent.py:38)

All agents inherit from `BaseAgent` which provides:
- Standard response format
- AI model integration (Claude, Gemini)
- World Model API integration
- Error handling
- Logging

```python
from services.agents.base_agent import BaseAgent, AgentCapability, AgentResponse

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="my-agent-001",
            agent_type="my_agent",
            capabilities=[AgentCapability.ANALYSIS]
        )

    async def execute_task(self, task_id, task_type, parameters):
        # Implementation
        return self.create_response(
            task_id=task_id,
            status="success",
            confidence=0.85,
            result={...}
        )
```

## AutoDev Agents

### PRD Agent (prd_agent.py:1)
**Purpose**: Transform ideas into PRDs using Gemini

**Key Methods**:
- `_generate_prd()` - Create comprehensive PRD
- `_refine_prd()` - Enhance existing PRD
- `_create_user_stories()` - Generate user stories
- `_generate_acceptance_criteria()` - Create Gherkin scenarios

**Task Types**: `generate_prd`, `refine_prd`, `create_user_stories`, `generate_acceptance_criteria`

### Code Agent (code_agent.py:1)
**Purpose**: Implement features and fix bugs using Claude

**Key Methods**:
- `_implement_feature()` - Code implementation from plan
- `_fix_bug()` - Debug and fix issues (3 iterations max)
- `_generate_tests()` - Create unit tests
- `_refactor_code()` - Improve code quality

**Task Types**: `implement_feature`, `fix_bug`, `generate_tests`, `refactor_code`

### QA Agent (qa_agent.py:1)
**Purpose**: Multi-agent review and quality gates

**Key Methods**:
- `_multi_agent_review()` - Claude + Gemini review
- `_claude_code_review()` - First-tier review (plan adherence)
- `_gemini_code_review()` - Second-tier review (maintainability/security)
- `_validate_quality_gates()` - Run SonarQube + Snyk + Coverage

**Task Types**: `multi_agent_review`, `validate_quality_gates`, `generate_e2e_tests`

### AutoDev Orchestrator (autodev_orchestrator.py:1)
**Purpose**: Coordinate multi-agent workflows

**Key Methods**:
- `_feature_development_workflow()` - Full feature cycle
- `_bug_fix_workflow()` - Bug fix cycle
- `_refactoring_workflow()` - Refactoring cycle

**Task Types**: `feature_development`, `bug_fix`, `refactoring`

## CPG Ecosystem Agents (Phase 3A)

### Zeitgeist Agent (zeitgeist_agent.py:1)
**Purpose**: Market intelligence and trend detection

**Task Types**: `analyze_trends`, `identify_opportunities`, `generate_weekly_report`

### Bard Agent (bard_agent.py:1)
**Purpose**: Brand storytelling and content generation

**Task Types**: `generate_brand_story`, `create_campaign`, `atomize_content`

### Master Planner (master_planner.py:1)
**Purpose**: Multi-agent workflow orchestration

**Task Types**: `create_goal`, `execute_goal`, `get_goal_status`

## Service Integrations

### Gemini Service (gemini_service.py:1)
**Purpose**: Direct Gemini API integration

```python
from services.gemini_service import gemini_service

# Generate content
response = await gemini_service.generate_content(
    prompt="Your prompt",
    system_instruction="System instructions",
    temperature=0.8
)

# Generate structured JSON
data = await gemini_service.generate_structured_output(
    prompt="Your prompt",
    schema={...},
    temperature=0.7
)

# Multimodal analysis
result = await gemini_service.analyze_multimodal(
    prompt="Analyze this",
    images=["base64_image"],
    temperature=0.7
)
```

## Coding Conventions

### Agent Implementation
1. Inherit from `BaseAgent`
2. Define `agent_id`, `agent_type`, `capabilities`
3. Implement `execute_task()` method
4. Use `create_response()` for standardized output
5. Add comprehensive docstrings

### Error Handling
```python
try:
    result = await self._do_something()
except Exception as e:
    logger.error(f"Task failed: {e}")
    return self.create_response(
        task_id=task_id,
        status="failed",
        confidence=0.0,
        result={},
        error_message=str(e)
    )
```

### AI Model Calls
```python
# Claude
response = await self.call_claude(
    prompt="Your prompt",
    system_prompt="System prompt",
    max_tokens=4096
)

# Gemini
response = await gemini_service.generate_content(
    prompt="Your prompt",
    temperature=0.8
)
```

## Testing

### Unit Tests
```python
import pytest
from services.agents.prd_agent import PRDAgent

@pytest.mark.asyncio
async def test_prd_generation():
    agent = PRDAgent()
    response = await agent.execute_task(
        task_id="test-001",
        task_type="generate_prd",
        parameters={"title": "Test", "description": "Test"}
    )
    assert response.status == "success"
    assert response.confidence > 0.7
```

### Mock AI Calls
```python
from unittest.mock import AsyncMock, patch

@patch('services.gemini_service.gemini_service.generate_content')
async def test_with_mock(mock_generate):
    mock_generate.return_value = "Mocked response"
    # Test code
```

## Performance Targets

| Agent | Operation | Target Time |
|-------|-----------|-------------|
| PRD Agent | generate_prd | <60s |
| Code Agent | implement_feature | <5min |
| QA Agent | multi_agent_review | <2min |
| Orchestrator | feature_development | <20min |

## Dependencies

- **HTTPX** - Async HTTP client
- **Pydantic** - Data validation
- **Python-dotenv** - Environment variables
- **Anthropic SDK** - Claude API (optional)
- **Google AI SDK** - Gemini API (optional)

---

**Module Owner**: Services Team
**Last Updated**: October 11, 2025
