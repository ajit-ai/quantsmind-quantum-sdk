"""
State Vector Module

This module provides state vector definitions for the Quantum package.

Purpose
-------
Provide state vector management for quantum computing operations.

Responsibilities
----------------
- Define state vector structure
- Support state vector operations
- Support state vector validation
- Support state vector metadata

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


class StateVector(QuantumState):
    """Concrete implementation of a state vector.

    This class provides state vector functionality for quantum computing.
    State vectors represent pure quantum states.

    Attributes:
        _num_qubits: Number of qubits
        _amplitudes: Complex amplitudes
        _metadata: State metadata

    Example:
        >>> state_vector = StateVector(1)
        >>> state_vector.initialize_zero()
    """

    def __init__(
        self,
        num_qubits: int,
        amplitudes: Optional[List[complex]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a StateVector.

        Args:
            num_qubits: Number of qubits
            amplitudes: Complex amplitudes
            metadata: State metadata

        Example:
            >>> state_vector = StateVector(1)
        """
        super().__init__(num_qubits, metadata)
        self._amplitudes = amplitudes
        self._state_type = StateType.STATE_VECTOR

        if amplitudes is None:
            self.initialize_zero()

    @property
    def amplitudes(self) -> List[complex]:
        """Get the amplitudes.

        Returns:
            List of complex amplitudes

        Example:
            >>> amps = state_vector.amplitudes
        """
        return self._amplitudes.copy() if self._amplitudes else []

    @property
    def state_type(self) -> StateType:
        """Get the state type.

        Returns:
            State type

        Example:
            >>> stype = state_vector.state_type
        """
        return self._state_type

    def set_amplitudes(self, amplitudes: List[complex]) -> None:
        """Set the amplitudes.

        Args:
            amplitudes: Complex amplitudes

        Example:
            >>> state_vector.set_amplitudes([1, 0])
        """
        expected_size = 2 ** self._num_qubits
        if len(amplitudes) != expected_size:
            raise StateError(f"Amplitudes length {len(amplitudes)} does not match expected size {expected_size}", {"num_qubits": self._num_qubits})

        self._amplitudes = amplitudes

    def get_amplitude(self, index: int) -> complex:
        """Get an amplitude by index.

        Args:
            index: Amplitude index

        Returns:
            Complex amplitude

        Example:
            >>> amp = state_vector.get_amplitude(0)
        """
        if self._amplitudes is None:
            raise StateError("Amplitudes not initialized", {"num_qubits": self._num_qubits})

        if index < 0 or index >= len(self._amplitudes):
            raise StateError(f"Amplitude index {index} out of range", {"index": index, "size": len(self._amplitudes)})

        return self._amplitudes[index]

    def get_probability(self, index: int) -> float:
        """Get the probability of measuring a specific basis state.

        Args:
            index: Basis state index

        Returns:
            Probability

        Example:
            >>> prob = state_vector.get_probability(0)
        """
        amplitude = self.get_amplitude(index)
        return abs(amplitude) ** 2

    def get_probabilities(self) -> List[float]:
        """Get all measurement probabilities.

        Returns:
            List of probabilities

        Example:
            >>> probs = state_vector.get_probabilities()
        """
        if self._amplitudes is None:
            return []

        return [abs(amp) ** 2 for amp in self._amplitudes]

    def initialize_zero(self) -> None:
        """Initialize to |0⟩ state.

        Example:
            >>> state_vector.initialize_zero()
        """
        size = 2 ** self._num_qubits
        self._amplitudes = [0j] * size
        self._amplitudes[0] = 1.0 + 0j

    def initialize_one(self) -> None:
        """Initialize to |1⟩ state.

        Example:
            >>> state_vector.initialize_one()
        """
        size = 2 ** self._num_qubits
        self._amplitudes = [0j] * size
        self._amplitudes[-1] = 1.0 + 0j

    def initialize_plus(self) -> None:
        """Initialize to |+⟩ state.

        Example:
            >>> state_vector.initialize_plus()
        """
        if self._num_qubits != 1:
            raise StateError("Plus state only defined for single qubit", {"num_qubits": self._num_qubits})

        self._amplitudes = [0.70710678 + 0j, 0.70710678 + 0j]

    def initialize_minus(self) -> None:
        """Initialize to |-⟩ state.

        Example:
            >>> state_vector.initialize_minus()
        """
        if self._num_qubits != 1:
            raise StateError("Minus state only defined for single qubit", {"num_qubits": self._num_qubits})

        self._amplitudes = [0.70710678 + 0j, -0.70710678 + 0j]

    def get_norm(self) -> float:
        """Get the norm of the state vector.

        Returns:
            Norm

        Example:
            >>> norm = state_vector.get_norm()
        """
        if self._amplitudes is None:
            return 0.0

        return sum(abs(amp) ** 2 for amp in self._amplitudes) ** 0.5

    def normalize(self) -> None:
        """Normalize the state vector.

        Example:
            >>> state_vector.normalize()
        """
        if self._amplitudes is None:
            return

        norm = self.get_norm()
        if norm > 0:
            self._amplitudes = [amp / norm for amp in self._amplitudes]

    def validate(self) -> ValidationResult:
        """Validate the state vector.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = state_vector.validate()
        """
        errors = []

        # Validate base state
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if self._amplitudes is None:
            errors.append("Amplitudes not initialized")
        else:
            expected_size = 2 ** self._num_qubits
            if len(self._amplitudes) != expected_size:
                errors.append(f"Amplitudes length {len(self._amplitudes)} does not match expected size {expected_size}")

            # Check normalization
            norm_squared = sum(abs(amp) ** 2 for amp in self._amplitudes)
            if abs(norm_squared - 1.0) > 1e-6:
                errors.append(f"State vector not normalized: norm^2 = {norm_squared}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            State vector definition

        Example:
            >>> data = state_vector.to_dict()
        """
        data = super().to_dict()
        data["state_type"] = self._state_type.value
        data["amplitudes"] = [(amp.real, amp.imag) for amp in self._amplitudes] if self._amplitudes else []
        data["norm"] = self.get_norm()
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(state_vector)
        """
        return f"StateVector(num_qubits={self._num_qubits}, norm={self.get_norm():.4f})"
