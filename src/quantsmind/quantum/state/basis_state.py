"""
Basis State Module

This module provides basis state definitions for the Quantum package.

Purpose
-------
Provide basis state management for quantum computing operations.

Responsibilities
----------------
- Define basis state structure
- Support basis state operations
- Support basis state validation
- Support basis state metadata

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
from quantsmind.quantum.algorithms.types import QubitIndex, ValidationResult
from quantsmind.quantum.state.quantum_state import QuantumState


class BasisState(QuantumState):
    """Concrete implementation of a basis state.

    This class provides basis state functionality for quantum computing.
    Basis states are computational basis states like |0⟩ and |1⟩.

    Attributes:
        _num_qubits: Number of qubits
        _basis_string: Basis string (e.g., "010")
        _metadata: State metadata

    Example:
        >>> basis_state = BasisState(3, "010")
    """

    def __init__(
        self,
        num_qubits: int,
        basis_string: str = "0",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a BasisState.

        Args:
            num_qubits: Number of qubits
            basis_string: Basis string
            metadata: State metadata

        Example:
            >>> basis_state = BasisState(3, "010")
        """
        super().__init__(num_qubits, metadata)
        self._basis_string = basis_string
        self._state_type = StateType.BASIS

    @property
    def basis_string(self) -> str:
        """Get the basis string.

        Returns:
            Basis string

        Example:
            >>> basis_str = basis_state.basis_string
        """
        return self._basis_string

    @property
    def state_type(self) -> StateType:
        """Get the state type.

        Returns:
            State type

        Example:
            >>> stype = basis_state.state_type
        """
        return self._state_type

    def set_basis_string(self, basis_string: str) -> None:
        """Set the basis string.

        Args:
            basis_string: Basis string

        Example:
            >>> basis_state.set_basis_string("101")
        """
        if len(basis_string) != self._num_qubits:
            raise StateError(f"Basis string length {len(basis_string)} does not match num_qubits {self._num_qubits}", {"basis_string": basis_string})

        for char in basis_string:
            if char not in ["0", "1"]:
                raise StateError(f"Invalid character in basis string: {char}", {"basis_string": basis_string})

        self._basis_string = basis_string

    def get_decimal_value(self) -> int:
        """Get the decimal value of the basis state.

        Returns:
            Decimal value

        Example:
            >>> value = basis_state.get_decimal_value()
        """
        return int(self._basis_string, 2)

    def flip_qubit(self, qubit_index: QubitIndex) -> None:
        """Flip a qubit in the basis state.

        Args:
            qubit_index: Qubit index to flip

        Example:
            >>> basis_state.flip_qubit(0)
        """
        if qubit_index < 0 or qubit_index >= self._num_qubits:
            raise StateError(f"Qubit index {qubit_index} out of range", {"index": qubit_index, "num_qubits": self._num_qubits})

        # Flip the bit at the specified position
        position = self._num_qubits - 1 - qubit_index
        new_string = list(self._basis_string)
        new_string[position] = "1" if new_string[position] == "0" else "0"
        self._basis_string = "".join(new_string)

    def validate(self) -> ValidationResult:
        """Validate the basis state.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = basis_state.validate()
        """
        errors = []

        # Validate base state
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if len(self._basis_string) != self._num_qubits:
            errors.append(f"Basis string length {len(self._basis_string)} does not match num_qubits {self._num_qubits}")

        for char in self._basis_string:
            if char not in ["0", "1"]:
                errors.append(f"Invalid character in basis string: {char}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Basis state definition

        Example:
            >>> data = basis_state.to_dict()
        """
        data = super().to_dict()
        data["basis_string"] = self._basis_string
        data["state_type"] = self._state_type.value
        data["decimal_value"] = self.get_decimal_value()
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(basis_state)
        """
        return f"BasisState(num_qubits={self._num_qubits}, basis_string={self._basis_string})"
