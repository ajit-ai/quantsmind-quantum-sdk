"""Tests for the QMQ-02 automatic QUBO/Ising mapping pipeline."""

from __future__ import annotations

import itertools

import pytest

from quantsmind.quantum import (
    Constraint,
    MappingError,
    Objective,
    ObjectiveSense,
    OptimizationModel,
    QuantumProblem,
    Variable,
)
from quantsmind.quantum.mapping.ising import IsingMapper
from quantsmind.quantum.mapping.qubo import ProblemMapper, QUBOMapper
from quantsmind.quantum.optimization.ising import IsingModel
from quantsmind.quantum.optimization.qubo import QUBOModel
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
    return problem


class TestProblemMapper:
    def test_maps_optimization_problem(self) -> None:
        model = ProblemMapper().map(_knapsack_problem())
        assert isinstance(model, OptimizationModel)
        assert model.name == "knapsack_model"
        assert model.problem_name == "knapsack"


class TestQUBOMapper:
    def test_knapsack_global_optimum_exact(self) -> None:
        problem = _knapsack_problem()
        mapping = QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL)
        qubo = mapping.payload
        assert isinstance(qubo, QUBOModel)
        assert mapping.target == "QUBOModel"
        assert mapping.metadata["sense"] == "maximize"
        assert mapping.metadata["sense_inverted"] is True
        assert mapping.metadata["decision_variables"] == ["x0", "x1", "x2"]
        assert mapping.metadata["slack_variables"] == [
            "capacity_slack_0",
            "capacity_slack_1",
            "capacity_slack_2",
        ]
        assert mapping.metadata["penalty"] == pytest.approx(60.0)

        best = min(
            qubo.energy(dict(zip(qubo.variables, bits, strict=False)))
            for bits in itertools.product([0, 1], repeat=len(qubo.variables))
        )
        # -3-4 = -7 achieved by the only feasible optimum (1, 1, 0).
        assert best == pytest.approx(-7.0)
        assert problem.constraints[0].evaluate({"x0": 1, "x1": 1, "x2": 0}).name == "SATISFIED"

    def test_minimize_sense_not_inverted(self) -> None:
        problem = QuantumProblem("min_cost", domain="optimization")
        problem.add_variable(Variable.binary("x"))
        problem.add_objective(Objective("cost", ObjectiveSense.MINIMIZE, expression="3*x"))
        mapping = QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL)
        assert mapping.metadata["sense_inverted"] is False
        assert mapping.payload.linear["x"] == 3.0

    def test_penalty_parameter_honored(self) -> None:
        mapping = QUBOMapper().map(
            _knapsack_problem(),
            strategy=ComputationStrategy.CLASSICAL,
            penalty=25.0,
        )
        assert mapping.metadata["penalty"] == 25.0
        assert all(t["weight"] == 25.0 for t in mapping.metadata["penalties"])

    def test_callable_objective_rejected(self) -> None:
        problem = QuantumProblem("p", domain="optimization")
        problem.add_variable(Variable.binary("x"))
        problem.add_objective(Objective.maximize("o", expression=lambda v: v["x"]))
        with pytest.raises(MappingError, match="cannot be mapped"):
            QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL)

    def test_missing_objective_rejected(self) -> None:
        problem = QuantumProblem("p", domain="optimization")
        problem.add_variable(Variable.binary("x"))
        with pytest.raises(MappingError, match="optimization"):
            QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL)

    def test_unknown_variable_in_objective_rejected(self) -> None:
        problem = QuantumProblem("p", domain="optimization")
        problem.add_variable(Variable.binary("x"))
        problem.add_objective(Objective.maximize("o", expression="x + qq"))
        with pytest.raises(MappingError, match="outside the problem"):
            QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL)

    def test_non_binary_variable_rejected(self) -> None:
        problem = QuantumProblem("p", domain="optimization")
        problem.add_variable(Variable.integer("n", lower_bound=0, upper_bound=3))
        problem.add_objective(Objective.minimize("o", expression="3*n"))
        with pytest.raises(MappingError, match="binary variables only"):
            QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL)

    def test_degree_three_rejected(self) -> None:
        problem = QuantumProblem("p", domain="optimization")
        for name in ("x", "y", "z"):
            problem.add_variable(Variable.binary(name))
        problem.add_objective(Objective.minimize("o", expression="x*y*z"))
        with pytest.raises(MappingError, match="degree 3"):
            QUBOMapper().map(problem, strategy=ComputationStrategy.CLASSICAL)


class TestIsingMapper:
    def test_qubo_to_ising_payload(self) -> None:
        mapping = QUBOMapper().map(_knapsack_problem(), strategy=ComputationStrategy.QUANTUM)
        ising_mapping = IsingMapper().map(mapping.payload)
        assert ising_mapping.target == "IsingModel"
        ising = ising_mapping.payload
        assert isinstance(ising, IsingModel)
        assert ising.num_variables == len(mapping.payload.variables)
        # energy-exact for a sample assignment
        assignment = {name: (i % 2) for i, name in enumerate(ising.variables)}
        spins = [2 * assignment[name] - 1 for name in ising.variables]
        assert ising.energy(spins) == pytest.approx(mapping.payload.energy(assignment))

    def test_rejects_non_qubo(self) -> None:
        with pytest.raises(MappingError, match="QUBOModel"):
            IsingMapper().map("not-a-qubo")
