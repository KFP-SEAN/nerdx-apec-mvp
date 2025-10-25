# Routers Directory

## Purpose

FastAPI route handlers for all API endpoints. Provides RESTful API interface to the agentic system.

## Structure

```
routers/
├── __init__.py          # Router exports
├── autodev.py           # AutoDev system endpoints (17)
├── agents.py            # CPG agent endpoints (Phase 3A)
└── workflows.py         # Workflow orchestration endpoints
```

## API Organization

### AutoDev Router (`/api/v1/autodev/*`)

17 endpoints organized by agent:

#### PRD Agent Endpoints (4)
1. `POST /autodev/prd/generate` - Generate PRD from idea
2. `POST /autodev/prd/refine` - Refine existing PRD
3. `POST /autodev/prd/user-stories` - Create user stories
4. `POST /autodev/prd/acceptance-criteria` - Generate Gherkin scenarios

#### Code Agent Endpoints (4)
5. `POST /autodev/code/implement` - Implement feature
6. `POST /autodev/code/fix-bug` - Fix bug with debugging
7. `POST /autodev/code/generate-tests` - Generate unit tests
8. `POST /autodev/code/refactor` - Refactor code

#### QA Agent Endpoints (3)
9. `POST /autodev/qa/multi-agent-review` - Claude + Gemini review
10. `POST /autodev/qa/quality-gates` - Run SonarQube + Snyk + Coverage
11. `POST /autodev/qa/generate-e2e-tests` - Generate E2E tests

#### Orchestrator Endpoints (6)
12. `POST /autodev/workflows/feature-development` - Full feature workflow
13. `POST /autodev/workflows/bug-fix` - Bug fix workflow
14. `POST /autodev/workflows/refactoring` - Refactoring workflow
15. `GET /autodev/workflows/status/{workflow_id}` - Get workflow status
16. `POST /autodev/workflows/pause/{workflow_id}` - Pause workflow
17. `POST /autodev/workflows/cancel/{workflow_id}` - Cancel workflow

### Agents Router (`/api/v1/agents/*`)

Phase 3A CPG ecosystem endpoints for Zeitgeist and Bard agents.

### Workflows Router (`/api/v1/workflows/*`)

Phase 3A workflow orchestration endpoints.

## Request/Response Models

### Pydantic Models

All endpoints use Pydantic models for validation:

```python
from pydantic import BaseModel
from typing import Dict, Any, List

class GeneratePRDRequest(BaseModel):
    """Generate PRD request"""
    title: str
    description: str
    requirements: List[str] = []
    context: str = ""
    target_audience: str = "End users"

class AgentResponse(BaseModel):
    """Standard agent response"""
    agent_id: str
    agent_type: str
    task_id: str
    status: str
    confidence: float
    result: Dict[str, Any]
    processing_time_ms: int | None = None
```

## Endpoint Implementation Pattern

### Standard Structure

```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/endpoint-name")
async def endpoint_handler(request: RequestModel):
    """
    Endpoint description

    Detailed documentation about what this endpoint does,
    parameters, and return values.
    """
    try:
        # 1. Get agent instance
        agent = get_agent()

        # 2. Generate task ID
        task_id = f"task-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # 3. Execute agent task
        response = await agent.execute_task(
            task_id=task_id,
            task_type="task_type",
            parameters=request.model_dump()
        )

        # 4. Return response
        return response.model_dump()

    except Exception as e:
        logger.error(f"Endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

## Error Handling

### HTTP Status Codes

- **200 OK** - Success
- **202 Accepted** - Async operation accepted
- **400 Bad Request** - Invalid request
- **404 Not Found** - Resource not found
- **429 Too Many Requests** - Rate limit exceeded
- **500 Internal Server Error** - Server error
- **503 Service Unavailable** - Service temporarily unavailable

### Error Response Format

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": {
    "additional": "context"
  }
}
```

### Error Handling Example

```python
@router.post("/endpoint")
async def handler(request: Request):
    try:
        result = await process(request)
        return result
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

## Request Validation

### Using Pydantic

```python
from pydantic import BaseModel, Field, validator

class FeatureRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    priority: str = Field(default="medium")

    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high', 'critical']:
            raise ValueError('Invalid priority')
        return v
```

## Response Formatting

### Success Response

Always return the agent response in a consistent format:

```python
return {
    "agent_id": "agent-001",
    "agent_type": "prd_agent",
    "task_id": "task-123",
    "status": "success",
    "confidence": 0.88,
    "result": {
        "prd": {...},
        "metadata": {...}
    },
    "processing_time_ms": 3450
}
```

## Documentation

### OpenAPI/Swagger

Add comprehensive docstrings to all endpoints:

```python
@router.post("/generate-prd")
async def generate_prd(request: GeneratePRDRequest):
    """
    Generate comprehensive PRD from natural language idea

    Uses Gemini 2.0 Flash Thinking to transform vague requirements into
    concrete, actionable Product Requirements Documents.

    **Parameters**:
    - title: Feature/product title
    - description: Natural language description
    - requirements: List of initial requirements (optional)
    - context: Additional context (optional)
    - target_audience: Target users (default: "End users")

    **Returns**:
    - Complete PRD with 12 sections
    - User stories with priorities
    - Acceptance criteria in Gherkin format
    - Success metrics and timeline

    **Example**:
    ```json
    {
      "title": "User Authentication System",
      "description": "Build a secure user authentication system",
      "requirements": ["Email/password login", "OAuth"]
    }
    ```
    """
    # Implementation
```

## Testing

### Unit Tests

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_prd():
    response = client.post(
        "/api/v1/autodev/prd/generate",
        json={
            "title": "Test Feature",
            "description": "Test description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "prd" in data["result"]
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_feature_workflow():
    response = client.post(
        "/api/v1/autodev/workflows/feature-development",
        json={
            "issue_number": 1,
            "issue_title": "Test",
            "issue_body": "Test description"
        }
    )
    assert response.status_code == 200
    workflow_id = response.json()["workflow_id"]

    # Check status
    status_response = client.get(
        f"/api/v1/autodev/workflows/status/{workflow_id}"
    )
    assert status_response.status_code == 200
```

## Performance Considerations

### Async Operations

All route handlers should be async:

```python
@router.post("/endpoint")
async def handler(request: Request):
    # Use await for I/O operations
    result = await agent.execute_task(...)
    return result
```

### Timeouts

Set appropriate timeouts for long-running operations:

```python
from fastapi import BackgroundTasks

@router.post("/long-operation")
async def handler(request: Request, background_tasks: BackgroundTasks):
    # For operations >30s, use background tasks
    background_tasks.add_task(process_long_operation, request)
    return {"status": "accepted", "task_id": task_id}
```

## Security

### Input Validation

Always validate and sanitize input:

```python
from pydantic import validator

class Request(BaseModel):
    code: str

    @validator('code')
    def sanitize_code(cls, v):
        # Remove potentially dangerous patterns
        dangerous = ['eval', 'exec', '__import__']
        for pattern in dangerous:
            if pattern in v:
                raise ValueError(f'Dangerous pattern: {pattern}')
        return v
```

### Authentication

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.post("/protected")
async def protected_endpoint(token: str = Depends(security)):
    # Verify token
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    # Process request
```

## Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/endpoint")
@limiter.limit("10/minute")
async def handler(request: Request):
    # Implementation
```

## Monitoring

### Metrics

Track important metrics:

```python
from prometheus_client import Counter, Histogram

request_count = Counter('api_requests_total', 'Total requests', ['endpoint', 'status'])
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

@router.post("/endpoint")
async def handler(request: Request):
    start = time.time()
    try:
        result = await process(request)
        request_count.labels(endpoint='/endpoint', status='success').inc()
        return result
    finally:
        duration = time.time() - start
        request_duration.observe(duration)
```

---

**Module Owner**: API Team
**Last Updated**: October 11, 2025
