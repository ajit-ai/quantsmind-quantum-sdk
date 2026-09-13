"""QMQ-05 benchmark & classical-comparison tests.

Covers the pure metric/comparison math (centralized sense/energy rules, §10,
including the permanent energy-direction regression §23), the deterministic
winner policy (§12/§13), model serialization (§16/§18), the runner over the
canonical suite (classical members exact, hybrid members executed vs real
MicroQuantum QAOA), repeated-run aggregation (§14), honest failure handling
and the MicroQuantum-blocked subprocess degradation path (§21).
"""

from __future__ import annotations

import dataclasses
import subprocess
import sys
from pathlib import Path

import pytest

from quantsmind.quantum import (
    BaselineConfig,
    Benchmark,
    BenchmarkComparison,
    BenchmarkMetrics,
    BenchmarkResult,
    BenchmarkRunner,
    BenchmarkRunSummary,
    BenchmarkSuite,
    BenchmarkWinner,
    Constraint,
    Objective,
    ObjectiveSense,
    QuantumProblem,
    Variable,
    approximation_ratio,
    b1_knapsack,
    b5_geq_max,
    constraint_violations,
    default_suite,
    normalized_score,
    objective_sense,
    optimality_gap,
)
from quantsmind.quantum.integration.microquantum import qaoa_available

_SRC = str(Path(__file__).parents[3] / "src")

_CLASSICAL_IDS = ("b1_knapsack", "b2_linear_max", "b5_geq_max")
_CLASSICAL_OPTIMA = {"b1_knapsack": 7.0, "b2_linear_max": 12.0, "b5_geq_max": 8.0}


def _fast_optimizer():
    mq = pytest.importorskip("microquantum")
    return mq.GradientDescent(learning_rate=0.1, max_iter=3, tol=1e-6)


def _hybrid_benchmark(benchmark_id: str) -> Benchmark:
    suite = default_suite()
    benchmark = suite.get(benchmark_id)
    return dataclasses.replace(
        benchmark, options=dataclasses.replace(benchmark.options, qaoa_optimizer=_fast_optimizer())
    )


def _entry_metrics(
    *,
    objective: float | None = None,
    energy: float | None = None,
    feasible: bool | None = True,
    violations: float = 0.0,
    status: str = "executed",
) -> BenchmarkMetrics:
    return BenchmarkMetrics(
        objective_value=objective,
        energy=energy,
        feasible=feasible,
        constraint_violation_magnitude=violations,
        status=status,
    )


class TestBenchmarkModels:
    def test_validation_rejects_empty_ids(self) -> None:
        with pytest.raises(ValueError, match="benchmark_id"):
            Benchmark(benchmark_id="", name="x", problem=b1_knapsack())
        with pytest.raises(ValueError, match="name"):
            Benchmark(benchmark_id="x", name="", problem=b1_knapsack())

    def test_strategy_string_is_coerced(self) -> None:
        benchmark = Benchmark(
            benchmark_id="b", name="b", problem=b1_knapsack(), strategy="classical"
        )
        assert benchmark.strategy is not None
        assert benchmark.strategy.name.lower() == "classical"

    def test_resolved_strategy_falls_back_to_problem_preference(self) -> None:
        problem = b1_knapsack()
        benchmark = Benchmark(benchmark_id="b", name="b", problem=problem, strategy=None)
        assert benchmark.resolved_strategy.name.lower() == "classical"

    def test_round_trip(self) -> None:
        suite = default_suite()
        for benchmark in suite.benchmarks.values():
            rebuilt = Benchmark.from_dict(benchmark.to_dict())
            assert rebuilt.benchmark_id == benchmark.benchmark_id
            assert rebuilt.name == benchmark.name
            assert rebuilt.strategy_label == benchmark.strategy_label
            assert rebuilt.known_optimum == benchmark.known_optimum
            assert rebuilt.problem.name == benchmark.problem.name
            assert [v.name for v in rebuilt.problem.variables] == [
                v.name for v in benchmark.problem.variables
            ]
            if benchmark.options is not None:
                assert rebuilt.options.to_dict() == benchmark.options.to_dict()

    def test_baseline_defaults(self) -> None:
        config = BaselineConfig()
        assert config.kind == "classical"
        assert config.enabled is True
        assert config.max_variables == 20
        assert config.solver is None


class TestBenchmarkMetricsMath:
    def test_objective_sense(self) -> None:
        assert objective_sense(b5_geq_max()) is ObjectiveSense.MAXIMIZE
        problem = QuantumProblem("min", domain="optimization")
        problem.add_objective(Objective("cost", ObjectiveSense.MINIMIZE, expression="a"))
        assert objective_sense(problem) is ObjectiveSense.MINIMIZE

    def test_optimality_gap_exact_and_relative(self) -> None:
        assert optimality_gap(7.0, 7.0) == 0.0
        assert optimality_gap(5.0, 10.0) == 0.5
        assert optimality_gap(12.0, 10.0) == 0.2  # sense-independent

    def test_optimality_gap_zero_optimum_uses_absolute(self) -> None:
        assert optimality_gap(0.0, 0.0) == 0.0
        assert optimality_gap(1.0, 0.0) == 1.0
        assert optimality_gap(-2.0, 0.0) == 2.0

    def test_optimality_gap_missing(self) -> None:
        assert optimality_gap(None, 5.0) is None
        assert optimality_gap(5.0, None) is None

    def test_approximation_ratio_maximize(self) -> None:
        assert approximation_ratio(5.0, 10.0, ObjectiveSense.MAXIMIZE) == 0.5
        assert approximation_ratio(10.0, 10.0, ObjectiveSense.MAXIMIZE) == 1.0

    def test_approximation_ratio_minimize(self) -> None:
        assert approximation_ratio(8.0, 10.0, ObjectiveSense.MINIMIZE) == 1.25

    def test_approximation_ratio_uninterpretable(self) -> None:
        assert approximation_ratio(5.0, 0.0, ObjectiveSense.MAXIMIZE) is None
        assert approximation_ratio(5.0, 10.0, ObjectiveSense.MINIMIZE) == 2.0
        assert approximation_ratio(0.0, 10.0, ObjectiveSense.MAXIMIZE) == 0.0
        assert approximation_ratio(0.0, 10.0, ObjectiveSense.MINIMIZE) is None
        assert approximation_ratio(-1.0, 10.0, ObjectiveSense.MAXIMIZE) is None
        assert approximation_ratio(None, 10.0, ObjectiveSense.MAXIMIZE) is None

    def test_normalized_score_obeys_sense(self) -> None:
        assert normalized_score(ObjectiveSense.MAXIMIZE, 5.0, 0.0) == 5.0
        assert normalized_score(ObjectiveSense.MINIMIZE, 5.0, 0.0) == -5.0

    def test_normalized_score_prefers_objective_over_energy(self) -> None:
        # objective present => energy ignored for ranking
        assert normalized_score(ObjectiveSense.MINIMIZE, 5.0, -999.0) == -5.0

    def test_normalized_score_energy_lower_always_better(self) -> None:
        # QMQ-04 energy-direction regression ($23): QUBO energy is lower-better
        # under every sense.
        assert normalized_score(ObjectiveSense.MAXIMIZE, None, -7.0) == 7.0
        assert normalized_score(ObjectiveSense.MAXIMIZE, None, -5.0) == 5.0
        assert normalized_score(ObjectiveSense.MINIMIZE, None, 0.0) == 0.0
        assert normalized_score(ObjectiveSense.MINIMIZE, None, 1.0) == -1.0
        assert normalized_score(ObjectiveSense.MAXIMIZE, None, None) is None

    def test_constraint_violations_le(self) -> None:
        problem = QuantumProblem("le", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        problem.add_variable(Variable.binary("x1"))
        problem.add_constraint(Constraint.le("cap", expression="2*x0 + 3*x1", value=5.0))
        count, magnitude = constraint_violations(problem, {"x0": 1, "x1": 1})
        assert count == 0
        assert magnitude == 0.0
        count, magnitude = constraint_violations(problem, {"x0": 1, "x1": 1})
        assert count == 0
        # violating assignment: lhs = 5 <= 5 ok; use tighter bound
        problem2 = QuantumProblem("le2", domain="optimization")
        problem2.add_variable(Variable.binary("x0"))
        problem2.add_variable(Variable.binary("x1"))
        problem2.add_constraint(Constraint.le("cap", expression="2*x0 + 3*x1", value=4.0))
        count, magnitude = constraint_violations(problem2, {"x0": 1, "x1": 1})
        assert count == 1
        assert magnitude == pytest.approx(1.0)  # 5 - 4

    def test_constraint_violations_ge_and_eq(self) -> None:
        problem = QuantumProblem("ge", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        problem.add_variable(Variable.binary("x1"))
        problem.add_constraint(Constraint.ge("min", expression="x0 + x1", value=2.0))
        count, magnitude = constraint_violations(problem, {"x0": 0, "x1": 1})
        assert count == 1
        assert magnitude == pytest.approx(1.0)  # 2 - 1

        problem.add_constraint(Constraint.eq("exact", expression="x0 + x1", value=1.0))
        count, magnitude = constraint_violations(problem, {"x0": 1, "x1": 1})
        assert count == 1  # ge satisfied, eq violated
        assert magnitude == pytest.approx(1.0)  # |2 - 1|

    def test_metrics_round_trip(self) -> None:
        metrics = BenchmarkMetrics(
            objective_value=7.0,
            energy=-12.5,
            feasible=True,
            constraint_violations=0,
            optimality_gap=0.0,
            approximation_ratio=1.0,
            wall_clock_time=0.25,
            num_evaluations=64,
            num_variables=3,
            status="executed",
            metadata={"leg": "classical"},
        )
        rebuilt = BenchmarkMetrics.from_dict(metrics.to_dict())
        assert rebuilt.objective_value == metrics.objective_value
        assert rebuilt.optimality_gap == 0.0
        assert rebuilt.metadata["leg"] == "classical"


class TestBenchmarkComparison:
    def _build(
        self,
        *,
        strategy="quantum",
        strategy_metrics: BenchmarkMetrics | None = None,
        baseline_metrics: BenchmarkMetrics | None = None,
        sense: ObjectiveSense = ObjectiveSense.MAXIMIZE,
        strategy_status: str = "executed",
        baseline_status: str = "executed",
    ) -> BenchmarkComparison:
        return BenchmarkComparison.build(
            strategy=strategy,
            strategy_metrics=strategy_metrics,
            baseline_metrics=baseline_metrics,
            sense=sense,
            strategy_status=strategy_status,
            baseline_status=baseline_status,
        )

    def test_better_strategy_wins(self) -> None:
        comparison = self._build(
            strategy_metrics=_entry_metrics(objective=8.0),
            baseline_metrics=_entry_metrics(objective=6.0),
        )
        assert comparison.winner is BenchmarkWinner.QUANTUM_WIN
        assert comparison.objective_delta == pytest.approx(2.0)
        assert comparison.strategy_status == "executed"

    def test_worse_strategy_is_classical_win(self) -> None:
        comparison = self._build(
            strategy_metrics=_entry_metrics(objective=6.0),
            baseline_metrics=_entry_metrics(objective=8.0),
        )
        assert comparison.winner is BenchmarkWinner.CLASSICAL_WIN
        assert comparison.objective_delta == pytest.approx(-2.0)

    def test_minimize_still_lower_objective_wins(self) -> None:
        comparison = self._build(
            strategy_metrics=_entry_metrics(objective=4.0),
            baseline_metrics=_entry_metrics(objective=6.0),
            sense=ObjectiveSense.MINIMIZE,
        )
        assert comparison.winner is BenchmarkWinner.QUANTUM_WIN

    def test_hybrid_strategy_maps_to_hybrid_win(self) -> None:
        comparison = self._build(
            strategy="hybrid",
            strategy_metrics=_entry_metrics(objective=9.0),
            baseline_metrics=_entry_metrics(objective=6.0),
        )
        assert comparison.winner is BenchmarkWinner.HYBRID_WIN

    def test_feasibility_class_dominates_objective(self) -> None:
        comparison = self._build(
            strategy_metrics=_entry_metrics(objective=5.0, feasible=True),
            baseline_metrics=_entry_metrics(objective=9.0, feasible=False),
        )
        assert comparison.winner is BenchmarkWinner.QUANTUM_WIN

    def test_both_infeasible_fewer_violations_wins(self) -> None:
        comparison = self._build(
            strategy_metrics=_entry_metrics(objective=1.0, feasible=False, violations=1.0),
            baseline_metrics=_entry_metrics(objective=9.0, feasible=False, violations=4.0),
        )
        assert comparison.winner is BenchmarkWinner.QUANTUM_WIN

    def test_tie_on_exact_equality(self) -> None:
        comparison = self._build(
            strategy_metrics=_entry_metrics(objective=7.0),
            baseline_metrics=_entry_metrics(objective=7.0),
        )
        assert comparison.winner is BenchmarkWinner.TIE
        assert comparison.tie_break != ""

    def test_energy_direction_regression(self) -> None:
        # lower QUBO energy is better under EVERY sense ($23 regression).
        comparison = self._build(
            strategy_metrics=_entry_metrics(objective=None, energy=-7.0),
            baseline_metrics=_entry_metrics(objective=None, energy=-5.0),
            sense=ObjectiveSense.MAXIMIZE,
        )
        assert comparison.winner is BenchmarkWinner.QUANTUM_WIN

    def test_objective_present_overrides_energy(self) -> None:
        comparison = self._build(
            strategy_metrics=_entry_metrics(objective=4.0, energy=5.0),
            baseline_metrics=_entry_metrics(objective=6.0, energy=-5.0),
            sense=ObjectiveSense.MINIMIZE,
        )
        assert comparison.winner is BenchmarkWinner.QUANTUM_WIN

    def test_missing_baseline_is_no_comparable_result(self) -> None:
        comparison = self._build(
            strategy_metrics=_entry_metrics(objective=7.0), baseline_metrics=None
        )
        assert comparison.winner is BenchmarkWinner.NO_COMPARABLE_RESULT
        assert comparison.baseline_status == "disabled"

    def test_missing_strategy_is_no_comparable_result(self) -> None:
        comparison = self._build(
            strategy_metrics=None,
            baseline_metrics=_entry_metrics(objective=7.0),
        )
        assert comparison.winner is BenchmarkWinner.NO_COMPARABLE_RESULT

    def test_failed_strategy_is_no_comparable_result(self) -> None:
        comparison = self._build(
            strategy_metrics=_entry_metrics(objective=None, status="failed"),
            baseline_metrics=_entry_metrics(objective=7.0),
        )
        assert comparison.winner is BenchmarkWinner.NO_COMPARABLE_RESULT
        assert comparison.strategy_status == "failed"

    def test_disabled_baseline_is_no_comparable_result(self) -> None:
        comparison = self._build(baseline_metrics=None, baseline_status="disabled")
        assert comparison.winner is BenchmarkWinner.NO_COMPARABLE_RESULT

    def test_deterministic_and_round_trip(self) -> None:
        kwargs = dict(
            strategy="quantum",
            strategy_metrics=_entry_metrics(objective=8.0),
            baseline_metrics=_entry_metrics(objective=6.0),
        )
        first = self._build(**kwargs)
        second = self._build(**kwargs)
        assert first.to_dict() == second.to_dict()
        rebuilt = BenchmarkComparison.from_dict(first.to_dict())
        assert rebuilt.winner is first.winner
        assert rebuilt.selected_reason == first.selected_reason


class TestBenchmarkSuite:
    def test_default_suite_shape(self) -> None:
        suite = default_suite()
        assert isinstance(suite, BenchmarkSuite)
        assert suite.ids == [
            "b1_knapsack",
            "b2_linear_max",
            "b3_qubo_min",
            "b4_maxcut_triangle",
            "b5_geq_max",
        ]
        assert len(suite.benchmarks) == 5

    def test_known_optima(self) -> None:
        suite = default_suite()
        assert suite.get("b1_knapsack").known_optimum == 7.0
        assert suite.get("b2_linear_max").known_optimum == 12.0
        assert suite.get("b3_qubo_min").known_optimum == 0.0
        assert suite.get("b4_maxcut_triangle").known_optimum == 2.0
        assert suite.get("b5_geq_max").known_optimum == 8.0

    def test_unique_problem_names(self) -> None:
        names = [benchmark.problem.name for benchmark in default_suite().benchmarks.values()]
        assert len(names) == len(set(names))

    def test_duplicate_registration_rejected(self) -> None:
        suite = default_suite()
        with pytest.raises(ValueError, match="duplicate benchmark id"):
            suite.add(suite.get("b1_knapsack"))

    def test_round_trip(self) -> None:
        suite = default_suite()
        rebuilt = BenchmarkSuite.from_dict(suite.to_dict())
        assert rebuilt.name == suite.name
        assert rebuilt.ids == suite.ids
        assert rebuilt.get("b4_maxcut_triangle").known_optimum == 2.0


class TestBenchmarkRunnerClassical:
    @pytest.mark.parametrize("benchmark_id", list(_CLASSICAL_IDS))
    def test_canonical_classical_exact(self, benchmark_id: str) -> None:
        benchmark = default_suite().get(benchmark_id)
        result = BenchmarkRunner().run(benchmark)
        assert result.status == "executed"
        assert result.executed_strategy == "classical"
        assert result.metrics is not None
        assert result.metrics.objective_value == pytest.approx(_CLASSICAL_OPTIMA[benchmark_id])
        assert result.metrics.feasible is True
        assert result.metrics.optimality_gap == 0.0
        assert result.metrics.approximation_ratio == pytest.approx(1.0)
        assert result.metrics.num_evaluations > 0
        assert result.metrics.num_variables == len(benchmark.problem.variables)
        assert result.metrics.num_constraints == len(benchmark.problem.constraints)
        assert result.comparison is not None
        assert result.comparison.winner is BenchmarkWinner.TIE
        assert result.total_time >= 0.0
        assert result.metrics.wall_clock_time >= 0.0

    def test_result_carries_report_reference(self) -> None:
        result = BenchmarkRunner().run(default_suite().get("b1_knapsack"))
        assert result.report is not None
        payload = result.to_dict()
        assert payload["report_ref"] is not None
        assert payload["report_ref"]["solution_feasible"] is True
        assert payload["report_ref"]["executor"] == "classical/exhaustive"

    def test_result_round_trip(self) -> None:
        result = BenchmarkRunner().run(default_suite().get("b1_knapsack"))
        payload = result.to_dict()
        rebuilt = BenchmarkResult.from_dict(payload)
        assert rebuilt.status == result.status
        assert rebuilt.benchmark_id == result.benchmark_id
        assert rebuilt.metrics.objective_value == result.metrics.objective_value
        assert rebuilt.comparison.winner is result.comparison.winner
        assert rebuilt.report is None
        assert rebuilt.repetitions == []

    def test_disabled_baseline_reports_no_comparable(self) -> None:
        benchmark = dataclasses.replace(
            default_suite().get("b1_knapsack"),
            baseline=BaselineConfig(enabled=False),
        )
        result = BenchmarkRunner().run(benchmark)
        assert result.status == "executed"
        assert result.comparison.winner is BenchmarkWinner.NO_COMPARABLE_RESULT
        assert result.comparison.baseline_status == "disabled"
        assert "no classical baseline" in result.comparison.selected_reason

    def test_missing_strategy_records_failed_without_raise(self) -> None:
        problem = QuantumProblem("no-strategy", domain="optimization")
        problem.add_variable(Variable.binary("a"))
        problem.add_objective(Objective("v", ObjectiveSense.MAXIMIZE, expression="a"))
        benchmark = Benchmark(benchmark_id="ns", name="no strategy", problem=problem, strategy=None)
        result = BenchmarkRunner().run(benchmark)
        assert result.status == "failed"
        assert result.comparison.winner is BenchmarkWinner.NO_COMPARABLE_RESULT
        assert "no strategy" in result.comparison.selected_reason

    def test_missing_strategy_raises_when_requested(self) -> None:
        problem = QuantumProblem("no-strategy-2", domain="optimization")
        problem.add_variable(Variable.binary("a"))
        problem.add_objective(Objective("v", ObjectiveSense.MAXIMIZE, expression="a"))
        benchmark = Benchmark(
            benchmark_id="ns2", name="no strategy", problem=problem, strategy=None
        )
        with pytest.raises(RuntimeError, match="no strategy"):
            BenchmarkRunner().run(benchmark, raise_on_error=True)


@pytest.mark.skipif(not qaoa_available(), reason="microquantum missing")
class TestBenchmarkRunnerHybrid:
    def test_qubo_min_hybrid_executed(self) -> None:
        benchmark = _hybrid_benchmark("b3_qubo_min")
        result = BenchmarkRunner().run(benchmark)
        assert result.status == "executed"
        assert result.executed_strategy == "hybrid"
        assert result.metrics is not None
        assert result.metrics.objective_value == 0.0
        assert result.metrics.optimality_gap == 0.0
        assert result.metrics.feasible is True
        assert result.metrics.metadata["leg"] in ("classical", "quantum")
        assert result.comparison is not None
        assert result.comparison.winner is BenchmarkWinner.TIE
        assert result.comparison.metadata["quantum_leg"] == "executed"
        assert "hybrid_selected_leg" in result.comparison.metadata
        assert result.metrics.num_qubits == 2

    def test_maxcut_triangle_hybrid_executed(self) -> None:
        benchmark = _hybrid_benchmark("b4_maxcut_triangle")
        result = BenchmarkRunner().run(benchmark)
        assert result.status == "executed"
        assert result.metrics.objective_value == 2.0
        assert result.metrics.feasible is True
        assert result.comparison.winner is BenchmarkWinner.TIE

    def test_repeated_runs_aggregate(self) -> None:
        benchmark = _hybrid_benchmark("b3_qubo_min")
        result = BenchmarkRunner().run(benchmark, runs=3)
        assert result.summary is not None
        assert isinstance(result.summary, BenchmarkRunSummary)
        assert result.summary.runs == 3
        assert result.summary.success_rate == 1.0
        assert result.summary.feasibility_rate == 1.0
        assert result.summary.best_objective == 0.0
        assert result.summary.mean_execution_time > 0.0
        assert len(result.repetitions) == 3
        for repetition in result.repetitions:
            assert repetition.repetitions == []
            assert repetition.summary is None
        payload = result.to_dict()
        assert len(payload["repetitions"]) == 3
        assert payload["summary"]["runs"] == 3
        rebuilt = BenchmarkResult.from_dict(payload)
        assert rebuilt.summary.runs == 3
        assert rebuilt.summary.winners == {"tie": 3}


class TestDependencyHandling:
    def _block_code(self, body: str) -> str:
        return f"""
import sys
sys.path.insert(0, {_SRC!r})

class _Block:
    def find_spec(self, name, path=None, target=None):
        if name == "microquantum" or name.startswith("microquantum."):
            raise ImportError("blocked for test")
        return None

sys.meta_path.insert(0, _Block())
{body}
print("OK")
"""

    def test_quantum_benchmark_without_microquantum_degrades_to_classical(self) -> None:
        code = self._block_code(
            """
from quantsmind.quantum import (
    Benchmark,
    BenchmarkRunner,
    BenchmarkWinner,
    Objective,
    ObjectiveSense,
    QuantumProblem,
    Variable,
)

p = QuantumProblem("blocked-quantum", domain="optimization")
p.add_variable(Variable.binary("a"))
p.add_variable(Variable.binary("b"))
p.add_objective(Objective("v", ObjectiveSense.MAXIMIZE, expression="3*a + 4*b"))
benchmark = Benchmark(
    benchmark_id="qb", name="quantum-blocked", problem=p,
    strategy="quantum", known_optimum=7.0,
)
result = BenchmarkRunner().run(benchmark)
assert result.status == "executed"
assert result.executed_strategy == "classical"   # honest degradation, provenance classical
assert result.metrics is not None
assert result.metrics.objective_value == 7.0
assert result.comparison.winner is BenchmarkWinner.TIE  # completed run, no advantage claim
"""
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, result.stderr

    def test_hybrid_benchmark_without_microquantum_degrades_to_classical(self) -> None:
        code = self._block_code(
            """
from quantsmind.quantum import (
    Benchmark,
    BenchmarkRunner,
    BenchmarkWinner,
    Objective,
    ObjectiveSense,
    QuantumProblem,
    Variable,
)

p = QuantumProblem("blocked-hybrid", domain="optimization")
p.add_variable(Variable.binary("a"))
p.add_variable(Variable.binary("b"))
p.add_objective(Objective("v", ObjectiveSense.MAXIMIZE, expression="3*a + 4*b"))
benchmark = Benchmark(
    benchmark_id="hb", name="hybrid-blocked", problem=p,
    strategy="hybrid", known_optimum=7.0,
)
result = BenchmarkRunner().run(benchmark)
assert result.status == "executed"
assert result.executed_strategy == "classical"
assert result.metrics.objective_value == 7.0
assert result.comparison.winner is BenchmarkWinner.TIE
"""
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, result.stderr

    def test_lazy_import_preserved(self) -> None:
        code = self._block_code(
            """
from quantsmind.quantum import default_suite, BenchmarkRunner
suite = default_suite()
assert len(suite.ids) == 5
result = BenchmarkRunner().run(suite.get("b1_knapsack"))
assert result.metrics.objective_value == 7.0
"""
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, result.stderr
