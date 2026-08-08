"""
Quantum Validators Module

This module provides validator definitions for the Quantum package.

Purpose
-------
Provide comprehensive validator definitions for quantum computing operations.

Responsibilities
----------------
- Define quantum-specific validators
- Support circuit validation
- Support state validation
- Support gate validation

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.constants (quantum constants)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.quantum.algorithms.constants import (
    MAX_GATE_COUNT,
    MAX_QUBITS,
    MAX_SHOTS,
    MIN_GATE_COUNT,
    MIN_QUBITS,
    MIN_SHOTS,
)
from quantsmind.quantum.algorithms.enums import GateType
from quantsmind.quantum.algorithms.exceptions import ValidationError
from quantsmind.quantum.algorithms.types import QubitIndex, ValidationResult


class QuantumValidator:
    """Base validator for quantum objects.

    This class provides validator functionality for quantum object validation.

    Example:
        >>> validator = QuantumValidator()
        >>> is_valid, errors = validator.validate_qubit_index(0, 5)
    """

    def validate_qubit_index(self, index: QubitIndex, max_qubits: int) -> ValidationResult:
        """Validate a qubit index.

        Args:
            index: Qubit index
            max_qubits: Maximum number of qubits

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_qubit_index(0, 5)
        """
        errors = []

        if index < 0:
            errors.append(f"Qubit index cannot be negative: {index}")

        if index >= max_qubits:
            errors.append(f"Qubit index {index} exceeds maximum {max_qubits}")

        return (len(errors) == 0, errors)

    def validate_qubit_count(self, num_qubits: int) -> ValidationResult:
        """Validate the number of qubits.

        Args:
            num_qubits: Number of qubits

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_qubit_count(5)
        """
        errors = []

        if num_qubits < MIN_QUBITS:
            errors.append(f"Number of qubits {num_qubits} is below minimum {MIN_QUBITS}")

        if num_qubits > MAX_QUBITS:
            errors.append(f"Number of qubits {num_qubits} exceeds maximum {MAX_QUBITS}")

        return (len(errors) == 0, errors)

    def validate_shots(self, shots: int) -> ValidationResult:
        """Validate the number of shots.

        Args:
            shots: Number of shots

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_shots(1024)
        """
        errors = []

        if shots < MIN_SHOTS:
            errors.append(f"Number of shots {shots} is below minimum {MIN_SHOTS}")

        if shots > MAX_SHOTS:
            errors.append(f"Number of shots {shots} exceeds maximum {MAX_SHOTS}")

        return (len(errors) == 0, errors)

    def validate_gate_count(self, gate_count: int) -> ValidationResult:
        """Validate the number of gates.

        Args:
            gate_count: Number of gates

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_gate_count(100)
        """
        errors = []

        if gate_count < MIN_GATE_COUNT:
            errors.append(f"Number of gates {gate_count} is below minimum {MIN_GATE_COUNT}")

        if gate_count > MAX_GATE_COUNT:
            errors.append(f"Number of gates {gate_count} exceeds maximum {MAX_GATE_COUNT}")

        return (len(errors) == 0, errors)


class GateValidator(QuantumValidator):
    """Validator for quantum gates.

    This class provides validator functionality for gate validation.

    Example:
        >>> validator = GateValidator()
        >>> is_valid, errors = validator.validate(gate)
    """

    def validate(self, gate: Any) -> ValidationResult:
        """Validate a gate.

        Args:
            gate: Gate to validate

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate(gate)
        """
        errors = []

        if not hasattr(gate, "name"):
            errors.append("Gate must have a 'name' attribute")

        if not hasattr(gate, "gate_type"):
            errors.append("Gate must have a 'gate_type' attribute")

        if not hasattr(gate, "num_qubits"):
            errors.append("Gate must have a 'num_qubits' attribute")

        if hasattr(gate, "num_qubits"):
            is_valid, qubit_errors = self.validate_qubit_count(gate.num_qubits)
            errors.extend(qubit_errors)

        return (len(errors) == 0, errors)

    def validate_gate_matrix(self, matrix: Any, num_qubits: int) -> ValidationResult:
        """Validate a gate matrix.

        Args:
            matrix: Gate matrix
            num_qubits: Number of qubits

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_gate_matrix(matrix, 1)
        """
        errors = []

        expected_size = 2 ** num_qubits

        if matrix is None:
            errors.append("Gate matrix cannot be None")
            return (False, errors)

        try:
            rows = len(matrix)
            if rows != expected_size:
                errors.append(f"Gate matrix has {rows} rows, expected {expected_size}")

            for row in matrix:
                if len(row) != expected_size:
                    errors.append(f"Gate matrix row has {len(row)} columns, expected {expected_size}")
        except Exception as e:
            errors.append(f"Gate matrix validation failed: {str(e)}")

        return (len(errors) == 0, errors)

    def validate_gate_parameters(self, parameters: Dict[str, Any], gate_type: GateType) -> ValidationResult:
        """Validate gate parameters.

        Args:
            parameters: Gate parameters
            gate_type: Gate type

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_gate_parameters({"theta": 1.57}, GateType.PARAMETERIZED)
        """
        errors = []

        if gate_type == GateType.PARAMETERIZED and not parameters:
            errors.append("Parameterized gate must have parameters")

        return (len(errors) == 0, errors)


class CircuitValidator(QuantumValidator):
    """Validator for quantum circuits.

    This class provides validator functionality for circuit validation.

    Example:
        >>> validator = CircuitValidator()
        >>> is_valid, errors = validator.validate(circuit)
    """

    def validate(self, circuit: Any) -> ValidationResult:
        """Validate a circuit.

        Args:
            circuit: Circuit to validate

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate(circuit)
        """
        errors = []

        if not hasattr(circuit, "num_qubits"):
            errors.append("Circuit must have a 'num_qubits' attribute")

        if hasattr(circuit, "num_qubits"):
            is_valid, qubit_errors = self.validate_qubit_count(circuit.num_qubits)
            errors.extend(qubit_errors)

        if not hasattr(circuit, "depth"):
            errors.append("Circuit must have a 'depth' attribute")

        if not hasattr(circuit, "num_gates"):
            errors.append("Circuit must have a 'num_gates' attribute")

        if hasattr(circuit, "num_gates"):
            is_valid, gate_errors = self.validate_gate_count(circuit.num_gates)
            errors.extend(gate_errors)

        return (len(errors) == 0, errors)

    def validate_gate_application(self, gate: Any, qubits: List[int], circuit_num_qubits: int) -> ValidationResult:
        """Validate gate application to qubits.

        Args:
            gate: Gate to apply
            qubits: Target qubits
            circuit_num_qubits: Number of qubits in circuit

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_gate_application(gate, [0, 1], 2)
        """
        errors = []

        if not qubits:
            errors.append("Gate must target at least one qubit")

        if len(qubits) != len(set(qubits)):
            errors.append("Gate cannot target the same qubit multiple times")

        for qubit in qubits:
            is_valid, qubit_errors = self.validate_qubit_index(qubit, circuit_num_qubits)
            errors.extend(qubit_errors)

        if hasattr(gate, "num_qubits") and len(qubits) != gate.num_qubits:
            errors.append(f"Gate requires {gate.num_qubits} qubits, but {len(qubits)} provided")

        return (len(errors) == 0, errors)


class StateValidator(QuantumValidator):
    """Validator for quantum states.

    This class provides validator functionality for state validation.

    Example:
        >>> validator = StateValidator()
        >>> is_valid, errors = validator.validate(state)
    """

    def validate(self, state: Any) -> ValidationResult:
        """Validate a state.

        Args:
            state: State to validate

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate(state)
        """
        errors = []

        if not hasattr(state, "num_qubits"):
            errors.append("State must have a 'num_qubits' attribute")

        if hasattr(state, "num_qubits"):
            is_valid, qubit_errors = self.validate_qubit_count(state.num_qubits)
            errors.extend(qubit_errors)

        return (len(errors) == 0, errors)

    def validate_state_vector(self, state_vector: Any, num_qubits: int) -> ValidationResult:
        """Validate a state vector.

        Args:
            state_vector: State vector to validate
            num_qubits: Number of qubits

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_state_vector(state_vector, 1)
        """
        errors = []

        expected_size = 2 ** num_qubits

        if state_vector is None:
            errors.append("State vector cannot be None")
            return (False, errors)

        try:
            if len(state_vector) != expected_size:
                errors.append(f"State vector has {len(state_vector)} elements, expected {expected_size}")

            # Check normalization
            norm_squared = sum(abs(x) ** 2 for x in state_vector)
            if abs(norm_squared - 1.0) > 1e-6:
                errors.append(f"State vector not normalized: norm^2 = {norm_squared}")
        except Exception as e:
            errors.append(f"State vector validation failed: {str(e)}")

        return (len(errors) == 0, errors)

    def validate_density_matrix(self, density_matrix: Any, num_qubits: int) -> ValidationResult:
        """Validate a density matrix.

        Args:
            density_matrix: Density matrix to validate
            num_qubits: Number of qubits

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_density_matrix(density_matrix, 1)
        """
        errors = []

        expected_size = 2 ** num_qubits

        if density_matrix is None:
            errors.append("Density matrix cannot be None")
            return (False, errors)

        try:
            rows = len(density_matrix)
            if rows != expected_size:
                errors.append(f"Density matrix has {rows} rows, expected {expected_size}")

            for row in density_matrix:
                if len(row) != expected_size:
                    errors.append(f"Density matrix row has {len(row)} columns, expected {expected_size}")

            # Check trace = 1
            trace = sum(density_matrix[i][i] for i in range(expected_size))
            if abs(trace - 1.0) > 1e-6:
                errors.append(f"Density matrix trace is {trace}, expected 1.0")
        except Exception as e:
            errors.append(f"Density matrix validation failed: {str(e)}")

        return (len(errors) == 0, errors)


class MeasurementValidator(QuantumValidator):
    """Validator for measurement operations.

    This class provides validator functionality for measurement validation.

    Example:
        >>> validator = MeasurementValidator()
        >>> is_valid, errors = validator.validate(measurement)
    """

    def validate(self, measurement: Any) -> ValidationResult:
        """Validate a measurement.

        Args:
            measurement: Measurement to validate

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate(measurement)
        """
        errors = []

        if not hasattr(measurement, "measurement_type"):
            errors.append("Measurement must have a 'measurement_type' attribute")

        return (len(errors) == 0, errors)

    def validate_measurement_qubits(self, qubits: List[int], circuit_num_qubits: int) -> ValidationResult:
        """Validate measurement qubits.

        Args:
            qubits: Qubits to measure
            circuit_num_qubits: Number of qubits in circuit

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_measurement_qubits([0, 1], 2)
        """
        errors = []

        if not qubits:
            errors.append("Measurement must target at least one qubit")

        for qubit in qubits:
            is_valid, qubit_errors = self.validate_qubit_index(qubit, circuit_num_qubits)
            errors.extend(qubit_errors)

        return (len(errors) == 0, errors)


# Export
__all__ = [
    "QuantumValidator",
    "GateValidator",
    "CircuitValidator",
    "StateValidator",
    "MeasurementValidator",
]
