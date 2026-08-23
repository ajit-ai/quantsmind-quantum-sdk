"""
Ancilla Qubit Module

This module provides ancilla qubit definitions for the Quantum package.

Purpose
-------
Provide ancilla qubit management for quantum computing operations.

Responsibilities
----------------
- Define ancilla qubit structure
- Support ancilla qubit operations
- Support ancilla qubit validation
- Support ancilla qubit metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.interfaces (quantum interfaces)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.qubit.qubit (qubit module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.types import QubitIndex, ValidationResult
from quantsmind.quantum.qubit.qubit import Qubit


class AncillaQubit(Qubit):
    """Concrete implementation of an ancilla qubit.

    This class provides ancilla qubit functionality for quantum computing.
    Ancilla qubits are auxiliary qubits used for intermediate computations.

    Attributes:
        _index: Qubit index
        _state: Qubit state
        _purpose: Ancilla purpose
        _metadata: Qubit metadata

    Example:
        >>> ancilla = AncillaQubit(5, purpose="computation")
        >>> ancilla.reset()
    """

    def __init__(
        self,
        index: QubitIndex,
        purpose: str = "computation",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an AncillaQubit.

        Args:
            index: Qubit index
            purpose: Ancilla purpose
            metadata: Qubit metadata

        Example:
            >>> ancilla = AncillaQubit(5, purpose="computation")
        """
        super().__init__(index, metadata)
        self._purpose = purpose

    @property
    def purpose(self) -> str:
        """Get the ancilla purpose.

        Returns:
            Ancilla purpose

        Example:
            >>> purpose = ancilla.purpose
        """
        return self._purpose

    def set_purpose(self, purpose: str) -> None:
        """Set the ancilla purpose.

        Args:
            purpose: Ancilla purpose

        Example:
            >>> ancilla.set_purpose("error_correction")
        """
        self._purpose = purpose

    def validate(self) -> ValidationResult:
        """Validate the ancilla qubit.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = ancilla.validate()
        """
        errors = []

        # Validate base qubit
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if not self._purpose:
            errors.append("Ancilla purpose cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Ancilla qubit definition

        Example:
            >>> data = ancilla.to_dict()
        """
        data = super().to_dict()
        data["purpose"] = self._purpose
        data["type"] = "ancilla"
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(ancilla)
        """
        return f"AncillaQubit(index={self._index}, state={self._state}, purpose={self._purpose})"


# Export
__all__ = [
    "AncillaQubit",
]
