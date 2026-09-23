"""
Runtime Job Module

This module provides job management for the Runtime package.

Purpose
-------
Provide job management for the QuantsMind SDK.

Responsibilities
----------------
- Manage job lifecycle
- Schedule tasks within jobs
- Track job progress
- Handle job dependencies

Dependencies
------------
typing (standard library)
logging (standard library)
uuid (standard library)
datetime (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.task (task)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from quantsmind.runtime.constants import RUNTIME_VERSION
from quantsmind.runtime.enums import ExecutionState, TaskPriority
from quantsmind.runtime.exceptions import JobError
from quantsmind.runtime.task import Task
from quantsmind.runtime.types import ExecutionResult, JobID, TaskID

logger = logging.getLogger(__name__)


class Job:
    """Concrete implementation of a job.

    This class provides job management for execution operations.

    Attributes:
        _job_id: Job identifier
        _name: Job name
        _tasks: Job tasks
        _state: Job state
        _priority: Job priority
        _dependencies: Job dependencies
        _results: Task results
        _created_at: Creation timestamp
        _started_at: Start timestamp
        _completed_at: Completion timestamp
        _metadata: Job metadata

    Example:
        >>> job = Job(name="my_job")
        >>> job.add_task(task)
        >>> job.execute()
    """

    def __init__(
        self,
        name: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: list[JobID] | None = None,
        job_id: JobID | None = None,
    ) -> None:
        """Initialize a Job.

        Args:
            name: Job name
            priority: Job priority
            dependencies: Job dependencies
            job_id: Optional job identifier

        Example:
            >>> job = Job(name="my_job")
        """
        self._job_id = job_id or str(uuid.uuid4())
        self._name = name
        self._tasks: dict[TaskID, Task] = {}
        self._state = ExecutionState.CREATED
        self._priority = priority
        self._dependencies = dependencies or []
        self._results: dict[TaskID, ExecutionResult] = {}
        self._created_at = datetime.now(UTC).replace(tzinfo=None)
        self._started_at: datetime | None = None
        self._completed_at: datetime | None = None
        self._metadata: dict[str, Any] = {
            "runtime_version": RUNTIME_VERSION,
        }
        logger.debug(f"Created job: {self._job_id}")

    @property
    def job_id(self) -> JobID:
        """Get the job ID.

        Returns:
            Job identifier

        Example:
            >>> print(f"Job ID: {job.job_id}")
        """
        return self._job_id

    @property
    def name(self) -> str:
        """Get the job name.

        Returns:
            Job name

        Example:
            >>> print(f"Name: {job.name}")
        """
        return self._name

    @property
    def state(self) -> ExecutionState:
        """Get the job state.

        Returns:
            Job state

        Example:
            >>> print(f"State: {job.state}")
        """
        return self._state

    @property
    def priority(self) -> TaskPriority:
        """Get the job priority.

        Returns:
            Job priority

        Example:
            >>> print(f"Priority: {job.priority}")
        """
        return self._priority

    @property
    def dependencies(self) -> list[JobID]:
        """Get the job dependencies.

        Returns:
            Job dependencies

        Example:
            >>> print(f"Dependencies: {job.dependencies}")
        """
        return self._dependencies.copy()

    @property
    def task_count(self) -> int:
        """Get the number of tasks.

        Returns:
            Number of tasks

        Example:
            >>> print(f"Task count: {job.task_count}")
        """
        return len(self._tasks)

    @property
    def is_completed(self) -> bool:
        """Check if the job is completed.

        Returns:
            True if completed, False otherwise

        Example:
            >>> if job.is_completed:
            ...     print("Job completed")
        """
        return self._state in [ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED]

    def add_task(self, task: Task) -> None:
        """Add a task to the job.

        Args:
            task: Task to add

        Raises:
            JobError: If task already exists

        Example:
            >>> job.add_task(task)
        """
        if task.task_id in self._tasks:
            raise JobError(f"Task already exists: {task.task_id}", job_id=self._job_id)
        self._tasks[task.task_id] = task
        logger.debug(f"Added task to job: {task.task_id}")

    def remove_task(self, task_id: TaskID) -> None:
        """Remove a task from the job.

        Args:
            task_id: Task identifier

        Example:
            >>> job.remove_task("task_123")
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            logger.debug(f"Removed task from job: {task_id}")

    def get_task(self, task_id: TaskID) -> Task | None:
        """Get a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task or None

        Example:
            >>> task = job.get_task("task_123")
        """
        return self._tasks.get(task_id)

    def get_tasks(self) -> list[Task]:
        """Get all tasks.

        Returns:
            List of tasks

        Example:
            >>> tasks = job.get_tasks()
        """
        return list(self._tasks.values())

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the job.

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> is_valid, errors = job.validate()
        """
        errors = []

        if not self._name:
            errors.append("Job name is required")

        if not self._tasks:
            errors.append("Job must have at least one task")

        for task in self._tasks.values():
            is_valid, task_errors = task.validate()
            if not is_valid:
                errors.extend([f"Task {task.task_id}: {err}" for err in task_errors])

        return (len(errors) == 0, errors)

    def execute(self) -> dict[TaskID, ExecutionResult]:
        """Execute the job.

        Returns:
            Dictionary of task results

        Raises:
            JobError: If execution fails

        Example:
            >>> results = job.execute()
        """
        if self._state != ExecutionState.QUEUED and self._state != ExecutionState.CREATED:
            raise JobError(f"Cannot execute job in state: {self._state}", job_id=self._job_id)

        self._state = ExecutionState.RUNNING
        self._started_at = datetime.now(UTC).replace(tzinfo=None)
        logger.info(f"Executing job: {self._job_id}")

        try:
            for task in self._tasks.values():
                task._state = ExecutionState.QUEUED
                result = task.execute()
                self._results[task.task_id] = result

            self._state = ExecutionState.COMPLETED
            self._completed_at = datetime.now(UTC).replace(tzinfo=None)
            logger.info(f"Job completed: {self._job_id}")
            return self._results
        except Exception as e:
            self._state = ExecutionState.FAILED
            self._completed_at = datetime.now(UTC).replace(tzinfo=None)
            logger.error(f"Job failed: {self._job_id}", exc_info=True)
            raise JobError(f"Job execution failed: {str(e)}", job_id=self._job_id) from e

    def cancel(self) -> None:
        """Cancel the job.

        Example:
            >>> job.cancel()
        """
        if self._state not in [ExecutionState.CREATED, ExecutionState.QUEUED, ExecutionState.RUNNING]:
            logger.warning(f"Cancelling job in state: {self._state}")
        
        for task in self._tasks.values():
            task.cancel()
        
        self._state = ExecutionState.CANCELLED
        self._completed_at = datetime.now(UTC).replace(tzinfo=None)
        logger.info(f"Cancelled job: {self._job_id}")

    def set_metadata(self, key: str, value: Any) -> None:
        """Set job metadata.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> job.set_metadata("description", "My job")
        """
        self._metadata[key] = value
        logger.debug(f"Set job metadata: {key}")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get job metadata.

        Args:
            key: Metadata key
            default: Default value

        Returns:
            Metadata value or default

        Example:
            >>> value = job.get_metadata("description")
        """
        return self._metadata.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert job to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = job.to_dict()
        """
        return {
            "job_id": self._job_id,
            "name": self._name,
            "state": self._state.value,
            "priority": self._priority.value,
            "dependencies": self._dependencies.copy(),
            "task_count": self.task_count,
            "created_at": self._created_at.isoformat(),
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "completed_at": self._completed_at.isoformat() if self._completed_at else None,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(job)
        """
        return f"Job(job_id={self._job_id}, name={self._name}, state={self._state.value})"


# Export
__all__ = [
    "Job",
]
