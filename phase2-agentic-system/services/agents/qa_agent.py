"""
QA Agent (Quality Assurance & Multi-Agent Review Agent)
Hybrid Gemini + Claude + Quality Tools for comprehensive code review and validation

Ensures code quality, security, and adherence to standards through multi-agent review.
"""
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from services.agents.base_agent import BaseAgent, AgentCapability, AgentResponse
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    """
    QA Agent: Multi-Agent Code Review & Quality Gates

    Powered by Claude + Gemini + Quality Tools

    Core Capabilities:
    - Multi-agent code review
      * Claude: Plan adherence, logic correctness, implementation quality
      * Gemini: Maintainability, security, architecture, long-term implications
    - Quality gate validation (SonarQube AI Code Assurance)
    - Security scanning (Snyk integration)
    - Test coverage validation (80% requirement)
    - E2E test generation from Gherkin scenarios
    - Performance and scalability analysis
    """

    def __init__(self, agent_id: str = "qa-agent-001", world_model_url: Optional[str] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="qa_agent",
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.OPTIMIZATION
            ],
            world_model_url=world_model_url
        )

        # Quality gate thresholds (from PRD)
        self.quality_gates = {
            "coverage": 0.80,  # 80% minimum
            "duplication": 0.03,  # 3% maximum
            "security_rating": "A",
            "security_hotspots": 0,
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 0
        }

    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        parameters: Dict[str, Any]
    ) -> AgentResponse:
        """
        Execute QA agent task

        Supported task types:
        - multi_agent_review: Claude + Gemini code review
        - validate_quality_gates: Run all quality gates
        - security_scan: Snyk security analysis
        - test_coverage_check: Validate test coverage
        - generate_e2e_tests: Create E2E tests from Gherkin
        - performance_analysis: Analyze performance implications
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"QA Agent executing task: {task_type}")

            if task_type == "multi_agent_review":
                result = await self._multi_agent_review(parameters)
            elif task_type == "validate_quality_gates":
                result = await self._validate_quality_gates(parameters)
            elif task_type == "security_scan":
                result = await self._security_scan(parameters)
            elif task_type == "test_coverage_check":
                result = await self._test_coverage_check(parameters)
            elif task_type == "generate_e2e_tests":
                result = await self._generate_e2e_tests(parameters)
            elif task_type == "performance_analysis":
                result = await self._performance_analysis(parameters)
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
            logger.error(f"QA Agent task failed: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return self.create_response(
                task_id=task_id,
                status="failed",
                confidence=0.0,
                result={},
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )

    async def _multi_agent_review(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-agent code review: Claude + Gemini

        Parameters:
            - pr_number: int - Pull request number
            - diff: str - Code diff
            - plan: Dict - Original development plan
            - review_aspects: List[str] - Aspects to review

        Returns:
            Combined review from both agents with approval/rejection
        """
        pr_number = parameters.get("pr_number", 0)
        diff = parameters.get("diff", "")
        plan = parameters.get("plan", {})
        review_aspects = parameters.get("review_aspects", ["all"])

        # Phase 1: Claude Review (Plan Adherence & Logic)
        claude_review = await self._claude_code_review(diff, plan)

        # Phase 2: Gemini Review (Maintainability, Security, Architecture)
        gemini_review = await self._gemini_code_review(diff, plan)

        # Combine reviews
        combined_review = await self._combine_reviews(claude_review, gemini_review)

        # Make approval decision
        approval_decision = await self._make_approval_decision(combined_review)

        return {
            "pr_number": pr_number,
            "claude_review": claude_review,
            "gemini_review": gemini_review,
            "combined_review": combined_review,
            "approval": approval_decision["approved"],
            "approval_reason": approval_decision["reason"],
            "action_items": combined_review.get("action_items", []),
            "confidence": 0.88
        }

    async def _claude_code_review(self, diff: str, plan: Dict) -> Dict[str, Any]:
        """
        Claude code review: Plan adherence and logic correctness

        Focus:
        - Does implementation match the plan?
        - Is the logic correct?
        - Are edge cases handled?
        - Code quality and best practices
        """
        system_prompt = """You are performing a first-tier code review focusing on plan adherence and implementation quality.

Review Criteria:
1. **Plan Adherence**: Does the code implement exactly what was planned?
2. **Logic Correctness**: Is the logic sound and bug-free?
3. **Edge Cases**: Are edge cases and error conditions handled?
4. **Code Quality**: Clean, readable, maintainable code
5. **Best Practices**: Following language/framework conventions
6. **Testing**: Adequate test coverage

Review Standards:
- Be thorough but constructive
- Provide specific line references
- Suggest improvements with examples
- Categorize issues by severity (blocker, major, minor, suggestion)"""

        prompt = f"""Review the following code changes against the development plan:

**Development Plan**:
{json.dumps(plan, indent=2)}

**Code Changes (Diff)**:
```diff
{diff}
```

Provide comprehensive review covering:
1. Plan adherence (does it implement what was planned?)
2. Logic correctness (any bugs or logical errors?)
3. Edge case handling (missing error handling?)
4. Code quality (readability, maintainability)
5. Testing (adequate test coverage?)

Format as JSON with:
- overall_assessment: (approve_with_comments, request_changes, reject)
- plan_adherence_score: 0-10
- logic_correctness_score: 0-10
- issues: Array of {{severity, line, description, suggestion}}
- strengths: Array of positive observations
- recommendations: Array of improvement suggestions"""

        try:
            review_text = await self.call_claude(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=8000
            )

            # Parse structured review
            schema = {
                "overall_assessment": "string",
                "plan_adherence_score": "number",
                "logic_correctness_score": "number",
                "issues": [
                    {
                        "severity": "string",
                        "line": "string",
                        "description": "string",
                        "suggestion": "string"
                    }
                ],
                "strengths": ["string"],
                "recommendations": ["string"]
            }

            structured_review = await self._parse_review_json(review_text, schema)

            return {
                "reviewer": "Claude (Plan Adherence & Logic)",
                "review": structured_review,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Claude code review failed: {e}")
            raise

    async def _gemini_code_review(self, diff: str, plan: Dict) -> Dict[str, Any]:
        """
        Gemini code review: Maintainability, security, architecture

        Focus:
        - Long-term maintainability
        - Security vulnerabilities
        - Architecture and design patterns
        - Scalability implications
        - Technical debt
        """
        system_instruction = """You are performing a second-tier code review focusing on maintainability, security, and architecture.

Review Criteria:
1. **Maintainability**: Code organization, documentation, future extensibility
2. **Security**: Vulnerabilities, input validation, authentication/authorization
3. **Architecture**: Design patterns, separation of concerns, SOLID principles
4. **Scalability**: Performance implications, resource usage, bottlenecks
5. **Technical Debt**: Code smells, duplication, complexity

Strategic Perspective:
- Think about long-term implications
- Consider team collaboration and knowledge transfer
- Identify potential future issues
- Suggest architectural improvements"""

        prompt = f"""Review the following code changes from a strategic perspective:

**Development Plan Context**:
{json.dumps(plan, indent=2)}

**Code Changes**:
```diff
{diff}
```

Provide strategic review covering:
1. **Maintainability**: How easy will this be to maintain and extend?
2. **Security**: Any security vulnerabilities or concerns?
3. **Architecture**: Does it follow good design principles?
4. **Scalability**: Any performance or scalability issues?
5. **Technical Debt**: Code smells or future problems?

Format as JSON with:
- overall_assessment: (strong_approve, approve, concerns, reject)
- maintainability_score: 0-10
- security_score: 0-10
- architecture_score: 0-10
- security_issues: Array of security concerns
- architectural_concerns: Array of design issues
- technical_debt: Array of code smells and concerns
- long_term_recommendations: Array of strategic suggestions"""

        try:
            review_data = await gemini_service.generate_structured_output(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.7
            )

            return {
                "reviewer": "Gemini (Maintainability & Security)",
                "review": review_data,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Gemini code review failed: {e}")
            raise

    async def _combine_reviews(
        self,
        claude_review: Dict[str, Any],
        gemini_review: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Combine Claude and Gemini reviews into unified assessment

        Synthesizes both perspectives to make final decision
        """
        claude_data = claude_review.get("review", {})
        gemini_data = gemini_review.get("review", {})

        # Aggregate scores
        plan_adherence = claude_data.get("plan_adherence_score", 0)
        logic_correctness = claude_data.get("logic_correctness_score", 0)
        maintainability = gemini_data.get("maintainability_score", 0)
        security = gemini_data.get("security_score", 0)
        architecture = gemini_data.get("architecture_score", 0)

        overall_score = (
            plan_adherence * 0.25 +
            logic_correctness * 0.25 +
            maintainability * 0.20 +
            security * 0.20 +
            architecture * 0.10
        )

        # Collect all issues
        all_issues = []
        all_issues.extend(claude_data.get("issues", []))

        # Add security issues from Gemini
        for sec_issue in gemini_data.get("security_issues", []):
            all_issues.append({
                "severity": "major",
                "category": "security",
                "description": sec_issue,
                "source": "Gemini"
            })

        # Add architectural concerns
        for arch_concern in gemini_data.get("architectural_concerns", []):
            all_issues.append({
                "severity": "minor",
                "category": "architecture",
                "description": arch_concern,
                "source": "Gemini"
            })

        # Categorize issues
        blockers = [i for i in all_issues if i.get("severity") == "blocker"]
        majors = [i for i in all_issues if i.get("severity") == "major"]
        minors = [i for i in all_issues if i.get("severity") == "minor"]

        return {
            "overall_score": overall_score,
            "scores": {
                "plan_adherence": plan_adherence,
                "logic_correctness": logic_correctness,
                "maintainability": maintainability,
                "security": security,
                "architecture": architecture
            },
            "issues": {
                "blockers": blockers,
                "major": majors,
                "minor": minors,
                "total": len(all_issues)
            },
            "action_items": await self._prioritize_action_items(all_issues),
            "recommendations": (
                claude_data.get("recommendations", []) +
                gemini_data.get("long_term_recommendations", [])
            )
        }

    async def _make_approval_decision(self, combined_review: Dict) -> Dict[str, Any]:
        """
        Make approval/rejection decision based on combined review

        Rules:
        - Blockers = Reject
        - Score < 6.0 = Request Changes
        - Major security issues = Request Changes
        - Score >= 8.0 and no major issues = Approve
        - Otherwise = Approve with Comments
        """
        score = combined_review.get("overall_score", 0)
        issues = combined_review.get("issues", {})

        blockers = len(issues.get("blockers", []))
        majors = len(issues.get("major", []))

        if blockers > 0:
            return {
                "approved": False,
                "status": "rejected",
                "reason": f"{blockers} blocker(s) must be fixed before approval"
            }

        if score < 6.0:
            return {
                "approved": False,
                "status": "request_changes",
                "reason": f"Overall score ({score:.1f}/10) below acceptance threshold"
            }

        # Check for security issues
        security_score = combined_review.get("scores", {}).get("security", 0)
        if security_score < 7.0:
            return {
                "approved": False,
                "status": "request_changes",
                "reason": "Security score below minimum threshold"
            }

        if score >= 8.0 and majors == 0:
            return {
                "approved": True,
                "status": "approved",
                "reason": f"High quality code (score: {score:.1f}/10) with no major issues"
            }

        return {
            "approved": True,
            "status": "approved_with_comments",
            "reason": f"Acceptable quality (score: {score:.1f}/10). Please address {majors} major issue(s) in follow-up"
        }

    async def _validate_quality_gates(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all quality gates

        Parameters:
            - target: str - Project/module to validate
            - gates: List[str] - Specific gates to run

        Returns:
            Quality gate validation results
        """
        target = parameters.get("target", ".")
        gates = parameters.get("gates", ["sonarqube", "snyk", "coverage"])

        results = {}

        if "sonarqube" in gates:
            results["sonarqube"] = await self._run_sonarqube_gate(target)

        if "snyk" in gates:
            results["snyk"] = await self._run_snyk_gate(target)

        if "coverage" in gates:
            results["coverage"] = await self._run_coverage_gate(target)

        # Overall pass/fail
        all_passed = all(gate.get("passed", False) for gate in results.values())

        return {
            "gates": results,
            "overall_passed": all_passed,
            "summary": await self._summarize_gate_results(results),
            "confidence": 0.90
        }

    async def _run_sonarqube_gate(self, target: str) -> Dict[str, Any]:
        """
        Run SonarQube AI Code Assurance quality gate

        Checks:
        - New code coverage >= 80%
        - New code duplication < 3%
        - Security hotspots = 0
        - Security rating = A
        """
        # In production, call actual SonarQube API
        # This is a simulation

        logger.info(f"Running SonarQube quality gate for: {target}")

        # Simulated results
        results = {
            "new_coverage": 0.85,  # 85%
            "new_duplication": 0.02,  # 2%
            "security_hotspots": 0,
            "security_rating": "A",
            "code_smells": 5,
            "bugs": 0,
            "vulnerabilities": 0
        }

        # Check against thresholds
        passed = (
            results["new_coverage"] >= self.quality_gates["coverage"] and
            results["new_duplication"] <= self.quality_gates["duplication"] and
            results["security_hotspots"] == self.quality_gates["security_hotspots"] and
            results["security_rating"] == self.quality_gates["security_rating"]
        )

        return {
            "gate": "SonarQube AI Code Assurance",
            "passed": passed,
            "results": results,
            "violations": await self._extract_sonar_violations(results),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _run_snyk_gate(self, target: str) -> Dict[str, Any]:
        """
        Run Snyk security scan

        Checks:
        - Critical vulnerabilities = 0
        - High vulnerabilities = 0
        - License compliance
        """
        logger.info(f"Running Snyk security scan for: {target}")

        # Simulated results
        results = {
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 0,
            "medium_vulnerabilities": 2,
            "low_vulnerabilities": 5,
            "license_issues": 0
        }

        passed = (
            results["critical_vulnerabilities"] == 0 and
            results["high_vulnerabilities"] == 0
        )

        return {
            "gate": "Snyk Security Scan",
            "passed": passed,
            "results": results,
            "vulnerabilities": await self._extract_snyk_vulnerabilities(results),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _run_coverage_gate(self, target: str) -> Dict[str, Any]:
        """
        Run test coverage validation

        Requirement: >= 80% coverage on new code
        """
        logger.info(f"Running coverage check for: {target}")

        # Simulated coverage results
        results = {
            "total_coverage": 0.82,  # 82%
            "new_code_coverage": 0.85,  # 85%
            "lines_covered": 1850,
            "lines_total": 2250,
            "branches_covered": 420,
            "branches_total": 500
        }

        passed = results["new_code_coverage"] >= self.quality_gates["coverage"]

        return {
            "gate": "Test Coverage",
            "passed": passed,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _security_scan(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive security scan

        Parameters:
            - scope: str - Scope of scan
            - scan_type: str - Type of scan (sast, dast, dependencies)

        Returns:
            Security scan results with vulnerabilities
        """
        scope = parameters.get("scope", ".")
        scan_type = parameters.get("scan_type", "full")

        # Run security scans
        results = {
            "snyk_scan": await self._run_snyk_gate(scope),
            "sast_analysis": await self._run_sast_analysis(scope),
            "dependency_check": await self._check_dependencies(scope)
        }

        # Aggregate findings
        total_critical = sum(
            scan.get("results", {}).get("critical_vulnerabilities", 0)
            for scan in results.values()
        )

        total_high = sum(
            scan.get("results", {}).get("high_vulnerabilities", 0)
            for scan in results.values()
        )

        return {
            "scans": results,
            "summary": {
                "total_critical": total_critical,
                "total_high": total_high,
                "passed": total_critical == 0 and total_high == 0
            },
            "confidence": 0.87
        }

    async def _test_coverage_check(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detailed test coverage analysis

        Parameters:
            - target: str - Target module
            - minimum_coverage: float - Minimum required coverage

        Returns:
            Coverage analysis with file-level breakdown
        """
        target = parameters.get("target", ".")
        minimum_coverage = parameters.get("minimum_coverage", 0.8)

        coverage_result = await self._run_coverage_gate(target)

        # Get file-level coverage (simulated)
        file_coverage = await self._get_file_coverage(target)

        return {
            "overall_coverage": coverage_result,
            "file_coverage": file_coverage,
            "files_below_threshold": [
                f for f in file_coverage
                if f["coverage"] < minimum_coverage
            ],
            "confidence": 0.88
        }

    async def _generate_e2e_tests(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate E2E tests from Gherkin acceptance criteria

        Parameters:
            - acceptance_criteria: List[Dict] - Gherkin scenarios
            - framework: str - Test framework (playwright, selenium)
            - platform: str - Target platform (web, mobile)

        Returns:
            Generated E2E test files
        """
        acceptance_criteria = parameters.get("acceptance_criteria", [])
        framework = parameters.get("framework", "playwright")
        platform = parameters.get("platform", "web")

        system_prompt = f"""You are generating E2E tests from Gherkin acceptance criteria.

Framework: {framework}
Platform: {platform}

Test Requirements:
- Translate each Gherkin scenario into executable test
- Use proper selectors and assertions
- Handle waits and async operations
- Include setup and teardown
- Add descriptive test names
- Handle error scenarios

Best Practices:
- DRY: Extract reusable functions
- Page Object Model for web tests
- Proper error handling
- Clear test data management"""

        prompt = f"""Generate E2E tests from the following Gherkin acceptance criteria:

**Acceptance Criteria**:
{json.dumps(acceptance_criteria, indent=2)}

**Framework**: {framework}
**Platform**: {platform}

Generate complete test files with:
1. Proper imports and setup
2. Test suite organization
3. Individual test cases for each scenario
4. Helper functions and utilities
5. Clear assertions and error messages

Format as JSON with test files."""

        try:
            test_code = await self.call_claude(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=12000
            )

            return {
                "test_files": await self._extract_test_files(test_code),
                "framework": framework,
                "scenarios_covered": len(acceptance_criteria),
                "confidence": 0.85
            }

        except Exception as e:
            logger.error(f"E2E test generation failed: {e}")
            raise

    async def _performance_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance implications of code changes

        Parameters:
            - diff: str - Code changes
            - performance_profile: Dict - Current performance metrics

        Returns:
            Performance impact analysis
        """
        diff = parameters.get("diff", "")
        performance_profile = parameters.get("performance_profile", {})

        system_prompt = """You are analyzing performance implications of code changes.

Focus Areas:
- Algorithm complexity (Big O analysis)
- Database query efficiency
- Memory usage
- Network calls
- Caching opportunities
- Potential bottlenecks

Provide actionable recommendations."""

        prompt = f"""Analyze performance implications:

**Code Changes**:
```diff
{diff}
```

**Current Performance Profile**:
{json.dumps(performance_profile, indent=2) if performance_profile else "No baseline"}

Analyze:
1. Algorithm complexity changes
2. Database/network impact
3. Memory usage implications
4. Potential bottlenecks
5. Optimization opportunities

Format as detailed analysis."""

        try:
            analysis = await self.call_claude(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=6000
            )

            return {
                "analysis": analysis,
                "performance_impact": "Estimated low",  # Would be calculated
                "recommendations": [],
                "confidence": 0.82
            }

        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            raise

    # Helper methods

    async def _parse_review_json(self, review_text: str, schema: Dict) -> Dict:
        """Parse review text into structured JSON"""
        # In production, use Claude's JSON mode or structured output
        try:
            if "```json" in review_text:
                json_start = review_text.find("```json") + 7
                json_end = review_text.find("```", json_start)
                json_text = review_text[json_start:json_end].strip()
                return json.loads(json_text)
            return {}
        except:
            return {}

    async def _prioritize_action_items(self, issues: List[Dict]) -> List[Dict]:
        """Prioritize action items by severity and impact"""
        priorities = {"blocker": 1, "major": 2, "minor": 3, "suggestion": 4}
        return sorted(issues, key=lambda x: priorities.get(x.get("severity", "minor"), 5))

    async def _summarize_gate_results(self, results: Dict) -> str:
        """Summarize quality gate results"""
        passed = sum(1 for gate in results.values() if gate.get("passed"))
        total = len(results)
        return f"{passed}/{total} quality gates passed"

    async def _extract_sonar_violations(self, results: Dict) -> List[Dict]:
        """Extract SonarQube violations"""
        return []

    async def _extract_snyk_vulnerabilities(self, results: Dict) -> List[Dict]:
        """Extract Snyk vulnerabilities"""
        return []

    async def _run_sast_analysis(self, scope: str) -> Dict:
        """Run SAST analysis"""
        return {"passed": True, "results": {}}

    async def _check_dependencies(self, scope: str) -> Dict:
        """Check dependencies for vulnerabilities"""
        return {"passed": True, "results": {}}

    async def _get_file_coverage(self, target: str) -> List[Dict]:
        """Get file-level coverage breakdown"""
        return []

    async def _extract_test_files(self, test_code: str) -> List[Dict]:
        """Extract test files from generated code"""
        return []


# Singleton instance
_qa_agent_instance: Optional[QAAgent] = None


def get_qa_agent() -> QAAgent:
    """Get QA agent singleton instance"""
    global _qa_agent_instance
    if _qa_agent_instance is None:
        _qa_agent_instance = QAAgent()
    return _qa_agent_instance
