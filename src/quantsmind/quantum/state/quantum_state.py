"""
Quantum State Module

This module provides quantum state definitions for the Quantum package.

Purpose
-------
Provide quantum state management for quantum computing operations.

Responsibilities
----------------
- Define quantum state structure
- Support quantum state operations
- Support quantum state validation
- Support quantum state metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.interfaces (quantum interfaces)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.exceptions import StateError
from quantsmind.quantum.algorithms.interfaces import IQuantumState
from quantsmind.quantum.algorithms.types import DensityMatrix, StateVector, ValidationResult


class QuantumState(IQuantumState):
    """Concrete implementation of a quantum state.

    This class provides quantum state functionality for quantum computing.

    Attributes:
        _num_qubits: Number of qubits
        _state_vector: State vector representation
        _density_matrix: Density matrix representation
        _metadata: State metadata

    Example:
        >>> state = QuantumState(1)
        >>> state.initialize_zero()
    """

    def __init__(
        self,
        num_qubits: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a QuantumState.

        Args:
            num_qubits: Number of qubits
            metadata: State metadata

        Example:
            >>> state = QuantumState(1)
        """
        if num_qubits <= 0:
            raise StateError("Number of qubits must be positive", {"num_qubits": num_qubits})

        self._num_qubits = num_qubits
        self._state_vector: StateVector | None = None
        self._density_matrix: DensityMatrix | None = None
        self._metadata = metadata or {}

    @property
    def num_qubits(self) -> int:
        """Get the number of qubits in the state.

        Returns:
            Number of qubits

        Example:
            >>> n = state.num_qubits
        """
        return self._num_qubits

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the state metadata.

        Returns:
            State metadata

        Example:
            >>> metadata = state.metadata
        """
        return self._metadata.copy()

    def get_state_vector(self) -> StateVector:
        """Get the state vector representation.

        Returns:
            State vector

        Example:
            >>> sv = state.get_state_vector()
        """
        if self._state_vector is None:
            raise StateError("State vector not initialized", {"num_qubits": self._num_qubits})
        return self._state_vector

    def get_density_matrix(self) -> DensityMatrix:
        """Get the density matrix representation.

        Returns:
            Density matrix

        Example:
            >>> dm = state.get_density_matrix()
        """
        if self._density_matrix is None:
            raise StateError("Density matrix not initialized", {"num_qubits": self._num_qubits})
        return self._density_matrix

    def set_state_vector(self, state_vector: StateVector) -> None:
        """Set the state vector.

        Args:
            state_vector: State vector

        Example:
            >>> state.set_state_vector([1, 0])
        """
        self._state_vector = state_vector
        self._density_matrix = None  # Invalidate density matrix

    def set_density_matrix(self, density_matrix: DensityMatrix) -> None:
        """Set the density matrix.

        Args:
            density_matrix: Density matrix

        Example:
            >>> state.set_density_matrix([[1, 0], [0, 0]])
        """
        self._density_matrix = density_matrix
        self._state_vector = None  # Invalidate state vector

    def initialize_zero(self) -> None:
        """Initialize to |0⟩ state.

        Example:
            >>> state.initialize_zero()
        """
        # Placeholder implementation
        size = 2 ** self._num_qubits
        self._state_vector = [0] * size
        self._state_vector[0] = 1.0
        self._density_matrix = None

    def initialize_one(self) -> None:
        """Initialize to |1⟩ state.

        Example:
            >>> state.initialize_one()
        """
        # Placeholder implementation
        size = 2 ** self._num_qubits
        self._state_vector = [0] * size
        self._state_vector[-1] = 1.0
        self._density_matrix = None

    def normalize(self) -> None:
        """Normalize the state.

        Example:
            >>> state.normalize()
        """
        if self._state_vector is not None or self._density_matrix is not None:
            # Placeholder normalization
            pass

    def validate(self) -> ValidationResult:
        """Validate the state.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = state.validate()
        """
        errors = []

        if self._num_qubits <= 0:
            errors.append("Number of qubits must be positive")

        if self._state_vector is None and self._density_matrix is None:
            errors.append("State must have either state vector or density matrix")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            State definition

        Example:
            >>> data = state.to_dict()
        """
        return {
            "num_qubits": self._num_qubits,
            "has_state_vector": self._state_vector is not None,
            "has_density_matrix": self._density_matrix is not None,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(state)
        """
        return f"QuantumState(num_qubits={self._num_qubits})"
