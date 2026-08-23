"""
Qubit Register Module

This module provides qubit register definitions for the Quantum package.

Purpose
-------
Provide qubit register management for quantum computing operations.

Responsibilities
----------------
- Define qubit register structure
- Support qubit register operations
- Support qubit register validation
- Support qubit register metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.qubit.qubit (qubit module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.exceptions import QubitError
from quantsmind.quantum.algorithms.types import QubitIndex, ValidationResult
from quantsmind.quantum.qubit.qubit import Qubit


class QubitRegister:
    """Concrete implementation of a qubit register.

    This class provides qubit register functionality for quantum computing.

    Attributes:
        _name: Register name
        _qubits: List of qubits
        _metadata: Register metadata

    Example:
        >>> register = QubitRegister("qr", 5)
        >>> register.add_qubit(Qubit(0))
    """

    def __init__(
        self,
        name: str,
        size: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a QubitRegister.

        Args:
            name: Register name
            size: Register size
            metadata: Register metadata

        Example:
            >>> register = QubitRegister("qr", 5)
        """
        if not name:
            raise QubitError("Register name cannot be empty", {"name": name})

        if size <= 0:
            raise QubitError("Register size must be positive", {"size": size})

        self._name = name
        self._qubits: list[Qubit] = []
        self._size = size
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the register name.

        Returns:
            Register name

        Example:
            >>> name = register.name
        """
        return self._name

    @property
    def size(self) -> int:
        """Get the register size.

        Returns:
            Register size

        Example:
            >>> size = register.size
        """
        return self._size

    @property
    def qubits(self) -> list[Qubit]:
        """Get the qubits in the register.

        Returns:
            List of qubits

        Example:
            >>> qubits = register.qubits
        """
        return self._qubits.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the register metadata.

        Returns:
            Register metadata

        Example:
            >>> metadata = register.metadata
        """
        return self._metadata.copy()

    def add_qubit(self, qubit: Qubit) -> None:
        """Add a qubit to the register.

        Args:
            qubit: Qubit to add

        Example:
            >>> register.add_qubit(Qubit(0))
        """
        if len(self._qubits) >= self._size:
            raise QubitError("Register is full", {"size": self._size})

        if qubit.index >= self._size:
            raise QubitError(f"Qubit index {qubit.index} exceeds register size {self._size}", {"index": qubit.index})

        # Check if qubit with same index already exists
        for existing_qubit in self._qubits:
            if existing_qubit.index == qubit.index:
                raise QubitError(f"Qubit with index {qubit.index} already exists", {"index": qubit.index})

        self._qubits.append(qubit)

    def remove_qubit(self, index: QubitIndex) -> bool:
        """Remove a qubit from the register.

        Args:
            index: Qubit index

        Returns:
            True if removed

        Example:
            >>> removed = register.remove_qubit(0)
        """
        for i, qubit in enumerate(self._qubits):
            if qubit.index == index:
                del self._qubits[i]
                return True
        return False

    def get_qubit(self, index: QubitIndex) -> Qubit | None:
        """Get a qubit by index.

        Args:
            index: Qubit index

        Returns:
            Qubit or None

        Example:
            >>> qubit = register.get_qubit(0)
        """
        for qubit in self._qubits:
            if qubit.index == index:
                return qubit
        return None

    def reset_all(self) -> None:
        """Reset all qubits to |0⟩ state.

        Example:
            >>> register.reset_all()
        """
        for qubit in self._qubits:
            qubit.reset()

    def count(self) -> int:
        """Get the number of qubits in the register.

        Returns:
            Number of qubits

        Example:
            >>> count = register.count()
        """
        return len(self._qubits)

    def is_full(self) -> bool:
        """Check if the register is full.

        Returns:
            True if full

        Example:
            >>> full = register.is_full()
        """
        return len(self._qubits) >= self._size

    def validate(self) -> ValidationResult:
        """Validate the register.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = register.validate()
        """
        errors = []

        if not self._name:
            errors.append("Register name cannot be empty")

        if self._size <= 0:
            errors.append("Register size must be positive")

        if len(self._qubits) > self._size:
            errors.append(f"Register has {len(self._qubits)} qubits, but size is {self._size}")

        # Validate all qubits
        for qubit in self._qubits:
            is_valid, qubit_errors = qubit.validate()
            errors.extend(qubit_errors)

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Register definition

        Example:
            >>> data = register.to_dict()
        """
        return {
            "name": self._name,
            "size": self._size,
            "qubit_count": len(self._qubits),
            "qubits": [q.to_dict() for q in self._qubits],
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(register)
        """
        return f"QubitRegister(name={self._name}, size={self._size}, qubits={len(self._qubits)})"


# Export
__all__ = [
    "QubitRegister",
]
