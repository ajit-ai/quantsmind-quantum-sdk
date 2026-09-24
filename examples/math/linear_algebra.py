"""Linear algebra: dot products, norms, and determinants.

Feature: vector/matrix value objects from ``quantsmind.math``.
Purpose: show exact small-matrix math with no dependencies.
Input: v = [1, 2, 3], w = [4, 5, 6], M = [[1, 2], [3, 4]].
Processing: dot, magnitude, cross, determinant.
Output: 32.0, ~3.742, [-3, 6, -3], -2.0.
Meaning: the primitives other domains build on, verified exactly.

Run from the repository root::

    python examples/math/linear_algebra.py
"""

from __future__ import annotations

from quantsmind.math.linear_algebra.matrix import DenseMatrix
from quantsmind.math.linear_algebra.vector import CoordinateVector


def main() -> None:
    left = CoordinateVector([1.0, 2.0, 3.0])
    right = CoordinateVector([4.0, 5.0, 6.0])
    print(f"dot: {left.dot(right)}")
    print(f"|v|: {left.magnitude():.3f}")
    print(f"cross: {list(left.cross(right).data)}")
    matrix = DenseMatrix([[1.0, 2.0], [3.0, 4.0]])
    print(f"det: {matrix.determinant()}")


if __name__ == "__main__":
    main()
