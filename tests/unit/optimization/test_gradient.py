"""Unit tests for gradient-based optimization."""

from __future__ import annotations

from quantsmind.optimization.gradient_optimizer import AdamOptimizer


class TestAdam:
    def test_descends_quadratic(self) -> None:
        optimizer = AdamOptimizer()
        result, history = optimizer.optimize(lambda x: x**2, lambda x: 2 * x, 1.0)
        assert result < 1.0
        assert len(history) > 1
        assert history[-1] <= history[0]
