"""
Single Qubit Gate Module

This module provides single qubit gate definitions for the Quantum package.

Purpose
-------
Provide single qubit gate management for quantum computing operations.

Responsibilities
----------------
- Define single qubit gate structure
- Support single qubit gate operations
- Support single qubit gate validation
- Support single qubit gate metadata

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

import math
from typing import Any, Dict, List, Optional

from quantsmind.quantum.algorithms.constants import (
    GATE_H,
    GATE_I,
    GATE_S,
    GATE_SX,
    GATE_T,
    GATE_X,
    GATE_Y,
    GATE_Z,
    HADAMARD_MATRIX,
    IDENTITY_MATRIX,
    PAULI_X_MATRIX,
    PAULI_Y_MATRIX,
    PAULI_Z_MATRIX,
    S_GATE_MATRIX,
    SX_GATE_MATRIX,
    T_GATE_MATRIX,
)
from quantsmind.quantum.algorithms.enums import GateType
from quantsmind.quantum.algorithms.exceptions import GateError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.gate.gate import QuantumGate


class SingleQubitGate(QuantumGate):
    """Concrete implementation of a single qubit gate.

    This class provides single qubit gate functionality for quantum computing.

    Attributes:
        _name: Gate name
        _gate_type: Gate type
        _parameters: Gate parameters
        _matrix: Unitary matrix
        _metadata: Gate metadata

    Example:
        >>> gate = SingleQubitGate("H")
    """

    def __init__(
        self,
        name: str,
        parameters: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a SingleQubitGate.

        Args:
            name: Gate name
            parameters: Gate parameters
            metadata: Gate metadata

        Example:
            >>> gate = SingleQubitGate("H")
        """
        super().__init__(name, GateType.SINGLE_QUBIT.value, 1, parameters, metadata)
        self._initialize_matrix()

    def _initialize_matrix(self) -> None:
        """Initialize the gate matrix based on the gate name.

        Example:
            >>> gate._initialize_matrix()
        """
        if self._name == GATE_I:
            self.set_matrix([[complex(x) for x in row] for row in IDENTITY_MATRIX])
        elif self._name == GATE_X:
            self.set_matrix([[complex(x) for x in row] for row in PAULI_X_MATRIX])
        elif self._name == GATE_Y:
            self.set_matrix([[complex(x) for x in row] for row in PAULI_Y_MATRIX])
        elif self._name == GATE_Z:
            self.set_matrix([[complex(x) for x in row] for row in PAULI_Z_MATRIX])
        elif self._name == GATE_H:
            self.set_matrix([[complex(x) for x in row] for row in HADAMARD_MATRIX])
        elif self._name == GATE_S:
            self.set_matrix([[complex(x) for x in row] for row in S_GATE_MATRIX])
        elif self._name == GATE_T:
            self.set_matrix([[complex(x) for x in row] for row in T_GATE_MATRIX])
        elif self._name == GATE_SX:
            self.set_matrix([[complex(x) for x in row] for row in SX_GATE_MATRIX])
        else:
            # Custom gate, matrix must be set manually
            pass

    def validate(self) -> ValidationResult:
        """Validate the single qubit gate.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = gate.validate()
        """
        errors = []

        # Validate base gate
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if self._num_qubits != 1:
            errors.append(f"Single qubit gate must have 1 qubit, got {self._num_qubits}")

        return (len(errors) == 0, errors)


class IdentityGate(SingleQubitGate):
    """Identity gate (I).

    Leaves the qubit unchanged.

    Example:
        >>> gate = IdentityGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize an IdentityGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = IdentityGate()
        """
        super().__init__(GATE_I, metadata=metadata)


class PauliXGate(SingleQubitGate):
    """Pauli-X gate (X).

    Bit flip gate.

    Example:
        >>> gate = PauliXGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a PauliXGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = PauliXGate()
        """
        super().__init__(GATE_X, metadata=metadata)


class PauliYGate(SingleQubitGate):
    """Pauli-Y gate (Y).

    Bit and phase flip gate.

    Example:
        >>> gate = PauliYGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a PauliYGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = PauliYGate()
        """
        super().__init__(GATE_Y, metadata=metadata)


class PauliZGate(SingleQubitGate):
    """Pauli-Z gate (Z).

    Phase flip gate.

    Example:
        >>> gate = PauliZGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a PauliZGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = PauliZGate()
        """
        super().__init__(GATE_Z, metadata=metadata)


class HadamardGate(SingleQubitGate):
    """Hadamard gate (H).

    Creates superposition.

    Example:
        >>> gate = HadamardGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a HadamardGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = HadamardGate()
        """
        super().__init__(GATE_H, metadata=metadata)


class SGate(SingleQubitGate):
    """S gate (phase gate).

    Phase gate with π/2 phase shift.

    Example:
        >>> gate = SGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize an SGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = SGate()
        """
        super().__init__(GATE_S, metadata=metadata)


class TGate(SingleQubitGate):
    """T gate (π/8 gate).

    Phase gate with π/4 phase shift.

    Example:
        >>> gate = TGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a TGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = TGate()
        """
        super().__init__(GATE_T, metadata=metadata)


class SXGate(SingleQubitGate):
    """SX gate (square root of X).

    Square root of Pauli-X gate.

    Example:
        >>> gate = SXGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize an SXGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = SXGate()
        """
        super().__init__(GATE_SX, metadata=metadata)


# Export
__all__ = [
    "SingleQubitGate",
    "IdentityGate",
    "PauliXGate",
    "PauliYGate",
    "PauliZGate",
    "HadamardGate",
    "SGate",
    "TGate",
    "SXGate",
]
