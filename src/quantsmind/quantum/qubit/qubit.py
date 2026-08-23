"""
Qubit Module

This module provides qubit definitions for the Quantum package.

Purpose
-------
Provide qubit management for quantum computing operations.

Responsibilities
----------------
- Define qubit structure
- Support qubit operations
- Support qubit validation
- Support qubit metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.interfaces (quantum interfaces)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.exceptions import QubitError
from quantsmind.quantum.algorithms.interfaces import IQubit
from quantsmind.quantum.algorithms.types import QubitIndex, ValidationResult


class Qubit(IQubit):
    """Concrete implementation of a qubit.

    This class provides qubit functionality for quantum computing.

    Attributes:
        _index: Qubit index
        _state: Qubit state
        _metadata: Qubit metadata

    Example:
        >>> qubit = Qubit(0)
        >>> qubit.reset()
    """

    def __init__(
        self,
        index: QubitIndex,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Qubit.

        Args:
            index: Qubit index
            metadata: Qubit metadata

        Example:
            >>> qubit = Qubit(0)
        """
        if index < 0:
            raise QubitError("Qubit index cannot be negative", {"index": index})

        self._index = index
        self._state = "0"  # Initialize to |0⟩ state
        self._metadata = metadata or {}

    @property
    def index(self) -> QubitIndex:
        """Get the qubit index.

        Returns:
            Qubit index

        Example:
            >>> idx = qubit.index
        """
        return self._index

    @property
    def state(self) -> str:
        """Get the qubit state.

        Returns:
            Qubit state

        Example:
            >>> state = qubit.state
        """
        return self._state

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the qubit metadata.

        Returns:
            Qubit metadata

        Example:
            >>> metadata = qubit.metadata
        """
        return self._metadata.copy()

    def set_state(self, state: str) -> None:
        """Set the qubit state.

        Args:
            state: Qubit state

        Example:
            >>> qubit.set_state("1")
        """
        if state not in ["0", "1", "superposition", "entangled", "mixed"]:
            raise QubitError(f"Invalid qubit state: {state}", {"state": state})
        self._state = state

    def reset(self) -> None:
        """Reset the qubit to |0⟩ state.

        Example:
            >>> qubit.reset()
        """
        self._state = "0"

    def validate(self) -> ValidationResult:
        """Validate the qubit.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = qubit.validate()
        """
        errors = []

        if self._index < 0:
            errors.append("Qubit index cannot be negative")

        if self._state not in ["0", "1", "superposition", "entangled", "mixed"]:
            errors.append(f"Invalid qubit state: {self._state}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Qubit definition

        Example:
            >>> data = qubit.to_dict()
        """
        return {
            "index": self._index,
            "state": self._state,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(qubit)
        """
        return f"Qubit(index={self._index}, state={self._state})"


# Export
__all__ = [
    "Qubit",
]
