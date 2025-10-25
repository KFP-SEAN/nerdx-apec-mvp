"""
AutoDev API Endpoints
Claude & Gemini-based Autonomous Development System

Complete workflow automation: PRD → Code → Review → Deploy
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from services.agents.prd_agent import get_prd_agent
from services.agents.code_agent import get_code_agent
from services.agents.qa_agent import get_qa_agent
from services.agents.autodev_orchestrator import get_autodev_orchestrator, WorkflowType

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Request/Response Models ====================

# PRD Agent Models
class GeneratePRDRequest(BaseModel):
    """Generate PRD from idea"""
    title: str
    description: str
    requirements: List[str] = []
    context: str = ""
    target_audience: str = "End users"


class RefinePRDRequest(BaseModel):
    """Refine existing PRD"""
    prd_content: Dict[str, Any]
    feedback: str
    refinement_goals: List[str] = []


class CreateUserStoriesRequest(BaseModel):
    """Generate user stories"""
    prd_content: Dict[str, Any]
    max_stories: int = 10
    focus_areas: List[str] = []


class GenerateAcceptanceCriteriaRequest(BaseModel):
    """Generate Gherkin acceptance criteria"""
    user_stories: List[Dict[str, Any]]
    detailed: bool = True


# Code Agent Models
class ImplementFeatureRequest(BaseModel):
    """Implement feature from plan"""
    plan: Dict[str, Any]
    files: List[str] = []
    test_required: bool = True
    context: Dict[str, Any] = {}


class FixBugRequest(BaseModel):
    """Debug and fix issue"""
    error_log: str
    context: Dict[str, Any] = {}
    max_iterations: int = 3


class GenerateTestsRequest(BaseModel):
    """Generate unit tests"""
    file_path: str
    coverage_target: float = 0.8
    test_framework: str = "auto"


class RefactorCodeRequest(BaseModel):
    """Refactor code"""
    file_path: str
    refactoring_goals: List[str]
    preserve_behavior: bool = True


# QA Agent Models
class MultiAgentReviewRequest(BaseModel):
    """Multi-agent code review"""
    pr_number: int
    diff: str
    plan: Dict[str, Any]
    review_aspects: List[str] = ["all"]


class ValidateQualityGatesRequest(BaseModel):
    """Validate quality gates"""
    target: str = "."
    gates: List[str] = ["sonarqube", "snyk", "coverage"]


class GenerateE2ETestsRequest(BaseModel):
    """Generate E2E tests"""
    acceptance_criteria: List[Dict[str, Any]]
    framework: str = "playwright"
    platform: str = "web"


# Orchestrator Models
class FeatureDevelopmentRequest(BaseModel):
    """Full feature development workflow"""
    issue_number: int
    issue_title: str
    issue_body: str
    context: Dict[str, Any] = {}


class BugFixWorkflowRequest(BaseModel):
    """Bug fix workflow"""
    issue_number: int
    error_log: str
    context: Dict[str, Any] = {}


class RefactoringWorkflowRequest(BaseModel):
    """Refactoring workflow"""
    file_path: str
    refactoring_goals: List[str]


class WorkflowStatusRequest(BaseModel):
    """Get workflow status"""
    workflow_id: str


# ==================== PRD Agent Endpoints ====================

@router.post("/prd/generate")
async def generate_prd(request: GeneratePRDRequest):
    """
    Generate comprehensive PRD from natural language idea

    Uses Gemini 2.0 Flash Thinking to transform vague requirements into
    concrete, actionable Product Requirements Documents.

    Returns:
    - Executive summary
    - Problem statement
    - Objectives & goals
    - User stories
    - Functional & non-functional requirements
    - Acceptance criteria (Gherkin)
    - Technical considerations
    - Success metrics
    - Timeline & risks
    """
    try:
        agent = get_prd_agent()
        task_id = f"prd-generate-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="generate_prd",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"PRD generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/prd/refine")
async def refine_prd(request: RefinePRDRequest):
    """
    Refine existing PRD based on stakeholder feedback

    Incorporates feedback while maintaining PRD structure and improving
    clarity and specificity.
    """
    try:
        agent = get_prd_agent()
        task_id = f"prd-refine-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="refine_prd",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"PRD refinement failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/prd/user-stories")
async def create_user_stories(request: CreateUserStoriesRequest):
    """
    Generate user stories from requirements

    Creates user stories in standard format:
    "As a [user], I want [feature], so that [benefit]"

    Includes:
    - Priority (Critical, High, Medium, Low)
    - Story points estimate
    - Acceptance criteria
    """
    try:
        agent = get_prd_agent()
        task_id = f"user-stories-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="create_user_stories",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"User story generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/prd/acceptance-criteria")
async def generate_acceptance_criteria(request: GenerateAcceptanceCriteriaRequest):
    """
    Generate Gherkin-format acceptance criteria

    Creates Given-When-Then scenarios for each user story, covering:
    - Happy path scenarios
    - Alternative paths
    - Edge cases and error conditions
    - Data validation scenarios
    """
    try:
        agent = get_prd_agent()
        task_id = f"acceptance-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="generate_acceptance_criteria",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Acceptance criteria generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Code Agent Endpoints ====================

@router.post("/code/implement")
async def implement_feature(request: ImplementFeatureRequest):
    """
    Implement feature from development plan

    Uses Claude Sonnet 4.5 to transform plans into production-ready code with:
    - Full codebase implementation
    - Multi-file code generation
    - Unit test generation (if test_required=True)
    - CLAUDE.md context integration
    - Comprehensive error handling
    """
    try:
        agent = get_code_agent()
        task_id = f"implement-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="implement_feature",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Feature implementation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/code/fix-bug")
async def fix_bug(request: FixBugRequest):
    """
    Debug and fix issue with iterative debugging

    Analyzes error logs, identifies root cause, implements fix,
    and adds regression tests. Supports up to max_iterations attempts.
    """
    try:
        agent = get_code_agent()
        task_id = f"bugfix-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="fix_bug",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Bug fix failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/code/generate-tests")
async def generate_tests(request: GenerateTestsRequest):
    """
    Generate comprehensive unit tests

    Creates tests with:
    - Happy path and edge case coverage
    - Error condition testing
    - Boundary value testing
    - Mock external dependencies
    - Target coverage: 80%+
    """
    try:
        agent = get_code_agent()
        task_id = f"tests-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="generate_tests",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/code/refactor")
async def refactor_code(request: RefactorCodeRequest):
    """
    Refactor code for improved quality

    Improves:
    - Readability and maintainability
    - Complexity reduction
    - Code smell elimination
    - SOLID principles adherence
    - Documentation
    """
    try:
        agent = get_code_agent()
        task_id = f"refactor-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="refactor_code",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Code refactoring failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== QA Agent Endpoints ====================

@router.post("/qa/multi-agent-review")
async def multi_agent_review(request: MultiAgentReviewRequest):
    """
    Multi-agent code review: Claude + Gemini

    Two-tier review process:
    1. Claude Review: Plan adherence, logic correctness, implementation quality
    2. Gemini Review: Maintainability, security, architecture, scalability

    Returns combined review with approval/rejection decision.

    Quality Scores (0-10):
    - Plan adherence
    - Logic correctness
    - Maintainability
    - Security
    - Architecture

    Approval Criteria:
    - No blockers
    - Overall score >= 6.0
    - Security score >= 7.0
    """
    try:
        agent = get_qa_agent()
        task_id = f"review-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="multi_agent_review",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Multi-agent review failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/qa/quality-gates")
async def validate_quality_gates(request: ValidateQualityGatesRequest):
    """
    Run all quality gates

    Quality Gates:
    1. **SonarQube AI Code Assurance**:
       - New code coverage: >= 80%
       - New code duplication: < 3%
       - Security hotspots: 0
       - Security rating: A

    2. **Snyk Security Scan**:
       - Critical vulnerabilities: 0
       - High vulnerabilities: 0

    3. **Test Coverage**:
       - New code coverage: >= 80%

    Returns pass/fail for each gate and overall status.
    """
    try:
        agent = get_qa_agent()
        task_id = f"quality-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="validate_quality_gates",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Quality gate validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/qa/generate-e2e-tests")
async def generate_e2e_tests(request: GenerateE2ETestsRequest):
    """
    Generate E2E tests from Gherkin acceptance criteria

    Transforms Given-When-Then scenarios into executable tests.

    Supported Frameworks:
    - Playwright (default)
    - Selenium
    - Cypress

    Platforms:
    - Web (default)
    - Mobile
    """
    try:
        agent = get_qa_agent()
        task_id = f"e2e-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await agent.execute_task(
            task_id=task_id,
            task_type="generate_e2e_tests",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"E2E test generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Orchestrator Endpoints ====================

@router.post("/workflows/feature-development")
async def feature_development_workflow(request: FeatureDevelopmentRequest):
    """
    End-to-end feature development workflow

    Complete automation: Idea → PR

    Workflow Steps:
    1. Generate PRD (Gemini)
    2. Create user stories (Gemini)
    3. Generate acceptance criteria (Gemini)
    4. Implement feature (Claude)
    5. Generate tests (Claude)
    6. Multi-agent code review (Claude + Gemini)
    7. Run quality gates (SonarQube + Snyk + Coverage)
    8. Generate E2E tests (Claude)
    9. Create PR (if all passed)

    Average Duration: 15-20 minutes

    Returns:
    - Workflow ID
    - Step-by-step results
    - Overall status (success/requires_changes/failed)
    - PR ready status
    """
    try:
        orchestrator = await get_autodev_orchestrator()
        task_id = f"feature-workflow-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await orchestrator.execute_task(
            task_id=task_id,
            task_type="feature_development",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Feature development workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/workflows/bug-fix")
async def bug_fix_workflow(request: BugFixWorkflowRequest):
    """
    Bug fix workflow

    Complete automation: Error → Fix → PR

    Workflow Steps:
    1. Analyze error (Claude)
    2. Debug and implement fix (Claude)
    3. Generate regression tests (Claude)
    4. Code review (Claude + Gemini)
    5. Quality validation (SonarQube + Snyk)
    6. Create PR

    Average Duration: 5-10 minutes
    """
    try:
        orchestrator = await get_autodev_orchestrator()
        task_id = f"bugfix-workflow-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await orchestrator.execute_task(
            task_id=task_id,
            task_type="bug_fix",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Bug fix workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/workflows/refactoring")
async def refactoring_workflow(request: RefactoringWorkflowRequest):
    """
    Code refactoring workflow

    Workflow Steps:
    1. Analyze code quality (Claude)
    2. Plan refactoring (Claude)
    3. Execute refactoring (Claude)
    4. Validate behavior preserved (tests)
    5. Code review (Claude + Gemini)
    6. Create PR

    Average Duration: 10-15 minutes
    """
    try:
        orchestrator = await get_autodev_orchestrator()
        task_id = f"refactor-workflow-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await orchestrator.execute_task(
            task_id=task_id,
            task_type="refactoring",
            parameters=request.model_dump()
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Refactoring workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/workflows/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get workflow execution status

    Returns:
    - Workflow ID
    - Current status
    - Current step
    - Steps completed / total
    - Results (if completed)
    """
    try:
        orchestrator = await get_autodev_orchestrator()
        task_id = f"status-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await orchestrator.execute_task(
            task_id=task_id,
            task_type="get_workflow_status",
            parameters={"workflow_id": workflow_id}
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Workflow status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/workflows/cancel/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """
    Cancel active workflow

    Stops workflow execution and marks as cancelled.
    """
    try:
        orchestrator = await get_autodev_orchestrator()
        task_id = f"cancel-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        response = await orchestrator.execute_task(
            task_id=task_id,
            task_type="cancel_workflow",
            parameters={"workflow_id": workflow_id}
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Workflow cancellation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
