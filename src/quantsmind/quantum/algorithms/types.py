"""
Quantum Types Module

This module provides type definitions for the Quantum package.

Purpose
-------
Provide comprehensive type definitions for quantum computing operations.

Responsibilities
----------------
- Define quantum-specific types
- Support type hints
- Provide type aliases

Dependencies
------------
typing (standard library)
numpy (external)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Union

try:
    import numpy as np
    from numpy.typing import NDArray
except ImportError:
    # Fallback for environments without numpy
    NDArray = Any
    np = None

# Type aliases
QubitIndex = int
QubitIndices = list[QubitIndex]
GateParameters = dict[str, float]
StateVector = NDArray
DensityMatrix = NDArray
ComplexMatrix = NDArray
ProbabilityDistribution = list[float]
MeasurementResult = dict[int, int]
CircuitDepth = int
GateCount = int
QubitCount = int

# Function types
GateFunction = Callable[[Any], Any]
MeasurementFunction = Callable[[Any], MeasurementResult]
OptimizationFunction = Callable[[Any], float]
CompilerPass = Callable[[Any], Any]

# Result types
ValidationResult = tuple[bool, list[str]]
ExecutionResult = dict[str, Any]
JobResult = dict[str, Any]

# Configuration types
BackendConfig = dict[str, Any]
ProviderConfig = dict[str, Any]
NoiseConfig = dict[str, Any]
CompilerConfig = dict[str, Any]

# Complex types
QuantumState = Union[StateVector, DensityMatrix]
QuantumOperator = Union[ComplexMatrix, Callable]
MeasurementBasis = str

# Export
__all__ = [
    "QubitIndex",
    "QubitIndices",
    "GateParameters",
    "StateVector",
    "DensityMatrix",
    "ComplexMatrix",
    "ProbabilityDistribution",
    "MeasurementResult",
    "CircuitDepth",
    "GateCount",
    "QubitCount",
    "GateFunction",
    "MeasurementFunction",
    "OptimizationFunction",
    "CompilerPass",
    "ValidationResult",
    "ExecutionResult",
    "JobResult",
    "BackendConfig",
    "ProviderConfig",
    "NoiseConfig",
    "CompilerConfig",
    "QuantumState",
    "QuantumOperator",
    "MeasurementBasis",
]
