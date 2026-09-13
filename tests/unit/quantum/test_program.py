"""Unit tests for the declarative QuantumProgram / GateSpec layer."""

from __future__ import annotations

import pytest

from quantsmind.quantum import GateSpec, QuantumProgram


class TestGateSpec:
    def test_from_tuple(self) -> None:
        spec = GateSpec.from_tuple("cx", [0, 1])
        assert spec.name == "cx"
        assert spec.qubits == (0, 1)
        assert spec.params == ()

    def test_empty_name_rejected(self) -> None:
        with pytest.raises(ValueError):
            GateSpec("", (0,))

    def test_empty_qubits_rejected(self) -> None:
        with pytest.raises(ValueError):
            GateSpec("h", ())

    def test_negative_qubit_rejected(self) -> None:
        with pytest.raises(ValueError):
            GateSpec("h", (-1,))

    def test_to_dict(self) -> None:
        spec = GateSpec.from_tuple("rx", [2], 0.5)
        assert spec.to_dict() == {"name": "rx", "qubits": [2], "params": [0.5]}


class TestQuantumProgram:
    def test_default_construction(self) -> None:
        program = QuantumProgram(2)
        assert program.num_qubits == 2
        assert program.num_operations == 0
        assert program.name == "program"

    def test_zero_qubits_rejected(self) -> None:
        with pytest.raises(ValueError):
            QuantumProgram(0)

    def test_out_of_range_qubit_rejected_at_init(self) -> None:
        with pytest.raises(ValueError):
            QuantumProgram(1, [GateSpec("h", (1,))])

    def test_fluent_add(self) -> None:
        program = QuantumProgram(2).add("h", [0]).add("cx", [0, 1])
        assert program.gate_names == ["h", "cx"]
        assert program.num_operations == 2

    def test_add_gate_validates_range(self) -> None:
        program = QuantumProgram(2)
        with pytest.raises(ValueError):
            program.add_gate(GateSpec("h", (5,)))

    def test_bell_state_convenience(self) -> None:
        program = QuantumProgram.bell_state()
        assert program.num_qubits == 2
        assert program.gate_names == ["h", "cx"]

    def test_serialization_roundtrip(self) -> None:
        program = (
            QuantumProgram(2, name="test", metadata={"tag": "x"}).add("h", [0]).add("cx", [0, 1])
        )
        restored = QuantumProgram.from_dict(program.to_dict())
        assert restored == program
