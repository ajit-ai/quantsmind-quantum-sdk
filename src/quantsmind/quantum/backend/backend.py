"""
Backend Module

This module provides backend definitions for the Quantum package.

Purpose
-------
Provide backend management for quantum computing operations.

Responsibilities
----------------
- Define backend structure
- Support backend operations
- Support backend validation
- Support backend metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.interfaces (quantum interfaces)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.quantum.algorithms.enums import BackendType
from quantsmind.quantum.algorithms.exceptions import BackendError
from quantsmind.quantum.algorithms.interfaces import IQuantumBackend
from quantsmind.quantum.algorithms.types import BackendConfig, ValidationResult
from quantsmind.quantum.circuit.circuit import QuantumCircuit


class QuantumBackend(IQuantumBackend):
    """Concrete implementation of a quantum backend.

    This class provides backend functionality for quantum computing.

    Attributes:
        _name: Backend name
        _backend_type: Backend type
        _num_qubits: Number of qubits
        _configuration: Backend configuration
        _metadata: Backend metadata

    Example:
        >>> backend = QuantumBackend("simulator", BackendType.SIMULATOR, 5)
        >>> result = backend.run(circuit, shots=1024)
    """

    def __init__(
        self,
        name: str,
        backend_type: BackendType,
        num_qubits: int,
        configuration: Optional[BackendConfig] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a QuantumBackend.

        Args:
            name: Backend name
            backend_type: Backend type
            num_qubits: Number of qubits
            configuration: Backend configuration
            metadata: Backend metadata

        Example:
            >>> backend = QuantumBackend("simulator", BackendType.SIMULATOR, 5)
        """
        if not name:
            raise BackendError("Backend name cannot be empty", {"name": name})

        if num_qubits <= 0:
            raise BackendError("Number of qubits must be positive", {"num_qubits": num_qubits})

        self._name = name
        self._backend_type = backend_type
        self._num_qubits = num_qubits
        self._configuration = configuration or {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the backend name.

        Returns:
            Backend name

        Example:
            >>> name = backend.name
        """
        return self._name

    @property
    def backend_type(self) -> BackendType:
        """Get the backend type.

        Returns:
            Backend type

        Example:
            >>> btype = backend.backend_type
        """
        return self._backend_type

    @property
    def num_qubits(self) -> int:
        """Get the number of available qubits.

        Returns:
            Number of qubits

        Example:
            >>> n = backend.num_qubits
        """
        return self._num_qubits

    @property
    def configuration(self) -> BackendConfig:
        """Get the backend configuration.

        Returns:
            Backend configuration

        Example:
            >>> config = backend.configuration
        """
        return self._configuration.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the backend metadata.

        Returns:
            Backend metadata

        Example:
            >>> metadata = backend.metadata
        """
        return self._metadata.copy()

    def configure(self, config: BackendConfig) -> None:
        """Configure the backend.

        Args:
            config: Backend configuration

        Example:
            >>> backend.configure({"optimization_level": 2})
        """
        self._configuration.update(config)

    def run(self, circuit: QuantumCircuit, shots: int = 1024) -> Dict[str, Any]:
        """Run a circuit on the backend.

        Args:
            circuit: Circuit to run
            shots: Number of shots

        Returns:
            Job result

        Example:
            >>> result = backend.run(circuit, shots=1000)
        """
        if circuit.num_qubits > self._num_qubits:
            raise BackendError(f"Circuit requires {circuit.num_qubits} qubits, backend has {self._num_qubits}", {"circuit_qubits": circuit.num_qubits, "backend_qubits": self._num_qubits})

        # Placeholder implementation - actual execution requires simulation or provider connection
        return {
            "backend": self._name,
            "shots": shots,
            "circuit": circuit.name,
            "status": "completed",
            "counts": {},
        }

    def validate(self) -> ValidationResult:
        """Validate the backend.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = backend.validate()
        """
        errors = []

        if not self._name:
            errors.append("Backend name cannot be empty")

        if self._num_qubits <= 0:
            errors.append("Number of qubits must be positive")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Backend definition

        Example:
            >>> data = backend.to_dict()
        """
        return {
            "name": self._name,
            "backend_type": self._backend_type.value,
            "num_qubits": self._num_qubits,
            "configuration": self._configuration,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(backend)
        """
        return f"QuantumBackend(name={self._name}, type={self._backend_type.value}, qubits={self._num_qubits})"
