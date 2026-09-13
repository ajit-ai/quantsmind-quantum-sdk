"""Solutions and results of the QMQ-10 AI/ML Intelligence layer.

Domain result classes translate a QMQ
:class:`~quantsmind.quantum.result.result.SolutionReport` into readable ML
decisions: fitted coefficients and predictions (classification/regression),
the selected candidate, the selected hyperparameter configuration, or the
delegated feature-selection selection set.  They reuse the existing QMQ-05
constraint evaluation and QMQ-06 interpretation infrastructure.  For
delegated families (feature selection / clustering) the solution is either
the QMQ-09 :class:`DataSolution` or the ML wrapper
:class:`MLFeatureSelectionSolution`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.benchmark.metrics import constraint_violations
from quantsmind.quantum.ml.mapping import (
    DecodedHyperparameterChoice,
    DecodedMLCoefficient,
    DecodedModelSelection,
    MLMapper,
)
from quantsmind.quantum.ml.metrics import MLMetrics
from quantsmind.quantum.ml.problem import MLProblem, MLProblemType

if TYPE_CHECKING:
    from quantsmind.quantum.benchmark.models import BenchmarkResult
    from quantsmind.quantum.result.result import SolutionReport
    from quantsmind.quantum.result.result_interpretation import ResultInterpretation

__all__ = [
    "MLBaseSolution",
    "ClassificationSolution",
    "RegressionSolution",
    "MLFeatureSelectionSolution",
    "ModelSelectionSolution",
    "HyperparameterSolution",
    "MLOptimizationResult",
    "ml_solution_from_report",
]


@dataclass
class MLBaseSolution:
    """Common domain fields of every ML solution.

    Decision fields are derived from the deterministic ML mapping, so they
    always reflect the feature/candidate/hyperparameter order of the problem.
    Constraint compliance comes from the existing QMQ-05 metric helpers,
    never recomputed ad hoc.
    """

    problem_name: str = ""
    problem_type: str = ""
    objective_value: float | None = None
    objective_values: dict[str, float] = field(default_factory=dict)
    constraint_status: dict[str, str] = field(default_factory=dict)
    feasible: bool = False
    metrics: Any = field(default_factory=MLMetrics)
    energy: float | None = None
    solver: str = ""
    strategy: str = ""
    algorithm: str = ""
    backend: str = ""
    seed: int | None = None
    shots: int = 1024
    num_variables: int = 0
    num_constraints: int = 0
    execution_time: float | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.problem_name:
            raise ValueError("ML solution requires a problem_name")
        if self.problem_type:
            self.problem_type = MLProblemType.parse(self.problem_type).value

    def _common_to_dict(self) -> dict[str, Any]:
        return {
            "problem_name": self.problem_name,
            "problem_type": self.problem_type,
            "objective_value": self.objective_value,
            "objective_values": dict(self.objective_values),
            "constraint_status": dict(self.constraint_status),
            "feasible": bool(self.feasible),
            "metrics": self.metrics.to_dict() if self.metrics is not None else {},
            "energy": self.energy,
            "solver": self.solver,
            "strategy": self.strategy,
            "algorithm": self.algorithm,
            "backend": self.backend,
            "seed": self.seed,
            "shots": self.shots,
            "num_variables": self.num_variables,
            "num_constraints": self.num_constraints,
            "execution_time": self.execution_time,
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def _common_from_dict(cls, data: dict[str, Any]) -> dict[str, Any]:
        metrics = data.get("metrics", {})
        return {
            "problem_name": str(data.get("problem_name", "")),
            "problem_type": str(data.get("problem_type", "")),
            "objective_value": (
                float(data["objective_value"]) if data.get("objective_value") is not None else None
            ),
            "objective_values": {
                name: float(value) for name, value in data.get("objective_values", {}).items()
            },
            "constraint_status": {
                name: str(status) for name, status in data.get("constraint_status", {}).items()
            },
            "feasible": bool(data.get("feasible", False)),
            "metrics": MLMetrics.from_dict(dict(metrics)) if metrics else MLMetrics(),
            "energy": (float(data["energy"]) if data.get("energy") is not None else None),
            "solver": str(data.get("solver", "")),
            "strategy": str(data.get("strategy", "")),
            "algorithm": str(data.get("algorithm", "")),
            "backend": str(data.get("backend", "")),
            "seed": (int(data["seed"]) if data.get("seed") is not None else None),
            "shots": int(data.get("shots", 1024)),
            "num_variables": int(data.get("num_variables", 0)),
            "num_constraints": int(data.get("num_constraints", 0)),
            "execution_time": (
                float(data["execution_time"]) if data.get("execution_time") is not None else None
            ),
            "provenance": dict(data.get("provenance", {})),
            "metadata": dict(data.get("metadata", {})),
        }


@dataclass
class ClassificationSolution(MLBaseSolution):
    """Solution of a classification (least-squares) problem.

    Attributes:
        coefficients: Feature name -> fitting coefficient (0.0 / 1.0).
        predictions: Fitted response per record in record order.
    """

    coefficients: dict[str, float] = field(default_factory=dict)
    predictions: list[float] = field(default_factory=list)

    @property
    def selected_features(self) -> list[str]:
        """Return the features with an active coefficient in feature order."""
        return [name for name, value in self.coefficients.items() if value >= 0.5]

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._common_to_dict(),
            "coefficients": {name: float(value) for name, value in self.coefficients.items()},
            "predictions": [float(value) for value in self.predictions],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClassificationSolution:
        return cls(
            **_common_from_dict(data),
            coefficients={
                name: float(value) for name, value in data.get("coefficients", {}).items()
            },
            predictions=[float(value) for value in data.get("predictions", [])],
        )


@dataclass
class RegressionSolution(MLBaseSolution):
    """Solution of a regression (least-squares) problem.

    Attributes:
        coefficients: Feature name -> fitting coefficient (0.0 / 1.0).
        predictions: Fitted response per record in record order.
    """

    coefficients: dict[str, float] = field(default_factory=dict)
    predictions: list[float] = field(default_factory=list)

    @property
    def selected_features(self) -> list[str]:
        """Return the features with an active coefficient in feature order."""
        return [name for name, value in self.coefficients.items() if value >= 0.5]

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._common_to_dict(),
            "coefficients": {name: float(value) for name, value in self.coefficients.items()},
            "predictions": [float(value) for value in self.predictions],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegressionSolution:
        return cls(
            **_common_from_dict(data),
            coefficients={
                name: float(value) for name, value in data.get("coefficients", {}).items()
            },
            predictions=[float(value) for value in data.get("predictions", [])],
        )


@dataclass
class MLFeatureSelectionSolution(MLBaseSolution):
    """Wrapper solution of a delegated feature-selection problem (QMQ-09).

    Attributes:
        selected_features: Selected feature names in feature order.
        selected_utility: Total utility of the selected features.
        selection_cost: Total cost of the selected features.
    """

    selected_features: list[str] = field(default_factory=list)
    selected_utility: float = 0.0
    selection_cost: float = 0.0

    @classmethod
    def from_data_solution(
        cls,
        problem: MLProblem,
        solution: Any,
    ) -> MLFeatureSelectionSolution:
        """Build the ML wrapper from a delegated QMQ-09 ``DataSolution``."""
        return cls(
            problem_name=problem.name,
            problem_type=problem.problem_type.value,
            selected_features=list(getattr(solution, "selected_features", [])),
            selected_utility=float(getattr(solution, "selected_utility", 0.0)),
            selection_cost=float(getattr(solution, "selection_cost", 0.0)),
            objective_value=getattr(solution, "objective_value", None),
            objective_values=dict(getattr(solution, "objective_values", {})),
            constraint_status=dict(getattr(solution, "constraint_status", {})),
            feasible=bool(getattr(solution, "feasible", False)),
            metrics=getattr(solution, "metrics", None),
            energy=getattr(solution, "energy", None),
            solver=str(getattr(solution, "solver", "")),
            strategy=str(getattr(solution, "strategy", "")),
            algorithm=str(getattr(solution, "algorithm", "")),
            backend=str(getattr(solution, "backend", "")),
            seed=getattr(solution, "seed", None),
            shots=int(getattr(solution, "shots", 1024)),
            num_variables=int(getattr(solution, "num_variables", 0)),
            num_constraints=int(getattr(solution, "num_constraints", 0)),
            execution_time=getattr(solution, "execution_time", None),
            provenance=dict(getattr(solution, "provenance", {})),
            metadata=dict(getattr(solution, "metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = self._common_to_dict()
        payload["selected_features"] = list(self.selected_features)
        payload["selected_utility"] = float(self.selected_utility)
        payload["selection_cost"] = float(self.selection_cost)
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLFeatureSelectionSolution:
        return cls(
            **_common_from_dict(data),
            selected_features=[str(name) for name in data.get("selected_features", [])],
            selected_utility=float(data.get("selected_utility", 0.0)),
            selection_cost=float(data.get("selection_cost", 0.0)),
        )


@dataclass
class ModelSelectionSolution(MLBaseSolution):
    """Solution of a one-hot model-selection problem.

    Attributes:
        selected_model_id: Identifier of the selected candidate.
    """

    selected_model_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = self._common_to_dict()
        payload["selected_model_id"] = self.selected_model_id
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelSelectionSolution:
        return cls(
            **_common_from_dict(data),
            selected_model_id=str(data.get("selected_model_id", "")),
        )


@dataclass
class HyperparameterSolution(MLBaseSolution):
    """Solution of a one-hot hyperparameter optimization problem.

    Attributes:
        selected_choices: Hyperparameter name -> selected choice value.
    """

    selected_choices: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = self._common_to_dict()
        payload["selected_choices"] = dict(self.selected_choices)
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HyperparameterSolution:
        return cls(
            **_common_from_dict(data),
            selected_choices=dict(data.get("selected_choices", {})),
        )


def _common_from_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Return the base kwargs shared by every ML solution ``from_dict``."""
    return MLBaseSolution._common_from_dict(data)


@dataclass
class MLOptimizationResult:
    """Result of an ML solve or benchmark.

    ``report`` and ``benchmark`` are kept as in-memory composition
    references; serialization carries lightweight references (mirroring
    QMQ-05 :class:`BenchmarkResult`).  The solution is an ML domain solution
    or, for delegated clustering, the QMQ-09 ``DataSolution``.
    """

    solution: Any = None
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
        benchmark = self.benchmark.to_dict() if self.benchmark is not None else None
        interpretation = self.interpretation.to_dict() if self.interpretation is not None else None
        return {
            "solution": self.solution.to_dict() if self.solution is not None else None,
            "report_ref": report_ref,
            "benchmark": benchmark,
            "interpretation": interpretation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLOptimizationResult:
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
            solution=_solution_from_dict(dict(solution)) if solution is not None else None,
            report=None,
            benchmark=(
                BenchmarkResult.from_dict(dict(benchmark)) if benchmark is not None else None
            ),
            interpretation=(
                ResultInterpretation.from_dict(dict(interpretation))
                if interpretation is not None
                else None
            ),
        )


def ml_solution_from_report(
    problem: MLProblem,
    report: SolutionReport,
    *,
    execution_time: float | None = None,
    selected_threshold: float = 0.5,
) -> Any:
    """Build the ML domain solution from a workflow :class:`SolutionReport`.

    Decodes the decision-variable assignment through the deterministic ML
    mapping, computes ML metrics from the dataset and reuses the existing
    constraint-evaluation infrastructure for feasibility, constraint status
    and violation magnitude.  Delegated families are not handled here (the
    optimizer uses the QMQ-09 data solution).
    """
    problem_name = problem.problem_type.name
    if problem_name in ("FEATURE_SELECTION", "CLUSTERING"):
        raise ValueError(f"{problem.problem_type.value} is delegated to the QMQ-09 Data layer")
    assignments = _report_assignments(report)
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
            name: status.name.lower() for name, status in report.solution.constraint_status.items()
        }
    else:
        status_dict = {
            constraint.name: constraint.evaluate(assignments).name.lower()
            for constraint in quantum.constraints
        }
    feasible = report.solution.feasible if report.solution is not None else (violation_count == 0)

    objective_values: dict[str, float] = {}
    if report.solution is not None and report.solution.objective_values:
        objective_values = {
            name: float(value) for name, value in report.solution.objective_values.items()
        }
    objective_value = next(iter(objective_values.values())) if objective_values else None

    mapping = MLMapper().map(problem)
    decoded = mapping.decode_assignments(assignments, selected_threshold=selected_threshold)
    metrics = MLMetrics.compute(
        problem,
        assignments,
        selected_threshold=selected_threshold,
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
    algorithm = str(getattr(execution, "algorithm", "")) or str(solution_meta.get("algorithm", ""))
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
    common = MLBaseSolution(
        problem_name=problem.name,
        problem_type=problem.problem_type.value,
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
        execution_time=(float(execution_time) if execution_time is not None else None),
        provenance=dict(report.provenance.to_dict()) if report.provenance is not None else {},
        metadata=dict(solution_meta),
    )

    if problem_name in ("CLASSIFICATION", "REGRESSION"):
        coefficients: dict[str, float] = {}
        for item in decoded:
            if isinstance(item, DecodedMLCoefficient):
                coefficients[item.feature_name] = item.value
        predictions = _predictions(problem, coefficients, threshold=selected_threshold)
        if problem_name == "CLASSIFICATION":
            return ClassificationSolution(
                **_dict_for_base(common),
                coefficients=coefficients,
                predictions=[float(value) for value in predictions],
            )
        return RegressionSolution(
            **_dict_for_base(common),
            coefficients=coefficients,
            predictions=[float(value) for value in predictions],
        )
    if problem_name == "MODEL_SELECTION":
        model_id = ""
        for item in decoded:
            if isinstance(item, DecodedModelSelection) and item.selected:
                model_id = item.model_id
                break
        return ModelSelectionSolution(**_dict_for_base(common), selected_model_id=model_id)
    selected_choices: dict[str, Any] = {}
    for item in decoded:
        if isinstance(item, DecodedHyperparameterChoice) and item.selected:
            selected_choices[item.parameter_name] = item.choice_value
    return HyperparameterSolution(**_dict_for_base(common), selected_choices=selected_choices)


def _dict_for_base(solution: MLBaseSolution) -> dict[str, Any]:
    """Return the base kwargs of an ML solution as a plain dict."""
    return {
        "problem_name": solution.problem_name,
        "problem_type": solution.problem_type,
        "objective_value": solution.objective_value,
        "objective_values": dict(solution.objective_values),
        "constraint_status": dict(solution.constraint_status),
        "feasible": solution.feasible,
        "metrics": solution.metrics,
        "energy": solution.energy,
        "solver": solution.solver,
        "strategy": solution.strategy,
        "algorithm": solution.algorithm,
        "backend": solution.backend,
        "seed": solution.seed,
        "shots": solution.shots,
        "num_variables": solution.num_variables,
        "num_constraints": solution.num_constraints,
        "execution_time": solution.execution_time,
        "provenance": dict(solution.provenance),
        "metadata": dict(solution.metadata),
    }


def _predictions(
    problem: MLProblem,
    coefficients: dict[str, float],
    *,
    threshold: float,
) -> list[float]:
    """Return fitted responses ``sum_f w_f * x_if`` per record (feature order)."""
    dataset = problem.dataset
    if dataset is None:
        return []
    feature_names = dataset.feature_names
    matrix = dataset.matrix()
    predictions: list[float] = []
    for record in matrix:
        total = 0.0
        for name, active in coefficients.items():
            if active >= threshold and name in feature_names:
                total += float(record[feature_names.index(name)])
        predictions.append(total)
    return predictions


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


def _quantum_for(problem: MLProblem) -> Any:
    """Build the QMQ problem of an ML problem (lazy import avoids cycles)."""
    from quantsmind.quantum.ml.formulation import MLFormulationAdapter

    return MLFormulationAdapter().to_quantum_problem(problem)


def _solution_from_dict(data: dict[str, Any]) -> Any:
    """Rebuild any ML solution from its serialized payload."""
    problem_type = MLProblemType.parse(data.get("problem_type", ""))
    name = problem_type.name if problem_type is not None else ""
    if name == "CLASSIFICATION":
        return ClassificationSolution.from_dict(data)
    if name == "REGRESSION":
        return RegressionSolution.from_dict(data)
    if name == "FEATURE_SELECTION":
        return MLFeatureSelectionSolution.from_dict(data)
    if name == "MODEL_SELECTION":
        return ModelSelectionSolution.from_dict(data)
    if name == "HYPERPARAMETER_OPTIMIZATION":
        return HyperparameterSolution.from_dict(data)
    if name == "CLUSTERING":
        from quantsmind.quantum.data.solution import DataSolution

        return DataSolution.from_dict(data)
    raise ValueError(f"unsupported ML solution problem type {problem_type}")
