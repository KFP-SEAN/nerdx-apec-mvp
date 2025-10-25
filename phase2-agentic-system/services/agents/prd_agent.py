"""
PRD Agent (Product Requirements Document Agent)
Gemini 2.0 Flash Thinking-based strategic planner and requirements engineer

Transforms vague ideas into concrete, actionable PRDs with user stories and acceptance criteria.
"""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.agents.base_agent import BaseAgent, AgentCapability, AgentResponse
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class PRDAgent(BaseAgent):
    """
    PRD Agent: Requirements Engineering & Strategic Planning

    Powered by Gemini 2.0 Flash Thinking (1M+ token context)

    Core Capabilities:
    - PRD generation from natural language
    - Requirements refinement and clarification
    - User story creation (As a... I want... So that...)
    - Acceptance criteria generation (Gherkin format)
    - Multimodal requirement analysis (text + diagrams)
    """

    def __init__(self, agent_id: str = "prd-agent-001", world_model_url: Optional[str] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="prd_agent",
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.GENERATION,
                AgentCapability.COORDINATION
            ],
            world_model_url=world_model_url
        )

    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        parameters: Dict[str, Any]
    ) -> AgentResponse:
        """
        Execute PRD agent task

        Supported task types:
        - generate_prd: Create PRD from idea
        - refine_prd: Enhance existing PRD
        - create_user_stories: Generate user stories
        - generate_acceptance_criteria: Create Gherkin scenarios
        - analyze_requirements: Multimodal analysis
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"PRD Agent executing task: {task_type}")

            if task_type == "generate_prd":
                result = await self._generate_prd(parameters)
            elif task_type == "refine_prd":
                result = await self._refine_prd(parameters)
            elif task_type == "create_user_stories":
                result = await self._create_user_stories(parameters)
            elif task_type == "generate_acceptance_criteria":
                result = await self._generate_acceptance_criteria(parameters)
            elif task_type == "analyze_requirements":
                result = await self._analyze_requirements(parameters)
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
            logger.error(f"PRD Agent task failed: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return self.create_response(
                task_id=task_id,
                status="failed",
                confidence=0.0,
                result={},
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )

    async def _generate_prd(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive PRD from natural language idea

        Parameters:
            - title: str - Feature/product title
            - description: str - Natural language description
            - requirements: List[str] - Initial requirements (optional)
            - context: str - Additional context (optional)
            - target_audience: str - Target users (optional)

        Returns:
            Complete PRD with sections: overview, objectives, user stories,
            acceptance criteria, technical requirements, success metrics
        """
        title = parameters.get("title", "")
        description = parameters.get("description", "")
        requirements = parameters.get("requirements", [])
        context = parameters.get("context", "")
        target_audience = parameters.get("target_audience", "End users")

        system_instruction = """You are an expert product requirements engineer and strategic planner.

Your role:
- Transform vague ideas into concrete, actionable Product Requirements Documents (PRDs)
- Apply SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
- Generate clear user stories and acceptance criteria
- Consider technical feasibility and constraints
- Focus on user value and business impact

Format:
- Use clear, professional language
- Be specific and avoid ambiguity
- Include measurable success metrics
- Follow industry best practices"""

        prompt = f"""Generate a comprehensive Product Requirements Document (PRD) for the following feature/product:

**Title**: {title}

**Description**: {description}

**Initial Requirements**:
{chr(10).join(f"- {req}" for req in requirements) if requirements else "None provided"}

**Context**: {context if context else "General use case"}

**Target Audience**: {target_audience}

Generate a complete PRD with the following sections:

1. **Executive Summary** (2-3 sentences)
2. **Problem Statement** (What problem are we solving?)
3. **Objectives & Goals** (SMART objectives)
4. **Target Users** (User personas and characteristics)
5. **User Stories** (At least 3 user stories in format: "As a [user], I want [feature], so that [benefit]")
6. **Functional Requirements** (Detailed feature requirements)
7. **Non-Functional Requirements** (Performance, security, scalability)
8. **Acceptance Criteria** (Gherkin scenarios for each user story)
9. **Technical Considerations** (Architecture, dependencies, constraints)
10. **Success Metrics** (KPIs to measure success)
11. **Timeline Estimate** (Development phases)
12. **Risks & Mitigation** (Potential challenges)

Format as JSON with these keys: executive_summary, problem_statement, objectives, target_users, user_stories, functional_requirements, non_functional_requirements, acceptance_criteria, technical_considerations, success_metrics, timeline, risks"""

        try:
            schema = {
                "executive_summary": "string",
                "problem_statement": "string",
                "objectives": ["string"],
                "target_users": ["string"],
                "user_stories": [
                    {
                        "id": "string",
                        "user": "string",
                        "action": "string",
                        "benefit": "string",
                        "priority": "string"
                    }
                ],
                "functional_requirements": ["string"],
                "non_functional_requirements": {
                    "performance": ["string"],
                    "security": ["string"],
                    "scalability": ["string"]
                },
                "acceptance_criteria": [
                    {
                        "user_story_id": "string",
                        "scenarios": [
                            {
                                "given": "string",
                                "when": "string",
                                "then": "string"
                            }
                        ]
                    }
                ],
                "technical_considerations": {
                    "architecture": "string",
                    "dependencies": ["string"],
                    "constraints": ["string"]
                },
                "success_metrics": [
                    {
                        "metric": "string",
                        "target": "string",
                        "measurement": "string"
                    }
                ],
                "timeline": {
                    "planning": "string",
                    "development": "string",
                    "testing": "string",
                    "deployment": "string"
                },
                "risks": [
                    {
                        "risk": "string",
                        "impact": "string",
                        "mitigation": "string"
                    }
                ]
            }

            prd_data = await gemini_service.generate_structured_output(
                prompt=prompt,
                system_instruction=system_instruction,
                schema=schema,
                temperature=0.8
            )

            return {
                "prd": prd_data,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "agent_id": self.agent_id,
                    "model": "gemini-2.5-pro"  # Using Gemini 2.5 Pro
                },
                "confidence": 0.88
            }

        except Exception as e:
            logger.error(f"PRD generation failed: {e}")
            raise

    async def _refine_prd(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine existing PRD based on feedback

        Parameters:
            - prd_content: Dict - Existing PRD
            - feedback: str - Refinement feedback
            - refinement_goals: List[str] - Specific goals for refinement

        Returns:
            Refined PRD
        """
        prd_content = parameters.get("prd_content", {})
        feedback = parameters.get("feedback", "")
        refinement_goals = parameters.get("refinement_goals", [])

        system_instruction = """You are refining an existing PRD based on stakeholder feedback.

Your role:
- Incorporate feedback while maintaining PRD structure
- Clarify ambiguous sections
- Add missing details
- Improve specificity and measurability
- Maintain consistency across sections"""

        prompt = f"""Refine the following PRD based on the feedback provided:

**Current PRD**:
{json.dumps(prd_content, indent=2)}

**Feedback**:
{feedback}

**Refinement Goals**:
{chr(10).join(f"- {goal}" for goal in refinement_goals) if refinement_goals else "General improvements"}

Provide the refined PRD maintaining the same JSON structure. Focus on:
1. Addressing the feedback points
2. Improving clarity and specificity
3. Ensuring consistency across sections
4. Enhancing acceptance criteria
5. Updating technical considerations if needed"""

        try:
            refined_prd = await gemini_service.generate_structured_output(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.7
            )

            return {
                "refined_prd": refined_prd,
                "refinement_summary": "PRD refined based on feedback",
                "confidence": 0.85
            }

        except Exception as e:
            logger.error(f"PRD refinement failed: {e}")
            raise

    async def _create_user_stories(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate user stories from requirements

        Parameters:
            - prd_content: Dict - PRD or requirements
            - max_stories: int - Maximum number of stories (default: 10)
            - focus_areas: List[str] - Specific areas to focus on

        Returns:
            User stories in standard format
        """
        prd_content = parameters.get("prd_content", {})
        max_stories = parameters.get("max_stories", 10)
        focus_areas = parameters.get("focus_areas", [])

        system_instruction = """You are generating user stories following industry best practices.

User Story Format:
"As a [user type], I want [action/feature], so that [benefit/value]"

Guidelines:
- Focus on user value, not implementation
- Keep stories small and testable
- Use clear, non-technical language
- Prioritize by business value and user impact
- Include acceptance criteria"""

        prompt = f"""Generate user stories based on the following requirements:

**Requirements/PRD**:
{json.dumps(prd_content, indent=2)}

**Focus Areas**:
{chr(10).join(f"- {area}" for area in focus_areas) if focus_areas else "All areas"}

**Maximum Stories**: {max_stories}

Generate user stories with:
1. Clear user persona
2. Specific action or feature
3. Business value or benefit
4. Priority (Critical, High, Medium, Low)
5. Story points estimate (1, 2, 3, 5, 8, 13)
6. Basic acceptance criteria (bullet points)

Format as JSON array of user stories."""

        try:
            schema = {
                "user_stories": [
                    {
                        "id": "string",
                        "title": "string",
                        "as_a": "string",
                        "i_want": "string",
                        "so_that": "string",
                        "priority": "string",
                        "story_points": "number",
                        "acceptance_criteria": ["string"],
                        "notes": "string"
                    }
                ]
            }

            stories_data = await gemini_service.generate_structured_output(
                prompt=prompt,
                system_instruction=system_instruction,
                schema=schema,
                temperature=0.8
            )

            return {
                "user_stories": stories_data.get("user_stories", []),
                "total_stories": len(stories_data.get("user_stories", [])),
                "confidence": 0.87
            }

        except Exception as e:
            logger.error(f"User story generation failed: {e}")
            raise

    async def _generate_acceptance_criteria(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Gherkin-format acceptance criteria

        Parameters:
            - user_stories: List[Dict] - User stories
            - detailed: bool - Generate detailed scenarios (default: True)

        Returns:
            Gherkin scenarios for each user story
        """
        user_stories = parameters.get("user_stories", [])
        detailed = parameters.get("detailed", True)

        system_instruction = """You are generating acceptance criteria in Gherkin (BDD) format.

Gherkin Format:
Given [initial context/state]
When [action/event]
Then [expected outcome]
And [additional outcomes] (optional)

Guidelines:
- Be specific and testable
- Cover happy path and edge cases
- Use concrete examples
- Avoid technical implementation details
- Focus on observable behavior"""

        prompt = f"""Generate Gherkin acceptance criteria for the following user stories:

**User Stories**:
{json.dumps(user_stories, indent=2)}

**Detail Level**: {"Detailed with edge cases" if detailed else "Basic scenarios only"}

For each user story, generate:
1. Happy path scenario
2. Alternative paths (if applicable)
3. Edge cases and error conditions
4. Data validation scenarios

Format as JSON with Gherkin scenarios."""

        try:
            schema = {
                "acceptance_criteria": [
                    {
                        "user_story_id": "string",
                        "user_story_title": "string",
                        "scenarios": [
                            {
                                "scenario_name": "string",
                                "type": "string",
                                "given": ["string"],
                                "when": ["string"],
                                "then": ["string"],
                                "and": ["string"]
                            }
                        ]
                    }
                ]
            }

            criteria_data = await gemini_service.generate_structured_output(
                prompt=prompt,
                system_instruction=system_instruction,
                schema=schema,
                temperature=0.7
            )

            return {
                "acceptance_criteria": criteria_data.get("acceptance_criteria", []),
                "total_scenarios": sum(
                    len(ac.get("scenarios", []))
                    for ac in criteria_data.get("acceptance_criteria", [])
                ),
                "confidence": 0.86
            }

        except Exception as e:
            logger.error(f"Acceptance criteria generation failed: {e}")
            raise

    async def _analyze_requirements(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multimodal requirements analysis (text + diagrams/screenshots)

        Parameters:
            - description: str - Text description
            - images: List[str] - Base64 encoded images or URLs
            - analysis_type: str - Type of analysis (functional, technical, user_experience)

        Returns:
            Analyzed requirements with insights
        """
        description = parameters.get("description", "")
        images = parameters.get("images", [])
        analysis_type = parameters.get("analysis_type", "functional")

        system_instruction = f"""You are analyzing requirements using multimodal inputs (text + images).

Analysis Type: {analysis_type}

Your role:
- Extract requirements from diagrams, wireframes, and screenshots
- Identify implicit requirements not explicitly stated
- Highlight potential issues or ambiguities
- Suggest improvements based on best practices"""

        prompt = f"""Analyze the following requirements:

**Text Description**:
{description}

**Visual Inputs**: {len(images)} image(s) provided

**Analysis Focus**: {analysis_type}

Provide:
1. Extracted functional requirements
2. Non-functional requirements identified
3. User experience insights
4. Technical considerations
5. Potential issues or gaps
6. Recommendations

Format as detailed JSON analysis."""

        try:
            if images:
                # Multimodal analysis
                analysis_text = await gemini_service.analyze_multimodal(
                    prompt=prompt,
                    images=images,
                    system_instruction=system_instruction,
                    temperature=0.7
                )
            else:
                # Text-only analysis
                analysis_text = await gemini_service.generate_content(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=0.7
                )

            # Parse structured analysis
            schema = {
                "functional_requirements": ["string"],
                "non_functional_requirements": ["string"],
                "user_experience_insights": ["string"],
                "technical_considerations": ["string"],
                "potential_issues": ["string"],
                "recommendations": ["string"]
            }

            # Request structured output
            structured_analysis = await gemini_service.generate_structured_output(
                prompt=f"Convert the following analysis into structured JSON:\n\n{analysis_text}",
                schema=schema,
                temperature=0.5
            )

            return {
                "analysis": structured_analysis,
                "raw_analysis": analysis_text,
                "multimodal": len(images) > 0,
                "confidence": 0.84
            }

        except Exception as e:
            logger.error(f"Requirements analysis failed: {e}")
            raise


# Singleton instance
_prd_agent_instance: Optional[PRDAgent] = None


def get_prd_agent() -> PRDAgent:
    """Get PRD agent singleton instance"""
    global _prd_agent_instance
    if _prd_agent_instance is None:
        _prd_agent_instance = PRDAgent()
    return _prd_agent_instance
