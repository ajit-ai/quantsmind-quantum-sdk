"""Portfolio results of the QMQ-08 portfolio layer.

:class:`PortfolioComponent` describes one asset decision,
:class:`PortfolioSolution` is the domain result of a portfolio solve and
:class:`PortfolioOptimizationResult` bundles the solution with the optional
QMQ-05 benchmark result and QMQ-06 interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.benchmark.metrics import constraint_violations
from quantsmind.quantum.finance.mapping import FinanceAssetMapper
from quantsmind.quantum.finance.portfolio_metrics import PortfolioMetrics
from quantsmind.quantum.finance.weights import AllocationKind

if TYPE_CHECKING:
    from quantsmind.quantum.benchmark.models import BenchmarkResult
    from quantsmind.quantum.core.problem import QuantumProblem
    from quantsmind.quantum.finance.portfolio import PortfolioOptimizationProblem
    from quantsmind.quantum.result.result import SolutionReport
    from quantsmind.quantum.result.result_interpretation import ResultInterpretation

__all__ = [
    "PortfolioComponent",
    "PortfolioSolution",
    "PortfolioOptimizationResult",
]


@dataclass
class PortfolioComponent:
    """One asset decision inside a :class:`PortfolioSolution`.

    Args:
        asset_id: Asset identifier.
        symbol: Asset symbol.
        index: Deterministic variable index in universe order.
        variable_name: Decision-variable name (``x<i>``).
        weight: Assigned value of the asset in the solution.
        selected: Whether the value exceeds the selection threshold.
        expected_return: Supplied expected return of the asset.
        expected_contribution: ``weight * expected_return``.
        risk_contribution: Marginal variance contribution when a risk matrix
            was supplied (``None`` otherwise).
    """

    asset_id: str
    symbol: str
    index: int
    variable_name: str
    weight: float
    selected: bool
    expected_return: float
    expected_contribution: float
    risk_contribution: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "asset_id": self.asset_id,
            "symbol": self.symbol,
            "index": self.index,
            "variable_name": self.variable_name,
            "weight": float(self.weight),
            "selected": bool(self.selected),
            "expected_return": float(self.expected_return),
            "expected_contribution": float(self.expected_contribution),
            "risk_contribution": self.risk_contribution,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PortfolioComponent:
        """Rebuild a component from :meth:`to_dict` output."""
        return cls(
            asset_id=str(data["asset_id"]),
            symbol=str(data.get("symbol", "")),
            index=int(data.get("index", 0)),
            variable_name=str(data.get("variable_name", "")),
            weight=float(data.get("weight", 0.0)),
            selected=bool(data.get("selected", False)),
            expected_return=float(data.get("expected_return", 0.0)),
            expected_contribution=float(data.get("expected_contribution", 0.0)),
            risk_contribution=(
                float(data["risk_contribution"])
                if data.get("risk_contribution") is not None
                else None
            ),
        )


@dataclass
class PortfolioSolution:
    """The domain result of solving a portfolio optimization problem.

    Components are ordered by the deterministic universe order. ``weights()``
    maps every asset identifier (in that order) to its weight. Constraint
    compliance comes from the existing QMQ constraint-evaluation
    infrastructure (QMQ-05 metric helpers), never recomputed ad hoc.

    Args:
        problem_name: Name of the originating portfolio problem.
        allocation_kind: Allocation representation that was solved.
        components: Ordered per-asset decisions.
        objective_value: Value of the first objective (the primary one).
        objective_values: Objective name -> evaluated value.
        constraint_status: Constraint name -> ``"satisfied"/"violated"/...``.
        feasible: Whether no constraint was violated.
        metrics: Measured portfolio metrics.
        energy: QUBO energy reported by the execution (when available).
        solver: Solver label (e.g. ``"classical/exhaustive"``).
        strategy: Selected computation strategy (lower-case label).
        algorithm: Executed algorithm (e.g. ``"exhaustive"``).
        backend: Backend label.
        seed: Execution seed.
        shots: Shot count.
        num_variables: Number of decision variables.
        num_constraints: Number of constraints after formulation.
        optimization_level: Execution optimization hint.
        selection_threshold: Threshold used to mark components selected.
        execution_time: Wall time of the solve in seconds.
        provenance: JSON-safe provenance metadata of the run.
        metadata: Free-form result metadata.
    """

    problem_name: str = ""
    allocation_kind: AllocationKind = AllocationKind.BINARY
    components: list[PortfolioComponent] = field(default_factory=list)
    objective_value: float | None = None
    objective_values: dict[str, float] = field(default_factory=dict)
    constraint_status: dict[str, str] = field(default_factory=dict)
    feasible: bool = False
    metrics: PortfolioMetrics = field(default_factory=PortfolioMetrics)
    energy: float | None = None
    solver: str = ""
    strategy: str = ""
    algorithm: str = ""
    backend: str = ""
    seed: int | None = None
    shots: int = 1024
    num_variables: int = 0
    num_constraints: int = 0
    optimization_level: int = 0
    selection_threshold: float = 0.5
    execution_time: float | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.allocation_kind = AllocationKind.parse(self.allocation_kind)
        if not self.problem_name:
            raise ValueError("portfolio solution requires a problem_name")

    def weights(self) -> dict[str, float]:
        """Deterministic asset identifier -> weight mapping (universe order)."""
        return {component.asset_id: float(component.weight) for component in self.components}

    def selected_assets(self) -> list[str]:
        """Selected asset identifiers in universe order."""
        return [component.asset_id for component in self.components if component.selected]

    @classmethod
    def from_report(
        cls,
        portfolio: PortfolioOptimizationProblem,
        report: SolutionReport,
        *,
        execution_time: float | None = None,
        selection_threshold: float = 0.5,
    ) -> PortfolioSolution:
        """Build a portfolio solution from a workflow :class:`SolutionReport`.

        Decodes the decision-variable assignment through the deterministic
        asset mapping (QMQ-07), computes portfolio metrics from supplied data
        and reuses the existing constraint-evaluation infrastructure for
        feasibility, constraint status and violation magnitude.
        """
        financial = portfolio.to_financial_problem()
        assignments = _report_assignments(report)
        decoded = (
            FinanceAssetMapper()
            .map(financial)
            .decode_assignments(assignments, selected_threshold=selection_threshold)
        )
        weights = {decoded_asset.asset_id: float(decoded_asset.value) for decoded_asset in decoded}

        quantum = _quantum_for(portfolio)
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

        components: list[PortfolioComponent] = []
        risk_contributions: dict[str, float] = {}
        if financial.risk is not None:
            from quantsmind.quantum.finance.portfolio_metrics import risk_contributions as _rc

            risk_contributions = _rc(financial.risk, weights)
        for decoded_asset in decoded:
            asset = financial.universe.asset(decoded_asset.asset_id)
            components.append(
                PortfolioComponent(
                    asset_id=decoded_asset.asset_id,
                    symbol=decoded_asset.symbol,
                    index=decoded_asset.index,
                    variable_name=decoded_asset.variable_name,
                    weight=float(decoded_asset.value),
                    selected=bool(decoded_asset.selected),
                    expected_return=float(asset.expected_return),
                    expected_contribution=float(asset.expected_return * decoded_asset.value),
                    risk_contribution=risk_contributions.get(decoded_asset.asset_id),
                )
            )

        metrics = PortfolioMetrics.compute(
            financial.universe,
            weights,
            financial.risk,
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
            problem_name=portfolio.name,
            allocation_kind=portfolio.allocation_kind,
            components=components,
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
            "allocation_kind": self.allocation_kind.name.lower(),
            "components": [component.to_dict() for component in self.components],
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
            "optimization_level": self.optimization_level,
            "selection_threshold": float(self.selection_threshold),
            "execution_time": self.execution_time,
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PortfolioSolution:
        """Rebuild a portfolio solution from :meth:`to_dict` output."""
        return cls(
            problem_name=str(data.get("problem_name", "")),
            allocation_kind=AllocationKind.parse(data.get("allocation_kind", "binary")),
            components=[PortfolioComponent.from_dict(d) for d in data.get("components", [])],
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
            metrics=PortfolioMetrics.from_dict(dict(data.get("metrics", {}))),
            energy=(float(data["energy"]) if data.get("energy") is not None else None),
            solver=str(data.get("solver", "")),
            strategy=str(data.get("strategy", "")),
            algorithm=str(data.get("algorithm", "")),
            backend=str(data.get("backend", "")),
            seed=(int(data["seed"]) if data.get("seed") is not None else None),
            shots=int(data.get("shots", 1024)),
            num_variables=int(data.get("num_variables", 0)),
            num_constraints=int(data.get("num_constraints", 0)),
            optimization_level=int(data.get("optimization_level", 0)),
            selection_threshold=float(data.get("selection_threshold", 0.5)),
            execution_time=(
                float(data["execution_time"]) if data.get("execution_time") is not None else None
            ),
            provenance=dict(data.get("provenance", {})),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class PortfolioOptimizationResult:
    """Result of a portfolio solve or benchmark.

    ``report`` and ``benchmark`` are kept as in-memory composition
    references; serialization carries lightweight references (mirroring
    QMQ-05 :class:`BenchmarkResult`).
    """

    solution: PortfolioSolution | None = None
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
    def from_dict(cls, data: dict[str, Any]) -> PortfolioOptimizationResult:
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
            solution=PortfolioSolution.from_dict(dict(solution)) if solution is not None else None,
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


def _quantum_for(portfolio: PortfolioOptimizationProblem) -> QuantumProblem:
    """Build the QMQ problem of a portfolio (lazy import avoids cycles)."""
    from quantsmind.quantum.finance.portfolio import PortfolioFormulationAdapter

    return PortfolioFormulationAdapter().to_quantum_problem(portfolio)
