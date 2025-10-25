"""
Base Agent Class
All specialized agents inherit from this base class
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
import httpx

logger = logging.getLogger(__name__)


class AgentCapability(str, Enum):
    """Agent capabilities"""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    OPTIMIZATION = "optimization"
    PREDICTION = "prediction"
    COORDINATION = "coordination"


class AgentResponse(BaseModel):
    """Standard agent response format"""
    agent_id: str
    agent_type: str
    task_id: str
    status: str  # success, failed, partial
    confidence: float  # 0.0 to 1.0
    result: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    created_at: datetime = datetime.utcnow()
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None


class BaseAgent:
    """
    Base class for all specialized agents

    Provides common functionality:
    - AI model integration
    - Logging & monitoring
    - Error handling
    - Response standardization
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: List[AgentCapability],
        world_model_url: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.world_model_url = world_model_url or "http://localhost:8000"

        # HTTP client for API calls
        self.http_client = httpx.AsyncClient(timeout=30.0)

        logger.info(f"Initialized {agent_type} agent: {agent_id}")

    async def initialize(self):
        """Initialize agent (override in subclasses)"""
        pass

    async def close(self):
        """Cleanup resources"""
        await self.http_client.aclose()

    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        parameters: Dict[str, Any]
    ) -> AgentResponse:
        """
        Execute a task (override in subclasses)

        Args:
            task_id: Unique task identifier
            task_type: Type of task to execute
            parameters: Task-specific parameters

        Returns:
            AgentResponse with results
        """
        raise NotImplementedError("Subclasses must implement execute_task")

    async def call_world_model(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call Phase 1 World Model API

        Args:
            endpoint: API endpoint (e.g., "/api/v1/analytics/trends")
            method: HTTP method
            data: Request payload (for POST/PUT)

        Returns:
            API response data
        """
        try:
            url = f"{self.world_model_url}{endpoint}"

            if method == "GET":
                response = await self.http_client.get(url)
            elif method == "POST":
                response = await self.http_client.post(url, json=data)
            elif method == "PUT":
                response = await self.http_client.put(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"World Model API error: {e}")
            raise

    async def call_claude(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> str:
        """
        Call Claude API for structured analysis

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Max response tokens

        Returns:
            Claude's response text
        """
        try:
            # Use World Model's Claude agent
            response = await self.call_world_model(
                "/api/v1/ai/claude",
                method="POST",
                data={
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "max_tokens": max_tokens
                }
            )
            return response.get("text", "")

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    async def call_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 8192
    ) -> str:
        """
        Call Gemini API for creative generation

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Max response tokens

        Returns:
            Gemini's response text
        """
        try:
            # Use World Model's Gemini agent
            response = await self.call_world_model(
                "/api/v1/ai/gemini",
                method="POST",
                data={
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "max_tokens": max_tokens
                }
            )
            return response.get("text", "")

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def create_response(
        self,
        task_id: str,
        status: str,
        confidence: float,
        result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        processing_time_ms: Optional[int] = None
    ) -> AgentResponse:
        """
        Create standardized agent response

        Args:
            task_id: Task identifier
            status: Task status (success/failed/partial)
            confidence: Confidence score (0.0-1.0)
            result: Task results
            metadata: Additional metadata
            error_message: Error message (if failed)
            processing_time_ms: Processing duration

        Returns:
            AgentResponse object
        """
        return AgentResponse(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            task_id=task_id,
            status=status,
            confidence=confidence,
            result=result,
            metadata=metadata or {},
            error_message=error_message,
            processing_time_ms=processing_time_ms
        )

    def validate_capability(self, required_capability: AgentCapability):
        """
        Validate that agent has required capability

        Args:
            required_capability: Required capability

        Raises:
            ValueError if capability not supported
        """
        if required_capability not in self.capabilities:
            raise ValueError(
                f"{self.agent_type} does not support {required_capability}"
            )
