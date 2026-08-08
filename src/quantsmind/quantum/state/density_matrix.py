"""
Density Matrix Module

This module provides density matrix definitions for the Quantum package.

Purpose
-------
Provide density matrix management for quantum computing operations.

Responsibilities
----------------
- Define density matrix structure
- Support density matrix operations
- Support density matrix validation
- Support density matrix metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.state.quantum_state (quantum state module)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.quantum.algorithms.exceptions import StateError
from quantsmind.quantum.algorithms.enums import StateType
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.state.quantum_state import QuantumState


class DensityMatrix(QuantumState):
    """Concrete implementation of a density matrix.

    This class provides density matrix functionality for quantum computing.
    Density matrices represent mixed quantum states.

    Attributes:
        _num_qubits: Number of qubits
        _matrix: Density matrix
        _metadata: State metadata

    Example:
        >>> density_matrix = DensityMatrix(1)
        >>> density_matrix.initialize_pure_zero()
    """

    def __init__(
        self,
        num_qubits: int,
        matrix: Optional[List[List[complex]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a DensityMatrix.

        Args:
            num_qubits: Number of qubits
            matrix: Density matrix
            metadata: State metadata

        Example:
            >>> density_matrix = DensityMatrix(1)
        """
        super().__init__(num_qubits, metadata)
        self._matrix = matrix
        self._state_type = StateType.DENSITY_MATRIX

        if matrix is None:
            self.initialize_pure_zero()

    @property
    def matrix(self) -> List[List[complex]]:
        """Get the density matrix.

        Returns:
            Density matrix

        Example:
            >>> mat = density_matrix.matrix
        """
        return [row.copy() for row in self._matrix] if self._matrix else []

    @property
    def state_type(self) -> StateType:
        """Get the state type.

        Returns:
            State type

        Example:
            >>> stype = density_matrix.state_type
        """
        return self._state_type

    def set_matrix(self, matrix: List[List[complex]]) -> None:
        """Set the density matrix.

        Args:
            matrix: Density matrix

        Example:
            >>> density_matrix.set_matrix([[1, 0], [0, 0]])
        """
        expected_size = 2 ** self._num_qubits
        if len(matrix) != expected_size:
            raise StateError(f"Matrix rows {len(matrix)} does not match expected size {expected_size}", {"num_qubits": self._num_qubits})

        for row in matrix:
            if len(row) != expected_size:
                raise StateError(f"Matrix columns {len(row)} does not match expected size {expected_size}", {"num_qubits": self._num_qubits})

        self._matrix = matrix

    def get_element(self, row: int, col: int) -> complex:
        """Get a matrix element.

        Args:
            row: Row index
            col: Column index

        Returns:
            Matrix element

        Example:
            >>> elem = density_matrix.get_element(0, 0)
        """
        if self._matrix is None:
            raise StateError("Matrix not initialized", {"num_qubits": self._num_qubits})

        size = 2 ** self._num_qubits
        if row < 0 or row >= size or col < 0 or col >= size:
            raise StateError(f"Matrix indices ({row}, {col}) out of range", {"size": size})

        return self._matrix[row][col]

    def initialize_pure_zero(self) -> None:
        """Initialize to pure |0⟩ state.

        Example:
            >>> density_matrix.initialize_pure_zero()
        """
        size = 2 ** self._num_qubits
        self._matrix = [[0j] * size for _ in range(size)]
        self._matrix[0][0] = 1.0 + 0j

    def initialize_pure_one(self) -> None:
        """Initialize to pure |1⟩ state.

        Example:
            >>> density_matrix.initialize_pure_one()
        """
        size = 2 ** self._num_qubits
        self._matrix = [[0j] * size for _ in range(size)]
        self._matrix[-1][-1] = 1.0 + 0j

    def initialize_maximally_mixed(self) -> None:
        """Initialize to maximally mixed state.

        Example:
            >>> density_matrix.initialize_maximally_mixed()
        """
        size = 2 ** self._num_qubits
        value = 1.0 / size
        self._matrix = [[value + 0j for _ in range(size)] for _ in range(size)]

    def get_trace(self) -> complex:
        """Get the trace of the density matrix.

        Returns:
            Trace

        Example:
            >>> trace = density_matrix.get_trace()
        """
        if self._matrix is None:
            return 0j

        size = 2 ** self._num_qubits
        return sum(self._matrix[i][i] for i in range(size))

    def get_purity(self) -> float:
        """Get the purity of the density matrix.

        Returns:
            Purity (Tr(ρ²))

        Example:
            >>> purity = density_matrix.get_purity()
        """
        if self._matrix is None:
            return 0.0

        size = 2 ** self._num_qubits
        purity = 0j

        for i in range(size):
            for j in range(size):
                purity += self._matrix[i][j] * self._matrix[j][i]

        return purity.real

    def is_pure(self) -> bool:
        """Check if the state is pure.

        Returns:
            True if pure

        Example:
            >>> pure = density_matrix.is_pure()
        """
        purity = self.get_purity()
        return abs(purity - 1.0) < 1e-6

    def is_mixed(self) -> bool:
        """Check if the state is mixed.

        Returns:
            True if mixed

        Example:
            >>> mixed = density_matrix.is_mixed()
        """
        return not self.is_pure()

    def normalize(self) -> None:
        """Normalize the density matrix.

        Example:
            >>> density_matrix.normalize()
        """
        if self._matrix is None:
            return

        trace = self.get_trace()
        if trace.real > 0:
            size = 2 ** self._num_qubits
            for i in range(size):
                for j in range(size):
                    self._matrix[i][j] /= trace

    def validate(self) -> ValidationResult:
        """Validate the density matrix.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = density_matrix.validate()
        """
        errors = []

        # Validate base state
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if self._matrix is None:
            errors.append("Matrix not initialized")
        else:
            expected_size = 2 ** self._num_qubits
            if len(self._matrix) != expected_size:
                errors.append(f"Matrix rows {len(self._matrix)} does not match expected size {expected_size}")

            for i, row in enumerate(self._matrix):
                if len(row) != expected_size:
                    errors.append(f"Matrix row {i} has {len(row)} columns, expected {expected_size}")

            # Check trace = 1
            trace = self.get_trace()
            if abs(trace - 1.0) > 1e-6:
                errors.append(f"Density matrix trace is {trace}, expected 1.0")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Density matrix definition

        Example:
            >>> data = density_matrix.to_dict()
        """
        data = super().to_dict()
        data["state_type"] = self._state_type.value
        data["matrix"] = [[(elem.real, elem.imag) for elem in row] for row in self._matrix] if self._matrix else []
        data["trace"] = self.get_trace()
        data["purity"] = self.get_purity()
        data["is_pure"] = self.is_pure()
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(density_matrix)
        """
        return f"DensityMatrix(num_qubits={self._num_qubits}, purity={self.get_purity():.4f})"
