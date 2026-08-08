"""
Runtime Package — Defines the execution model for QuantsMind: how work described by core
abstractions is scheduled, dispatched, and executed across heterogeneous backends.

This package is part of the QuantsMind SDK (R0.5.0).

Purpose
-------
Provide a unified execution environment for all QuantsMind domain packages including
Mathematics, Quantum Computing, AI, Physics, Chemistry, Biology, Astronomy, Finance,
Simulation, Optimization, and Visualization.

Modules
-------
- constants: Runtime constants and default values
- enums: Runtime enumerations (ExecutionState, ResourceType, TaskPriority, etc.)
- types: Type definitions for runtime objects
- exceptions: Runtime exception hierarchy
- context: Execution context management
- session: Runtime session management
- task: Task execution model
- job: Job management (collection of tasks)
- workflow: Workflow management (conditional execution, parallel execution)
- pipeline: Pipeline management (input, transformation, execution, export)
- executor: Task executor
- scheduler: Task scheduler
- dispatcher: Task dispatcher
- engine: Execution engine
- kernel: Runtime kernel
- resource: Resource management
- resource_manager: Resource manager
- cpu_resource: CPU resource
- gpu_resource: GPU resource
- quantum_resource: Quantum resource
- memory_resource: Memory resource
- storage_resource: Storage resource
- lifecycle: Lifecycle management
- registry: Runtime registry
- plugin_manager: Plugin management
- configuration: Configuration management
- settings: Settings management
- logging: Logging management
- telemetry: Telemetry collection
- metrics: Metrics collection
- monitoring: Monitoring service
- event: Event management
- event_bus: Event bus
- state_machine: State machine
- cache: Cache management
- factories: Factory methods
- validators: Validation functions
- serializers: Serialization functions
- interfaces: Runtime interfaces
- protocols: Runtime protocols
- utils: Utility functions
"""

from __future__ import annotations

__version__ = "R0.5.0"

__all__ = [
    # Foundational modules
    "constants",
    "enums",
    "exceptions",
    "types",
    # Core runtime modules
    "context",
    "session",
    "task",
    "job",
    "workflow",
    "pipeline",
    # Execution modules
    "executor",
    "scheduler",
    "dispatcher",
    "engine",
    "kernel",
    # Resource management modules
    "resource",
    "resource_manager",
    "cpu_resource",
    "gpu_resource",
    "quantum_resource",
    "memory_resource",
    "storage_resource",
    # Lifecycle and registry modules
    "lifecycle",
    "registry",
    # Plugin management
    "plugin_manager",
    # Configuration modules
    "configuration",
    "settings",
    # Observability modules
    "logging",
    "telemetry",
    "metrics",
    "monitoring",
    # Event system
    "event",
    "event_bus",
    # State machine and cache
    "state_machine",
    "cache",
    # Support modules
    "factories",
    "validators",
    "serializers",
    "interfaces",
    "utils",
    "__version__",
]
