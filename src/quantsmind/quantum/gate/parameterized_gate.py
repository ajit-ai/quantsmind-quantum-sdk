"""
Parameterized Gate Module

This module provides parameterized gate definitions for the Quantum package.

Purpose
-------
Provide parameterized gate management for quantum computing operations.

Responsibilities
----------------
- Define parameterized gate structure
- Support parameterized gate operations
- Support parameterized gate validation
- Support parameterized gate metadata

Dependencies
------------
typing (standard library)
math (standard library)
quantsmind.quantum.algorithms.constants (quantum constants)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.gate.gate (gate module)
"""

from __future__ import annotations

import math
from typing import Any

from quantsmind.quantum.algorithms.constants import (
    GATE_PHASE,
    GATE_RX,
    GATE_RY,
    GATE_RZ,
    GATE_U,
)
from quantsmind.quantum.algorithms.enums import GateType
from quantsmind.quantum.algorithms.exceptions import GateError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.gate.gate import QuantumGate


class ParameterizedGate(QuantumGate):
    """Concrete implementation of a parameterized gate.

    This class provides parameterized gate functionality for quantum computing.
    Parameterized gates have parameters that can be varied.

    Attributes:
        _name: Gate name
        _gate_type: Gate type
        _num_qubits: Number of qubits
        _parameters: Gate parameters
        _matrix: Unitary matrix
        _metadata: Gate metadata

    Example:
        >>> gate = ParameterizedGate("RX", {"theta": 1.57})
    """

    def __init__(
        self,
        name: str,
        parameters: dict[str, float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a ParameterizedGate.

        Args:
            name: Gate name
            parameters: Gate parameters
            metadata: Gate metadata

        Example:
            >>> gate = ParameterizedGate("RX", {"theta": 1.57})
        """
        if not parameters:
            raise GateError("Parameterized gate must have parameters", {"name": name})

        super().__init__(name, GateType.PARAMETERIZED.value, 1, parameters, metadata)
        self._initialize_matrix()

    def _initialize_matrix(self) -> None:
        """Initialize the gate matrix based on the gate name and parameters.

        Example:
            >>> gate._initialize_matrix()
        """
        if self._name == GATE_RX:
            theta = self._parameters.get("theta", 0.0)
            cos_half = math.cos(theta / 2)
            sin_half = math.sin(theta / 2)
            self.set_matrix([
                [cos_half, -1j * sin_half],
                [-1j * sin_half, cos_half],
            ])
        elif self._name == GATE_RY:
            theta = self._parameters.get("theta", 0.0)
            cos_half = math.cos(theta / 2)
            sin_half = math.sin(theta / 2)
            self.set_matrix([
                [cos_half, -sin_half],
                [sin_half, cos_half],
            ])
        elif self._name == GATE_RZ:
            phi = self._parameters.get("phi", 0.0)
            self.set_matrix([
                [math.exp(-1j * phi / 2), 0],
                [0, math.exp(1j * phi / 2)],
            ])
        elif self._name == GATE_PHASE:
            phi = self._parameters.get("phi", 0.0)
            self.set_matrix([
                [1, 0],
                [0, math.exp(1j * phi)],
            ])
        elif self._name == GATE_U:
            theta = self._parameters.get("theta", 0.0)
            phi = self._parameters.get("phi", 0.0)
            lam = self._parameters.get("lambda", 0.0)
            self.set_matrix([
                [math.cos(theta / 2), -math.exp(1j * lam) * math.sin(theta / 2)],
                [math.exp(1j * phi) * math.sin(theta / 2), math.exp(1j * (phi + lam)) * math.cos(theta / 2)],
            ])
        else:
            # Custom gate, matrix must be set manually
            pass

    def update_parameter(self, key: str, value: float) -> None:
        """Update a parameter and recompute the matrix.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> gate.update_parameter("theta", 2.0)
        """
        self._parameters[key] = value
        self._initialize_matrix()

    def validate(self) -> ValidationResult:
        """Validate the parameterized gate.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = gate.validate()
        """
        errors = []

        # Validate base gate
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if not self._parameters:
            errors.append("Parameterized gate must have parameters")

        return (len(errors) == 0, errors)


class RXGate(ParameterizedGate):
    """RX gate (rotation around X axis).

    Rotation gate around the X axis.

    Example:
        >>> gate = RXGate(theta=1.57)
    """

    def __init__(self, theta: float = 0.0, metadata: dict[str, Any] | None = None) -> None:
        """Initialize an RXGate.

        Args:
            theta: Rotation angle
            metadata: Gate metadata

        Example:
            >>> gate = RXGate(theta=1.57)
        """
        super().__init__(GATE_RX, {"theta": theta}, metadata=metadata)


class RYGate(ParameterizedGate):
    """RY gate (rotation around Y axis).

    Rotation gate around the Y axis.

    Example:
        >>> gate = RYGate(theta=1.57)
    """

    def __init__(self, theta: float = 0.0, metadata: dict[str, Any] | None = None) -> None:
        """Initialize an RYGate.

        Args:
            theta: Rotation angle
            metadata: Gate metadata

        Example:
            >>> gate = RYGate(theta=1.57)
        """
        super().__init__(GATE_RY, {"theta": theta}, metadata=metadata)


class RZGate(ParameterizedGate):
    """RZ gate (rotation around Z axis).

    Rotation gate around the Z axis.

    Example:
        >>> gate = RZGate(phi=1.57)
    """

    def __init__(self, phi: float = 0.0, metadata: dict[str, Any] | None = None) -> None:
        """Initialize an RZGate.

        Args:
            phi: Rotation angle
            metadata: Gate metadata

        Example:
            >>> gate = RZGate(phi=1.57)
        """
        super().__init__(GATE_RZ, {"phi": phi}, metadata=metadata)


class PhaseGate(ParameterizedGate):
    """Phase gate.

    Applies a phase to the |1⟩ state.

    Example:
        >>> gate = PhaseGate(phi=1.57)
    """

    def __init__(self, phi: float = 0.0, metadata: dict[str, Any] | None = None) -> None:
        """Initialize a PhaseGate.

        Args:
            phi: Phase angle
            metadata: Gate metadata

        Example:
            >>> gate = PhaseGate(phi=1.57)
        """
        super().__init__(GATE_PHASE, {"phi": phi}, metadata=metadata)


class UGate(ParameterizedGate):
    """U gate (universal single-qubit gate).

    Universal single-qubit rotation gate.

    Example:
        >>> gate = UGate(theta=1.57, phi=0.0, lam=0.0)
    """

    def __init__(
        self,
        theta: float = 0.0,
        phi: float = 0.0,
        lam: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a UGate.

        Args:
            theta: Theta angle
            phi: Phi angle
            lam: Lambda angle
            metadata: Gate metadata

        Example:
            >>> gate = UGate(theta=1.57, phi=0.0, lam=0.0)
        """
        super().__init__(GATE_U, {"theta": theta, "phi": phi, "lambda": lam}, metadata=metadata)


# Export
__all__ = [
    "ParameterizedGate",
    "RXGate",
    "RYGate",
    "RZGate",
    "PhaseGate",
    "UGate",
]
