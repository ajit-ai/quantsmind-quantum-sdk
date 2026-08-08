"""
Controlled Gate Module

This module provides controlled gate definitions for the Quantum package.

Purpose
-------
Provide controlled gate management for quantum computing operations.

Responsibilities
----------------
- Define controlled gate structure
- Support controlled gate operations
- Support controlled gate validation
- Support controlled gate metadata

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

from typing import Any, Dict, List, Optional

from quantsmind.quantum.algorithms.constants import GATE_CCX, GATE_CX, GATE_CY, GATE_CZ
from quantsmind.quantum.algorithms.enums import GateType
from quantsmind.quantum.algorithms.exceptions import GateError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.gate.gate import QuantumGate


class ControlledGate(QuantumGate):
    """Concrete implementation of a controlled gate.

    This class provides controlled gate functionality for quantum computing.
    Controlled gates apply a target gate conditionally based on control qubits.

    Attributes:
        _name: Gate name
        _gate_type: Gate type
        _num_qubits: Number of qubits
        _num_controls: Number of control qubits
        _target_gate: Target gate
        _matrix: Unitary matrix
        _metadata: Gate metadata

    Example:
        >>> gate = ControlledGate("CX", 2, 1)
    """

    def __init__(
        self,
        name: str,
        num_qubits: int,
        num_controls: int,
        target_gate: Optional[QuantumGate] = None,
        parameters: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a ControlledGate.

        Args:
            name: Gate name
            num_qubits: Number of qubits
            num_controls: Number of control qubits
            target_gate: Target gate
            parameters: Gate parameters
            metadata: Gate metadata

        Example:
            >>> gate = ControlledGate("CX", 2, 1)
        """
        super().__init__(name, GateType.CONTROLLED.value, num_qubits, parameters, metadata)
        self._num_controls = num_controls
        self._target_gate = target_gate
        self._initialize_matrix()

    @property
    def num_controls(self) -> int:
        """Get the number of control qubits.

        Returns:
            Number of control qubits

        Example:
            >>> n = gate.num_controls
        """
        return self._num_controls

    @property
    def target_gate(self) -> Optional[QuantumGate]:
        """Get the target gate.

        Returns:
            Target gate

        Example:
            >>> target = gate.target_gate
        """
        return self._target_gate

    def set_target_gate(self, target_gate: QuantumGate) -> None:
        """Set the target gate.

        Args:
            target_gate: Target gate

        Example:
            >>> gate.set_target_gate(pauli_x)
        """
        self._target_gate = target_gate

    def _initialize_matrix(self) -> None:
        """Initialize the gate matrix based on the gate name.

        Example:
            >>> gate._initialize_matrix()
        """
        if self._name == GATE_CX and self._num_qubits == 2 and self._num_controls == 1:
            # CNOT gate matrix
            self.set_matrix([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0],
            ])
        elif self._name == GATE_CY and self._num_qubits == 2 and self._num_controls == 1:
            # CY gate matrix
            self.set_matrix([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, -1j],
                [0, 0, 1j, 0],
            ])
        elif self._name == GATE_CZ and self._num_qubits == 2 and self._num_controls == 1:
            # CZ gate matrix
            self.set_matrix([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, -1],
            ])
        elif self._name == GATE_CCX and self._num_qubits == 3 and self._num_controls == 2:
            # CCX (Toffoli) gate matrix
            self.set_matrix([
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0, 0, 1, 0],
            ])
        else:
            # Custom gate, matrix must be set manually
            pass

    def validate(self) -> ValidationResult:
        """Validate the controlled gate.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = gate.validate()
        """
        errors = []

        # Validate base gate
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if self._num_controls < 1:
            errors.append(f"Controlled gate must have at least 1 control qubit, got {self._num_controls}")

        if self._num_controls >= self._num_qubits:
            errors.append(f"Number of controls {self._num_controls} must be less than total qubits {self._num_qubits}")

        if self._target_gate is not None:
            is_valid, target_errors = self._target_gate.validate()
            errors.extend(target_errors)

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Controlled gate definition

        Example:
            >>> data = gate.to_dict()
        """
        data = super().to_dict()
        data["num_controls"] = self._num_controls
        data["has_target_gate"] = self._target_gate is not None
        if self._target_gate:
            data["target_gate"] = self._target_gate.name
        return data


class CNOTGate(ControlledGate):
    """CNOT gate (CX).

    Controlled-NOT gate.

    Example:
        >>> gate = CNOTGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a CNOTGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = CNOTGate()
        """
        super().__init__(GATE_CX, 2, 1, metadata=metadata)


class CYGate(ControlledGate):
    """CY gate.

    Controlled-Y gate.

    Example:
        >>> gate = CYGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a CYGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = CYGate()
        """
        super().__init__(GATE_CY, 2, 1, metadata=metadata)


class CZGate(ControlledGate):
    """CZ gate.

    Controlled-Z gate.

    Example:
        >>> gate = CZGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a CZGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = CZGate()
        """
        super().__init__(GATE_CZ, 2, 1, metadata=metadata)


class CCXGate(ControlledGate):
    """CCX gate (Toffoli).

    Controlled-controlled-NOT gate.

    Example:
        >>> gate = CCXGate()
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a CCXGate.

        Args:
            metadata: Gate metadata

        Example:
            >>> gate = CCXGate()
        """
        super().__init__(GATE_CCX, 3, 2, metadata=metadata)


# Export
__all__ = [
    "ControlledGate",
    "CNOTGate",
    "CYGate",
    "CZGate",
    "CCXGate",
]
