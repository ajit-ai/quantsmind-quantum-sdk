"""Tests for QuantumProgram -> MicroQuantum circuit translation (the bridge)."""

from __future__ import annotations

import pytest

from quantsmind.quantum import (
    GateParamError,
    GateSpec,
    QuantumProgram,
    UnknownGateError,
    build_circuit,
    validate_program,
)


@pytest.fixture
def microquantum():
    import microquantum

    return microquantum


class TestBuildCircuit:
    def test_bell_state_translation(self, microquantum) -> None:
        circuit = build_circuit(QuantumProgram.bell_state())
        assert isinstance(circuit, microquantum.QuantumCircuit)
        assert circuit.num_qubits == 2
        assert circuit.num_gates == 2
        assert circuit.depth == 2

    def test_parameterized_gate(self, microquantum) -> None:
        program = QuantumProgram(1).add("rx", [0], 0.5)
        circuit = build_circuit(program)
        assert circuit.num_gates == 1

    def test_custom_matrix_through_operator_factory(self, microquantum) -> None:
        # 'swap' maps to MicroQuantum Operator.SWAP()
        program = QuantumProgram(2).add("swap", [0, 1])
        circuit = build_circuit(program)
        assert circuit.num_gates == 1

    def test_unknown_gate_raises(self, microquantum) -> None:
        program = QuantumProgram(1, [GateSpec("nope", (0,))])
        with pytest.raises(UnknownGateError):
            build_circuit(program)

    def test_wrong_param_count_raises(self, microquantum) -> None:
        program = QuantumProgram(1, [GateSpec("h", (0,), (0.5,))])
        with pytest.raises(GateParamError):
            build_circuit(program)

    def test_missing_param_raises(self, microquantum) -> None:
        program = QuantumProgram(1, [GateSpec("rx", (0,))])
        with pytest.raises(GateParamError):
            build_circuit(program)

    def test_wrong_qubit_count_raises(self, microquantum) -> None:
        program = QuantumProgram(2, [GateSpec("cx", (0,))])
        with pytest.raises(ValueError, match="expects exactly 2 qubits"):
            build_circuit(program)


class TestValidateProgram:
    def test_valid_program_no_errors(self) -> None:
        assert validate_program(QuantumProgram.bell_state()) == []

    def test_unknown_gate_reported(self) -> None:
        errors = validate_program(QuantumProgram(1, [GateSpec("nope", (0,))]))
        assert any("nope" in e for e in errors)

    def test_param_mismatch_reported(self) -> None:
        errors = validate_program(QuantumProgram(1, [GateSpec("h", (0,), (1.0,))]))
        assert any("parameter" in e for e in errors)

    def test_cx_two_qubits_accepted(self) -> None:
        assert validate_program(QuantumProgram(2).add("cx", [0, 1])) == []
