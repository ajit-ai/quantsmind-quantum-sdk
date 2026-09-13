"""Tests for the QMQ-01 core domain objects."""

from __future__ import annotations

import pytest

from quantsmind.quantum import (
    Constraint,
    ConstraintOperator,
    ConstraintPriority,
    ConstraintStatus,
    DomainContext,
    Objective,
    ObjectiveSense,
    OptimizationModel,
    ProblemSolution,
    QuantumProblem,
    Variable,
    VariableType,
)


class TestVariable:
    def test_binary_factory(self) -> None:
        variable = Variable.binary("x0")
        assert variable.name == "x0"
        assert variable.type is VariableType.BINARY
        assert variable.lower_bound == 0 and variable.upper_bound == 1

    def test_integer_and_continuous(self) -> None:
        assert Variable.integer("i", -2, 10).upper_bound == 10
        assert Variable.continuous("c").lower_bound is None
        assert Variable.categorical("cat", domain="labels").type is VariableType.CATEGORICAL

    def test_bounds_validation(self) -> None:
        with pytest.raises(ValueError):
            Variable.integer("i", 10, 1)
        with pytest.raises(ValueError):
            Variable("x", VariableType.CATEGORICAL, lower_bound=0)

    def test_vtype_parse(self) -> None:
        assert VariableType.parse("binary") is VariableType.BINARY
        assert VariableType.parse(VariableType.INTEGER) is VariableType.INTEGER
        assert VariableType.parse("CONTINUOUS") is VariableType.CONTINUOUS
        assert VariableType.parse("categorical") is VariableType.CATEGORICAL
        with pytest.raises(ValueError):
            VariableType.parse("nope")

    def test_round_trip(self) -> None:
        variable = Variable.binary("x", description="flag")
        rebuilt = Variable.from_dict(variable.to_dict())
        assert rebuilt == variable


class TestObjective:
    def test_minimize_maximize_factories(self) -> None:
        assert Objective.minimize("cost").sense is ObjectiveSense.MINIMIZE
        assert Objective.maximize("profit").sense is ObjectiveSense.MAXIMIZE

    def test_sense_parse(self) -> None:
        assert ObjectiveSense.parse("min") is ObjectiveSense.MINIMIZE
        assert ObjectiveSense.parse("maximize") is ObjectiveSense.MAXIMIZE
        with pytest.raises(ValueError):
            ObjectiveSense.parse("sideways")

    def test_negative_weight_rejected(self) -> None:
        with pytest.raises(ValueError):
            Objective.maximize("profit", weight=-1.0)

    def test_evaluate_callable(self) -> None:
        objective = Objective(
            "cost",
            ObjectiveSense.MAXIMIZE,
            expression=lambda variables: variables["x"] * 2 + 1,
            weight=3.0,
        )
        # evaluate() returns the raw expression value; weight applies later
        assert objective.evaluate({"x": 4}) == 9.0

    def test_evaluate_symbolic_string(self) -> None:
        objective = Objective("cost", ObjectiveSense.MINIMIZE, expression="2*x + 1")
        assert objective.evaluate({"x": 4}) == 9.0

    def test_evaluate_symbolic_parse_error(self) -> None:
        from quantsmind.quantum.optimization.expression import ExpressionParseError

        objective = Objective("cost", ObjectiveSense.MINIMIZE, expression="2x + 1")
        with pytest.raises(ExpressionParseError):
            objective.evaluate({"x": 4})

    def test_evaluate_none(self) -> None:
        objective = Objective("cost", ObjectiveSense.MINIMIZE, weight=2.0)
        assert objective.evaluate({"x": 4}) is None

    def test_round_trip(self) -> None:
        objective = Objective.maximize("profit", weight=2.5)
        rebuilt = Objective.from_dict(objective.to_dict())
        assert rebuilt.name == objective.name
        assert rebuilt.sense is objective.sense
        assert rebuilt.weight == objective.weight
        # callable expressions are not serialized
        assert rebuilt.expression is None

    def test_describe(self) -> None:
        assert Objective.minimize("cost").describe() == "minimize cost"


class TestConstraint:
    def test_factory_operators(self) -> None:
        le = Constraint.le("c1", expression=lambda v: v["x"], value=5.0)
        ge = Constraint.ge("c2", expression=lambda v: v["x"], value=1.0)
        eq = Constraint.eq("c3", expression=lambda v: v["x"], value=3.0)
        assert le.operator is ConstraintOperator.LE
        assert ge.operator is ConstraintOperator.GE
        assert eq.operator is ConstraintOperator.EQ

    def test_priority_and_operator_parse(self) -> None:
        assert ConstraintPriority.parse("soft") is ConstraintPriority.SOFT
        assert ConstraintOperator.parse("<=") is ConstraintOperator.LE
        assert ConstraintOperator.parse("eq") is ConstraintOperator.EQ
        with pytest.raises(ValueError):
            ConstraintOperator.parse("~~")

    def test_negative_penalty_rejected(self) -> None:
        with pytest.raises(ValueError):
            Constraint.le("c1", penalty=-1.0)

    def test_evaluate_and_status(self) -> None:
        constraint = Constraint.le(
            "c1",
            expression=lambda v: v["x"],
            value=5.0,
            priority=ConstraintPriority.HARD,
        )
        assert constraint.evaluate({"x": 3}) is ConstraintStatus.SATISFIED
        assert constraint.evaluate({"x": 6}) is ConstraintStatus.VIOLATED
        assert constraint.evaluate({"x": 5.0}) is ConstraintStatus.SATISFIED

    def test_equality_tolerance(self) -> None:
        eq = Constraint.eq("eq1", expression=lambda v: v["x"], value=5.0)
        assert eq.evaluate({"x": 5.0 + 1e-12}) is ConstraintStatus.SATISFIED
        assert eq.evaluate({"x": 5.1}) is ConstraintStatus.VIOLATED

    def test_status_from_symbolic_string(self) -> None:

        constraint = Constraint.le("c1", expression="x", value=5.0)
        assert constraint.evaluate({"x": 3}) is ConstraintStatus.SATISFIED
        assert constraint.evaluate({"x": 6}) is ConstraintStatus.VIOLATED

    def test_status_from_bad_symbolic_string(self) -> None:
        from quantsmind.quantum.optimization.expression import ExpressionParseError

        # "x <= 5" embeds the operator in the expression, which is not a
        # valid symbolic expression; the operator belongs on the Constraint.
        with pytest.raises(ExpressionParseError):
            Constraint.le("c1", expression="x <= 5", value=5.0).evaluate({"x": 3})

    def test_unknown_without_expression(self) -> None:
        assert Constraint.le("c1").evaluate({"x": 3}) is ConstraintStatus.UNKNOWN

    def test_round_trip(self) -> None:
        constraint = Constraint.eq("c", expression=lambda v: v["x"], value=2.0)
        rebuilt = Constraint.from_dict(constraint.to_dict())
        assert rebuilt.name == "c"
        assert rebuilt.operator is ConstraintOperator.EQ
        assert rebuilt.value == 2.0
        assert rebuilt.expression is None


class TestDomainContext:
    def test_qualified_includes_subdomain(self) -> None:
        context = DomainContext(domain="finance", subdomain="portfolio", use_case="optimization")
        assert context.qualified() == "finance/portfolio"

    def test_qualified_without_subdomain(self) -> None:
        assert DomainContext(domain="physics").qualified() == "physics"

    def test_round_trip(self) -> None:
        context = DomainContext(domain="physics", units=["eV"])
        rebuilt = DomainContext.from_dict(context.to_dict())
        assert rebuilt == context

    def test_empty_domain_rejected(self) -> None:
        with pytest.raises(ValueError):
            DomainContext(domain="  ")


class TestQuantumProblem:
    def test_construction_and_coercion(self) -> None:
        problem = QuantumProblem("p1", domain="optimization", description="test problem")
        assert isinstance(problem.domain, DomainContext)
        assert problem.domain.domain == "optimization"
        assert problem.size == 0

    def test_add_and_get(self) -> None:
        problem = QuantumProblem("p1", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        problem.add_objective(Objective.maximize("profit", expression=lambda v: v["x0"]))
        problem.add_constraint(Constraint.eq("c", expression=lambda v: v["x0"], value=1.0))
        assert problem.variable_names == ["x0"]
        assert problem.objective_names == ["profit"]
        assert problem.constraint_names == ["c"]
        assert problem.variable("x0").name == "x0"
        assert problem.objective("profit").name == "profit"
        assert problem.constraint("c").name == "c"
        assert problem.size == 1

    def test_duplicate_raises(self) -> None:
        problem = QuantumProblem("p1", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        with pytest.raises(ValueError, match="duplicate variable"):
            problem.add_variable(Variable.binary("x0"))
        with pytest.raises(KeyError, match="ghost"):
            problem.variable("ghost")

    def test_preferred_strategy_coercion(self) -> None:
        problem = QuantumProblem("p1", domain="optimization", preferred_strategy="hybrid")
        assert problem.preferred_strategy.name == "HYBRID"

    def test_preferred_strategy_invalid(self) -> None:
        with pytest.raises(ValueError):
            QuantumProblem("p1", domain="optimization", preferred_strategy="nope")

    def test_round_trip_with_formulation(self) -> None:
        problem = QuantumProblem("p1", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        problem.formulation = OptimizationModel.from_problem(problem)
        rebuilt = QuantumProblem.from_dict(problem.to_dict())
        assert rebuilt.name == "p1"
        assert [v.name for v in rebuilt.variables] == ["x0"]
        assert rebuilt.formulation is not None
        assert rebuilt.formulation.kind == "optimization"
        assert rebuilt.preferred_strategy is None


class TestProblemSolution:
    def _make_problem(self) -> QuantumProblem:
        problem = QuantumProblem("p", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        problem.add_variable(Variable.binary("x1"))
        problem.add_objective(Objective.maximize("profit", expression=lambda v: v["x0"] + v["x1"]))
        problem.add_constraint(
            Constraint.le("cap", expression=lambda v: v["x0"] + v["x1"], value=1.0)
        )
        return problem

    def test_evaluate_and_feasibility(self) -> None:
        problem = self._make_problem()
        solution = ProblemSolution.from_names("p", ["x0", "x1"], ["profit"], ["cap"])
        solution.assignments = {"x0": 1, "x1": 0}
        solution.evaluate(problem)
        assert solution.feasible
        assert solution.objective_values["profit"] == 1.0
        assert solution.constraint_status["cap"] is ConstraintStatus.SATISFIED

    def test_violated_constraint_infeasible(self) -> None:
        problem = self._make_problem()
        solution = ProblemSolution.from_names("p", ["x0", "x1"], ["profit"], ["cap"])
        solution.assignments = {"x0": 1, "x1": 1}
        solution.evaluate(problem)
        assert not solution.feasible
        assert solution.constraint_status["cap"] is ConstraintStatus.VIOLATED

    def test_score_sense_aware_maximize(self) -> None:
        problem = self._make_problem()
        solution = ProblemSolution.from_names("p", ["x0", "x1"], ["profit"], ["cap"])
        solution.assignments = {"x0": 1, "x1": 0}
        solution.evaluate(problem)
        assert solution.compute_score(problem) == 1.0

    def test_score_minimize_negated(self) -> None:
        problem = QuantumProblem("p", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        problem.add_objective(Objective.minimize("cost", expression=lambda v: v["x0"], weight=2.0))
        solution = ProblemSolution.from_names("p", ["x0"], ["cost"], [])
        solution.assignments = {"x0": 1}
        assert solution.compute_score(problem) == -2.0

    def test_round_trip(self) -> None:
        solution = ProblemSolution.from_names("p", ["x"], ["o"], ["c"])
        solution.assignments = {"x": 1}
        solution.constraint_status["c"] = ConstraintStatus.SATISFIED
        rebuilt = ProblemSolution.from_dict(solution.to_dict())
        assert rebuilt.assignments == {"x": 1}
        assert rebuilt.constraint_status["c"] is ConstraintStatus.SATISFIED
