"""
Runtime Interfaces Module

This module provides interfaces for the Runtime package.

Purpose
-------
Provide interfaces for the QuantsMind SDK.

Responsibilities
----------------
- Define execution interfaces
- Define resource interfaces
- Define plugin interfaces
- Define event interfaces

Dependencies
------------
typing (standard library)
abc (standard library)
quantsmind.runtime.types (runtime types)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from quantsmind.runtime.types import ExecutionResult, ResourceAmount


class IExecutor(ABC):
    """Interface for task executor.

    This interface defines the contract for task executors.

    Example:
        >>> class MyExecutor(IExecutor):
        ...     def execute(self, task):
        ...         return task.execute()
    """

    @abstractmethod
    def execute(self, task: Any, callback: Optional[Callable] = None) -> ExecutionResult:
        """Execute a task.

        Args:
            task: Task to execute
            callback: Optional callback

        Returns:
            Execution result
        """
        pass


class IScheduler(ABC):
    """Interface for task scheduler.

    This interface defines the contract for task schedulers.

    Example:
        >>> class MyScheduler(IScheduler):
        ...     def schedule(self, task):
        ...         self._queue.put(task)
    """

    @abstractmethod
    def schedule(self, task: Any) -> None:
        """Schedule a task.

        Args:
            task: Task to schedule
        """
        pass


class IResource(ABC):
    """Interface for resource.

    This interface defines the contract for resources.

    Example:
        >>> class MyResource(IResource):
        ...     def allocate(self, amount):
        ...         self._allocated += amount
    """

    @abstractmethod
    def allocate(self, amount: ResourceAmount) -> bool:
        """Allocate resource amount.

        Args:
            amount: Amount to allocate

        Returns:
            True if allocated, False otherwise
        """
        pass

    @abstractmethod
    def release(self, amount: ResourceAmount) -> bool:
        """Release resource amount.

        Args:
            amount: Amount to release

        Returns:
            True if released, False otherwise
        """
        pass


class IPlugin(ABC):
    """Interface for plugin.

    This interface defines the contract for plugins.

    Example:
        >>> class MyPlugin(IPlugin):
        ...     def initialize(self):
        ...         pass
    """

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin.

        Example:
            >>> plugin.initialize()
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup the plugin.

        Example:
            >>> plugin.cleanup()
        """
        pass


class IEventBus(ABC):
    """Interface for event bus.

    This interface defines the contract for event buses.

    Example:
        >>> class MyEventBus(IEventBus):
        ...     def publish(self, event):
        ...         self._dispatch(event)
    """

    @abstractmethod
    def publish(self, event: Any) -> None:
        """Publish an event.

        Args:
            event: Event to publish
        """
        pass

    @abstractmethod
    def subscribe(self, event_type: Any, callback: Callable) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Event type to subscribe to
            callback: Callback function
        """
        pass


class ICache(ABC):
    """Interface for cache.

    This interface defines the contract for caches.

    Example:
        >>> class MyCache(ICache):
        ...     def set(self, key, value):
        ...         self._cache[key] = value
    """

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set a cache entry.

        Args:
            key: Cache key
            value: Cache value
        """
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get a cache entry.

        Args:
            key: Cache key

        Returns:
            Cache value or None
        """
        pass


class IValidator(ABC):
    """Interface for validator.

    This interface defines the contract for validators.

    Example:
        >>> class MyValidator(IValidator):
        ...     def validate(self, obj):
        ...         return True, []
    """

    @abstractmethod
    def validate(self, obj: Any) -> tuple[bool, List[str]]:
        """Validate an object.

        Args:
            obj: Object to validate

        Returns:
            Tuple of (is_valid, errors)
        """
        pass


class ISerializer(ABC):
    """Interface for serializer.

    This interface defines the contract for serializers.

    Example:
        >>> class MySerializer(ISerializer):
        ...     def serialize(self, data):
        ...         return json.dumps(data)
    """

    @abstractmethod
    def serialize(self, data: Any, **kwargs: Any) -> str:
        """Serialize data.

        Args:
            data: Data to serialize
            **kwargs: Additional arguments

        Returns:
            Serialized string
        """
        pass

    @abstractmethod
    def deserialize(self, data: str, **kwargs: Any) -> Any:
        """Deserialize data.

        Args:
            data: Serialized string
            **kwargs: Additional arguments

        Returns:
            Deserialized data
        """
        pass


# Export
__all__ = [
    "IExecutor",
    "IScheduler",
    "IResource",
    "IPlugin",
    "IEventBus",
    "ICache",
    "IValidator",
    "ISerializer",
]
