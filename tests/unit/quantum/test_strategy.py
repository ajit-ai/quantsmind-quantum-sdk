"""Tests for the QMQ-01 strategy layer."""

from __future__ import annotations

import pytest

from quantsmind.quantum import (
    ComputationStrategy,
    QuantumProblem,
    StrategySelector,
    Variable,
)


class TestComputationStrategy:
    def test_parse(self) -> None:
        assert ComputationStrategy.parse("hybrid") is ComputationStrategy.HYBRID
        assert ComputationStrategy.parse("HYBRID") is ComputationStrategy.HYBRID
        assert ComputationStrategy.parse("quantum-inspired") is ComputationStrategy.QUANTUM_INSPIRED
        assert ComputationStrategy.parse("quantum inspired") is ComputationStrategy.QUANTUM_INSPIRED
        assert ComputationStrategy.parse(ComputationStrategy.AUTO) is ComputationStrategy.AUTO
        with pytest.raises(ValueError):
            ComputationStrategy.parse("nope")

    def test_values(self) -> None:
        assert {s.value for s in ComputationStrategy} == {
            "classical",
            "quantum",
            "hybrid",
            "quantum_inspired",
            "auto",
        }

    def test_uses_quantum_runtime(self) -> None:
        assert ComputationStrategy.QUANTUM.uses_quantum_runtime
        assert ComputationStrategy.HYBRID.uses_quantum_runtime
        assert not ComputationStrategy.CLASSICAL.uses_quantum_runtime
        assert not ComputationStrategy.QUANTUM_INSPIRED.uses_quantum_runtime
        assert not ComputationStrategy.AUTO.uses_quantum_runtime


class TestStrategySelector:
    def _problem(self, size: int, preferred: str | None = None) -> QuantumProblem:
        problem = QuantumProblem("p", domain="optimization", preferred_strategy=preferred)
        for i in range(size):
            problem.add_variable(Variable.binary(f"x{i}"))
        return problem

    def test_validation(self) -> None:
        with pytest.raises(ValueError):
            StrategySelector(quantum_attempt_threshold=0)
        with pytest.raises(ValueError):
            StrategySelector(quantum_attempt_threshold=10, quantum_inspired_threshold=5)

    def test_explicit_preference_honoured(self) -> None:
        selector = StrategySelector()
        assert selector.select(self._problem(2, "quantum")) is ComputationStrategy.QUANTUM
        assert selector.select(self._problem(2, "hybrid")) is ComputationStrategy.HYBRID
        assert (
            selector.select(self._problem(2, "quantum_inspired"))
            is ComputationStrategy.QUANTUM_INSPIRED
        )
        assert selector.select(self._problem(2, "classical")) is ComputationStrategy.CLASSICAL

    def test_explicit_quantum_downgraded_without_backend(self) -> None:
        selector = StrategySelector()
        assert (
            selector.select(
                self._problem(2, "quantum"),
                backend_available=False,
            )
            is ComputationStrategy.CLASSICAL
        )
        assert (
            selector.select(
                self._problem(2, "hybrid"),
                available_algorithms=set(),
            )
            is ComputationStrategy.CLASSICAL
        )
        # classical preference never downgrades
        assert (
            selector.select(self._problem(2, "classical"), backend_available=False)
            is ComputationStrategy.CLASSICAL
        )

    def test_auto_without_backend_is_classical(self) -> None:
        selector = StrategySelector()
        assert (
            selector.select(self._problem(2), backend_available=False)
            is ComputationStrategy.CLASSICAL
        )

    def test_auto_size_rules(self) -> None:
        selector = StrategySelector(quantum_attempt_threshold=5, quantum_inspired_threshold=20)
        assert selector.select(self._problem(3)) is ComputationStrategy.HYBRID
        assert selector.select(self._problem(10)) is ComputationStrategy.QUANTUM_INSPIRED
        assert selector.select(self._problem(30)) is ComputationStrategy.CLASSICAL

    def test_auto_international_border(self) -> None:
        selector = StrategySelector(quantum_attempt_threshold=5, quantum_inspired_threshold=20)
        assert selector.select(self._problem(5)) is ComputationStrategy.HYBRID
        assert selector.select(self._problem(20)) is ComputationStrategy.QUANTUM_INSPIRED
        assert selector.select(self._problem(21)) is ComputationStrategy.CLASSICAL

    def test_quantum_suitable_flag_false(self) -> None:
        selector = StrategySelector(quantum_attempt_threshold=100)
        problem = self._problem(2)
        problem.metadata["quantum_suitable"] = False
        assert selector.select(problem) is ComputationStrategy.CLASSICAL

    def test_quantum_enabled_master_switch(self) -> None:
        selector = StrategySelector(quantum_enabled=False)
        assert selector.select(self._problem(2, "quantum")) is ComputationStrategy.CLASSICAL
        assert selector.select(self._problem(2)) is ComputationStrategy.CLASSICAL

    def test_explain(self) -> None:
        selector = StrategySelector()
        explanation = selector.explain(self._problem(2, "hybrid"))
        assert explanation["strategy"] is ComputationStrategy.HYBRID
        assert "preferred_strategy=HYBRID" in explanation["reason"]


class TestStrategySelectorClassicalUniverse:
    """AUTHORITY: hangs microquantum availability so AUTO sees no runtime."""

    @pytest.fixture(autouse=True)
    def _no_microquantum(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import quantsmind.quantum.strategy.selector as selector_module

        monkeypatch.setattr(selector_module, "microquantum_available", lambda: False)

    def test_auto_without_mq_is_classical(self) -> None:
        selector = StrategySelector()
        problem = QuantumProblem("p", domain="optimization")
        problem.add_variable(Variable.binary("x0"))
        assert selector.select(problem) is ComputationStrategy.CLASSICAL
