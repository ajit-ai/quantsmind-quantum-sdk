"""
Runtime Executor Module

This module provides executor for the Runtime package.

Purpose
-------
Provide task execution for the QuantsMind SDK.

Responsibilities
----------------
- Execute tasks
- Handle task lifecycle
- Track execution progress
- Manage execution errors

Dependencies
------------
typing (standard library)
logging (standard library)
threading (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.task (task)
"""

from __future__ import annotations

import logging
import threading

from quantsmind.runtime.enums import ExecutionState
from quantsmind.runtime.exceptions import TaskError
from quantsmind.runtime.task import Task
from quantsmind.runtime.types import Callback, ExecutionResult, TaskID

logger = logging.getLogger(__name__)


class Executor:
    """Concrete implementation of an executor.

    This class provides task execution capabilities.

    Attributes:
        _max_workers: Maximum number of workers
        _active_tasks: Active tasks
        _completed_tasks: Completed tasks
        _failed_tasks: Failed tasks
        _lock: Thread lock

    Example:
        >>> executor = Executor(max_workers=4)
        >>> executor.execute(task)
    """

    def __init__(self, max_workers: int = 4) -> None:
        """Initialize an Executor.

        Args:
            max_workers: Maximum number of workers

        Example:
            >>> executor = Executor(max_workers=4)
        """
        self._max_workers = max_workers
        self._active_tasks: dict[TaskID, Task] = {}
        self._completed_tasks: dict[TaskID, Task] = {}
        self._failed_tasks: dict[TaskID, Task] = {}
        self._lock = threading.Lock()
        logger.debug(f"Created executor with max_workers={max_workers}")

    @property
    def max_workers(self) -> int:
        """Get the maximum number of workers.

        Returns:
            Maximum number of workers

        Example:
            >>> print(f"Max workers: {executor.max_workers}")
        """
        return self._max_workers

    @property
    def active_count(self) -> int:
        """Get the number of active tasks.

        Returns:
            Number of active tasks

        Example:
            >>> print(f"Active count: {executor.active_count}")
        """
        with self._lock:
            return len(self._active_tasks)

    @property
    def completed_count(self) -> int:
        """Get the number of completed tasks.

        Returns:
            Number of completed tasks

        Example:
            >>> print(f"Completed count: {executor.completed_count}")
        """
        with self._lock:
            return len(self._completed_tasks)

    @property
    def failed_count(self) -> int:
        """Get the number of failed tasks.

        Returns:
            Number of failed tasks

        Example:
            >>> print(f"Failed count: {executor.failed_count}")
        """
        with self._lock:
            return len(self._failed_tasks)

    def execute(self, task: Task, callback: Callback | None = None) -> ExecutionResult:
        """Execute a task.

        Args:
            task: Task to execute
            callback: Optional callback

        Returns:
            Execution result

        Raises:
            TaskError: If execution fails

        Example:
            >>> result = executor.execute(task)
        """
        with self._lock:
            if len(self._active_tasks) >= self._max_workers:
                raise TaskError("Maximum workers reached", task_id=task.task_id)
            self._active_tasks[task.task_id] = task

        try:
            result = task.execute()
            
            with self._lock:
                del self._active_tasks[task.task_id]
                self._completed_tasks[task.task_id] = task

            if callback:
                callback(result)

            return result
        except Exception:
            with self._lock:
                if task.task_id in self._active_tasks:
                    del self._active_tasks[task.task_id]
                self._failed_tasks[task.task_id] = task
            raise

    def execute_async(self, task: Task, callback: Callback | None = None) -> None:
        """Execute a task asynchronously.

        Args:
            task: Task to execute
            callback: Optional callback

        Example:
            >>> executor.execute_async(task)
        """
        def _execute():
            try:
                self.execute(task, callback)
            except Exception:
                logger.error(f"Async execution failed: {task.task_id}", exc_info=True)

        thread = threading.Thread(target=_execute)
        thread.start()

    def cancel(self, task_id: TaskID) -> bool:
        """Cancel a task.

        Args:
            task_id: Task identifier

        Returns:
            True if cancelled, False otherwise

        Example:
            >>> cancelled = executor.cancel("task_123")
        """
        with self._lock:
            if task_id in self._active_tasks:
                task = self._active_tasks[task_id]
                task.cancel()
                del self._active_tasks[task_id]
                return True
        return False

    def get_task_status(self, task_id: TaskID) -> ExecutionState | None:
        """Get task status.

        Args:
            task_id: Task identifier

        Returns:
            Task state or None

        Example:
            >>> status = executor.get_task_status("task_123")
        """
        with self._lock:
            if task_id in self._active_tasks:
                return self._active_tasks[task_id].state
            elif task_id in self._completed_tasks:
                return self._completed_tasks[task_id].state
            elif task_id in self._failed_tasks:
                return self._failed_tasks[task_id].state
        return None

    def shutdown(self) -> None:
        """Shutdown the executor.

        Example:
            >>> executor.shutdown()
        """
        with self._lock:
            for task in self._active_tasks.values():
                task.cancel()
            self._active_tasks.clear()
        logger.info("Executor shutdown")


# Export
__all__ = [
    "Executor",
]
