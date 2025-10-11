"""
AI Orchestrator - "Polyglot AI" Task Routing

Routes tasks to the most appropriate AI model based on:
- Task type (structured vs creative)
- Performance requirements (speed vs quality)
- Context size
- Cost optimization

Philosophy: Use Claude for core/secure tasks, Gemini for creative/rapid tasks
"""
from typing import Dict, Any, Optional, Literal
from enum import Enum
import logging

from agents.claude_agent import get_claude_agent
from agents.gemini_agent import get_gemini_agent
from agents.maeju_agent import get_maeju_agent

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Types of tasks that can be routed"""
    # Claude-optimized tasks
    API_DESIGN = "api_design"
    SECURITY_ANALYSIS = "security_analysis"
    DATABASE_QUERY = "database_query"
    CODE_REVIEW = "code_review"
    STRUCTURED_GENERATION = "structured_generation"

    # Gemini-optimized tasks
    VIDEO_SCRIPT = "video_script"
    RECIPE_VARIATION = "recipe_variation"
    PRODUCT_DESCRIPTION = "product_description"
    CONTENT_ATOMIZATION = "content_atomization"
    DATA_ANALYSIS = "data_analysis"
    CREATIVE_WRITING = "creative_writing"

    # Maeju (conversational)
    CHAT = "chat"
    PRODUCT_STORYTELLING = "product_storytelling"
    TASTE_ANALYSIS = "taste_analysis"


class AIOrchestrator:
    """
    Central orchestrator for multi-model AI tasks

    Implements the "polyglot AI" philosophy from the PRD
    """

    def __init__(self):
        self.claude = get_claude_agent()
        self.gemini = get_gemini_agent()
        self.maeju = get_maeju_agent()

        # Task routing configuration
        self.task_routing = {
            # Claude tasks (precision, security, structure)
            TaskType.API_DESIGN: "claude",
            TaskType.SECURITY_ANALYSIS: "claude",
            TaskType.DATABASE_QUERY: "claude",
            TaskType.CODE_REVIEW: "claude",
            TaskType.STRUCTURED_GENERATION: "claude",

            # Gemini tasks (creativity, speed, large context)
            TaskType.VIDEO_SCRIPT: "gemini",
            TaskType.RECIPE_VARIATION: "gemini",
            TaskType.PRODUCT_DESCRIPTION: "gemini",
            TaskType.CONTENT_ATOMIZATION: "gemini",
            TaskType.DATA_ANALYSIS: "gemini",
            TaskType.CREATIVE_WRITING: "gemini",

            # Maeju tasks (conversational, domain-specific)
            TaskType.CHAT: "maeju",
            TaskType.PRODUCT_STORYTELLING: "maeju",
            TaskType.TASTE_ANALYSIS: "maeju",
        }

        logger.info("AI Orchestrator initialized with Claude, Gemini, and Maeju")

    def get_optimal_agent(self, task_type: TaskType) -> Literal["claude", "gemini", "maeju"]:
        """
        Determine optimal agent for task type

        Args:
            task_type: Type of task

        Returns:
            Agent identifier
        """
        return self.task_routing.get(task_type, "claude")  # Default to Claude

    async def execute_task(
        self,
        task_type: TaskType,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute task with optimal AI agent

        Args:
            task_type: Type of task
            **kwargs: Task-specific parameters

        Returns:
            Task result with metadata about which agent was used
        """
        agent_name = self.get_optimal_agent(task_type)

        logger.info(f"Routing {task_type.value} to {agent_name}")

        try:
            # Route to appropriate agent
            if agent_name == "claude":
                result = await self._execute_claude_task(task_type, **kwargs)
            elif agent_name == "gemini":
                result = await self._execute_gemini_task(task_type, **kwargs)
            elif agent_name == "maeju":
                result = await self._execute_maeju_task(task_type, **kwargs)
            else:
                raise ValueError(f"Unknown agent: {agent_name}")

            # Add orchestration metadata
            result["orchestration"] = {
                "task_type": task_type.value,
                "routed_to": agent_name,
                "routing_reason": self._get_routing_reason(task_type, agent_name)
            }

            return result

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise

    async def _execute_claude_task(
        self,
        task_type: TaskType,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute Claude-specific tasks"""

        if task_type == TaskType.API_DESIGN:
            return await self.claude.design_api_schema(
                description=kwargs.get("description", ""),
                requirements=kwargs.get("requirements", []),
                existing_schema=kwargs.get("existing_schema")
            )

        elif task_type == TaskType.SECURITY_ANALYSIS:
            return await self.claude.analyze_security(
                code=kwargs.get("code", ""),
                context=kwargs.get("context")
            )

        elif task_type == TaskType.DATABASE_QUERY:
            return await self.claude.generate_database_query(
                intent=kwargs.get("intent", ""),
                schema=kwargs.get("schema", {}),
                query_language=kwargs.get("query_language", "cypher")
            )

        elif task_type == TaskType.CODE_REVIEW:
            return await self.claude.review_code(
                code=kwargs.get("code", ""),
                language=kwargs.get("language", "python"),
                context=kwargs.get("context")
            )

        elif task_type == TaskType.STRUCTURED_GENERATION:
            return await self.claude.generate(
                prompt=kwargs.get("prompt", ""),
                system_prompt=kwargs.get("system_prompt"),
                response_format="json"
            )

        else:
            raise ValueError(f"Unsupported Claude task: {task_type}")

    async def _execute_gemini_task(
        self,
        task_type: TaskType,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute Gemini-specific tasks"""

        if task_type == TaskType.VIDEO_SCRIPT:
            return await self.gemini.generate_video_script(
                product=kwargs.get("product", {}),
                duration_seconds=kwargs.get("duration_seconds", 60),
                target_audience=kwargs.get("target_audience", "general"),
                style=kwargs.get("style", "engaging")
            )

        elif task_type == TaskType.RECIPE_VARIATION:
            return await self.gemini.variate_recipe(
                base_recipe=kwargs.get("base_recipe", {}),
                variations_count=kwargs.get("variations_count", 3),
                dietary_restrictions=kwargs.get("dietary_restrictions")
            )

        elif task_type == TaskType.PRODUCT_DESCRIPTION:
            return await self.gemini.generate_product_descriptions(
                product=kwargs.get("product", {}),
                variants=kwargs.get("variants", ["short", "long", "seo"]),
                languages=kwargs.get("languages", ["en"])
            )

        elif task_type == TaskType.CONTENT_ATOMIZATION:
            return await self.gemini.atomize_content(
                pillar_content=kwargs.get("pillar_content", ""),
                content_type=kwargs.get("content_type", "blog_post"),
                output_formats=kwargs.get("output_formats", ["short_video", "carousel"])
            )

        elif task_type == TaskType.DATA_ANALYSIS:
            return await self.gemini.analyze_data_patterns(
                data=kwargs.get("data", {}),
                analysis_type=kwargs.get("analysis_type", "general")
            )

        elif task_type == TaskType.CREATIVE_WRITING:
            return await self.gemini.generate(
                prompt=kwargs.get("prompt", ""),
                system_instruction=kwargs.get("system_instruction"),
                temperature=kwargs.get("temperature", 0.9),
                response_format=kwargs.get("response_format", "text")
            )

        else:
            raise ValueError(f"Unsupported Gemini task: {task_type}")

    async def _execute_maeju_task(
        self,
        task_type: TaskType,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute Maeju-specific tasks"""

        if task_type == TaskType.CHAT:
            return await self.maeju.chat(
                user_message=kwargs.get("user_message", ""),
                user_id=kwargs.get("user_id", ""),
                conversation_history=kwargs.get("conversation_history"),
                user_context=kwargs.get("user_context"),
                available_products=kwargs.get("available_products")
            )

        elif task_type == TaskType.PRODUCT_STORYTELLING:
            story = self.maeju.generate_product_story(
                product=kwargs.get("product", {}),
                style=kwargs.get("style", "engaging")
            )
            return {"content": story}

        elif task_type == TaskType.TASTE_ANALYSIS:
            preferences = self.maeju.analyze_taste_preferences(
                user_input=kwargs.get("user_input", "")
            )
            return {"content": preferences}

        else:
            raise ValueError(f"Unsupported Maeju task: {task_type}")

    def _get_routing_reason(self, task_type: TaskType, agent: str) -> str:
        """Get human-readable reason for routing decision"""
        reasons = {
            ("claude", TaskType.API_DESIGN): "Claude excels at structured, secure API design",
            ("claude", TaskType.SECURITY_ANALYSIS): "Claude's strong vulnerability detection",
            ("claude", TaskType.DATABASE_QUERY): "Claude's precise query generation",
            ("claude", TaskType.CODE_REVIEW): "Claude's thorough code review capabilities",
            ("gemini", TaskType.VIDEO_SCRIPT): "Gemini's creative content generation",
            ("gemini", TaskType.RECIPE_VARIATION): "Gemini's creative variations",
            ("gemini", TaskType.PRODUCT_DESCRIPTION): "Gemini's fast, creative writing",
            ("gemini", TaskType.CONTENT_ATOMIZATION): "Gemini's large context window",
            ("gemini", TaskType.DATA_ANALYSIS): "Gemini's ability to process large datasets",
            ("maeju", TaskType.CHAT): "Maeju's domain-specific conversational abilities",
            ("maeju", TaskType.PRODUCT_STORYTELLING): "Maeju's storytelling expertise",
        }

        return reasons.get((agent, task_type), f"{agent} is optimal for this task")

    async def execute_with_fallback(
        self,
        task_type: TaskType,
        fallback_agent: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute task with fallback to another agent if primary fails

        Args:
            task_type: Type of task
            fallback_agent: Agent to try if primary fails
            **kwargs: Task parameters

        Returns:
            Task result
        """
        try:
            return await self.execute_task(task_type, **kwargs)
        except Exception as primary_error:
            if fallback_agent:
                logger.warning(f"Primary agent failed, trying fallback {fallback_agent}: {primary_error}")

                try:
                    # Override routing temporarily
                    original_routing = self.task_routing[task_type]
                    self.task_routing[task_type] = fallback_agent

                    result = await self.execute_task(task_type, **kwargs)

                    # Restore original routing
                    self.task_routing[task_type] = original_routing

                    result["orchestration"]["fallback_used"] = True
                    result["orchestration"]["primary_error"] = str(primary_error)

                    return result

                except Exception as fallback_error:
                    logger.error(f"Fallback agent also failed: {fallback_error}")
                    raise

            raise


# Singleton instance
_orchestrator: Optional[AIOrchestrator] = None


def get_orchestrator() -> AIOrchestrator:
    """Get AI orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator()
    return _orchestrator
