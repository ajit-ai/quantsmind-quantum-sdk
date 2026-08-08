"""
Execution Context Module

This module provides execution context definitions for the Quantum package.

Purpose
-------
Provide execution context management for quantum computing operations.

Responsibilities
----------------
- Define execution context structure
- Support execution context operations
- Support execution context validation
- Support execution context metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.backend.backend (backend module)
quantsmind.quantum.circuit.circuit (circuit module)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.quantum.algorithms.exceptions import ExecutionError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.backend.backend import QuantumBackend
from quantsmind.quantum.circuit.circuit import QuantumCircuit


class ExecutionContext:
    """Concrete implementation of a quantum execution context.

    This class provides execution context functionality for quantum computing.

    Attributes:
        _name: Context name
        _circuit: Circuit to execute
        _backend: Target backend
        _shots: Number of shots
        _configuration: Execution configuration
        _metadata: Context metadata

    Example:
        >>> context = ExecutionContext("bell_state", circuit, backend, shots=1024)
    """

    def __init__(
        self,
        name: str,
        circuit: QuantumCircuit,
        backend: QuantumBackend,
        shots: int = 1024,
        configuration: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an ExecutionContext.

        Args:
            name: Context name
            circuit: Circuit to execute
            backend: Target backend
            shots: Number of shots
            configuration: Execution configuration
            metadata: Context metadata

        Example:
            >>> context = ExecutionContext("bell_state", circuit, backend, shots=1024)
        """
        if not name:
            raise ExecutionError("Context name cannot be empty", {"name": name})

        if circuit is None:
            raise ExecutionError("Circuit cannot be None", {"circuit": None})

        if backend is None:
            raise ExecutionError("Backend cannot be None", {"backend": None})

        if shots <= 0:
            raise ExecutionError("Shots must be positive", {"shots": shots})

        self._name = name
        self._circuit = circuit
        self._backend = backend
        self._shots = shots
        self._configuration = configuration or {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the context name.

        Returns:
            Context name

        Example:
            >>> name = context.name
        """
        return self._name

    @property
    def circuit(self) -> QuantumCircuit:
        """Get the circuit.

        Returns:
            Circuit

        Example:
            >>> circuit = context.circuit
        """
        return self._circuit

    @property
    def backend(self) -> QuantumBackend:
        """Get the backend.

        Returns:
            Backend

        Example:
            >>> backend = context.backend
        """
        return self._backend

    @property
    def shots(self) -> int:
        """Get the number of shots.

        Returns:
            Number of shots

        Example:
            >>> shots = context.shots
        """
        return self._shots

    @property
    def configuration(self) -> Dict[str, Any]:
        """Get the execution configuration.

        Returns:
            Execution configuration

        Example:
            >>> config = context.configuration
        """
        return self._configuration.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the context metadata.

        Returns:
            Context metadata

        Example:
            >>> metadata = context.metadata
        """
        return self._metadata.copy()

    def set_circuit(self, circuit: QuantumCircuit) -> None:
        """Set the circuit.

        Args:
            circuit: Circuit to execute

        Example:
            >>> context.set_circuit(circuit)
        """
        if circuit is None:
            raise ExecutionError("Circuit cannot be None", {"circuit": None})

        self._circuit = circuit

    def set_backend(self, backend: QuantumBackend) -> None:
        """Set the backend.

        Args:
            backend: Target backend

        Example:
            >>> context.set_backend(backend)
        """
        if backend is None:
            raise ExecutionError("Backend cannot be None", {"backend": None})

        self._backend = backend

    def set_shots(self, shots: int) -> None:
        """Set the number of shots.

        Args:
            shots: Number of shots

        Example:
            >>> context.set_shots(2048)
        """
        if shots <= 0:
            raise ExecutionError("Shots must be positive", {"shots": shots})

        self._shots = shots

    def validate(self) -> ValidationResult:
        """Validate the execution context.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = context.validate()
        """
        errors = []

        if not self._name:
            errors.append("Context name cannot be empty")

        if self._circuit is None:
            errors.append("Circuit cannot be None")

        if self._backend is None:
            errors.append("Backend cannot be None")

        if self._shots <= 0:
            errors.append("Shots must be positive")

        # Validate circuit
        if self._circuit:
            is_valid, circuit_errors = self._circuit.validate()
            errors.extend(circuit_errors)

        # Validate backend
        if self._backend:
            is_valid, backend_errors = self._backend.validate()
            errors.extend(backend_errors)

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Execution context definition

        Example:
            >>> data = context.to_dict()
        """
        return {
            "name": self._name,
            "circuit": self._circuit.name,
            "backend": self._backend.name,
            "shots": self._shots,
            "configuration": self._configuration,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(context)
        """
        return f"ExecutionContext(name={self._name}, circuit={self._circuit.name}, backend={self._backend.name})"
