"""QMQ-05 benchmark models: definition, metrics, comparison, results.

The models are generic over the existing QMQ-01..04 pipeline: a
:class:`Benchmark` wraps a :class:`~quantsmind.quantum.core.problem.QuantumProblem`
plus strategy/algorithm/execution configuration; :class:`BenchmarkMetrics`
describe a measured execution; :class:`BenchmarkComparison` classifies the
benchmark result against the classical baseline; :class:`BenchmarkResult` is
the serializable report.  All sense/ranking logic delegates to
:mod:`quantsmind.quantum.benchmark.metrics` (no duplicated sign handling,
QMQ-05 §10).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.benchmark.metrics import (
    approximation_ratio,
    constraint_violations,
    normalized_score,
    optimality_gap,
    sense_label,
)
from quantsmind.quantum.core.objective import ObjectiveSense
from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.execution.options import ExecutionOptions
from quantsmind.quantum.optimization.classical import ExhaustiveSolver
from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.result.result import SolutionReport

_EXECUTED = "executed"


class BenchmarkWinner(Enum):
    """Classification of a benchmark run vs its classical baseline (QMQ-05 §13).

    * ``CLASSICAL_WIN`` — the classical baseline produced the better result.
    * ``QUANTUM_WIN`` — a quantum strategy produced the better result.
    * ``HYBRID_WIN`` — a hybrid strategy (its selected leg) produced the
      better result.
    * ``TIE`` — baseline and strategy tied after normalization.
    * ``NO_COMPARABLE_RESULT`` — no fair comparison was possible (the
      strategy leg did not execute, the baseline is disabled, or no
      comparable objective/energy existed).

    These describe *measured outcomes only*; no "quantum advantage" claim is
    ever derived from a classification.
    """

    CLASSICAL_WIN = "classical_win"
    QUANTUM_WIN = "quantum_win"
    HYBRID_WIN = "hybrid_win"
    TIE = "tie"
    NO_COMPARABLE_RESULT = "no_comparable_result"

    @classmethod
    def parse(cls, value: Any) -> BenchmarkWinner:
        """Coerce a label or member to a :class:`BenchmarkWinner`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.value == text or member.name.lower() == text:
                return member
        raise ValueError(
            f"unknown benchmark winner {value!r}; expected one of: "
            + ", ".join(member.value for member in cls)
        )


@dataclass
class BaselineConfig:
    """Configuration of the classical baseline (QMQ-05 §4/§8).

    The baseline reuses the QMQ-02/04 exact exhaustive solver — no second
    classical solver exists.  ``kind`` is fixed to ``"classical"`` until the
    SDK adds another baseline; only that kind is honoured.
    """

    kind: str = "classical"
    enabled: bool = True
    solver: ExhaustiveSolver | None = None
    max_variables: int = 20


@dataclass
class Benchmark:
    """Definition of one benchmark (QMQ-05 §4).

    A benchmark is a reusable, serializable recipe: the problem to solve,
    the strategy to run (defaulting to the problem's preferred strategy),
    optional algorithm/execution options, the classical baseline
    configuration, an optional known optimum, and free-form metadata.
    """

    benchmark_id: str
    name: str
    problem: QuantumProblem
    strategy: ComputationStrategy | str | None = None
    algorithm: str = ""
    options: ExecutionOptions | None = None
    formulation: str = "optimization"
    baseline: BaselineConfig | None = None
    known_optimum: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.benchmark_id:
            raise ValueError("benchmark_id must be a non-empty string")
        if not self.name:
            raise ValueError("name must be a non-empty string")
        if not isinstance(self.problem, QuantumProblem):
            raise TypeError("Benchmark requires a QuantumProblem")
        if isinstance(self.strategy, str):
            self.strategy = ComputationStrategy.parse(self.strategy)
        if self.known_optimum is not None:
            self.known_optimum = float(self.known_optimum)

    @property
    def resolved_strategy(self) -> ComputationStrategy | None:
        """Strategy of the benchmark (its own, else the problem's preferred)."""
        if self.strategy is not None:
            return (
                self.strategy
                if isinstance(self.strategy, ComputationStrategy)
                else ComputationStrategy.parse(self.strategy)
            )
        preferred = self.problem.preferred_strategy
        if preferred is None:
            return None
        return (
            preferred
            if isinstance(preferred, ComputationStrategy)
            else ComputationStrategy.parse(preferred)
        )

    @property
    def strategy_label(self) -> str | None:
        """Serialized strategy label of :attr:`resolved_strategy`."""
        resolved = self.resolved_strategy
        return resolved.name.lower() if resolved is not None else None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "benchmark_id": self.benchmark_id,
            "name": self.name,
            "problem": self.problem.to_dict(),
            "strategy": self.strategy_label,
            "algorithm": self.algorithm,
            "options": self.options.to_dict() if self.options is not None else None,
            "formulation": self.formulation,
            "baseline": (
                {
                    "kind": self.baseline.kind,
                    "enabled": self.baseline.enabled,
                    "max_variables": self.baseline.max_variables,
                }
                if self.baseline is not None
                else None
            ),
            "known_optimum": self.known_optimum,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Benchmark:
        """Rebuild a Benchmark from :meth:`to_dict` output."""
        baseline = data.get("baseline")
        return cls(
            benchmark_id=str(data["benchmark_id"]),
            name=str(data["name"]),
            problem=QuantumProblem.from_dict(dict(data["problem"])),
            strategy=(str(data["strategy"]) if data.get("strategy") else None),
            algorithm=str(data.get("algorithm", "")),
            options=(
                ExecutionOptions.from_dict(dict(data["options"]))
                if data.get("options") is not None
                else None
            ),
            formulation=str(data.get("formulation", "optimization")),
            baseline=(
                BaselineConfig(
                    kind=str(baseline.get("kind", "classical")),
                    enabled=bool(baseline.get("enabled", True)),
                    max_variables=int(baseline.get("max_variables", 20)),
                )
                if baseline is not None
                else None
            ),
            known_optimum=(
                float(data["known_optimum"]) if data.get("known_optimum") is not None else None
            ),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"Benchmark(id={self.benchmark_id!r}, name={self.name!r}, "
            f"strategy={self.strategy_label}, problem={self.problem.name!r})"
        )


@dataclass
class BenchmarkMetrics:
    """Measured quality / performance / resource metrics (QMQ-05 §6/§7).

    Missing information is ``None`` (or ``0`` for counts) — nothing is
    invented beyond what the execution layer actually reports.
    """

    # solution quality
    objective_value: float | None = None
    energy: float | None = None
    feasible: bool | None = None
    constraint_violations: int = 0
    constraint_violation_magnitude: float = 0.0
    optimality_gap: float | None = None
    approximation_ratio: float | None = None
    # execution performance
    wall_clock_time: float | None = None
    num_evaluations: int | None = None
    iterations: int | None = None
    shots: int | None = None
    executions: int = 1
    retries: int = 0
    # resource / metadata
    num_variables: int = 0
    num_constraints: int = 0
    num_qubits: int | None = None
    circuit_depth: int | None = None
    num_gates: int | None = None
    microquantum_version: str = ""
    backend: str = ""
    optimizer: str = ""
    seed: int | None = None
    optimization_level: int = 0
    status: str = "executed"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_execution(
        cls,
        problem: QuantumProblem,
        execution: Any,
        *,
        sense: ObjectiveSense | str,
        reference_optimum: float | None = None,
        wall_clock_time: float | None = None,
        options: ExecutionOptions | None = None,
        seed: int | None = None,
        backend: str = "",
        optimizer: str = "",
        microquantum_version: str = "",
        num_qubits: int | None = None,
        status: str = "executed",
        executions: int = 1,
        retries: int = 0,
    ) -> BenchmarkMetrics:
        """Build metrics from a normalized QMQ-04 execution result.

        ``execution`` may be a :class:`ClassicalExecutionResult`,
        :class:`QuantumExecutionResult`, or any leg exposing
        ``assignment``/``objective_value``/``energy``/``feasible``.
        ``reference_optimum`` is the known optimum (or the baseline optimum)
        used for the gap/ratio; ``None`` leaves them unknown.
        """
        parsed_sense = sense if isinstance(sense, ObjectiveSense) else ObjectiveSense.parse(sense)
        assignment = getattr(execution, "assignment", None)
        assignment = dict(assignment) if isinstance(assignment, dict) else {}
        objective_value = getattr(execution, "objective_value", None)
        objective_value = float(objective_value) if objective_value is not None else None
        energy = getattr(execution, "energy", None)
        energy = float(energy) if energy is not None else None
        feasible = getattr(execution, "feasible", None)
        feasible = bool(feasible) if feasible is not None else None

        violation_count, violation_magnitude = (0, 0.0)
        if assignment:
            violation_count, violation_magnitude = constraint_violations(problem, assignment)

        num_evaluations = getattr(execution, "num_evaluations", None)
        iterations = getattr(execution, "iterations", None)
        shots = getattr(execution, "shots", None)

        return cls(
            objective_value=objective_value,
            energy=energy,
            feasible=feasible,
            constraint_violations=violation_count,
            constraint_violation_magnitude=violation_magnitude,
            optimality_gap=(
                optimality_gap(objective_value, reference_optimum)
                if reference_optimum is not None
                else None
            ),
            approximation_ratio=(
                approximation_ratio(objective_value, reference_optimum, parsed_sense)
                if reference_optimum is not None
                else None
            ),
            wall_clock_time=(float(wall_clock_time) if wall_clock_time is not None else None),
            num_evaluations=(int(num_evaluations) if num_evaluations is not None else None),
            iterations=(int(iterations) if iterations is not None else None),
            shots=(int(shots) if shots is not None else None),
            executions=executions,
            retries=retries,
            num_variables=len(problem.variables),
            num_constraints=len(problem.constraints),
            num_qubits=num_qubits,
            microquantum_version=microquantum_version,
            backend=backend,
            optimizer=optimizer,
            seed=seed,
            optimization_level=options.optimization_level if options is not None else 0,
            status=status,
            metadata={
                "leg": getattr(execution, "leg", ""),
                "executor": getattr(execution, "executor", "") or getattr(execution, "solver", ""),
                "algorithm": getattr(execution, "algorithm", ""),
                "converged": getattr(execution, "converged", None),
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "objective_value": self.objective_value,
            "energy": self.energy,
            "feasible": self.feasible,
            "constraint_violations": self.constraint_violations,
            "constraint_violation_magnitude": self.constraint_violation_magnitude,
            "optimality_gap": self.optimality_gap,
            "approximation_ratio": self.approximation_ratio,
            "wall_clock_time": self.wall_clock_time,
            "num_evaluations": self.num_evaluations,
            "iterations": self.iterations,
            "shots": self.shots,
            "executions": self.executions,
            "retries": self.retries,
            "num_variables": self.num_variables,
            "num_constraints": self.num_constraints,
            "num_qubits": self.num_qubits,
            "circuit_depth": self.circuit_depth,
            "num_gates": self.num_gates,
            "microquantum_version": self.microquantum_version,
            "backend": self.backend,
            "optimizer": self.optimizer,
            "seed": self.seed,
            "optimization_level": self.optimization_level,
            "status": self.status,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkMetrics:
        """Rebuild metrics from :meth:`to_dict` output."""
        return cls(
            objective_value=(
                float(data["objective_value"]) if data.get("objective_value") is not None else None
            ),
            energy=(float(data["energy"]) if data.get("energy") is not None else None),
            feasible=(bool(data["feasible"]) if data.get("feasible") is not None else None),
            constraint_violations=int(data.get("constraint_violations", 0)),
            constraint_violation_magnitude=float(data.get("constraint_violation_magnitude", 0.0)),
            optimality_gap=(
                float(data["optimality_gap"]) if data.get("optimality_gap") is not None else None
            ),
            approximation_ratio=(
                float(data["approximation_ratio"])
                if data.get("approximation_ratio") is not None
                else None
            ),
            wall_clock_time=(
                float(data["wall_clock_time"]) if data.get("wall_clock_time") is not None else None
            ),
            num_evaluations=(
                int(data["num_evaluations"]) if data.get("num_evaluations") is not None else None
            ),
            iterations=(int(data["iterations"]) if data.get("iterations") is not None else None),
            shots=(int(data["shots"]) if data.get("shots") is not None else None),
            executions=int(data.get("executions", 1)),
            retries=int(data.get("retries", 0)),
            num_variables=int(data.get("num_variables", 0)),
            num_constraints=int(data.get("num_constraints", 0)),
            num_qubits=(int(data["num_qubits"]) if data.get("num_qubits") is not None else None),
            circuit_depth=(
                int(data["circuit_depth"]) if data.get("circuit_depth") is not None else None
            ),
            num_gates=(int(data["num_gates"]) if data.get("num_gates") is not None else None),
            microquantum_version=str(data.get("microquantum_version", "")),
            backend=str(data.get("backend", "")),
            optimizer=str(data.get("optimizer", "")),
            seed=(int(data["seed"]) if data.get("seed") is not None else None),
            optimization_level=int(data.get("optimization_level", 0)),
            status=str(data.get("status", "executed")),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"BenchmarkMetrics(objective={self.objective_value}, energy={self.energy}, "
            f"feasible={self.feasible}, gap={self.optimality_gap})"
        )


def _normalized(metrics: BenchmarkMetrics, sense: ObjectiveSense) -> float | None:
    """Higher-is-better scalar for one metrics object (centralized, §10)."""
    return normalized_score(sense, metrics.objective_value, metrics.energy)


def _feasibility_rank(feasible: bool | None) -> int:
    """``feasible > unknown > infeasible`` (QMQ-05 §12 policy)."""
    if feasible is True:
        return 2
    if feasible is None:
        return 1
    return 0


def _feasibility_rank_label(feasible: bool | None) -> str:
    if feasible is True:
        return "feasible"
    if feasible is None:
        return "unknown"
    return "infeasible"


def metrics_rank_key(
    metrics: BenchmarkMetrics, sense: ObjectiveSense
) -> tuple[int, float, float] | None:
    """Deterministic ``(feasibility class, violations, normalized score)`` key.

    Higher tuple is better: feasible beats unknown beats infeasible; among
    infeasible results a lower violation magnitude beats a higher one (the
    magnitude is negated so fewer violations rank higher), then the
    normalized objective decides.
    """
    score = _normalized(metrics, sense)
    if score is None:
        return None
    rank = _feasibility_rank(metrics.feasible)
    violations = metrics.constraint_violation_magnitude if metrics.feasible is False else 0.0
    return (rank, -violations, float(score))


def _winner_for_strategy(strategy: str) -> BenchmarkWinner:
    mapping = {
        "classical": BenchmarkWinner.CLASSICAL_WIN,
        "quantum": BenchmarkWinner.QUANTUM_WIN,
        "hybrid": BenchmarkWinner.HYBRID_WIN,
    }
    return mapping.get(strategy.lower(), BenchmarkWinner.NO_COMPARABLE_RESULT)


@dataclass
class BenchmarkComparison:
    """Benchmark strategy outcome vs the classical baseline (QMQ-05 §9/§12/§13).

    Fields:
        strategy: Strategy label that was benchmarked.
        baseline: Baseline label (``"classical"``).
        sense: Sense used for ranking (``"minimize"``/``"maximize"``).
        winner: Result classification.
        objective_delta: Normalized objective delta (strategy - baseline),
            positive means the strategy outcome is better.
        strategy_status: ``"executed"`` / ``"failed"`` / ``"skipped"``.
        baseline_status: Same for the baseline.
        selected_reason: Human-readable justification.
        metadata: Free-form (e.g. the QMQ-04 hybrid leg comparison dict).
    """

    strategy: str = ""
    baseline: str = "classical"
    sense: str = "minimize"
    winner: BenchmarkWinner = BenchmarkWinner.NO_COMPARABLE_RESULT
    objective_delta: float | None = None
    strategy_status: str = ""
    baseline_status: str = ""
    selected_reason: str = ""
    tie_break: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def build(
        cls,
        *,
        strategy: str,
        strategy_metrics: BenchmarkMetrics | None,
        baseline_metrics: BenchmarkMetrics | None,
        sense: ObjectiveSense | str = ObjectiveSense.MINIMIZE,
        strategy_status: str = "executed",
        baseline_status: str = "executed",
        metadata: dict[str, Any] | None = None,
    ) -> BenchmarkComparison:
        """Classify a strategy outcome against the classical baseline.

        Deterministic policy (QMQ-05 §12/§13):

        1. ``feasible`` beats ``unknown`` beats ``infeasible``;
        2. both feasible (or both unknown): better normalized objective wins
           (per sense; energy fallback, lower always better);
        3. both infeasible: fewer constraint violations wins, then objective;
        4. exact equalities are a ``TIE``;
        5. a missing strategy/baseline outcome, a disabled baseline, or a
           missing objective/energy produces ``NO_COMPARABLE_RESULT``.

        A strictly better strategy outcome is classified on the *strategy*
        (``classical`` -> CLASSICAL_WIN, ``quantum`` -> QUANTUM_WIN,
        ``hybrid`` -> HYBRID_WIN); a worse one is ``CLASSICAL_WIN``.
        """
        parsed_sense = sense if isinstance(sense, ObjectiveSense) else ObjectiveSense.parse(sense)
        label = sense_label(parsed_sense)
        metadata = dict(metadata or {})

        if baseline_metrics is None:
            return cls.build_none(
                strategy=strategy,
                sense=label,
                strategy_metrics=strategy_metrics,
                strategy_status=strategy_status,
                baseline_status="disabled",
                reason="no classical baseline result available for comparison "
                "(baseline disabled or failed)",
                metadata=metadata,
            )

        if strategy_metrics is None or strategy_metrics.status != _EXECUTED:
            return cls.build_none(
                strategy=strategy,
                sense=label,
                strategy_metrics=strategy_metrics,
                strategy_status=strategy_metrics.status if strategy_metrics else strategy_status,
                baseline_status=baseline_status,
                reason="the benchmark strategy did not execute; nothing to compare",
                metadata=metadata,
            )

        strategy_key = metrics_rank_key(strategy_metrics, parsed_sense)
        baseline_key = metrics_rank_key(baseline_metrics, parsed_sense)
        if strategy_key is None or baseline_key is None:
            return cls.build_none(
                strategy=strategy,
                sense=label,
                strategy_metrics=strategy_metrics,
                strategy_status="executed",
                baseline_status=baseline_status,
                reason=(
                    "no comparable objective/energy value for ranking "
                    f"(strategy={strategy_key is not None}, baseline={baseline_key is not None})"
                ),
                metadata=metadata,
            )

        strategy_score = _normalized(strategy_metrics, parsed_sense)
        baseline_score = _normalized(baseline_metrics, parsed_sense)
        delta = (
            float(strategy_score) - float(baseline_score)
            if strategy_score is not None and baseline_score is not None
            else None
        )

        if strategy_key > baseline_key:
            winner = _winner_for_strategy(strategy)
            reason = (
                f"{strategy} outcome ranked above the {baseline_status} classical baseline "
                f"(feasibility={_feasibility_rank_label(strategy_metrics.feasible)}, "
                f"delta={delta:+.3g})"
                if delta is not None
                else f"{strategy} outcome ranked above the classical baseline"
            )
            return cls(
                strategy=strategy,
                sense=label,
                winner=winner,
                objective_delta=delta,
                strategy_status="executed",
                baseline_status=baseline_status,
                selected_reason=reason,
                metadata=metadata,
            )
        if strategy_key < baseline_key:
            return cls(
                strategy=strategy,
                sense=label,
                winner=BenchmarkWinner.CLASSICAL_WIN,
                objective_delta=delta,
                strategy_status="executed",
                baseline_status=baseline_status,
                selected_reason=(
                    "the classical baseline ranked above the benchmark outcome "
                    f"(delta={delta:+.3g})"
                    if delta is not None
                    else "the classical baseline ranked above the benchmark outcome"
                ),
                metadata=metadata,
            )
        return cls(
            strategy=strategy,
            sense=label,
            winner=BenchmarkWinner.TIE,
            objective_delta=delta,
            strategy_status="executed",
            baseline_status=baseline_status,
            selected_reason=(
                "baseline and strategy outcome are equal after normalization "
                "(same feasibility class and objective)"
            ),
            tie_break="baseline and strategy outcome are tied exactly",
            metadata=metadata,
        )

    @classmethod
    def build_none(
        cls,
        *,
        strategy: str,
        sense: str,
        strategy_metrics: BenchmarkMetrics | None,
        strategy_status: str,
        baseline_status: str,
        reason: str,
        metadata: dict[str, Any],
    ) -> BenchmarkComparison:
        """Build a ``NO_COMPARABLE_RESULT`` comparison."""
        return cls(
            strategy=strategy,
            sense=sense,
            winner=BenchmarkWinner.NO_COMPARABLE_RESULT,
            strategy_status=strategy_status,
            baseline_status=baseline_status,
            selected_reason=reason,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "strategy": self.strategy,
            "baseline": self.baseline,
            "sense": self.sense,
            "winner": self.winner.value,
            "objective_delta": self.objective_delta,
            "strategy_status": self.strategy_status,
            "baseline_status": self.baseline_status,
            "selected_reason": self.selected_reason,
            "tie_break": self.tie_break,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkComparison:
        """Rebuild a comparison from :meth:`to_dict` output."""
        return cls(
            strategy=str(data.get("strategy", "")),
            baseline=str(data.get("baseline", "classical")),
            sense=str(data.get("sense", "minimize")),
            winner=BenchmarkWinner.parse(data.get("winner", "no_comparable_result")),
            objective_delta=(
                float(data["objective_delta"]) if data.get("objective_delta") is not None else None
            ),
            strategy_status=str(data.get("strategy_status", "")),
            baseline_status=str(data.get("baseline_status", "")),
            selected_reason=str(data.get("selected_reason", "")),
            tie_break=str(data.get("tie_break", "")),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"BenchmarkComparison(strategy={self.strategy!r}, "
            f"winner={self.winner.value}, sense={self.sense})"
        )


@dataclass
class BenchmarkRunSummary:
    """Aggregates of repeated benchmark runs (QMQ-05 §14)."""

    runs: int
    success_rate: float = 0.0
    feasibility_rate: float = 0.0
    mean_objective: float | None = None
    min_objective: float | None = None
    max_objective: float | None = None
    best_objective: float | None = None
    objective_stddev: float | None = None
    mean_execution_time: float | None = None
    winners: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "runs": self.runs,
            "success_rate": self.success_rate,
            "feasibility_rate": self.feasibility_rate,
            "mean_objective": self.mean_objective,
            "min_objective": self.min_objective,
            "max_objective": self.max_objective,
            "best_objective": self.best_objective,
            "objective_stddev": self.objective_stddev,
            "mean_execution_time": self.mean_execution_time,
            "winners": dict(self.winners),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkRunSummary:
        """Rebuild a summary from :meth:`to_dict` output."""
        winners = data.get("winners", {})
        return cls(
            runs=int(data.get("runs", 0)),
            success_rate=float(data.get("success_rate", 0.0)),
            feasibility_rate=float(data.get("feasibility_rate", 0.0)),
            mean_objective=(
                float(data["mean_objective"]) if data.get("mean_objective") is not None else None
            ),
            min_objective=(
                float(data["min_objective"]) if data.get("min_objective") is not None else None
            ),
            max_objective=(
                float(data["max_objective"]) if data.get("max_objective") is not None else None
            ),
            best_objective=(
                float(data["best_objective"]) if data.get("best_objective") is not None else None
            ),
            objective_stddev=(
                float(data["objective_stddev"])
                if data.get("objective_stddev") is not None
                else None
            ),
            mean_execution_time=(
                float(data["mean_execution_time"])
                if data.get("mean_execution_time") is not None
                else None
            ),
            winners={str(k): int(v) for k, v in winners.items()},
        )


@dataclass
class BenchmarkResult:
    """Serializable report of one benchmark run (QMQ-05 §16).

    The in-memory object keeps a reference to the underlying
    :class:`SolutionReport` (composition, QMQ-05 §17); serialization carries
    only lightweight reference metadata — the full solution report is not
    duplicated inside the benchmark report.
    """

    benchmark: Benchmark
    benchmark_id: str
    name: str
    strategy: str
    status: str = "executed"
    error: str = ""
    executed_strategy: str = ""
    metrics: BenchmarkMetrics | None = None
    comparison: BenchmarkComparison | None = None
    report: SolutionReport | None = None
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    finished_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    total_time: float = 0.0
    repetitions: list[BenchmarkResult] = field(default_factory=list)
    summary: BenchmarkRunSummary | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary (report kept as a reference)."""
        reference = None
        if self.report is not None:
            reference = {
                "solution_feasible": (
                    self.report.solution.feasible if self.report.solution is not None else None
                ),
                "selected_leg": self.report.selected_leg,
                "executor": (
                    self.report.provenance.executor if self.report.provenance is not None else ""
                ),
                "created_at": self.report.created_at,
            }
        return {
            "benchmark": self.benchmark.to_dict(),
            "benchmark_id": self.benchmark_id,
            "name": self.name,
            "strategy": self.strategy,
            "status": self.status,
            "error": self.error,
            "executed_strategy": self.executed_strategy,
            "metrics": self.metrics.to_dict() if self.metrics is not None else None,
            "comparison": self.comparison.to_dict() if self.comparison is not None else None,
            "report_ref": reference,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "total_time": self.total_time,
            "repetitions": [repetition.to_dict() for repetition in self.repetitions],
            "summary": self.summary.to_dict() if self.summary is not None else None,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkResult:
        """Rebuild a result from :meth:`to_dict` output.

        The :class:`SolutionReport` reference is intentionally not rebuilt
        (composition reference); all measured fields round-trip exactly.
        """
        metrics = data.get("metrics")
        comparison = data.get("comparison")
        summary = data.get("summary")
        return cls(
            benchmark=Benchmark.from_dict(dict(data["benchmark"])),
            benchmark_id=str(data["benchmark_id"]),
            name=str(data["name"]),
            strategy=str(data.get("strategy", "")),
            status=str(data.get("status", "executed")),
            error=str(data.get("error", "")),
            executed_strategy=str(data.get("executed_strategy", "")),
            metrics=BenchmarkMetrics.from_dict(dict(metrics)) if metrics is not None else None,
            comparison=(
                BenchmarkComparison.from_dict(dict(comparison)) if comparison is not None else None
            ),
            report=None,
            started_at=str(data.get("started_at", "")),
            finished_at=str(data.get("finished_at", "")),
            total_time=float(data.get("total_time", 0.0)),
            repetitions=[cls.from_dict(dict(rep)) for rep in data.get("repetitions", [])],
            summary=BenchmarkRunSummary.from_dict(dict(summary)) if summary is not None else None,
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        metrics = (
            f"objective={self.metrics.objective_value}, feasible={self.metrics.feasible}"
            if self.metrics is not None
            else "no-metrics"
        )
        comparison = f", winner={self.comparison.winner.value}" if self.comparison else ""
        return (
            f"BenchmarkResult(id={self.benchmark_id!r}, status={self.status}, "
            f"{metrics}{comparison})"
        )


@dataclass
class BenchmarkSuite:
    """A named collection of benchmarks for reproducible evaluation (QMQ-05 §18).

    ``benchmarks`` is keyed by ``benchmark_id`` so members are addressable and
    serializable.  The canonical suite is produced by
    :func:`quantsmind.quantum.benchmark.suite.default_suite`.
    """

    name: str
    description: str = ""
    benchmarks: dict[str, Benchmark] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("suite name must be a non-empty string")

    def add(self, benchmark: Benchmark) -> Benchmark:
        """Register a benchmark (duplicate ids are rejected)."""
        if benchmark.benchmark_id in self.benchmarks:
            raise ValueError(f"duplicate benchmark id {benchmark.benchmark_id!r}")
        self.benchmarks[benchmark.benchmark_id] = benchmark
        return benchmark

    def get(self, benchmark_id: str) -> Benchmark:
        """Return a benchmark by id."""
        return self.benchmarks[benchmark_id]

    @property
    def ids(self) -> list[str]:
        """Benchmark ids in registration order."""
        return list(self.benchmarks)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "benchmarks": [benchmark.to_dict() for benchmark in self.benchmarks.values()],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkSuite:
        """Rebuild a suite from :meth:`to_dict` output."""
        suite = cls(
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
        )
        for benchmark_data in data.get("benchmarks", []):
            suite.add(Benchmark.from_dict(dict(benchmark_data)))
        return suite

    def __repr__(self) -> str:
        return f"BenchmarkSuite(name={self.name!r}, benchmarks={list(self.benchmarks)})"


__all__ = [
    "BaselineConfig",
    "Benchmark",
    "BenchmarkComparison",
    "BenchmarkMetrics",
    "BenchmarkResult",
    "BenchmarkRunSummary",
    "BenchmarkSuite",
    "BenchmarkWinner",
    "metrics_rank_key",
]
