"""Quantum executor delegating to MicroQuantum's public QAOA (QMQ-04 §7/§9).

The quantum leg is a thin, validated wrapper over
:func:`~quantsmind.quantum.integration.microquantum.run_qaoa` — the engine
keeps its single QAOA implementation; this layer adds plan-driven options,
MicroQuantum-availability handling and explicit result validation (§9).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum._mq import require_microquantum
from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.execution.errors import (
    InvalidQuantumResultError,
    MicroQuantumUnavailableError,
    QuantumExecutionError,
)
from quantsmind.quantum.execution.evaluation import (
    feasibility_predicate,
    objective_value,
)
from quantsmind.quantum.execution.executor import Executor, ExecutorContext
from quantsmind.quantum.execution.options import ExecutionOptions
from quantsmind.quantum.integration.microquantum import (
    QaoaExecutionResult,
    QuantumIntegrationError,
    qaoa_available,
    run_qaoa,
)
from quantsmind.quantum.strategy.strategy import ComputationStrategy


@dataclass
class QuantumExecutionResult:
    """Validated, normalized quantum execution result.

    Leg identity is ``"quantum"``; :attr:`executor`/:attr:`solver` keep the
    legacy label ``"microquantum/qaoa"`` so provenance serialization does
    not change.
    """

    leg: str = "quantum"
    solver: str = "microquantum/qaoa"
    executor: str = "microquantum/qaoa"
    algorithm: str = "qaoa"
    assignment: dict[str, int] = field(default_factory=dict)
    energy: float | None = None
    ising_energy: float | None = None
    mq_eigenvalue: float | None = None
    objective_value: float | None = None
    feasible: bool | None = None
    bitstring: str = ""
    backend: str = ""
    num_layers: int = 1
    shots: int = 0
    seed: int | None = None
    converged: bool = False
    iterations: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "leg": self.leg,
            "solver": self.solver,
            "executor": self.executor,
            "algorithm": self.algorithm,
            "assignment": {k: int(v) for k, v in self.assignment.items()},
            "energy": self.energy,
            "ising_energy": self.ising_energy,
            "mq_eigenvalue": self.mq_eigenvalue,
            "objective_value": self.objective_value,
            "feasible": self.feasible,
            "bitstring": self.bitstring,
            "backend": self.backend,
            "num_layers": self.num_layers,
            "shots": self.shots,
            "seed": self.seed,
            "converged": self.converged,
            "iterations": self.iterations,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuantumExecutionResult:
        """Rebuild a result from :meth:`to_dict` output."""
        return cls(
            leg=str(data.get("leg", "quantum")),
            solver=str(data.get("solver", "microquantum/qaoa")),
            executor=str(data.get("executor", "microquantum/qaoa")),
            algorithm=str(data.get("algorithm", "qaoa")),
            assignment={str(k): int(v) for k, v in data.get("assignment", {}).items()},
            energy=(float(data["energy"]) if data.get("energy") is not None else None),
            ising_energy=(
                float(data["ising_energy"]) if data.get("ising_energy") is not None else None
            ),
            mq_eigenvalue=(
                float(data["mq_eigenvalue"]) if data.get("mq_eigenvalue") is not None else None
            ),
            objective_value=(
                float(data["objective_value"]) if data.get("objective_value") is not None else None
            ),
            feasible=(bool(data["feasible"]) if data.get("feasible") is not None else None),
            bitstring=str(data.get("bitstring", "")),
            backend=str(data.get("backend", "")),
            num_layers=int(data.get("num_layers", 1)),
            shots=int(data.get("shots", 0)),
            seed=(int(data["seed"]) if data.get("seed") is not None else None),
            converged=bool(data.get("converged", False)),
            iterations=int(data.get("iterations", 0)),
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def from_qaoa(
        cls,
        result: QaoaExecutionResult,
        *,
        objective_value: float | None,
        feasible: bool | None,
        options: ExecutionOptions,
    ) -> QuantumExecutionResult:
        """Normalize a validated :class:`QaoaExecutionResult`."""
        return cls(
            assignment=dict(result.assignment),
            energy=result.energy,
            ising_energy=result.ising_energy,
            mq_eigenvalue=result.mq_eigenvalue,
            objective_value=objective_value,
            feasible=feasible,
            bitstring=result.bitstring,
            backend=result.backend,
            num_layers=int(result.num_layers),
            shots=int(result.shots),
            seed=result.seed,
            converged=bool(result.converged),
            iterations=int(result.iterations),
            metadata={
                **dict(result.metadata),
                "optimization_level": options.optimization_level,
            },
        )

    def __repr__(self) -> str:
        return (
            f"QuantumExecutionResult(backend={self.backend!r}, "
            f"bitstring={self.bitstring!r}, energy={self.energy}, "
            f"feasible={self.feasible})"
        )


class QuantumExecutor(Executor):
    """QAOA quantum leg of an execution (delegates unchanged to MicroQuantum)."""

    name = "quantum-executor"
    executor_id = "quantum"
    strategies = (ComputationStrategy.QUANTUM,)

    def is_available(self, capabilities: Any | None = None) -> bool:
        return qaoa_available()

    def prepare(self, context: ExecutorContext) -> None:
        try:
            require_microquantum()
        except ImportError as exc:
            raise MicroQuantumUnavailableError(str(exc)) from exc
        if context.ising is None:
            raise QuantumExecutionError(
                "quantum execution requires an Ising mapping; the plan must map the problem first"
            )
        return None

    def execute(self, context: ExecutorContext) -> QaoaExecutionResult:
        self.prepare(context)
        ising = context.ising
        if ising is None:
            raise QuantumExecutionError(
                "quantum execution requires an Ising mapping; the plan must map the problem first"
            )
        options = context.options
        try:
            return run_qaoa(
                ising,
                qubo=context.qubo,
                num_layers=options.num_layers,
                shots=options.shots,
                seed=options.seed,
                backend=options.backend,
                name=context.problem.name,
                optimizer=options.qaoa_optimizer,
            )
        except ImportError as exc:
            raise MicroQuantumUnavailableError(str(exc)) from exc
        except QuantumIntegrationError as exc:
            raise QuantumExecutionError(f"MicroQuantum QAOA execution failed: {exc}") from exc

    def validate(
        self,
        result: QaoaExecutionResult,
        context: ExecutorContext,
    ) -> QuantumExecutionResult:
        """Validate a QaoaExecutionResult before it becomes a leg of the run.

        Checks (QMQ-04 §9): decoded variable names against the mapped QUBO
        (slack variables included), binary values, re-computed QUBO energy
        consistency, domain objective/feasibility.  The raw MicroQuantum
        metadata stays intact.
        """
        problem: QuantumProblem = context.problem
        qubo = context.qubo
        ising = context.ising

        if qubo is not None:
            allowed = set(qubo.variables)
        elif ising is not None:
            allowed = set(ising.variables)
        else:
            allowed = set(result.assignment)
        unknown = sorted(set(result.assignment) - allowed)
        if unknown:
            raise InvalidQuantumResultError(
                f"quantum result decoded {len(unknown)} variable(s) not present "
                f"in the mapped model: {unknown[:5]}; expected one of "
                f"{sorted(allowed)[:5]}"
            )
        for name, value in result.assignment.items():
            if value not in (0, 1):
                raise InvalidQuantumResultError(
                    f"quantum result decoded non-binary value {value!r} for variable {name!r}"
                )

        if qubo is not None and result.energy is not None:
            recomputed = qubo.energy(result.assignment)
            if abs(recomputed - float(result.energy)) > 1e-6:
                raise InvalidQuantumResultError(
                    f"quantum result energy {result.energy} disagrees with the "
                    f"recomputed QUBO energy {recomputed} for the decoded "
                    "assignment"
                )

        objective = objective_value(problem, result.assignment)
        feasible = bool(feasibility_predicate(problem)(result.assignment))
        return QuantumExecutionResult.from_qaoa(
            result,
            objective_value=objective,
            feasible=feasible,
            options=context.options,
        )


__all__ = ["QuantumExecutor", "QuantumExecutionResult"]
