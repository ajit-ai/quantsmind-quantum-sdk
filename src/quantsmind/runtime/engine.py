"""
Runtime Engine Module

This module provides execution engine for the Runtime package.

Purpose
-------
Provide execution engine for the QuantsMind SDK.

Responsibilities
----------------
- Manage execution lifecycle
- Coordinate executor, scheduler, dispatcher
- Track execution history
- Handle execution errors

Dependencies
------------
typing (standard library)
logging (standard library)
threading (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.context (context)
quantsmind.runtime.session (session)
quantsmind.runtime.executor (executor)
quantsmind.runtime.scheduler (scheduler)
quantsmind.runtime.dispatcher (dispatcher)
quantsmind.runtime.task (task)
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any

from quantsmind.runtime.dispatcher import Dispatcher
from quantsmind.runtime.exceptions import ExecutionError
from quantsmind.runtime.executor import Executor
from quantsmind.runtime.scheduler import Scheduler
from quantsmind.runtime.session import RuntimeSession
from quantsmind.runtime.task import Task
from quantsmind.runtime.types import (
    Callback,
    ExecutionResult,
)

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """Concrete implementation of an execution engine.

    This class provides execution engine capabilities.

    Attributes:
        _session: Runtime session
        _scheduler: Task scheduler
        _dispatcher: Task dispatcher
        _executor: Task executor
        _execution_history: Execution history
        _running: Running state
        _lock: Thread lock

    Example:
        >>> engine = ExecutionEngine()
        >>> engine.start()
        >>> engine.execute(task)
    """

    def __init__(
        self,
        num_executors: int = 4,
        max_workers_per_executor: int = 2,
        max_queue_size: int = 1000,
    ) -> None:
        """Initialize an ExecutionEngine.

        Args:
            num_executors: Number of executors
            max_workers_per_executor: Maximum workers per executor
            max_queue_size: Maximum queue size

        Example:
            >>> engine = ExecutionEngine()
        """
        self._session = RuntimeSession()
        self._scheduler = Scheduler(max_queue_size=max_queue_size)
        self._dispatcher = Dispatcher(num_executors=num_executors, max_workers_per_executor=max_workers_per_executor)
        self._executor = Executor(max_workers=max_workers_per_executor * num_executors)
        self._execution_history: list[dict[str, Any]] = []
        self._running = False
        self._lock = threading.Lock()
        logger.debug("Created execution engine")

    @property
    def session(self) -> RuntimeSession:
        """Get the runtime session.

        Returns:
            Runtime session

        Example:
            >>> session = engine.session
        """
        return self._session

    @property
    def is_running(self) -> bool:
        """Check if the engine is running.

        Returns:
            True if running, False otherwise

        Example:
            >>> if engine.is_running:
            ...     print("Engine is running")
        """
        return self._running

    @property
    def execution_count(self) -> int:
        """Get the number of executions.

        Returns:
            Number of executions

        Example:
            >>> print(f"Execution count: {engine.execution_count}")
        """
        with self._lock:
            return len(self._execution_history)

    def start(self) -> None:
        """Start the execution engine.

        Example:
            >>> engine.start()
        """
        self._session.initialize()
        self._session.start()
        self._scheduler.start()
        self._running = True
        logger.info("Execution engine started")

    def stop(self) -> None:
        """Stop the execution engine.

        Example:
            >>> engine.stop()
        """
        self._running = False
        self._scheduler.stop()
        self._dispatcher.shutdown()
        self._executor.shutdown()
        self._session.close()
        logger.info("Execution engine stopped")

    def execute(self, task: Task, callback: Callback | None = None) -> ExecutionResult:
        """Execute a task.

        Args:
            task: Task to execute
            callback: Optional callback

        Returns:
            Execution result

        Raises:
            ExecutionError: If execution fails

        Example:
            >>> result = engine.execute(task)
        """
        if not self._running:
            raise ExecutionError("Engine is not running")

        self._scheduler.schedule(task)
        result = self._dispatcher.dispatch(task, callback)
        
        self._record_execution(task, result)
        
        return result

    def execute_async(self, task: Task, callback: Callback | None = None) -> None:
        """Execute a task asynchronously.

        Args:
            task: Task to execute
            callback: Optional callback

        Example:
            >>> engine.execute_async(task)
        """
        if not self._running:
            raise ExecutionError("Engine is not running")

        self._scheduler.schedule(task)
        self._dispatcher.dispatch_async(task, callback)

    def _record_execution(self, task: Task, result: ExecutionResult) -> None:
        """Record execution in history.

        Args:
            task: Task
            result: Result
        """
        with self._lock:
            self._execution_history.append({
                "task_id": task.task_id,
                "name": task.name,
                "state": task.state.value,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            })

    def get_execution_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get execution history.

        Args:
            limit: Maximum number of records

        Returns:
            Execution history

        Example:
            >>> history = engine.get_execution_history()
        """
        with self._lock:
            return self._execution_history[-limit:]

    def get_status(self) -> dict[str, Any]:
        """Get engine status.

        Returns:
            Engine status

        Example:
            >>> status = engine.get_status()
        """
        return {
            "running": self._running,
            "session_id": self._session.session_id,
            "session_state": self._session.state.value,
            "scheduler_queue_size": self._scheduler.queue_size,
            "scheduler_scheduled_count": self._scheduler.scheduled_count,
            "dispatcher_dispatched_count": self._dispatcher.dispatched_count,
            "executor_status": {
                "active_count": self._executor.active_count,
                "completed_count": self._executor.completed_count,
                "failed_count": self._executor.failed_count,
            },
            "execution_count": self.execution_count,
        }


# Export
__all__ = [
    "ExecutionEngine",
]
