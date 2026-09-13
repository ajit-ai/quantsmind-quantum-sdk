"""Tests for MicroQuantum algorithm delegation."""

from __future__ import annotations

import pytest

from quantsmind.quantum import (
    available_algorithms,
    resolve_algorithm,
    run_algorithm,
)


class TestAlgorithmDelegation:
    def test_available_algorithms_are_unique_and_sorted(self) -> None:
        algorithms = available_algorithms()
        assert algorithms == sorted(algorithms)
        assert len(algorithms) == len(set(algorithms))
        assert "grover" in algorithms
        assert "vqe" in algorithms

    def test_resolve_algorithm_returns_microquantum_class(self) -> None:
        cls = resolve_algorithm("grover")
        assert cls.__module__.startswith("microquantum")
        assert cls.__name__ == "GroverSearch"

    def test_resolve_algorithm_alias(self) -> None:
        assert resolve_algorithm("adapt-vqe") is resolve_algorithm("adapt_vqe")

    def test_resolve_unknown_algorithm_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown algorithm"):
            resolve_algorithm("not_an_algorithm")

    def test_run_grover_delegates_to_microquantum(self) -> None:
        result = run_algorithm("grover", num_qubits=3, target=5)
        assert result.__class__.__name__ == "GroverResult"
        assert result.most_probable == 5
        assert result.success_probability > 0.9

    def test_run_algorithm_returns_native_result(self) -> None:
        result = run_algorithm("grover", num_qubits=2, target=1)
        assert hasattr(result, "to_dict")
