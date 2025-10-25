"""
Helios Hybrid Scheduler

Budget-aware task scheduling with parallel execution support.

Key Features:
- DAG-based dependency management
- Priority-based task scheduling
- Budget-aware execution planning
- Parallel task execution (up to 10+ simultaneous)
- Dynamic rescheduling based on failures
- Deadline-aware prioritization
"""

import logging
import asyncio
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from collections import deque

from models.helios.task_models import (
    Task,
    TaskDAG,
    TaskStatus,
    TaskPriority,
    ScheduleRequest,
    ScheduleResponse
)
from models.helios.usage_models import TaskResourceRequest, ResourceAllocation
from services.orchestrator.resource_governor import ResourceGovernor

logger = logging.getLogger(__name__)


class HybridScheduler:
    """
    Hybrid task scheduler with budget awareness

    Scheduling Strategy:
    1. Topological sort based on dependencies
    2. Priority-based ordering within each level
    3. Budget-aware execution gating
    4. Parallel execution up to max_parallel limit
    5. Dynamic rescheduling on failures
    """

    def __init__(self, resource_governor: ResourceGovernor, max_parallel: int = 10):
        """
        Initialize Hybrid Scheduler

        Args:
            resource_governor: Resource Governor for budget management
            max_parallel: Maximum parallel task execution
        """
        self.resource_governor = resource_governor
        self.max_parallel = max_parallel

        # Active DAGs (project_id -> TaskDAG)
        self.active_dags: Dict[str, TaskDAG] = {}

        # Execution tracking
        self.running_tasks: Dict[str, Task] = {}  # task_id -> Task
        self.execution_semaphore = asyncio.Semaphore(max_parallel)

        logger.info(f"Hybrid Scheduler initialized (max_parallel={max_parallel})")

    async def schedule_project(self, request: ScheduleRequest) -> ScheduleResponse:
        """
        Schedule a project's tasks

        Args:
            request: Schedule request with tasks and constraints

        Returns:
            ScheduleResponse with execution plan
        """
        logger.info(f"Scheduling project {request.project_id} with {len(request.tasks)} tasks")

        # Create DAG
        dag = TaskDAG(project_id=request.project_id)
        for task in request.tasks:
            dag.add_task(task)

        # Validate DAG (no cycles)
        if not self._validate_dag(dag):
            raise ValueError("Task DAG contains cycles")

        # Store DAG
        self.active_dags[request.project_id] = dag

        # Compute execution plan
        execution_order = self._compute_execution_order(dag)

        # Estimate duration and cost
        estimated_duration, estimated_cost = self._estimate_execution(dag, execution_order)

        logger.info(f"Project {request.project_id} scheduled: "
                   f"{len(execution_order)} execution batches, "
                   f"~{estimated_duration:.1f} min, "
                   f"~{estimated_cost:.1f} cost units")

        return ScheduleResponse(
            project_id=request.project_id,
            scheduled_tasks=len(request.tasks),
            execution_order=execution_order,
            estimated_duration_minutes=estimated_duration,
            estimated_cost_units=estimated_cost,
            message=f"Project scheduled with {len(execution_order)} execution batches"
        )

    async def execute_project(self, project_id: str) -> Dict[str, any]:
        """
        Execute a scheduled project

        Args:
            project_id: Project to execute

        Returns:
            Execution statistics
        """
        if project_id not in self.active_dags:
            raise ValueError(f"Project {project_id} not scheduled")

        dag = self.active_dags[project_id]
        logger.info(f"Starting execution of project {project_id}")

        start_time = datetime.utcnow()
        tasks_completed = 0
        tasks_failed = 0

        # Execute until complete
        while not dag.is_complete():
            # Get ready tasks
            ready_tasks = dag.get_ready_tasks()

            if not ready_tasks:
                # No tasks ready - check if blocked
                blocked = dag.get_blocked_tasks()
                if blocked:
                    logger.warning(f"Project {project_id} has {len(blocked)} blocked tasks")
                    break

                # Wait for running tasks
                if dag.running_tasks:
                    await asyncio.sleep(1)
                    continue
                else:
                    # No running, no ready, no blocked - done
                    break

            # Execute ready tasks (up to parallel limit)
            batch = ready_tasks[:self.max_parallel - len(self.running_tasks)]

            if batch:
                # Execute batch in parallel
                results = await asyncio.gather(
                    *[self._execute_task(task, dag) for task in batch],
                    return_exceptions=True
                )

                for task, result in zip(batch, results):
                    if isinstance(result, Exception):
                        logger.error(f"Task {task.task_id} failed: {result}")
                        dag.mark_failed(task.task_id, str(result))
                        tasks_failed += 1
                    else:
                        dag.mark_completed(task.task_id)
                        tasks_completed += 1

            # Small delay between batches
            await asyncio.sleep(0.5)

        # Compute final stats
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        completion_stats = dag.get_completion_stats()

        logger.info(f"Project {project_id} execution complete: {completion_stats}")

        return {
            "project_id": project_id,
            "duration_minutes": duration,
            "tasks_completed": tasks_completed,
            "tasks_failed": tasks_failed,
            **completion_stats
        }

    async def _execute_task(self, task: Task, dag: TaskDAG) -> bool:
        """
        Execute a single task

        Args:
            task: Task to execute
            dag: Parent DAG

        Returns:
            True if successful, raises exception on failure
        """
        async with self.execution_semaphore:
            logger.info(f"Executing task {task.task_id} ({task.agent_type})")

            # Mark as running
            dag.mark_running(task.task_id)
            self.running_tasks[task.task_id] = task

            try:
                # Request resource allocation
                resource_request = TaskResourceRequest(
                    task_id=task.task_id,
                    project_id=task.project_id,
                    agent_type=task.agent_type,
                    preferred_model=task.preferred_model,
                    estimated_messages=task.estimated_messages,
                    estimated_input_tokens=task.estimated_tokens // 2,
                    estimated_output_tokens=task.estimated_tokens // 2,
                    priority=task.priority,
                    requires_opus=task.requires_opus,
                    deadline=task.deadline
                )

                allocation = await self.resource_governor.request_resources(resource_request)

                if not allocation.allocated:
                    # Resource denied - requeue if deadline allows
                    if task.deadline and datetime.utcnow() < task.deadline:
                        logger.info(f"Task {task.task_id} requeued: {allocation.decision_reason}")
                        dag.tasks[task.task_id].status = TaskStatus.PENDING

                        if task.task_id in self.running_tasks:
                            del self.running_tasks[task.task_id]
                        if task.task_id in dag.running_tasks:
                            dag.running_tasks.remove(task.task_id)

                        # Wait if scheduled
                        if allocation.estimated_wait_time_seconds > 0:
                            await asyncio.sleep(min(allocation.estimated_wait_time_seconds, 60))

                        return False
                    else:
                        raise Exception(f"Resource allocation denied: {allocation.decision_reason}")

                # Update task with allocated model
                task.allocated_model = allocation.allocated_model

                # Simulate task execution (in real implementation, call actual agent)
                execution_time = task.estimated_messages * 2  # ~2 seconds per message
                await asyncio.sleep(min(execution_time, 10))  # Cap at 10 seconds for testing

                # Record actual usage
                task.actual_messages = task.estimated_messages
                task.actual_tokens = task.estimated_tokens

                logger.info(f"Task {task.task_id} completed successfully "
                           f"using {allocation.allocated_model.value}")

                return True

            except Exception as e:
                logger.error(f"Task {task.task_id} execution failed: {e}")

                # Retry logic
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.PENDING
                    logger.info(f"Task {task.task_id} retry {task.retry_count}/{task.max_retries}")

                    if task.task_id in self.running_tasks:
                        del self.running_tasks[task.task_id]
                    if task.task_id in dag.running_tasks:
                        dag.running_tasks.remove(task.task_id)

                    await asyncio.sleep(task.retry_count * 2)  # Exponential backoff
                    return False
                else:
                    raise

            finally:
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]

    def _validate_dag(self, dag: TaskDAG) -> bool:
        """
        Validate DAG has no cycles

        Args:
            dag: TaskDAG to validate

        Returns:
            True if valid (acyclic), False if cycles detected
        """
        visited = set()
        rec_stack = set()

        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            # Check all dependent tasks
            if task_id in dag.tasks:
                for dep_id in dag.tasks[task_id].depends_on:
                    if dep_id not in visited:
                        if has_cycle(dep_id):
                            return True
                    elif dep_id in rec_stack:
                        return True

            rec_stack.remove(task_id)
            return False

        for task_id in dag.tasks.keys():
            if task_id not in visited:
                if has_cycle(task_id):
                    logger.error(f"Cycle detected in DAG for project {dag.project_id}")
                    return False

        return True

    def _compute_execution_order(self, dag: TaskDAG) -> List[List[str]]:
        """
        Compute execution order using topological sort

        Returns:
            List of task ID batches (each batch can execute in parallel)
        """
        # Compute in-degree for each task
        in_degree = {task_id: len(task.depends_on) for task_id, task in dag.tasks.items()}

        # Queue for tasks with no dependencies
        ready_queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])

        execution_order = []

        while ready_queue:
            # Current batch (all tasks with 0 in-degree)
            batch = []
            batch_size = len(ready_queue)

            for _ in range(batch_size):
                task_id = ready_queue.popleft()
                batch.append(task_id)

                # Reduce in-degree for dependent tasks
                if task_id in dag.tasks:
                    for blocked_id in dag.tasks[task_id].blocks:
                        in_degree[blocked_id] -= 1
                        if in_degree[blocked_id] == 0:
                            ready_queue.append(blocked_id)

            # Sort batch by priority
            batch.sort(key=lambda tid: dag.tasks[tid].calculate_priority_score(), reverse=True)
            execution_order.append(batch)

        return execution_order

    def _estimate_execution(
        self,
        dag: TaskDAG,
        execution_order: List[List[str]]
    ) -> Tuple[float, float]:
        """
        Estimate execution duration and cost

        Returns:
            Tuple of (duration_minutes, cost_units)
        """
        total_duration = 0.0
        total_cost = 0.0

        for batch in execution_order:
            # Parallel batch - duration is max of batch
            batch_duration = 0.0
            batch_cost = 0.0

            for task_id in batch:
                task = dag.tasks[task_id]

                # Estimate ~2 minutes per message
                task_duration = task.estimated_messages * 2

                # Estimate cost (assume worst case Opus)
                task_cost = task.estimated_messages * 5.0 if task.requires_opus else task.estimated_messages * 1.5

                batch_duration = max(batch_duration, task_duration)
                batch_cost += task_cost

            total_duration += batch_duration
            total_cost += batch_cost

        return total_duration, total_cost

    def get_project_status(self, project_id: str) -> Optional[Dict[str, any]]:
        """Get current status of a project"""
        if project_id not in self.active_dags:
            return None

        dag = self.active_dags[project_id]
        return {
            "project_id": project_id,
            "is_complete": dag.is_complete(),
            "stats": dag.get_completion_stats(),
            "running_tasks": list(dag.running_tasks),
            "ready_tasks": [t.task_id for t in dag.get_ready_tasks()],
            "blocked_tasks": [t.task_id for t in dag.get_blocked_tasks()]
        }

    def cancel_project(self, project_id: str) -> bool:
        """Cancel a project execution"""
        if project_id not in self.active_dags:
            return False

        dag = self.active_dags[project_id]

        # Cancel all pending/running tasks
        for task in dag.tasks.values():
            if task.status in [TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.RUNNING]:
                task.status = TaskStatus.CANCELLED

        logger.info(f"Project {project_id} cancelled")
        return True
