"""
Operator Module

This module provides operator definitions for the Quantum package.

Purpose
-------
Provide operator management for quantum computing operations.

Responsibilities
----------------
- Define operator structure
- Support operator operations
- Support operator validation
- Support operator metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.quantum.algorithms.exceptions import CircuitError
from quantsmind.quantum.algorithms.types import ValidationResult


class QuantumOperator:
    """Concrete implementation of a quantum operator.

    This class provides operator functionality for quantum computing.

    Attributes:
        _name: Operator name
        _num_qubits: Number of qubits
        _matrix: Operator matrix
        _metadata: Operator metadata

    Example:
        >>> operator = QuantumOperator("X", 1)
    """

    def __init__(
        self,
        name: str,
        num_qubits: int,
        matrix: Optional[List[List[complex]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a QuantumOperator.

        Args:
            name: Operator name
            num_qubits: Number of qubits
            matrix: Operator matrix
            metadata: Operator metadata

        Example:
            >>> operator = QuantumOperator("X", 1)
        """
        if not name:
            raise CircuitError("Operator name cannot be empty", {"name": name})

        if num_qubits <= 0:
            raise CircuitError("Number of qubits must be positive", {"num_qubits": num_qubits})

        self._name = name
        self._num_qubits = num_qubits
        self._matrix = matrix
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the operator name.

        Returns:
            Operator name

        Example:
            >>> name = operator.name
        """
        return self._name

    @property
    def num_qubits(self) -> int:
        """Get the number of qubits.

        Returns:
            Number of qubits

        Example:
            >>> n = operator.num_qubits
        """
        return self._num_qubits

    @property
    def matrix(self) -> List[List[complex]]:
        """Get the operator matrix.

        Returns:
            Operator matrix

        Example:
            >>> matrix = operator.matrix
        """
        return [row.copy() for row in self._matrix] if self._matrix else []

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the operator metadata.

        Returns:
            Operator metadata

        Example:
            >>> metadata = operator.metadata
        """
        return self._metadata.copy()

    def set_matrix(self, matrix: List[List[complex]]) -> None:
        """Set the operator matrix.

        Args:
            matrix: Operator matrix

        Example:
            >>> operator.set_matrix([[1, 0], [0, 1]])
        """
        expected_size = 2 ** self._num_qubits
        if len(matrix) != expected_size:
            raise CircuitError(f"Matrix rows {len(matrix)} does not match expected size {expected_size}", {"num_qubits": self._num_qubits})

        for row in matrix:
            if len(row) != expected_size:
                raise CircuitError(f"Matrix columns {len(row)} does not match expected size {expected_size}", {"num_qubits": self._num_qubits})

        self._matrix = matrix

    def get_element(self, row: int, col: int) -> complex:
        """Get a matrix element.

        Args:
            row: Row index
            col: Column index

        Returns:
            Matrix element

        Example:
            >>> elem = operator.get_element(0, 0)
        """
        if self._matrix is None:
            raise CircuitError("Matrix not set", {"name": self._name})

        size = 2 ** self._num_qubits
        if row < 0 or row >= size or col < 0 or col >= size:
            raise CircuitError(f"Matrix indices ({row}, {col}) out of range", {"size": size})

        return self._matrix[row][col]

    def validate(self) -> ValidationResult:
        """Validate the operator.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = operator.validate()
        """
        errors = []

        if not self._name:
            errors.append("Operator name cannot be empty")

        if self._num_qubits <= 0:
            errors.append("Number of qubits must be positive")

        if self._matrix is None:
            errors.append("Matrix not set")
        else:
            expected_size = 2 ** self._num_qubits
            if len(self._matrix) != expected_size:
                errors.append(f"Matrix rows {len(self._matrix)} does not match expected size {expected_size}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Operator definition

        Example:
            >>> data = operator.to_dict()
        """
        return {
            "name": self._name,
            "num_qubits": self._num_qubits,
            "has_matrix": self._matrix is not None,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(operator)
        """
        return f"QuantumOperator(name={self._name}, num_qubits={self._num_qubits})"


# Export
__all__ = [
    "QuantumOperator",
]
