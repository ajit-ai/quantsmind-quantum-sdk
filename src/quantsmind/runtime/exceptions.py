"""
Runtime Exceptions Module

This module provides exception hierarchy for the Runtime package.

Purpose
-------
Provide runtime exceptions for the QuantsMind SDK.

Responsibilities
----------------
- Define base runtime exception
- Define execution exceptions
- Define resource exceptions
- Define configuration exceptions
- Define plugin exceptions

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any


class RuntimeErrorError(Exception):
    """Base exception for runtime errors.

    This is the base class for all runtime-related exceptions.

    Attributes:
        message: Error message
        details: Additional error details

    Example:
        >>> raise RuntimeErrorError("Runtime error occurred")
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize a RuntimeErrorError.

        Args:
            message: Error message
            details: Additional error details

        Example:
            >>> raise RuntimeErrorError("Runtime error occurred")
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ExecutionError(RuntimeErrorError):
    """Exception for execution errors.

    Raised when an execution operation fails.

    Attributes:
        execution_id: Execution identifier

    Example:
        >>> raise ExecutionError("Task execution failed", execution_id="task_123")
    """

    def __init__(self, message: str, execution_id: str | None = None, **kwargs: Any) -> None:
        """Initialize an ExecutionError.

        Args:
            message: Error message
            execution_id: Execution identifier
            **kwargs: Additional details

        Example:
            >>> raise ExecutionError("Task execution failed", execution_id="task_123")
        """
        details = {"execution_id": execution_id, **kwargs}
        super().__init__(message, details)
        self.execution_id = execution_id


class TaskError(ExecutionError):
    """Exception for task errors.

    Raised when a task operation fails.

    Attributes:
        task_id: Task identifier

    Example:
        >>> raise TaskError("Task validation failed", task_id="task_123")
    """

    def __init__(self, message: str, task_id: str | None = None, **kwargs: Any) -> None:
        """Initialize a TaskError.

        Args:
            message: Error message
            task_id: Task identifier
            **kwargs: Additional details

        Example:
            >>> raise TaskError("Task validation failed", task_id="task_123")
        """
        details = {"task_id": task_id, **kwargs}
        super().__init__(message, details)
        self.task_id = task_id


class JobError(ExecutionError):
    """Exception for job errors.

    Raised when a job operation fails.

    Attributes:
        job_id: Job identifier

    Example:
        >>> raise JobError("Job scheduling failed", job_id="job_123")
    """

    def __init__(self, message: str, job_id: str | None = None, **kwargs: Any) -> None:
        """Initialize a JobError.

        Args:
            message: Error message
            job_id: Job identifier
            **kwargs: Additional details

        Example:
            >>> raise JobError("Job scheduling failed", job_id="job_123")
        """
        details = {"job_id": job_id, **kwargs}
        super().__init__(message, details)
        self.job_id = job_id


class WorkflowError(ExecutionError):
    """Exception for workflow errors.

    Raised when a workflow operation fails.

    Attributes:
        workflow_id: Workflow identifier

    Example:
        >>> raise WorkflowError("Workflow execution failed", workflow_id="workflow_123")
    """

    def __init__(self, message: str, workflow_id: str | None = None, **kwargs: Any) -> None:
        """Initialize a WorkflowError.

        Args:
            message: Error message
            workflow_id: Workflow identifier
            **kwargs: Additional details

        Example:
            >>> raise WorkflowError("Workflow execution failed", workflow_id="workflow_123")
        """
        details = {"workflow_id": workflow_id, **kwargs}
        super().__init__(message, details)
        self.workflow_id = workflow_id


class PipelineError(ExecutionError):
    """Exception for pipeline errors.

    Raised when a pipeline operation fails.

    Attributes:
        pipeline_id: Pipeline identifier

    Example:
        >>> raise PipelineError("Pipeline execution failed", pipeline_id="pipeline_123")
    """

    def __init__(self, message: str, pipeline_id: str | None = None, **kwargs: Any) -> None:
        """Initialize a PipelineError.

        Args:
            message: Error message
            pipeline_id: Pipeline identifier
            **kwargs: Additional details

        Example:
            >>> raise PipelineError("Pipeline execution failed", pipeline_id="pipeline_123")
        """
        details = {"pipeline_id": pipeline_id, **kwargs}
        super().__init__(message, details)
        self.pipeline_id = pipeline_id


class ResourceError(RuntimeErrorError):
    """Exception for resource errors.

    Raised when a resource operation fails.

    Attributes:
        resource_id: Resource identifier

    Example:
        >>> raise ResourceError("Resource allocation failed", resource_id="resource_123")
    """

    def __init__(self, message: str, resource_id: str | None = None, **kwargs: Any) -> None:
        """Initialize a ResourceError.

        Args:
            message: Error message
            resource_id: Resource identifier
            **kwargs: Additional details

        Example:
            >>> raise ResourceError("Resource allocation failed", resource_id="resource_123")
        """
        details = {"resource_id": resource_id, **kwargs}
        super().__init__(message, details)
        self.resource_id = resource_id


class ResourceAllocationError(ResourceError):
    """Exception for resource allocation errors.

    Raised when resource allocation fails.

    Example:
        >>> raise ResourceAllocationError("Insufficient memory", resource_id="memory_123")
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize a ResourceAllocationError.

        Args:
            message: Error message
            **kwargs: Additional details

        Example:
            >>> raise ResourceAllocationError("Insufficient memory", resource_id="memory_123")
        """
        super().__init__(message, **kwargs)


class ResourceExhaustionError(ResourceError):
    """Exception for resource exhaustion errors.

    Raised when a resource is exhausted.

    Example:
        >>> raise ResourceExhaustionError("CPU quota exceeded", resource_id="cpu_123")
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize a ResourceExhaustionError.

        Args:
            message: Error message
            **kwargs: Additional details

        Example:
            >>> raise ResourceExhaustionError("CPU quota exceeded", resource_id="cpu_123")
        """
        super().__init__(message, **kwargs)


class ConfigurationError(RuntimeErrorError):
    """Exception for configuration errors.

    Raised when a configuration operation fails.

    Attributes:
        config_key: Configuration key

    Example:
        >>> raise ConfigurationError("Invalid configuration value", config_key="timeout")
    """

    def __init__(self, message: str, config_key: str | None = None, **kwargs: Any) -> None:
        """Initialize a ConfigurationError.

        Args:
            message: Error message
            config_key: Configuration key
            **kwargs: Additional details

        Example:
            >>> raise ConfigurationError("Invalid configuration value", config_key="timeout")
        """
        details = {"config_key": config_key, **kwargs}
        super().__init__(message, details)
        self.config_key = config_key


class ValidationError(RuntimeErrorError):
    """Exception for validation errors.

    Raised when validation fails.

    Attributes:
        field: Field that failed validation

    Example:
        >>> raise ValidationError("Invalid task configuration", field="timeout")
    """

    def __init__(self, message: str, field: str | None = None, **kwargs: Any) -> None:
        """Initialize a ValidationError.

        Args:
            message: Error message
            field: Field that failed validation
            **kwargs: Additional details

        Example:
            >>> raise ValidationError("Invalid task configuration", field="timeout")
        """
        details = {"field": field, **kwargs}
        super().__init__(message, details)
        self.field = field


class PluginError(RuntimeErrorError):
    """Exception for plugin errors.

    Raised when a plugin operation fails.

    Attributes:
        plugin_id: Plugin identifier

    Example:
        >>> raise PluginError("Plugin loading failed", plugin_id="plugin_123")
    """

    def __init__(self, message: str, plugin_id: str | None = None, **kwargs: Any) -> None:
        """Initialize a PluginError.

        Args:
            message: Error message
            plugin_id: Plugin identifier
            **kwargs: Additional details

        Example:
            >>> raise PluginError("Plugin loading failed", plugin_id="plugin_123")
        """
        details = {"plugin_id": plugin_id, **kwargs}
        super().__init__(message, details)
        self.plugin_id = plugin_id


class PluginLoadError(PluginError):
    """Exception for plugin loading errors.

    Raised when plugin loading fails.

    Example:
        >>> raise PluginLoadError("Plugin not found", plugin_id="plugin_123")
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize a PluginLoadError.

        Args:
            message: Error message
            **kwargs: Additional details

        Example:
            >>> raise PluginLoadError("Plugin not found", plugin_id="plugin_123")
        """
        super().__init__(message, **kwargs)


class PluginDependencyError(PluginError):
    """Exception for plugin dependency errors.

    Raised when plugin dependencies are not satisfied.

    Example:
        >>> raise PluginDependencyError("Missing dependency", plugin_id="plugin_123")
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize a PluginDependencyError.

        Args:
            message: Error message
            **kwargs: Additional details

        Example:
            >>> raise PluginDependencyError("Missing dependency", plugin_id="plugin_123")
        """
        super().__init__(message, **kwargs)


class TimeoutError(RuntimeErrorError):
    """Exception for timeout errors.

    Raised when an operation times out.

    Attributes:
        timeout: Timeout value

    Example:
        >>> raise TimeoutError("Operation timed out", timeout=300.0)
    """

    def __init__(self, message: str, timeout: float | None = None, **kwargs: Any) -> None:
        """Initialize a TimeoutError.

        Args:
            message: Error message
            timeout: Timeout value
            **kwargs: Additional details

        Example:
            >>> raise TimeoutError("Operation timed out", timeout=300.0)
        """
        details = {"timeout": timeout, **kwargs}
        super().__init__(message, details)
        self.timeout = timeout


class CancellationError(RuntimeErrorError):
    """Exception for cancellation errors.

    Raised when an operation is cancelled.

    Example:
        >>> raise CancellationError("Operation cancelled by user")
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize a CancellationError.

        Args:
            message: Error message
            **kwargs: Additional details

        Example:
            >>> raise CancellationError("Operation cancelled by user")
        """
        super().__init__(message, **kwargs)


class StateMachineError(RuntimeErrorError):
    """Exception for state machine errors.

    Raised when a state transition is invalid.

    Attributes:
        from_state: Source state
        to_state: Target state

    Example:
        >>> raise StateMachineError("Invalid state transition", from_state="running", to_state="completed")
    """

    def __init__(self, message: str, from_state: str | None = None, to_state: str | None = None, **kwargs: Any) -> None:
        """Initialize a StateMachineError.

        Args:
            message: Error message
            from_state: Source state
            to_state: Target state
            **kwargs: Additional details

        Example:
            >>> raise StateMachineError("Invalid state transition", from_state="running", to_state="completed")
        """
        details = {"from_state": from_state, "to_state": to_state, **kwargs}
        super().__init__(message, details)
        self.from_state = from_state
        self.to_state = to_state


class EventError(RuntimeErrorError):
    """Exception for event errors.

    Raised when an event operation fails.

    Attributes:
        event_id: Event identifier

    Example:
        >>> raise EventError("Event dispatch failed", event_id="event_123")
    """

    def __init__(self, message: str, event_id: str | None = None, **kwargs: Any) -> None:
        """Initialize an EventError.

        Args:
            message: Error message
            event_id: Event identifier
            **kwargs: Additional details

        Example:
            >>> raise EventError("Event dispatch failed", event_id="event_123")
        """
        details = {"event_id": event_id, **kwargs}
        super().__init__(message, details)
        self.event_id = event_id


# Export
__all__ = [
    "RuntimeError",
    "ExecutionError",
    "TaskError",
    "JobError",
    "WorkflowError",
    "PipelineError",
    "ResourceError",
    "ResourceAllocationError",
    "ResourceExhaustionError",
    "ConfigurationError",
    "ValidationError",
    "PluginError",
    "PluginLoadError",
    "PluginDependencyError",
    "TimeoutError",
    "CancellationError",
    "StateMachineError",
    "EventError",
]
