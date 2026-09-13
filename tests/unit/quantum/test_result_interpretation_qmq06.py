"""QMQ-06 result interpretation & provenance tests.

Covers the evidence-backed quality classification (optimal/near-optimal/
feasible/infeasible/unknown, §4/§6/§11/§23), the structured sections
(§19), the canonical examples A-F (§24), summary honesty (§18) — including
the "no quantum-advantage claim" and "completion alone is never optimal"
rules — machine-readable fields, serialization/round-trip (§17), the
AdditiveCommand-style integration into :class:`SolutionReport` (§20), and
the MicroQuantum-blocked classical-fallback degradation path (§22).
"""

from __future__ import annotations

import dataclasses
import json
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
    BenchmarkWinner,
    ComputationStrategy,
    Constraint,
    ConstraintStatus,
    ExecutionOptions,
    Objective,
    ObjectiveSense,
    ProblemSolution,
    Provenance,
    QuantumProblem,
    ResultInterpretation,
    ResultInterpreter,
    SolutionQuality,
    SolutionReport,
    Variable,
)
from quantsmind.quantum.integration.microquantum import qaoa_available
from quantsmind.quantum.result.result_interpretation import (
    FeasibilityStatus,
    InterpretationStatus,
    Qualification,
)

_SRC = str(Path(__file__).parents[3] / "src")


def _fast_optimizer():
    mq = pytest.importorskip("microquantum")
    return mq.GradientDescent(learning_rate=0.1, max_iter=3, tol=1e-6)


def _problem(*, maximize: bool = False) -> QuantumProblem:
    problem = QuantumProblem("qmq06_problem", domain="optimization")
    problem.add_variable(Variable.binary("a"))
    problem.add_variable(Variable.binary("b"))
    sense = ObjectiveSense.MAXIMIZE if maximize else ObjectiveSense.MINIMIZE
    problem.add_objective(Objective("z", sense, expression="3*a + 4*b"))
    problem.add_constraint(Constraint.le("cap", expression="a + b", value=1.0))
    problem.preferred_strategy = ComputationStrategy.CLASSICAL
    return problem


def _metrics(
    *,
    objective: float | None,
    feasible: bool | None = True,
    gap: float | None = None,
    ratio: float | None = None,
    energy: float | None = None,
    executor: str = "classical/exhaustive",
    algorithm: str = "exhaustive",
    num_qubits: int | None = 2,
    status: str = "executed",
) -> BenchmarkMetrics:
    return BenchmarkMetrics(
        objective_value=objective,
        energy=energy,
        feasible=feasible,
        constraint_violations=0 if feasible is not False else 1,
        constraint_violation_magnitude=2.0 if feasible is False else 0.0,
        optimality_gap=gap,
        approximation_ratio=ratio,
        num_qubits=num_qubits,
        status=status,
        metadata={"executor": executor, "algorithm": algorithm, "leg": "classical"},
    )


def _benchmark(
    *,
    strategy: str = "classical",
    algorithm: str = "exhaustive",
    known_optimum: float | None = None,
    options: ExecutionOptions | None = None,
    problem: QuantumProblem | None = None,
) -> Benchmark:
    return Benchmark(
        benchmark_id="qmq06_b",
        name="QMQ-06 test benchmark",
        problem=problem or _problem(),
        strategy=strategy,
        algorithm=algorithm,
        options=options,
        baseline=BaselineConfig(),
        known_optimum=known_optimum,
    )


def _comparison(
    *,
    strategy: str = "classical",
    winner: str = "tie",
    delta: float | None = 0.0,
    strategy_status: str = "executed",
    baseline_status: str = "executed",
) -> BenchmarkComparison:
    return BenchmarkComparison(
        strategy=strategy,
        baseline="classical",
        sense="minimize",
        winner=BenchmarkWinner.parse(winner),
        objective_delta=delta,
        strategy_status=strategy_status,
        baseline_status=baseline_status,
        selected_reason="synthetic comparison",
        metadata={},
    )


def _result(
    *,
    benchmark: Benchmark,
    metrics: BenchmarkMetrics | None,
    status: str = "executed",
    executed_strategy: str = "",
    error: str = "",
    comparison: BenchmarkComparison | None = None,
    report: SolutionReport | None = None,
) -> BenchmarkResult:
    return BenchmarkResult(
        benchmark=benchmark,
        benchmark_id=benchmark.benchmark_id,
        name=benchmark.name,
        strategy=benchmark.strategy_label or "",
        status=status,
        error=error,
        executed_strategy=executed_strategy,
        metrics=metrics,
        comparison=comparison,
        report=report,
        metadata={},
    )


class TestEnumsAndParsing:
    def test_quality_parse(self) -> None:
        assert SolutionQuality.parse("OPTIMAL") is SolutionQuality.OPTIMAL
        assert SolutionQuality.parse("near_optimal") is SolutionQuality.NEAR_OPTIMAL
        assert SolutionQuality.parse("nonsense") is SolutionQuality.UNKNOWN
        assert SolutionQuality.parse(SolutionQuality.FEASIBLE) is SolutionQuality.FEASIBLE

    def test_status_and_feasibility_parse(self) -> None:
        assert InterpretationStatus.parse("degraded") is InterpretationStatus.DEGRADED
        assert InterpretationStatus.parse("x") is InterpretationStatus.UNKNOWN
        assert FeasibilityStatus.parse("INFEASIBLE") is FeasibilityStatus.INFEASIBLE
        assert FeasibilityStatus.parse("x") is FeasibilityStatus.UNKNOWN

    def test_qualification_parse(self) -> None:
        assert Qualification.parse("mathematical_proof") is Qualification.MATHEMATICAL_PROOF
        assert Qualification.parse("x") is Qualification.UNCERTAIN


class TestCanonicalExamples:
    def test_a_optimal_classical_exact(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=3.0, gap=0.0, ratio=1.0),
            comparison=_comparison(),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.solution_quality is SolutionQuality.OPTIMAL
        assert interpretation.qualification is Qualification.MATHEMATICAL_PROOF
        assert interpretation.objective.optimality_gap == 0.0
        assert "solution is optimal" in interpretation.summary
        assert not any(
            limitation.category == "known_optimum_unavailable"
            for limitation in interpretation.limitations
        )

    def test_b_near_optimal_gap_within_tolerance(self) -> None:
        benchmark = _benchmark(known_optimum=10.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=9.5, gap=0.05, ratio=0.95),
            comparison=_comparison(),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.solution_quality is SolutionQuality.NEAR_OPTIMAL
        assert interpretation.objective.optimality_gap == pytest.approx(0.05)
        assert "near-optimal" in interpretation.summary

    def test_b2_gap_beyond_near_tolerance_is_feasible(self) -> None:
        benchmark = _benchmark(known_optimum=10.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=7.0, gap=0.3, ratio=0.7),
            comparison=_comparison(),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.solution_quality is SolutionQuality.FEASIBLE
        assert "near-optimal" not in interpretation.summary
        assert "solution is optimal" not in interpretation.summary

    def test_c_no_known_optimum_is_honest_feasible(self) -> None:
        benchmark = _benchmark(known_optimum=None)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=5.0, gap=None, ratio=None),
            comparison=_comparison(),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.solution_quality is SolutionQuality.FEASIBLE
        assert interpretation.objective.known_optimum is None
        assert any(
            limitation.category == "known_optimum_unavailable"
            for limitation in interpretation.limitations
        )
        assert "optimality is not assessed" in interpretation.summary
        assert "solution is optimal" not in interpretation.summary

    def test_d_infeasible_solution(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=2.0, feasible=False),
            comparison=_comparison(),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.solution_quality is SolutionQuality.INFEASIBLE
        assert interpretation.feasibility.status is FeasibilityStatus.INFEASIBLE
        assert interpretation.feasibility.violated == 1
        assert not any(
            limitation.category == "energy_minimization_form"
            for limitation in interpretation.limitations
        )
        assert "infeasible" in interpretation.summary

    def test_e_classical_benchmark_ties_baseline(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=3.0, gap=0.0, ratio=1.0),
            comparison=_comparison(winner="tie", delta=0.0),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.benchmark is not None
        assert interpretation.winner == "tie"
        assert interpretation.benchmark.outcome == "tie"
        assert interpretation.benchmark.measured_basis == ["objective"]
        assert "tied" in interpretation.summary

    def test_f_classical_fallback_degraded(self) -> None:
        benchmark = _benchmark(strategy="hybrid", algorithm="qaoa", known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(
                objective=3.0,
                gap=0.0,
                ratio=1.0,
                executor="classical/exhaustive",
                algorithm="exhaustive",
            ),
            executed_strategy="classical",
            comparison=_comparison(strategy="hybrid"),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.status is InterpretationStatus.DEGRADED
        assert interpretation.fallback_used is True
        assert interpretation.strategy.actual_strategy == "classical"
        assert interpretation.strategy.requested_strategy == "hybrid"
        assert any(
            limitation.category == "classical_fallback" for limitation in interpretation.limitations
        )
        assert "degraded" in interpretation.summary
        assert "not a quantum-advantage claim" not in interpretation.summary


class TestSummaryHonesty:
    def test_completion_alone_never_optimal_without_known_optimum(self) -> None:
        benchmark = _benchmark(strategy="hybrid", algorithm="qaoa", known_optimum=None)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(
                objective=2.5,
                gap=None,
                ratio=None,
                executor="microquantum/qaoa",
                algorithm="qaoa",
            ),
            executed_strategy="hybrid",
            comparison=_comparison(strategy="hybrid"),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.solution_quality is SolutionQuality.FEASIBLE
        assert "solution is optimal" not in interpretation.summary
        assert any(
            limitation.category == "heuristic_solution" for limitation in interpretation.limitations
        )

    def test_quantum_win_never_claims_quantum_advantage(self) -> None:
        benchmark = _benchmark(strategy="hybrid", algorithm="qaoa", known_optimum=None)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(
                objective=5.0,
                gap=None,
                ratio=None,
                executor="microquantum/qaoa",
                algorithm="qaoa",
            ),
            executed_strategy="hybrid",
            comparison=_comparison(strategy="hybrid", winner="hybrid_win", delta=0.4),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.winner == "hybrid_win"
        assert interpretation.benchmark.outcome == "better"
        summary = interpretation.summary
        assert "measured run-level result, not a quantum-advantage claim" in summary
        assert "quantum advantage" not in summary.lower()

    def test_quantum_optimality_is_empirical_not_proof(self) -> None:
        benchmark = _benchmark(strategy="hybrid", algorithm="qaoa", known_optimum=0.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(
                objective=0.0,
                gap=0.0,
                ratio=None,
                executor="microquantum/qaoa",
                algorithm="qaoa",
            ),
            executed_strategy="hybrid",
            comparison=_comparison(strategy="hybrid"),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.solution_quality is SolutionQuality.OPTIMAL
        assert interpretation.qualification is Qualification.EMPIRICAL

    def test_no_comparable_baseline_wording(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=3.0, gap=0.0, ratio=1.0),
            comparison=_comparison(winner="no_comparable_result", delta=None),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.winner == "no_comparable_result"
        assert interpretation.benchmark.outcome == "not_comparable"
        assert any(
            limitation.category == "no_comparable_baseline"
            for limitation in interpretation.limitations
        )
        assert "no comparable" in interpretation.summary


class TestMachineReadableFields:
    def test_structured_fields_present(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=3.0, gap=0.0, ratio=1.0),
            comparison=_comparison(),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        payload = interpretation.to_dict()
        for key in (
            "status",
            "summary",
            "solution_quality",
            "qualification",
            "feasibility",
            "objective",
            "benchmark",
            "strategy",
            "algorithm",
            "execution",
            "limitations",
            "provenance",
        ):
            assert key in payload
        data = interpretation
        assert data.objective is not None
        assert data.feasibility is not None
        assert data.strategy is not None
        assert data.algorithm is not None
        assert data.execution is not None
        assert data.provenance is not None
        assert data.provenance.problem_name == "qmq06_problem"
        assert data.provenance.benchmark_id == "qmq06_b"
        json.dumps(interpretation.to_dict())

    def test_flat_view_properties(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=3.0, gap=0.0, ratio=1.0, executor="classical/exhaustive"),
            comparison=_comparison(),
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.winner == "tie"
        assert interpretation.objective_value == 3.0
        assert interpretation.optimality_gap == 0.0
        assert interpretation.approximation_ratio == 1.0
        assert interpretation.requested_strategy == "classical"
        assert interpretation.selected_strategy == "classical"
        assert interpretation.actual_executor == "classical/exhaustive"
        assert interpretation.fallback_used is False
        assert interpretation.feasibility_status == "feasible"

    def test_deterministic(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=3.0, gap=0.0, ratio=1.0),
            comparison=_comparison(),
        )
        interpreter = ResultInterpreter()
        first = interpreter.interpret_benchmark(result)
        second = interpreter.interpret_benchmark(result)
        assert first.to_dict() == second.to_dict()

    def test_round_trip(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=3.0, gap=0.0, ratio=1.0),
            comparison=_comparison(),
        )
        original = ResultInterpreter().interpret_benchmark(result)
        rebuilt = ResultInterpretation.from_dict(original.to_dict())
        assert rebuilt.to_dict() == original.to_dict()


class TestSolutionReportIntegration:
    def test_report_carries_benchmark_and_interpretation(self) -> None:
        problem = _problem()
        solution = ProblemSolution(
            problem_name=problem.name,
            assignments={"a": 1, "b": 0},
            objective_values={"z": 3.0},
            constraint_status={"cap": ConstraintStatus.SATISFIED},
            feasible=True,
        )
        provenance = Provenance(
            strategy=ComputationStrategy.CLASSICAL,
            formulation="optimization",
            algorithm="exhaustive",
            executor="classical/exhaustive",
        )
        report = SolutionReport(
            problem=problem,
            solution=solution,
            provenance=provenance,
            strategy=ComputationStrategy.CLASSICAL,
        )
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=3.0, gap=0.0, ratio=1.0),
            comparison=_comparison(),
            report=report,
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        report.benchmark = result
        report.result_interpretation = interpretation

        payload = report.to_dict()
        assert payload["benchmark"] is not None
        assert payload["benchmark"]["benchmark_id"] == "qmq06_b"
        assert payload["result_interpretation"] is not None
        assert payload["result_interpretation"]["solution_quality"] == "optimal"
        assert payload["selected_leg"] is None

    def test_interpret_report_without_benchmark(self) -> None:
        problem = _problem()
        solution = ProblemSolution(
            problem_name=problem.name,
            assignments={"a": 1, "b": 0},
            objective_values={"z": 3.0},
            constraint_status={
                "cap": ConstraintStatus.SATISFIED,
                "extra": ConstraintStatus.UNKNOWN,
            },
            feasible=True,
        )
        provenance = Provenance(
            strategy=ComputationStrategy.CLASSICAL,
            formulation="optimization",
            algorithm="exhaustive",
            executor="classical/exhaustive",
        )
        report = SolutionReport(
            problem=problem,
            solution=solution,
            provenance=provenance,
            strategy=ComputationStrategy.CLASSICAL,
        )
        interpretation = ResultInterpreter().interpret_report(report)
        assert interpretation.benchmark is None
        assert interpretation.solution_quality is SolutionQuality.FEASIBLE
        assert interpretation.feasibility.status is FeasibilityStatus.FEASIBLE
        assert interpretation.status is InterpretationStatus.EXECUTED
        assert interpretation.objective.objective_value == 3.0
        assert any(
            limitation.category == "known_optimum_unavailable"
            for limitation in interpretation.limitations
        )


class TestFailureAndTolerance:
    def test_failed_benchmark(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = BenchmarkResult(
            benchmark=benchmark,
            benchmark_id=benchmark.benchmark_id,
            name=benchmark.name,
            strategy="quantum",
            status="failed",
            error="MicroQuantumUnavailableError: microquantum is not installed",
            executed_strategy="",
            metrics=None,
            comparison=BenchmarkComparison.build_none(
                strategy="quantum",
                sense="minimize",
                strategy_metrics=None,
                strategy_status="failed",
                baseline_status="disabled",
                reason="quantum unavailable",
                metadata={},
            ),
            report=None,
            metadata={"error": "quantum unavailable"},
        )
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.status is InterpretationStatus.FAILED
        assert interpretation.solution_quality is SolutionQuality.UNKNOWN
        assert interpretation.feasibility.status is FeasibilityStatus.UNKNOWN
        assert interpretation.execution.failure_category == "backend_unavailable"
        assert any(
            limitation.category == "failed_execution" for limitation in interpretation.limitations
        )
        assert "Execution failed" in interpretation.summary

    def test_custom_gap_tolerance(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=3.00000001, gap=3.3e-9, ratio=1.0),
            comparison=_comparison(),
        )
        strict = ResultInterpreter().interpret_benchmark(result)
        relaxed = ResultInterpreter(gap_tolerance=1e-8).interpret_benchmark(result)
        assert strict.solution_quality is SolutionQuality.NEAR_OPTIMAL
        assert relaxed.solution_quality is SolutionQuality.OPTIMAL
        assert "near-optimal" in strict.summary
        assert "solution is optimal" in relaxed.summary


class TestBenchmarkRunnerIntegration:
    def test_canonical_classical_is_optimal(self) -> None:
        from quantsmind.quantum import default_suite

        result = BenchmarkRunner().run(default_suite().get("b1_knapsack"))
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.status is InterpretationStatus.EXECUTED
        assert interpretation.solution_quality is SolutionQuality.OPTIMAL
        assert interpretation.qualification is Qualification.MATHEMATICAL_PROOF
        assert interpretation.objective.optimality_gap == 0.0
        assert interpretation.winner == "tie"
        assert interpretation.actual_executor == "classical/exhaustive"

    @pytest.mark.skipif(not qaoa_available(), reason="microquantum missing")
    def test_canonical_hybrid_empirical_optimal(self) -> None:
        from quantsmind.quantum import default_suite

        benchmark = default_suite().get("b3_qubo_min")
        benchmark = dataclasses.replace(
            benchmark,
            options=dataclasses.replace(benchmark.options, qaoa_optimizer=_fast_optimizer()),
        )
        result = BenchmarkRunner().run(benchmark)
        interpretation = ResultInterpreter().interpret_benchmark(result)
        assert interpretation.status is InterpretationStatus.EXECUTED
        assert interpretation.solution_quality is SolutionQuality.OPTIMAL
        assert interpretation.qualification is Qualification.EMPIRICAL
        assert interpretation.winner == "tie"
        assert "not a quantum-advantage claim" not in interpretation.summary


class TestMicroQuantumBlocked:
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

    def test_hybrid_interpretation_without_microquantum_degrades(self) -> None:
        code = self._block_code(
            """
from quantsmind.quantum import (
    Benchmark,
    BenchmarkRunner,
    Objective,
    ObjectiveSense,
    QuantumProblem,
    ResultInterpreter,
    Variable,
)

p = QuantumProblem("blocked-hybrid-06", domain="optimization")
p.add_variable(Variable.binary("a"))
p.add_variable(Variable.binary("b"))
p.add_objective(Objective("v", ObjectiveSense.MAXIMIZE, expression="3*a + 4*b"))
benchmark = Benchmark(
    benchmark_id="hb06", name="hybrid-blocked-06", problem=p,
    strategy="hybrid", known_optimum=7.0,
)
result = BenchmarkRunner().run(benchmark)
assert result.status == "executed"
assert result.executed_strategy == "classical"
interpretation = ResultInterpreter().interpret_benchmark(result)
assert interpretation.status.value == "degraded"
assert interpretation.fallback_used is True
assert interpretation.strategy.actual_strategy == "classical"
assert interpretation.solution_quality.value == "optimal"
assert any(limitation.category == "classical_fallback" for limitation in interpretation.limitations)
assert "degraded" in interpretation.summary
assert "quantum advantage" not in interpretation.summary.lower()
"""
        )
        run = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=120
        )
        assert run.returncode == 0, run.stderr


class TestSummarizeConvenience:
    def test_summarize_returns_narrative(self) -> None:
        benchmark = _benchmark(known_optimum=3.0)
        result = _result(
            benchmark=benchmark,
            metrics=_metrics(objective=3.0, gap=0.0, ratio=1.0),
            comparison=_comparison(),
        )
        text = ResultInterpreter().summarize(benchmark=result)
        assert isinstance(text, str)
        assert "solution is optimal" in text
