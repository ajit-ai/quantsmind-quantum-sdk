"""Tests for the QMQ-02 Ising model and QUBO <-> Ising conversions.

The conversion is asserted to be **energy-exact**: for every binary assignment
``E_qubo(x) == E_ising(s(x))`` with ``s = 2x - 1``, and the round trip
``QUBO -> Ising -> QUBO`` preserves every energy exactly.
"""

from __future__ import annotations

import itertools

import pytest

from quantsmind.quantum.optimization.ising import IsingError, IsingModel
from quantsmind.quantum.optimization.qubo import QUBOModel


class TestConstruction:
    def test_canonicalization(self) -> None:
        model = IsingModel(
            variables=["a", "b"],
            h={"b": 2.0, "a": 1.0},
            couplings={("b", "a"): 3.0},
        )
        assert model.variables == ["a", "b"]
        assert model.h == {"b": 2.0, "a": 1.0}
        assert model.couplings == {("a", "b"): 3.0}

    def test_zero_terms_dropped(self) -> None:
        model = IsingModel(variables=["a", "b"], h={"a": 0.0}, couplings={("a", "b"): 0.0})
        assert model.h == {}
        assert model.couplings == {}

    def test_duplicate_variables_rejected(self) -> None:
        with pytest.raises(IsingError, match="duplicate"):
            IsingModel(variables=["a", "a"])

    def test_unknown_variable_rejected(self) -> None:
        with pytest.raises(IsingError, match="unknown"):
            IsingModel(variables=["a"], h={"b": 1.0})
        with pytest.raises(IsingError, match="unknown"):
            IsingModel(variables=["a"], couplings={("a", "b"): 1.0})

    def test_self_coupling_rejected(self) -> None:
        with pytest.raises(IsingError, match="self-coupling"):
            IsingModel(variables=["a"], couplings={("a", "a"): 1.0})

    def test_mutators(self) -> None:
        model = IsingModel(variables=["a", "b"])
        model.add_field("a", 2.0).add_field("a", -1.0)
        model.add_coupling("b", "a", 3.0).add_field("b", 0.0)
        assert model.h == {"a": 1.0}
        assert model.couplings == {("a", "b"): 3.0}
        with pytest.raises(IsingError):
            model.add_field("nope", 1.0)
        with pytest.raises(IsingError):
            model.add_coupling("a", "a", 1.0)


class TestEnergy:
    def test_energy_dict(self) -> None:
        model = IsingModel(
            variables=["a", "b"],
            h={"a": -1.0, "b": 2.0},
            couplings={("a", "b"): 4.0},
            constant=3.0,
        )
        # 3 + (-1)(-1) + 2(1) + 4(-1)(1)
        assert model.energy({"a": -1, "b": 1}) == 3.0 + 1.0 + 2.0 - 4.0
        # 3 + (-1)(1) + 2(1) + 4(1)(1)
        assert model.energy({"a": 1, "b": 1}) == 3.0 - 1.0 + 2.0 + 4.0

    def test_energy_sequence(self) -> None:
        model = IsingModel(variables=["a", "b"], h={"a": 2.0})
        assert model.energy([-1, 1]) == -2.0

    def test_energy_validation(self) -> None:
        model = IsingModel(variables=["a"])
        with pytest.raises(IsingError, match="missing"):
            model.energy({})
        with pytest.raises(IsingError, match="unknown"):
            model.energy({"q": -1})
        with pytest.raises(IsingError, match="not a spin"):
            model.energy({"a": 0})
        with pytest.raises(IsingError, match="exactly one spin"):
            model.energy([-1, 1])


class TestConversionExactness:
    def _qubo(self) -> QUBOModel:
        return QUBOModel(
            variables=["x0", "x1", "x2"],
            linear={"x0": -3.0, "x1": -4.0, "x2": -5.0},
            quadratic={
                ("x0", "x1"): 2.0,
                ("x0", "x2"): -1.5,
                ("x1", "x2"): 0.5,
            },
            constant=0.0,
        )

    def test_from_qubo_is_energy_exact(self) -> None:
        qubo = self._qubo()
        ising = IsingModel.from_qubo(qubo)
        for bits in itertools.product([0, 1], repeat=3):
            spin = [2 * bit - 1 for bit in bits]
            assignment = dict(zip(qubo.variables, bits, strict=False))
            assert ising.energy(spin) == pytest.approx(qubo.energy(assignment))

    def test_to_qubo_is_energy_exact(self) -> None:
        ising = IsingModel(
            variables=["x0", "x1", "x2"],
            h={"x0": 1.5, "x1": -2.0, "x2": 0.25},
            couplings={("x0", "x2"): 1.5, ("x1", "x2"): -0.5},
            constant=-2.0,
        )
        qubo = ising.to_qubo()
        for bits in itertools.product([0, 1], repeat=3):
            spin = [2 * bit - 1 for bit in bits]
            assignment = dict(zip(ising.variables, bits, strict=False))
            assert qubo.energy(assignment) == pytest.approx(ising.energy(spin))

    def test_round_trip_preserves_energy(self) -> None:
        qubo = self._qubo()
        qubo.offset = 4.0
        round_trip = IsingModel.from_qubo(qubo).to_qubo()
        for bits in itertools.product([0, 1], repeat=3):
            assignment = dict(zip(qubo.variables, bits, strict=False))
            assert round_trip.energy(assignment) == pytest.approx(qubo.energy(assignment))

    def test_known_conversion_values(self) -> None:
        ising = IsingModel.from_qubo(QUBOModel(variables=["x"], linear={"x": -3.0}))
        # h = a/2 = -1.5, constant = a/2 = -1.5.
        assert ising.h == {"x": -1.5}
        assert ising.constant == -1.5
        assert ising.energy([-1]) == pytest.approx(0.0)
        assert ising.energy([1]) == pytest.approx(-3.0)

    def test_conversion_metadata(self) -> None:
        ising = IsingModel.from_qubo(self._qubo())
        assert ising.metadata["source"] == "qubo_to_ising"
        assert ising.name == "qubo_ising"


class TestSerialization:
    def test_round_trip(self) -> None:
        model = IsingModel(
            variables=["a", "b"],
            h={"a": 1.0, "b": -2.0},
            couplings={("a", "b"): 3.0},
            constant=0.5,
            offset=1.0,
            name="demo",
        )
        rebuilt = IsingModel.from_dict(model.to_dict())
        assert rebuilt.name == model.name
        assert rebuilt.variables == model.variables
        assert rebuilt.h == model.h
        assert rebuilt.couplings == model.couplings
        assert rebuilt.constant == model.constant
        assert rebuilt.offset == model.offset

    def test_coupling_keys_use_comma(self) -> None:
        data = IsingModel(variables=["a", "b"], couplings={("a", "b"): 3.0}).to_dict()
        assert data["couplings"] == {"a,b": 3.0}
