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

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

try:
    import numpy as np
    from numpy.typing import NDArray
except ImportError:
    # Fallback for environments without numpy
    NDArray = Any
    np = None

# Type aliases
QubitIndex = int
QubitIndices = List[QubitIndex]
GateParameters = Dict[str, float]
StateVector = NDArray
DensityMatrix = NDArray
ComplexMatrix = NDArray
ProbabilityDistribution = List[float]
MeasurementResult = Dict[int, int]
CircuitDepth = int
GateCount = int
QubitCount = int

# Function types
GateFunction = Callable[[Any], Any]
MeasurementFunction = Callable[[Any], MeasurementResult]
OptimizationFunction = Callable[[Any], float]
CompilerPass = Callable[[Any], Any]

# Result types
ValidationResult = Tuple[bool, List[str]]
ExecutionResult = Dict[str, Any]
JobResult = Dict[str, Any]

# Configuration types
BackendConfig = Dict[str, Any]
ProviderConfig = Dict[str, Any]
NoiseConfig = Dict[str, Any]
CompilerConfig = Dict[str, Any]

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
