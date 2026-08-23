"""
Quantum Interfaces Module

This module provides interface definitions for the Quantum package.

Purpose
-------
Provide comprehensive interface definitions for quantum computing operations.

Responsibilities
----------------
- Define quantum-specific interfaces
- Support protocol-based design
- Enable vendor-neutral abstractions

Dependencies
------------
typing (standard library)
abc (standard library)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from quantsmind.quantum.algorithms.enums import (
    BackendType,
    GateType,
    JobStatus,
    MeasurementType,
    ProviderType,
)
from quantsmind.quantum.algorithms.types import (
    BackendConfig,
    CompilerConfig,
    DensityMatrix,
    JobResult,
    MeasurementBasis,
    MeasurementResult,
    ProviderConfig,
    QubitIndex,
    QubitIndices,
    StateVector,
    ValidationResult,
)


class IQubit(ABC):
    """Interface for a qubit.

    This interface defines the contract for qubit implementations.

    Example:
        >>> class MyQubit(IQubit):
        ...     def __init__(self, index: QubitIndex):
        ...         self._index = index
        ...     @property
        ...     def index(self) -> QubitIndex:
        ...         return self._index
    """

    @property
    @abstractmethod
    def index(self) -> QubitIndex:
        """Get the qubit index.

        Returns:
            Qubit index

        Example:
            >>> idx = qubit.index
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the qubit to |0⟩ state.

        Example:
            >>> qubit.reset()
        """
        pass


class IQuantumGate(ABC):
    """Interface for a quantum gate.

    This interface defines the contract for gate implementations.

    Example:
        >>> class MyGate(IQuantumGate):
        ...     def __init__(self, name: str, gate_type: GateType):
        ...         self._name = name
        ...         self._gate_type = gate_type
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the gate name.

        Returns:
            Gate name

        Example:
            >>> name = gate.name
        """
        pass

    @property
    @abstractmethod
    def gate_type(self) -> GateType:
        """Get the gate type.

        Returns:
            Gate type

        Example:
            >>> gtype = gate.gate_type
        """
        pass

    @property
    @abstractmethod
    def num_qubits(self) -> int:
        """Get the number of qubits the gate operates on.

        Returns:
            Number of qubits

        Example:
            >>> n = gate.num_qubits
        """
        pass

    @abstractmethod
    def get_matrix(self) -> Any:
        """Get the unitary matrix representation.

        Returns:
            Unitary matrix

        Example:
            >>> matrix = gate.get_matrix()
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate the gate.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = gate.validate()
        """
        pass


class IQuantumCircuit(ABC):
    """Interface for a quantum circuit.

    This interface defines the contract for circuit implementations.

    Example:
        >>> class MyCircuit(IQuantumCircuit):
        ...     def __init__(self, num_qubits: int):
        ...         self._num_qubits = num_qubits
    """

    @property
    @abstractmethod
    def num_qubits(self) -> int:
        """Get the number of qubits in the circuit.

        Returns:
            Number of qubits

        Example:
            >>> n = circuit.num_qubits
        """
        pass

    @property
    @abstractmethod
    def depth(self) -> int:
        """Get the circuit depth.

        Returns:
            Circuit depth

        Example:
            >>> d = circuit.depth
        """
        pass

    @property
    @abstractmethod
    def num_gates(self) -> int:
        """Get the number of gates in the circuit.

        Returns:
            Number of gates

        Example:
            >>> n = circuit.num_gates
        """
        pass

    @abstractmethod
    def add_gate(self, gate: IQuantumGate, qubits: QubitIndices) -> None:
        """Add a gate to the circuit.

        Args:
            gate: Gate to add
            qubits: Target qubits

        Example:
            >>> circuit.add_gate(h_gate, [0])
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate the circuit.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = circuit.validate()
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Circuit definition

        Example:
            >>> data = circuit.to_dict()
        """
        pass


class IQuantumState(ABC):
    """Interface for a quantum state.

    This interface defines the contract for state implementations.

    Example:
        >>> class MyState(IQuantumState):
        ...     def __init__(self, state_vector: StateVector):
        ...         self._state = state_vector
    """

    @property
    @abstractmethod
    def num_qubits(self) -> int:
        """Get the number of qubits in the state.

        Returns:
            Number of qubits

        Example:
            >>> n = state.num_qubits
        """
        pass

    @abstractmethod
    def get_state_vector(self) -> StateVector:
        """Get the state vector representation.

        Returns:
            State vector

        Example:
            >>> sv = state.get_state_vector()
        """
        pass

    @abstractmethod
    def get_density_matrix(self) -> DensityMatrix:
        """Get the density matrix representation.

        Returns:
            Density matrix

        Example:
            >>> dm = state.get_density_matrix()
        """
        pass

    @abstractmethod
    def normalize(self) -> None:
        """Normalize the state.

        Example:
            >>> state.normalize()
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate the state.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = state.validate()
        """
        pass


class IMeasurement(ABC):
    """Interface for a measurement operation.

    This interface defines the contract for measurement implementations.

    Example:
        >>> class MyMeasurement(IMeasurement):
        ...     def __init__(self, measurement_type: MeasurementType):
        ...         self._type = measurement_type
    """

    @property
    @abstractmethod
    def measurement_type(self) -> MeasurementType:
        """Get the measurement type.

        Returns:
            Measurement type

        Example:
            >>> mtype = measurement.measurement_type
        """
        pass

    @abstractmethod
    def measure(self, state: IQuantumState, qubits: QubitIndices) -> MeasurementResult:
        """Perform measurement on the state.

        Args:
            state: Quantum state to measure
            qubits: Qubits to measure

        Returns:
            Measurement result

        Example:
            >>> result = measurement.measure(state, [0, 1])
        """
        pass

    @abstractmethod
    def set_basis(self, basis: MeasurementBasis) -> None:
        """Set the measurement basis.

        Args:
            basis: Measurement basis

        Example:
            >>> measurement.set_basis("X")
        """
        pass


class IQuantumBackend(ABC):
    """Interface for a quantum backend.

    This interface defines the contract for backend implementations.

    Example:
        >>> class MyBackend(IQuantumBackend):
        ...     def __init__(self, name: str, backend_type: BackendType):
        ...         self._name = name
        ...         self._type = backend_type
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the backend name.

        Returns:
            Backend name

        Example:
            >>> name = backend.name
        """
        pass

    @property
    @abstractmethod
    def backend_type(self) -> BackendType:
        """Get the backend type.

        Returns:
            Backend type

        Example:
            >>> btype = backend.backend_type
        """
        pass

    @property
    @abstractmethod
    def num_qubits(self) -> int:
        """Get the number of available qubits.

        Returns:
            Number of qubits

        Example:
            >>> n = backend.num_qubits
        """
        pass

    @abstractmethod
    def run(self, circuit: IQuantumCircuit, shots: int = 1024) -> JobResult:
        """Run a circuit on the backend.

        Args:
            circuit: Circuit to run
            shots: Number of shots

        Returns:
            Job result

        Example:
            >>> result = backend.run(circuit, shots=1000)
        """
        pass

    @abstractmethod
    def configure(self, config: BackendConfig) -> None:
        """Configure the backend.

        Args:
            config: Backend configuration

        Example:
            >>> backend.configure({"optimization_level": 2})
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate the backend.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = backend.validate()
        """
        pass


class IQuantumProvider(ABC):
    """Interface for a quantum provider.

    This interface defines the contract for provider implementations.

    Example:
        >>> class MyProvider(IQuantumProvider):
        ...     def __init__(self, name: str, provider_type: ProviderType):
        ...         self._name = name
        ...         self._type = provider_type
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name

        Example:
            >>> name = provider.name
        """
        pass

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Get the provider type.

        Returns:
            Provider type

        Example:
            >>> ptype = provider.provider_type
        """
        pass

    @abstractmethod
    def get_backends(self) -> list[IQuantumBackend]:
        """Get available backends.

        Returns:
            List of backends

        Example:
            >>> backends = provider.get_backends()
        """
        pass

    @abstractmethod
    def get_backend(self, name: str) -> IQuantumBackend | None:
        """Get a specific backend.

        Args:
            name: Backend name

        Returns:
            Backend or None

        Example:
            >>> backend = provider.get_backend("ibmq_manila")
        """
        pass

    @abstractmethod
    def authenticate(self, credentials: dict[str, Any]) -> bool:
        """Authenticate with the provider.

        Args:
            credentials: Authentication credentials

        Returns:
            True if authenticated

        Example:
            >>> success = provider.authenticate({"token": "my_token"})
        """
        pass

    @abstractmethod
    def configure(self, config: ProviderConfig) -> None:
        """Configure the provider.

        Args:
            config: Provider configuration

        Example:
            >>> provider.configure({"region": "us-east"})
        """
        pass


class IQuantumCompiler(ABC):
    """Interface for a quantum compiler.

    This interface defines the contract for compiler implementations.

    Example:
        >>> class MyCompiler(IQuantumCompiler):
        ...     def transpile(self, circuit: IQuantumCircuit, backend: IQuantumBackend) -> IQuantumCircuit:
        ...         return circuit
    """

    @abstractmethod
    def transpile(self, circuit: IQuantumCircuit, backend: IQuantumBackend) -> IQuantumCircuit:
        """Transpile a circuit for a backend.

        Args:
            circuit: Circuit to transpile
            backend: Target backend

        Returns:
            Transpiled circuit

        Example:
            >>> transpiled = compiler.transpile(circuit, backend)
        """
        pass

    @abstractmethod
    def optimize(self, circuit: IQuantumCircuit, level: int = 1) -> IQuantumCircuit:
        """Optimize a circuit.

        Args:
            circuit: Circuit to optimize
            level: Optimization level

        Returns:
            Optimized circuit

        Example:
            >>> optimized = compiler.optimize(circuit, level=2)
        """
        pass

    @abstractmethod
    def configure(self, config: CompilerConfig) -> None:
        """Configure the compiler.

        Args:
            config: Compiler configuration

        Example:
            >>> compiler.configure({"optimization_level": 2})
        """
        pass


class IQuantumJob(ABC):
    """Interface for a quantum job.

    This interface defines the contract for job implementations.

    Example:
        >>> class MyJob(IQuantumJob):
        ...     def __init__(self, job_id: str):
        ...         self._id = job_id
    """

    @property
    @abstractmethod
    def job_id(self) -> str:
        """Get the job ID.

        Returns:
            Job ID

        Example:
            >>> jid = job.job_id
        """
        pass

    @property
    @abstractmethod
    def status(self) -> JobStatus:
        """Get the job status.

        Returns:
            Job status

        Example:
            >>> status = job.status
        """
        pass

    @abstractmethod
    def cancel(self) -> bool:
        """Cancel the job.

        Returns:
            True if cancelled

        Example:
            >>> cancelled = job.cancel()
        """
        pass

    @abstractmethod
    def result(self) -> JobResult | None:
        """Get the job result.

        Returns:
            Job result or None

        Example:
            >>> result = job.result()
        """
        pass

    @abstractmethod
    def wait(self, timeout: int | None = None) -> JobResult:
        """Wait for the job to complete.

        Args:
            timeout: Timeout in seconds

        Returns:
            Job result

        Example:
            >>> result = job.wait(timeout=300)
        """
        pass


# Export
__all__ = [
    "IQubit",
    "IQuantumGate",
    "IQuantumCircuit",
    "IQuantumState",
    "IMeasurement",
    "IQuantumBackend",
    "IQuantumProvider",
    "IQuantumCompiler",
    "IQuantumJob",
]
