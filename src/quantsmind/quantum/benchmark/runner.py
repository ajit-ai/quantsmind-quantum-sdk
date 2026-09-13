"""Benchmark runner: executes a :class:`Benchmark` against its classical baseline.

The runner is deliberately thin and honest (QMQ-05 §19/§20):

* The benchmark strategy runs through the existing
  :class:`~quantsmind.quantum.workflow.workflow.QuantumWorkflow` pipeline
  (formulate -> classify -> recommend -> plan -> map -> execute).
* The classical baseline is a **separate** CLASSICAL-preference workflow run
  over the same problem, reusing the QMQ-02/04 exhaustive solver (no second
  classical solver, no duplicated execution engine).
* Strategy forcing never touches ``ExecutionOptions.strategy`` (that only
  feeds context/provenance, not dispatch): the problem is cloned with
  ``preferred_strategy`` set, which the QMQ-03 reasoned selector honours.
* A quantum leg that cannot run degrades honestly (recorded) or records a
  ``failed`` run with the typed error — a completion alone never becomes a
  "quantum advantage" claim (QMQ-05 §13).
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from statistics import mean, pstdev
from time import monotonic
from typing import Any

from quantsmind.quantum.benchmark.metrics import is_better
from quantsmind.quantum.benchmark.models import (
    BaselineConfig,
    Benchmark,
    BenchmarkComparison,
    BenchmarkMetrics,
    BenchmarkResult,
    BenchmarkRunSummary,
    metrics_rank_key,
)
from quantsmind.quantum.core.objective import ObjectiveSense
from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.execution.hybrid import HybridExecutionResult
from quantsmind.quantum.execution.options import ExecutionOptions
from quantsmind.quantum.optimization.classical import ExhaustiveSolver
from quantsmind.quantum.result.result import SolutionReport
from quantsmind.quantum.strategy.strategy import ComputationStrategy
from quantsmind.quantum.workflow.workflow import QuantumWorkflow

_EXECUTED = "executed"
_FAILED = "failed"


def _clone_with_strategy(
    problem: QuantumProblem, strategy: ComputationStrategy, *, name: str | None = None
) -> QuantumProblem:
    """Clone the problem forcing a preferred strategy (QMQ-05 §20).

    The clone carries no formulation and records the forced preference; the
    reasoned selector turns that preference into the actual execution plan.
    """
    return QuantumProblem.from_dict(
        {
            **problem.to_dict(),
            "name": name or f"{problem.name}::{strategy.name.lower()}",
            "formulation": None,
            "preferred_strategy": strategy.name.lower(),
        }
    )


def _sense_of(problem: QuantumProblem) -> ObjectiveSense:
    if problem.objectives:
        return problem.objectives[0].sense
    return ObjectiveSense.MINIMIZE


def _num_qubits(report: SolutionReport | None) -> int | None:
    """Mapped qubit count from the mapping metadata (ising vars, then QUBO vars)."""
    if report is None or report.mapping is None:
        return None
    metadata = report.mapping.metadata or {}
    variables = metadata.get("variables")
    if isinstance(variables, list) and variables:
        return len(variables)
    decision = metadata.get("decision_variables")
    slack = metadata.get("slack_variables")
    if isinstance(decision, list) or isinstance(slack, list):
        return len(decision or []) + len(slack or [])
    return None


def _microquantum_version(report: SolutionReport) -> str:
    if report.provenance is None:
        return ""
    return str(report.provenance.metadata.get("microquantum_version", "") or "")


def _optimizer_label(options: ExecutionOptions | None) -> str:
    if options is not None and options.qaoa_optimizer is not None:
        return type(options.qaoa_optimizer).__name__
    return ""


def _selected_execution(report: SolutionReport) -> Any:
    """Execution object the metrics should be derived from.

    Hybrid reports use the selected leg (QMQ-04 selection) — the benchmark
    compares the *outcome that was actually chosen*, never a fabricated blend.
    """
    execution = report.execution
    if isinstance(execution, HybridExecutionResult):
        if report.selected_leg == "quantum":
            return report.quantum_execution
        return report.classical_execution
    return execution


def _build_metrics(
    problem: QuantumProblem,
    report: SolutionReport,
    *,
    sense: ObjectiveSense,
    reference_optimum: float | None,
    wall_clock_time: float | None,
    options: ExecutionOptions | None,
    seed: int | None,
    status: str,
) -> BenchmarkMetrics:
    execution = _selected_execution(report)
    backend = options.backend if options is not None and options.backend else ""
    backend = getattr(execution, "backend", "") or backend
    seed = seed if seed is not None else getattr(execution, "seed", None)
    return BenchmarkMetrics.from_execution(
        problem,
        execution,
        sense=sense,
        reference_optimum=reference_optimum,
        wall_clock_time=wall_clock_time,
        options=options,
        seed=int(seed) if seed is not None else None,
        backend=str(backend),
        optimizer=_optimizer_label(options),
        microquantum_version=_microquantum_version(report),
        num_qubits=_num_qubits(report),
        status=status,
    )


class BenchmarkRunner:
    """Runs benchmarks and produces serializable :class:`BenchmarkResult` reports.

    A runner holds no per-run state; it can be reused across benchmarks and
    suites.  ``runs > 1`` repeats a benchmark and aggregates the repetitions
    into a :class:`BenchmarkRunSummary` (QMQ-05 §14).
    """

    def __init__(
        self,
        *,
        default_seed: int | None = None,
        default_shots: int = 1024,
    ) -> None:
        self.default_seed = default_seed
        self.default_shots = default_shots

    def run(
        self,
        benchmark: Benchmark,
        *,
        runs: int = 1,
        raise_on_error: bool = False,
    ) -> BenchmarkResult:
        """Run a benchmark once or several times.

        Args:
            benchmark: The benchmark definition to execute.
            runs: Number of repetitions (``1`` returns a single-run result).
            raise_on_error: If True, a failing strategy run raises instead of
                being recorded as a ``failed`` run (used in tests/CI).
        """
        if not isinstance(benchmark, Benchmark):
            raise TypeError("BenchmarkRunner.run requires a Benchmark")
        if runs < 1:
            raise ValueError("runs must be >= 1")

        if runs == 1:
            return self._run_once(benchmark, raise_on_error=raise_on_error)

        repetitions = [
            self._run_once(benchmark, raise_on_error=raise_on_error) for _ in range(runs)
        ]
        best = self._pick_best(repetitions, benchmark)
        best.repetitions = [
            BenchmarkResult.from_dict(repetition.to_dict()) for repetition in repetitions
        ]
        best.summary = self._summarize(repetitions, benchmark)
        return best

    # -- internals ---------------------------------------------------------

    def _run_once(
        self,
        benchmark: Benchmark,
        *,
        run_index: int = 0,
        raise_on_error: bool = False,
    ) -> BenchmarkResult:
        problem = benchmark.problem
        sense = _sense_of(problem)
        started = datetime.now(UTC).isoformat()

        resolved = benchmark.resolved_strategy
        if resolved is None:
            return self._failed_result(
                benchmark,
                started,
                "no strategy to benchmark: benchmark.strategy and "
                "problem.preferred_strategy are both unset",
                raise_on_error=raise_on_error,
            )
        resolved_label = resolved.name.lower()

        baseline_config = benchmark.baseline or BaselineConfig()
        solver = baseline_config.solver or ExhaustiveSolver(
            max_variables=baseline_config.max_variables
        )
        options = self._options(benchmark, resolved)
        seed = options.seed

        # Timing: strategy phase and baseline phase are measured separately.
        baseline_wall = 0.0
        baseline_metrics: BenchmarkMetrics | None = None

        if baseline_config.enabled:
            baseline_start = monotonic()
            try:
                baseline_report = self._run_strategy(
                    benchmark,
                    ComputationStrategy.CLASSICAL,
                    name=f"{problem.name}::baseline",
                    solver=solver,
                    options=replace(options, strategy=None),
                )
                baseline_wall = monotonic() - baseline_start
                baseline_metrics = _build_metrics(
                    problem,
                    baseline_report,
                    sense=sense,
                    reference_optimum=None,
                    wall_clock_time=baseline_wall,
                    options=None,
                    seed=seed,
                    status=_EXECUTED,
                )
            except Exception as exc:  # noqa: BLE001 - baseline failure is recorded
                baseline_wall = monotonic() - baseline_start
                if raise_on_error:
                    raise
                baseline_metrics = BenchmarkMetrics(
                    status=_FAILED,
                    metadata={"error": f"{type(exc).__name__}: {exc}"},
                )

        reference_optimum = benchmark.known_optimum
        if reference_optimum is None and baseline_metrics is not None:
            reference_optimum = baseline_metrics.objective_value

        strategy_wall = 0.0
        strategy_status = _EXECUTED
        strategy_error = ""
        report: SolutionReport | None = None
        strategy_start = monotonic()
        try:
            report = self._run_strategy(
                benchmark,
                resolved,
                name=f"{problem.name}::{resolved_label}",
                solver=solver,
                options=options,
            )
            strategy_wall = monotonic() - strategy_start
        except Exception as exc:  # noqa: BLE001 - strategy failure is recorded
            strategy_wall = monotonic() - strategy_start
            strategy_error = f"{type(exc).__name__}: {exc}"
            if raise_on_error:
                raise

        if strategy_error:
            strategy_status = _FAILED

        strategy_metrics = None
        if report is not None:
            strategy_metrics = _build_metrics(
                problem,
                report,
                sense=sense,
                reference_optimum=reference_optimum,
                wall_clock_time=strategy_wall,
                options=options,
                seed=seed,
                status=strategy_status,
            )
            if strategy_error:
                strategy_metrics.metadata["error"] = strategy_error
        elif strategy_error:
            strategy_metrics = BenchmarkMetrics(status=_FAILED, metadata={"error": strategy_error})

        executed_strategy = (
            report.strategy.name.lower()
            if report is not None and report.strategy is not None
            else resolved_label
        )

        comparison_metadata: dict[str, Any] = {}
        if report is not None and isinstance(report.execution, HybridExecutionResult):
            comparison_metadata["hybrid_selected_leg"] = report.selected_leg
            comparison_metadata["hybrid_execution_comparison"] = (
                report.comparison.to_dict() if report.comparison is not None else dict()
            )
            comparison_metadata["quantum_leg"] = (
                "executed" if report.execution.quantum is not None else "skipped"
            )

        baseline_status = (
            "disabled"
            if not baseline_config.enabled
            else (baseline_metrics.status if baseline_metrics is not None else "failed")
        )
        comparison = BenchmarkComparison.build(
            strategy=resolved_label,
            strategy_metrics=strategy_metrics,
            baseline_metrics=baseline_metrics,
            sense=sense,
            strategy_status=strategy_status,
            baseline_status=baseline_status,
            metadata=comparison_metadata,
        )
        if strategy_error:
            comparison.metadata["error"] = strategy_error

        total_time = strategy_wall + baseline_wall
        metadata: dict[str, Any] = {
            "requested_strategy": resolved_label,
            "baseline_enabled": baseline_config.enabled,
            "solver_max_variables": baseline_config.max_variables,
            "run_index": run_index,
        }
        if strategy_error:
            metadata["error"] = strategy_error
        if baseline_metrics is not None and baseline_metrics.status != _EXECUTED:
            metadata["baseline_error"] = str(baseline_metrics.metadata.get("error", "failed"))

        return BenchmarkResult(
            benchmark=benchmark,
            benchmark_id=benchmark.benchmark_id,
            name=benchmark.name,
            strategy=resolved_label,
            status=strategy_status,
            error=strategy_error,
            executed_strategy=executed_strategy,
            metrics=strategy_metrics,
            comparison=comparison,
            report=report,
            started_at=started,
            finished_at=datetime.now(UTC).isoformat(),
            total_time=total_time,
            metadata=metadata,
        )

    def _run_strategy(
        self,
        benchmark: Benchmark,
        strategy: ComputationStrategy,
        *,
        name: str,
        solver: ExhaustiveSolver,
        options: ExecutionOptions | None,
    ) -> SolutionReport:
        """Run a single strategy through a fresh workflow (reproducible runs)."""
        forced_problem = _clone_with_strategy(benchmark.problem, strategy, name=name)
        workflow = QuantumWorkflow(
            problem=forced_problem,
            name=f"benchmark:{benchmark.benchmark_id}",
            shots=self.default_shots,
            seed=options.seed if options is not None else self.default_seed,
            classical_executor=solver,
            requested_algorithm=benchmark.algorithm or None,
            options=options,
        )
        return workflow.run()

    def _options(self, benchmark: Benchmark, strategy: ComputationStrategy) -> ExecutionOptions:
        base = benchmark.options or ExecutionOptions()
        return replace(base, strategy=strategy)

    def _failed_result(
        self,
        benchmark: Benchmark,
        started: str,
        message: str,
        *,
        raise_on_error: bool,
    ) -> BenchmarkResult:
        if raise_on_error:
            raise RuntimeError(message)
        return BenchmarkResult(
            benchmark=benchmark,
            benchmark_id=benchmark.benchmark_id,
            name=benchmark.name,
            strategy="",
            status=_FAILED,
            error=message,
            executed_strategy="",
            metrics=None,
            comparison=BenchmarkComparison.build_none(
                strategy="",
                sense=_sense_of(benchmark.problem).name.lower(),
                strategy_metrics=None,
                strategy_status=_FAILED,
                baseline_status="disabled",
                reason=message,
                metadata={"error": message},
            ),
            report=None,
            started_at=started,
            finished_at=datetime.now(UTC).isoformat(),
            total_time=0.0,
            metadata={"error": message},
        )

    # -- aggregation -------------------------------------------------------

    def _pick_best(
        self, repetitions: list[BenchmarkResult], benchmark: Benchmark
    ) -> BenchmarkResult:
        """Return the best single run (feasibility class, then objective)."""
        sense = _sense_of(benchmark.problem)
        ranked: list[tuple[tuple[int, float, float], BenchmarkResult]] = []
        for repetition in repetitions:
            if repetition.metrics is None:
                continue
            key = metrics_rank_key(repetition.metrics, sense)
            if key is not None:
                ranked.append((key, repetition))
        best = max(ranked, key=lambda item: item[0])[1] if ranked else repetitions[0]
        return self._flatten(best)

    @staticmethod
    def _flatten(result: BenchmarkResult) -> BenchmarkResult:
        """Strip repetitions/summary so a carried single run stays flat."""
        result.repetitions = []
        result.summary = None
        return result

    def _summarize(
        self, repetitions: list[BenchmarkResult], benchmark: Benchmark
    ) -> BenchmarkRunSummary:
        runs = len(repetitions)
        sense = _sense_of(benchmark.problem)
        objective_values: list[float] = []
        times: list[float] = []
        winners: dict[str, int] = {}
        for repetition in repetitions:
            if repetition.metrics is not None and repetition.metrics.objective_value is not None:
                objective_values.append(repetition.metrics.objective_value)
            if repetition.total_time is not None:
                times.append(repetition.total_time)
            if repetition.comparison is not None:
                label = repetition.comparison.winner.value
                winners[label] = winners.get(label, 0) + 1

        summary = BenchmarkRunSummary(runs=runs)
        successes = sum(
            1 for rep in repetitions if rep.status == _EXECUTED and rep.metrics is not None
        )
        feasible = sum(
            1 for rep in repetitions if rep.metrics is not None and rep.metrics.feasible is True
        )
        summary.success_rate = successes / runs
        summary.feasibility_rate = feasible / runs

        if objective_values:
            summary.mean_objective = mean(objective_values)
            summary.min_objective = min(objective_values)
            summary.max_objective = max(objective_values)
            if len(objective_values) > 1:
                summary.objective_stddev = pstdev(objective_values)
            best_objective = objective_values[0]
            for value in objective_values[1:]:
                if is_better(value, best_objective, sense):
                    best_objective = value
            summary.best_objective = best_objective
        if times:
            summary.mean_execution_time = mean(times)
        summary.winners = winners
        return summary


__all__ = ["BenchmarkRunner"]
