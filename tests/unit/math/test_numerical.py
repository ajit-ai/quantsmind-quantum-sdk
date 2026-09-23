"""Unit tests for quantsmind.math.numerical root finding."""

from __future__ import annotations

from quantsmind.math.numerical import NumericalSolver


class TestNewtonRaphson:
    """The derivative evaluation must call the objective, not an undefined name."""

    def test_converges_to_sqrt2(self) -> None:
        solver = NumericalSolver()
        root = solver._newton_raphson(lambda x: x * x - 2.0, 1.0)
        assert abs(root - 1.41421356) < 1e-6
