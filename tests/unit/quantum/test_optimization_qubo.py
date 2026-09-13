"""Tests for the QMQ-02 QUBO model."""

from __future__ import annotations

import itertools

import pytest

from quantsmind.quantum.optimization.expression import parse_expression
from quantsmind.quantum.optimization.qubo import QUBOError, QUBOModel, qubo_from_expression


def _model(**kwargs: object) -> QUBOModel:
    return QUBOModel(variables=["x", "y", "z"], **kwargs)  # type: ignore[arg-type]


class TestConstruction:
    def test_diagonal_absorbed_into_linear(self) -> None:
        model = QUBOModel(
            variables=["x"],
            linear={},
            quadratic={("x", "x"): 5.0},
        )
        assert model.linear == {"x": 5.0}
        assert model.quadratic == {}

    def test_reversed_quadratic_canonicalized(self) -> None:
        model = _model(quadratic={("y", "x"): 2.0})
        assert model.quadratic == {("x", "y"): 2.0}

    def test_accumulation_of_duplicate_terms(self) -> None:
        model = _model(linear={"x": 1.0}, quadratic={("x", "y"): 3.0, ("y", "x"): -1.0})
        assert model.linear == {"x": 1.0}
        assert model.quadratic == {("x", "y"): 2.0}

    def test_zero_terms_dropped(self) -> None:
        model = _model(linear={"x": 0.0}, quadratic={("x", "z"): 0.0})
        assert model.linear == {}
        assert model.quadratic == {}

    @pytest.mark.parametrize(
        "variables",
        [["x", "x"], ["1x"], ["x y"], [""]],
    )
    def test_invalid_variable_names(self, variables: list[str]) -> None:
        with pytest.raises(QUBOError):
            QUBOModel(variables=variables)

    def test_unknown_variable_in_coefficients(self) -> None:
        with pytest.raises(QUBOError):
            _model(linear={"nope": 1.0})
        with pytest.raises(QUBOError):
            _model(quadratic={("x", "nope"): 1.0})

    def test_nonfinite_coefficient(self) -> None:
        with pytest.raises(QUBOError):
            _model(linear={"x": float("inf")})


class TestMutation:
    def test_add_linear_accumulates_and_prunes(self) -> None:
        model = _model()
        model.add_linear("x", 2.0).add_linear("x", -2.0)
        assert model.linear == {}

    def test_add_quadratic_accumulates(self) -> None:
        model = _model()
        model.add_quadratic("y", "x", 2.0).add_quadratic("x", "y", -3.0)
        assert model.quadratic == {("x", "y"): -1.0}

    def test_diagonal_quadratic_rejected(self) -> None:
        with pytest.raises(QUBOError, match="diagonal"):
            _model().add_quadratic("x", "x", 1.0)

    def test_add_constant(self) -> None:
        model = _model()
        model.add_constant(1.5).add_constant(2.5)
        assert model.constant == 4.0

    def test_unknown_variable_mutation(self) -> None:
        with pytest.raises(QUBOError):
            _model().add_linear("nope", 1.0)
        with pytest.raises(QUBOError):
            _model().add_quadratic("x", "nope", 1.0)


class TestEnergy:
    def test_energy_full_dict(self) -> None:
        model = _model(
            linear={"x": 2.0, "y": 3.0},
            quadratic={("x", "y"): 4.0},
            constant=1.0,
        )
        # 1 + 2*1 + 3*0 + 4*1*0
        assert model.energy({"x": 1, "y": 0, "z": 0}) == 3.0
        # 1 + 2 + 3 + 4
        assert model.energy({"x": 1, "y": 1, "z": 0}) == 10.0

    def test_energy_sequence(self) -> None:
        model = _model(linear={"x": 2.0})
        assert model.energy([1, 0, 0]) == 2.0

    def test_energy_bool_values(self) -> None:
        model = _model(linear={"x": 2.0})
        assert model.energy({"x": True, "y": False, "z": False}) == 2.0

    def test_energy_requires_complete_dict(self) -> None:
        model = _model()
        with pytest.raises(QUBOError, match="missing"):
            model.energy({"x": 1})
        with pytest.raises(QUBOError, match="unknown"):
            model.energy({"x": 1, "y": 0, "z": 0, "q": 1})

    def test_energy_requires_exact_sequence(self) -> None:
        model = _model()
        with pytest.raises(QUBOError, match="exactly one bit"):
            model.energy([1, 0])

    def test_energy_rejects_nonbinary(self) -> None:
        model = _model()
        with pytest.raises(QUBOError, match="not binary"):
            model.energy({"x": 2, "y": 0, "z": 0})


class TestFromExpression:
    def test_linear_only(self) -> None:
        model = qubo_from_expression(parse_expression("3*x + 4*y"), ["x", "y"])
        assert model.linear == {"x": 3.0, "y": 4.0}
        assert model.quadratic == {}

    def test_quadratic_and_idempotence(self) -> None:
        model = qubo_from_expression(parse_expression("x*x + x*y"), ["x", "y"])
        assert model.linear == {"x": 1.0}
        assert model.quadratic == {("x", "y"): 1.0}

    def test_constant(self) -> None:
        model = qubo_from_expression(parse_expression("x - 2"), ["x"])
        assert model.constant == -2.0

    def test_degree_too_high_rejected(self) -> None:
        with pytest.raises(QUBOError, match="degree at most 2"):
            qubo_from_expression(parse_expression("x*y*z"), ["x", "y", "z"])

    def test_unknown_variable_rejected(self) -> None:
        with pytest.raises(QUBOError, match="outside the model"):
            qubo_from_expression(parse_expression("x + q"), ["x"])


class TestSerialization:
    def test_round_trip(self) -> None:
        model = _model(
            linear={"x": 2.0, "z": -1.0},
            quadratic={("x", "y"): 3.0},
            constant=5.0,
            offset=1.0,
            name="demo",
        )
        rebuilt = QUBOModel.from_dict(model.to_dict())
        assert rebuilt.name == model.name
        assert rebuilt.variables == model.variables
        assert rebuilt.linear == model.linear
        assert rebuilt.quadratic == model.quadratic
        assert rebuilt.constant == model.constant
        assert rebuilt.offset == model.offset

    def test_quadratic_keys_use_comma(self) -> None:
        data = _model(quadratic={("x", "z"): 3.0}).to_dict()
        assert data["quadratic"] == {"x,z": 3.0}

    def test_serialized_energy_preserved(self) -> None:
        model = _model(linear={"x": 1.5, "y": -2.5}, quadratic={("x", "z"): 0.5})
        rebuilt = QUBOModel.from_dict(model.to_dict())
        for bits in itertools.product([0, 1], repeat=3):
            assignment = dict(zip(model.variables, bits, strict=False))
            assert rebuilt.energy(assignment) == model.energy(assignment)

    def test_degree_property(self) -> None:
        assert _model().degree == 0
        assert _model(linear={"x": 1.0}).degree == 1
        assert _model(quadratic={("x", "y"): 1.0}).degree == 2
