"""QMQ-03 algorithm registry.

The registry is the single source of truth for which algorithms QuantsMind
Quantum knows about.  It is a plain, extensible catalog — not a giant
conditional.  Registration is explicit, and the default catalog ships the
QMQ-03 algorithm set.

Availability is never inferred here: a registered algorithm is *known to the
architecture*; whether it can run is decided by the capability layer at
selection time.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Self

from quantsmind.quantum.intelligence.algorithms import (
    AlgorithmAvailability,
    AlgorithmCategory,
    AlgorithmDescriptor,
)
from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.intelligence.capabilities import CapabilityModel

_EXHAUSTIVE = "exhaustive"
_QML = "qml"


class UnknownAlgorithmError(KeyError):
    """Raised when an algorithm id is not registered."""

    def __init__(self, name: str) -> None:
        self.algorithm_name = name
        super().__init__(f"unknown algorithm {name!r}")


class DuplicateAlgorithmError(ValueError):
    """Raised when registering an id that already exists."""

    def __init__(self, name: str) -> None:
        self.algorithm_name = name
        super().__init__(f"algorithm {name!r} is already registered")


def _default_catalog() -> list[AlgorithmDescriptor]:
    """The QMQ-03 default algorithm catalog.

    Quantum entries mirror public MicroQuantum classes (QMQ-03 §4); they are
    never implemented inside QuantsMind.  ``exhaustive`` is the QMQ-02
    classical baseline; ``qml`` is a quantum machine-learning descriptor that
    only becomes executable when a QML capability is probed.
    """
    strategies_quantum = (ComputationStrategy.QUANTUM, ComputationStrategy.HYBRID)
    families_optimization = (
        "binary_optimization",
        "integer_optimization",
        "graph_optimization",
        "constraint_optimization",
        "continuous_optimization",
    )
    return [
        AlgorithmDescriptor(
            name="qaoa",
            label="QAOA",
            category=AlgorithmCategory.OPTIMIZATION,
            description="Quantum Approximate Optimization Algorithm for "
            "quadratic optimization on a quantum circuit.",
            problem_classes=families_optimization,
            formulations=("qubo", "ising"),
            strategies=strategies_quantum,
            execution_modes=("vqe_loop",),
            microquantum_identifier="QAOA",
            required_capabilities=("quantum_execution_enabled", "qaoa_available"),
            min_variables=2,
            max_variables=20,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="vqe",
            label="VQE",
            category=AlgorithmCategory.VARIATIONAL,
            description="Variational Quantum Eigensolver for ground-state energy problems.",
            problem_classes=("binary_optimization", "continuous_optimization"),
            formulations=("qubo", "ising", "simulation"),
            strategies=strategies_quantum,
            execution_modes=("vqe_loop",),
            microquantum_identifier="VQE",
            required_capabilities=("quantum_execution_enabled", "vqe_available"),
            min_variables=2,
            max_variables=20,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="vqd",
            label="VQD",
            category=AlgorithmCategory.VARIATIONAL,
            description="Variational Quantum Deflation.",
            problem_classes=("binary_optimization", "continuous_optimization"),
            formulations=("qubo", "ising", "simulation"),
            strategies=strategies_quantum,
            execution_modes=("vqe_loop",),
            microquantum_identifier="VQD",
            required_capabilities=("quantum_execution_enabled", "vqd_available"),
            min_variables=2,
            max_variables=20,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="adapt_vqe",
            label="ADAPT-VQE",
            category=AlgorithmCategory.VARIATIONAL,
            description="Adaptive Variational Quantum Eigensolver.",
            problem_classes=("binary_optimization", "continuous_optimization"),
            formulations=("qubo", "ising", "simulation"),
            strategies=strategies_quantum,
            execution_modes=("vqe_loop",),
            microquantum_identifier="AdaptVQE",
            required_capabilities=(
                "quantum_execution_enabled",
                "adapt_vqe_available",
            ),
            min_variables=2,
            max_variables=20,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="grover",
            label="Grover Search",
            category=AlgorithmCategory.SEARCH,
            description="Grover's search for unstructured search problems.",
            problem_classes=("search", "sampling"),
            formulations=("mathematical",),
            strategies=strategies_quantum,
            execution_modes=("oracle_based",),
            microquantum_identifier="GroverSearch",
            required_capabilities=("quantum_execution_enabled", "grover_available"),
            min_variables=2,
            max_variables=12,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="bernoulli_masked_vqe",
            label="Bernoulli Masked VQE",
            category=AlgorithmCategory.VARIATIONAL,
            description="Bernoulli-masked variational search.",
            problem_classes=("search",),
            formulations=("mathematical",),
            strategies=(ComputationStrategy.QUANTUM,),
            execution_modes=("vqe_loop",),
            microquantum_identifier="BernoulliMaskedVQE",
            required_capabilities=(
                "quantum_execution_enabled",
                "bernoulli_masked_vqe_available",
            ),
            min_variables=2,
            max_variables=20,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="qft",
            label="Quantum Fourier Transform",
            category=AlgorithmCategory.LINEAR_ALGEBRA,
            description="Quantum Fourier transform.",
            problem_classes=("search", "sampling"),
            formulations=("mathematical",),
            strategies=strategies_quantum,
            execution_modes=("constructive",),
            microquantum_identifier="QFT",
            required_capabilities=("quantum_execution_enabled", "qft_available"),
            min_variables=2,
            max_variables=20,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="phase_estimation",
            label="Phase Estimation",
            category=AlgorithmCategory.LINEAR_ALGEBRA,
            description="Quantum phase estimation.",
            problem_classes=(
                "linear_algebra",
                "sampling",
                "constraint_optimization",
            ),
            formulations=("mathematical",),
            strategies=strategies_quantum,
            execution_modes=("constructive",),
            microquantum_identifier="PhaseEstimation",
            required_capabilities=(
                "quantum_execution_enabled",
                "phase_estimation_available",
            ),
            min_variables=2,
            max_variables=12,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="hhl",
            label="HHL",
            category=AlgorithmCategory.LINEAR_ALGEBRA,
            description="Harrow-Hassidim-Lloyd linear-system solver.",
            problem_classes=("linear_algebra",),
            formulations=("mathematical",),
            strategies=strategies_quantum,
            execution_modes=("swap_network",),
            microquantum_identifier="HHL",
            required_capabilities=("quantum_execution_enabled", "hhl_available"),
            min_variables=2,
            max_variables=8,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="shor",
            label="Shor",
            category=AlgorithmCategory.LINEAR_ALGEBRA,
            description="Shor's algorithm for integer factorization.",
            problem_classes=("sampling",),
            formulations=("mathematical",),
            strategies=strategies_quantum,
            execution_modes=("constructive",),
            microquantum_identifier="ShorsAlgorithm",
            required_capabilities=("quantum_execution_enabled", "shor_available"),
            min_variables=2,
            max_variables=12,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="amplitude_estimation",
            label="Amplitude Estimation",
            category=AlgorithmCategory.SAMPLING,
            description="Quantum amplitude estimation for sampling problems.",
            problem_classes=("sampling", "statistical"),
            formulations=("mathematical", "statistical"),
            strategies=strategies_quantum,
            execution_modes=("constructive",),
            microquantum_identifier="AmplitudeEstimation",
            required_capabilities=(
                "quantum_execution_enabled",
                "amplitude_estimation_available",
            ),
            min_variables=2,
            max_variables=12,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="deutsch_jozsa",
            label="Deutsch-Jozsa",
            category=AlgorithmCategory.LINEAR_ALGEBRA,
            description="Deutsch-Jozsa oracle distinction.",
            problem_classes=("search",),
            formulations=("mathematical",),
            strategies=strategies_quantum,
            execution_modes=("oracle_based",),
            microquantum_identifier="DeutschJozsa",
            required_capabilities=(
                "quantum_execution_enabled",
                "deutsch_jozsa_available",
            ),
            min_variables=2,
            max_variables=12,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="bernstein_vazirani",
            label="Bernstein-Vazirani",
            category=AlgorithmCategory.LINEAR_ALGEBRA,
            description="Bernstein-Vazirani hidden-string recovery.",
            problem_classes=("search",),
            formulations=("mathematical",),
            strategies=strategies_quantum,
            execution_modes=("oracle_based",),
            microquantum_identifier="BernsteinVazirani",
            required_capabilities=(
                "quantum_execution_enabled",
                "bernstein_vazirani_available",
            ),
            min_variables=2,
            max_variables=12,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="hamiltonian_simulation",
            label="Hamiltonian Simulation",
            category=AlgorithmCategory.SIMULATION,
            description="Trotterized Hamiltonian time evolution.",
            problem_classes=("simulation",),
            formulations=("simulation",),
            strategies=(ComputationStrategy.QUANTUM,),
            execution_modes=("trotter",),
            microquantum_identifier="HamiltonianSimulation",
            required_capabilities=(
                "quantum_execution_enabled",
                "hamiltonian_simulation_available",
            ),
            min_variables=2,
            max_variables=20,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="continuous_quantum_walk",
            label="Continuous Quantum Walk",
            category=AlgorithmCategory.SIMULATION,
            description="Continuous-time quantum walk.",
            problem_classes=("simulation",),
            formulations=("simulation",),
            strategies=(ComputationStrategy.QUANTUM,),
            execution_modes=("trotter",),
            microquantum_identifier="ContinuousQuantumWalk",
            required_capabilities=(
                "quantum_execution_enabled",
                "continuous_quantum_walk_available",
            ),
            min_variables=2,
            max_variables=20,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name="discrete_quantum_walk",
            label="Discrete Quantum Walk",
            category=AlgorithmCategory.SIMULATION,
            description="Discrete-time quantum walk.",
            problem_classes=("simulation",),
            formulations=("simulation",),
            strategies=(ComputationStrategy.QUANTUM,),
            execution_modes=("trotter",),
            microquantum_identifier="DiscreteQuantumWalk",
            required_capabilities=(
                "quantum_execution_enabled",
                "discrete_quantum_walk_available",
            ),
            min_variables=2,
            max_variables=20,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name=_QML,
            label="Quantum ML",
            category=AlgorithmCategory.MACHINE_LEARNING,
            description="Quantum machine-learning model (backend-specific).",
            problem_classes=("machine_learning",),
            formulations=("ml",),
            strategies=strategies_quantum,
            execution_modes=("training_loop",),
            microquantum_identifier="QuantumKernel",
            required_capabilities=("qml_available",),
            min_variables=None,
            max_variables=None,
            metadata={"kind": "quantum"},
        ),
        AlgorithmDescriptor(
            name=_EXHAUSTIVE,
            label="Exhaustive search",
            category=AlgorithmCategory.CLASSICAL,
            description="Classical exhaustive search baseline (QMQ-02).",
            problem_classes=(
                "binary_optimization",
                "integer_optimization",
                "continuous_optimization",
                "graph_optimization",
                "constraint_optimization",
            ),
            formulations=("qubo", "ising", "optimization"),
            strategies=(ComputationStrategy.CLASSICAL,),
            execution_modes=("exhaustive",),
            microquantum_identifier=None,
            required_capabilities=("classical_baseline_available",),
            min_variables=0,
            max_variables=None,
            metadata={"kind": "classical"},
        ),
    ]


class AlgorithmRegistry:
    """Registry of algorithm descriptors.

    Implements registration, lookup, search and availability queries.
    The default catalog is loaded on construction and can be replaced or
    extended.
    """

    def __init__(self, descriptors: list[AlgorithmDescriptor] | None = None) -> None:
        self._algorithms: dict[str, AlgorithmDescriptor] = {}
        self.catalog_version: str = "qmq-03-default"
        for descriptor in _default_catalog():
            self.register(descriptor)
        for descriptor in descriptors if descriptors is not None else []:
            self.register(descriptor)

    # ------------------------------------------------------------------
    # registration / lookup
    # ------------------------------------------------------------------

    def register(self, descriptor: AlgorithmDescriptor) -> AlgorithmDescriptor:
        """Register ``descriptor``; raise on a duplicate or empty id."""
        if not descriptor.name:
            raise ValueError("algorithm name must be a non-empty string")
        if descriptor.name in self._algorithms:
            raise DuplicateAlgorithmError(descriptor.name)
        self._algorithms[descriptor.name] = descriptor
        return descriptor

    def unregister(self, name: str) -> AlgorithmDescriptor:
        """Remove ``name``; raise :class:`UnknownAlgorithmError`."""
        if name not in self._algorithms:
            raise UnknownAlgorithmError(name)
        return self._algorithms.pop(name)

    def get(self, name: str) -> AlgorithmDescriptor:
        """Return the descriptor for ``name`` or raise UnknownAlgorithmError."""
        try:
            return self._algorithms[name]
        except KeyError as exc:
            raise UnknownAlgorithmError(name) from exc

    def __contains__(self, name: object) -> bool:
        return name in self._algorithms

    def __getitem__(self, name: str) -> AlgorithmDescriptor:
        return self.get(name)

    def __len__(self) -> int:
        return len(self._algorithms)

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._algorithms))

    # ------------------------------------------------------------------
    # search
    # ------------------------------------------------------------------

    def find(
        self,
        *,
        problem_class: str | None = None,
        formulation: str | None = None,
        category: AlgorithmCategory | None = None,
        strategy: ComputationStrategy | str | None = None,
    ) -> list[AlgorithmDescriptor]:
        """Return descriptors matching the given signals (sorted by name)."""
        parsed_strategy = None
        if strategy is not None and not isinstance(strategy, ComputationStrategy):
            parsed_strategy = ComputationStrategy.parse(strategy)
        else:
            parsed_strategy = strategy
        return sorted(
            (
                descriptor
                for descriptor in self._algorithms.values()
                if descriptor.matches(
                    problem_class=problem_class,
                    formulation=formulation,
                    strategy=parsed_strategy,
                )
                and (category is None or descriptor.category == category)
            ),
            key=lambda d: d.name,
        )

    def registered(self) -> list[AlgorithmDescriptor]:
        """All registered descriptors sorted by name."""
        return sorted(self._algorithms.values(), key=lambda d: d.name)

    # ------------------------------------------------------------------
    # availability
    # ------------------------------------------------------------------

    def available(self, capabilities: CapabilityModel) -> list[AlgorithmAvailability]:
        """Executive availability for every registered algorithm."""
        return [descriptor.availability(capabilities) for descriptor in self.registered()]

    def executable_algorithms(self, capabilities: CapabilityModel) -> list[str]:
        """Sorted ids currently executable against ``capabilities``."""
        return sorted(
            descriptor.name
            for descriptor in self.registered()
            if descriptor.availability(capabilities).currently_executable
        )

    # ------------------------------------------------------------------
    # serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize the registry (descriptors + version)."""
        return {
            "version": self.catalog_version,
            "algorithms": [descriptor.to_dict() for descriptor in self.registered()],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a registry from :meth:`to_dict` output.

        Only the serialized descriptors are registered (the default
        catalog is not preloaded).
        """
        registry = cls.__new__(cls)
        registry._algorithms = {}
        registry.catalog_version = str(data.get("version", "custom"))
        for descriptor_data in data.get("algorithms", []):
            registry.register(AlgorithmDescriptor.from_dict(descriptor_data))
        return registry

    def __repr__(self) -> str:
        return f"AlgorithmRegistry({len(self)} algorithms; version={self.catalog_version!r})"


__all__ = [
    "AlgorithmRegistry",
    "UnknownAlgorithmError",
    "DuplicateAlgorithmError",
    "AlgorithmAvailability",
]
