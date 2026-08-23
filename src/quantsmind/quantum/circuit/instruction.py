"""
Instruction Module

This module provides instruction definitions for the Quantum package.

Purpose
-------
Provide instruction management for quantum computing operations.

Responsibilities
----------------
- Define instruction structure
- Support instruction operations
- Support instruction validation
- Support instruction metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.gate.gate (gate module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.exceptions import CircuitError
from quantsmind.quantum.algorithms.types import QubitIndices, ValidationResult
from quantsmind.quantum.gate.gate import QuantumGate


class Instruction:
    """Concrete implementation of a quantum instruction.

    This class provides instruction functionality for quantum computing.
    An instruction represents a single operation in a quantum circuit.

    Attributes:
        _gate: Gate to apply
        _qubits: Target qubits
        _clbits: Classical bits (for measurement)
        _params: Instruction parameters
        _metadata: Instruction metadata

    Example:
        >>> instruction = Instruction(h_gate, [0])
    """

    def __init__(
        self,
        gate: QuantumGate,
        qubits: QubitIndices,
        clbits: list[int] | None = None,
        params: dict[str, float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Instruction.

        Args:
            gate: Gate to apply
            qubits: Target qubits
            clbits: Classical bits
            params: Instruction parameters
            metadata: Instruction metadata

        Example:
            >>> instruction = Instruction(h_gate, [0])
        """
        if gate is None:
            raise CircuitError("Gate cannot be None", {"gate": None})

        if not qubits:
            raise CircuitError("Qubits cannot be empty", {"qubits": qubits})

        self._gate = gate
        self._qubits = qubits
        self._clbits = clbits or []
        self._params = params or {}
        self._metadata = metadata or {}

    @property
    def gate(self) -> QuantumGate:
        """Get the gate.

        Returns:
            Gate

        Example:
            >>> gate = instruction.gate
        """
        return self._gate

    @property
    def qubits(self) -> QubitIndices:
        """Get the target qubits.

        Returns:
            Qubit indices

        Example:
            >>> qubits = instruction.qubits
        """
        return self._qubits.copy()

    @property
    def clbits(self) -> list[int]:
        """Get the classical bits.

        Returns:
            Classical bit indices

        Example:
            >>> clbits = instruction.clbits
        """
        return self._clbits.copy()

    @property
    def params(self) -> dict[str, float]:
        """Get the instruction parameters.

        Returns:
            Parameters

        Example:
            >>> params = instruction.params
        """
        return self._params.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the instruction metadata.

        Returns:
            Instruction metadata

        Example:
            >>> metadata = instruction.metadata
        """
        return self._metadata.copy()

    def set_qubits(self, qubits: QubitIndices) -> None:
        """Set the target qubits.

        Args:
            qubits: Qubit indices

        Example:
            >>> instruction.set_qubits([1])
        """
        if not qubits:
            raise CircuitError("Qubits cannot be empty", {"qubits": qubits})

        if len(qubits) != self._gate.num_qubits:
            raise CircuitError(f"Gate requires {self._gate.num_qubits} qubits, but {len(qubits)} provided", {"gate": self._gate.name})

        self._qubits = qubits

    def set_clbits(self, clbits: list[int]) -> None:
        """Set the classical bits.

        Args:
            clbits: Classical bit indices

        Example:
            >>> instruction.set_clbits([0])
        """
        self._clbits = clbits

    def set_param(self, key: str, value: float) -> None:
        """Set a parameter.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> instruction.set_param("theta", 1.57)
        """
        self._params[key] = value

    def validate(self, num_qubits: int, num_clbits: int = 0) -> ValidationResult:
        """Validate the instruction.

        Args:
            num_qubits: Number of qubits in the circuit
            num_clbits: Number of classical bits in the circuit

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = instruction.validate(2)
        """
        errors = []

        # Validate gate
        is_valid, gate_errors = self._gate.validate()
        errors.extend(gate_errors)

        # Validate qubit indices
        for qubit in self._qubits:
            if qubit < 0 or qubit >= num_qubits:
                errors.append(f"Qubit index {qubit} out of range [0, {num_qubits})")

        # Validate classical bit indices
        for clbit in self._clbits:
            if clbit < 0 or clbit >= num_clbits:
                errors.append(f"Classical bit index {clbit} out of range [0, {num_clbits})")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Instruction definition

        Example:
            >>> data = instruction.to_dict()
        """
        return {
            "gate": self._gate.name,
            "qubits": self._qubits,
            "clbits": self._clbits,
            "params": self._params,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(instruction)
        """
        return f"Instruction(gate={self._gate.name}, qubits={self._qubits})"


# Export
__all__ = [
    "Instruction",
]
