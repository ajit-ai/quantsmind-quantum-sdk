"""Unit tests for numerical differentiation."""

from __future__ import annotations

from quantsmind.calculus.differentiation import Differentiator


class TestJacobian:
    def test_quadratic_bilinear(self) -> None:
        diff = Differentiator()
        jac = diff.jacobian(lambda x: [x[0] ** 2, x[0] * x[1]], [1.0, 2.0])
        assert abs(jac[0][0] - 2.0) < 1e-4
        assert abs(jac[0][1] - 0.0) < 1e-4
        assert abs(jac[1][0] - 2.0) < 1e-4
        assert abs(jac[1][1] - 1.0) < 1e-4


class TestHessian:
    def test_sum_of_squares(self) -> None:
        diff = Differentiator()
        hess = diff.hessian(lambda x: x[0] ** 2 + x[1] ** 2, [1.0, 2.0])
        assert abs(hess[0][0] - 2.0) < 1e-2
        assert abs(hess[1][1] - 2.0) < 1e-2
        assert abs(hess[0][1]) < 1e-2
