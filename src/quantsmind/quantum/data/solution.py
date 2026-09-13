"""Solutions and results of the QMQ-09 Data Intelligence layer.

:class:`DataSolution` is the domain result of a Data solve: selected
features with utility/cost, cluster assignments, metric aggregation and the
execution facts.  It is built from a QMQ
:class:`~quantsmind.quantum.result.result.SolutionReport` via
:meth:`DataSolution.from_report`, reusing the existing QMQ-05 constraint
evaluation and QMQ-06 interpretation infrastructure.  The benchmark is
optional and delegated to QMQ-05; interpretation to QMQ-06.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.benchmark.metrics import constraint_violations
from quantsmind.quantum.data.mapping import DataMapper
from quantsmind.quantum.data.metrics import DataMetrics
from quantsmind.quantum.data.problem import DataProblem, DataProblemType

if TYPE_CHECKING:
    from quantsmind.quantum.benchmark.models import BenchmarkResult
    from quantsmind.quantum.result.result import SolutionReport
    from quantsmind.quantum.result.result_interpretation import ResultInterpretation

__all__ = ["DataSolution", "DataOptimizationResult"]


@dataclass
class DataSolution:
    """The domain result of solving a Data optimization problem.

    Decision fields are derived from the deterministic Data mapping, so they
    always reflect the feature/record order of the underlying dataset.
    Constraint compliance comes from the existing QMQ-05 metric helpers,
    never recomputed ad hoc.

    Args:
        problem_name: Name of the originating data problem.
        problem_type: Data problem family.
        selected_features: Selected feature names in feature order (FS).
        selected_utility: Total utility of the selected features (FS).
        selection_cost: Total cost of the selected features (FS).
        cluster_assignments: Record id -> cluster id (clustering).
        objective_value: Value of the first objective (the primary one).
        objective_values: Objective name -> evaluated value.
        constraint_status: Constraint name -> status label.
        feasible: Whether no constraint was violated.
        metrics: Aggregated data metrics.
        energy: QUBO energy reported by the execution (when available).
        solver: Solver label (e.g. ``"classical/exhaustive"``).
        strategy: Selected computation strategy (lower-case label).
        algorithm: Executed algorithm (e.g. ``"exhaustive"``).
        backend: Backend label.
        seed: Execution seed.
        shots: Shot count.
        num_variables: Number of decision variables.
        num_constraints: Number of constraints after formulation.
        selection_threshold: Threshold used to mark features selected.
        execution_time: Wall time of the solve in seconds.
        provenance: JSON-safe provenance metadata of the run.
        metadata: Free-form result metadata.
    """

    problem_name: str = ""
    problem_type: str = ""
    selected_features: list[str] = field(default_factory=list)
    selected_utility: float = 0.0
    selection_cost: float = 0.0
    cluster_assignments: dict[str, int] = field(default_factory=dict)
    objective_value: float | None = None
    objective_values: dict[str, float] = field(default_factory=dict)
    constraint_status: dict[str, str] = field(default_factory=dict)
    feasible: bool = False
    metrics: DataMetrics = field(default_factory=DataMetrics)
    energy: float | None = None
    solver: str = ""
    strategy: str = ""
    algorithm: str = ""
    backend: str = ""
    seed: int | None = None
    shots: int = 1024
    num_variables: int = 0
    num_constraints: int = 0
    selection_threshold: float = 0.5
    execution_time: float | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.problem_name:
            raise ValueError("data solution requires a problem_name")
        if not self.problem_type:
            self.problem_type = DataProblemType.FEATURE_SELECTION.value
        else:
            self.problem_type = DataProblemType.parse(self.problem_type).value

    def selected(self) -> list[str]:
        """Return the selected features in feature order (alias)."""
        return list(self.selected_features)

    def assigned_clusters(self) -> dict[str, int]:
        """Return the record id -> cluster id assignments (alias)."""
        return dict(self.cluster_assignments)

    @property
    def cluster_count(self) -> int:
        """Number of non-empty clusters used by the solution."""
        if not self.cluster_assignments:
            return 0
        return len(set(self.cluster_assignments.values()))

    @property
    def total_within_cluster_distance(self) -> float | None:
        """Total within-cluster pairwise distance (clustering)."""
        return self.metrics.total_within_cluster_distance

    @classmethod
    def from_report(
        cls,
        problem: DataProblem,
        report: SolutionReport,
        *,
        execution_time: float | None = None,
        selection_threshold: float = 0.5,
    ) -> DataSolution:
        """Build a data solution from a workflow :class:`SolutionReport`.

        Decodes the decision-variable assignment through the deterministic
        Data mapping, computes data metrics from the dataset and reuses the
        existing constraint-evaluation infrastructure for feasibility,
        constraint status and violation magnitude.
        """
        assignments = _report_assignments(report)
        mapping = DataMapper().map(problem)
        decoded = mapping.decode_assignments(assignments, selected_threshold=selection_threshold)

        quantum = _quantum_for(problem)
        violation_count: int
        violation_magnitude: float
        if assignments:
            violation_count, violation_magnitude = constraint_violations(
                quantum, {name: int(value) for name, value in assignments.items()}
            )
        else:
            violation_count, violation_magnitude = 0, 0.0

        status_dict: dict[str, str] = {}
        if report.solution is not None and report.solution.constraint_status:
            status_dict = {
                name: status.name.lower()
                for name, status in report.solution.constraint_status.items()
            }
        else:
            status_dict = {
                constraint.name: constraint.evaluate(assignments).name.lower()
                for constraint in quantum.constraints
            }
        feasible = (
            report.solution.feasible if report.solution is not None else (violation_count == 0)
        )

        objective_values: dict[str, float] = {}
        if report.solution is not None and report.solution.objective_values:
            objective_values = {
                name: float(value) for name, value in report.solution.objective_values.items()
            }
        objective_value = next(iter(objective_values.values())) if objective_values else None

        selected_features: list[str] = []
        cluster_assignments: dict[str, int] = {}
        if problem.problem_type is DataProblemType.FEATURE_SELECTION:
            from quantsmind.quantum.data.mapping import DecodedDataFeature

            selected_features = [
                item.feature_name
                for item in decoded
                if isinstance(item, DecodedDataFeature) and item.selected
            ]
        from quantsmind.quantum.data.mapping import DecodedClusterAssignment

        for item in decoded:
            if isinstance(item, DecodedClusterAssignment) and item.value >= selection_threshold:
                cluster_assignments[item.record_id] = item.cluster_index

        metrics = DataMetrics.compute(
            problem,
            assignments,
            selected_threshold=selection_threshold,
            violation_count=violation_count,
            violation_magnitude=violation_magnitude,
        )

        execution = report.execution
        solution_meta = report.solution.metadata if report.solution is not None else {}
        energy = getattr(execution, "energy", None)
        execution_seed = getattr(execution, "seed", None)
        execution_shots = getattr(execution, "shots", None)
        solver = (
            str(getattr(execution, "solver", ""))
            or str(getattr(execution, "executor", ""))
            or str(solution_meta.get("executor", ""))
        )
        algorithm = str(getattr(execution, "algorithm", "")) or str(
            solution_meta.get("algorithm", "")
        )
        backend = (
            str(getattr(execution, "backend", ""))
            or str(getattr(execution, "backend_name", ""))
            or str(solution_meta.get("backend", ""))
        )
        shots = (
            int(execution_shots)
            if execution_shots is not None
            else int(solution_meta.get("shots", 0) or 0)
        )
        return cls(
            problem_name=problem.name,
            problem_type=problem.problem_type.value,
            selected_features=selected_features,
            selected_utility=float(metrics.selected_utility),
            selection_cost=float(metrics.selection_cost),
            cluster_assignments=cluster_assignments,
            objective_value=objective_value,
            objective_values=objective_values,
            constraint_status=status_dict,
            feasible=bool(feasible),
            metrics=metrics,
            energy=float(energy) if energy is not None else None,
            solver=solver,
            strategy=report.strategy.name.lower() if report.strategy is not None else "",
            algorithm=algorithm,
            backend=backend,
            seed=int(execution_seed) if execution_seed is not None else None,
            shots=shots,
            num_variables=len(quantum.variables),
            num_constraints=len(quantum.constraints),
            selection_threshold=float(selection_threshold),
            execution_time=(float(execution_time) if execution_time is not None else None),
            provenance=dict(report.provenance.to_dict()) if report.provenance is not None else {},
            metadata=dict(solution_meta),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_name": self.problem_name,
            "problem_type": self.problem_type,
            "selected_features": list(self.selected_features),
            "selected_utility": float(self.selected_utility),
            "selection_cost": float(self.selection_cost),
            "cluster_assignments": dict(self.cluster_assignments),
            "objective_value": self.objective_value,
            "objective_values": dict(self.objective_values),
            "constraint_status": dict(self.constraint_status),
            "feasible": bool(self.feasible),
            "metrics": self.metrics.to_dict(),
            "energy": self.energy,
            "solver": self.solver,
            "strategy": self.strategy,
            "algorithm": self.algorithm,
            "backend": self.backend,
            "seed": self.seed,
            "shots": self.shots,
            "num_variables": self.num_variables,
            "num_constraints": self.num_constraints,
            "selection_threshold": float(self.selection_threshold),
            "execution_time": self.execution_time,
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataSolution:
        """Rebuild a solution from :meth:`to_dict` output."""
        return cls(
            problem_name=str(data.get("problem_name", "")),
            problem_type=str(data.get("problem_type", "feature_selection")),
            selected_features=[str(name) for name in data.get("selected_features", [])],
            selected_utility=float(data.get("selected_utility", 0.0)),
            selection_cost=float(data.get("selection_cost", 0.0)),
            cluster_assignments={
                str(record): int(cluster)
                for record, cluster in data.get("cluster_assignments", {}).items()
            },
            objective_value=(
                float(data["objective_value"]) if data.get("objective_value") is not None else None
            ),
            objective_values={
                name: float(value) for name, value in data.get("objective_values", {}).items()
            },
            constraint_status={
                name: str(status) for name, status in data.get("constraint_status", {}).items()
            },
            feasible=bool(data.get("feasible", False)),
            metrics=DataMetrics.from_dict(dict(data.get("metrics", {}))),
            energy=(float(data["energy"]) if data.get("energy") is not None else None),
            solver=str(data.get("solver", "")),
            strategy=str(data.get("strategy", "")),
            algorithm=str(data.get("algorithm", "")),
            backend=str(data.get("backend", "")),
            seed=(int(data["seed"]) if data.get("seed") is not None else None),
            shots=int(data.get("shots", 1024)),
            num_variables=int(data.get("num_variables", 0)),
            num_constraints=int(data.get("num_constraints", 0)),
            selection_threshold=float(data.get("selection_threshold", 0.5)),
            execution_time=(
                float(data["execution_time"]) if data.get("execution_time") is not None else None
            ),
            provenance=dict(data.get("provenance", {})),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class DataOptimizationResult:
    """Result of a Data solve or benchmark.

    ``report`` and ``benchmark`` are kept as in-memory composition
    references; serialization carries lightweight references (mirroring
    QMQ-05 :class:`BenchmarkResult`).
    """

    solution: DataSolution | None = None
    report: SolutionReport | None = None
    benchmark: BenchmarkResult | None = None
    interpretation: ResultInterpretation | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary (reports kept as references)."""
        report_ref = None
        if self.report is not None:
            report_ref = {
                "problem": (self.report.problem.name if self.report.problem is not None else ""),
                "strategy": (
                    self.report.strategy.name.lower() if self.report.strategy is not None else ""
                ),
                "feasible": (
                    self.report.solution.feasible if self.report.solution is not None else None
                ),
                "selected_leg": self.report.selected_leg,
                "created_at": self.report.created_at,
            }
        return {
            "solution": self.solution.to_dict() if self.solution is not None else None,
            "report_ref": report_ref,
            "benchmark": self.benchmark.to_dict() if self.benchmark is not None else None,
            "interpretation": (
                self.interpretation.to_dict() if self.interpretation is not None else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataOptimizationResult:
        """Rebuild a result from :meth:`to_dict` output.

        Composition references (``report``) are intentionally not rebuilt;
        the measured fields round-trip exactly.
        """
        from quantsmind.quantum.benchmark.models import BenchmarkResult
        from quantsmind.quantum.result.result_interpretation import ResultInterpretation

        solution = data.get("solution")
        benchmark = data.get("benchmark")
        interpretation = data.get("interpretation")
        return cls(
            solution=DataSolution.from_dict(dict(solution)) if solution is not None else None,
            report=None,
            benchmark=BenchmarkResult.from_dict(dict(benchmark)) if benchmark is not None else None,
            interpretation=(
                ResultInterpretation.from_dict(dict(interpretation))
                if interpretation is not None
                else None
            ),
        )


def _report_assignments(report: SolutionReport) -> dict[str, Any]:
    """Decision-variable assignments recorded by a workflow report."""
    if report.solution is not None and report.solution.assignments:
        return {
            name: value for name, value in report.solution.assignments.items() if value is not None
        }
    raw = getattr(report.execution, "assignment", None)
    if isinstance(raw, dict):
        return {name: value for name, value in raw.items() if value is not None}
    return {}


def _quantum_for(problem: DataProblem) -> Any:
    """Build the QMQ problem of a data problem (lazy import avoids cycles)."""
    from quantsmind.quantum.data.formulation import DataFormulationAdapter

    return DataFormulationAdapter().to_quantum_problem(problem)
