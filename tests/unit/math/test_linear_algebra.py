"""Unit tests for math linear-algebra value objects."""

from __future__ import annotations

from quantsmind.math.linear_algebra.matrix import DenseMatrix
from quantsmind.math.linear_algebra.vector import CoordinateVector


class TestVector:
    def test_dot_and_magnitude(self) -> None:
        left = CoordinateVector([1.0, 2.0, 3.0])
        right = CoordinateVector([4.0, 5.0, 6.0])
        assert left.dot(right) == 32.0
        assert left.magnitude() == 3.7416573867739413

    def test_cross(self) -> None:
        left = CoordinateVector([1.0, 2.0, 3.0])
        right = CoordinateVector([4.0, 5.0, 6.0])
        assert list(left.cross(right).data) == [-3.0, 6.0, -3.0]


class TestMatrix:
    def test_determinant(self) -> None:
        matrix = DenseMatrix([[1.0, 2.0], [3.0, 4.0]])
        assert matrix.determinant() == -2.0
        assert matrix.is_square_matrix() is True
