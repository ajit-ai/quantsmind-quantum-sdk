"""
Quantum Dataset Module

This module provides quantum dataset definitions for the Knowledge package.

Purpose
-------
Provide quantum dataset management with quantum state and circuit support.

Responsibilities
----------------
- Define quantum dataset structure
- Support quantum state data
- Support quantum circuit data
- Support quantum measurement data
- Support quantum metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.dataset.dataset (dataset)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.dataset.dataset import Dataset
from quantsmind.knowledge.enums import DatasetType
from quantsmind.knowledge.exceptions import DatasetError
from quantsmind.knowledge.types import (
    DatasetData,
    DatasetSchema,
    ValidationResult,
)


class QuantumDataset(Dataset):
    """Concrete implementation of a quantum dataset.

    This class provides quantum dataset functionality with quantum state and circuit support.

    Attributes:
        _quantum_states: Quantum state records
        _quantum_circuits: Quantum circuit records
        _quantum_measurements: Quantum measurement records
        _qubit_count: Number of qubits

    Example:
        >>> dataset = QuantumDataset("quantum_data", qubit_count=2)
        >>> dataset.add_quantum_state({"state": [1, 0, 0, 0]})
    """

    def __init__(
        self,
        name: str,
        qubit_count: int = 1,
        schema: Optional[DatasetSchema] = None,
        data: Optional[DatasetData] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a QuantumDataset.

        Args:
            name: Dataset name
            qubit_count: Number of qubits
            schema: Dataset schema
            data: Dataset data
            metadata: Dataset metadata

        Example:
            >>> dataset = QuantumDataset("quantum_data", qubit_count=2)
        """
        super().__init__(
            name=name,
            dataset_type=DatasetType.QUANTUM,
            schema=schema,
            data=data,
            metadata=metadata,
        )
        if qubit_count < 1:
            raise DatasetError("Qubit count must be at least 1", {"qubit_count": qubit_count})

        self._qubit_count = qubit_count
        self._quantum_states: List[Dict[str, Any]] = []
        self._quantum_circuits: List[Dict[str, Any]] = []
        self._quantum_measurements: List[Dict[str, Any]] = []

    @property
    def qubit_count(self) -> int:
        """Get the qubit count.

        Returns:
            Number of qubits

        Example:
            >>> qubits = dataset.qubit_count
        """
        return self._qubit_count

    @property
    def quantum_states(self) -> List[Dict[str, Any]]:
        """Get the quantum states.

        Returns:
            Quantum state records

        Example:
            >>> states = dataset.quantum_states
        """
        return self._quantum_states.copy()

    @property
    def quantum_circuits(self) -> List[Dict[str, Any]]:
        """Get the quantum circuits.

        Returns:
            Quantum circuit records

        Example:
            >>> circuits = dataset.quantum_circuits
        """
        return self._quantum_circuits.copy()

    @property
    def quantum_measurements(self) -> List[Dict[str, Any]]:
        """Get the quantum measurements.

        Returns:
            Quantum measurement records

        Example:
            >>> measurements = dataset.quantum_measurements
        """
        return self._quantum_measurements.copy()

    def add_quantum_state(self, state: Dict[str, Any]) -> None:
        """Add a quantum state to the dataset.

        Args:
            state: Quantum state data

        Raises:
            DatasetError: If state is invalid

        Example:
            >>> dataset.add_quantum_state({"state": [1, 0, 0, 0]})
        """
        if not isinstance(state, dict):
            raise DatasetError("Quantum state must be a dictionary", {"state": state})

        state_vector = state.get("state")
        if state_vector is not None:
            expected_size = 2 ** self._qubit_count
            if len(state_vector) != expected_size:
                raise DatasetError(
                    f"State vector size must be {expected_size} for {self._qubit_count} qubits",
                    {"qubit_count": self._qubit_count, "state_size": len(state_vector)},
                )

        self._quantum_states.append(state)
        self._updated_at = self._updated_at

    def add_quantum_circuit(self, circuit: Dict[str, Any]) -> None:
        """Add a quantum circuit to the dataset.

        Args:
            circuit: Quantum circuit data

        Raises:
            DatasetError: If circuit is invalid

        Example:
            >>> dataset.add_quantum_circuit({"gates": ["H", "CNOT"]})
        """
        if not isinstance(circuit, dict):
            raise DatasetError("Quantum circuit must be a dictionary", {"circuit": circuit})

        self._quantum_circuits.append(circuit)
        self._updated_at = self._updated_at

    def add_quantum_measurement(self, measurement: Dict[str, Any]) -> None:
        """Add a quantum measurement to the dataset.

        Args:
            measurement: Quantum measurement data

        Raises:
            DatasetError: If measurement is invalid

        Example:
            >>> dataset.add_quantum_measurement({"counts": {"00": 500, "11": 500}})
        """
        if not isinstance(measurement, dict):
            raise DatasetError("Quantum measurement must be a dictionary", {"measurement": measurement})

        self._quantum_measurements.append(measurement)
        self._updated_at = self._updated_at

    def get_quantum_states_by_circuit(self, circuit_id: str) -> List[Dict[str, Any]]:
        """Get quantum states for a specific circuit.

        Args:
            circuit_id: Circuit ID

        Returns:
            Quantum state records

        Example:
            >>> states = dataset.get_quantum_states_by_circuit("circuit_001")
        """
        return [state for state in self._quantum_states if state.get("circuit_id") == circuit_id]

    def get_measurements_by_circuit(self, circuit_id: str) -> List[Dict[str, Any]]:
        """Get measurements for a specific circuit.

        Args:
            circuit_id: Circuit ID

        Returns:
            Measurement records

        Example:
            >>> measurements = dataset.get_measurements_by_circuit("circuit_001")
        """
        return [m for m in self._quantum_measurements if m.get("circuit_id") == circuit_id]

    def calculate_fidelity(self, state1: List[float], state2: List[float]) -> float:
        """Calculate fidelity between two quantum states.

        Args:
            state1: First state vector
            state2: Second state vector

        Returns:
            Fidelity value

        Example:
            >>> fidelity = dataset.calculate_fidelity([1, 0], [1, 0])
        """
        import math

        if len(state1) != len(state2):
            raise DatasetError("State vectors must have the same length")

        # Calculate overlap
        overlap = sum(complex(s1) * complex(s2).conjugate() for s1, s2 in zip(state1, state2))
        fidelity = abs(overlap) ** 2
        return fidelity

    def validate(self) -> ValidationResult:
        """Validate the quantum dataset.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = dataset.validate()
        """
        errors = []

        # Validate base dataset
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate qubit count
        if self._qubit_count < 1:
            errors.append("Qubit count must be at least 1")

        # Validate quantum states
        for i, state in enumerate(self._quantum_states):
            state_vector = state.get("state")
            if state_vector is not None:
                expected_size = 2 ** self._qubit_count
                if len(state_vector) != expected_size:
                    errors.append(f"Quantum state {i} has incorrect size")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dataset definition

        Example:
            >>> data = dataset.to_dict()
        """
        data = super().to_dict()
        data.update({
            "qubit_count": self._qubit_count,
            "quantum_states_count": len(self._quantum_states),
            "quantum_circuits_count": len(self._quantum_circuits),
            "quantum_measurements_count": len(self._quantum_measurements),
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(dataset)
        """
        return f"QuantumDataset(id={self._id}, name={self._name}, qubits={self._qubit_count}, states={len(self._quantum_states)})"


# Export
__all__ = [
    "QuantumDataset",
]
