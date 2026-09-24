"""Unit tests for quantsmind.algebra polynomials."""

from __future__ import annotations

from quantsmind.algebra import Polynomial


class TestPolynomial:
    def test_evaluate_and_degree(self) -> None:
        poly = Polynomial("p", [1.0, 2.0, 3.0])
        assert poly.evaluate(2.0) == 17.0
        assert poly.degree() == 2

    def test_derivative(self) -> None:
        poly = Polynomial("p", [1.0, 2.0, 3.0])
        assert list(poly.derivative().coefficients) == [2.0, 6.0]
