"""
Simulator Backend Module

This module provides simulator backend definitions for the Quantum package.

Purpose
-------
Provide simulator backend management for quantum computing operations.

Responsibilities
----------------
- Define simulator backend structure
- Support simulator backend operations
- Support simulator backend validation
- Support simulator backend metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.backend.backend (backend module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.enums import BackendType
from quantsmind.quantum.algorithms.exceptions import BackendError
from quantsmind.quantum.algorithms.types import BackendConfig, ValidationResult
from quantsmind.quantum.backend.backend import QuantumBackend
from quantsmind.quantum.circuit.circuit import QuantumCircuit


class SimulatorBackend(QuantumBackend):
    """Concrete implementation of a simulator backend.

    This class provides simulator backend functionality for quantum computing.

    Attributes:
        _name: Backend name
        _num_qubits: Number of qubits
        _simulator_type: Simulator type
        _configuration: Backend configuration
        _metadata: Backend metadata

    Example:
        >>> backend = SimulatorBackend("statevector", 5)
        >>> result = backend.run(circuit, shots=1024)
    """

    def __init__(
        self,
        name: str,
        num_qubits: int,
        simulator_type: str = "statevector",
        configuration: BackendConfig | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a SimulatorBackend.

        Args:
            name: Backend name
            num_qubits: Number of qubits
            simulator_type: Simulator type
            configuration: Backend configuration
            metadata: Backend metadata

        Example:
            >>> backend = SimulatorBackend("statevector", 5)
        """
        super().__init__(name, BackendType.SIMULATOR, num_qubits, configuration, metadata)
        self._simulator_type = simulator_type

    @property
    def simulator_type(self) -> str:
        """Get the simulator type.

        Returns:
            Simulator type

        Example:
            >>> stype = backend.simulator_type
        """
        return self._simulator_type

    def set_simulator_type(self, simulator_type: str) -> None:
        """Set the simulator type.

        Args:
            simulator_type: Simulator type

        Example:
            >>> backend.set_simulator_type("matrix_product_state")
        """
        valid_types = ["statevector", "unitary", "matrix_product_state", "stabilizer"]
        if simulator_type not in valid_types:
            raise BackendError(f"Invalid simulator type: {simulator_type}", {"valid_types": valid_types})

        self._simulator_type = simulator_type

    def run(self, circuit: QuantumCircuit, shots: int = 1024) -> dict[str, Any]:
        """Run a circuit on the simulator.

        Args:
            circuit: Circuit to run
            shots: Number of shots

        Returns:
            Job result

        Example:
            >>> result = backend.run(circuit, shots=1000)
        """
        # Validate circuit
        if circuit.num_qubits > self._num_qubits:
            raise BackendError(f"Circuit requires {circuit.num_qubits} qubits, backend has {self._num_qubits}", {"circuit_qubits": circuit.num_qubits, "backend_qubits": self._num_qubits})

        # Placeholder implementation - actual simulation requires quantum state simulation
        result = super().run(circuit, shots)
        result["simulator_type"] = self._simulator_type
        return result

    def validate(self) -> ValidationResult:
        """Validate the simulator backend.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = backend.validate()
        """
        errors = []

        # Validate base backend
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        valid_types = ["statevector", "unitary", "matrix_product_state", "stabilizer"]
        if self._simulator_type not in valid_types:
            errors.append(f"Invalid simulator type: {self._simulator_type}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Simulator backend definition

        Example:
            >>> data = backend.to_dict()
        """
        data = super().to_dict()
        data["simulator_type"] = self._simulator_type
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(backend)
        """
        return f"SimulatorBackend(name={self._name}, type={self._simulator_type}, qubits={self._num_qubits})"


# Export
__all__ = [
    "SimulatorBackend",
]
