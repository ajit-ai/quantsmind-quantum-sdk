"""Tests for the QMQ-01 mapping layer (QuantumCircuitMapper)."""

from __future__ import annotations

import pytest

from quantsmind.quantum import (
    ComputationStrategy,
    MappingError,
    MappingResult,
    QuantumCircuitMapper,
    QuantumProgram,
)


class TestMappingResult:
    def test_to_dict(self) -> None:
        result = MappingResult(
            mapper="quantum_circuit",
            strategy=ComputationStrategy.HYBRID,
            source="program",
            target="circuit",
            steps=["validated program"],
            metadata={"num_qubits": 2},
        )
        data = result.to_dict()
        assert data["strategy"] == "hybrid"
        assert data["metadata"]["num_qubits"] == 2
        assert "payload" not in data


class TestQuantumCircuitMapper:
    def _mapper(self) -> QuantumCircuitMapper:
        return QuantumCircuitMapper()

    def test_map_valid_bell(self) -> None:
        result = self._mapper().map(
            QuantumProgram.bell_state(), strategy=ComputationStrategy.HYBRID
        )
        assert isinstance(result, MappingResult)
        assert result.mapper == "quantum_circuit"
        assert result.metadata["num_qubits"] == 2
        assert any("validated" in step for step in result.steps)

    def test_map_rejects_classical_strategy(self) -> None:
        with pytest.raises(MappingError, match="quantum strategy"):
            self._mapper().map(
                QuantumProgram.bell_state(),
                strategy=ComputationStrategy.CLASSICAL,
            )

    def test_map_rejects_invalid_program(self) -> None:
        program = QuantumProgram(1).add("nope", [0])
        with pytest.raises(MappingError, match="unknown gate"):
            self._mapper().map(program, strategy=ComputationStrategy.HYBRID)

    def test_build_produces_circuit(self) -> None:
        mapper = self._mapper()
        result = mapper.map(QuantumProgram.bell_state(), strategy=ComputationStrategy.HYBRID)
        circuit = mapper.build(result)
        assert circuit.num_qubits == 2

    def test_build_requires_prior_map(self) -> None:
        with pytest.raises(MappingError, match="map\\(\\) must be called"):
            self._mapper().build(
                MappingResult(
                    mapper="quantum_circuit",
                    strategy=ComputationStrategy.HYBRID,
                    source="program",
                    target="circuit",
                )
            )

    def test_build_rejects_foreign_result(self) -> None:
        mapper = self._mapper()
        mapper.map(QuantumProgram.bell_state(), strategy=ComputationStrategy.HYBRID)
        foreign = MappingResult(
            mapper="other",
            strategy=ComputationStrategy.HYBRID,
            source="program",
            target="circuit",
        )
        with pytest.raises(MappingError, match="produced by"):
            mapper.build(foreign)


class TestMappingDelegatesToBridge:
    """AUTHORITY: the mapper must not re-implement gate/circuit logic."""

    def test_validate_delegated_to_bridge(self) -> None:
        import inspect

        import quantsmind.quantum.mapping.mapper as mapper_module
        from quantsmind.quantum.bridge import validate_program

        source = inspect.getsource(mapper_module)
        assert "from quantsmind.quantum.bridge import" in source
        assert mapper_module.validate_program is validate_program
        # no gate table is re-implemented in the mapper
        assert "_GATE_FACTORIES" not in source
