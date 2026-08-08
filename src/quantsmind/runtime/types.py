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
import uuid
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
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
ConfigValue = Union[str, int, float, bool, List[Any], Dict[str, Any]]
ConfigDict = Dict[str, ConfigValue]

# Execution results
Result = Any
SuccessResult = Result
FailureResult = Result
ExecutionResult = Union[SuccessResult, FailureResult]

# Resources
ResourceAmount = Union[int, float]
ResourceCapacity = ResourceAmount
ResourceAllocation = Dict[ResourceID, ResourceAmount]

# Events
EventData = Dict[str, Any]
EventPayload = Dict[str, Any]

# Callbacks
Callback = Callable[..., Any]
EventCallback = Callable[[EventData], None]
TaskCallback = Callable[[ExecutionResult], None]
ProgressCallback = Callable[[float], None]

# Metrics
MetricValue = Union[int, float]
MetricDict = Dict[str, MetricValue]
Metrics = MetricDict

# Telemetry
TelemetryData = Dict[str, Any]
TelemetryPoint = Tuple[Timestamp, TelemetryData]

# State
State = str
StateTransition = Tuple[State, State]

# Plugin
PluginVersion = str
PluginCapability = str
PluginCapabilities = List[PluginCapability]

# Cache
CacheKey = str
CacheValue = Any
CacheEntry = Tuple[CacheValue, Timestamp]

# Serialization
SerializedData = bytes
SerializationFormat = str

# Validation
ValidationResult = Tuple[bool, List[str]]
ValidationErrors = List[str]

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
