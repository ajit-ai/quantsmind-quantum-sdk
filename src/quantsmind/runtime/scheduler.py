"""
Runtime Scheduler Module

This module provides scheduler for the Runtime package.

Purpose
-------
Provide task scheduling for the QuantsMind SDK.

Responsibilities
----------------
- Schedule tasks
- Manage task queue
- Handle task priorities
- Track scheduled tasks

Dependencies
------------
typing (standard library)
logging (standard library)
queue (standard library)
threading (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.task (task)
"""

from __future__ import annotations

import logging
import queue
import threading
from typing import Any, Dict, List, Optional

from quantsmind.runtime.constants import DEFAULT_MAX_QUEUE_SIZE
from quantsmind.runtime.enums import ExecutionState, TaskPriority
from quantsmind.runtime.exceptions import TaskError
from quantsmind.runtime.task import Task
from quantsmind.runtime.types import TaskID

logger = logging.getLogger(__name__)


class Scheduler:
    """Concrete implementation of a scheduler.

    This class provides task scheduling capabilities.

    Attributes:
        _queue: Task queue
        _max_queue_size: Maximum queue size
        _scheduled_tasks: Scheduled tasks
        _lock: Thread lock
        _running: Running state

    Example:
        >>> scheduler = Scheduler(max_queue_size=100)
        >>> scheduler.schedule(task)
    """

    def __init__(self, max_queue_size: int = DEFAULT_MAX_QUEUE_SIZE) -> None:
        """Initialize a Scheduler.

        Args:
            max_queue_size: Maximum queue size

        Example:
            >>> scheduler = Scheduler(max_queue_size=100)
        """
        self._queue: queue.PriorityQueue = queue.PriorityQueue(maxsize=max_queue_size)
        self._max_queue_size = max_queue_size
        self._scheduled_tasks: Dict[TaskID, Task] = {}
        self._lock = threading.Lock()
        self._running = False
        logger.debug(f"Created scheduler with max_queue_size={max_queue_size}")

    @property
    def max_queue_size(self) -> int:
        """Get the maximum queue size.

        Returns:
            Maximum queue size

        Example:
            >>> print(f"Max queue size: {scheduler.max_queue_size}")
        """
        return self._max_queue_size

    @property
    def queue_size(self) -> int:
        """Get the current queue size.

        Returns:
            Current queue size

        Example:
            >>> print(f"Queue size: {scheduler.queue_size}")
        """
        return self._queue.qsize()

    @property
    def scheduled_count(self) -> int:
        """Get the number of scheduled tasks.

        Returns:
            Number of scheduled tasks

        Example:
            >>> print(f"Scheduled count: {scheduler.scheduled_count}")
        """
        with self._lock:
            return len(self._scheduled_tasks)

    def schedule(self, task: Task) -> None:
        """Schedule a task.

        Args:
            task: Task to schedule

        Raises:
            TaskError: If queue is full

        Example:
            >>> scheduler.schedule(task)
        """
        if self._queue.full():
            raise TaskError("Queue is full", task_id=task.task_id)

        # Priority: lower value = higher priority
        priority = 5 - task.priority.value
        self._queue.put((priority, task.task_id, task))
        
        with self._lock:
            self._scheduled_tasks[task.task_id] = task
        
        task._state = ExecutionState.QUEUED
        logger.debug(f"Scheduled task: {task.task_id}")

    def unschedule(self, task_id: TaskID) -> bool:
        """Unschedule a task.

        Args:
            task_id: Task identifier

        Returns:
            True if unscheduled, False otherwise

        Example:
            >>> unscheduled = scheduler.unschedule("task_123")
        """
        with self._lock:
            if task_id in self._scheduled_tasks:
                task = self._scheduled_tasks[task_id]
                task._state = ExecutionState.CANCELLED
                del self._scheduled_tasks[task_id]
                return True
        return False

    def get_next(self) -> Optional[Task]:
        """Get the next task to execute.

        Returns:
            Next task or None

        Example:
            >>> task = scheduler.get_next()
        """
        try:
            priority, task_id, task = self._queue.get_nowait()
            
            with self._lock:
                if task_id in self._scheduled_tasks:
                    del self._scheduled_tasks[task_id]
            
            return task
        except queue.Empty:
            return None

    def peek(self) -> Optional[Task]:
        """Peek at the next task without removing it.

        Returns:
            Next task or None

        Example:
            >>> task = scheduler.peek()
        """
        if self._queue.empty():
            return None
        
        priority, task_id, task = self._queue.queue[0]
        return task

    def clear(self) -> None:
        """Clear the scheduler.

        Example:
            >>> scheduler.clear()
        """
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break
            self._scheduled_tasks.clear()
        logger.info("Scheduler cleared")

    def start(self) -> None:
        """Start the scheduler.

        Example:
            >>> scheduler.start()
        """
        self._running = True
        logger.info("Scheduler started")

    def stop(self) -> None:
        """Stop the scheduler.

        Example:
            >>> scheduler.stop()
        """
        self._running = False
        logger.info("Scheduler stopped")


# Export
__all__ = [
    "Scheduler",
]
