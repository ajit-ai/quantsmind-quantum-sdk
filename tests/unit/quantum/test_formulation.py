"""Tests for the QMQ-01 formulation layer."""

from __future__ import annotations

import pytest

from quantsmind.quantum import (
    Constraint,
    GraphModel,
    MathematicalModel,
    MLModel,
    Objective,
    OptimizationModel,
    QuantumProblem,
    SimulationModel,
    StatisticalModel,
    Variable,
    formulate,
    model_from_dict,
)


def _problem(model_kind: str | None) -> QuantumProblem:
    problem = QuantumProblem("p", domain="optimization")
    problem.add_variable(Variable.binary("x0"))
    if model_kind is not None:
        problem.metadata["model_kind"] = model_kind
    return problem


class TestFormulationModels:
    def test_mathematical_snapshot(self) -> None:
        model = MathematicalModel.from_problem(_problem("optimization"))
        assert model.problem_name == "p"
        assert model.variables == ["x0"]
        assert model.n_variables == 1
        assert model.kind == "mathematical"
        assert model.n_objectives == 0
        assert model.describe()  # non-empty
        assert model.to_dict()["kind"] == "mathematical"

    def test_optimization_model(self) -> None:
        problem = _problem("optimization")
        problem.add_objective(Objective.maximize("profit", expression=None))
        problem.add_constraint(Constraint.le("cap", expression=None, value=1.0))
        model = OptimizationModel.from_problem(problem)
        assert model.kind == "optimization"
        assert model.objective_senses == {"profit": "maximize"}
        assert model.variable_bounds == {"x0": [0, 1]}
        assert model.n_objectives == 1
        assert model.n_constraints == 1

    def test_graph_model(self) -> None:
        problem = _problem("graph")
        problem.metadata["graph_nodes"] = ["a", "b", "c"]
        problem.metadata["graph_edges"] = [["a", "b"], ["b", "c"]]
        model = GraphModel.from_problem(problem)
        assert model.kind == "graph"
        assert model.n_nodes == 3
        assert model.n_edges == 2
        assert ("a", "b") in model.edges
        assert model.to_dict()["edges"] == [["a", "b"], ["b", "c"]]

    def test_ml_model(self) -> None:
        problem = _problem("ml")
        problem.metadata.update(
            {"ml_features": ["f1", "f2"], "ml_target": "y", "ml_task": "regression"}
        )
        model = MLModel.from_problem(problem)
        assert model.kind == "ml"
        assert model.features == ["f1", "f2"]
        assert model.target == "y"
        assert model.task == "regression"

    def test_simulation_model(self) -> None:
        problem = _problem("simulation")
        problem.metadata.update({"simulation_steps": 10, "simulation_dynamics": "hamiltonian"})
        model = SimulationModel.from_problem(problem)
        assert model.kind == "simulation"
        assert model.time_steps == 10
        assert model.n_steps == 10
        assert model.dynamics == "hamiltonian"

    def test_statistical_model(self) -> None:
        problem = _problem("statistical")
        problem.metadata.update(
            {
                "statistical_distribution": "gaussian",
                "statistical_assumptions": ["iid", "normal"],
            }
        )
        model = StatisticalModel.from_problem(problem)
        assert model.kind == "statistical"
        assert model.distribution == "gaussian"
        assert model.assumptions == ["iid", "normal"]

    def test_round_trips(self) -> None:
        for model in [
            MathematicalModel.from_problem(_problem(None)),
            OptimizationModel.from_problem(_problem("optimization")),
            GraphModel.from_problem(_problem("graph")),
            MLModel.from_problem(_problem("ml")),
            SimulationModel.from_problem(_problem("simulation")),
            StatisticalModel.from_problem(_problem("statistical")),
        ]:
            rebuilt = type(model).from_dict(model.to_dict())
            assert rebuilt.kind == model.kind
            assert rebuilt.name == model.name
            assert rebuilt.variables == model.variables


class TestFormulate:
    def test_formulate_returns_existing(self) -> None:
        problem = _problem("optimization")
        model = OptimizationModel.from_problem(problem)
        problem.formulation = model
        assert formulate(problem) is model

    def test_formulate_dispatch(self) -> None:
        assert formulate(_problem("graph")).kind == "graph"
        assert formulate(_problem("optimization")).kind == "optimization"
        assert formulate(_problem(None)).kind == "mathematical"

    def test_formulate_defaults_to_optimization_with_objectives(self) -> None:
        problem = _problem(None)
        problem.add_objective(Objective.maximize("cost", expression=None))
        assert formulate(problem).kind == "optimization"

    def test_model_from_dict_by_kind(self) -> None:
        data = OptimizationModel.from_problem(_problem("optimization")).to_dict()
        rebuilt = model_from_dict(data)
        assert isinstance(rebuilt, OptimizationModel)
        with pytest.raises(ValueError):
            model_from_dict({"kind": "nope"})
