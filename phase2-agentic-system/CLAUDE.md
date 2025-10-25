# NERDX APEC MVP - Phase 3: Agentic CPG Ecosystem + AutoDev System

## Project Overview

**Type**: AI-powered CPG brand automation + Autonomous software development system
**Tech Stack**: Python 3.11+, FastAPI, Redis, PostgreSQL
**AI Models**: Claude Sonnet 4.5, Gemini 2.0 Flash Thinking, Sora 2
**Version**: 3.1.0

## Architecture

```
┌─────────────────────────────────────────┐
│     Phase 3: Agentic System (Port 8002) │
├─────────────────────────────────────────┤
│  Phase 3A: CPG Ecosystem Agents         │
│  - Zeitgeist (Market Analysis)          │
│  - Bard (Brand Storytelling)            │
│  - Master Planner (Orchestration)       │
│                                          │
│  Phase 3B: AutoDev System               │
│  - PRD Agent (Gemini)                   │
│  - Code Agent (Claude)                  │
│  - QA Agent (Hybrid)                    │
│  - AutoDev Orchestrator                 │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│   Phase 1: World Model (Port 8000)      │
│   - Analytics Engine                     │
│   - Trend Tracker                        │
│   - ML Predictor                         │
└─────────────────────────────────────────┘
```

## Core File Structure

### Main Application
- **main.py:1** - FastAPI application entry point
- **config.py:1** - Settings and configuration
- **requirements.txt:1** - Python dependencies

### AutoDev System Agents
- **services/agents/prd_agent.py:1** - PRD generation (Gemini)
- **services/agents/code_agent.py:1** - Code implementation (Claude)
- **services/agents/qa_agent.py:1** - Multi-agent code review
- **services/agents/autodev_orchestrator.py:1** - Workflow orchestration

### CPG Ecosystem Agents (Phase 3A)
- **services/agents/zeitgeist_agent.py:1** - Market trend analysis
- **services/agents/bard_agent.py:1** - Brand storytelling
- **services/agents/master_planner.py:1** - Multi-agent orchestration

### API Routers
- **routers/autodev.py:1** - AutoDev API endpoints (17 endpoints)
- **routers/agents.py:1** - CPG agent endpoints
- **routers/workflows.py:1** - Workflow endpoints

### Services
- **services/gemini_service.py:1** - Gemini API integration
- **services/cameo_service.py:1** - CAMEO video generation
- **services/sora_service.py:1** - Sora 2 integration

### Documentation
- **AUTODEV_ARCHITECTURE.md:1** - AutoDev system architecture
- **AUTODEV_IMPLEMENTATION_SUMMARY.md:1** - Implementation complete report
- **PHASE3A_IMPLEMENTATION.md:1** - CPG ecosystem implementation
- **EXPANSION_PLAN_PHASE3.md:1** - Full expansion roadmap

## Key Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py
# Server runs on http://localhost:8002

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8002

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=services --cov=routers --cov-report=html
```

### API Testing

```bash
# Health check
curl http://localhost:8002/health

# Generate PRD
curl -X POST http://localhost:8002/api/v1/autodev/prd/generate \
  -H "Content-Type: application/json" \
  -d '{"title": "Feature Name", "description": "Description"}'

# Feature development workflow
curl -X POST http://localhost:8002/api/v1/autodev/workflows/feature-development \
  -H "Content-Type: application/json" \
  -d '{"issue_number": 1, "issue_title": "Title", "issue_body": "Body"}'

# Multi-agent code review
curl -X POST http://localhost:8002/api/v1/autodev/qa/multi-agent-review \
  -H "Content-Type: application/json" \
  -d '{"pr_number": 1, "diff": "diff content", "plan": {}}'
```

### Documentation

```bash
# View API documentation
open http://localhost:8002/docs          # Swagger UI
open http://localhost:8002/redoc         # ReDoc

# View root endpoint
curl http://localhost:8002/ | jq
```

### Docker

```bash
# Build image
docker build -t nerdx-agentic-system:3.1.0 .

# Run container
docker run -p 8002:8002 \
  -e GEMINI_API_KEY=your_key \
  -e ANTHROPIC_API_KEY=your_key \
  nerdx-agentic-system:3.1.0

# Docker Compose
docker-compose up -d
```

## Coding Standards

### Python Style
- **PEP 8** compliance
- **Black** formatter (line length: 100)
- **isort** for imports
- **Type hints** required for all functions
- **Docstrings**: Google style

### Code Organization
```python
# Standard library imports
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Third-party imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local imports
from services.agents.base_agent import BaseAgent
from config import settings
```

### Async/Await
- Use `async def` for all I/O operations
- Use `await` for async calls
- Use `asyncio.gather()` for parallel operations

### Error Handling
```python
try:
    result = await agent.execute_task(...)
except AgentError as e:
    logger.error(f"Agent error: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Processing task: {task_id}")
logger.error(f"Failed to process: {error}")
logger.debug(f"Debug info: {data}")
```

## API Response Format

### Success Response
```json
{
  "agent_id": "prd-agent-001",
  "agent_type": "prd_agent",
  "task_id": "task-123",
  "status": "success",
  "confidence": 0.88,
  "result": {...},
  "processing_time_ms": 3450
}
```

### Error Response
```json
{
  "error": "ErrorType",
  "message": "Error description",
  "details": {...}
}
```

## Environment Variables

Required:
- `GEMINI_API_KEY` - Gemini API key
- `ANTHROPIC_API_KEY` - Claude API key
- `OPENAI_API_KEY` - Sora API key
- `REDIS_HOST` - Redis host (default: localhost)
- `REDIS_PORT` - Redis port (default: 6379)

Optional:
- `SONAR_TOKEN` - SonarQube token
- `SNYK_TOKEN` - Snyk token
- `GITHUB_TOKEN` - GitHub API token

## Testing Strategy

### Unit Tests
- Test individual agent methods
- Mock external API calls
- Target coverage: 80%+

### Integration Tests
- Test agent coordination
- Test API endpoints
- Test workflows end-to-end

### E2E Tests
- Test via API endpoints
- Test GitHub Actions workflows
- Test quality gates

## Git Workflow

### Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `autodev/issue-{number}` - AutoDev generated

### Commit Messages (Conventional Commits)
```
feat: add PRD generation agent
fix: resolve timeout in code agent
docs: update AutoDev documentation
refactor: improve QA agent structure
test: add unit tests for orchestrator
```

### Pull Requests
- Use AutoDev system for PR creation
- Ensure all quality gates pass
- Get multi-agent code review approval

## Quality Requirements

### Code Quality
- SonarQube rating: A
- Code coverage: ≥80%
- Code duplication: <3%
- Security hotspots: 0

### Performance
- API response time: <5s (95th percentile)
- Agent response time: <10s per task
- Workflow completion: <30 minutes

### Security
- No critical or high vulnerabilities (Snyk)
- Input validation on all endpoints
- API key rotation policy
- Secrets never in code

## Dependencies

### Core
- **FastAPI** 0.104+ - Web framework
- **Pydantic** 2.0+ - Data validation
- **HTTPX** 0.25+ - Async HTTP client
- **Redis** 5.0+ - State management

### AI/ML
- **Anthropic** - Claude API
- **Google AI** - Gemini API
- **OpenAI** - Sora API

### Quality Tools
- **SonarQube** - Code quality
- **Snyk** - Security scanning
- **Pytest** - Testing framework
- **Playwright** - E2E testing

## Monitoring & Observability

### Metrics (Prometheus)
- Agent response times
- Workflow success rates
- API endpoint latency
- Quality gate pass rates

### Logging (Structured)
```python
logger.info("Agent task completed", extra={
    "agent_id": agent_id,
    "task_type": task_type,
    "duration_ms": duration,
    "status": "success"
})
```

### Alerts
- Agent failure rate >5%
- API latency >10s
- Quality gate failures
- Security vulnerabilities detected

## Deployment

### Production Checklist
- [ ] All environment variables configured
- [ ] Redis cluster configured
- [ ] Monitoring dashboards set up
- [ ] Alerting configured
- [ ] Backup strategy in place
- [ ] Rate limiting enabled
- [ ] SSL certificates installed
- [ ] Load balancer configured

### Scaling
- Horizontal scaling via replicas
- Redis cluster for state
- Async task processing
- CDN for static assets

## Support

### Documentation
- Architecture: `AUTODEV_ARCHITECTURE.md`
- Implementation: `AUTODEV_IMPLEMENTATION_SUMMARY.md`
- API Docs: http://localhost:8002/docs

### Troubleshooting
1. Check logs: `tail -f logs/app.log`
2. Verify Redis: `redis-cli ping`
3. Test API: `curl http://localhost:8002/health`
4. Check env vars: `printenv | grep API_KEY`

## Version History

- **3.1.0** - AutoDev system added (PRD, Code, QA agents + Orchestrator)
- **3.0.0** - Phase 3A implementation (Zeitgeist, Bard, Master Planner)
- **2.0.0** - CAMEO video generation with Sora 2
- **1.0.0** - Initial release

---

**Last Updated**: October 11, 2025
**Maintainers**: NERD Development Team
**License**: Proprietary
