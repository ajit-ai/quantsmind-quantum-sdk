"""
Quantum Enums Module

This module provides enumeration definitions for the Quantum package.

Purpose
-------
Provide comprehensive enumerations for quantum computing concepts.

Responsibilities
----------------
- Define quantum-specific enumerations
- Support type-safe enum usage
- Provide enum serialization

Dependencies
------------
enum (standard library)
"""

from __future__ import annotations

from enum import Enum


class GateType(Enum):
    """Enumeration of quantum gate types.

    Example:
        >>> gate_type = GateType.SINGLE_QUBIT
    """

    SINGLE_QUBIT = "single_qubit"
    MULTI_QUBIT = "multi_qubit"
    CONTROLLED = "controlled"
    PARAMETERIZED = "parameterized"
    MEASUREMENT = "measurement"
    RESET = "reset"
    BARRIER = "barrier"


class StateType(Enum):
    """Enumeration of quantum state types.

    Example:
        >>> state_type = StateType.STATE_VECTOR
    """

    BASIS = "basis"
    STATE_VECTOR = "state_vector"
    DENSITY_MATRIX = "density_matrix"
    BLOCH = "bloch"
    STABILIZER = "stabilizer"


class MeasurementType(Enum):
    """Enumeration of measurement types.

    Example:
        >>> measurement_type = MeasurementType.PROJECTIVE
    """

    PROJECTIVE = "projective"
    WEAK = "weak"
    PARTIAL = "partial"
    MID_CIRCUIT = "mid_circuit"
    NON_DESTRUCTIVE = "non_destructive"


class BackendType(Enum):
    """Enumeration of backend types.

    Example:
        >>> backend_type = BackendType.SIMULATOR
    """

    SIMULATOR = "simulator"
    PROVIDER = "provider"
    HYBRID = "hybrid"
    CUSTOM = "custom"


class ProviderType(Enum):
    """Enumeration of quantum provider types.

    Example:
        >>> provider_type = ProviderType.IBM
    """

    IBM = "ibm"
    GOOGLE = "google"
    AWS_BRAKET = "aws_braket"
    AZURE_QUANTUM = "azure_quantum"
    IONQ = "ionq"
    RIGETTI = "rigetti"
    QUANTINUUM = "quantinuum"
    XANADU = "xanadu"
    LOCAL = "local"
    CUSTOM = "custom"


class NoiseType(Enum):
    """Enumeration of noise types.

    Example:
        >>> noise_type = NoiseType.BIT_FLIP
    """

    BIT_FLIP = "bit_flip"
    PHASE_FLIP = "phase_flip"
    AMPLITUDE_DAMPING = "amplitude_damping"
    PHASE_DAMPING = "phase_damping"
    DEPOLARIZING = "depolarizing"
    READOUT_ERROR = "readout_error"
    THERMAL = "thermal"
    CUSTOM = "custom"


class AlgorithmType(Enum):
    """Enumeration of quantum algorithm types.

    Example:
        >>> algorithm_type = AlgorithmType.VARIATIONAL
    """

    VARIATIONAL = "variational"
    SAMPLING = "sampling"
    OPTIMIZATION = "optimization"
    SEARCH = "search"
    SIMULATION = "simulation"
    MACHINE_LEARNING = "machine_learning"
    CRYPTOGRAPHY = "cryptography"
    CUSTOM = "custom"


class CompilerPassType(Enum):
    """Enumeration of compiler pass types.

    Example:
        >>> pass_type = CompilerPassType.TRANSPILATION
    """

    TRANSPILATION = "transpilation"
    OPTIMIZATION = "optimization"
    MAPPING = "mapping"
    SCHEDULING = "scheduling"
    VALIDATION = "validation"
    CUSTOM = "custom"


class JobStatus(Enum):
    """Enumeration of quantum job statuses.

    Example:
        >>> status = JobStatus.RUNNING
    """

    INITIALIZING = "initializing"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class BasisType(Enum):
    """Enumeration of measurement bases.

    Example:
        >>> basis_type = BasisType.COMPUTATIONAL
    """

    COMPUTATIONAL = "computational"
    X = "x"
    Y = "y"
    Z = "z"
    CUSTOM = "custom"


class PauliType(Enum):
    """Enumeration of Pauli operators.

    Example:
        >>> pauli_type = PauliType.X
    """

    I = "I"
    X = "X"
    Y = "Y"
    Z = "Z"


class QubitState(Enum):
    """Enumeration of qubit states.

    Example:
        >>> qubit_state = QubitState.ZERO
    """

    ZERO = "0"
    ONE = "1"
    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"
    MIXED = "mixed"


class OptimizationLevel(Enum):
    """Enumeration of optimization levels.

    Example:
        >>> opt_level = OptimizationLevel.MEDIUM
    """

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class TranspilerTarget(Enum):
    """Enumeration of transpiler targets.

    Example:
        >>> target = TranspilerTarget.GATE_SET
    """

    GATE_SET = "gate_set"
    TOPOLOGY = "topology"
    COUPLING_MAP = "coupling_map"
    FULL = "full"


# Export
__all__ = [
    "GateType",
    "StateType",
    "MeasurementType",
    "BackendType",
    "ProviderType",
    "NoiseType",
    "AlgorithmType",
    "CompilerPassType",
    "JobStatus",
    "BasisType",
    "PauliType",
    "QubitState",
    "OptimizationLevel",
    "TranspilerTarget",
]
