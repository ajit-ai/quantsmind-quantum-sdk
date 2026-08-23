"""
Gate Module

This module provides gate definitions for the Quantum package.

Purpose
-------
Provide gate management for quantum computing operations.

Responsibilities
----------------
- Define gate structure
- Support gate operations
- Support gate validation
- Support gate metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.interfaces (quantum interfaces)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.exceptions import GateError
from quantsmind.quantum.algorithms.interfaces import IQuantumGate
from quantsmind.quantum.algorithms.types import GateParameters, ValidationResult


class QuantumGate(IQuantumGate):
    """Concrete implementation of a quantum gate.

    This class provides gate functionality for quantum computing.

    Attributes:
        _name: Gate name
        _gate_type: Gate type
        _num_qubits: Number of qubits
        _parameters: Gate parameters
        _matrix: Unitary matrix
        _metadata: Gate metadata

    Example:
        >>> gate = QuantumGate("H", GateType.SINGLE_QUBIT, 1)
    """

    def __init__(
        self,
        name: str,
        gate_type: str,
        num_qubits: int,
        parameters: GateParameters | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a QuantumGate.

        Args:
            name: Gate name
            gate_type: Gate type
            num_qubits: Number of qubits
            parameters: Gate parameters
            metadata: Gate metadata

        Example:
            >>> gate = QuantumGate("H", GateType.SINGLE_QUBIT, 1)
        """
        if not name:
            raise GateError("Gate name cannot be empty", {"name": name})

        if num_qubits <= 0:
            raise GateError("Number of qubits must be positive", {"num_qubits": num_qubits})

        self._name = name
        self._gate_type = gate_type
        self._num_qubits = num_qubits
        self._parameters = parameters or {}
        self._matrix: list[list[complex]] | None = None
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the gate name.

        Returns:
            Gate name

        Example:
            >>> name = gate.name
        """
        return self._name

    @property
    def gate_type(self) -> str:
        """Get the gate type.

        Returns:
            Gate type

        Example:
            >>> gtype = gate.gate_type
        """
        return self._gate_type

    @property
    def num_qubits(self) -> int:
        """Get the number of qubits the gate operates on.

        Returns:
            Number of qubits

        Example:
            >>> n = gate.num_qubits
        """
        return self._num_qubits

    @property
    def parameters(self) -> GateParameters:
        """Get the gate parameters.

        Returns:
            Gate parameters

        Example:
            >>> params = gate.parameters
        """
        return self._parameters.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the gate metadata.

        Returns:
            Gate metadata

        Example:
            >>> metadata = gate.metadata
        """
        return self._metadata.copy()

    def set_matrix(self, matrix: list[list[complex]]) -> None:
        """Set the unitary matrix.

        Args:
            matrix: Unitary matrix

        Example:
            >>> gate.set_matrix([[1, 0], [0, 1]])
        """
        expected_size = 2 ** self._num_qubits
        if len(matrix) != expected_size:
            raise GateError(f"Matrix rows {len(matrix)} does not match expected size {expected_size}", {"num_qubits": self._num_qubits})

        for row in matrix:
            if len(row) != expected_size:
                raise GateError(f"Matrix columns {len(row)} does not match expected size {expected_size}", {"num_qubits": self._num_qubits})

        self._matrix = matrix

    def set_parameter(self, key: str, value: float) -> None:
        """Set a parameter.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> gate.set_parameter("theta", 1.57)
        """
        self._parameters[key] = value

    def get_matrix(self) -> list[list[complex]]:
        """Get the unitary matrix representation.

        Returns:
            Unitary matrix

        Example:
            >>> matrix = gate.get_matrix()
        """
        if self._matrix is None:
            raise GateError("Gate matrix not set", {"name": self._name})
        return [row.copy() for row in self._matrix]

    def get_parameter(self, key: str, default: float | None = None) -> float | None:
        """Get a parameter.

        Args:
            key: Parameter key
            default: Default value

        Returns:
            Parameter value or default

        Example:
            >>> theta = gate.get_parameter("theta", 0.0)
        """
        return self._parameters.get(key, default)

    def validate(self) -> ValidationResult:
        """Validate the gate.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = gate.validate()
        """
        errors = []

        if not self._name:
            errors.append("Gate name cannot be empty")

        if self._num_qubits <= 0:
            errors.append("Number of qubits must be positive")

        if self._matrix is None:
            errors.append("Gate matrix not set")
        else:
            expected_size = 2 ** self._num_qubits
            if len(self._matrix) != expected_size:
                errors.append(f"Matrix rows {len(self._matrix)} does not match expected size {expected_size}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Gate definition

        Example:
            >>> data = gate.to_dict()
        """
        return {
            "name": self._name,
            "gate_type": self._gate_type,
            "num_qubits": self._num_qubits,
            "parameters": self._parameters,
            "has_matrix": self._matrix is not None,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(gate)
        """
        return f"QuantumGate(name={self._name}, type={self._gate_type}, num_qubits={self._num_qubits})"


# Export
__all__ = [
    "QuantumGate",
]
