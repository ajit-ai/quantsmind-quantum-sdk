"""End-to-end QMQ-02 workflow tests (classical baseline + QAOA quantum path)."""

from __future__ import annotations

import pytest

from quantsmind.quantum import (
    Constraint,
    Objective,
    ObjectiveSense,
    ProblemSolution,
    QuantumProblem,
    QuantumWorkflow,
    SolutionReport,
    Variable,
    WorkflowError,
)
from quantsmind.quantum.integration.microquantum import qaoa_available
from quantsmind.quantum.strategy.strategy import ComputationStrategy


def _knapsack_problem() -> QuantumProblem:
    problem = QuantumProblem("knapsack", domain="optimization")
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


class TestClassicalWorkflow:
    def _run(self, problem: QuantumProblem) -> SolutionReport:
        workflow = QuantumWorkflow(problem, name="knapsack_classical")
        return workflow.run()

    def test_end_to_end_optimal(self) -> None:
        report = self._run(_knapsack_problem())
        assert isinstance(report, SolutionReport)
        assert report.strategy.name == "CLASSICAL"
        assert report.solution.assignments == {"x0": 1, "x1": 1, "x2": 0}
        assert report.solution.objective_values["value"] == 7.0
        assert report.solution.feasible is True
        assert report.provenance.strategy_label == "classical"
        assert report.provenance.executor == "classical/exhaustive"
        assert report.provenance.algorithm == "exhaustive"
        assert report.provenance.metadata["microquantum_used"] is False

    def test_mapping_pipeline(self) -> None:
        workflow = QuantumWorkflow(_knapsack_problem())
        workflow.formulate()
        workflow.select_strategy()
        workflow.map()
        assert workflow.strategy.name == "CLASSICAL"
        assert workflow.formulation_mapping is not None
        assert workflow.formulation_mapping.target == "QUBOModel"
        assert workflow.mapping.target == "QUBOModel"
        assert workflow.qubo is not None
        assert workflow.ising is None

    def test_explicit_penalty(self) -> None:
        problem = _knapsack_problem()
        workflow = QuantumWorkflow(problem, penalty=12.5)
        workflow.map()
        assert workflow.formulation_mapping.metadata["penalty"] == 12.5

    def test_quantum_inspired_rejected(self) -> None:
        problem = _knapsack_problem()
        problem.preferred_strategy = ComputationStrategy.QUANTUM_INSPIRED
        workflow = QuantumWorkflow(problem)
        with pytest.raises(WorkflowError, match="QUANTUM_INSPIRED"):
            workflow.run()

    def test_quantum_path_requires_microquantum(self, monkeypatch) -> None:
        import quantsmind.quantum.workflow.workflow as workflow_module

        # The selector (real MicroQuantum available) picks QUANTUM; the
        # workflow's own availability check then rejects the run.
        monkeypatch.setattr(workflow_module, "microquantum_available", lambda: False)
        problem = _knapsack_problem()
        problem.preferred_strategy = ComputationStrategy.QUANTUM
        with pytest.raises(WorkflowError, match="microquantum"):
            QuantumWorkflow(problem).run()

    def test_solution_is_problemsolution(self) -> None:
        report = self._run(_knapsack_problem())
        assert isinstance(report.solution, ProblemSolution)


class TestQuantumWorkflowQMQ02:
    @pytest.mark.skipif(not qaoa_available(), reason="microquantum missing")
    def test_end_to_end_qaoa(self) -> None:
        problem = QuantumProblem("qaoa_demo", domain="optimization")
        problem.add_variable(Variable.binary("a"))
        problem.add_variable(Variable.binary("b"))
        problem.add_objective(Objective("value", ObjectiveSense.MAXIMIZE, expression="3*a + 4*b"))
        problem.preferred_strategy = ComputationStrategy.QUANTUM
        workflow = QuantumWorkflow(
            problem,
            name="qaoa_demo",
            num_layers=1,
            shots=64,
            seed=5,
            qaoa_optimizer=_fast_optimizer(),
        )
        report = workflow.run()
        assert report.strategy.uses_quantum_runtime
        assert report.execution.solver == "microquantum/qaoa"
        assert report.mapping.target == "IsingModel"
        assert workflow.ising is not None
        assert set(report.solution.assignments) == {"a", "b"}
        assert report.solution.feasible is True
        assert report.provenance.executor == "microquantum/qaoa"
        assert report.provenance.metadata["microquantum_used"] is True
        assert report.provenance.algorithm == "qaoa"

    @pytest.mark.skipif(not qaoa_available(), reason="microquantum missing")
    def test_ising_energy_consistency(self) -> None:
        problem = QuantumProblem("iso", domain="optimization")
        problem.add_variable(Variable.binary("a"))
        problem.add_objective(Objective("v", ObjectiveSense.MINIMIZE, expression="2*a"))
        problem.preferred_strategy = ComputationStrategy.QUANTUM
        workflow = QuantumWorkflow(problem, shots=32, seed=1, qaoa_optimizer=_fast_optimizer())
        workflow.run()
        execution = workflow.execution
        spins = [1 if execution.assignment["a"] == 1 else -1]
        assert workflow.ising.energy(spins) == pytest.approx(execution.energy)
        assert workflow.qubo.energy(execution.assignment) == pytest.approx(execution.energy)
