"""Tests for the QMQ-01 result layer (SolutionReport, Interpretation, Provenance)."""

from __future__ import annotations

from quantsmind.quantum import (
    ComputationStrategy,
    Constraint,
    Interpretation,
    InterpretationQuality,
    ProblemSolution,
    Provenance,
    QuantumProblem,
    SolutionInterpreter,
    SolutionReport,
    Variable,
)


class TestInterpretation:
    def test_high_feasible(self) -> None:
        problem = QuantumProblem("p", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        problem.add_constraint(Constraint.le("cap", expression=lambda v: v["x0"], value=1.0))
        solution = ProblemSolution.from_names("p", ["x0"], [], ["cap"])
        solution.assignments = {"x0": 0}
        solution.evaluate(problem)
        interpretation = SolutionInterpreter().interpret(solution)
        assert interpretation.quality is InterpretationQuality.HIGH
        assert interpretation.details["feasible"] is True

    def test_low_infeasible(self) -> None:
        problem = QuantumProblem("p", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        problem.add_constraint(Constraint.ge("min", expression=lambda v: v["x0"], value=1.0))
        solution = ProblemSolution.from_names("p", ["x0"], [], ["min"])
        solution.assignments = {"x0": 0}
        solution.evaluate(problem)
        interpretation = SolutionInterpreter().interpret(solution)
        assert interpretation.quality is InterpretationQuality.LOW
        assert "infeasible" in interpretation.summary

    def test_unknown_when_nothing_evaluable(self) -> None:
        solution = ProblemSolution.from_names("p", ["x0"], [], [])
        interpretation = SolutionInterpreter().interpret(solution)
        assert interpretation.quality is InterpretationQuality.UNKNOWN

    def test_interpretation_round_trip(self) -> None:
        interpretation = Interpretation(
            summary="feasible",
            quality=InterpretationQuality.HIGH,
            confidence=0.9,
            details={"feasible": True},
        )
        rebuilt = Interpretation.from_dict(interpretation.to_dict())
        assert rebuilt.quality is interpretation.quality
        assert rebuilt.confidence == 0.9

    def test_interpretation_records_strategy(self) -> None:
        problem = QuantumProblem("p", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        solution = ProblemSolution.from_names("p", ["x0"], [], [])
        interpretation = SolutionInterpreter()(solution, strategy=ComputationStrategy.HYBRID)
        assert interpretation.details["strategy"] == "hybrid"

    def test_call_aliases_interpret(self) -> None:
        solution = ProblemSolution.from_names("p", ["x0"], [], [])
        assert SolutionInterpreter()(solution) == SolutionInterpreter().interpret(solution)


class TestProvenance:
    def test_basic(self) -> None:
        provenance = Provenance(strategy=ComputationStrategy.HYBRID, formulation="optimization")
        assert provenance.strategy_label == "hybrid"
        assert provenance.sdk_version

    def test_from_execution(self) -> None:
        class FakeResult:
            experiment_id = "exp-1"
            program_name = "bell"
            backend_name = "statevector"
            shots = 32
            provenance = {"executed_backend": "statevector"}

        provenance = Provenance.from_execution(
            strategy=ComputationStrategy.HYBRID,
            formulation="optimization",
            algorithm="",
            execution=FakeResult(),
        )
        assert provenance.execution_metadata["actual_backend"] == "statevector"
        assert provenance.execution_metadata["shots"] == 32
        assert provenance.backend == "statevector"

    def test_round_trip(self) -> None:
        provenance = Provenance(strategy="hybrid", formulation="graph")
        rebuilt = Provenance.from_dict(provenance.to_dict())
        assert rebuilt.strategy_label == "hybrid"
        assert rebuilt.formulation == "graph"


class TestSolutionReport:
    def test_empty_serializes(self) -> None:
        data = SolutionReport().to_dict()
        assert data["problem"] is None
        assert data["strategy"] is None

    def test_with_problem(self) -> None:
        problem = QuantumProblem("p", domain="optimization")
        report = SolutionReport(problem=problem)
        assert report.to_dict()["problem"]["name"] == "p"
        assert "created_at" in report.to_dict()
