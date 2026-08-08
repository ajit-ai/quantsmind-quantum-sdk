"""
Quantum Register Module

This module provides quantum register definitions for the Quantum package.

Purpose
-------
Provide quantum register management for quantum computing operations.

Responsibilities
----------------
- Define quantum register structure
- Support quantum register operations
- Support quantum register validation
- Support quantum register metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.qubit.qubit (qubit module)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.quantum.algorithms.exceptions import CircuitError
from quantsmind.quantum.algorithms.types import QubitIndex, ValidationResult
from quantsmind.quantum.qubit.qubit import Qubit


class QuantumRegister:
    """Concrete implementation of a quantum register.

    This class provides quantum register functionality for quantum computing.

    Attributes:
        _name: Register name
        _size: Register size
        _qubits: List of qubits
        _metadata: Register metadata

    Example:
        >>> register = QuantumRegister("qr", 5)
        >>> register.initialize()
    """

    def __init__(
        self,
        name: str,
        size: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a QuantumRegister.

        Args:
            name: Register name
            size: Register size
            metadata: Register metadata

        Example:
            >>> register = QuantumRegister("qr", 5)
        """
        if not name:
            raise CircuitError("Register name cannot be empty", {"name": name})

        if size <= 0:
            raise CircuitError("Register size must be positive", {"size": size})

        self._name = name
        self._size = size
        self._qubits: List[Qubit] = []
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
    def qubits(self) -> List[Qubit]:
        """Get the qubits in the register.

        Returns:
            List of qubits

        Example:
            >>> qubits = register.qubits
        """
        return self._qubits.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the register metadata.

        Returns:
            Register metadata

        Example:
            >>> metadata = register.metadata
        """
        return self._metadata.copy()

    def initialize(self) -> None:
        """Initialize the register with qubits.

        Example:
            >>> register.initialize()
        """
        self._qubits = [Qubit(i) for i in range(self._size)]

    def add_qubit(self, qubit: Qubit) -> None:
        """Add a qubit to the register.

        Args:
            qubit: Qubit to add

        Example:
            >>> register.add_qubit(Qubit(0))
        """
        if len(self._qubits) >= self._size:
            raise CircuitError("Register is full", {"size": self._size})

        if qubit.index >= self._size:
            raise CircuitError(f"Qubit index {qubit.index} exceeds register size {self._size}", {"index": qubit.index})

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

    def get_qubit(self, index: QubitIndex) -> Optional[Qubit]:
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

    def to_dict(self) -> Dict[str, Any]:
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
        return f"QuantumRegister(name={self._name}, size={self._size}, qubits={len(self._qubits)})"
