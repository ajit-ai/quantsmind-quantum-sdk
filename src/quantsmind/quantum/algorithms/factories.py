"""
Quantum Factories Module

This module provides factory definitions for the Quantum package.

Purpose
-------
Provide comprehensive factory definitions for quantum computing operations.

Responsibilities
----------------
- Define quantum-specific factories
- Support object creation
- Enable flexible instantiation

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from quantsmind.quantum.algorithms.enums import GateType, StateType
from quantsmind.quantum.algorithms.exceptions import QuantumError


class QuantumFactory:
    """Base factory for quantum objects.

    This class provides factory functionality for quantum object creation.

    Example:
        >>> factory = QuantumFactory()
        >>> gate = factory.create_gate("H", GateType.SINGLE_QUBIT)
    """

    def __init__(self) -> None:
        """Initialize a QuantumFactory.

        Example:
            >>> factory = QuantumFactory()
        """
        self._gate_registry: Dict[str, Type[Any]] = {}
        self._state_registry: Dict[str, Type[Any]] = {}

    def register_gate(self, name: str, gate_class: Type[Any]) -> None:
        """Register a gate class.

        Args:
            name: Gate name
            gate_class: Gate class

        Example:
            >>> factory.register_gate("H", HadamardGate)
        """
        self._gate_registry[name] = gate_class

    def register_state(self, name: str, state_class: Type[Any]) -> None:
        """Register a state class.

        Args:
            name: State name
            state_class: State class

        Example:
            >>> factory.register_state("zero", ZeroState)
        """
        self._state_registry[name] = state_class

    def create_gate(self, name: str, gate_type: GateType, **kwargs: Any) -> Any:
        """Create a gate instance.

        Args:
            name: Gate name
            gate_type: Gate type
            **kwargs: Additional parameters

        Returns:
            Gate instance

        Example:
            >>> gate = factory.create_gate("H", GateType.SINGLE_QUBIT)
        """
        if name not in self._gate_registry:
            raise QuantumError(f"Gate '{name}' not registered", {"gate": name})

        gate_class = self._gate_registry[name]
        return gate_class(gate_type=gate_type, **kwargs)

    def create_state(self, name: str, state_type: StateType, **kwargs: Any) -> Any:
        """Create a state instance.

        Args:
            name: State name
            state_type: State type
            **kwargs: Additional parameters

        Returns:
            State instance

        Example:
            >>> state = factory.create_state("zero", StateType.BASIS)
        """
        if name not in self._state_registry:
            raise QuantumError(f"State '{name}' not registered", {"state": name})

        state_class = self._state_registry[name]
        return state_class(state_type=state_type, **kwargs)

    def list_gates(self) -> List[str]:
        """List registered gates.

        Returns:
            List of gate names

        Example:
            >>> gates = factory.list_gates()
        """
        return list(self._gate_registry.keys())

    def list_states(self) -> List[str]:
        """List registered states.

        Returns:
            List of state names

        Example:
            >>> states = factory.list_states()
        """
        return list(self._state_registry.keys())


class GateFactory(QuantumFactory):
    """Factory for creating quantum gates.

    This class provides factory functionality for gate creation.

    Example:
        >>> factory = GateFactory()
        >>> gate = factory.create_hadamard()
    """

    def create_identity(self) -> Any:
        """Create an identity gate.

        Returns:
            Identity gate

        Example:
            >>> gate = factory.create_identity()
        """
        return self.create_gate("I", GateType.SINGLE_QUBIT)

    def create_pauli_x(self) -> Any:
        """Create a Pauli-X gate.

        Returns:
            Pauli-X gate

        Example:
            >>> gate = factory.create_pauli_x()
        """
        return self.create_gate("X", GateType.SINGLE_QUBIT)

    def create_pauli_y(self) -> Any:
        """Create a Pauli-Y gate.

        Returns:
            Pauli-Y gate

        Example:
            >>> gate = factory.create_pauli_y()
        """
        return self.create_gate("Y", GateType.SINGLE_QUBIT)

    def create_pauli_z(self) -> Any:
        """Create a Pauli-Z gate.

        Returns:
            Pauli-Z gate

        Example:
            >>> gate = factory.create_pauli_z()
        """
        return self.create_gate("Z", GateType.SINGLE_QUBIT)

    def create_hadamard(self) -> Any:
        """Create a Hadamard gate.

        Returns:
            Hadamard gate

        Example:
            >>> gate = factory.create_hadamard()
        """
        return self.create_gate("H", GateType.SINGLE_QUBIT)

    def create_s_gate(self) -> Any:
        """Create an S gate.

        Returns:
            S gate

        Example:
            >>> gate = factory.create_s_gate()
        """
        return self.create_gate("S", GateType.SINGLE_QUBIT)

    def create_t_gate(self) -> Any:
        """Create a T gate.

        Returns:
            T gate

        Example:
            >>> gate = factory.create_t_gate()
        """
        return self.create_gate("T", GateType.SINGLE_QUBIT)

    def create_cnot(self) -> Any:
        """Create a CNOT gate.

        Returns:
            CNOT gate

        Example:
            >>> gate = factory.create_cnot()
        """
        return self.create_gate("CX", GateType.CONTROLLED)

    def create_swap(self) -> Any:
        """Create a SWAP gate.

        Returns:
            SWAP gate

        Example:
            >>> gate = factory.create_swap()
        """
        return self.create_gate("SWAP", GateType.MULTI_QUBIT)

    def create_rotation_x(self, theta: float) -> Any:
        """Create an RX rotation gate.

        Args:
            theta: Rotation angle

        Returns:
            RX gate

        Example:
            >>> gate = factory.create_rotation_x(math.pi/2)
        """
        return self.create_gate("RX", GateType.PARAMETERIZED, theta=theta)

    def create_rotation_y(self, theta: float) -> Any:
        """Create an RY rotation gate.

        Args:
            theta: Rotation angle

        Returns:
            RY gate

        Example:
            >>> gate = factory.create_rotation_y(math.pi/2)
        """
        return self.create_gate("RY", GateType.PARAMETERIZED, theta=theta)

    def create_rotation_z(self, theta: float) -> Any:
        """Create an RZ rotation gate.

        Args:
            theta: Rotation angle

        Returns:
            RZ gate

        Example:
            >>> gate = factory.create_rotation_z(math.pi/2)
        """
        return self.create_gate("RZ", GateType.PARAMETERIZED, theta=theta)


class StateFactory(QuantumFactory):
    """Factory for creating quantum states.

    This class provides factory functionality for state creation.

    Example:
        >>> factory = StateFactory()
        >>> state = factory.create_zero_state(1)
    """

    def create_zero_state(self, num_qubits: int) -> Any:
        """Create a zero state.

        Args:
            num_qubits: Number of qubits

        Returns:
            Zero state

        Example:
            >>> state = factory.create_zero_state(1)
        """
        return self.create_state("zero", StateType.BASIS, num_qubits=num_qubits)

    def create_one_state(self, num_qubits: int) -> Any:
        """Create a one state.

        Args:
            num_qubits: Number of qubits

        Returns:
            One state

        Example:
            >>> state = factory.create_one_state(1)
        """
        return self.create_state("one", StateType.BASIS, num_qubits=num_qubits)

    def create_plus_state(self, num_qubits: int) -> Any:
        """Create a plus state.

        Args:
            num_qubits: Number of qubits

        Returns:
            Plus state

        Example:
            >>> state = factory.create_plus_state(1)
        """
        return self.create_state("plus", StateType.STATE_VECTOR, num_qubits=num_qubits)

    def create_minus_state(self, num_qubits: int) -> Any:
        """Create a minus state.

        Args:
            num_qubits: Number of qubits

        Returns:
            Minus state

        Example:
            >>> state = factory.create_minus_state(1)
        """
        return self.create_state("minus", StateType.STATE_VECTOR, num_qubits=num_qubits)

    def create_random_state(self, num_qubits: int) -> Any:
        """Create a random state.

        Args:
            num_qubits: Number of qubits

        Returns:
            Random state

        Example:
            >>> state = factory.create_random_state(2)
        """
        return self.create_state("random", StateType.STATE_VECTOR, num_qubits=num_qubits)

    def create_maximally_entangled_state(self, num_qubits: int) -> Any:
        """Create a maximally entangled state.

        Args:
            num_qubits: Number of qubits

        Returns:
            Maximally entangled state

        Example:
            >>> state = factory.create_maximally_entangled_state(2)
        """
        return self.create_state("ghz", StateType.STATE_VECTOR, num_qubits=num_qubits)


class BackendFactory(QuantumFactory):
    """Factory for creating quantum backends.

    This class provides factory functionality for backend creation.

    Example:
        >>> factory = BackendFactory()
        >>> backend = factory.create_simulator("statevector")
    """

    def create_simulator(self, simulator_type: str = "statevector") -> Any:
        """Create a simulator backend.

        Args:
            simulator_type: Simulator type

        Returns:
            Simulator backend

        Example:
            >>> backend = factory.create_simulator("statevector")
        """
        return self.create_gate(f"simulator_{simulator_type}", GateType.SINGLE_QUBIT)

    def create_provider_backend(self, provider_name: str, backend_name: str) -> Any:
        """Create a provider backend.

        Args:
            provider_name: Provider name
            backend_name: Backend name

        Returns:
            Provider backend

        Example:
            >>> backend = factory.create_provider_backend("IBM", "ibmq_manila")
        """
        return self.create_gate(f"{provider_name}_{backend_name}", GateType.SINGLE_QUBIT)


# Export
__all__ = [
    "QuantumFactory",
    "GateFactory",
    "StateFactory",
    "BackendFactory",
]
