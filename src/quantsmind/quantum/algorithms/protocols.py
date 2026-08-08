"""
Quantum Protocols Module

This module provides protocol definitions for the Quantum package.

Purpose
-------
Provide comprehensive protocol definitions for quantum computing operations.

Responsibilities
----------------
- Define quantum-specific protocols
- Support structural subtyping
- Enable flexible implementations

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

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
    GateParameters,
    JobResult,
    MeasurementBasis,
    MeasurementResult,
    NoiseConfig,
    ProviderConfig,
    QubitIndex,
    QubitIndices,
    StateVector,
    ValidationResult,
)


@runtime_checkable
class QubitProtocol(Protocol):
    """Protocol for a qubit.

    This protocol defines the structural contract for qubit implementations.

    Example:
        >>> class MyQubit:
        ...     def __init__(self, index: QubitIndex):
        ...         self._index = index
        ...     @property
        ...     def index(self) -> QubitIndex:
        ...         return self._index
        ...     def reset(self) -> None:
        ...         pass
    """

    @property
    def index(self) -> QubitIndex:
        """Get the qubit index.

        Returns:
            Qubit index

        Example:
            >>> idx = qubit.index
        """
        ...

    def reset(self) -> None:
        """Reset the qubit to |0⟩ state.

        Example:
            >>> qubit.reset()
        """
        ...


@runtime_checkable
class QuantumGateProtocol(Protocol):
    """Protocol for a quantum gate.

    This protocol defines the structural contract for gate implementations.

    Example:
        >>> class MyGate:
        ...     @property
        ...     def name(self) -> str:
        ...         return "H"
        ...     @property
        ...     def gate_type(self) -> GateType:
        ...         return GateType.SINGLE_QUBIT
    """

    @property
    def name(self) -> str:
        """Get the gate name.

        Returns:
            Gate name

        Example:
            >>> name = gate.name
        """
        ...

    @property
    def gate_type(self) -> GateType:
        """Get the gate type.

        Returns:
            Gate type

        Example:
            >>> gtype = gate.gate_type
        """
        ...

    @property
    def num_qubits(self) -> int:
        """Get the number of qubits the gate operates on.

        Returns:
            Number of qubits

        Example:
            >>> n = gate.num_qubits
        """
        ...

    def get_matrix(self) -> Any:
        """Get the unitary matrix representation.

        Returns:
            Unitary matrix

        Example:
            >>> matrix = gate.get_matrix()
        """
        ...

    def validate(self) -> ValidationResult:
        """Validate the gate.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = gate.validate()
        """
        ...


@runtime_checkable
class QuantumCircuitProtocol(Protocol):
    """Protocol for a quantum circuit.

    This protocol defines the structural contract for circuit implementations.

    Example:
        >>> class MyCircuit:
        ...     @property
        ...     def num_qubits(self) -> int:
        ...         return 2
    """

    @property
    def num_qubits(self) -> int:
        """Get the number of qubits in the circuit.

        Returns:
            Number of qubits

        Example:
            >>> n = circuit.num_qubits
        """
        ...

    @property
    def depth(self) -> int:
        """Get the circuit depth.

        Returns:
            Circuit depth

        Example:
            >>> d = circuit.depth
        """
        ...

    @property
    def num_gates(self) -> int:
        """Get the number of gates in the circuit.

        Returns:
            Number of gates

        Example:
            >>> n = circuit.num_gates
        """
        ...

    def add_gate(self, gate: Any, qubits: QubitIndices) -> None:
        """Add a gate to the circuit.

        Args:
            gate: Gate to add
            qubits: Target qubits

        Example:
            >>> circuit.add_gate(h_gate, [0])
        """
        ...

    def validate(self) -> ValidationResult:
        """Validate the circuit.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = circuit.validate()
        """
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Circuit definition

        Example:
            >>> data = circuit.to_dict()
        """
        ...


@runtime_checkable
class QuantumStateProtocol(Protocol):
    """Protocol for a quantum state.

    This protocol defines the structural contract for state implementations.

    Example:
        >>> class MyState:
        ...     @property
        ...     def num_qubits(self) -> int:
        ...         return 1
    """

    @property
    def num_qubits(self) -> int:
        """Get the number of qubits in the state.

        Returns:
            Number of qubits

        Example:
            >>> n = state.num_qubits
        """
        ...

    def get_state_vector(self) -> StateVector:
        """Get the state vector representation.

        Returns:
            State vector

        Example:
            >>> sv = state.get_state_vector()
        """
        ...

    def get_density_matrix(self) -> DensityMatrix:
        """Get the density matrix representation.

        Returns:
            Density matrix

        Example:
            >>> dm = state.get_density_matrix()
        """
        ...

    def normalize(self) -> None:
        """Normalize the state.

        Example:
            >>> state.normalize()
        """
        ...

    def validate(self) -> ValidationResult:
        """Validate the state.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = state.validate()
        """
        ...


@runtime_checkable
class MeasurementProtocol(Protocol):
    """Protocol for a measurement operation.

    This protocol defines the structural contract for measurement implementations.

    Example:
        >>> class MyMeasurement:
        ...     @property
        ...     def measurement_type(self) -> MeasurementType:
        ...         return MeasurementType.PROJECTIVE
    """

    @property
    def measurement_type(self) -> MeasurementType:
        """Get the measurement type.

        Returns:
            Measurement type

        Example:
            >>> mtype = measurement.measurement_type
        """
        ...

    def measure(self, state: Any, qubits: QubitIndices) -> MeasurementResult:
        """Perform measurement on the state.

        Args:
            state: Quantum state to measure
            qubits: Qubits to measure

        Returns:
            Measurement result

        Example:
            >>> result = measurement.measure(state, [0, 1])
        """
        ...

    def set_basis(self, basis: MeasurementBasis) -> None:
        """Set the measurement basis.

        Args:
            basis: Measurement basis

        Example:
            >>> measurement.set_basis("X")
        """
        ...


@runtime_checkable
class QuantumBackendProtocol(Protocol):
    """Protocol for a quantum backend.

    This protocol defines the structural contract for backend implementations.

    Example:
        >>> class MyBackend:
        ...     @property
        ...     def name(self) -> str:
        ...         return "simulator"
    """

    @property
    def name(self) -> str:
        """Get the backend name.

        Returns:
            Backend name

        Example:
            >>> name = backend.name
        """
        ...

    @property
    def backend_type(self) -> BackendType:
        """Get the backend type.

        Returns:
            Backend type

        Example:
            >>> btype = backend.backend_type
        """
        ...

    @property
    def num_qubits(self) -> int:
        """Get the number of available qubits.

        Returns:
            Number of qubits

        Example:
            >>> n = backend.num_qubits
        """
        ...

    def run(self, circuit: Any, shots: int = 1024) -> JobResult:
        """Run a circuit on the backend.

        Args:
            circuit: Circuit to run
            shots: Number of shots

        Returns:
            Job result

        Example:
            >>> result = backend.run(circuit, shots=1000)
        """
        ...

    def configure(self, config: BackendConfig) -> None:
        """Configure the backend.

        Args:
            config: Backend configuration

        Example:
            >>> backend.configure({"optimization_level": 2})
        """
        ...

    def validate(self) -> ValidationResult:
        """Validate the backend.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = backend.validate()
        """
        ...


@runtime_checkable
class QuantumProviderProtocol(Protocol):
    """Protocol for a quantum provider.

    This protocol defines the structural contract for provider implementations.

    Example:
        >>> class MyProvider:
        ...     @property
        ...     def name(self) -> str:
        ...         return "IBM"
    """

    @property
    def name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name

        Example:
            >>> name = provider.name
        """
        ...

    @property
    def provider_type(self) -> ProviderType:
        """Get the provider type.

        Returns:
            Provider type

        Example:
            >>> ptype = provider.provider_type
        """
        ...

    def get_backends(self) -> List[Any]:
        """Get available backends.

        Returns:
            List of backends

        Example:
            >>> backends = provider.get_backends()
        """
        ...

    def get_backend(self, name: str) -> Optional[Any]:
        """Get a specific backend.

        Args:
            name: Backend name

        Returns:
            Backend or None

        Example:
            >>> backend = provider.get_backend("ibmq_manila")
        """
        ...

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with the provider.

        Args:
            credentials: Authentication credentials

        Returns:
            True if authenticated

        Example:
            >>> success = provider.authenticate({"token": "my_token"})
        """
        ...

    def configure(self, config: ProviderConfig) -> None:
        """Configure the provider.

        Args:
            config: Provider configuration

        Example:
            >>> provider.configure({"region": "us-east"})
        """
        ...


@runtime_checkable
class QuantumCompilerProtocol(Protocol):
    """Protocol for a quantum compiler.

    This protocol defines the structural contract for compiler implementations.

    Example:
        >>> class MyCompiler:
        ...     def transpile(self, circuit: Any, backend: Any) -> Any:
        ...         return circuit
    """

    def transpile(self, circuit: Any, backend: Any) -> Any:
        """Transpile a circuit for a backend.

        Args:
            circuit: Circuit to transpile
            backend: Target backend

        Returns:
            Transpiled circuit

        Example:
            >>> transpiled = compiler.transpile(circuit, backend)
        """
        ...

    def optimize(self, circuit: Any, level: int = 1) -> Any:
        """Optimize a circuit.

        Args:
            circuit: Circuit to optimize
            level: Optimization level

        Returns:
            Optimized circuit

        Example:
            >>> optimized = compiler.optimize(circuit, level=2)
        """
        ...

    def configure(self, config: CompilerConfig) -> None:
        """Configure the compiler.

        Args:
            config: Compiler configuration

        Example:
            >>> compiler.configure({"optimization_level": 2})
        """
        ...


@runtime_checkable
class QuantumJobProtocol(Protocol):
    """Protocol for a quantum job.

    This protocol defines the structural contract for job implementations.

    Example:
        >>> class MyJob:
        ...     @property
        ...     def job_id(self) -> str:
        ...         return "job_001"
    """

    @property
    def job_id(self) -> str:
        """Get the job ID.

        Returns:
            Job ID

        Example:
            >>> jid = job.job_id
        """
        ...

    @property
    def status(self) -> JobStatus:
        """Get the job status.

        Returns:
            Job status

        Example:
            >>> status = job.status
        """
        ...

    def cancel(self) -> bool:
        """Cancel the job.

        Returns:
            True if cancelled

        Example:
            >>> cancelled = job.cancel()
        """
        ...

    def result(self) -> Optional[JobResult]:
        """Get the job result.

        Returns:
            Job result or None

        Example:
            >>> result = job.result()
        """
        ...

    def wait(self, timeout: Optional[int] = None) -> JobResult:
        """Wait for the job to complete.

        Args:
            timeout: Timeout in seconds

        Returns:
            Job result

        Example:
            >>> result = job.wait(timeout=300)
        """
        ...


# Export
__all__ = [
    "QubitProtocol",
    "QuantumGateProtocol",
    "QuantumCircuitProtocol",
    "QuantumStateProtocol",
    "MeasurementProtocol",
    "QuantumBackendProtocol",
    "QuantumProviderProtocol",
    "QuantumCompilerProtocol",
    "QuantumJobProtocol",
]
