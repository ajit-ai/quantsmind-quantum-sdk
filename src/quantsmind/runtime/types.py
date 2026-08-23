"""
Runtime Types Module

This module provides type definitions for the Runtime package.

Purpose
-------
Provide type definitions for the QuantsMind SDK.

Responsibilities
----------------
- Define type aliases for runtime objects
- Define type aliases for execution results
- Define type aliases for resources
- Define type aliases for events

Dependencies
------------
typing (standard library)
datetime (standard library)
uuid (standard library)
"""

from __future__ import annotations

import datetime
from collections.abc import Callable
from typing import (
    Any,
    TypeVar,
    Union,
)

# Generic type variables
T = TypeVar("T")
R = TypeVar("R")
K = TypeVar("K")
V = TypeVar("V")

# Identifiers
SessionID = str
TaskID = str
JobID = str
WorkflowID = str
PipelineID = str
ResourceID = str
PluginID = str
EventID = str
ExecutionID = str

# Timestamps
Timestamp = datetime.datetime
TimeDelta = datetime.timedelta

# Configuration
ConfigValue = Union[str, int, float, bool, list[Any], dict[str, Any]]
ConfigDict = dict[str, ConfigValue]

# Execution results
Result = Any
SuccessResult = Result
FailureResult = Result
ExecutionResult = Union[SuccessResult, FailureResult]

# Resources
ResourceAmount = Union[int, float]
ResourceCapacity = ResourceAmount
ResourceAllocation = dict[ResourceID, ResourceAmount]

# Events
EventData = dict[str, Any]
EventPayload = dict[str, Any]

# Callbacks
Callback = Callable[..., Any]
EventCallback = Callable[[EventData], None]
TaskCallback = Callable[[ExecutionResult], None]
ProgressCallback = Callable[[float], None]

# Metrics
MetricValue = Union[int, float]
MetricDict = dict[str, MetricValue]
Metrics = MetricDict

# Telemetry
TelemetryData = dict[str, Any]
TelemetryPoint = tuple[Timestamp, TelemetryData]

# State
State = str
StateTransition = tuple[State, State]

# Plugin
PluginVersion = str
PluginCapability = str
PluginCapabilities = list[PluginCapability]

# Cache
CacheKey = str
CacheValue = Any
CacheEntry = tuple[CacheValue, Timestamp]

# Serialization
SerializedData = bytes
SerializationFormat = str

# Validation
ValidationResult = tuple[bool, list[str]]
ValidationErrors = list[str]

# Retry
RetryCount = int
RetryDelay = float

# Priority
Priority = int

# Timeout
Timeout = float

# Queue
QueueSize = int

# Memory
MemorySize = int

# Storage
StorageSize = int

# Network
Bandwidth = float
Latency = float

# Export
__all__ = [
    # Type variables
    "T",
    "R",
    "K",
    "V",
    # Identifiers
    "SessionID",
    "TaskID",
    "JobID",
    "WorkflowID",
    "PipelineID",
    "ResourceID",
    "PluginID",
    "EventID",
    "ExecutionID",
    # Timestamps
    "Timestamp",
    "TimeDelta",
    # Configuration
    "ConfigValue",
    "ConfigDict",
    # Execution results
    "Result",
    "SuccessResult",
    "FailureResult",
    "ExecutionResult",
    # Resources
    "ResourceAmount",
    "ResourceCapacity",
    "ResourceAllocation",
    # Events
    "EventData",
    "EventPayload",
    # Callbacks
    "Callback",
    "EventCallback",
    "TaskCallback",
    "ProgressCallback",
    # Metrics
    "MetricValue",
    "MetricDict",
    "Metrics",
    # Telemetry
    "TelemetryData",
    "TelemetryPoint",
    # State
    "State",
    "StateTransition",
    # Plugin
    "PluginVersion",
    "PluginCapability",
    "PluginCapabilities",
    # Cache
    "CacheKey",
    "CacheValue",
    "CacheEntry",
    # Serialization
    "SerializedData",
    "SerializationFormat",
    # Validation
    "ValidationResult",
    "ValidationErrors",
    # Retry
    "RetryCount",
    "RetryDelay",
    # Priority
    "Priority",
    # Timeout
    "Timeout",
    # Queue
    "QueueSize",
    # Memory
    "MemorySize",
    # Storage
    "StorageSize",
    # Network
    "Bandwidth",
    "Latency",
]
