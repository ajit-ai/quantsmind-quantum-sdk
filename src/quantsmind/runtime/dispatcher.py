"""
Runtime Dispatcher Module

This module provides dispatcher for the Runtime package.

Purpose
-------
Provide task dispatching for the QuantsMind SDK.

Responsibilities
----------------
- Dispatch tasks to executors
- Manage executor pool
- Handle task routing
- Track dispatched tasks

Dependencies
------------
typing (standard library)
logging (standard library)
threading (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.executor (executor)
quantsmind.runtime.task (task)
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, List, Optional

from quantsmind.runtime.constants import RUNTIME_VERSION
from quantsmind.runtime.enums import ExecutionState
from quantsmind.runtime.exceptions import TaskError
from quantsmind.runtime.executor import Executor
from quantsmind.runtime.task import Task
from quantsmind.runtime.types import Callback, ExecutionResult, TaskID

logger = logging.getLogger(__name__)


class Dispatcher:
    """Concrete implementation of a dispatcher.

    This class provides task dispatching capabilities.

    Attributes:
        _executors: Executor pool
        _current_executor_index: Current executor index
        _lock: Thread lock
        _dispatched_tasks: Dispatched tasks

    Example:
        >>> dispatcher = Dispatcher(num_executors=4)
        >>> dispatcher.dispatch(task)
    """

    def __init__(self, num_executors: int = 4, max_workers_per_executor: int = 2) -> None:
        """Initialize a Dispatcher.

        Args:
            num_executors: Number of executors
            max_workers_per_executor: Maximum workers per executor

        Example:
            >>> dispatcher = Dispatcher(num_executors=4)
        """
        self._executors: List[Executor] = [
            Executor(max_workers=max_workers_per_executor) for _ in range(num_executors)
        ]
        self._current_executor_index = 0
        self._lock = threading.Lock()
        self._dispatched_tasks: Dict[TaskID, Executor] = {}
        logger.debug(f"Created dispatcher with {num_executors} executors")

    @property
    def num_executors(self) -> int:
        """Get the number of executors.

        Returns:
            Number of executors

        Example:
            >>> print(f"Num executors: {dispatcher.num_executors}")
        """
        return len(self._executors)

    @property
    def dispatched_count(self) -> int:
        """Get the number of dispatched tasks.

        Returns:
            Number of dispatched tasks

        Example:
            >>> print(f"Dispatched count: {dispatcher.dispatched_count}")
        """
        with self._lock:
            return len(self._dispatched_tasks)

    def dispatch(self, task: Task, callback: Optional[Callback] = None) -> ExecutionResult:
        """Dispatch a task to an executor.

        Args:
            task: Task to dispatch
            callback: Optional callback

        Returns:
            Execution result

        Raises:
            TaskError: If dispatch fails

        Example:
            >>> result = dispatcher.dispatch(task)
        """
        executor = self._get_next_executor()
        
        with self._lock:
            self._dispatched_tasks[task.task_id] = executor
        
        result = executor.execute(task, callback)
        
        with self._lock:
            if task.task_id in self._dispatched_tasks:
                del self._dispatched_tasks[task.task_id]
        
        return result

    def dispatch_async(self, task: Task, callback: Optional[Callback] = None) -> None:
        """Dispatch a task asynchronously.

        Args:
            task: Task to dispatch
            callback: Optional callback

        Example:
            >>> dispatcher.dispatch_async(task)
        """
        executor = self._get_next_executor()
        
        with self._lock:
            self._dispatched_tasks[task.task_id] = executor
        
        executor.execute_async(task, callback)

    def _get_next_executor(self) -> Executor:
        """Get the next executor using round-robin.

        Returns:
            Next executor
        """
        with self._lock:
            executor = self._executors[self._current_executor_index]
            self._current_executor_index = (self._current_executor_index + 1) % len(self._executors)
        return executor

    def cancel(self, task_id: TaskID) -> bool:
        """Cancel a dispatched task.

        Args:
            task_id: Task identifier

        Returns:
            True if cancelled, False otherwise

        Example:
            >>> cancelled = dispatcher.cancel("task_123")
        """
        with self._lock:
            if task_id in self._dispatched_tasks:
                executor = self._dispatched_tasks[task_id]
                del self._dispatched_tasks[task_id]
                return executor.cancel(task_id)
        return False

    def get_executor_status(self) -> List[Dict[str, Any]]:
        """Get executor status.

        Returns:
            List of executor status

        Example:
            >>> status = dispatcher.get_executor_status()
        """
        return [
            {
                "index": i,
                "active_count": executor.active_count,
                "completed_count": executor.completed_count,
                "failed_count": executor.failed_count,
            }
            for i, executor in enumerate(self._executors)
        ]

    def shutdown(self) -> None:
        """Shutdown the dispatcher.

        Example:
            >>> dispatcher.shutdown()
        """
        for executor in self._executors:
            executor.shutdown()
        logger.info("Dispatcher shutdown")


# Export
__all__ = [
    "Dispatcher",
]
