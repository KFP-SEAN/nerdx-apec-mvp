"""
Helios Task Models

Task scheduling and dependency management models for Helios orchestration.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from enum import Enum

from models.helios.usage_models import ModelType


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"           # Waiting to be scheduled
    QUEUED = "queued"             # In execution queue
    RUNNING = "running"           # Currently executing
    COMPLETED = "completed"       # Successfully completed
    FAILED = "failed"             # Failed with error
    CANCELLED = "cancelled"       # Manually cancelled
    BLOCKED = "blocked"           # Blocked by dependencies


class TaskPriority(str, Enum):
    """Task priority levels"""
    CRITICAL = "critical"   # Priority 9-10
    HIGH = "high"          # Priority 7-8
    MEDIUM = "medium"      # Priority 5-6
    LOW = "low"            # Priority 3-4
    MINIMAL = "minimal"    # Priority 1-2


class Task(BaseModel):
    """
    Represents a single task in the Helios orchestration system
    """
    task_id: str = Field(..., description="Unique task identifier")
    project_id: str = Field(..., description="Project this task belongs to")

    # Task metadata
    name: str = Field(..., description="Human-readable task name")
    description: Optional[str] = Field(default=None, description="Task description")
    agent_type: str = Field(..., description="Type of agent to execute this task")

    # Execution parameters
    preferred_model: ModelType = Field(default=ModelType.SONNET)
    requires_opus: bool = Field(default=False, description="Whether Opus is mandatory")
    estimated_messages: int = Field(default=1, ge=1)
    estimated_tokens: int = Field(default=0, ge=0)

    # Priority and scheduling
    priority: int = Field(default=5, ge=1, le=10)
    priority_level: TaskPriority = Field(default=TaskPriority.MEDIUM)
    deadline: Optional[datetime] = Field(default=None, description="Task deadline")

    # Dependencies
    depends_on: List[str] = Field(default_factory=list, description="Task IDs this depends on")
    blocks: List[str] = Field(default_factory=list, description="Task IDs this blocks")

    # Status tracking
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Execution details
    allocated_model: Optional[ModelType] = None
    actual_messages: int = Field(default=0)
    actual_tokens: int = Field(default=0)

    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # Retry logic
    max_retries: int = Field(default=3, ge=0)
    retry_count: int = Field(default=0, ge=0)

    def can_execute(self, completed_tasks: Set[str]) -> bool:
        """
        Check if task can be executed based on dependencies

        Args:
            completed_tasks: Set of completed task IDs

        Returns:
            True if all dependencies are satisfied
        """
        if self.status != TaskStatus.PENDING:
            return False

        # Check if all dependencies are completed
        for dep_id in self.depends_on:
            if dep_id not in completed_tasks:
                return False

        return True

    def calculate_priority_score(self) -> float:
        """
        Calculate dynamic priority score considering deadline

        Returns:
            Priority score (higher = more urgent)
        """
        base_score = float(self.priority)

        # Deadline urgency bonus
        if self.deadline:
            time_until_deadline = (self.deadline - datetime.utcnow()).total_seconds()
            hours_remaining = time_until_deadline / 3600

            if hours_remaining < 1:
                base_score += 5.0  # Very urgent
            elif hours_remaining < 6:
                base_score += 3.0  # Urgent
            elif hours_remaining < 24:
                base_score += 1.5  # Moderately urgent
            elif hours_remaining < 48:
                base_score += 0.5  # Slightly urgent

        # Retry penalty (lower priority for retried tasks)
        if self.retry_count > 0:
            base_score -= self.retry_count * 0.5

        return max(1.0, base_score)


class TaskDAG(BaseModel):
    """
    Directed Acyclic Graph of tasks representing project workflow
    """
    project_id: str
    tasks: Dict[str, Task] = Field(default_factory=dict)

    # Execution tracking
    completed_tasks: Set[str] = Field(default_factory=set)
    failed_tasks: Set[str] = Field(default_factory=set)
    running_tasks: Set[str] = Field(default_factory=set)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    def add_task(self, task: Task):
        """Add a task to the DAG"""
        self.tasks[task.task_id] = task

        # Update blocks relationships
        for dep_id in task.depends_on:
            if dep_id in self.tasks:
                if task.task_id not in self.tasks[dep_id].blocks:
                    self.tasks[dep_id].blocks.append(task.task_id)

    def get_ready_tasks(self) -> List[Task]:
        """
        Get all tasks ready for execution

        Returns:
            List of tasks that can be executed now
        """
        ready = []

        for task in self.tasks.values():
            if task.can_execute(self.completed_tasks):
                ready.append(task)

        # Sort by priority score (descending)
        ready.sort(key=lambda t: t.calculate_priority_score(), reverse=True)

        return ready

    def mark_completed(self, task_id: str):
        """Mark a task as completed"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.tasks[task_id].completed_at = datetime.utcnow()
            self.completed_tasks.add(task_id)

            if task_id in self.running_tasks:
                self.running_tasks.remove(task_id)

    def mark_failed(self, task_id: str, error: str):
        """Mark a task as failed"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.FAILED
            self.tasks[task_id].error = error
            self.tasks[task_id].completed_at = datetime.utcnow()
            self.failed_tasks.add(task_id)

            if task_id in self.running_tasks:
                self.running_tasks.remove(task_id)

    def mark_running(self, task_id: str):
        """Mark a task as running"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.RUNNING
            self.tasks[task_id].started_at = datetime.utcnow()
            self.running_tasks.add(task_id)

    def get_blocked_tasks(self) -> List[Task]:
        """Get tasks blocked by failed dependencies"""
        blocked = []

        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                # Check if any dependency failed
                for dep_id in task.depends_on:
                    if dep_id in self.failed_tasks:
                        task.status = TaskStatus.BLOCKED
                        blocked.append(task)
                        break

        return blocked

    def is_complete(self) -> bool:
        """Check if all tasks are completed or failed"""
        for task in self.tasks.values():
            if task.status in [TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.RUNNING]:
                return False
        return True

    def get_completion_stats(self) -> Dict[str, Any]:
        """Get completion statistics"""
        total = len(self.tasks)
        completed = len(self.completed_tasks)
        failed = len(self.failed_tasks)
        running = len(self.running_tasks)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        blocked = sum(1 for t in self.tasks.values() if t.status == TaskStatus.BLOCKED)

        return {
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending,
            "blocked": blocked,
            "completion_rate": completed / total if total > 0 else 0,
            "success_rate": completed / (completed + failed) if (completed + failed) > 0 else 0
        }


class ScheduleRequest(BaseModel):
    """Request to schedule a task or project"""
    project_id: str
    tasks: List[Task]
    max_parallel: int = Field(default=10, ge=1, le=50, description="Max parallel task execution")
    budget_aware: bool = Field(default=True, description="Whether to consider budget constraints")


class ScheduleResponse(BaseModel):
    """Response from task scheduling"""
    project_id: str
    scheduled_tasks: int
    execution_order: List[List[str]]  # List of parallel execution batches
    estimated_duration_minutes: float
    estimated_cost_units: float
    message: str
