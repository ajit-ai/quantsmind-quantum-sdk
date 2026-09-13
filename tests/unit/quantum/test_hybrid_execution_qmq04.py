"""QMQ-04 hybrid workflow & execution tests.

Covers the plan-driven executors (classical / quantum / hybrid), explicit
comparison + deterministic selection, quantum result validation (§9),
execution options, the workflow lifecycle state machine, dependency
handling (§21, MicroQuantum blocked), and the canonical hybrid run (§20)
against real MicroQuantum QAOA.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from quantsmind.quantum import (
    ClassicalExecutionError,
    ClassicalExecutionResult,
    ClassicalExecutor,
    Constraint,
    ExecutionComparison,
    ExecutionComparisonEntry,
    ExecutionOptions,
    ExecutorContext,
    HybridExecutionResult,
    HybridExecutor,
    InvalidQuantumResultError,
    Objective,
    ObjectiveSense,
    QuantumExecutionResult,
    QuantumExecutor,
    QuantumProblem,
    QuantumWorkflow,
    QUBOModel,
    SolutionReport,
    UnsupportedStrategyError,
    Variable,
    WorkflowError,
    WorkflowState,
)
from quantsmind.quantum.integration.microquantum import (
    QaoaExecutionResult,
    qaoa_available,
)
from quantsmind.quantum.mapping.qubo import QUBOMapper
from quantsmind.quantum.strategy.strategy import ComputationStrategy

_SRC = str(Path(__file__).parents[3] / "src")


def _knapsack_problem() -> QuantumProblem:
    problem = QuantumProblem("knapsack_qmq04", domain="optimization")
    problem.add_variable(Variable.binary("x0"))
    problem.add_variable(Variable.binary("x1"))
    problem.add_variable(Variable.binary("x2"))
    problem.add_objective(
        Objective("value", ObjectiveSense.MAXIMIZE, expression="3*x0 + 4*x1 + 5*x2")
    )
    problem.add_constraint(Constraint.le("capacity", expression="2*x0 + 3*x1 + 4*x2", value=5.0))
    problem.preferred_strategy = ComputationStrategy.CLASSICAL
    return problem


def _fast_optimizer():
    mq = pytest.importorskip("microquantum")
    return mq.GradientDescent(learning_rate=0.1, max_iter=3, tol=1e-6)


def _context(
    problem: QuantumProblem,
    *,
    qubo=None,
    ising=None,
    options: ExecutionOptions | None = None,
    strategy: ComputationStrategy | None = None,
) -> ExecutorContext:
    plan = SimpleNamespace(
        strategy=strategy or problem.preferred_strategy or ComputationStrategy.CLASSICAL,
        algorithm="qaoa",
    )
    return ExecutorContext(
        problem=problem,
        plan=plan,
        formulation=None,
        qubo=qubo,
        ising=ising,
        options=options or ExecutionOptions(),
    )


def _decisions(problem: QuantumProblem, assignment: dict[str, int]) -> dict[str, int]:
    return {name: assignment[name] for name in problem.variable_names}


class TestClassicalExecutor:
    def test_runs_exhaustive_baseline(self) -> None:
        problem = _knapsack_problem()
        qubo = QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL).payload
        result = ClassicalExecutor().execute(_context(problem, qubo=qubo))
        assert isinstance(result, ClassicalExecutionResult)
        assert _decisions(problem, result.assignment) == {"x0": 1, "x1": 1, "x2": 0}
        assert result.objective_value == 7.0
        assert result.feasible is True
        assert result.num_evaluations == 64
        assert result.executor == "classical/exhaustive"

    def test_rejects_missing_qubo(self) -> None:
        problem = _knapsack_problem()
        with pytest.raises(ClassicalExecutionError, match="QUBO"):
            ClassicalExecutor().execute(_context(problem))

    def test_wraps_exhaustive_limit(self) -> None:
        problem = QuantumProblem("big", domain="optimization")
        for index in range(21):
            problem.add_variable(Variable.binary(f"v{index}"))
        terms = " + ".join(f"v{index}" for index in range(21))
        problem.add_objective(Objective("sum", ObjectiveSense.MINIMIZE, expression=terms))
        problem.preferred_strategy = ComputationStrategy.CLASSICAL
        qubo = QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL).payload
        with pytest.raises(ClassicalExecutionError, match="exhaustive"):
            ClassicalExecutor().execute(_context(problem, qubo=qubo))

    def test_result_round_trip(self) -> None:
        problem = _knapsack_problem()
        qubo = QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL).payload
        result = ClassicalExecutor().execute(_context(problem, qubo=qubo))
        rebuilt = ClassicalExecutionResult.from_dict(result.to_dict())
        assert rebuilt.assignment == result.assignment
        assert rebuilt.energy == result.energy


class TestExecutionComparison:
    @staticmethod
    def _entry(
        leg: str,
        objective: float | None = None,
        energy: float | None = None,
        feasible: bool | None = None,
        status: str = "executed",
        message: str = "",
    ) -> ExecutionComparisonEntry:
        return ExecutionComparisonEntry(
            leg=leg,
            objective_value=objective,
            energy=energy,
            feasible=feasible,
            status=status,
            message=message,
        )

    def test_minimize_picks_lower_objective(self) -> None:
        comparison = ExecutionComparison.build(
            [
                self._entry("classical", objective=7.0, feasible=True),
                self._entry("quantum", objective=5.0, feasible=True),
            ],
            sense=ObjectiveSense.MINIMIZE,
        )
        assert comparison.winner == "quantum"
        assert "objective" in comparison.selected_reason

    def test_maximize_picks_higher_objective(self) -> None:
        comparison = ExecutionComparison.build(
            [
                self._entry("classical", objective=7.0, feasible=True),
                self._entry("quantum", objective=5.0, feasible=True),
            ],
            sense=ObjectiveSense.MAXIMIZE,
        )
        assert comparison.winner == "classical"

    def test_feasible_beats_infeasible(self) -> None:
        comparison = ExecutionComparison.build(
            [
                self._entry("classical", objective=1.0, feasible=False),
                self._entry("quantum", objective=9.0, feasible=True),
            ],
            sense=ObjectiveSense.MAXIMIZE,
        )
        assert comparison.winner == "quantum"

    def test_tie_prefers_classical(self) -> None:
        comparison = ExecutionComparison.build(
            [
                self._entry("classical", objective=7.0, feasible=True),
                self._entry("quantum", objective=7.0, feasible=True),
            ],
            sense=ObjectiveSense.MAXIMIZE,
        )
        assert comparison.winner == "classical"
        assert comparison.tie_break != ""

    def test_energy_fallback(self) -> None:
        comparison = ExecutionComparison.build(
            [
                self._entry("classical", energy=-5.0, feasible=True),
                self._entry("quantum", energy=-7.0, feasible=True),
            ],
            sense=ObjectiveSense.MINIMIZE,
        )
        assert comparison.winner == "quantum"

    def test_skipped_legs_are_not_ranked(self) -> None:
        comparison = ExecutionComparison.build(
            [
                self._entry("classical", status="skipped", message="unavailable"),
                self._entry("quantum", objective=3.0, feasible=True),
            ],
            sense=ObjectiveSense.MINIMIZE,
        )
        assert comparison.winner == "quantum"

    def test_no_executed_leg(self) -> None:
        comparison = ExecutionComparison.build(
            [
                self._entry("classical", status="failed", message="x"),
                self._entry("quantum", status="skipped", message="y"),
            ],
            sense=ObjectiveSense.MINIMIZE,
        )
        assert comparison.winner is None
        assert "no executable leg" in comparison.selected_reason

    def test_deterministic(self) -> None:
        entries = [
            self._entry("classical", objective=7.0, feasible=True),
            self._entry("quantum", objective=5.0, feasible=True),
        ]
        first = ExecutionComparison.build(entries, sense=ObjectiveSense.MAXIMIZE)
        second = ExecutionComparison.build(entries, sense=ObjectiveSense.MAXIMIZE)
        assert first.to_dict() == second.to_dict()

    def test_round_trip(self) -> None:
        comparison = ExecutionComparison.build(
            [
                self._entry("classical", objective=7.0, feasible=True),
                self._entry("quantum", objective=5.0, feasible=True),
            ],
            sense=ObjectiveSense.MAXIMIZE,
        )
        assert ExecutionComparison.from_dict(comparison.to_dict()).winner == comparison.winner


class TestQuantumValidation:
    @staticmethod
    def _problem() -> QuantumProblem:
        problem = QuantumProblem("val", domain="optimization")
        problem.add_variable(Variable.binary("a"))
        problem.add_variable(Variable.binary("b"))
        problem.add_objective(Objective("cost", ObjectiveSense.MINIMIZE, expression="3*a + 4*b"))
        return problem

    @staticmethod
    def _context() -> ExecutorContext:
        qubo = QUBOModel(variables=["a", "b"], linear={"a": 3.0, "b": 4.0})
        return _context(TestQuantumValidation._problem(), qubo=qubo)

    def test_valid_assignment(self) -> None:
        result = QuantumExecutor().validate(
            QaoaExecutionResult(assignment={"a": 1, "b": 0}, energy=3.0),
            self._context(),
        )
        assert isinstance(result, QuantumExecutionResult)
        assert result.feasible is True
        assert result.objective_value == 3.0
        assert result.executor == "microquantum/qaoa"

    def test_unknown_variable_rejected(self) -> None:
        executor = QuantumExecutor()
        with pytest.raises(InvalidQuantumResultError, match="not present"):
            executor.validate(
                QaoaExecutionResult(assignment={"a": 1, "b": 0, "zz": 1}),
                self._context(),
            )

    def test_non_binary_value_rejected(self) -> None:
        executor = QuantumExecutor()
        with pytest.raises(InvalidQuantumResultError, match="non-binary"):
            executor.validate(
                QaoaExecutionResult(assignment={"a": 2, "b": 0}),
                self._context(),
            )

    def test_energy_mismatch_rejected(self) -> None:
        executor = QuantumExecutor()
        with pytest.raises(InvalidQuantumResultError, match="energy"):
            executor.validate(
                QaoaExecutionResult(assignment={"a": 1, "b": 1}, energy=999.0),
                self._context(),
            )

    def test_infeasible_but_valid_is_recorded(self) -> None:
        problem = self._problem()
        problem.add_constraint(Constraint.le("cap", expression="a + b", value=1))
        qubo = QUBOModel(variables=["a", "b"], linear={"a": 3.0, "b": 4.0})
        result = QuantumExecutor().validate(
            QaoaExecutionResult(assignment={"a": 1, "b": 1}, energy=7.0),
            _context(problem, qubo=qubo),
        )
        assert result.feasible is False
        assert result.energy == 7.0


class TestExecutionOptions:
    def test_round_trip(self) -> None:
        options = ExecutionOptions(
            strategy="hybrid",
            algorithm="qaoa",
            shots=33,
            seed=7,
            num_layers=2,
            optimization_level=2,
            metadata={"k": 1},
        )
        rebuilt = ExecutionOptions.from_dict(options.to_dict())
        assert rebuilt.resolved_strategy is ComputationStrategy.HYBRID
        assert rebuilt.shots == 33
        assert rebuilt.seed == 7
        assert rebuilt.num_layers == 2
        assert rebuilt.optimization_level == 2
        assert rebuilt.algorithm == "qaoa"
        assert rebuilt.metadata["k"] == 1

    def test_workflow_defaults(self) -> None:
        workflow = QuantumWorkflow(_knapsack_problem(), shots=11, num_layers=3)
        options = workflow.execution_options()
        assert options.shots == 11
        assert options.num_layers == 3

    def test_options_override_workflow_args(self) -> None:
        workflow = QuantumWorkflow(
            _knapsack_problem(),
            shots=11,
            options=ExecutionOptions(seed=7, shots=33),
        )
        options = workflow.execution_options()
        assert options.seed == 7
        assert options.shots == 33

    def test_strategy_resolved_after_plan(self) -> None:
        workflow = QuantumWorkflow(_knapsack_problem())
        workflow.plan()
        assert workflow.execution_options().resolved_strategy is ComputationStrategy.CLASSICAL


class TestWorkflowStateMachine:
    def test_run_completes(self) -> None:
        workflow = QuantumWorkflow(_knapsack_problem())
        report = workflow.run()
        assert isinstance(report, SolutionReport)
        assert workflow.state is WorkflowState.COMPLETED

    def test_reuse_rejected(self) -> None:
        workflow = QuantumWorkflow(_knapsack_problem())
        workflow.run()
        with pytest.raises(WorkflowError, match="already"):
            workflow.run()

    def test_backward_transition_rejected(self) -> None:
        workflow = QuantumWorkflow(_knapsack_problem())
        workflow.map()
        with pytest.raises(WorkflowError, match="backward"):
            workflow.select_strategy()

    def test_map_failure_marks_failed(self, monkeypatch) -> None:
        import quantsmind.quantum.workflow.workflow as workflow_module

        monkeypatch.setattr(workflow_module, "microquantum_available", lambda: False)
        problem = _knapsack_problem()
        problem.preferred_strategy = ComputationStrategy.QUANTUM
        workflow = QuantumWorkflow(problem)
        with pytest.raises(WorkflowError, match="microquantum"):
            workflow.run()
        assert workflow.state is WorkflowState.FAILED


class TestCreateExecutor:
    def test_classical(self) -> None:
        workflow = QuantumWorkflow(_knapsack_problem())
        workflow.select_strategy()
        assert isinstance(workflow.create_executor(), ClassicalExecutor)

    def test_quantum(self) -> None:
        problem = _knapsack_problem()
        problem.preferred_strategy = ComputationStrategy.QUANTUM
        workflow = QuantumWorkflow(problem)
        workflow.select_strategy()
        assert isinstance(workflow.create_executor(), QuantumExecutor)

    def test_hybrid(self) -> None:
        problem = _knapsack_problem()
        problem.preferred_strategy = ComputationStrategy.HYBRID
        workflow = QuantumWorkflow(problem)
        workflow.select_strategy()
        executor = workflow.create_executor()
        assert isinstance(executor, HybridExecutor)
        assert isinstance(executor.classical_executor, ClassicalExecutor)

    def test_unsupported(self) -> None:
        problem = _knapsack_problem()
        problem.preferred_strategy = ComputationStrategy.QUANTUM_INSPIRED
        workflow = QuantumWorkflow(problem)
        workflow.select_strategy()
        with pytest.raises(UnsupportedStrategyError, match="cannot create an executor"):
            workflow.create_executor()

    def test_override(self) -> None:
        override = QuantumExecutor()
        workflow = QuantumWorkflow(_knapsack_problem(), executor=override)
        assert workflow.create_executor() is override


class TestHybridExecution:
    @pytest.mark.skipif(not qaoa_available(), reason="microquantum missing")
    def test_canonical_hybrid_maxcut(self) -> None:
        problem = QuantumProblem("maxcut_triangle", domain="optimization")
        for variable in ("a", "b", "c"):
            problem.add_variable(Variable.binary(variable))
        problem.add_objective(
            Objective(
                "cut",
                ObjectiveSense.MAXIMIZE,
                expression=("1*(a+b-2*a*b) + 1*(b+c-2*b*c) + 1*(a+c-2*a*c)"),
            )
        )
        problem.preferred_strategy = ComputationStrategy.HYBRID
        options = dict(num_layers=1, shots=64, seed=7)
        workflow = QuantumWorkflow(
            problem, name="hybrid_maxcut", qaoa_optimizer=_fast_optimizer(), **options
        )
        report = workflow.run()
        assert report.strategy is ComputationStrategy.HYBRID
        execution = report.execution
        assert isinstance(execution, HybridExecutionResult)
        assert report.classical_execution is not None
        assert report.quantum_execution is not None
        assert report.comparison is not None
        assert report.selected_leg in ("classical", "quantum")
        assert report.selected_leg == execution.selected
        assert execution.comparison.winner == report.selected_leg
        assert execution.classical.num_evaluations > 0
        assert set(execution.quantum.assignment) == {"a", "b", "c"}
        assert report.provenance.executor == "hybrid"
        assert report.solution.feasible is True
        assert report.solution.objective_values["cut"] == 2.0
        payload = report.to_dict()
        for key in (
            "classical_execution",
            "quantum_execution",
            "comparison",
            "selected_leg",
        ):
            assert key in payload and payload[key] is not None

    @pytest.mark.skipif(not qaoa_available(), reason="microquantum missing")
    def test_hybrid_deterministic_with_seed(self) -> None:
        def run() -> SolutionReport:
            problem = QuantumProblem("det", domain="optimization")
            problem.add_variable(Variable.binary("a"))
            problem.add_variable(Variable.binary("b"))
            problem.add_objective(
                Objective("value", ObjectiveSense.MAXIMIZE, expression="3*a + 4*b")
            )
            problem.preferred_strategy = ComputationStrategy.HYBRID
            return QuantumWorkflow(
                problem, shots=64, seed=5, qaoa_optimizer=_fast_optimizer()
            ).run()

        first = run()
        second = run()
        assert first.selected_leg == second.selected_leg
        assert first.solution.assignments == second.solution.assignments

    @pytest.mark.skipif(not qaoa_available(), reason="microquantum missing")
    def test_hybrid_knapsack_with_constraint(self) -> None:
        problem = _knapsack_problem()
        problem.preferred_strategy = ComputationStrategy.HYBRID
        workflow = QuantumWorkflow(problem, shots=64, seed=3, qaoa_optimizer=_fast_optimizer())
        report = workflow.run()
        execution = report.execution
        assert isinstance(execution, HybridExecutionResult)
        assert execution.classical is not None
        assert execution.quantum is not None
        assert report.selected_leg == "classical"
        assert _decisions(problem, report.solution.assignments) == {"x0": 1, "x1": 1, "x2": 0}
        assert report.solution.feasible is True
        assert report.provenance.executor == "hybrid"
        assert _decisions(problem, execution.selected_assignment) == {"x0": 1, "x1": 1, "x2": 0}

    def test_hybrid_skips_quantum_when_unavailable(self, monkeypatch) -> None:
        import quantsmind.quantum.execution.hybrid as hybrid_module

        monkeypatch.setattr(hybrid_module, "qaoa_available", lambda: False)
        problem = _knapsack_problem()
        qubo = QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL).payload
        result = HybridExecutor().execute(
            _context(problem, qubo=qubo, strategy=ComputationStrategy.HYBRID)
        )
        assert isinstance(result, HybridExecutionResult)
        assert result.quantum is None
        assert result.classical is not None
        assert result.selected == "classical"
        assert _decisions(problem, result.assignment) == {"x0": 1, "x1": 1, "x2": 0}
        statuses = {entry.leg: entry.status for entry in result.comparison.entries}
        assert statuses == {"classical": "executed", "quantum": "skipped"}
        assert result.metadata["fallback_used"] is True

    def test_hybrid_round_trip(self, monkeypatch) -> None:
        import quantsmind.quantum.execution.hybrid as hybrid_module

        monkeypatch.setattr(hybrid_module, "qaoa_available", lambda: False)
        problem = _knapsack_problem()
        qubo = QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL).payload
        result = HybridExecutor().execute(
            _context(problem, qubo=qubo, strategy=ComputationStrategy.HYBRID)
        )
        rebuilt = HybridExecutionResult.from_dict(result.to_dict())
        assert rebuilt.selected == result.selected
        assert rebuilt.selected_assignment == result.selected_assignment


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

    def test_quantum_raises_import_error_without_microquantum(self) -> None:
        code = self._block_code(
            """
from types import SimpleNamespace

from quantsmind.quantum import (
    ExecutorContext,
    ExecutionOptions,
    MicroQuantumUnavailableError,
    QuantumProblem,
    Variable,
)
from quantsmind.quantum.execution import QuantumExecutor
from quantsmind.quantum.strategy.strategy import ComputationStrategy

p = QuantumProblem("knapsack", domain="optimization")
p.add_variable(Variable.binary("x0"))
p.add_variable(Variable.binary("x1"))
context = ExecutorContext(
    problem=p,
    plan=SimpleNamespace(strategy=ComputationStrategy.QUANTUM, algorithm="qaoa"),
    formulation=None,
    qubo=None,
    ising=None,
    options=ExecutionOptions(),
)
try:
    QuantumExecutor().prepare(context)
except MicroQuantumUnavailableError as exc:
    assert isinstance(exc, ImportError)
    assert isinstance(exc, ValueError)
    assert "microquantum" in str(exc)
    assert "quantsmind[quantum]" in str(exc)
except ImportError as exc:
    raise SystemExit(f"wrong error: {{type(exc).__name__}}") from exc
except Exception as exc:
    raise SystemExit(f"raised {{type(exc).__name__}}: {{exc}}") from exc
else:
    raise SystemExit("expected MicroQuantumUnavailableError")
"""
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, result.stderr

    def test_hybrid_degrades_to_classical_without_microquantum(self) -> None:
        code = self._block_code(
            """
from types import SimpleNamespace

from quantsmind.quantum import (
    Constraint,
    ExecutorContext,
    ExecutionOptions,
    Objective,
    ObjectiveSense,
    QuantumProblem,
    Variable,
)
from quantsmind.quantum.execution import HybridExecutor
from quantsmind.quantum.mapping.qubo import QUBOMapper
from quantsmind.quantum.strategy.strategy import ComputationStrategy

p = QuantumProblem("knapsack", domain="optimization")
p.add_variable(Variable.binary("x0"))
p.add_variable(Variable.binary("x1"))
p.add_variable(Variable.binary("x2"))
p.add_objective(
    Objective("value", ObjectiveSense.MAXIMIZE, expression="3*x0 + 4*x1 + 5*x2")
)
p.add_constraint(Constraint.le("cap", expression="2*x0 + 3*x1 + 4*x2", value=5.0))
qubo = QUBOMapper().map(p, strategy=ComputationStrategy.CLASSICAL).payload
context = ExecutorContext(
    problem=p,
    plan=SimpleNamespace(strategy=ComputationStrategy.HYBRID, algorithm="qaoa"),
    formulation=None,
    qubo=qubo,
    ising=None,
    options=ExecutionOptions(),
)
result = HybridExecutor().execute(context)
assert result.selected == "classical"
assert result.quantum is None
assert result.classical is not None
assert [(e.leg, e.status) for e in result.comparison.entries] == [
    ("classical", "executed"),
    ("quantum", "skipped"),
]
assert result.quantum_unavailable is True
"""
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, result.stderr

    def test_hybrid_preference_without_microquantum_degrades_cleanly(self) -> None:
        code = self._block_code(
            """
from quantsmind.quantum import (
    Constraint,
    Objective,
    ObjectiveSense,
    QuantumProblem,
    QuantumWorkflow,
    Variable,
)
from quantsmind.quantum.strategy.strategy import ComputationStrategy

p = QuantumProblem("knapsack", domain="optimization")
p.add_variable(Variable.binary("x0"))
p.add_variable(Variable.binary("x1"))
p.add_variable(Variable.binary("x2"))
p.add_objective(
    Objective("value", ObjectiveSense.MAXIMIZE, expression="3*x0 + 4*x1 + 5*x2")
)
p.add_constraint(Constraint.le("cap", expression="2*x0 + 3*x1 + 4*x2", value=5.0))
p.preferred_strategy = ComputationStrategy.HYBRID
report = QuantumWorkflow(p).run()
assert report.strategy == ComputationStrategy.CLASSICAL
assert report.provenance.executor == "classical/exhaustive"
assert report.selected_leg is None
assert report.quantum_execution is None
assert report.comparison is None
assert report.solution.assignments == {"x0": 1, "x1": 1, "x2": 0}
assert report.solution.feasible is True
assert report.solution.metadata.get("quantum_unavailable") is False
assert report.solution.metadata.get("execution_fallback") is False
"""
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, result.stderr

    def test_classical_workflow_without_microquantum(self) -> None:
        code = self._block_code(
            """
from quantsmind.quantum import QuantumProblem, QuantumWorkflow, Variable
from quantsmind.quantum.strategy.strategy import ComputationStrategy
from quantsmind.quantum.core.objective import Objective, ObjectiveSense

p = QuantumProblem("tiny", domain="optimization")
p.add_variable(Variable.binary("a"))
p.add_objective(Objective("v", ObjectiveSense.MINIMIZE, expression="2*a"))
p.preferred_strategy = ComputationStrategy.CLASSICAL
report = QuantumWorkflow(p).run()
assert report.classical_execution is not None
assert report.selected_leg is None
assert report.provenance.executor == "classical/exhaustive"
"""
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, result.stderr
