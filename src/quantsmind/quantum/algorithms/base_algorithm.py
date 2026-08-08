"""
Base Algorithm Module

This module provides base algorithm definitions for the Quantum package.

Purpose
-------
Provide base algorithm management for quantum computing operations.

Responsibilities
----------------
- Define base algorithm structure
- Support base algorithm operations
- Support base algorithm validation
- Support base algorithm metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.circuit.circuit (circuit module)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from quantsmind.quantum.algorithms.exceptions import AlgorithmError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.circuit.circuit import QuantumCircuit


class BaseAlgorithm:
    """Concrete implementation of a base quantum algorithm.

    This class provides base algorithm functionality for quantum computing.
    This is an abstract base class for specific quantum algorithms.

    Attributes:
        _name: Algorithm name
        _num_qubits: Number of qubits
        _parameters: Algorithm parameters
        _circuit: Algorithm circuit
        _metadata: Algorithm metadata

    Example:
        >>> algorithm = BaseAlgorithm("custom", 2)
        >>> circuit = algorithm.build_circuit()
    """

    def __init__(
        self,
        name: str,
        num_qubits: int,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a BaseAlgorithm.

        Args:
            name: Algorithm name
            num_qubits: Number of qubits
            parameters: Algorithm parameters
            metadata: Algorithm metadata

        Example:
            >>> algorithm = BaseAlgorithm("custom", 2)
        """
        if not name:
            raise AlgorithmError("Algorithm name cannot be empty", {"name": name})

        if num_qubits <= 0:
            raise AlgorithmError("Number of qubits must be positive", {"num_qubits": num_qubits})

        self._name = name
        self._num_qubits = num_qubits
        self._parameters = parameters or {}
        self._circuit: Optional[QuantumCircuit] = None
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the algorithm name.

        Returns:
            Algorithm name

        Example:
            >>> name = algorithm.name
        """
        return self._name

    @property
    def num_qubits(self) -> int:
        """Get the number of qubits.

        Returns:
            Number of qubits

        Example:
            >>> n = algorithm.num_qubits
        """
        return self._num_qubits

    @property
    def parameters(self) -> Dict[str, Any]:
        """Get the algorithm parameters.

        Returns:
            Algorithm parameters

        Example:
            >>> params = algorithm.parameters
        """
        return self._parameters.copy()

    @property
    def circuit(self) -> Optional[QuantumCircuit]:
        """Get the algorithm circuit.

        Returns:
            Algorithm circuit

        Example:
            >>> circuit = algorithm.circuit
        """
        return self._circuit

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the algorithm metadata.

        Returns:
            Algorithm metadata

        Example:
            >>> metadata = algorithm.metadata
        """
        return self._metadata.copy()

    def set_parameter(self, key: str, value: Any) -> None:
        """Set an algorithm parameter.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> algorithm.set_parameter("iterations", 10)
        """
        self._parameters[key] = value

    def get_parameter(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """Get an algorithm parameter.

        Args:
            key: Parameter key
            default: Default value

        Returns:
            Parameter value or default

        Example:
            >>> iterations = algorithm.get_parameter("iterations", 1)
        """
        return self._parameters.get(key, default)

    def build_circuit(self) -> QuantumCircuit:
        """Build the algorithm circuit.

        Returns:
            Algorithm circuit

        Example:
            >>> circuit = algorithm.build_circuit()
        """
        # Placeholder implementation - should be overridden by subclasses
        self._circuit = QuantumCircuit(f"{self._name}_circuit", self._num_qubits, self._metadata.copy())
        return self._circuit

    def validate(self) -> ValidationResult:
        """Validate the algorithm.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = algorithm.validate()
        """
        errors = []

        if not self._name:
            errors.append("Algorithm name cannot be empty")

        if self._num_qubits <= 0:
            errors.append("Number of qubits must be positive")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Algorithm definition

        Example:
            >>> data = algorithm.to_dict()
        """
        return {
            "name": self._name,
            "num_qubits": self._num_qubits,
            "parameters": self._parameters,
            "has_circuit": self._circuit is not None,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(algorithm)
        """
        return f"BaseAlgorithm(name={self._name}, num_qubits={self._num_qubits})"
