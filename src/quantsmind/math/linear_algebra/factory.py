"""
Matrix Factory Module

This module provides factory functions and classes for creating matrix instances.
Factories provide convenient creation methods for matrices with common configurations.

Purpose
-------
Provide factory functions and classes for creating matrix instances.

Scientific Meaning
------------------
Factories simplify matrix creation in scientific computing applications,
ensuring consistent initialization and reducing boilerplate code.

Responsibilities
----------------
- Provide factory functions for common matrices
- Support builder patterns
- Enable matrix configuration
- Support custom factories

Dependencies
------------
typing (standard library)
quantsmind.math.linear_algebra.matrix (matrix classes)

Future Extensions
-----------------
- Configurable factories
- Factory composition
- Factory caching
"""

from __future__ import annotations

import logging

from quantsmind.math.linear_algebra.matrix import (
    DenseMatrix,
    DiagonalMatrix,
    IdentityMatrix,
    Matrix,
    OrthogonalMatrix,
    SparseMatrix,
    SymmetricMatrix,
)
from quantsmind.math.types import Scalar

logger = logging.getLogger(__name__)


class MatrixFactory:
    """Factory for creating Matrix instances.

    This class provides convenient methods for creating matrices with common configurations.

    Example:
        >>> factory = MatrixFactory()
        >>> matrix = factory.create_identity(3)
    """

    def create_matrix(self, data: list[list[Scalar]]) -> Matrix:
        """Create a generic Matrix instance.

        Args:
            data: Matrix data

        Returns:
            Matrix instance

        Example:
            >>> matrix = factory.create_matrix([[1.0, 2.0], [3.0, 4.0]])
        """
        return Matrix(data)

    def create_dense_matrix(self, data: list[list[Scalar]]) -> DenseMatrix:
        """Create a DenseMatrix instance.

        Args:
            data: Matrix data

        Returns:
            DenseMatrix instance

        Example:
            >>> matrix = factory.create_dense_matrix([[1.0, 2.0], [3.0, 4.0]])
        """
        return DenseMatrix(data)

    def create_sparse_matrix(self, data: list[list[Scalar]]) -> SparseMatrix:
        """Create a SparseMatrix instance.

        Args:
            data: Matrix data

        Returns:
            SparseMatrix instance

        Example:
            >>> matrix = factory.create_sparse_matrix([[0.0, 1.0], [0.0, 0.0]])
        """
        return SparseMatrix(data)

    def create_identity(self, size: int) -> IdentityMatrix:
        """Create an IdentityMatrix instance.

        Args:
            size: Size of the identity matrix

        Returns:
            IdentityMatrix instance

        Example:
            >>> matrix = factory.create_identity(3)
        """
        return IdentityMatrix(size)

    def create_diagonal(self, diagonal: list[Scalar]) -> DiagonalMatrix:
        """Create a DiagonalMatrix instance.

        Args:
            diagonal: Diagonal elements

        Returns:
            DiagonalMatrix instance

        Example:
            >>> matrix = factory.create_diagonal([1.0, 2.0, 3.0])
        """
        return DiagonalMatrix(diagonal)

    def create_symmetric(self, data: list[list[Scalar]]) -> SymmetricMatrix:
        """Create a SymmetricMatrix instance.

        Args:
            data: Matrix data (must be symmetric)

        Returns:
            SymmetricMatrix instance

        Raises:
            ValueError: If data is not symmetric

        Example:
            >>> matrix = factory.create_symmetric([[1.0, 2.0], [2.0, 1.0]])
        """
        return SymmetricMatrix(data)

    def create_orthogonal(self, data: list[list[Scalar]]) -> OrthogonalMatrix:
        """Create an OrthogonalMatrix instance.

        Args:
            data: Matrix data (must be orthogonal)

        Returns:
            OrthogonalMatrix instance

        Raises:
            ValueError: If data is not orthogonal

        Example:
            >>> matrix = factory.create_orthogonal([[1.0, 0.0], [0.0, 1.0]])
        """
        return OrthogonalMatrix(data)

    def create_zeros(self, rows: int, cols: int) -> Matrix:
        """Create a zero matrix.

        Args:
            rows: Number of rows
            cols: Number of columns

        Returns:
            Zero matrix

        Example:
            >>> matrix = factory.create_zeros(3, 3)
        """
        data = [[0.0 for _ in range(cols)] for _ in range(rows)]
        return Matrix(data)

    def create_ones(self, rows: int, cols: int) -> Matrix:
        """Create a matrix of ones.

        Args:
            rows: Number of rows
            cols: Number of columns

        Returns:
            Matrix of ones

        Example:
            >>> matrix = factory.create_ones(3, 3)
        """
        data = [[1.0 for _ in range(cols)] for _ in range(rows)]
        return Matrix(data)

    def create_constant(self, rows: int, cols: int, value: Scalar) -> Matrix:
        """Create a constant matrix.

        Args:
            rows: Number of rows
            cols: Number of columns
            value: Constant value

        Returns:
            Constant matrix

        Example:
            >>> matrix = factory.create_constant(3, 3, 5.0)
        """
        data = [[value for _ in range(cols)] for _ in range(rows)]
        return Matrix(data)

    def create_random(self, rows: int, cols: int, min_val: Scalar = 0.0, max_val: Scalar = 1.0) -> Matrix:
        """Create a random matrix.

        Args:
            rows: Number of rows
            cols: Number of columns
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Random matrix

        Example:
            >>> matrix = factory.create_random(3, 3)
        """
        import random
        data = [[random.uniform(min_val, max_val) for _ in range(cols)] for _ in range(rows)]
        return Matrix(data)

    def create_from_diagonal(self, diagonal: list[Scalar]) -> Matrix:
        """Create a matrix from diagonal elements.

        Args:
            diagonal: Diagonal elements

        Returns:
            Diagonal matrix

        Example:
            >>> matrix = factory.create_from_diagonal([1.0, 2.0, 3.0])
        """
        return self.create_diagonal(diagonal)

    def create_block(self, blocks: list[list[Matrix]]) -> Matrix:
        """Create a block matrix from submatrices.

        Args:
            blocks: 2D list of submatrices

        Returns:
            Block matrix

        Example:
            >>> A = factory.create_identity(2)
            >>> B = factory.create_zeros(2, 2)
            >>> block = factory.create_block([[A, B], [B, A]])
        """
        # Calculate dimensions
        block_rows = len(blocks)
        block_cols = len(blocks[0])
        row_sizes = [blocks[i][0].rows for i in range(block_rows)]
        col_sizes = [blocks[0][j].cols for j in range(block_cols)]

        total_rows = sum(row_sizes)
        total_cols = sum(col_sizes)

        # Build block matrix
        data = [[0.0 for _ in range(total_cols)] for _ in range(total_rows)]
        row_offset = 0
        for i in range(block_rows):
            col_offset = 0
            for j in range(block_cols):
                block = blocks[i][j]
                for bi in range(block.rows):
                    for bj in range(block.cols):
                        data[row_offset + bi][col_offset + bj] = block[bi, bj]
                col_offset += col_sizes[j]
            row_offset += row_sizes[i]

        return Matrix(data)


# Export
__all__ = [
    "MatrixFactory",
]
