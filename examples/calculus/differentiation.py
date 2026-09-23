"""Numerical differentiation: Jacobian of a two-output map.

Feature: `Differentiator` from ``quantsmind.calculus``.
Purpose: show finite-difference Jacobians with no dependencies.
Input: f(x) = [x0^2, x0*x1] at (1, 2).
Processing: central differences per output row.
Output: [[2, 0], [2, 1]] up to differencing tolerance.
Meaning: the exact Jacobian, recovered numerically.

Run from the repository root::

    python examples/calculus/differentiation.py
"""

from __future__ import annotations

from quantsmind.calculus.differentiation import Differentiator


def main() -> None:
    jacobian = Differentiator().jacobian(lambda x: [x[0] ** 2, x[0] * x[1]], [1.0, 2.0])
    for row in jacobian:
        print([round(value, 3) for value in row])


if __name__ == "__main__":
    main()
