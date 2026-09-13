"""MicroQuantum integration facade.

Keeps the *only* microquantum-importing seams behind clearly marked
helpers.  Nothing else in ``quantsmind.quantum`` should import
``microquantum`` directly; the runtime availability checks and the lazy
import live in :mod:`quantsmind.quantum._mq` and are re-exported here
for the domain layer.

Importing this module (or any of ``quantsmind.quantum``) never requires
``microquantum`` to be installed.

QMQ-02 adds the QUBO/Ising -> MicroQuantum delegation: an
:class:`~quantsmind.quantum.optimization.ising.IsingModel` becomes a
``microquantum.PauliSum`` (the Ising Hamiltonian) and an
``OptimizationProblem``, which is then minimised with MicroQuantum's
``QAOA`` via its public API.  No circuits, gates, states, simulators,
QAOA implementations or runtimes are duplicated here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum._mq import (
    microquantum_available,
    require_microquantum,
    resolve_backend,
)

if TYPE_CHECKING:
    from quantsmind.quantum.optimization.ising import IsingModel
    from quantsmind.quantum.optimization.qubo import QUBOModel


class QuantumIntegrationError(RuntimeError):
    """Raised when a MicroQuantum delegation fails or is unavailable."""


@dataclass
class QaoaExecutionResult:
    """Record of a QUBO/Ising run delegated to MicroQuantum's QAOA.

    Args:
        solver: Solver identity (``"microquantum/qaoa"``).
        algorithm: Algorithm used (``"qaoa"``).
        backend: Backend that executed the run.
        num_layers: Number of QAOA layers used.
        bitstring: Most-frequent measured bitstring.
        assignment: QUBO variable name -> 0/1 decoded from the bitstring.
        energy: QUBO energy of the assignment (minimization form, penalties
            included) when a QUBO was supplied.
        ising_energy: Ising energy of the assignment (carries the constant).
        mq_eigenvalue: Raw eigenvalue returned by MicroQuantum (Ising energy
            without the additive constant).
        converged: Whether MicroQuantum's optimizer reported convergence.
        iterations: Optimizer iterations reported by MicroQuantum.
        shots: Shot count used for the final sampling.
        seed: Seed used.
        metadata: Free-form execution metadata.
    """

    solver: str = "microquantum/qaoa"
    algorithm: str = "qaoa"
    backend: str = ""
    num_layers: int = 1
    bitstring: str = ""
    assignment: dict[str, int] = field(default_factory=dict)
    energy: float | None = None
    ising_energy: float | None = None
    mq_eigenvalue: float | None = None
    converged: bool = False
    iterations: int = 0
    shots: int = 0
    seed: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "solver": self.solver,
            "algorithm": self.algorithm,
            "backend": self.backend,
            "num_layers": self.num_layers,
            "bitstring": self.bitstring,
            "assignment": {k: int(v) for k, v in self.assignment.items()},
            "energy": self.energy,
            "ising_energy": self.ising_energy,
            "mq_eigenvalue": self.mq_eigenvalue,
            "converged": self.converged,
            "iterations": self.iterations,
            "shots": self.shots,
            "seed": self.seed,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QaoaExecutionResult:
        """Rebuild a result from :meth:`to_dict` output."""
        return cls(
            solver=str(data.get("solver", "microquantum/qaoa")),
            algorithm=str(data.get("algorithm", "qaoa")),
            backend=str(data.get("backend", "")),
            num_layers=int(data.get("num_layers", 1)),
            bitstring=str(data.get("bitstring", "")),
            assignment={str(k): int(v) for k, v in data.get("assignment", {}).items()},
            energy=(float(data["energy"]) if data.get("energy") is not None else None),
            ising_energy=(
                float(data["ising_energy"]) if data.get("ising_energy") is not None else None
            ),
            mq_eigenvalue=(
                float(data["mq_eigenvalue"]) if data.get("mq_eigenvalue") is not None else None
            ),
            converged=bool(data.get("converged", False)),
            iterations=int(data.get("iterations", 0)),
            shots=int(data.get("shots", 0)),
            seed=(int(data["seed"]) if data.get("seed") is not None else None),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"QaoaExecutionResult(backend={self.backend!r}, "
            f"bitstring={self.bitstring!r}, energy={self.energy}, "
            f"converged={self.converged})"
        )


def ising_to_pauli_sum(ising: IsingModel) -> Any:
    """Build the ``microquantum.PauliSum`` (Ising Hamiltonian) for a model.

    Qubit ``i`` of the Pauli labels corresponds to the ``i``-th variable in
    :attr:`IsingModel.variables`.  The additive constant is **not** part of
    the Pauli sum (MicroQuantum's eigenvalue excludes it); it is carried by
    :meth:`IsingModel.energy` instead.
    """
    mq = require_microquantum()
    count = len(ising.variables)
    terms: list[Any] = []
    for index, name in enumerate(ising.variables):
        value = ising.h.get(name, 0.0)
        if value != 0.0:
            label = ["I"] * count
            label[index] = "Z"
            terms.append(mq.PauliString("".join(label), float(value)))
    for (left, right), value in ising.couplings.items():
        if value != 0.0:
            label = ["I"] * count
            label[ising.variables.index(left)] = "Z"
            label[ising.variables.index(right)] = "Z"
            terms.append(mq.PauliString("".join(label), float(value)))
    if not terms:
        terms = [mq.PauliString("I" * count, 0.0)]
    return mq.PauliSum(terms)


def ising_to_optimization_problem(ising: IsingModel, *, name: str | None = None) -> Any:
    """Wrap an Ising model into a MicroQuantum ``OptimizationProblem``."""
    mq = require_microquantum()
    pauli_sum = ising_to_pauli_sum(ising)
    return mq.OptimizationProblem.from_ising(pauli_sum, name=name or ising.name)


def qaoa_available() -> bool:
    """Return whether a QAOA-capable MicroQuantum is importable."""
    if not microquantum_available():
        return False
    mq = require_microquantum()
    return hasattr(mq, "QAOA") and hasattr(mq, "OptimizationProblem")


def run_qaoa(
    ising: IsingModel,
    *,
    qubo: QUBOModel | None = None,
    num_layers: int = 1,
    shots: int = 1024,
    seed: int | None = None,
    backend: str | None = None,
    name: str | None = None,
    optimizer: Any | None = None,
) -> QaoaExecutionResult:
    """Minimise an Ising model via MicroQuantum's public QAOA API.

    The Ising model is wrapped as a MicroQuantum ``OptimizationProblem``
    (cost Hamiltonian); ``QAOA.from_problem().solve()`` performs the
    computation, and the optimized ansatz is sampled on the chosen backend
    to recover a bitstring.  Returns an honest record: MicroQuantum's raw
    eigenvalue plus the QUBO/Ising energies of the sampled assignment.

    Args:
        ising: The Ising model to minimise.
        qubo: Optional QUBO model for reporting the sampled assignment's
            QUBO energy.
        num_layers: QAOA layers (``p``).
        shots: Shot count used for the final sampling.
        seed: Optional RNG seed.
        backend: Backend name or engine backend instance.
        name: Problem name recorded in the result metadata.
        optimizer: Optional MicroQuantum optimizer instance to use for the
            variational loop (overrides the engine default; tests pass a
            low-iteration one to keep the run fast).

    Raises:
        QuantumIntegrationError: If QAOA is not available or the run fails.
        ImportError: If MicroQuantum is not installed (with install hint).
    """
    mq = require_microquantum()
    if not hasattr(mq, "QAOA") or not hasattr(mq, "OptimizationProblem"):
        raise QuantumIntegrationError(
            "the installed microquantum does not expose QAOA/optimization "
            "support required by QMQ-02"
        )
    problem = ising_to_optimization_problem(ising, name=name)
    backend_object = resolve_backend(backend)
    runtime = mq.ExecutionRuntime(backend=backend_object)
    try:
        qaoa = mq.QAOA.from_problem(
            problem,
            num_layers=int(num_layers),
            optimizer=optimizer,
            shots=int(shots),
            seed=seed,
        )
        result = qaoa.solve(problem, runtime=runtime)
    except Exception as exc:  # noqa: BLE001 - delegate engine errors as-is
        raise QuantumIntegrationError(f"MicroQuantum QAOA run failed: {exc}") from exc

    eigenvalue = getattr(result, "eigenvalue", None)
    eigenstate = getattr(result, "eigenstate", {}) or {}
    optimizer_result = getattr(result, "optimizer_result", None)
    converged = bool(getattr(optimizer_result, "converged", False))
    iterations = int(getattr(optimizer_result, "iterations", 0))

    try:
        optimized = qaoa.build_ansatz().bind_parameters(eigenstate)
        native = mq.execute(
            optimized,
            backend=backend_object,
            shots=int(shots),
            seed=seed,
        )
    except Exception as exc:  # noqa: BLE001
        raise QuantumIntegrationError(
            f"MicroQuantum sampling of the optimized ansatz failed: {exc}"
        ) from exc

    counts: dict[str, int] = getattr(native, "counts", {}) or {}
    actual_backend = getattr(native, "backend_name", "") or getattr(
        backend_object, "name", backend or ""
    )
    bitstring = max(sorted(counts), key=lambda key: counts[key]) if counts else ""
    assignment: dict[str, int] = {}
    for index, name in enumerate(ising.variables):
        assignment[name] = int(bitstring[index]) if index < len(bitstring) else 0
    spins = [1 if assignment[name] == 1 else -1 for name in ising.variables]
    ising_energy = ising.energy(spins)
    energy = qubo.energy(assignment) if qubo is not None else None
    return QaoaExecutionResult(
        backend=str(actual_backend),
        num_layers=int(num_layers),
        bitstring=bitstring,
        assignment=assignment,
        energy=energy,
        ising_energy=ising_energy,
        mq_eigenvalue=(float(eigenvalue) if eigenvalue is not None else None),
        converged=converged,
        iterations=iterations,
        shots=int(shots),
        seed=seed,
        metadata={
            "problem_name": name or ising.name,
            "num_variables": len(ising.variables),
            "num_layers": int(num_layers),
            "optimizer": getattr(optimizer, "name", type(optimizer).__name__)
            if optimizer is not None
            else "default",
        },
    )


__all__ = [
    "microquantum_available",
    "require_microquantum",
    "resolve_backend",
    "QuantumIntegrationError",
    "QaoaExecutionResult",
    "ising_to_pauli_sum",
    "ising_to_optimization_problem",
    "qaoa_available",
    "run_qaoa",
]
