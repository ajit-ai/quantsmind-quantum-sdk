"""
Quantum Exceptions Module

This module provides exception definitions for the Quantum package.

Purpose
-------
Provide comprehensive exception hierarchy for quantum computing operations.

Responsibilities
----------------
- Define quantum-specific exceptions
- Support exception chaining
- Provide detailed error context

Dependencies
------------
quantsmind.foundation.exceptions (foundation exceptions)
"""

from __future__ import annotations

from quantsmind.foundation.exceptions import QuantsMindError


class QuantumError(QuantsMindError):
    """Base exception for quantum computing errors.

    This is the root exception for all quantum-related errors.

    Attributes:
        message: Error message
        context: Error context dictionary

    Example:
        >>> raise QuantumError("Quantum operation failed", {"operation": "gate"})
    """

    def __init__(self, message: str, context: dict | None = None) -> None:
        """Initialize a QuantumError.

        Args:
            message: Error message
            context: Error context

        Example:
            >>> raise QuantumError("Quantum operation failed", {"operation": "gate"})
        """
        super().__init__(message, context)
        self.message = message
        self.context = context or {}


class QubitError(QuantumError):
    """Exception for qubit-related errors.

    Example:
        >>> raise QubitError("Qubit index out of range", {"index": 5, "max": 3})
    """

    pass


class GateError(QuantumError):
    """Exception for gate-related errors.

    Example:
        >>> raise GateError("Invalid gate parameters", {"gate": "H", "params": None})
    """

    pass


class CircuitError(QuantumError):
    """Exception for circuit-related errors.

    Example:
        >>> raise CircuitError("Circuit validation failed", {"circuit": "bell_state"})
    """

    pass


class StateError(QuantumError):
    """Exception for quantum state-related errors.

    Example:
        >>> raise StateError("State vector not normalized", {"norm": 1.5})
    """

    pass


class MeasurementError(QuantumError):
    """Exception for measurement-related errors.

    Example:
        >>> raise MeasurementError("Measurement basis invalid", {"basis": "X"})
    """

    pass


class BackendError(QuantumError):
    """Exception for backend-related errors.

    Example:
        >>> raise BackendError("Backend not available", {"backend": "ibmq_manila"})
    """

    pass


class ProviderError(QuantumError):
    """Exception for provider-related errors.

    Example:
        >>> raise ProviderError("Provider authentication failed", {"provider": "IBM"})
    """

    pass


class CompilerError(QuantumError):
    """Exception for compiler-related errors.

    Example:
        >>> raise CompilerError("Transpilation failed", {"circuit": "grover"})
    """

    pass


class ExecutionError(QuantumError):
    """Exception for execution-related errors.

    Example:
        >>> raise ExecutionError("Job execution failed", {"job_id": "job_001"})
    """

    pass


class NoiseError(QuantumError):
    """Exception for noise model-related errors.

    Example:
        >>> raise NoiseError("Invalid noise parameters", {"noise_type": "bit_flip"})
    """

    pass


class AlgorithmError(QuantumError):
    """Exception for algorithm-related errors.

    Example:
        >>> raise AlgorithmError("Algorithm initialization failed", {"algorithm": "QAOA"})
    """

    pass


class ParameterError(QuantumError):
    """Exception for parameter-related errors.

    Example:
        >>> raise ParameterError("Invalid parameter value", {"parameter": "theta", "value": "invalid"})
    """

    pass


class ValidationError(QuantumError):
    """Exception for validation-related errors.

    Example:
        >>> raise ValidationError("Validation failed", {"field": "qubit_count"})
    """

    pass


class SerializationError(QuantumError):
    """Exception for serialization-related errors.

    Example:
        >>> raise SerializationError("Circuit serialization failed", {"format": "qasm"})
    """

    pass


# Export
__all__ = [
    "QuantumError",
    "QubitError",
    "GateError",
    "CircuitError",
    "StateError",
    "MeasurementError",
    "BackendError",
    "ProviderError",
    "CompilerError",
    "ExecutionError",
    "NoiseError",
    "AlgorithmError",
    "ParameterError",
    "ValidationError",
    "SerializationError",
]
