"""Bell-state example execution test (9-D compatibility canary).

Runs the declarative H + CNOT program end to end on the local
statevector backend with a fixed seed and asserts the entanglement
signature structurally (keys, totals) so the test stays robust across
MicroQuantum patch releases while still catching engine drift.
"""

from __future__ import annotations

import pytest

from quantsmind.quantum import QuantumExperiment, QuantumProgram
from quantsmind.quantum.bridge import build_circuit, validate_program


class TestBellStateExample:
    def test_program_validates_cleanly(self) -> None:
        program = QuantumProgram.bell_state()
        assert program.num_qubits == 2
        assert program.gate_names == ["h", "cx"]
        assert validate_program(program) == []

    def test_circuit_builds(self) -> None:
        pytest.importorskip("microquantum")
        circuit = build_circuit(QuantumProgram.bell_state())
        assert type(circuit).__name__ == "QuantumCircuit"

    def test_seeded_execution_shows_entanglement(self) -> None:
        pytest.importorskip("microquantum")
        experiment = QuantumExperiment(
            QuantumProgram.bell_state(),
            backend="statevector",
            shots=1024,
            seed=42,
        )
        result = experiment.run()
        assert result.success is True
        assert result.program_name == "bell"
        assert set(result.counts) <= {"00", "11"}
        assert set(result.counts) == {"00", "11"}
        assert sum(result.counts.values()) == 1024
        assert result.provenance["backend_requested"] == "statevector"
        assert result.num_qubits == 2
        statevector = result.statevector
        assert statevector is not None
        assert abs(sum(abs(a) ** 2 for a in statevector) - 1.0) < 1e-9
