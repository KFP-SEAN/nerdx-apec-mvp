"""
Base Agent - 모든 에이전트의 추상 기반 클래스
FIPA-ACL 표준 및 공유 온톨로지 기반
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class AgentMessageType(str, Enum):
    """FIPA-ACL 메시지 타입"""
    REQUEST = "request"           # 작업 요청
    INFORM = "inform"             # 정보 전달
    PROPOSE = "propose"           # 제안
    ACCEPT = "accept"             # 수락
    REJECT = "reject"             # 거절
    QUERY = "query"               # 질의
    CONFIRM = "confirm"           # 확인
    FAILURE = "failure"           # 실패 알림


class AgentMessage(BaseModel):
    """에이전트 간 메시지 (FIPA-ACL 표준)"""
    message_type: AgentMessageType
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    conversation_id: Optional[str] = None
    reply_to: Optional[str] = None


class AgentState(str, Enum):
    """에이전트 상태"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


class BaseAgent(ABC):
    """
    Base Agent for Multi-Agent System (MAS)

    모든 에이전트는 이 클래스를 상속받아 구현합니다.
    FIPA-ACL 표준 통신 프로토콜과 공유 온톨로지를 사용합니다.
    """

    def __init__(self, agent_id: str, agent_type: str):
        """
        Args:
            agent_id: 에이전트 고유 식별자
            agent_type: 에이전트 타입 (예: "MarketIntelAgent")
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state = AgentState.IDLE
        self.message_queue: List[AgentMessage] = []
        self.knowledge_base: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()

        logger.info(f"[{self.agent_id}] Agent initialized: {self.agent_type}")

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        핵심 작업 실행 메서드 (각 에이전트가 구현)

        Args:
            task: 작업 명세 딕셔너리
                {
                    "task_id": str,
                    "task_type": str,
                    "parameters": Dict[str, Any],
                    "deadline": datetime (optional)
                }

        Returns:
            작업 결과 딕셔너리
                {
                    "task_id": str,
                    "status": "success" | "failure",
                    "result": Any,
                    "error": Optional[str],
                    "execution_time": float
                }
        """
        pass

    async def send_message(
        self,
        receiver: str,
        message_type: AgentMessageType,
        content: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> AgentMessage:
        """
        다른 에이전트에게 메시지 발송 (FIPA-ACL)

        Args:
            receiver: 수신자 에이전트 ID
            message_type: 메시지 타입 (REQUEST, INFORM 등)
            content: 메시지 내용
            conversation_id: 대화 스레드 ID (선택)

        Returns:
            발송한 메시지 객체
        """
        message = AgentMessage(
            message_type=message_type,
            sender=self.agent_id,
            receiver=receiver,
            content=content,
            conversation_id=conversation_id
        )

        logger.info(
            f"[{self.agent_id}] Sending {message_type} to {receiver}: "
            f"{content.get('task_type', 'unknown')}"
        )

        # 실제 구현에서는 메시지 브로커 (Redis Pub/Sub, RabbitMQ 등)를 사용
        # 여기서는 간단히 로깅만 수행

        return message

    async def receive_message(self, message: AgentMessage) -> None:
        """
        메시지 수신 및 큐에 추가

        Args:
            message: 수신한 메시지
        """
        self.message_queue.append(message)
        logger.info(
            f"[{self.agent_id}] Received {message.message_type} from {message.sender}"
        )

    async def process_message_queue(self) -> None:
        """메시지 큐 처리 (비동기)"""
        while self.message_queue:
            message = self.message_queue.pop(0)
            await self._handle_message(message)

    async def _handle_message(self, message: AgentMessage) -> None:
        """개별 메시지 처리"""
        if message.message_type == AgentMessageType.REQUEST:
            # 작업 요청 처리
            task = message.content
            try:
                result = await self.execute_task(task)
                # 결과를 INFORM 메시지로 회신
                await self.send_message(
                    receiver=message.sender,
                    message_type=AgentMessageType.INFORM,
                    content={"result": result},
                    conversation_id=message.conversation_id
                )
            except Exception as e:
                # 실패를 FAILURE 메시지로 회신
                await self.send_message(
                    receiver=message.sender,
                    message_type=AgentMessageType.FAILURE,
                    content={"error": str(e)},
                    conversation_id=message.conversation_id
                )

        elif message.message_type == AgentMessageType.QUERY:
            # 질의 처리
            query = message.content.get("query")
            response = await self._handle_query(query)
            await self.send_message(
                receiver=message.sender,
                message_type=AgentMessageType.INFORM,
                content={"response": response},
                conversation_id=message.conversation_id
            )

    async def _handle_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        질의 처리 (각 에이전트가 오버라이드 가능)

        Args:
            query: 질의 내용

        Returns:
            질의 응답
        """
        return {"status": "not_implemented"}

    def update_state(self, new_state: AgentState) -> None:
        """에이전트 상태 업데이트"""
        old_state = self.state
        self.state = new_state
        logger.info(f"[{self.agent_id}] State changed: {old_state} -> {new_state}")

    def add_to_knowledge_base(self, key: str, value: Any) -> None:
        """지식 베이스에 정보 추가"""
        self.knowledge_base[key] = value
        logger.debug(f"[{self.agent_id}] Knowledge base updated: {key}")

    def get_from_knowledge_base(self, key: str) -> Optional[Any]:
        """지식 베이스에서 정보 조회"""
        return self.knowledge_base.get(key)

    def get_status(self) -> Dict[str, Any]:
        """에이전트 상태 정보 반환"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state.value,
            "message_queue_size": len(self.message_queue),
            "knowledge_base_size": len(self.knowledge_base),
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds()
        }

    async def shutdown(self) -> None:
        """에이전트 종료 (리소스 정리)"""
        logger.info(f"[{self.agent_id}] Shutting down...")
        self.update_state(AgentState.IDLE)
        self.message_queue.clear()
