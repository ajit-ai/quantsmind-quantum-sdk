"""
Algebra Package

This package provides algebra engine functionality for the QuantsMind SDK.

Purpose
-------
Provide comprehensive algebra operations including polynomial manipulation,
linear algebra operations, and matrix computations.

Modules
-------
- polynomial: Polynomial and PolynomialSolver
- linear_algebra: Matrix, Vector, Tensor, SparseMatrix
"""

from __future__ import annotations

from quantsmind.algebra.linear_algebra import Matrix, SparseMatrix, Tensor, Vector
from quantsmind.algebra.polynomial import Polynomial, PolynomialSolver

__all__: list[str] = [
    "Polynomial",
    "PolynomialSolver",
    "Matrix",
    "Vector",
    "Tensor",
    "SparseMatrix",
]
