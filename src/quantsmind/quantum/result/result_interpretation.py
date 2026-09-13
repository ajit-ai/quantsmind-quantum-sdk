"""QMQ-06: structured, honest interpretation of execution and benchmark results.

:class:`ResultInterpreter` consumes a
:class:`~quantsmind.quantum.result.result.SolutionReport` and an optional
:class:`~quantsmind.quantum.benchmark.models.BenchmarkResult` and produces a
:class:`ResultInterpretation` — a domain-neutral, machine-readable explanation
of what was run, what the numbers say, and what they do *not* justify.

The interpretation layer is deliberately conservative:

* feasibility and objective facts are derived only from recorded data;
* a solution is labelled ``optimal`` only when a known optimum establishes
  it (within the configured numerical tolerance), never from completion;
* benchmark outcomes reuse the QMQ-05 comparison and its feasibility-first
  policy — no quantum-advantage claim is ever derived from a classification;
* missing information yields ``None`` / ``UNKNOWN`` plus a :class:`Limitation`,
  never an invented value.

The existing QMQ-01 :class:`~quantsmind.quantum.result.Interpretation` stays
the shallow solution-level summary attached by the workflow; QMQ-06 layers the
full structured interpretation on top of reports and benchmark results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.core.constraint import ConstraintStatus
from quantsmind.quantum.core.objective import ObjectiveSense
from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.benchmark.models import BenchmarkResult
    from quantsmind.quantum.result.result import SolutionReport


def _fmt(value: Any) -> str | None:
    """Format a float compactly for sentences (``None`` stays ``None``)."""
    if value is None:
        return None
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return str(value)


def _gap(achieved: float | None, optimum: float | None) -> float | None:
    """Relative distance from a known optimum (delegates to QMQ-05 math)."""
    from quantsmind.quantum.benchmark.metrics import optimality_gap

    return optimality_gap(achieved, optimum)


def _ratio(achieved: float | None, optimum: float | None, sense: str) -> float | None:
    """Approximation ratio against a known optimum (delegates to QMQ-05 math)."""
    from quantsmind.quantum.benchmark.metrics import approximation_ratio

    return approximation_ratio(achieved, optimum, sense)


class InterpretationStatus(Enum):
    """Outcome status of the interpreted run.

    Attributes:
        EXECUTED: The run completed as planned.
        FAILED: The run recorded a failure.
        DEGRADED: The run completed, but only after a fallback (e.g. a
            quantum-capable strategy executed classically).
        UNKNOWN: No execution status could be determined.
    """

    EXECUTED = "executed"
    FAILED = "failed"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

    @classmethod
    def parse(cls, value: Any) -> InterpretationStatus:
        """Coerce a label or member to an :class:`InterpretationStatus`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.value == text or member.name.lower() == text:
                return member
        return InterpretationStatus.UNKNOWN


class SolutionQuality(Enum):
    """Evidence-backed quality classification of a solution.

    Attributes:
        OPTIMAL: Feasible and equal to the known optimum (within tolerance).
        NEAR_OPTIMAL: Feasible and within the near-optimal tolerance of the
            known optimum.
        FEASIBLE: Feasible, with no evidence basis for optimality (no known
            optimum, or a gap beyond the near-optimal tolerance).
        INFEASIBLE: One or more constraints are violated.
        UNKNOWN: Feasibility could not be determined.
    """

    OPTIMAL = "optimal"
    NEAR_OPTIMAL = "near_optimal"
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    UNKNOWN = "unknown"

    @classmethod
    def parse(cls, value: Any) -> SolutionQuality:
        """Coerce a label or member to a :class:`SolutionQuality`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower().replace("-", "_")
        for member in cls:
            if member.value == text or member.name.lower() == text:
                return member
        return SolutionQuality.UNKNOWN


class FeasibilityStatus(Enum):
    """Constraint-satisfaction status of a solution.

    Attributes:
        FEASIBLE: No constraint is violated.
        INFEASIBLE: At least one constraint is violated.
        UNKNOWN: Constraint satisfaction could not be determined.
    """

    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    UNKNOWN = "unknown"

    @classmethod
    def parse(cls, value: Any) -> FeasibilityStatus:
        """Coerce a label or member to a :class:`FeasibilityStatus`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.value == text or member.name.lower() == text:
                return member
        return FeasibilityStatus.UNKNOWN


class Qualification(Enum):
    """Evidential basis behind an interpretation claim.

    Attributes:
        MATHEMATICAL_PROOF: Optimality established by an exact method (e.g.
            exhaustive search over the full discrete space).
        EMPIRICAL: Claim rests on recorded measurements.
        HEURISTIC: Claim rests on a heuristic method; optimality is not
            established.
        UNCERTAIN: Insufficient evidence for any stronger claim.
    """

    MATHEMATICAL_PROOF = "mathematical_proof"
    EMPIRICAL = "empirical"
    HEURISTIC = "heuristic"
    UNCERTAIN = "uncertain"

    @classmethod
    def parse(cls, value: Any) -> Qualification:
        """Coerce a label or member to a :class:`Qualification`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower().replace("-", "_")
        for member in cls:
            if member.value == text or member.name.lower() == text:
                return member
        return Qualification.UNCERTAIN


@dataclass
class Limitation:
    """One honest caveat about what an interpretation does *not* establish.

    Args:
        category: Machine-readable category, e.g. ``"known_optimum_unavailable"``.
        message: Human-readable limitation statement.
    """

    category: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {"category": self.category, "message": self.message}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Limitation:
        """Rebuild a limitation from :meth:`to_dict` output."""
        return cls(
            category=str(data.get("category", "")),
            message=str(data.get("message", "")),
        )


@dataclass
class FeasibilityInterpretation:
    """Structured view of constraint satisfaction.

    Args:
        status: Feasibility status.
        satisfied: Number of satisfied constraints.
        violated: Number of violated constraints.
        unknown: Number of unevaluated constraints.
        total: Total number of assessed constraints.
        violated_constraints: Names of violated constraints (when known).
        violation_magnitude: Total numerical violation magnitude.
        explanation: Human-readable sentence.
    """

    status: FeasibilityStatus = FeasibilityStatus.UNKNOWN
    satisfied: int = 0
    violated: int = 0
    unknown: int = 0
    total: int = 0
    violated_constraints: list[str] = field(default_factory=list)
    violation_magnitude: float = 0.0
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "status": self.status.value,
            "satisfied": self.satisfied,
            "violated": self.violated,
            "unknown": self.unknown,
            "total": self.total,
            "violated_constraints": list(self.violated_constraints),
            "violation_magnitude": self.violation_magnitude,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeasibilityInterpretation:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            status=FeasibilityStatus.parse(data.get("status", "unknown")),
            satisfied=int(data.get("satisfied", 0)),
            violated=int(data.get("violated", 0)),
            unknown=int(data.get("unknown", 0)),
            total=int(data.get("total", 0)),
            violated_constraints=[str(name) for name in data.get("violated_constraints", [])],
            violation_magnitude=float(data.get("violation_magnitude", 0.0)),
            explanation=str(data.get("explanation", "")),
        )


@dataclass
class ObjectiveInterpretation:
    """Structured view of the interpreted objective.

    Args:
        sense: Optimization sense (``"minimize"`` / ``"maximize"``).
        objective_value: Recorded objective value of the returned solution.
        energy: Recorded QUBO/Ising energy (when reported).
        known_optimum: Known optimum supplied to the benchmark (or ``None``).
        optimality_gap: Relative distance from the known optimum (``None``
            when no optimum is available).
        approximation_ratio: Approximation ratio vs the known optimum
            (``None`` when not interpretable).
        quality: Evidence-backed :class:`SolutionQuality`.
        qualification: Evidential basis of the quality claim.
        explanation: Human-readable sentence.
    """

    sense: str = "minimize"
    objective_value: float | None = None
    energy: float | None = None
    known_optimum: float | None = None
    optimality_gap: float | None = None
    approximation_ratio: float | None = None
    quality: SolutionQuality = SolutionQuality.UNKNOWN
    qualification: Qualification = Qualification.UNCERTAIN
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "sense": self.sense,
            "objective_value": self.objective_value,
            "energy": self.energy,
            "known_optimum": self.known_optimum,
            "optimality_gap": self.optimality_gap,
            "approximation_ratio": self.approximation_ratio,
            "quality": self.quality.value,
            "qualification": self.qualification.value,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectiveInterpretation:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            sense=str(data.get("sense", "minimize")),
            objective_value=(
                float(data["objective_value"]) if data.get("objective_value") is not None else None
            ),
            energy=(float(data["energy"]) if data.get("energy") is not None else None),
            known_optimum=(
                float(data["known_optimum"]) if data.get("known_optimum") is not None else None
            ),
            optimality_gap=(
                float(data["optimality_gap"]) if data.get("optimality_gap") is not None else None
            ),
            approximation_ratio=(
                float(data["approximation_ratio"])
                if data.get("approximation_ratio") is not None
                else None
            ),
            quality=SolutionQuality.parse(data.get("quality", "unknown")),
            qualification=Qualification.parse(data.get("qualification", "uncertain")),
            explanation=str(data.get("explanation", "")),
        )


@dataclass
class BenchmarkInterpretation:
    """Interpreted benchmark outcome vs the classical baseline.

    Args:
        benchmark_id: Id of the benchmark (if any).
        baseline: Baseline label (``"classical"``).
        winner: QMQ-05 winner classification value or ``None``.
        objective_delta: Normalized objective delta (strategy - baseline).
        measured_basis: What the outcome was ranked on (e.g. ``["objective"]``).
        strategy_status: Status of the benchmarked strategy leg.
        baseline_status: Status of the baseline leg.
        outcome: ``"better"`` / ``"worse"`` / ``"tie"`` /
            ``"not_comparable"`` for the benchmarked strategy.
        explanation: Human-readable sentence.
    """

    benchmark_id: str = ""
    baseline: str = "classical"
    winner: str | None = None
    objective_delta: float | None = None
    measured_basis: list[str] = field(default_factory=list)
    strategy_status: str = ""
    baseline_status: str = ""
    outcome: str = ""
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "benchmark_id": self.benchmark_id,
            "baseline": self.baseline,
            "winner": self.winner,
            "objective_delta": self.objective_delta,
            "measured_basis": list(self.measured_basis),
            "strategy_status": self.strategy_status,
            "baseline_status": self.baseline_status,
            "outcome": self.outcome,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkInterpretation:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            benchmark_id=str(data.get("benchmark_id", "")),
            baseline=str(data.get("baseline", "classical")),
            winner=(str(data["winner"]) if data.get("winner") is not None else None),
            objective_delta=(
                float(data["objective_delta"]) if data.get("objective_delta") is not None else None
            ),
            measured_basis=[str(b) for b in data.get("measured_basis", [])],
            strategy_status=str(data.get("strategy_status", "")),
            baseline_status=str(data.get("baseline_status", "")),
            outcome=str(data.get("outcome", "")),
            explanation=str(data.get("explanation", "")),
        )


@dataclass
class StrategyInterpretation:
    """Requested vs selected vs executed strategy.

    Args:
        requested_strategy: Strategy the caller asked for.
        selected_strategy: Strategy actually selected for execution.
        actual_strategy: Strategy that produced the outcome (may be a
            degraded fallback).
        fallback_used: Whether execution degraded to another strategy.
        reason: Reason for the fallback (when used).
        explanation: Human-readable sentence.
    """

    requested_strategy: str | None = None
    selected_strategy: str | None = None
    actual_strategy: str | None = None
    fallback_used: bool = False
    reason: str = ""
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "requested_strategy": self.requested_strategy,
            "selected_strategy": self.selected_strategy,
            "actual_strategy": self.actual_strategy,
            "fallback_used": self.fallback_used,
            "reason": self.reason,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StrategyInterpretation:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            requested_strategy=(
                str(data["requested_strategy"])
                if data.get("requested_strategy") is not None
                else None
            ),
            selected_strategy=(
                str(data["selected_strategy"])
                if data.get("selected_strategy") is not None
                else None
            ),
            actual_strategy=(
                str(data["actual_strategy"]) if data.get("actual_strategy") is not None else None
            ),
            fallback_used=bool(data.get("fallback_used", False)),
            reason=str(data.get("reason", "")),
            explanation=str(data.get("explanation", "")),
        )


@dataclass
class AlgorithmInterpretation:
    """Algorithm and runtime details of the executed run.

    Args:
        algorithm: Algorithm id (e.g. ``"qaoa"``, ``"exhaustive"``) or ``""``.
        backend: Backend that executed the quantum leg or ``""``.
        optimizer: Optimizer label used by the variational loop or ``""``.
        num_qubits: Mapped qubit count or ``None``.
        circuit_depth: Circuit depth or ``None``.
        num_gates: Gate count or ``None``.
        shots: Shot count or ``None``.
        microquantum_version: MicroQuantum version string or ``""``.
        explanation: Human-readable sentence.
    """

    algorithm: str = ""
    backend: str = ""
    optimizer: str = ""
    num_qubits: int | None = None
    circuit_depth: int | None = None
    num_gates: int | None = None
    shots: int | None = None
    microquantum_version: str = ""
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "algorithm": self.algorithm,
            "backend": self.backend,
            "optimizer": self.optimizer,
            "num_qubits": self.num_qubits,
            "circuit_depth": self.circuit_depth,
            "num_gates": self.num_gates,
            "shots": self.shots,
            "microquantum_version": self.microquantum_version,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlgorithmInterpretation:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            algorithm=str(data.get("algorithm", "")),
            backend=str(data.get("backend", "")),
            optimizer=str(data.get("optimizer", "")),
            num_qubits=(int(data["num_qubits"]) if data.get("num_qubits") is not None else None),
            circuit_depth=(
                int(data["circuit_depth"]) if data.get("circuit_depth") is not None else None
            ),
            num_gates=(int(data["num_gates"]) if data.get("num_gates") is not None else None),
            shots=(int(data["shots"]) if data.get("shots") is not None else None),
            microquantum_version=str(data.get("microquantum_version", "")),
            explanation=str(data.get("explanation", "")),
        )


@dataclass
class ExecutionInterpretation:
    """Execution-level status and cost facts.

    Args:
        executor: Executor label (e.g. ``"classical/exhaustive"``) or ``""``.
        status: Execution status (``"executed"`` / ``"failed"`` / ...).
        error: Recorded error message or ``""``.
        failure_category: Coarse failure category when the run failed.
        wall_clock_time: Wall-clock time of the interpreted phase.
        num_evaluations: Number of objective evaluations.
        iterations: Variational iterations.
        executions: Number of executions.
        retries: Number of retries.
        selected_leg: Selected leg of a hybrid run (``"classical"`` /
            ``"quantum"``) or ``None``.
        classical_status: Status of the classical leg/baseline or ``None``.
        quantum_status: Status of the quantum leg or ``None``.
        explanation: Human-readable sentence.
    """

    executor: str = ""
    status: str = "executed"
    error: str = ""
    failure_category: str | None = None
    wall_clock_time: float | None = None
    num_evaluations: int | None = None
    iterations: int | None = None
    executions: int = 0
    retries: int = 0
    selected_leg: str | None = None
    classical_status: str | None = None
    quantum_status: str | None = None
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "executor": self.executor,
            "status": self.status,
            "error": self.error,
            "failure_category": self.failure_category,
            "wall_clock_time": self.wall_clock_time,
            "num_evaluations": self.num_evaluations,
            "iterations": self.iterations,
            "executions": self.executions,
            "retries": self.retries,
            "selected_leg": self.selected_leg,
            "classical_status": self.classical_status,
            "quantum_status": self.quantum_status,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionInterpretation:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            executor=str(data.get("executor", "")),
            status=str(data.get("status", "executed")),
            error=str(data.get("error", "")),
            failure_category=(
                str(data["failure_category"]) if data.get("failure_category") is not None else None
            ),
            wall_clock_time=(
                float(data["wall_clock_time"]) if data.get("wall_clock_time") is not None else None
            ),
            num_evaluations=(
                int(data["num_evaluations"]) if data.get("num_evaluations") is not None else None
            ),
            iterations=(int(data["iterations"]) if data.get("iterations") is not None else None),
            executions=int(data.get("executions", 0)),
            retries=int(data.get("retries", 0)),
            selected_leg=(
                str(data["selected_leg"]) if data.get("selected_leg") is not None else None
            ),
            classical_status=(
                str(data["classical_status"]) if data.get("classical_status") is not None else None
            ),
            quantum_status=(
                str(data["quantum_status"]) if data.get("quantum_status") is not None else None
            ),
            explanation=str(data.get("explanation", "")),
        )


@dataclass
class ProvenanceOverview:
    """Consolidated provenance view of an interpreted run.

    Args:
        problem_name: Name of the problem that was solved.
        formulation: Formulation kind (``"optimization"``) or ``""``.
        strategy: Strategy that produced the outcome or ``None``.
        algorithm: Algorithm id or ``""``.
        executor: Executor label or ``""``.
        backend: Backend used or ``""``.
        microquantum_version: MicroQuantum version string or ``""``.
        sdk_version: QuantsMind SDK version or ``""``.
        benchmark_id: Benchmark id (if any) or ``None``.
        baseline: Classical baseline label or ``""``.
        created_at: UTC ISO timestamp of the report.
    """

    problem_name: str = ""
    formulation: str = ""
    strategy: str | None = None
    algorithm: str = ""
    executor: str = ""
    backend: str = ""
    microquantum_version: str = ""
    sdk_version: str = ""
    benchmark_id: str | None = None
    baseline: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_name": self.problem_name,
            "formulation": self.formulation,
            "strategy": self.strategy,
            "algorithm": self.algorithm,
            "executor": self.executor,
            "backend": self.backend,
            "microquantum_version": self.microquantum_version,
            "sdk_version": self.sdk_version,
            "benchmark_id": self.benchmark_id,
            "baseline": self.baseline,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProvenanceOverview:
        """Rebuild from :meth:`to_dict` output."""
        return cls(
            problem_name=str(data.get("problem_name", "")),
            formulation=str(data.get("formulation", "")),
            strategy=(str(data["strategy"]) if data.get("strategy") is not None else None),
            algorithm=str(data.get("algorithm", "")),
            executor=str(data.get("executor", "")),
            backend=str(data.get("backend", "")),
            microquantum_version=str(data.get("microquantum_version", "")),
            sdk_version=str(data.get("sdk_version", "")),
            benchmark_id=(
                str(data["benchmark_id"]) if data.get("benchmark_id") is not None else None
            ),
            baseline=str(data.get("baseline", "")),
            created_at=str(data.get("created_at", "")),
        )


@dataclass
class ResultInterpretation:
    """Complete structured interpretation of one execution / benchmark result.

    All sections are always present when constructed by :class:`ResultInterpreter`
    (they may carry ``None`` / ``UNKNOWN`` values when information is missing).
    The flat view properties mirror selected machine-readable fields so
    downstream consumers do not need to descend into the sections.

    Args:
        status: Run :class:`InterpretationStatus`.
        summary: Generated human-readable narrative (only supported claims).
        solution_quality: Evidence-backed :class:`SolutionQuality`.
        qualification: Overall evidential basis of the quality claim.
        feasibility: Constraint satisfaction section.
        objective: Objective facts and quality section.
        benchmark: Benchmark outcome section (``None`` without a benchmark).
        strategy: Requested/selected/actual strategy section.
        algorithm: Algorithm and runtime details.
        execution: Execution status and cost facts.
        limitations: Applicable caveats (:class:`Limitation` list).
        provenance: Consolidated provenance view.
    """

    status: InterpretationStatus = InterpretationStatus.UNKNOWN
    summary: str = ""
    solution_quality: SolutionQuality = SolutionQuality.UNKNOWN
    qualification: Qualification = Qualification.UNCERTAIN
    feasibility: FeasibilityInterpretation | None = None
    objective: ObjectiveInterpretation | None = None
    benchmark: BenchmarkInterpretation | None = None
    strategy: StrategyInterpretation | None = None
    algorithm: AlgorithmInterpretation | None = None
    execution: ExecutionInterpretation | None = None
    limitations: list[Limitation] = field(default_factory=list)
    provenance: ProvenanceOverview | None = None

    # -- flat machine-readable view ----------------------------------------

    @property
    def winner(self) -> str | None:
        """Benchmark winner classification value (``None`` without a benchmark)."""
        return self.benchmark.winner if self.benchmark is not None else None

    @property
    def objective_value(self) -> float | None:
        """Recorded objective value of the decoded solution."""
        return self.objective.objective_value if self.objective is not None else None

    @property
    def optimality_gap(self) -> float | None:
        """Relative distance from the known optimum (``None`` when unavailable)."""
        return self.objective.optimality_gap if self.objective is not None else None

    @property
    def approximation_ratio(self) -> float | None:
        """Approximation ratio vs the known optimum (``None`` when unavailable)."""
        return self.objective.approximation_ratio if self.objective is not None else None

    @property
    def requested_strategy(self) -> str | None:
        """Strategy the caller asked for."""
        return self.strategy.requested_strategy if self.strategy is not None else None

    @property
    def selected_strategy(self) -> str | None:
        """Strategy actually selected for execution."""
        return self.strategy.selected_strategy if self.strategy is not None else None

    @property
    def actual_executor(self) -> str:
        """Executor label that produced the outcome."""
        return self.execution.executor if self.execution is not None else ""

    @property
    def fallback_used(self) -> bool:
        """Whether execution degraded to another strategy."""
        return self.strategy.fallback_used if self.strategy is not None else False

    @property
    def feasibility_status(self) -> str | None:
        """Feasibility status value (``None`` when the section is absent)."""
        return self.feasibility.status.value if self.feasibility is not None else None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "status": self.status.value,
            "summary": self.summary,
            "solution_quality": self.solution_quality.value,
            "qualification": self.qualification.value,
            "feasibility": (self.feasibility.to_dict() if self.feasibility is not None else None),
            "objective": (self.objective.to_dict() if self.objective is not None else None),
            "benchmark": (self.benchmark.to_dict() if self.benchmark is not None else None),
            "strategy": (self.strategy.to_dict() if self.strategy is not None else None),
            "algorithm": (self.algorithm.to_dict() if self.algorithm is not None else None),
            "execution": (self.execution.to_dict() if self.execution is not None else None),
            "limitations": [limitation.to_dict() for limitation in self.limitations],
            "provenance": (self.provenance.to_dict() if self.provenance is not None else None),
            "winner": self.winner,
            "objective_value": self.objective_value,
            "optimality_gap": self.optimality_gap,
            "approximation_ratio": self.approximation_ratio,
            "requested_strategy": self.requested_strategy,
            "selected_strategy": self.selected_strategy,
            "actual_executor": self.actual_executor,
            "fallback_used": self.fallback_used,
            "feasibility_status": self.feasibility_status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResultInterpretation:
        """Rebuild from :meth:`to_dict` output."""
        feasibility = data.get("feasibility")
        objective = data.get("objective")
        benchmark = data.get("benchmark")
        strategy = data.get("strategy")
        algorithm = data.get("algorithm")
        execution = data.get("execution")
        provenance = data.get("provenance")
        return cls(
            status=InterpretationStatus.parse(data.get("status", "unknown")),
            summary=str(data.get("summary", "")),
            solution_quality=SolutionQuality.parse(data.get("solution_quality", "unknown")),
            qualification=Qualification.parse(data.get("qualification", "uncertain")),
            feasibility=(
                FeasibilityInterpretation.from_dict(dict(feasibility))
                if feasibility is not None
                else None
            ),
            objective=(
                ObjectiveInterpretation.from_dict(dict(objective))
                if objective is not None
                else None
            ),
            benchmark=(
                BenchmarkInterpretation.from_dict(dict(benchmark))
                if benchmark is not None
                else None
            ),
            strategy=(
                StrategyInterpretation.from_dict(dict(strategy)) if strategy is not None else None
            ),
            algorithm=(
                AlgorithmInterpretation.from_dict(dict(algorithm))
                if algorithm is not None
                else None
            ),
            execution=(
                ExecutionInterpretation.from_dict(dict(execution))
                if execution is not None
                else None
            ),
            limitations=[Limitation.from_dict(dict(item)) for item in data.get("limitations", [])],
            provenance=(
                ProvenanceOverview.from_dict(dict(provenance)) if provenance is not None else None
            ),
        )

    def __repr__(self) -> str:
        return (
            f"ResultInterpretation(status={self.status.value}, "
            f"quality={self.solution_quality.value}, "
            f"winner={self.winner})"
        )


class ResultInterpreter:
    """Builds :class:`ResultInterpretation` objects from reports and benchmarks.

    The interpreter is stateless apart from its numerical tolerances; the
    same inputs always produce the same interpretation (deterministic).
    """

    def __init__(
        self,
        *,
        gap_tolerance: float = 1e-9,
        near_optimal_tolerance: float = 0.1,
    ) -> None:
        self._gap_tolerance = float(gap_tolerance)
        self._near_optimal_tolerance = float(near_optimal_tolerance)

    def interpret_report(
        self,
        report: SolutionReport,
        *,
        gap_tolerance: float | None = None,
        near_optimal_tolerance: float | None = None,
    ) -> ResultInterpretation:
        """Interpret a solution report without benchmark evidence."""
        return self.interpret(
            report,
            benchmark=None,
            gap_tolerance=gap_tolerance,
            near_optimal_tolerance=near_optimal_tolerance,
        )

    def interpret_benchmark(
        self,
        benchmark: BenchmarkResult,
        *,
        gap_tolerance: float | None = None,
        near_optimal_tolerance: float | None = None,
    ) -> ResultInterpretation:
        """Interpret a benchmark result (using its embedded report when present)."""
        return self.interpret(
            benchmark.report,
            benchmark=benchmark,
            gap_tolerance=gap_tolerance,
            near_optimal_tolerance=near_optimal_tolerance,
        )

    def interpret(
        self,
        report: SolutionReport | None = None,
        *,
        benchmark: BenchmarkResult | None = None,
        gap_tolerance: float | None = None,
        near_optimal_tolerance: float | None = None,
    ) -> ResultInterpretation:
        """Produce a full structured interpretation of a run.

        Args:
            report: The workflow :class:`SolutionReport` (optional when full
                benchmark evidence exists, otherwise required for the
                solution-level facts).
            benchmark: The QMQ-05 :class:`BenchmarkResult` (optional).
            gap_tolerance: Optimality distance considered exact (overrides the
                interpreter default).
            near_optimal_tolerance: Gap below which a non-optimal result is
                labelled :attr:`SolutionQuality.NEAR_OPTIMAL`.

        Returns:
            A :class:`ResultInterpretation` over the available data.
        """
        gap_tol = self._gap_tolerance if gap_tolerance is None else float(gap_tolerance)
        near_tol = (
            self._near_optimal_tolerance
            if near_optimal_tolerance is None
            else float(near_optimal_tolerance)
        )
        return self._build(report, benchmark, gap_tol, near_tol)

    def summarize(
        self,
        report: SolutionReport | None = None,
        *,
        benchmark: BenchmarkResult | None = None,
    ) -> str:
        """Shortcut returning just the generated narrative of an interpretation."""
        return self.interpret(report, benchmark=benchmark).summary

    # -- construction -------------------------------------------------------

    def _build(
        self,
        report: SolutionReport | None,
        benchmark: BenchmarkResult | None,
        gap_tol: float,
        near_tol: float,
    ) -> ResultInterpretation:
        metrics = benchmark.metrics if benchmark is not None else None
        comparison = benchmark.comparison if benchmark is not None else None
        provenance = report.provenance if report is not None else None
        problem = report.problem if report is not None else None
        report_comparison = report.comparison if report is not None else None

        sense = self._sense_of(report, benchmark)
        feasibility = self._feasibility(report, benchmark)

        requested = self._requested_strategy(benchmark, problem)
        selected = self._selected_strategy(benchmark, report)
        actual = self._actual_strategy(benchmark, report, selected)
        fallback = self._fallback_used(selected, actual, provenance)

        executable_executor = self._executor(report, benchmark)
        algorithm = self._algorithm(report, benchmark)
        backend = self._backend(report, benchmark)
        exact = self._is_exact(executable_executor, algorithm)
        quantum_used = self._quantum_used(actual, executable_executor, algorithm)

        objective = self._objective_section(
            report,
            benchmark,
            feasibility.status,
            sense,
            gap_tol,
            near_tol,
            exact,
            quantum_used,
        )

        benchmark_section = self._benchmark_section(benchmark, metrics, comparison, sense)

        strategy_section = self._strategy_section(requested, selected, actual, fallback)

        algorithm_section = self._algorithm_section(report, benchmark, metrics, algorithm, backend)

        execution_section = self._execution_section(
            benchmark, metrics, report_comparison, comparison, executable_executor, fallback
        )

        status = self._status(benchmark, fallback)
        if status is InterpretationStatus.FAILED and strategy_section is not None:
            strategy_section.reason = execution_section.error

        provenance_section = self._provenance_section(
            report,
            benchmark,
            problem,
            provenance,
            actual,
            algorithm,
            executable_executor,
            backend,
            metrics,
        )

        limitations = self._limitations(
            benchmark,
            feasibility,
            objective,
            status,
            fallback,
            quantum_used,
            benchmark_section,
        )

        summary = self._build_summary(
            sense,
            feasibility,
            objective,
            status,
            strategy_section,
            algorithm_section,
            execution_section,
            benchmark_section,
            fallback,
            requested,
            actual,
            quantum_used,
        )

        qualification = (
            objective.qualification if objective is not None else Qualification.UNCERTAIN
        )

        return ResultInterpretation(
            status=status,
            summary=summary,
            solution_quality=(
                objective.quality if objective is not None else SolutionQuality.UNKNOWN
            ),
            qualification=qualification,
            feasibility=feasibility,
            objective=objective,
            benchmark=benchmark_section,
            strategy=strategy_section,
            algorithm=algorithm_section,
            execution=execution_section,
            limitations=limitations,
            provenance=provenance_section,
        )

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _label(value: Any) -> str | None:
        """Serialize a strategy value to its lower-case label."""
        if value is None:
            return None
        if isinstance(value, ComputationStrategy):
            return str(value.name).lower()
        return str(value).lower()

    @staticmethod
    def _sense_of(report: SolutionReport | None, benchmark: BenchmarkResult | None) -> str:
        if benchmark is not None and benchmark.comparison is not None:
            return benchmark.comparison.sense
        if report is not None and report.problem is not None and report.problem.objectives:
            sense = report.problem.objectives[0].sense
            return "maximize" if sense is ObjectiveSense.MAXIMIZE else "minimize"
        return "minimize"

    def _feasibility(
        self,
        report: SolutionReport | None,
        benchmark: BenchmarkResult | None,
    ) -> FeasibilityInterpretation:
        solution = report.solution if report is not None else None
        metrics = benchmark.metrics if benchmark is not None else None

        statuses: dict[str, ConstraintStatus] = {}
        if solution is not None and solution.constraint_status:
            statuses = dict(solution.constraint_status)
        values = list(statuses.values())
        satisfied = sum(s is ConstraintStatus.SATISFIED for s in values)
        violated = sum(s is ConstraintStatus.VIOLATED for s in values)
        unknown = sum(s is ConstraintStatus.UNKNOWN for s in values)
        total = len(values)
        violated_names = [
            name for name, item in statuses.items() if item is ConstraintStatus.VIOLATED
        ]

        metric_feasible = metrics.feasible if metrics is not None else None
        metric_violations = metrics.constraint_violations if metrics is not None else 0
        magnitude = metrics.constraint_violation_magnitude if metrics is not None else 0.0

        if violated > 0 or metric_feasible is False:
            fe_status = FeasibilityStatus.INFEASIBLE
        elif total > 0 or (metrics is not None and metric_feasible is True):
            fe_status = FeasibilityStatus.FEASIBLE
        else:
            fe_status = FeasibilityStatus.UNKNOWN

        if total:
            count_violated = violated
            count_satisfied = satisfied
            count_unknown = unknown
        elif metric_feasible is not None:
            count_violated = metric_violations
            count_satisfied = max(0, 1 - count_violated) if metric_feasible is True else 0
            count_unknown = 0
        else:
            count_violated = 0
            count_satisfied = 0
            count_unknown = total

        if fe_status is FeasibilityStatus.FEASIBLE:
            explanation = "All assessed constraints are satisfied."
        elif fe_status is FeasibilityStatus.INFEASIBLE:
            explanation = (
                f"{count_violated} of {max(total, 1)} assessed constraints are "
                f"violated (total magnitude {_fmt(magnitude) or 0})."
            )
        else:
            explanation = "Constraint satisfaction could not be determined from the available data."

        return FeasibilityInterpretation(
            status=fe_status,
            satisfied=count_satisfied,
            violated=count_violated,
            unknown=count_unknown,
            total=total or (1 if metric_feasible is not None else 0),
            violated_constraints=violated_names,
            violation_magnitude=float(magnitude),
            explanation=explanation,
        )

    def _objective_section(
        self,
        report: SolutionReport | None,
        benchmark: BenchmarkResult | None,
        feasibility: FeasibilityStatus,
        sense: str,
        gap_tol: float,
        near_tol: float,
        exact: bool,
        quantum_used: bool,
    ) -> ObjectiveInterpretation:
        metrics = benchmark.metrics if benchmark is not None else None
        solution = report.solution if report is not None else None
        provenance = report.provenance if report is not None else None

        objective_value: float | None = None
        if metrics is not None and metrics.objective_value is not None:
            objective_value = float(metrics.objective_value)
        elif solution is not None and solution.objective_values:
            objective_value = float(next(iter(solution.objective_values.values())))

        energy: float | None = None
        if metrics is not None and metrics.energy is not None:
            energy = float(metrics.energy)
        elif provenance is not None:
            raw_energy = provenance.execution_metadata.get("energy")
            energy = float(raw_energy) if raw_energy is not None else None

        known_optimum: float | None = None
        benchmark_def = benchmark.benchmark if benchmark is not None else None
        if benchmark_def is not None and benchmark_def.known_optimum is not None:
            known_optimum = float(benchmark_def.known_optimum)

        total_gap: float | None = None
        total_ratio: float | None = None
        if objective_value is not None and known_optimum is not None:
            total_gap = _gap(objective_value, known_optimum)
            total_ratio = _ratio(objective_value, known_optimum, sense)
        elif known_optimum is not None and metrics is not None:
            total_gap = metrics.optimality_gap
            total_ratio = metrics.approximation_ratio

        quality = self._classify_quality(
            feasibility, objective_value, known_optimum, total_gap, gap_tol, near_tol
        )
        qualification = self._classify_qualification(quality, exact, quantum_used)
        explanation = self._objective_explanation(
            quality, objective_value, known_optimum, total_gap, sense
        )

        return ObjectiveInterpretation(
            sense=sense,
            objective_value=objective_value,
            energy=energy,
            known_optimum=known_optimum,
            optimality_gap=total_gap,
            approximation_ratio=total_ratio,
            quality=quality,
            qualification=qualification,
            explanation=explanation,
        )

    @staticmethod
    def _classify_quality(
        feasibility: FeasibilityStatus,
        objective_value: float | None,
        known_optimum: float | None,
        gap: float | None,
        gap_tol: float,
        near_tol: float,
    ) -> SolutionQuality:
        if feasibility is FeasibilityStatus.INFEASIBLE:
            return SolutionQuality.INFEASIBLE
        if feasibility is FeasibilityStatus.UNKNOWN:
            return SolutionQuality.UNKNOWN
        if known_optimum is None or objective_value is None:
            return SolutionQuality.FEASIBLE
        if gap is None:
            return SolutionQuality.FEASIBLE
        if gap <= gap_tol:
            return SolutionQuality.OPTIMAL
        if gap <= max(near_tol, gap_tol):
            return SolutionQuality.NEAR_OPTIMAL
        return SolutionQuality.FEASIBLE

    @staticmethod
    def _classify_qualification(
        quality: SolutionQuality, exact: bool, quantum_used: bool
    ) -> Qualification:
        if quality is SolutionQuality.OPTIMAL:
            return Qualification.MATHEMATICAL_PROOF if exact else Qualification.EMPIRICAL
        if quality is SolutionQuality.UNKNOWN:
            return Qualification.UNCERTAIN
        if quantum_used:
            return Qualification.HEURISTIC
        return Qualification.EMPIRICAL

    @staticmethod
    def _objective_explanation(
        quality: SolutionQuality,
        objective_value: float | None,
        known_optimum: float | None,
        gap: float | None,
        sense: str,
    ) -> str:
        if quality is SolutionQuality.INFEASIBLE:
            return "The solution is infeasible; the objective is not qualified."
        if objective_value is None:
            return "No objective value was recorded."
        if known_optimum is None:
            return (
                f"Objective value {_fmt(objective_value)} ({sense} sense) with no "
                "known optimum to qualify against."
            )
        if gap is None:
            return (
                f"Objective value {_fmt(objective_value)} against known optimum "
                f"{_fmt(known_optimum)}."
            )
        if quality is SolutionQuality.OPTIMAL:
            return (
                f"Objective {_fmt(objective_value)} equals the known optimum "
                f"{_fmt(known_optimum)} within tolerance ({sense})."
            )
        if quality is SolutionQuality.NEAR_OPTIMAL:
            return (
                f"Objective {_fmt(objective_value)} is near the known optimum "
                f"{_fmt(known_optimum)} (gap {_fmt(gap)}) for {sense}."
            )
        return (
            f"Objective {_fmt(objective_value)} versus known optimum "
            f"{_fmt(known_optimum)} has gap {_fmt(gap)} for {sense}."
        )

    def _benchmark_section(
        self,
        benchmark: BenchmarkResult | None,
        metrics: Any,
        comparison: Any,
        sense: str,
    ) -> BenchmarkInterpretation | None:
        if benchmark is None:
            return None
        baseline = comparison.baseline if comparison is not None else "classical"
        winner = comparison.winner.value if comparison is not None else None
        delta = comparison.objective_delta if comparison is not None else None

        outcome = ""
        if winner is not None:
            if winner in {"quantum_win", "hybrid_win"}:
                outcome = "better"
            elif winner == "classical_win":
                outcome = "worse"
            elif winner == "tie":
                outcome = "tie"
            else:
                outcome = "not_comparable"

        basis: list[str] = []
        if winner is not None and winner != "no_comparable_result":
            if delta is not None:
                basis = ["objective"]
            elif metrics is not None and metrics.energy is not None:
                basis = ["energy"]
            else:
                basis = ["feasibility"]

        if outcome == "better":
            explanation = (
                f"The benchmarked strategy ranked above the {baseline} baseline "
                f"on {', '.join(basis) or 'the available evidence'}. This is a "
                "measured run-level result; it is not a quantum-advantage claim."
            )
        elif outcome == "worse":
            explanation = (
                f"The {baseline} baseline ranked above the benchmarked strategy "
                f"on {', '.join(basis) or 'the available evidence'}."
            )
        elif outcome == "tie":
            explanation = f"The benchmarked strategy tied the {baseline} baseline."
        elif winner is not None:
            explanation = f"No comparable {baseline} result was available to rank against."
        else:
            explanation = "No benchmark comparison was recorded."

        return BenchmarkInterpretation(
            benchmark_id=benchmark.benchmark_id,
            baseline=baseline,
            winner=winner,
            objective_delta=delta,
            measured_basis=basis,
            strategy_status=comparison.strategy_status if comparison is not None else "",
            baseline_status=comparison.baseline_status if comparison is not None else "",
            outcome=outcome,
            explanation=explanation,
        )

    def _strategy_section(
        self,
        requested: str | None,
        selected: str | None,
        actual: str | None,
        fallback: bool,
    ) -> StrategyInterpretation:
        reason = ""
        if fallback:
            reason = (
                "the quantum backend was unavailable; execution degraded to the classical solver"
            )
        parts = [
            f"requested={requested or 'unknown'}",
            f"selected={selected or 'unknown'}",
            f"actual={actual or 'unknown'}",
        ]
        explanation = "Strategy: " + ", ".join(parts) + "."
        if fallback:
            explanation += (
                " Fallback to classical execution because the quantum backend was unavailable."
            )
        return StrategyInterpretation(
            requested_strategy=requested,
            selected_strategy=selected,
            actual_strategy=actual,
            fallback_used=fallback,
            reason=reason,
            explanation=explanation,
        )

    def _algorithm_section(
        self,
        report: SolutionReport | None,
        benchmark: BenchmarkResult | None,
        metrics: Any,
        algorithm: str,
        backend: str,
    ) -> AlgorithmInterpretation:
        options = None
        benchmark_def = benchmark.benchmark if benchmark is not None else None
        if benchmark_def is not None:
            options = getattr(benchmark_def, "options", None)

        optimizer = ""
        if metrics is not None and metrics.optimizer:
            optimizer = metrics.optimizer
        elif options is not None and isinstance(options.qaoa_optimizer, str):
            optimizer = options.qaoa_optimizer

        microquantum_version = metrics.microquantum_version if metrics is not None else ""
        if not microquantum_version and report is not None and report.provenance is not None:
            microquantum_version = str(report.provenance.metadata.get("microquantum_version", ""))

        num_qubits = metrics.num_qubits if metrics is not None else None
        circuit_depth = metrics.circuit_depth if metrics is not None else None
        num_gates = metrics.num_gates if metrics is not None else None
        shots = metrics.shots if metrics is not None else None

        detail = ", ".join(
            part
            for part in [
                f"algorithm={algorithm}" if algorithm else "",
                f"backend={backend}" if backend else "",
                f"optimizer={optimizer}" if optimizer else "",
                f"qubits={num_qubits}" if num_qubits is not None else "",
                f"depth={circuit_depth}" if circuit_depth is not None else "",
                f"gates={num_gates}" if num_gates is not None else "",
                f"shots={shots}" if shots is not None else "",
            ]
            if part
        )
        explanation = f"Runtime details: {detail}." if detail else "No runtime details recorded."

        return AlgorithmInterpretation(
            algorithm=algorithm,
            backend=backend,
            optimizer=optimizer,
            num_qubits=num_qubits,
            circuit_depth=circuit_depth,
            num_gates=num_gates,
            shots=shots,
            microquantum_version=microquantum_version,
            explanation=explanation,
        )

    def _execution_section(
        self,
        benchmark: BenchmarkResult | None,
        metrics: Any,
        report_comparison: Any,
        comparison: Any,
        executor: str,
        fallback: bool,
    ) -> ExecutionInterpretation:
        if benchmark is not None:
            status = benchmark.status or ""
            error = benchmark.error or ""
        else:
            status = "degraded" if fallback else "executed"
            error = ""

        failure_category: str | None = None
        if status == "failed":
            lowered = error.lower()
            if "unavailable" in lowered or "install" in lowered:
                failure_category = "backend_unavailable"
            elif "timeout" in lowered or "timed out" in lowered:
                failure_category = "timeout"
            else:
                failure_category = "execution_error"

        selected_leg: str | None = None
        if benchmark is not None:
            if benchmark.metrics is not None:
                selected_leg = str(benchmark.metrics.metadata.get("leg") or "") or None
            if selected_leg is None and benchmark.report is not None:
                selected_leg = benchmark.report.selected_leg
        if selected_leg is None and report_comparison is not None:
            first = report_comparison.entries[0] if report_comparison.entries else None
            selected_leg = str(first.leg) if first is not None else None

        classical_status: str | None = None
        quantum_status: str | None = None
        if report_comparison is not None and report_comparison.entries:
            for entry in report_comparison.entries:
                if entry.leg == "classical":
                    classical_status = entry.status
                elif entry.leg == "quantum":
                    quantum_status = entry.status
        elif comparison is not None:
            classical_status = comparison.baseline_status or None
            if str(comparison.strategy or "").lower() in {"quantum", "hybrid"}:
                quantum_status = comparison.strategy_status or None

        explanation = f"Executed with {executor}{'; status: ' + status if status else ''}."

        return ExecutionInterpretation(
            executor=executor,
            status=status,
            error=error,
            failure_category=failure_category,
            wall_clock_time=metrics.wall_clock_time if metrics is not None else None,
            num_evaluations=metrics.num_evaluations if metrics is not None else None,
            iterations=metrics.iterations if metrics is not None else None,
            executions=metrics.executions if metrics is not None else 0,
            retries=metrics.retries if metrics is not None else 0,
            selected_leg=selected_leg,
            classical_status=classical_status,
            quantum_status=quantum_status,
            explanation=explanation,
        )

    def _provenance_section(
        self,
        report: SolutionReport | None,
        benchmark: BenchmarkResult | None,
        problem: Any,
        provenance: Any,
        actual: str | None,
        algorithm: str,
        executor: str,
        backend: str,
        metrics: Any,
    ) -> ProvenanceOverview:
        benchmark_def = benchmark.benchmark if benchmark is not None else None

        problem_name = ""
        if problem is not None:
            problem_name = getattr(problem, "name", "") or ""
        if not problem_name and benchmark_def is not None:
            problem_name = getattr(benchmark_def.problem, "name", "") or ""

        formulation = ""
        if provenance is not None and provenance.formulation:
            formulation = provenance.formulation
        if not formulation and benchmark_def is not None:
            formulation = benchmark_def.formulation

        strategy = actual or (provenance.strategy_label if provenance is not None else None)

        sdk_version = provenance.sdk_version if provenance is not None else ""
        created_at = ""
        if report is not None:
            created_at = report.created_at
        if not created_at and provenance is not None:
            created_at = provenance.created_at

        return ProvenanceOverview(
            problem_name=problem_name,
            formulation=formulation,
            strategy=strategy,
            algorithm=algorithm,
            executor=executor,
            backend=backend,
            microquantum_version=metrics.microquantum_version if metrics is not None else "",
            sdk_version=sdk_version,
            benchmark_id=benchmark.benchmark_id if benchmark is not None else None,
            baseline="classical" if benchmark is not None else "",
            created_at=created_at,
        )

    @staticmethod
    def _status(benchmark: BenchmarkResult | None, fallback: bool) -> InterpretationStatus:
        if benchmark is not None:
            raw = (benchmark.status or "").strip().lower()
            if raw == "failed":
                return InterpretationStatus.FAILED
            if raw == "executed":
                return InterpretationStatus.DEGRADED if fallback else InterpretationStatus.EXECUTED
            return InterpretationStatus.UNKNOWN
        return InterpretationStatus.DEGRADED if fallback else InterpretationStatus.EXECUTED

    @staticmethod
    def _limitations(
        benchmark: BenchmarkResult | None,
        feasibility: FeasibilityInterpretation,
        objective: ObjectiveInterpretation,
        status: InterpretationStatus,
        fallback: bool,
        quantum_used: bool,
        benchmark_section: BenchmarkInterpretation | None,
    ) -> list[Limitation]:
        limitations: list[Limitation] = []

        if feasibility.status is FeasibilityStatus.UNKNOWN:
            limitations.append(
                Limitation(
                    "feasibility_unknown",
                    "Constraint satisfaction could not be determined from the available data.",
                )
            )

        if objective.known_optimum is None and objective.quality in {
            SolutionQuality.FEASIBLE,
            SolutionQuality.UNKNOWN,
        }:
            limitations.append(
                Limitation(
                    "known_optimum_unavailable",
                    "No known optimum was supplied; optimality relative to an "
                    "optimum cannot be established.",
                )
            )

        if fallback:
            limitations.append(
                Limitation(
                    "classical_fallback",
                    "The requested quantum-capable strategy degraded to a "
                    "classical execution because the quantum backend was "
                    "unavailable.",
                )
            )

        if status is InterpretationStatus.FAILED:
            limitations.append(
                Limitation(
                    "failed_execution",
                    "The execution failed; no solution facts beyond the failure are interpreted.",
                )
            )
        elif quantum_used:
            limitations.append(
                Limitation(
                    "heuristic_solution",
                    "Quantum optimization is heuristic: completion alone does "
                    "not establish optimality.",
                )
            )

        if benchmark is not None and benchmark_section is not None:
            if benchmark_section.winner == "no_comparable_result":
                limitations.append(
                    Limitation(
                        "no_comparable_baseline",
                        "No comparable classical-baseline result existed; the "
                        "benchmark outcome is not ranked.",
                    )
                )
            if (
                benchmark_section.winner not in {None, "no_comparable_result"}
                and benchmark.metrics is not None
                and benchmark.metrics.wall_clock_time is not None
            ):
                limitations.append(
                    Limitation(
                        "timing_environment_dependent",
                        "Timing figures are environment-dependent; no "
                        "performance claim is derived from them.",
                    )
                )

        if objective.energy is not None:
            limitations.append(
                Limitation(
                    "energy_minimization_form",
                    "Energy is reported in the QUBO/Ising minimization form (lower always better).",
                )
            )

        return limitations

    def _build_summary(
        self,
        sense: str,
        feasibility: FeasibilityInterpretation,
        objective: ObjectiveInterpretation,
        status: InterpretationStatus,
        strategy_section: StrategyInterpretation,
        algorithm_section: AlgorithmInterpretation,
        execution_section: ExecutionInterpretation,
        benchmark_section: BenchmarkInterpretation | None,
        fallback: bool,
        requested: str | None,
        actual: str | None,
        quantum_used: bool,
    ) -> str:
        lines: list[str] = []

        if feasibility.status is FeasibilityStatus.FEASIBLE:
            lines.append("The solution is feasible.")
        elif feasibility.status is FeasibilityStatus.INFEASIBLE:
            lines.append(
                f"The solution is infeasible ({feasibility.violated} of "
                f"{max(feasibility.total, 1)} assessed constraints violated)."
            )
        else:
            lines.append("Constraint satisfaction could not be determined.")

        if objective.objective_value is not None:
            lines.append(f"Objective value: {_fmt(objective.objective_value)} ({sense} sense).")
            if objective.known_optimum is not None and objective.optimality_gap is not None:
                if objective.quality is SolutionQuality.OPTIMAL:
                    lines.append(
                        f"The objective equals the known optimum "
                        f"{_fmt(objective.known_optimum)} within tolerance; "
                        "the solution is optimal."
                    )
                elif objective.quality is SolutionQuality.NEAR_OPTIMAL:
                    lines.append(
                        f"The objective is near the known optimum "
                        f"{_fmt(objective.known_optimum)} (optimality gap "
                        f"{_fmt(objective.optimality_gap)}); the solution is "
                        "near-optimal."
                    )
                else:
                    lines.append(
                        f"The objective differs from the known optimum "
                        f"{_fmt(objective.known_optimum)} (optimality gap "
                        f"{_fmt(objective.optimality_gap)})."
                    )
            elif objective.quality in {SolutionQuality.FEASIBLE, SolutionQuality.UNKNOWN}:
                lines.append("No known optimum was supplied; optimality is not assessed.")

        if objective.energy is not None:
            lines.append(f"Energy: {_fmt(objective.energy)} (minimization form).")

        if benchmark_section is not None and benchmark_section.winner is not None:
            strategy_label = actual or benchmark_section.strategy_status or "strategy"
            if benchmark_section.outcome == "better":
                lines.append(
                    f"Benchmark {benchmark_section.benchmark_id}: the "
                    f"{strategy_label} outcome ranked above the "
                    f"{benchmark_section.baseline} baseline (basis: "
                    f"{', '.join(benchmark_section.measured_basis) or 'recorded evidence'}). "
                    "This is a measured run-level result, not a quantum-advantage claim."
                )
            elif benchmark_section.outcome == "worse":
                lines.append(
                    f"Benchmark {benchmark_section.benchmark_id}: the "
                    f"{benchmark_section.baseline} baseline ranked above the "
                    f"{strategy_label} outcome."
                )
            elif benchmark_section.outcome == "tie":
                lines.append(
                    f"Benchmark {benchmark_section.benchmark_id}: the "
                    f"{strategy_label} outcome tied the "
                    f"{benchmark_section.baseline} baseline."
                )
            else:
                lines.append(
                    f"Benchmark {benchmark_section.benchmark_id}: no comparable "
                    f"{benchmark_section.baseline} result was available."
                )

        if fallback and requested and actual and requested != actual:
            lines.append(
                f"Requested strategy {requested} degraded to {actual} because "
                "the quantum backend was unavailable."
            )

        if quantum_used and algorithm_section.algorithm:
            backend = (
                f" on backend {algorithm_section.backend}" if algorithm_section.backend else ""
            )
            lines.append(f"Quantum execution used {algorithm_section.algorithm}{backend}.")

        if status is InterpretationStatus.FAILED:
            message = execution_section.error.strip() if execution_section.error else ""
            lines.append(f"Execution failed{f': {message}' if message else '.'}")

        return "\n".join(lines)

    # -- source derivation --------------------------------------------------

    @staticmethod
    def _requested_strategy(benchmark: BenchmarkResult | None, problem: Any) -> str | None:
        if benchmark is not None:
            raw = getattr(benchmark, "strategy", None)
            return str(raw) if raw else None
        if problem is not None:
            preferred = getattr(problem, "preferred_strategy", None)
            return ResultInterpreter._label(preferred)
        return None

    @staticmethod
    def _selected_strategy(
        benchmark: BenchmarkResult | None, report: SolutionReport | None
    ) -> str | None:
        if benchmark is not None:
            raw = getattr(benchmark, "strategy", None)
            return str(raw) if raw else None
        if report is not None and report.strategy is not None:
            return ResultInterpreter._label(report.strategy)
        return None

    @staticmethod
    def _actual_strategy(
        benchmark: BenchmarkResult | None,
        report: SolutionReport | None,
        selected: str | None,
    ) -> str | None:
        if benchmark is not None:
            executed = getattr(benchmark, "executed_strategy", "") or ""
            if executed:
                return str(executed)
        if selected:
            return selected
        if report is not None and report.strategy is not None:
            return ResultInterpreter._label(report.strategy)
        return None

    @staticmethod
    def _fallback_used(
        selected: str | None,
        actual: str | None,
        provenance: Any,
    ) -> bool:
        if actual and selected and actual != selected:
            return True
        if selected in {"quantum", "hybrid"} and actual == selected:
            executor = provenance.executor if provenance is not None else ""
            if executor and "classical" in str(executor).lower():
                return True
        return False

    @staticmethod
    def _executor(report: SolutionReport | None, benchmark: BenchmarkResult | None) -> str:
        provenance = report.provenance if report is not None else None
        if provenance is not None and provenance.executor:
            return provenance.executor
        metrics = benchmark.metrics if benchmark is not None else None
        if metrics is not None and metrics.metadata:
            return str(metrics.metadata.get("executor", ""))
        return ""

    @staticmethod
    def _algorithm(report: SolutionReport | None, benchmark: BenchmarkResult | None) -> str:
        provenance = report.provenance if report is not None else None
        if provenance is not None and provenance.algorithm:
            return provenance.algorithm
        metrics = benchmark.metrics if benchmark is not None else None
        if metrics is not None and metrics.metadata:
            candidate = metrics.metadata.get("algorithm")
            if candidate:
                return str(candidate)
        benchmark_def = benchmark.benchmark if benchmark is not None else None
        if benchmark_def is not None:
            if benchmark_def.algorithm:
                return benchmark_def.algorithm
            options = getattr(benchmark_def, "options", None)
            if options is not None and options.algorithm:
                return str(options.algorithm)
        return ""

    @staticmethod
    def _backend(report: SolutionReport | None, benchmark: BenchmarkResult | None) -> str:
        provenance = report.provenance if report is not None else None
        if provenance is not None and provenance.backend:
            return provenance.backend
        metrics = benchmark.metrics if benchmark is not None else None
        if metrics is not None and metrics.backend:
            return metrics.backend
        benchmark_def = benchmark.benchmark if benchmark is not None else None
        options = getattr(benchmark_def, "options", None) if benchmark_def is not None else None
        if options is not None and options.backend:
            return str(options.backend)
        return ""

    @staticmethod
    def _is_exact(executor: str, algorithm: str) -> bool:
        text = f"{executor} {algorithm}".lower()
        return "exhaustive" in text or text.strip().startswith("exact")

    @staticmethod
    def _quantum_used(actual: str | None, executor: str, algorithm: str) -> bool:
        if actual in {"quantum", "hybrid"}:
            return True
        text = f"{executor} {algorithm}".lower()
        return any(token in text for token in ("microquantum", "quantum", "qaoa", "vqe"))


__all__ = [
    "AlgorithmInterpretation",
    "BenchmarkInterpretation",
    "ExecutionInterpretation",
    "FeasibilityInterpretation",
    "FeasibilityStatus",
    "InterpretationStatus",
    "Limitation",
    "ObjectiveInterpretation",
    "ProvenanceOverview",
    "Qualification",
    "ResultInterpretation",
    "ResultInterpreter",
    "SolutionQuality",
    "StrategyInterpretation",
]
