"""
Operation Module

This module provides operation definitions for the Quantum package.

Purpose
-------
Provide operation management for quantum computing operations.

Responsibilities
----------------
- Define operation structure
- Support operation operations
- Support operation validation
- Support operation metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.circuit.instruction (instruction module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.exceptions import CircuitError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.circuit.instruction import Instruction


class Operation:
    """Concrete implementation of a quantum operation.

    This class provides operation functionality for quantum computing.
    An operation represents a sequence of instructions.

    Attributes:
        _name: Operation name
        _instructions: List of instructions
        _metadata: Operation metadata

    Example:
        >>> operation = Operation("bell_pair")
        >>> operation.add_instruction(instruction)
    """

    def __init__(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Operation.

        Args:
            name: Operation name
            metadata: Operation metadata

        Example:
            >>> operation = Operation("bell_pair")
        """
        if not name:
            raise CircuitError("Operation name cannot be empty", {"name": name})

        self._name = name
        self._instructions: list[Instruction] = []
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the operation name.

        Returns:
            Operation name

        Example:
            >>> name = operation.name
        """
        return self._name

    @property
    def instructions(self) -> list[Instruction]:
        """Get the instructions.

        Returns:
            List of instructions

        Example:
            >>> instructions = operation.instructions
        """
        return self._instructions.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the operation metadata.

        Returns:
            Operation metadata

        Example:
            >>> metadata = operation.metadata
        """
        return self._metadata.copy()

    def add_instruction(self, instruction: Instruction) -> None:
        """Add an instruction to the operation.

        Args:
            instruction: Instruction to add

        Example:
            >>> operation.add_instruction(instruction)
        """
        if instruction is None:
            raise CircuitError("Instruction cannot be None", {"instruction": None})

        self._instructions.append(instruction)

    def remove_instruction(self, index: int) -> bool:
        """Remove an instruction from the operation.

        Args:
            index: Instruction index

        Returns:
            True if removed

        Example:
            >>> removed = operation.remove_instruction(0)
        """
        if 0 <= index < len(self._instructions):
            del self._instructions[index]
            return True
        return False

    def get_instruction(self, index: int) -> Instruction | None:
        """Get an instruction by index.

        Args:
            index: Instruction index

        Returns:
            Instruction or None

        Example:
            >>> instruction = operation.get_instruction(0)
        """
        if 0 <= index < len(self._instructions):
            return self._instructions[index]
        return None

    def clear(self) -> None:
        """Clear all instructions from the operation.

        Example:
            >>> operation.clear()
        """
        self._instructions.clear()

    def count(self) -> int:
        """Get the number of instructions.

        Returns:
            Number of instructions

        Example:
            >>> count = operation.count()
        """
        return len(self._instructions)

    def validate(self, num_qubits: int, num_clbits: int = 0) -> ValidationResult:
        """Validate the operation.

        Args:
            num_qubits: Number of qubits
            num_clbits: Number of classical bits

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = operation.validate(2)
        """
        errors = []

        if not self._name:
            errors.append("Operation name cannot be empty")

        # Validate all instructions
        for i, instruction in enumerate(self._instructions):
            is_valid, instr_errors = instruction.validate(num_qubits, num_clbits)
            errors.extend([f"Instruction {i}: {err}" for err in instr_errors])

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Operation definition

        Example:
            >>> data = operation.to_dict()
        """
        return {
            "name": self._name,
            "instruction_count": len(self._instructions),
            "instructions": [instr.to_dict() for instr in self._instructions],
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(operation)
        """
        return f"Operation(name={self._name}, instructions={len(self._instructions)})"


# Export
__all__ = [
    "Operation",
]
