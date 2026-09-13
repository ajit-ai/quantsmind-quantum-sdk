"""Tests for the QMQ-01 workflow layer (QuantumWorkflow)."""

from __future__ import annotations

import pytest

from quantsmind.quantum import (
    Constraint,
    MappingError,
    Objective,
    QuantumProblem,
    QuantumProgram,
    QuantumWorkflow,
    QUBOModel,
    SolutionReport,
    Variable,
)
from quantsmind.quantum.strategy.strategy import ComputationStrategy


def _bell_problem() -> QuantumProblem:
    problem = QuantumProblem("bit-flip", domain="optimization")
    problem.add_variable(Variable.binary("x0"))
    problem.add_variable(Variable.binary("x1"))
    problem.add_objective(Objective.maximize("ones", expression=lambda v: v["x0"] + v["x1"]))
    problem.add_constraint(Constraint.le("cap", expression=lambda v: v["x0"] + v["x1"], value=2.0))
    # qubit 0 -> x0, qubit 1 -> x1
    problem.metadata["encoding"] = {"0": "x0", "1": "x1"}
    return problem


def _symbolic_problem() -> QuantumProblem:
    problem = QuantumProblem("knapsack", domain="optimization")
    problem.add_variable(Variable.binary("x0"))
    problem.add_variable(Variable.binary("x1"))
    problem.add_objective(Objective.maximize("value", expression="3*x0 + 4*x1"))
    problem.add_constraint(Constraint.le("cap", expression="2*x0 + 3*x1", value=5.0))
    return problem


class TestQuantumWorkflow:
    def test_requires_problem_type(self) -> None:
        with pytest.raises(TypeError):
            QuantumWorkflow("nope")

    def test_stage_formulate(self) -> None:
        workflow = QuantumWorkflow(_bell_problem())
        model = workflow.formulate()
        assert model.kind == "optimization"
        assert workflow.formulation is model

    def test_stage_select_strategy(self) -> None:
        workflow = QuantumWorkflow(_bell_problem())
        assert workflow.select_strategy().name == "HYBRID"
        assert workflow.select_strategy().uses_quantum_runtime

    def test_map_no_program_problem_to_qubo(self) -> None:
        problem = _symbolic_problem()
        problem.preferred_strategy = ComputationStrategy.CLASSICAL
        workflow = QuantumWorkflow(problem)
        mapping = workflow.map()
        assert mapping.target == "QUBOModel"
        assert isinstance(workflow.qubo, QUBOModel)
        assert workflow.qubo.variables[:2] == ["x0", "x1"]

    def test_map_callable_objective_without_program_raises(self) -> None:
        # A callable objective cannot be turned into a QUBO automatically;
        # the mapping fails loudly instead of faking a result.
        problem = _bell_problem()
        problem.preferred_strategy = ComputationStrategy.CLASSICAL
        workflow = QuantumWorkflow(problem)
        with pytest.raises(MappingError, match="objective"):
            workflow.map()

    def test_run_end_to_end(self) -> None:
        workflow = QuantumWorkflow(
            _bell_problem(),
            program=QuantumProgram.bell_state(),
            backend="statevector",
            shots=100,
            seed=7,
            name="e2e",
        )
        report = workflow.run()
        assert isinstance(report, SolutionReport)
        assert report.problem.name == "bit-flip"
        assert report.formulation.kind == "optimization"
        assert report.strategy.uses_quantum_runtime
        assert report.mapping is not None
        assert report.execution is not None
        assert report.solution is not None
        assert report.solution.feasible
        assert report.interpretation.quality.value in {"high", "medium"}
        assert report.provenance.sdk_version
        assert report.provenance.strategy_label == "hybrid"

    def test_run_decodes_assignments(self) -> None:
        workflow = QuantumWorkflow(
            _bell_problem(),
            program=QuantumProgram.bell_state(),
            backend="statevector",
            shots=100,
            seed=7,
        )
        report = workflow.run()
        # bell counts are {"00": 50, "11": 50}; most probable (deterministic
        # tie-break to "00") decodes x0=0, x1=0.
        assert set(report.solution.assignments) == {"x0", "x1"}
        assert report.solution.assignments["x0"] in {0, 1}
        assert report.solution.assignments["x1"] in {0, 1}

    def test_report_serializes(self) -> None:
        workflow = QuantumWorkflow(
            _bell_problem(),
            program=QuantumProgram.bell_state(),
            backend="statevector",
            shots=32,
            seed=1,
        )
        data = workflow.run().to_dict()
        assert isinstance(data, dict)
        assert data["strategy"] == "hybrid"
        assert data["problem"]["name"] == "bit-flip"
        assert data["interpretation"]["quality"] in {"high", "medium"}

    def test_execution_uses_microquantum(self) -> None:
        workflow = QuantumWorkflow(
            _bell_problem(),
            program=QuantumProgram.bell_state(),
            backend="statevector",
            shots=64,
            seed=3,
        )
        report = workflow.run()
        assert report.execution.backend_name == "statevector"
        assert report.execution.shots == 64
        assert result_is_enriched(report)

    def test_provenance_captures_execution(self) -> None:
        workflow = QuantumWorkflow(
            _bell_problem(),
            program=QuantumProgram.bell_state(),
            backend="statevector",
            shots=16,
            seed=2,
        )
        report = workflow.run()
        assert report.provenance.execution_metadata["shots"] == 16
        assert report.provenance.execution_metadata["actual_backend"] == "statevector"


def result_is_enriched(report: SolutionReport) -> bool:
    """QuantumResult enrichment marker: program name + progress."""
    return bool(getattr(report.execution, "program_name", "")) and bool(
        getattr(report.execution, "experiment_id", "")
    )
