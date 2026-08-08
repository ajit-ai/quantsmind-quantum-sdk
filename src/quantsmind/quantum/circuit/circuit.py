"""
Circuit Module

This module provides circuit definitions for the Quantum package.

Purpose
-------
Provide circuit management for quantum computing operations.

Responsibilities
----------------
- Define circuit structure
- Support circuit operations
- Support circuit validation
- Support circuit metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.interfaces (quantum interfaces)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.gate.gate (gate module)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.quantum.algorithms.exceptions import CircuitError
from quantsmind.quantum.algorithms.interfaces import IQuantumCircuit
from quantsmind.quantum.algorithms.types import QubitIndex, QubitIndices, ValidationResult
from quantsmind.quantum.gate.gate import QuantumGate


class QuantumCircuit(IQuantumCircuit):
    """Concrete implementation of a quantum circuit.

    This class provides circuit functionality for quantum computing.

    Attributes:
        _name: Circuit name
        _num_qubits: Number of qubits
        _gates: List of gates in the circuit
        _qubit_indices: Qubit indices for each gate
        _metadata: Circuit metadata

    Example:
        >>> circuit = QuantumCircuit("bell_state", 2)
        >>> circuit.add_gate(h_gate, [0])
    """

    def __init__(
        self,
        name: str,
        num_qubits: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a QuantumCircuit.

        Args:
            name: Circuit name
            num_qubits: Number of qubits
            metadata: Circuit metadata

        Example:
            >>> circuit = QuantumCircuit("bell_state", 2)
        """
        if not name:
            raise CircuitError("Circuit name cannot be empty", {"name": name})

        if num_qubits <= 0:
            raise CircuitError("Number of qubits must be positive", {"num_qubits": num_qubits})

        self._name = name
        self._num_qubits = num_qubits
        self._gates: List[QuantumGate] = []
        self._qubit_indices: List[QubitIndices] = []
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the circuit name.

        Returns:
            Circuit name

        Example:
            >>> name = circuit.name
        """
        return self._name

    @property
    def num_qubits(self) -> int:
        """Get the number of qubits in the circuit.

        Returns:
            Number of qubits

        Example:
            >>> n = circuit.num_qubits
        """
        return self._num_qubits

    @property
    def depth(self) -> int:
        """Get the circuit depth.

        Returns:
            Circuit depth

        Example:
            >>> d = circuit.depth
        """
        # Placeholder implementation - actual depth calculation requires scheduling
        return len(self._gates)

    @property
    def num_gates(self) -> int:
        """Get the number of gates in the circuit.

        Returns:
            Number of gates

        Example:
            >>> n = circuit.num_gates
        """
        return len(self._gates)

    @property
    def gates(self) -> List[QuantumGate]:
        """Get the gates in the circuit.

        Returns:
            List of gates

        Example:
            >>> gates = circuit.gates
        """
        return self._gates.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the circuit metadata.

        Returns:
            Circuit metadata

        Example:
            >>> metadata = circuit.metadata
        """
        return self._metadata.copy()

    def add_gate(self, gate: QuantumGate, qubits: QubitIndices) -> None:
        """Add a gate to the circuit.

        Args:
            gate: Gate to add
            qubits: Target qubits

        Example:
            >>> circuit.add_gate(h_gate, [0])
        """
        if gate.num_qubits != len(qubits):
            raise CircuitError(f"Gate requires {gate.num_qubits} qubits, but {len(qubits)} provided", {"gate": gate.name})

        for qubit in qubits:
            if qubit < 0 or qubit >= self._num_qubits:
                raise CircuitError(f"Qubit index {qubit} out of range [0, {self._num_qubits})", {"qubit": qubit})

        self._gates.append(gate)
        self._qubit_indices.append(qubits)

    def remove_gate(self, index: int) -> bool:
        """Remove a gate from the circuit.

        Args:
            index: Gate index

        Returns:
            True if removed

        Example:
            >>> removed = circuit.remove_gate(0)
        """
        if 0 <= index < len(self._gates):
            del self._gates[index]
            del self._qubit_indices[index]
            return True
        return False

    def get_gate(self, index: int) -> Optional[QuantumGate]:
        """Get a gate by index.

        Args:
            index: Gate index

        Returns:
            Gate or None

        Example:
            >>> gate = circuit.get_gate(0)
        """
        if 0 <= index < len(self._gates):
            return self._gates[index]
        return None

    def get_gate_qubits(self, index: int) -> Optional[QubitIndices]:
        """Get the qubits for a gate.

        Args:
            index: Gate index

        Returns:
            Qubit indices or None

        Example:
            >>> qubits = circuit.get_gate_qubits(0)
        """
        if 0 <= index < len(self._qubit_indices):
            return self._qubit_indices[index]
        return None

    def clear(self) -> None:
        """Clear all gates from the circuit.

        Example:
            >>> circuit.clear()
        """
        self._gates.clear()
        self._qubit_indices.clear()

    def inverse(self) -> "QuantumCircuit":
        """Create the inverse of the circuit.

        Returns:
            Inverse circuit

        Example:
            >>> inverse_circuit = circuit.inverse()
        """
        inverse_circuit = QuantumCircuit(f"{self._name}_inverse", self._num_qubits, self._metadata.copy())
        
        # Add gates in reverse order with inverse gates
        for gate, qubits in reversed(list(zip(self._gates, self._qubit_indices))):
            # Placeholder - actual inverse gate creation depends on gate type
            inverse_circuit.add_gate(gate, qubits)
        
        return inverse_circuit

    def compose(self, other: "QuantumCircuit") -> "QuantumCircuit":
        """Compose this circuit with another.

        Args:
            other: Other circuit to compose with

        Returns:
            Composed circuit

        Example:
            >>> composed = circuit.compose(other_circuit)
        """
        if self._num_qubits != other.num_qubits:
            raise CircuitError("Cannot compose circuits with different qubit counts", {"this": self._num_qubits, "other": other.num_qubits})

        composed = QuantumCircuit(f"{self._name}_{other.name}", self._num_qubits)
        
        # Add gates from this circuit
        for gate, qubits in zip(self._gates, self._qubit_indices):
            composed.add_gate(gate, qubits)
        
        # Add gates from other circuit
        for gate, qubits in zip(other.gates, other._qubit_indices):
            composed.add_gate(gate, qubits)
        
        return composed

    def validate(self) -> ValidationResult:
        """Validate the circuit.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = circuit.validate()
        """
        errors = []

        if not self._name:
            errors.append("Circuit name cannot be empty")

        if self._num_qubits <= 0:
            errors.append("Number of qubits must be positive")

        # Validate all gates
        for i, gate in enumerate(self._gates):
            is_valid, gate_errors = gate.validate()
            errors.extend([f"Gate {i}: {err}" for err in gate_errors])

        # Validate qubit indices
        for i, qubits in enumerate(self._qubit_indices):
            for qubit in qubits:
                if qubit < 0 or qubit >= self._num_qubits:
                    errors.append(f"Gate {i}: Qubit index {qubit} out of range")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Circuit definition

        Example:
            >>> data = circuit.to_dict()
        """
        return {
            "name": self._name,
            "num_qubits": self._num_qubits,
            "depth": self.depth,
            "num_gates": self.num_gates,
            "gates": [{"gate": gate.name, "qubits": qubits} for gate, qubits in zip(self._gates, self._qubit_indices)],
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(circuit)
        """
        return f"QuantumCircuit(name={self._name}, num_qubits={self._num_qubits}, gates={self.num_gates})"
