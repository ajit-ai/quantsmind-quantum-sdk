"""
Multi Qubit Gate Module

This module provides multi qubit gate definitions for the Quantum package.

Purpose
-------
Provide multi qubit gate management for quantum computing operations.

Responsibilities
----------------
- Define multi qubit gate structure
- Support multi qubit gate operations
- Support multi qubit gate validation
- Support multi qubit gate metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.constants (quantum constants)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.gate.gate (gate module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.constants import GATE_ISWAP, GATE_SWAP
from quantsmind.quantum.algorithms.enums import GateType
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.gate.gate import QuantumGate


class MultiQubitGate(QuantumGate):
    """Concrete implementation of a multi qubit gate.

    This class provides multi qubit gate functionality for quantum computing.

    Attributes:
        _name: Gate name
        _gate_type: Gate type
        _num_qubits: Number of qubits
        _parameters: Gate parameters
        _matrix: Unitary matrix
        _metadata: Gate metadata

    Example:
        >>> gate = MultiQubitGate("SWAP", 2)
    """

    def __init__(
        self,
        name: str,
        num_qubits: int,
        parameters: dict[str, float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a MultiQubitGate.

        Args:
            name: Gate name
            num_qubits: Number of qubits
            parameters: Gate parameters
            metadata: Gate metadata

        Example:
            >>> gate = MultiQubitGate("SWAP", 2)
        """
        super().__init__(name, GateType.MULTI_QUBIT.value, num_qubits, parameters, metadata)
        self._initialize_matrix()

    def _initialize_matrix(self) -> None:
        """Initialize the gate matrix based on the gate name.

        Example:
            >>> gate._initialize_matrix()
        """
        if self._name == GATE_SWAP and self._num_qubits == 2:
            # SWAP gate matrix
            self.set_matrix([
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
            ])
        elif self._name == GATE_ISWAP and self._num_qubits == 2:
            # iSWAP gate matrix
            self.set_matrix([
                [1, 0, 0, 0],
                [0, 0, 1j, 0],
                [0, 1j, 0, 0],
                [0, 0, 0, 1],
            ])
        else:
            # Custom gate, matrix must be set manually
            pass

    def validate(self) -> ValidationResult:
        """Validate the multi qubit gate.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = gate.validate()
        """
        errors = []

        # Validate base gate
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if self._num_qubits < 2:
            errors.append(f"Multi qubit gate must have at least 2 qubits, got {self._num_qubits}")

        return (len(errors) == 0, errors)


class SwapGate(MultiQubitGate):
    """SWAP gate.

    Swaps the states of two qubits.

    Example:
        >>> gate = SwapGate()
    """

    def __init__(self, metadata: dict[str, Any] | None = None) -> None:
        """Initialize a SwapGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = SwapGate()
        """
        super().__init__(GATE_SWAP, 2, metadata=metadata)


class ISwapGate(MultiQubitGate):
    """iSWAP gate.

    Swaps the states of two qubits with a phase.

    Example:
        >>> gate = ISwapGate()
    """

    def __init__(self, metadata: dict[str, Any] | None = None) -> None:
        """Initialize an ISwapGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = ISwapGate()
        """
        super().__init__(GATE_ISWAP, 2, metadata=metadata)


# Export
__all__ = [
    "MultiQubitGate",
    "SwapGate",
    "ISwapGate",
]
