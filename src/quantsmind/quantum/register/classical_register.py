"""
Classical Register Module

This module provides classical register definitions for the Quantum package.

Purpose
-------
Provide classical register management for quantum computing operations.

Responsibilities
----------------
- Define classical register structure
- Support classical register operations
- Support classical register validation
- Support classical register metadata

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


class ClassicalRegister:
    """Concrete implementation of a classical register.

    This class provides classical register functionality for quantum computing.
    Classical registers store measurement results.

    Attributes:
        _name: Register name
        _size: Register size
        _bits: List of bit values
        _metadata: Register metadata

    Example:
        >>> register = ClassicalRegister("cr", 5)
        >>> register.initialize()
    """

    def __init__(
        self,
        name: str,
        size: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a ClassicalRegister.

        Args:
            name: Register name
            size: Register size
            metadata: Register metadata

        Example:
            >>> register = ClassicalRegister("cr", 5)
        """
        if not name:
            raise CircuitError("Register name cannot be empty", {"name": name})

        if size <= 0:
            raise CircuitError("Register size must be positive", {"size": size})

        self._name = name
        self._size = size
        self._bits: List[int] = []
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
    def bits(self) -> List[int]:
        """Get the bits in the register.

        Returns:
            List of bit values

        Example:
            >>> bits = register.bits
        """
        return self._bits.copy()

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
        """Initialize the register with zeros.

        Example:
            >>> register.initialize()
        """
        self._bits = [0] * self._size

    def set_bit(self, index: int, value: int) -> None:
        """Set a bit value.

        Args:
            index: Bit index
            value: Bit value (0 or 1)

        Example:
            >>> register.set_bit(0, 1)
        """
        if index < 0 or index >= self._size:
            raise CircuitError(f"Bit index {index} out of range [0, {self._size})", {"index": index})

        if value not in [0, 1]:
            raise CircuitError(f"Bit value must be 0 or 1, got {value}", {"value": value})

        if len(self._bits) <= index:
            self._bits.extend([0] * (index + 1 - len(self._bits)))

        self._bits[index] = value

    def get_bit(self, index: int) -> int:
        """Get a bit value.

        Args:
            index: Bit index

        Returns:
            Bit value

        Example:
            >>> bit = register.get_bit(0)
        """
        if index < 0 or index >= len(self._bits):
            return 0
        return self._bits[index]

    def set_bits(self, values: List[int]) -> None:
        """Set multiple bit values.

        Args:
            values: List of bit values

        Example:
            >>> register.set_bits([1, 0, 1])
        """
        if len(values) > self._size:
            raise CircuitError(f"Cannot set {len(values)} bits in register of size {self._size}", {"size": self._size})

        for value in values:
            if value not in [0, 1]:
                raise CircuitError(f"Bit value must be 0 or 1, got {value}", {"value": value})

        self._bits = values.copy()
        self._bits.extend([0] * (self._size - len(self._bits)))

    def get_bits(self) -> List[int]:
        """Get all bit values.

        Returns:
            List of bit values

        Example:
            >>> bits = register.get_bits()
        """
        return self._bits.copy()

    def reset_all(self) -> None:
        """Reset all bits to 0.

        Example:
            >>> register.reset_all()
        """
        self._bits = [0] * self._size

    def count(self) -> int:
        """Get the number of bits in the register.

        Returns:
            Number of bits

        Example:
            >>> count = register.count()
        """
        return len(self._bits)

    def get_int_value(self) -> int:
        """Get the integer value of the register.

        Returns:
            Integer value

        Example:
            >>> value = register.get_int_value()
        """
        value = 0
        for i, bit in enumerate(reversed(self._bits)):
            if bit:
                value += 2 ** i
        return value

    def set_int_value(self, value: int) -> None:
        """Set the register from an integer value.

        Args:
            value: Integer value

        Example:
            >>> register.set_int_value(5)
        """
        if value < 0:
            raise CircuitError(f"Integer value cannot be negative, got {value}", {"value": value})

        max_value = 2 ** self._size - 1
        if value > max_value:
            raise CircuitError(f"Integer value {value} exceeds maximum {max_value}", {"value": value, "max": max_value})

        self._bits = []
        for i in range(self._size):
            self._bits.append((value >> (self._size - 1 - i)) & 1)

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

        if len(self._bits) > self._size:
            errors.append(f"Register has {len(self._bits)} bits, but size is {self._size}")

        for bit in self._bits:
            if bit not in [0, 1]:
                errors.append(f"Invalid bit value: {bit}")

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
            "bit_count": len(self._bits),
            "bits": self._bits,
            "int_value": self.get_int_value(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(register)
        """
        return f"ClassicalRegister(name={self._name}, size={self._size}, bits={len(self._bits)})"
