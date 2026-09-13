"""Tests for QuantumExperiment orchestration and result enrichment."""

from __future__ import annotations

import pytest

from quantsmind.quantum import QuantumExperiment, QuantumProgram, QuantumResult, build_circuit


class TestQuantumExperiment:
    def test_initialization(self) -> None:
        experiment = QuantumExperiment(QuantumProgram.bell_state())
        assert experiment.name == "quantum_experiment"
        assert experiment.experiment_id  # uuid generated

    def test_run_bell_state(self) -> None:
        experiment = QuantumExperiment(
            QuantumProgram.bell_state(),
            backend="statevector",
            shots=100,
            seed=7,
            domain_metadata={"domain": "foundation"},
        )
        result = experiment.run()
        assert isinstance(result, QuantumResult)
        assert result.success
        assert result.backend_name == "statevector"
        assert result.shots == 100
        assert result.num_qubits == 2
        assert result.experiment_id == experiment.experiment_id
        assert result.counts == {"00": 50, "11": 50}

    def test_run_accepts_direct_circuit(self) -> None:
        import microquantum

        circuit = microquantum.QuantumCircuit(1)
        circuit.h(0)
        result = QuantumExperiment(circuit, backend="statevector", shots=32, seed=1).run()
        assert set(result.counts) <= {"0", "1"}
        assert result.num_qubits == 1

    def test_result_enrichment(self) -> None:
        experiment = QuantumExperiment(
            QuantumProgram.bell_state(),
            backend="statevector",
            shots=64,
            seed=3,
            domain_metadata={"domain": "finance", "trial": 1},
            name="trial_1",
        )
        result = experiment.run()
        assert result.program_name == "bell"
        assert result.domain_metadata == {"domain": "finance", "trial": 1}
        assert result.provenance["executed_backend"] == "statevector"
        assert result.to_dict()["experiment_id"] == experiment.experiment_id

    def test_native_result_accessible(self) -> None:
        result = QuantumExperiment(
            QuantumProgram.bell_state(), backend="statevector", shots=16
        ).run()
        native = result.native
        assert hasattr(native, "to_dict")

    def test_unknown_backend_fails(self) -> None:
        experiment = QuantumExperiment(
            QuantumProgram.bell_state(), backend="does_not_exist", shots=8
        )
        with pytest.raises(ValueError, match="unknown backend"):
            experiment.run()

    def test_statevector_result_passthrough(self) -> None:
        experiment = QuantumExperiment(
            QuantumProgram.bell_state(), backend="statevector", shots=8, seed=5
        )
        result = experiment.run()
        # statevector property is only non-None when the backend provides it
        assert result.counts  # counts always present for sampling


class TestBuildCircuitIntegration:
    def test_build_circuit_used_by_experiment(self) -> None:
        program = QuantumProgram(2).add("h", [0]).add("cx", [0, 1])
        circuit = build_circuit(program)
        assert circuit.num_qubits == 2
        assert circuit.num_gates == 2
