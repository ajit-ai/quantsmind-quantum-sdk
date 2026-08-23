"""
Runtime Enums Module

This module provides enumerations for the Runtime package.

Purpose
-------
Provide runtime enumerations for the QuantsMind SDK.

Responsibilities
----------------
- Define execution states
- Define resource types
- Define task priorities
- Define event types
- Define plugin states

Dependencies
------------
enum (standard library)
typing (standard library)
"""

from __future__ import annotations

import enum


class ExecutionState(enum.Enum):
    """Execution state enumeration.

    Represents the lifecycle states of executable objects.

    Attributes:
        CREATED: Object has been created
        INITIALIZED: Object has been initialized
        VALIDATED: Object has been validated
        QUEUED: Object is queued for execution
        RUNNING: Object is currently running
        PAUSED: Object execution is paused
        COMPLETED: Object execution completed successfully
        FAILED: Object execution failed
        CANCELLED: Object execution was cancelled
        ARCHIVED: Object has been archived
        DESTROYED: Object has been destroyed
    """

    CREATED = "created"
    INITIALIZED = "initialized"
    VALIDATED = "validated"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    DESTROYED = "destroyed"


class ResourceType(enum.Enum):
    """Resource type enumeration.

    Represents different types of computational resources.

    Attributes:
        CPU: CPU resource
        GPU: GPU resource
        QUANTUM: Quantum device resource
        MEMORY: Memory resource
        STORAGE: Storage resource
        NETWORK: Network resource
        CLOUD: Cloud resource
        EDGE: Edge resource
    """

    CPU = "cpu"
    GPU = "gpu"
    QUANTUM = "quantum"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    CLOUD = "cloud"
    EDGE = "edge"


class TaskPriority(enum.Enum):
    """Task priority enumeration.

    Represents priority levels for task scheduling.

    Attributes:
        LOW: Low priority
        NORMAL: Normal priority
        HIGH: High priority
        CRITICAL: Critical priority
    """

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class EventType(enum.Enum):
    """Event type enumeration.

    Represents different types of runtime events.

    Attributes:
        SESSION_STARTED: Session started event
        SESSION_CLOSED: Session closed event
        TASK_SUBMITTED: Task submitted event
        TASK_STARTED: Task started event
        TASK_COMPLETED: Task completed event
        TASK_CANCELLED: Task cancelled event
        JOB_STARTED: Job started event
        WORKFLOW_COMPLETED: Workflow completed event
        PIPELINE_FAILED: Pipeline failed event
        RESOURCE_ALLOCATED: Resource allocated event
        RESOURCE_RELEASED: Resource released event
        PLUGIN_LOADED: Plugin loaded event
        PLUGIN_UNLOADED: Plugin unloaded event
    """

    SESSION_STARTED = "session_started"
    SESSION_CLOSED = "session_closed"
    TASK_SUBMITTED = "task_submitted"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_CANCELLED = "task_cancelled"
    JOB_STARTED = "job_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    PIPELINE_FAILED = "pipeline_failed"
    RESOURCE_ALLOCATED = "resource_allocated"
    RESOURCE_RELEASED = "resource_released"
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_UNLOADED = "plugin_unloaded"


class PluginState(enum.Enum):
    """Plugin state enumeration.

    Represents the lifecycle states of plugins.

    Attributes:
        UNLOADED: Plugin is unloaded
        LOADING: Plugin is loading
        LOADED: Plugin is loaded
        ACTIVE: Plugin is active
        INACTIVE: Plugin is inactive
        UNLOADING: Plugin is unloading
        ERROR: Plugin is in error state
    """

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNLOADING = "unloading"
    ERROR = "error"


class LogLevel(enum.Enum):
    """Log level enumeration.

    Represents different logging levels.

    Attributes:
        DEBUG: Debug level
        INFO: Info level
        WARNING: Warning level
        ERROR: Error level
        CRITICAL: Critical level
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RetryPolicy(enum.Enum):
    """Retry policy enumeration.

    Represents different retry policies for failed tasks.

    Attributes:
        NONE: No retry
        FIXED: Fixed delay between retries
        EXPONENTIAL: Exponential backoff
        LINEAR: Linear backoff
    """

    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


class ExecutionMode(enum.Enum):
    """Execution mode enumeration.

    Represents different execution modes.

    Attributes:
        SYNCHRONOUS: Synchronous execution
        ASYNCHRONOUS: Asynchronous execution
        PARALLEL: Parallel execution
        DISTRIBUTED: Distributed execution
    """

    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"


class CachePolicy(enum.Enum):
    """Cache policy enumeration.

    Represents different cache policies.

    Attributes:
        NONE: No caching
        LRU: Least recently used
        LFU: Least frequently used
        FIFO: First in first out
        TTL: Time to live
    """

    NONE = "none"
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"


# Export
__all__ = [
    "ExecutionState",
    "ResourceType",
    "TaskPriority",
    "EventType",
    "PluginState",
    "LogLevel",
    "RetryPolicy",
    "ExecutionMode",
    "CachePolicy",
]
