"""Quantum experiment orchestration for QuantsMind.

A :class:`QuantumExperiment` is a **domain orchestration** wrapper: it
takes a :class:`~quantsmind.quantum.program.QuantumProgram` (or a built
MicroQuantum circuit), executes it through MicroQuantum's public runtime
and wraps the result in a
    :class:`~quantsmind.quantum.circuit_result.QuantumResult`.

Quantum computation is always delegated to MicroQuantum.  This module
contains no quantum algorithm, gate, circuit or simulator logic.
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum._mq import require_microquantum, resolve_backend
from quantsmind.quantum.bridge import build_circuit
from quantsmind.quantum.circuit_result import QuantumResult
from quantsmind.quantum.program import QuantumProgram

ProgramOrCircuit = QuantumProgram | Any


class QuantumExperiment:
    """Domain-level quantum experiment that delegates execution to MicroQuantum.

    Args:
        program: A QuantsMind QuantumProgram, or an already-built
            MicroQuantum QuantumCircuit.
        backend: Backend name (e.g. ``"statevector"``) or a MicroQuantum
            Backend instance.  ``None`` uses MicroQuantum's default.
        shots: Number of shots per execution.
        seed: Optional RNG seed for reproducibility.
        name: Experiment label.
        experiment_id: Optional explicit identity (generated otherwise).
        domain_metadata: Domain metadata attached to the result.
        optimization_level: MicroQuantum optimization level (0-3).
        options: Extra MicroQuantum runtime options.
    """

    def __init__(
        self,
        program: ProgramOrCircuit,
        *,
        backend: str | None = None,
        shots: int = 1024,
        seed: int | None = None,
        name: str = "quantum_experiment",
        experiment_id: str | None = None,
        domain_metadata: dict[str, Any] | None = None,
        optimization_level: int = 0,
        options: dict[str, Any] | None = None,
    ) -> None:
        import uuid

        if isinstance(program, QuantumProgram):
            self._program: QuantumProgram | None = program
            self._circuit: Any = None
            self._program_name = program.name
        else:
            require_microquantum()
            self._program = None
            self._circuit = program
            self._program_name = getattr(program, "name", "circuit")
        self._backend = backend
        self._shots = shots
        self._seed = seed
        self._name = name
        self._experiment_id = experiment_id or str(uuid.uuid4())
        self._domain_metadata = dict(domain_metadata or {})
        self._optimization_level = optimization_level
        self._options = options

    @property
    def name(self) -> str:
        """Experiment label."""
        return self._name

    @property
    def experiment_id(self) -> str:
        """Unique experiment identity."""
        return self._experiment_id

    def run(self) -> QuantumResult:
        """Execute the experiment through MicroQuantum and enrich the result."""
        mq = require_microquantum()

        if self._circuit is None:
            assert self._program is not None  # constructed with a program
            circuit = build_circuit(self._program)
        else:
            circuit = self._circuit
        backend_object = resolve_backend(self._backend)

        native = mq.execute(
            circuit,
            backend=backend_object,
            shots=self._shots,
            seed=self._seed,
            optimization_level=self._optimization_level,
            options=self._options,
            metadata={
                "quantsmind_experiment_id": self._experiment_id,
                "quantsmind_program": self._program_name,
            },
        )
        provenance = {
            "backend_requested": self._backend,
            "executed_backend": getattr(native, "backend_name", None),
            "shots": self._shots,
            "optimization_level": self._optimization_level,
        }
        return QuantumResult.from_backend_result(
            native,
            experiment_id=self._experiment_id,
            program_name=self._program_name,
            domain_metadata=self._domain_metadata,
            provenance=provenance,
        )


# ---------------------------------------------------------------------------
# MicroQuantum algorithm delegation
# ---------------------------------------------------------------------------

_ALGORITHMS: dict[str, str] = {
    "vqe": "VQE",
    "vqd": "VQD",
    "adapt_vqe": "AdaptVQE",
    "qaoa": "QAOA",
    "grover": "GroverSearch",
    "shor": "ShorsAlgorithm",
    "bernstein_vazirani": "BernsteinVazirani",
    "deutsch_jozsa": "DeutschJozsa",
    "qft": "QFT",
    "phase_estimation": "PhaseEstimation",
    "amplitude_estimation": "AmplitudeEstimation",
    "hamiltonian_simulation": "HamiltonianSimulation",
    "hhl": "HHL",
    "discrete_quantum_walk": "DiscreteQuantumWalk",
    "continuous_quantum_walk": "ContinuousQuantumWalk",
}

_ALGORITHM_ALIASES: dict[str, str] = {
    "adapt-vqe": "adapt_vqe",
    "grover_search": "grover",
    "shors": "shor",
    "phase_est": "phase_estimation",
    "amp_est": "amplitude_estimation",
}


def available_algorithms() -> list[str]:
    """Return the sorted list of canonical algorithm names QuantsMind can delegate."""
    return sorted(_ALGORITHMS)


def resolve_algorithm(name: str) -> type:
    """Resolve an algorithm name to its MicroQuantum class (public API)."""
    mq = require_microquantum()
    key = name.lower().strip()
    key = _ALGORITHM_ALIASES.get(key, key)
    if key not in _ALGORITHMS:
        raise ValueError(
            f"unknown algorithm {name!r}; available: {', '.join(available_algorithms())}"
        )
    cls_name = _ALGORITHMS[key]
    cls = getattr(mq, cls_name)
    if not isinstance(cls, type):
        raise ValueError(f"resolved name {cls_name!r} is not a class")
    return cls


def run_algorithm(name: str, **kwargs: Any) -> Any:
    """Instantiate and run a MicroQuantum algorithm by name.

    The algorithm class is resolved from MicroQuantum's public API, then
    instantiated with ``kwargs`` and run via its public entry point
    (``run``, ``solve`` or ``compute_minimum_eigenvalue``).  The native
    MicroQuantum result object is returned.
    """
    cls = resolve_algorithm(name)
    algorithm = cls(**kwargs)
    for entry in ("run", "solve", "compute_minimum_eigenvalue"):
        runner = getattr(algorithm, entry, None)
        if callable(runner):
            return runner()
    raise ValueError(f"algorithm {name!r} has no public runnable entry point")


__all__ = [
    "QuantumExperiment",
    "available_algorithms",
    "resolve_algorithm",
    "run_algorithm",
]
