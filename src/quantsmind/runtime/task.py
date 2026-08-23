"""
Runtime Task Module

This module provides task management for the Runtime package.

Purpose
-------
Provide task management for the QuantsMind SDK.

Responsibilities
----------------
- Manage task lifecycle
- Execute tasks
- Track task progress
- Handle task dependencies

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
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from quantsmind.runtime.constants import (
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    RUNTIME_VERSION,
)
from quantsmind.runtime.enums import ExecutionState, RetryPolicy, TaskPriority
from quantsmind.runtime.exceptions import TaskError
from quantsmind.runtime.types import ExecutionResult, TaskID

logger = logging.getLogger(__name__)


class Task:
    """Concrete implementation of a task.

    This class provides task management for execution operations.

    Attributes:
        _task_id: Task identifier
        _name: Task name
        _func: Task function
        _args: Task arguments
        _kwargs: Task keyword arguments
        _state: Task state
        _priority: Task priority
        _timeout: Task timeout
        _retry_policy: Retry policy
        _retry_count: Retry count
        _retry_delay: Retry delay
        _dependencies: Task dependencies
        _result: Task result
        _error: Task error
        _created_at: Creation timestamp
        _started_at: Start timestamp
        _completed_at: Completion timestamp
        _metadata: Task metadata

    Example:
        >>> task = Task(name="my_task", func=lambda x: x * 2, args=[5])
        >>> task.execute()
    """

    def __init__(
        self,
        name: str,
        func: Callable[..., ExecutionResult],
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: float = DEFAULT_TIMEOUT,
        retry_policy: RetryPolicy = RetryPolicy.NONE,
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        dependencies: list[TaskID] | None = None,
        task_id: TaskID | None = None,
    ) -> None:
        """Initialize a Task.

        Args:
            name: Task name
            func: Task function
            args: Task arguments
            kwargs: Task keyword arguments
            priority: Task priority
            timeout: Task timeout
            retry_policy: Retry policy
            retry_count: Retry count
            retry_delay: Retry delay
            dependencies: Task dependencies
            task_id: Optional task identifier

        Example:
            >>> task = Task(name="my_task", func=lambda x: x * 2, args=[5])
        """
        self._task_id = task_id or str(uuid.uuid4())
        self._name = name
        self._func = func
        self._args = args or []
        self._kwargs = kwargs or {}
        self._state = ExecutionState.CREATED
        self._priority = priority
        self._timeout = timeout
        self._retry_policy = retry_policy
        self._retry_count = retry_count
        self._retry_delay = retry_delay
        self._dependencies = dependencies or []
        self._result: ExecutionResult | None = None
        self._error: Exception | None = None
        self._created_at = datetime.utcnow()
        self._started_at: datetime | None = None
        self._completed_at: datetime | None = None
        self._metadata: dict[str, Any] = {
            "runtime_version": RUNTIME_VERSION,
        }
        logger.debug(f"Created task: {self._task_id}")

    @property
    def task_id(self) -> TaskID:
        """Get the task ID.

        Returns:
            Task identifier

        Example:
            >>> print(f"Task ID: {task.task_id}")
        """
        return self._task_id

    @property
    def name(self) -> str:
        """Get the task name.

        Returns:
            Task name

        Example:
            >>> print(f"Name: {task.name}")
        """
        return self._name

    @property
    def state(self) -> ExecutionState:
        """Get the task state.

        Returns:
            Task state

        Example:
            >>> print(f"State: {task.state}")
        """
        return self._state

    @property
    def priority(self) -> TaskPriority:
        """Get the task priority.

        Returns:
            Task priority

        Example:
            >>> print(f"Priority: {task.priority}")
        """
        return self._priority

    @property
    def timeout(self) -> float:
        """Get the task timeout.

        Returns:
            Task timeout

        Example:
            >>> print(f"Timeout: {task.timeout}")
        """
        return self._timeout

    @property
    def dependencies(self) -> list[TaskID]:
        """Get the task dependencies.

        Returns:
            Task dependencies

        Example:
            >>> print(f"Dependencies: {task.dependencies}")
        """
        return self._dependencies.copy()

    @property
    def result(self) -> ExecutionResult | None:
        """Get the task result.

        Returns:
            Task result or None

        Example:
            >>> result = task.result
        """
        return self._result

    @property
    def error(self) -> Exception | None:
        """Get the task error.

        Returns:
            Task error or None

        Example:
            >>> error = task.error
        """
        return self._error

    @property
    def is_completed(self) -> bool:
        """Check if the task is completed.

        Returns:
            True if completed, False otherwise

        Example:
            >>> if task.is_completed:
            ...     print("Task completed")
        """
        return self._state in [ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED]

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the task.

        Returns:
            Tuple of (is_valid, errors)

        Example:
            >>> is_valid, errors = task.validate()
        """
        errors = []

        if not self._name:
            errors.append("Task name is required")

        if not callable(self._func):
            errors.append("Task function must be callable")

        if self._timeout <= 0:
            errors.append("Timeout must be positive")

        if self._retry_count < 0:
            errors.append("Retry count must be non-negative")

        if self._retry_delay < 0:
            errors.append("Retry delay must be non-negative")

        return (len(errors) == 0, errors)

    def execute(self) -> ExecutionResult:
        """Execute the task.

        Returns:
            Execution result

        Raises:
            TaskError: If execution fails

        Example:
            >>> result = task.execute()
        """
        if self._state != ExecutionState.QUEUED and self._state != ExecutionState.CREATED:
            raise TaskError(f"Cannot execute task in state: {self._state}", task_id=self._task_id)

        self._state = ExecutionState.RUNNING
        self._started_at = datetime.utcnow()
        logger.info(f"Executing task: {self._task_id}")

        try:
            self._result = self._func(*self._args, **self._kwargs)
            self._state = ExecutionState.COMPLETED
            self._completed_at = datetime.utcnow()
            logger.info(f"Task completed: {self._task_id}")
            return self._result
        except Exception as e:
            self._error = e
            self._state = ExecutionState.FAILED
            self._completed_at = datetime.utcnow()
            logger.error(f"Task failed: {self._task_id}", exc_info=True)
            raise TaskError(f"Task execution failed: {str(e)}", task_id=self._task_id) from e

    def cancel(self) -> None:
        """Cancel the task.

        Example:
            >>> task.cancel()
        """
        if self._state not in [ExecutionState.CREATED, ExecutionState.QUEUED, ExecutionState.RUNNING]:
            logger.warning(f"Cancelling task in state: {self._state}")
        self._state = ExecutionState.CANCELLED
        self._completed_at = datetime.utcnow()
        logger.info(f"Cancelled task: {self._task_id}")

    def set_metadata(self, key: str, value: Any) -> None:
        """Set task metadata.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> task.set_metadata("description", "My task")
        """
        self._metadata[key] = value
        logger.debug(f"Set task metadata: {key}")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get task metadata.

        Args:
            key: Metadata key
            default: Default value

        Returns:
            Metadata value or default

        Example:
            >>> value = task.get_metadata("description")
        """
        return self._metadata.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = task.to_dict()
        """
        return {
            "task_id": self._task_id,
            "name": self._name,
            "state": self._state.value,
            "priority": self._priority.value,
            "timeout": self._timeout,
            "retry_policy": self._retry_policy.value,
            "retry_count": self._retry_count,
            "retry_delay": self._retry_delay,
            "dependencies": self._dependencies.copy(),
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
            >>> repr(task)
        """
        return f"Task(task_id={self._task_id}, name={self._name}, state={self._state.value})"


# Export
__all__ = [
    "Task",
]
