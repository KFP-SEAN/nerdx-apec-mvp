# AutoDev System Architecture
## Claude & Gemini 기반 자율 개발 시스템

**Version**: 1.0.0
**Date**: October 11, 2025
**Based on**: [KFP] Claude & Gemini 기반 자율 개발 시스템 구축 PRD

---

## Executive Summary

AutoDev is an autonomous software development system that integrates **Gemini** (strategic planner/designer) and **Claude Code** (execution engine/implementer) with **GitHub Actions** orchestration to transform PRDs into production-ready code autonomously.

### Core Operating Paradigm

```
Gemini (전략가 및 설계자)
  ↓ PRD, User Stories, Acceptance Criteria
AutoDev Orchestrator
  ↓ Execution Plans, Task Breakdown
Claude Code (실행자/개발자)
  ↓ Implementation, Tests, Debugging
Quality Gates (SonarQube + Snyk)
  ↓ Security & Quality Validation
E2E Test Automation
  ↓ Acceptance Validation
Production Deployment
```

---

## System Architecture

### 1. Agent Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│           AUTODEV ORCHESTRATOR AGENT                     │
│     (Workflow Management, Task Coordination)            │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
   ┌────▼────┐            ┌────▼────┐
   │ PLANNER │            │  QA     │
   │  Agent  │◄───────────┤  Agent  │
   └────┬────┘            └────▲────┘
        │                      │
        │  Task Assignment     │  Quality Feedback
        │                      │
   ┌────▼──────────────────────┴────┐
   │      EXECUTOR AGENTS            │
   ├─────────────────────────────────┤
   │  • PRD Agent (Gemini)           │
   │    - PRD generation             │
   │    - Requirements refinement    │
   │    - User story creation        │
   │                                  │
   │  • Code Agent (Claude)          │
   │    - Implementation             │
   │    - Debugging loops            │
   │    - Unit test generation       │
   │                                  │
   │  • Review Agent (Gemini)        │
   │    - Code review                │
   │    - Security analysis          │
   │    - Maintainability check      │
   │                                  │
   │  • Test Agent (Claude)          │
   │    - E2E test generation        │
   │    - Test execution             │
   │    - Coverage reporting         │
   └─────────────────────────────────┘
```

### 2. Core Components

#### A. PRD Agent (Gemini-based)
**Purpose**: Transform vague ideas into concrete, actionable PRDs

**Capabilities**:
- PRD generation from natural language descriptions
- Requirements refinement and clarification
- User story generation (As a... I want... So that...)
- Acceptance criteria creation (Gherkin format)
- Design document generation
- Multimodal analysis (diagrams, screenshots)

**Task Types**:
- `generate_prd`: Create PRD from idea
- `refine_prd`: Enhance existing PRD
- `create_user_stories`: Generate user stories
- `generate_acceptance_criteria`: Create Gherkin scenarios
- `analyze_requirements`: Multimodal requirement analysis

#### B. AutoDev Orchestrator
**Purpose**: Central coordination and workflow management

**Capabilities**:
- Development workflow orchestration
- Task decomposition and dependency management
- Agent coordination (PRD → Code → QA → Deploy)
- Progress tracking and reporting
- GitHub integration (issues, PRs, comments)
- CI/CD pipeline management

**Workflow Templates**:
1. **Feature Development**: PRD → Plan → Implement → Review → Test → Deploy
2. **Bug Fix**: Analysis → Fix → Test → Deploy
3. **Refactoring**: Assessment → Plan → Refactor → Test
4. **Documentation**: Generation → Review → Publish

#### C. Code Agent (Claude-based)
**Purpose**: Code implementation and debugging

**Capabilities**:
- Full codebase implementation
- Multi-file code generation
- Debugging loops with error analysis
- Unit test generation (Jest, Pytest, etc.)
- Code refactoring
- Dependency management
- Git operations (commit, branch, PR)

**Task Types**:
- `implement_feature`: Implement from plan
- `fix_bug`: Debug and fix issues
- `generate_tests`: Create unit tests
- `refactor_code`: Improve code quality
- `update_dependencies`: Manage packages

#### D. QA Agent (Hybrid: Gemini + Quality Tools)
**Purpose**: Quality assurance and validation

**Capabilities**:
- Multi-agent code review
  - Claude: Plan adherence, logic correctness
  - Gemini: Maintainability, security, architecture
- Static analysis integration (SonarQube)
- Security scanning (Snyk)
- Test coverage validation (80% requirement)
- E2E test generation from Gherkin
- Test execution and reporting

**Quality Gates**:
```yaml
SonarQube AI Code Assurance:
  - New Code Coverage: ≥80%
  - New Code Duplication: <3%
  - Security Hotspots: 0
  - Security Rating: A

Snyk Security:
  - Critical Vulnerabilities: 0
  - High Vulnerabilities: 0
  - License Compliance: ✓

Code Review:
  - Claude Review: Plan adherence ✓
  - Gemini Review: Maintainability ✓
```

#### E. Test Agent (Claude-based)
**Purpose**: E2E test automation

**Capabilities**:
- E2E test generation from Gherkin scenarios
- Playwright/Selenium test creation
- Test execution in Docker sandbox
- Visual regression testing
- Performance testing
- Test result reporting

---

## 3. CLAUDE.md Ecosystem

### Hierarchical Context Structure

```
~/.claude/
  └── CLAUDE.md                    # User-level preferences
      - Commit message style (Conventional Commits)
      - Preferred libraries and frameworks
      - Coding conventions
      - Personal workflow preferences

/project-root/
  └── CLAUDE.md                    # Project-level context
      - Architecture overview
      - Core file structure
      - Key dependencies
      - Build commands
      - Coding standards
      - Testing strategy

/project-root/[directory]/
  └── CLAUDE.md                    # Module-level context
      - Module purpose
      - API contracts
      - Local conventions
      - Integration points
```

### Template Structure

```markdown
# Project: [Name]
## Architecture: [Pattern]
## Tech Stack: [Technologies]

### Core Files
- file_path:line_number - Description

### Key Commands
```bash
npm install        # Install dependencies
npm run dev        # Start dev server
npm test          # Run tests
```

### Coding Standards
- Style guide references
- Naming conventions
- Comment requirements

### Quality Requirements
- Test coverage: 80%+
- Security scan: Pass
- Code duplication: <3%
```

---

## 4. GitHub Actions Integration

### Workflow: `.github/workflows/autodev.yml`

```yaml
name: AutoDev - Autonomous Development

on:
  issues:
    types: [assigned, labeled]
  issue_comment:
    types: [created]
  pull_request:
    types: [opened, synchronize]

jobs:
  # Step 1: Plan Feature (Gemini PRD Agent)
  plan_feature:
    if: github.event.issue.assignee && contains(github.event.issue.labels.*.name, 'autodev')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - uses: actions/checkout@v4

      - name: Generate Development Plan
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python scripts/autodev/orchestrator.py plan \
            --issue-number ${{ github.event.issue.number }} \
            --issue-title "${{ github.event.issue.title }}" \
            --issue-body "${{ github.event.issue.body }}"

      - name: Post Plan as Comment
        uses: actions/github-script@v7
        with:
          script: |
            const plan = require('./autodev_plan.json');
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: plan.markdown
            });

  # Step 2: Implement Feature (Claude Code Agent)
  implement_feature:
    if: |
      github.event.comment.body == '/autodev implement' &&
      github.event.issue.assignee
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
    steps:
      - uses: actions/checkout@v4

      - name: Load Development Plan
        id: load-plan
        run: |
          gh issue view ${{ github.event.issue.number }} \
            --json comments \
            --jq '.comments[] | select(.author.login == "github-actions") | .body' \
            > plan.md
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Execute Implementation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/autodev/code_agent.py implement \
            --plan-file plan.md \
            --issue-number ${{ github.event.issue.number }}

      - name: Create Feature Branch & Push
        run: |
          git config user.name "AutoDev Bot"
          git config user.email "autodev@nerdx.app"
          git checkout -b autodev/issue-${{ github.event.issue.number }}
          git add .
          git commit -m "feat: implement issue #${{ github.event.issue.number }}

          🤖 Generated by AutoDev (Claude Code)

          Co-Authored-By: AutoDev <autodev@nerdx.app>"
          git push origin autodev/issue-${{ github.event.issue.number }}

      - name: Create Pull Request
        run: |
          gh pr create \
            --title "feat: ${{ github.event.issue.title }}" \
            --body "Closes #${{ github.event.issue.number }}" \
            --base main \
            --head autodev/issue-${{ github.event.issue.number }}
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # Step 3: Quality Gate (Multi-Agent Review + Tools)
  quality_gate:
    if: github.event.pull_request && startsWith(github.head_ref, 'autodev/')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # Claude Code Review (Plan Adherence)
      - name: Claude Code Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/autodev/review_agent.py claude \
            --pr-number ${{ github.event.pull_request.number }} \
            --aspect plan-adherence

      # Gemini Code Review (Maintainability + Security)
      - name: Gemini Code Review
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python scripts/autodev/review_agent.py gemini \
            --pr-number ${{ github.event.pull_request.number }} \
            --aspect maintainability,security

      # Snyk Security Scan
      - name: Snyk Security Scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          command: test
          args: --severity-threshold=high

      # SonarQube Analysis
      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

      - name: SonarQube Quality Gate
        run: |
          curl -u ${{ secrets.SONAR_TOKEN }}: \
            "${{ secrets.SONAR_HOST_URL }}/api/qualitygates/project_status?projectKey=nerdx-apec-mvp" \
            | jq -e '.projectStatus.status == "OK"'

  # Step 4: E2E Test Automation
  e2e_test:
    if: |
      github.event.pull_request &&
      github.event.pull_request.base.ref == 'staging'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Staging
        run: |
          vercel deploy --staging --token=${{ secrets.VERCEL_TOKEN }}

      - name: Generate E2E Tests from Gherkin
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/autodev/test_agent.py generate-e2e \
            --pr-number ${{ github.event.pull_request.number }} \
            --framework playwright

      - name: Run E2E Tests
        run: |
          npm install
          npx playwright install
          npx playwright test

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 5. Development Workflow

### End-to-End Process

```
1. Issue Assignment
   ├─> GitHub Issue created and labeled 'autodev'
   └─> Assigned to AutoDev bot

2. Plan Generation (Gemini)
   ├─> PRD Agent analyzes issue
   ├─> Generates development plan
   ├─> Creates task breakdown
   └─> Posts plan as comment

3. User Approval
   ├─> Developer reviews plan
   └─> Comments "/autodev implement" to approve

4. Implementation (Claude)
   ├─> Code Agent loads plan
   ├─> Implements across codebase
   ├─> Generates unit tests
   ├─> Commits to feature branch
   └─> Creates Pull Request

5. Quality Gate
   ├─> Claude Review (plan adherence)
   ├─> Gemini Review (maintainability, security)
   ├─> Snyk Security Scan
   ├─> SonarQube Analysis
   └─> Quality gate pass/fail

6. E2E Testing
   ├─> Deploy to staging
   ├─> Generate E2E tests from Gherkin
   ├─> Execute tests
   └─> Report results

7. Deployment
   ├─> Merge to main
   ├─> Production deployment
   └─> Close issue
```

---

## 6. API Endpoints

### AutoDev API (`/api/v1/autodev/*`)

#### PRD Agent
- **POST** `/api/v1/autodev/prd/generate`
  - Generate PRD from idea
  - Parameters: `title`, `description`, `requirements`, `context`

- **POST** `/api/v1/autodev/prd/refine`
  - Refine existing PRD
  - Parameters: `prd_content`, `feedback`, `refinement_goals`

- **POST** `/api/v1/autodev/prd/user-stories`
  - Generate user stories
  - Parameters: `prd_content`, `max_stories`

#### Code Agent
- **POST** `/api/v1/autodev/code/implement`
  - Implement feature from plan
  - Parameters: `plan`, `files`, `test_required`

- **POST** `/api/v1/autodev/code/debug`
  - Debug and fix issues
  - Parameters: `error_log`, `context`, `max_iterations`

- **POST** `/api/v1/autodev/code/test`
  - Generate unit tests
  - Parameters: `file_path`, `coverage_target`

#### QA Agent
- **POST** `/api/v1/autodev/qa/review`
  - Multi-agent code review
  - Parameters: `pr_number`, `diff`, `review_aspects`

- **POST** `/api/v1/autodev/qa/scan`
  - Run quality gates
  - Parameters: `target`, `gate_type` (sonar|snyk)

#### Orchestrator
- **POST** `/api/v1/autodev/orchestrate/feature`
  - Full feature development workflow
  - Parameters: `issue_number`, `workflow_type`

- **GET** `/api/v1/autodev/orchestrate/status/{workflow_id}`
  - Get workflow status
  - Returns: progress, current_step, results

---

## 7. Integration with Existing Phase 3A System

### Synergy with Current Agents

```
Existing Agents (Phase 3A)         AutoDev Agents (New)
├─ Zeitgeist (Market Analyst)      ├─ PRD Agent (Requirements)
├─ Bard (Creative Director)        ├─ Code Agent (Implementation)
└─ Master Planner (Orchestrator)   ├─ QA Agent (Quality)
                                    └─ AutoDev Orchestrator (Dev Workflow)
```

### Combined Workflows

**Example: AI-Powered Product Launch with AutoDev**

```
1. Zeitgeist Agent: Analyze market trends
2. Bard Agent: Create brand narrative
3. PRD Agent: Generate product feature PRD
4. Code Agent: Implement e-commerce features
5. QA Agent: Validate quality
6. Deploy: Launch product
```

---

## 8. Technology Stack

### Core Technologies
- **Python 3.11+**: Agent implementation
- **FastAPI**: API server
- **Redis**: Task queue and state management
- **Docker**: Sandboxed execution environments
- **GitHub Actions**: CI/CD orchestration

### AI Models
- **Gemini 2.0 Flash Thinking**: Strategic planning, PRD generation, code review
  - Context window: 1M+ tokens
  - Multimodal: text + images + code
- **Claude Sonnet 4.5**: Code implementation, debugging, testing
  - Context window: 200K tokens
  - Code-optimized with tool use

### Quality Tools
- **SonarQube AI Code Assurance**: Code quality analysis
- **Snyk**: Security vulnerability scanning
- **Playwright**: E2E test automation
- **Jest/Pytest**: Unit testing frameworks

### Development Tools
- **Git**: Version control
- **GitHub CLI**: API automation
- **Vercel**: Deployment platform
- **Neo4j**: Knowledge graph (optional)

---

## 9. Security & Compliance

### Security Measures
- Docker sandbox isolation for code execution
- API key rotation and secret management
- GitHub Actions security best practices
- Snyk vulnerability scanning (critical/high: 0 tolerance)
- SonarQube security rating: A required

### Compliance
- Conventional Commits standard
- Code review mandatory (multi-agent)
- Test coverage minimum: 80%
- Code duplication maximum: 3%
- Security hotspots: 0 tolerance

---

## 10. Success Metrics

### KPIs
- **Automation Rate**: % of issues resolved autonomously
- **Quality Gate Pass Rate**: % of PRs passing first time
- **Mean Time to Implementation**: Issue → PR creation time
- **Test Coverage**: Maintained >80%
- **Security Score**: Zero critical/high vulnerabilities

### Target Performance
- PRD Generation: <60 seconds
- Code Implementation: <10 minutes (per feature)
- Quality Gate: <5 minutes
- E2E Test Generation: <3 minutes
- Full Workflow (Issue → PR): <20 minutes

---

## 11. Future Enhancements

### Phase 2 (Q1 2026)
- Multi-repository support
- Agent learning and memory persistence
- Advanced rollback mechanisms
- Performance optimization agent
- Infrastructure-as-Code agent

### Phase 3 (Q2 2026)
- Natural language requirements → Code (no PRD needed)
- Autonomous bug detection and fixing
- Self-healing production systems
- Multi-agent collaboration optimization
- Agent performance analytics dashboard

---

## Conclusion

The AutoDev system represents a paradigm shift in software development, combining the strategic capabilities of Gemini with the execution prowess of Claude Code, orchestrated through GitHub Actions. By integrating with the existing Phase 3A agentic system (Zeitgeist, Bard, Master Planner), we create a comprehensive AI-powered ecosystem for autonomous CPG brand development and software engineering.

**Status**: ✅ Architecture Designed - Ready for Implementation

---

**Document Version**: 1.0.0
**Author**: Claude AI + AutoDev System
**Last Updated**: October 11, 2025
