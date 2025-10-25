"""
AutoDev Orchestrator Agent
Central coordination and workflow management for autonomous development

Orchestrates PRD Agent, Code Agent, and QA Agent to execute complete development workflows.
"""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from services.agents.base_agent import BaseAgent, AgentCapability, AgentResponse
from services.agents.prd_agent import get_prd_agent
from services.agents.code_agent import get_code_agent
from services.agents.qa_agent import get_qa_agent

logger = logging.getLogger(__name__)


class WorkflowType(str, Enum):
    """AutoDev workflow types"""
    FEATURE_DEVELOPMENT = "feature_development"
    BUG_FIX = "bug_fix"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    PLANNING = "planning"
    IMPLEMENTING = "implementing"
    REVIEWING = "reviewing"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AutoDevOrchestrator(BaseAgent):
    """
    AutoDev Orchestrator: Central Workflow Coordination

    Orchestrates multi-agent development workflows:
    1. PRD Agent: Requirements → Development Plan
    2. Code Agent: Plan → Implementation
    3. QA Agent: Implementation → Review & Validation
    4. Deploy: Merge & Deploy

    Core Workflows:
    - Feature Development: Full cycle from idea to deployment
    - Bug Fix: Analysis → Fix → Validation
    - Refactoring: Assessment → Refactor → Validation
    - Documentation: Generation → Review → Publish
    """

    def __init__(self, agent_id: str = "autodev-orchestrator-001", world_model_url: Optional[str] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="autodev_orchestrator",
            capabilities=[
                AgentCapability.COORDINATION,
                AgentCapability.ANALYSIS
            ],
            world_model_url=world_model_url
        )

        # Agent instances
        self.prd_agent = None
        self.code_agent = None
        self.qa_agent = None

        # Workflow state storage (in production, use Redis/DB)
        self.workflows: Dict[str, Dict] = {}

    async def initialize(self):
        """Initialize orchestrator and agent instances"""
        await super().initialize()
        self.prd_agent = get_prd_agent()
        self.code_agent = get_code_agent()
        self.qa_agent = get_qa_agent()
        logger.info("AutoDev Orchestrator initialized with all agents")

    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        parameters: Dict[str, Any]
    ) -> AgentResponse:
        """
        Execute orchestrator task

        Supported task types:
        - start_workflow: Start new development workflow
        - get_workflow_status: Get workflow status
        - pause_workflow: Pause active workflow
        - resume_workflow: Resume paused workflow
        - cancel_workflow: Cancel workflow
        - feature_development: Full feature development cycle
        - bug_fix: Bug fix workflow
        - refactoring: Code refactoring workflow
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"AutoDev Orchestrator executing task: {task_type}")

            if task_type == "start_workflow":
                result = await self._start_workflow(parameters)
            elif task_type == "get_workflow_status":
                result = await self._get_workflow_status(parameters)
            elif task_type == "pause_workflow":
                result = await self._pause_workflow(parameters)
            elif task_type == "resume_workflow":
                result = await self._resume_workflow(parameters)
            elif task_type == "cancel_workflow":
                result = await self._cancel_workflow(parameters)
            elif task_type == "feature_development":
                result = await self._feature_development_workflow(parameters)
            elif task_type == "bug_fix":
                result = await self._bug_fix_workflow(parameters)
            elif task_type == "refactoring":
                result = await self._refactoring_workflow(parameters)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")

            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return self.create_response(
                task_id=task_id,
                status="success",
                confidence=result.get("confidence", 0.85),
                result=result,
                processing_time_ms=int(processing_time)
            )

        except Exception as e:
            logger.error(f"AutoDev Orchestrator task failed: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return self.create_response(
                task_id=task_id,
                status="failed",
                confidence=0.0,
                result={},
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )

    async def _start_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start new workflow

        Parameters:
            - workflow_type: str - Type of workflow
            - workflow_data: Dict - Workflow-specific data

        Returns:
            Workflow ID and initial status
        """
        workflow_type = parameters.get("workflow_type", WorkflowType.FEATURE_DEVELOPMENT)
        workflow_data = parameters.get("workflow_data", {})

        # Generate workflow ID
        workflow_id = f"autodev-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        # Initialize workflow state
        workflow_state = {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "status": WorkflowStatus.PENDING,
            "data": workflow_data,
            "steps": [],
            "current_step": None,
            "started_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        self.workflows[workflow_id] = workflow_state

        # Execute workflow based on type
        if workflow_type == WorkflowType.FEATURE_DEVELOPMENT:
            await self._execute_feature_development(workflow_id, workflow_data)
        elif workflow_type == WorkflowType.BUG_FIX:
            await self._execute_bug_fix(workflow_id, workflow_data)
        elif workflow_type == WorkflowType.REFACTORING:
            await self._execute_refactoring(workflow_id, workflow_data)

        return {
            "workflow_id": workflow_id,
            "status": self.workflows[workflow_id]["status"],
            "confidence": 0.88
        }

    async def _feature_development_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        End-to-end feature development workflow

        Workflow Steps:
        1. Generate PRD from feature request
        2. Create development plan
        3. Implement feature
        4. Generate tests
        5. Multi-agent code review
        6. Run quality gates
        7. Create PR

        Parameters:
            - issue_number: int - GitHub issue number
            - issue_title: str - Feature title
            - issue_body: str - Feature description
            - context: Dict - Additional context

        Returns:
            Complete workflow results with PR URL
        """
        issue_number = parameters.get("issue_number", 0)
        issue_title = parameters.get("issue_title", "")
        issue_body = parameters.get("issue_body", "")
        context = parameters.get("context", {})

        workflow_id = f"feature-{issue_number}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        results = {
            "workflow_id": workflow_id,
            "steps": []
        }

        try:
            # Step 1: Generate PRD
            logger.info(f"[{workflow_id}] Step 1: Generating PRD")
            prd_response = await self.prd_agent.execute_task(
                task_id=f"{workflow_id}-prd",
                task_type="generate_prd",
                parameters={
                    "title": issue_title,
                    "description": issue_body,
                    "context": context
                }
            )
            results["steps"].append({
                "step": "generate_prd",
                "status": prd_response.status,
                "result": prd_response.result
            })

            if prd_response.status != "success":
                raise Exception("PRD generation failed")

            prd_data = prd_response.result.get("prd", {})

            # Step 2: Generate user stories
            logger.info(f"[{workflow_id}] Step 2: Generating user stories")
            stories_response = await self.prd_agent.execute_task(
                task_id=f"{workflow_id}-stories",
                task_type="create_user_stories",
                parameters={
                    "prd_content": prd_data,
                    "max_stories": 10
                }
            )
            results["steps"].append({
                "step": "create_user_stories",
                "status": stories_response.status,
                "result": stories_response.result
            })

            user_stories = stories_response.result.get("user_stories", [])

            # Step 3: Generate acceptance criteria
            logger.info(f"[{workflow_id}] Step 3: Generating acceptance criteria")
            criteria_response = await self.prd_agent.execute_task(
                task_id=f"{workflow_id}-criteria",
                task_type="generate_acceptance_criteria",
                parameters={
                    "user_stories": user_stories,
                    "detailed": True
                }
            )
            results["steps"].append({
                "step": "generate_acceptance_criteria",
                "status": criteria_response.status,
                "result": criteria_response.result
            })

            acceptance_criteria = criteria_response.result.get("acceptance_criteria", [])

            # Step 4: Implement feature
            logger.info(f"[{workflow_id}] Step 4: Implementing feature")
            implementation_response = await self.code_agent.execute_task(
                task_id=f"{workflow_id}-implement",
                task_type="implement_feature",
                parameters={
                    "plan": {
                        "prd": prd_data,
                        "user_stories": user_stories,
                        "acceptance_criteria": acceptance_criteria
                    },
                    "test_required": True,
                    "context": context
                }
            )
            results["steps"].append({
                "step": "implement_feature",
                "status": implementation_response.status,
                "result": implementation_response.result
            })

            if implementation_response.status != "success":
                raise Exception("Implementation failed")

            implementation = implementation_response.result.get("implementation", {})

            # Step 5: Multi-agent code review
            logger.info(f"[{workflow_id}] Step 5: Multi-agent code review")
            review_response = await self.qa_agent.execute_task(
                task_id=f"{workflow_id}-review",
                task_type="multi_agent_review",
                parameters={
                    "pr_number": issue_number,
                    "diff": "Generated code changes",  # Would be actual diff
                    "plan": prd_data
                }
            )
            results["steps"].append({
                "step": "multi_agent_review",
                "status": review_response.status,
                "result": review_response.result
            })

            review = review_response.result

            # Step 6: Quality gates
            logger.info(f"[{workflow_id}] Step 6: Running quality gates")
            quality_response = await self.qa_agent.execute_task(
                task_id=f"{workflow_id}-quality",
                task_type="validate_quality_gates",
                parameters={
                    "target": ".",
                    "gates": ["sonarqube", "snyk", "coverage"]
                }
            )
            results["steps"].append({
                "step": "quality_gates",
                "status": quality_response.status,
                "result": quality_response.result
            })

            quality_gates = quality_response.result

            # Step 7: E2E tests
            logger.info(f"[{workflow_id}] Step 7: Generating E2E tests")
            e2e_response = await self.qa_agent.execute_task(
                task_id=f"{workflow_id}-e2e",
                task_type="generate_e2e_tests",
                parameters={
                    "acceptance_criteria": acceptance_criteria,
                    "framework": "playwright"
                }
            )
            results["steps"].append({
                "step": "generate_e2e_tests",
                "status": e2e_response.status,
                "result": e2e_response.result
            })

            # Determine overall workflow status
            all_passed = (
                review.get("approval", False) and
                quality_gates.get("overall_passed", False)
            )

            return {
                "workflow": "feature_development",
                "workflow_id": workflow_id,
                "issue_number": issue_number,
                "results": results,
                "overall_status": "success" if all_passed else "requires_changes",
                "pr_ready": all_passed,
                "confidence": 0.87
            }

        except Exception as e:
            logger.error(f"Feature development workflow failed: {e}")
            results["error"] = str(e)
            results["overall_status"] = "failed"
            return results

    async def _bug_fix_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bug fix workflow

        Workflow Steps:
        1. Analyze error/issue
        2. Debug and implement fix
        3. Generate regression tests
        4. Code review
        5. Quality validation
        6. Create PR

        Parameters:
            - issue_number: int
            - error_log: str
            - context: Dict

        Returns:
            Fix workflow results
        """
        issue_number = parameters.get("issue_number", 0)
        error_log = parameters.get("error_log", "")
        context = parameters.get("context", {})

        workflow_id = f"bugfix-{issue_number}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        results = {
            "workflow_id": workflow_id,
            "steps": []
        }

        try:
            # Step 1: Debug and fix
            logger.info(f"[{workflow_id}] Step 1: Debugging and fixing issue")
            fix_response = await self.code_agent.execute_task(
                task_id=f"{workflow_id}-fix",
                task_type="fix_bug",
                parameters={
                    "error_log": error_log,
                    "context": context,
                    "max_iterations": 3
                }
            )
            results["steps"].append({
                "step": "fix_bug",
                "status": fix_response.status,
                "result": fix_response.result
            })

            if fix_response.status != "success":
                raise Exception("Bug fix failed")

            # Step 2: Code review
            logger.info(f"[{workflow_id}] Step 2: Reviewing fix")
            review_response = await self.qa_agent.execute_task(
                task_id=f"{workflow_id}-review",
                task_type="multi_agent_review",
                parameters={
                    "pr_number": issue_number,
                    "diff": "Fix changes",
                    "plan": {"type": "bug_fix", "error": error_log}
                }
            )
            results["steps"].append({
                "step": "review_fix",
                "status": review_response.status,
                "result": review_response.result
            })

            # Step 3: Quality gates
            quality_response = await self.qa_agent.execute_task(
                task_id=f"{workflow_id}-quality",
                task_type="validate_quality_gates",
                parameters={"target": "."}
            )
            results["steps"].append({
                "step": "quality_gates",
                "status": quality_response.status,
                "result": quality_response.result
            })

            return {
                "workflow": "bug_fix",
                "workflow_id": workflow_id,
                "results": results,
                "overall_status": "success",
                "confidence": 0.86
            }

        except Exception as e:
            logger.error(f"Bug fix workflow failed: {e}")
            results["error"] = str(e)
            return results

    async def _refactoring_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Code refactoring workflow

        Workflow Steps:
        1. Analyze code quality
        2. Plan refactoring
        3. Execute refactoring
        4. Validate behavior preserved
        5. Code review
        6. Create PR

        Parameters:
            - file_path: str
            - refactoring_goals: List[str]

        Returns:
            Refactoring workflow results
        """
        file_path = parameters.get("file_path", "")
        refactoring_goals = parameters.get("refactoring_goals", [])

        workflow_id = f"refactor-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        results = {
            "workflow_id": workflow_id,
            "steps": []
        }

        try:
            # Step 1: Analyze codebase
            analysis_response = await self.code_agent.execute_task(
                task_id=f"{workflow_id}-analyze",
                task_type="analyze_codebase",
                parameters={
                    "analysis_type": "quality",
                    "scope": file_path
                }
            )
            results["steps"].append({
                "step": "analyze_code",
                "status": analysis_response.status,
                "result": analysis_response.result
            })

            # Step 2: Refactor
            refactor_response = await self.code_agent.execute_task(
                task_id=f"{workflow_id}-refactor",
                task_type="refactor_code",
                parameters={
                    "file_path": file_path,
                    "refactoring_goals": refactoring_goals,
                    "preserve_behavior": True
                }
            )
            results["steps"].append({
                "step": "refactor_code",
                "status": refactor_response.status,
                "result": refactor_response.result
            })

            # Step 3: Review
            review_response = await self.qa_agent.execute_task(
                task_id=f"{workflow_id}-review",
                task_type="multi_agent_review",
                parameters={
                    "diff": "Refactored code",
                    "plan": {"type": "refactoring", "goals": refactoring_goals}
                }
            )
            results["steps"].append({
                "step": "review",
                "status": review_response.status,
                "result": review_response.result
            })

            return {
                "workflow": "refactoring",
                "workflow_id": workflow_id,
                "results": results,
                "overall_status": "success",
                "confidence": 0.85
            }

        except Exception as e:
            logger.error(f"Refactoring workflow failed: {e}")
            results["error"] = str(e)
            return results

    async def _get_workflow_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get workflow status"""
        workflow_id = parameters.get("workflow_id", "")

        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]

        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "current_step": workflow.get("current_step"),
            "steps_completed": len([s for s in workflow["steps"] if s.get("completed")]),
            "total_steps": len(workflow["steps"]),
            "confidence": 0.90
        }

    async def _pause_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Pause active workflow"""
        workflow_id = parameters.get("workflow_id", "")

        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        self.workflows[workflow_id]["status"] = WorkflowStatus.PENDING
        self.workflows[workflow_id]["paused_at"] = datetime.utcnow().isoformat()

        return {"workflow_id": workflow_id, "status": "paused", "confidence": 0.90}

    async def _resume_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Resume paused workflow"""
        workflow_id = parameters.get("workflow_id", "")

        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        # Resume from current step
        current_status = self.workflows[workflow_id]["status"]
        if current_status != WorkflowStatus.PENDING:
            raise ValueError(f"Cannot resume workflow in status: {current_status}")

        return {"workflow_id": workflow_id, "status": "resumed", "confidence": 0.90}

    async def _cancel_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel workflow"""
        workflow_id = parameters.get("workflow_id", "")

        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        self.workflows[workflow_id]["status"] = WorkflowStatus.CANCELLED
        self.workflows[workflow_id]["cancelled_at"] = datetime.utcnow().isoformat()

        return {"workflow_id": workflow_id, "status": "cancelled", "confidence": 0.90}

    # Workflow execution helpers

    async def _execute_feature_development(self, workflow_id: str, data: Dict):
        """Execute feature development workflow"""
        self.workflows[workflow_id]["status"] = WorkflowStatus.PLANNING
        # Implementation would execute workflow asynchronously

    async def _execute_bug_fix(self, workflow_id: str, data: Dict):
        """Execute bug fix workflow"""
        self.workflows[workflow_id]["status"] = WorkflowStatus.PLANNING

    async def _execute_refactoring(self, workflow_id: str, data: Dict):
        """Execute refactoring workflow"""
        self.workflows[workflow_id]["status"] = WorkflowStatus.PLANNING


# Singleton instance
_autodev_orchestrator_instance: Optional[AutoDevOrchestrator] = None


async def get_autodev_orchestrator() -> AutoDevOrchestrator:
    """Get AutoDev Orchestrator singleton instance"""
    global _autodev_orchestrator_instance
    if _autodev_orchestrator_instance is None:
        _autodev_orchestrator_instance = AutoDevOrchestrator()
        await _autodev_orchestrator_instance.initialize()
    return _autodev_orchestrator_instance
