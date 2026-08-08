"""
Measurement Module

This module provides measurement definitions for the Quantum package.

Purpose
-------
Provide measurement management for quantum computing operations.

Responsibilities
----------------
- Define measurement structure
- Support measurement operations
- Support measurement validation
- Support measurement metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.interfaces (quantum interfaces)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.quantum.algorithms.enums import MeasurementType
from quantsmind.quantum.algorithms.exceptions import MeasurementError
from quantsmind.quantum.algorithms.interfaces import IMeasurement
from quantsmind.quantum.algorithms.types import MeasurementBasis, MeasurementResult, QubitIndex, QubitIndices, ValidationResult


class Measurement(IMeasurement):
    """Concrete implementation of a measurement.

    This class provides measurement functionality for quantum computing.

    Attributes:
        _name: Measurement name
        _measurement_type: Measurement type
        _qubits: Target qubits
        _basis: Measurement basis
        _clbits: Classical bits
        _metadata: Measurement metadata

    Example:
        >>> measurement = Measurement("m0", MeasurementType.PROJECTIVE)
        >>> measurement.set_basis("computational")
    """

    def __init__(
        self,
        name: str,
        measurement_type: MeasurementType,
        qubits: QubitIndices,
        basis: MeasurementBasis = "computational",
        clbits: Optional[List[int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Measurement.

        Args:
            name: Measurement name
            measurement_type: Measurement type
            qubits: Target qubits
            basis: Measurement basis
            clbits: Classical bits
            metadata: Measurement metadata

        Example:
            >>> measurement = Measurement("m0", MeasurementType.PROJECTIVE)
        """
        if not name:
            raise MeasurementError("Measurement name cannot be empty", {"name": name})

        if not qubits:
            raise MeasurementError("Qubits cannot be empty", {"qubits": qubits})

        self._name = name
        self._measurement_type = measurement_type
        self._qubits = qubits
        self._basis = basis
        self._clbits = clbits or []
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the measurement name.

        Returns:
            Measurement name

        Example:
            >>> name = measurement.name
        """
        return self._name

    @property
    def measurement_type(self) -> MeasurementType:
        """Get the measurement type.

        Returns:
            Measurement type

        Example:
            >>> mtype = measurement.measurement_type
        """
        return self._measurement_type

    @property
    def qubits(self) -> QubitIndices:
        """Get the target qubits.

        Returns:
            Qubit indices

        Example:
            >>> qubits = measurement.qubits
        """
        return self._qubits.copy()

    @property
    def basis(self) -> MeasurementBasis:
        """Get the measurement basis.

        Returns:
            Measurement basis

        Example:
            >>> basis = measurement.basis
        """
        return self._basis

    @property
    def clbits(self) -> List[int]:
        """Get the classical bits.

        Returns:
            Classical bit indices

        Example:
            >>> clbits = measurement.clbits
        """
        return self._clbits.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the measurement metadata.

        Returns:
            Measurement metadata

        Example:
            >>> metadata = measurement.metadata
        """
        return self._metadata.copy()

    def set_basis(self, basis: MeasurementBasis) -> None:
        """Set the measurement basis.

        Args:
            basis: Measurement basis

        Example:
            >>> measurement.set_basis("X")
        """
        self._basis = basis

    def set_qubits(self, qubits: QubitIndices) -> None:
        """Set the target qubits.

        Args:
            qubits: Qubit indices

        Example:
            >>> measurement.set_qubits([0, 1])
        """
        if not qubits:
            raise MeasurementError("Qubits cannot be empty", {"qubits": qubits})

        self._qubits = qubits

    def set_clbits(self, clbits: List[int]) -> None:
        """Set the classical bits.

        Args:
            clbits: Classical bit indices

        Example:
            >>> measurement.set_clbits([0, 1])
        """
        self._clbits = clbits

    def measure(self, state: Any, qubits: Optional[QubitIndices] = None) -> MeasurementResult:
        """Perform measurement on the state.

        Args:
            state: Quantum state to measure
            qubits: Qubits to measure (optional, uses default if not provided)

        Returns:
            Measurement result

        Example:
            >>> result = measurement.measure(state, [0, 1])
        """
        target_qubits = qubits if qubits is not None else self._qubits

        # Placeholder implementation - actual measurement requires state simulation
        result = {}
        for qubit in target_qubits:
            result[qubit] = 0  # Placeholder: always measure 0

        return result

    def validate(self, num_qubits: int, num_clbits: int = 0) -> ValidationResult:
        """Validate the measurement.

        Args:
            num_qubits: Number of qubits in the circuit
            num_clbits: Number of classical bits in the circuit

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = measurement.validate(2)
        """
        errors = []

        if not self._name:
            errors.append("Measurement name cannot be empty")

        for qubit in self._qubits:
            if qubit < 0 or qubit >= num_qubits:
                errors.append(f"Qubit index {qubit} out of range [0, {num_qubits})")

        for clbit in self._clbits:
            if clbit < 0 or clbit >= num_clbits:
                errors.append(f"Classical bit index {clbit} out of range [0, {num_clbits})")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Measurement definition

        Example:
            >>> data = measurement.to_dict()
        """
        return {
            "name": self._name,
            "measurement_type": self._measurement_type.value,
            "qubits": self._qubits,
            "basis": self._basis,
            "clbits": self._clbits,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(measurement)
        """
        return f"Measurement(name={self._name}, type={self._measurement_type.value}, qubits={self._qubits})"


# Export
__all__ = [
    "Measurement",
]
