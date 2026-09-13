"""Tests for the QMQ-02 classical exhaustive baseline."""

from __future__ import annotations

import itertools
import random

import pytest

from quantsmind.quantum.optimization.classical import (
    ClassicalSolverResult,
    ExhaustiveLimitError,
    ExhaustiveSolver,
    NoFeasibleSolutionError,
)
from quantsmind.quantum.optimization.qubo import QUBOModel


def _random_qubo(n: int, seed: int) -> QUBOModel:
    rng = random.Random(seed)
    names = [f"x{i}" for i in range(n)]
    linear = {name: rng.uniform(-5, 5) for name in names}
    quadratic: dict[tuple[str, str], float] = {}
    for i in range(n):
        for j in range(i + 1, n):
            value = rng.uniform(-3, 3)
            if abs(value) > 1e-3:
                quadratic[(names[i], names[j])] = value
    return QUBOModel(
        variables=names,
        linear=linear,
        quadratic=quadratic,
        constant=rng.uniform(-2, 2),
        name=f"random_{seed}",
    )


class TestExhaustiveSolver:
    def test_trivial_minimum(self) -> None:
        qubo = QUBOModel(variables=["x"], linear={"x": 5.0})
        result = ExhaustiveSolver().solve(qubo)
        assert result.assignment == {"x": 0}
        assert result.energy == 0.0
        assert result.solver == "classical/exhaustive"
        assert result.exhaustive is True
        assert result.num_evaluations == 2
        assert result.num_feasible == 2

    def test_matches_brute_force(self) -> None:
        for seed in range(4):
            qubo = _random_qubo(6, seed)
            best_energy = min(
                qubo.energy(dict(zip(qubo.variables, bits, strict=False)))
                for bits in itertools.product([0, 1], repeat=6)
            )
            result = ExhaustiveSolver().solve(qubo)
            assert result.energy == pytest.approx(best_energy)
            assert result.num_evaluations == 2**6

    def test_feasibility_predicate(self) -> None:
        qubo = _random_qubo(4, 1)
        solver = ExhaustiveSolver()

        def predicate(assignment: dict[str, int]) -> bool:
            return sum(assignment.values()) % 2 == 0

        expected = min(
            qubo.energy(dict(zip(qubo.variables, bits, strict=False)))
            for bits in itertools.product([0, 1], repeat=4)
            if sum(bits) % 2 == 0
        )
        result = solver.solve(qubo, is_feasible=predicate)
        assert result.energy == pytest.approx(expected)
        assert result.feasible is True
        assert sum(result.assignment.values()) % 2 == 0
        assert result.num_feasible == 8

    def test_objective_value_recorded(self) -> None:
        qubo = QUBOModel(variables=["x", "y"], linear={"x": 1.0})
        result = ExhaustiveSolver().solve(qubo, objective_fn=lambda a: -3 * a["x"] - 4 * a["y"])
        # min QUBO energy at (0, 0) -> objective 0.
        assert result.assignment == {"x": 0, "y": 0}
        assert result.objective_value == 0.0

    def test_tie_break_is_deterministic(self) -> None:
        qubo = QUBOModel(
            variables=["a", "b"],
            linear={"a": 1.0, "b": 1.0},
            quadratic={("a", "b"): -2.0},
        )
        result = ExhaustiveSolver().solve(qubo)
        # minima at (0,0) and (1,1); Gray order visits (0,0) first.
        assert result.assignment == {"a": 0, "b": 0}
        assert result.energy == 0.0

    def test_no_feasible_solution(self) -> None:
        qubo = QUBOModel(variables=["x"], linear={"x": 0.0})
        with pytest.raises(NoFeasibleSolutionError, match="no feasible"):
            ExhaustiveSolver().solve(qubo, is_feasible=lambda a: a["x"] == 2)

    def test_exhaustive_limit(self) -> None:
        qubo = _random_qubo(4, 0)
        solver = ExhaustiveSolver(max_variables=3)
        with pytest.raises(ExhaustiveLimitError, match="exceeds the configured limit"):
            solver.solve(qubo)

    def test_invalid_limit(self) -> None:
        with pytest.raises(ValueError):
            ExhaustiveSolver(max_variables=0)

    def test_large_qubo_at_limit(self) -> None:
        qubo = _random_qubo(3, 2)
        result = ExhaustiveSolver(max_variables=3).solve(qubo)
        assert result.num_evaluations == 8
        assert result.limit == 3


class TestClassicalSolverResult:
    def test_to_dict_round_trip(self) -> None:
        result = ClassicalSolverResult(
            assignment={"x": 1, "y": 0},
            energy=-3.5,
            objective_value=7.0,
            num_evaluations=4,
            num_feasible=3,
            limit=20,
        )
        rebuilt = ClassicalSolverResult.from_dict(result.to_dict())
        assert rebuilt.solver == "classical/exhaustive"
        assert rebuilt.assignment == {"x": 1, "y": 0}
        assert rebuilt.energy == -3.5
        assert rebuilt.objective_value == 7.0
        assert rebuilt.num_evaluations == 4
        assert rebuilt.num_feasible == 3
        assert rebuilt.limit == 20
