"""Finance solve & benchmark pipeline (QMQ-11 §16, Example A).

:class:`FinanceOptimizer` gives FinancialProblem instances the same thin,
workflow-backed pipeline that the Data, ML and Portfolio domains already
have: formulation through the Finance adapter (QMQ-07), QUBO mapping
(QMQ-02), workflow execution (QMQ-04) with the classical exhaustive
baseline, benchmarking (QMQ-05) and interpretation (QMQ-06).  No second
quantum algorithm or solver exists for finance problems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Any

from quantsmind.quantum.execution.options import ExecutionOptions
from quantsmind.quantum.finance.formulation import FinanceFormulationAdapter
from quantsmind.quantum.finance.mapping import DecodedAsset, FinanceAssetMapper
from quantsmind.quantum.finance.portfolio import OptimizationConfiguration
from quantsmind.quantum.result.result import SolutionReport

__all__ = ["FinancialSolution", "FinanceOptimizationResult", "FinanceOptimizer"]


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


@dataclass
class FinancialSolution:
    """Deterministic decoded solution of a FinancialProblem (QMQ-11).

    Args:
        problem_name: Name of the originating financial problem.
        allocation_kind: Allocation representation of the problem.
        assets: Ordered asset decisions.
        objective_value: Leading objective value of the solution.
        objective_values: Objective name -> value snapshot.
        constraint_status: Constraint name -> status label.
        feasible: Whether the solution satisfies all constraints.
        energy: QUBO energy reported by the execution (when available).
        solver: Solver/executor label.
        strategy: Selected computation strategy (lower-case label).
        algorithm: Executed algorithm (e.g. ``"exhaustive"``).
        backend: Backend label.
        seed: Execution seed.
        shots: Shot count.
        num_variables: Number of decision variables after formulation.
        num_constraints: Number of constraints after formulation.
        selection_threshold: Threshold used to mark assets selected.
        execution_time: Wall time of the solve in seconds.
        provenance: JSON-safe provenance metadata of the run.
        metadata: Free-form result metadata.
    """

    problem_name: str
    allocation_kind: str = "binary"
    assets: list[DecodedAsset] = field(default_factory=list)
    objective_value: float | None = None
    objective_values: dict[str, float] = field(default_factory=dict)
    constraint_status: dict[str, str] = field(default_factory=dict)
    feasible: bool = False
    energy: float | None = None
    solver: str = ""
    strategy: str = ""
    algorithm: str = ""
    backend: str = ""
    seed: int | None = None
    shots: int = 0
    num_variables: int = 0
    num_constraints: int = 0
    selection_threshold: float = 0.5
    execution_time: float | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def selected_assets(self) -> list[str]:
        """Selected asset identifiers in universe order."""
        return [asset.asset_id for asset in self.assets if asset.selected]

    @classmethod
    def from_report(
        cls,
        problem: Any,
        report: SolutionReport,
        *,
        execution_time: float | None = None,
        selection_threshold: float = 0.5,
    ) -> FinancialSolution:
        """Build a financial solution from a workflow :class:`SolutionReport`.

        Decodes the decision-variable assignment through the deterministic
        asset mapping (QMQ-07) and reuses the existing constraint-evaluation
        infrastructure for feasibility and constraint status.
        """
        from quantsmind.quantum.benchmark.metrics import constraint_violations

        financial = problem
        assignments = _report_assignments(report)
        decoded = (
            FinanceAssetMapper()
            .map(financial)
            .decode_assignments(assignments, selected_threshold=selection_threshold)
        )
        quantum = FinanceFormulationAdapter().to_quantum_problem(financial)
        if assignments:
            violation_count, _ = constraint_violations(
                quantum, {name: int(value) for name, value in assignments.items()}
            )
        else:
            violation_count = 0

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

        execution = report.execution
        solution_meta = report.solution.metadata if report.solution is not None else {}
        energy = getattr(execution, "energy", None)
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
        execution_seed = getattr(execution, "seed", None)
        execution_shots = getattr(execution, "shots", None)
        shots = (
            int(execution_shots)
            if execution_shots is not None
            else int(solution_meta.get("shots", 0) or 0)
        )
        return cls(
            problem_name=financial.name,
            allocation_kind=financial.allocation_kind.name.lower(),
            assets=decoded,
            objective_value=objective_value,
            objective_values=objective_values,
            constraint_status=status_dict,
            feasible=bool(feasible),
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
            "allocation_kind": self.allocation_kind,
            "assets": [asset.to_dict() for asset in self.assets],
            "objective_value": self.objective_value,
            "objective_values": dict(self.objective_values),
            "constraint_status": dict(self.constraint_status),
            "feasible": bool(self.feasible),
            "energy": self.energy,
            "solver": self.solver,
            "strategy": self.strategy,
            "algorithm": self.algorithm,
            "backend": self.backend,
            "seed": self.seed,
            "shots": self.shots,
            "num_variables": self.num_variables,
            "num_constraints": self.num_constraints,
            "selection_threshold": self.selection_threshold,
            "execution_time": self.execution_time,
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FinancialSolution:
        """Rebuild a solution from :meth:`to_dict` output."""
        return cls(
            problem_name=str(data.get("problem_name", "")),
            allocation_kind=str(data.get("allocation_kind", "binary")),
            assets=[DecodedAsset.from_dict(dict(a)) for a in data.get("assets", [])],
            objective_value=data.get("objective_value"),
            objective_values=dict(data.get("objective_values", {})),
            constraint_status=dict(data.get("constraint_status", {})),
            feasible=bool(data.get("feasible", False)),
            energy=data.get("energy"),
            solver=str(data.get("solver", "")),
            strategy=str(data.get("strategy", "")),
            algorithm=str(data.get("algorithm", "")),
            backend=str(data.get("backend", "")),
            seed=(int(data["seed"]) if data.get("seed") is not None else None),
            shots=int(data.get("shots", 0)),
            num_variables=int(data.get("num_variables", 0)),
            num_constraints=int(data.get("num_constraints", 0)),
            selection_threshold=float(data.get("selection_threshold", 0.5)),
            execution_time=(
                float(data["execution_time"]) if data.get("execution_time") is not None else None
            ),
            provenance=dict(data.get("provenance", {})),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"FinancialSolution({self.problem_name!r}, "
            f"selected={self.selected_assets()}, feasible={self.feasible})"
        )


class FinanceOptimizationResult:
    """Result of a Finance solve or benchmark.

    ``report`` and ``benchmark`` are kept as in-memory composition
    references; serialization carries lightweight references.
    """

    solution: FinancialSolution | None = None
    report: SolutionReport | None = None
    benchmark: Any | None = None
    interpretation: Any | None = None

    def __init__(
        self,
        *,
        solution: FinancialSolution | None = None,
        report: SolutionReport | None = None,
        benchmark: Any | None = None,
        interpretation: Any | None = None,
    ) -> None:
        self.solution = solution
        self.report = report
        self.benchmark = benchmark
        self.interpretation = interpretation

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
    def from_dict(cls, data: dict[str, Any]) -> FinanceOptimizationResult:
        """Rebuild a result from :meth:`to_dict` output."""
        from quantsmind.quantum.benchmark.models import BenchmarkResult
        from quantsmind.quantum.result.result_interpretation import ResultInterpretation

        solution = data.get("solution")
        benchmark = data.get("benchmark")
        interpretation = data.get("interpretation")
        return cls(
            solution=FinancialSolution.from_dict(dict(solution)) if solution is not None else None,
            report=None,
            benchmark=BenchmarkResult.from_dict(dict(benchmark)) if benchmark is not None else None,
            interpretation=(
                ResultInterpretation.from_dict(dict(interpretation))
                if interpretation is not None
                else None
            ),
        )

    def __repr__(self) -> str:
        return (
            f"FinanceOptimizationResult(solution={self.solution!r}, "
            f"benchmark={'yes' if self.benchmark is not None else 'no'})"
        )


class FinanceOptimizer:
    """Solves and benchmarks :class:`~quantsmind.quantum.finance.models
    .FinancialProblem` instances (QMQ-11 §16).

    A thin wrapper over the existing QMQ-03..06 pipeline: formulation
    through the Finance adapter, workflow execution (QMQ-04) with the
    classical exhaustive baseline, and interpretation (QMQ-06).  No second
    quantum algorithm or solver exists for finance problems.
    """

    def __init__(
        self,
        *,
        default_shots: int = 1024,
        default_seed: int | None = None,
    ) -> None:
        self.default_shots = int(default_shots)
        self.default_seed = default_seed

    def _options(
        self,
        problem: Any,
        strategy: str | None,
        seed: int | None,
        config: OptimizationConfiguration | None,
    ) -> ExecutionOptions:
        return ExecutionOptions(
            strategy=strategy,
            algorithm=(config.algorithm or None) if config is not None else None,
            shots=(config.shots if config is not None else self.default_shots),
            seed=seed,
            optimization_level=(config.optimization_level if config is not None else 0),
            metadata={
                "financial_problem": str(getattr(problem, "name", "")),
                "domain_layer": "finance",
            },
        )

    def solve(
        self,
        problem: Any,
        *,
        strategy: str | None = None,
        config: OptimizationConfiguration | None = None,
    ) -> FinanceOptimizationResult:
        """Solve a FinancialProblem through the existing workflow pipeline.

        The chosen strategy (explicit argument, else the configuration's
        preferred strategy, else the QMQ-03 automatic rule) is executed and
        the result is decoded into a :class:`FinancialSolution` with asset
        decisions, a QMQ-06 interpretation, and the underlying
        :class:`SolutionReport`.

        Raises:
            FinanceValidationError: If the problem is invalid.
        """
        problem.raise_if_invalid()
        from quantsmind.quantum.optimization.classical import ExhaustiveSolver
        from quantsmind.quantum.result.result_interpretation import ResultInterpreter
        from quantsmind.quantum.workflow.workflow import QuantumWorkflow

        preferred = strategy
        if preferred is None:
            preferred = (config.preferred_strategy or None) if config is not None else None
        seed = config.seed if config is not None and config.seed is not None else self.default_seed
        options = self._options(problem, preferred, seed, config)
        started = monotonic()
        workflow = QuantumWorkflow(
            problem=FinanceFormulationAdapter().to_quantum_problem(
                problem, preferred_strategy=preferred
            ),
            name=f"finance:{problem.name}",
            shots=options.shots,
            seed=seed,
            classical_executor=ExhaustiveSolver(
                max_variables=(config.solver_max_variables if config is not None else 20)
            ),
            requested_algorithm=(config.algorithm or None) if config is not None else None,
            options=options,
        )
        report = workflow.run()
        execution_time = monotonic() - started
        solution = FinancialSolution.from_report(problem, report, execution_time=execution_time)
        interpretation = ResultInterpreter().interpret_report(report)
        return FinanceOptimizationResult(
            solution=solution,
            report=report,
            benchmark=None,
            interpretation=interpretation,
        )

    def benchmark(
        self,
        problem: Any,
        *,
        strategy: str | None = None,
        known_optimum: float | None = None,
        runs: int = 1,
        raise_on_error: bool = False,
        config: OptimizationConfiguration | None = None,
    ) -> FinanceOptimizationResult:
        """Benchmark a FinancialProblem against the classical baseline (QMQ-05).

        The baseline reuses the existing exhaustive solver.  A failing
        strategy run is recorded as ``failed`` (honest) unless
        ``raise_on_error`` is set.

        Args:
            problem: The financial problem to benchmark.
            strategy: Strategy label to benchmark; defaults to the
                configuration's preferred strategy, else ``"classical"``.
            known_optimum: Optional known objective optimum for gap/ratio.
            runs: Number of repetitions (``1`` = single run).
            raise_on_error: If True, raise instead of recording failures.
            config: Optional execution/optimization configuration.
        """
        problem.raise_if_invalid()
        from quantsmind.quantum.benchmark.models import BaselineConfig, Benchmark
        from quantsmind.quantum.benchmark.runner import BenchmarkRunner
        from quantsmind.quantum.optimization.classical import ExhaustiveSolver
        from quantsmind.quantum.result.result_interpretation import ResultInterpreter

        preferred = strategy
        if preferred is None:
            if config is not None:
                preferred = config.preferred_strategy or "classical"
            else:
                preferred = "classical"
        if not preferred:
            preferred = "classical"
        seed = config.seed if config is not None and config.seed is not None else self.default_seed
        options = self._options(problem, preferred, seed, config)
        benchmark = Benchmark(
            benchmark_id=f"finance:{problem.name}",
            name=problem.name,
            problem=FinanceFormulationAdapter().to_quantum_problem(
                problem, preferred_strategy=preferred
            ),
            strategy=preferred,
            algorithm=(config.algorithm if config is not None else ""),
            options=options,
            formulation="optimization",
            baseline=BaselineConfig(
                kind="classical",
                enabled=True,
                solver=ExhaustiveSolver(
                    max_variables=(config.solver_max_variables if config is not None else 20)
                ),
                max_variables=(config.solver_max_variables if config is not None else 20),
            ),
            known_optimum=known_optimum,
            metadata={"financial_problem": problem.name, "domain_layer": "finance"},
        )
        runner = BenchmarkRunner(default_seed=seed, default_shots=options.shots)
        result = runner.run(benchmark, runs=runs, raise_on_error=raise_on_error)
        solution = None
        if result.report is not None:
            solution = FinancialSolution.from_report(
                problem, result.report, execution_time=result.total_time
            )
        interpreter = ResultInterpreter()
        interpretation = interpreter.interpret(
            report=result.report,
            benchmark=result,
        )
        return FinanceOptimizationResult(
            solution=solution,
            report=result.report,
            benchmark=result,
            interpretation=interpretation,
        )
