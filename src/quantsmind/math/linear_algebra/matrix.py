"""
Matrix Module

This module provides matrix operations for the Mathematics package.
Matrix represents a mathematical matrix with support for common operations.

Purpose
-------
Provide matrix operations for the Mathematics package.

Scientific Meaning
------------------
Matrix represents a mathematical matrix: linear transformations, quantum operators,
covariance matrices, adjacency matrices, or any other matrix quantity in scientific computing.

Responsibilities
----------------
- Support matrix creation
- Enable matrix operations
- Support matrix transformations
- Handle matrix validation

Dependencies
------------
math (standard library)
typing (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)
quantsmind.math.utilities (utility functions)
quantsmind.math.validation (validation functions)

Future Extensions
-----------------
- GPU-accelerated operations
- Sparse matrices
- Complex matrix operations
- Matrix views
"""

from __future__ import annotations

import logging
from typing import Any

from quantsmind.math.exceptions import (
    DimensionError,
    DivisionByZeroError,
    SingularMatrixError,
)
from quantsmind.math.exceptions import (
    IndexError as MathIndexError,
)
from quantsmind.math.types import Scalar, Shape
from quantsmind.math.utilities import is_square
from quantsmind.math.validation import validate_matrix

logger = logging.getLogger(__name__)


class Matrix:
    """Concrete implementation of a mathematical matrix.

    This class provides a comprehensive matrix representation with support for
    common matrix operations including addition, subtraction, multiplication,
    transposition, determinant, inverse, and decomposition.

    Scientific Meaning
    ------------------
    In scientific computing, matrices represent linear transformations,
    quantum operators, covariance matrices, adjacency matrices, and other
    fundamental mathematical structures.

    Attributes:
        _data: Matrix data (list of lists)
        _rows: Number of rows
        _cols: Number of columns

    Example:
        >>> m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        >>> print(f"Shape: {m.shape}")
    """

    def __init__(self, data: list[list[Scalar]]) -> None:
        """Initialize a Matrix.

        Args:
            data: Matrix data as list of lists

        Raises:
            ValueError: If data is invalid

        Example:
            >>> m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        """
        is_valid, errors = validate_matrix(data)
        if not is_valid:
            raise ValueError(f"Invalid matrix data: {errors}")

        self._data: list[list[Scalar]] = [list(row) for row in data]
        self._rows: int = len(self._data)
        self._cols: int = len(self._data[0]) if self._data else 0
        logger.debug(f"Created matrix of shape {self.shape}")

    @property
    def shape(self) -> Shape:
        """Get the matrix shape.

        Returns:
            Shape tuple (rows, cols)

        Example:
            >>> print(f"Shape: {matrix.shape}")
        """
        return (self._rows, self._cols)

    @property
    def data(self) -> list[list[Scalar]]:
        """Get the matrix data.

        Returns:
            Matrix data

        Example:
            >>> print(f"Data: {matrix.data}")
        """
        return [row.copy() for row in self._data]

    @property
    def rows(self) -> int:
        """Get the number of rows.

        Returns:
            Number of rows

        Example:
            >>> print(f"Rows: {matrix.rows}")
        """
        return self._rows

    @property
    def cols(self) -> int:
        """Get the number of columns.

        Returns:
            Number of columns

        Example:
            >>> print(f"Cols: {matrix.cols}")
        """
        return self._cols

    def __getitem__(self, index: int | tuple[int, int]) -> Scalar | list[Scalar]:
        """Get matrix element or row by index.

        Args:
            index: Row index or (row, col) tuple

        Returns:
            Element value or row

        Raises:
            IndexError: If index is out of bounds

        Example:
            >>> value = matrix[0, 0]
            >>> row = matrix[0]
        """
        if isinstance(index, tuple):
            row_idx, col_idx = index
            if row_idx < 0 or row_idx >= self._rows or col_idx < 0 or col_idx >= self._cols:
                raise MathIndexError(f"Index ({row_idx}, {col_idx}) out of bounds for shape {self.shape}")
            return self._data[row_idx][col_idx]
        else:
            if index < 0 or index >= self._rows:
                raise MathIndexError(f"Row index {index} out of bounds for {self._rows} rows")
            return self._data[index].copy()

    def __setitem__(self, index: tuple[int, int], value: Scalar) -> None:
        """Set matrix element by index.

        Args:
            index: (row, col) tuple
            value: Element value

        Raises:
            IndexError: If index is out of bounds

        Example:
            >>> matrix[0, 0] = 5.0
        """
        row_idx, col_idx = index
        if row_idx < 0 or row_idx >= self._rows or col_idx < 0 or col_idx >= self._cols:
            raise MathIndexError(f"Index ({row_idx}, {col_idx}) out of bounds for shape {self.shape}")
        self._data[row_idx][col_idx] = value

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(matrix)
        """
        return f"Matrix({self._data})"

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(matrix)
        """
        return "\n".join("[" + ", ".join(f"{x:8.4f}" for x in row) + "]" for row in self._data)

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> matrix1 == matrix2
        """
        if not isinstance(other, Matrix):
            return False
        if self.shape != other.shape:
            return False
        for i in range(self._rows):
            for j in range(self._cols):
                if abs(self._data[i][j] - other._data[i][j]) > 1e-10:
                    return False
        return True

    def __hash__(self) -> int:
        """Return hash.

        Returns:
            Hash value

        Example:
            >>> hash(matrix)
        """
        return hash(tuple(tuple(row) for row in self._data))

    def __add__(self, other: Matrix) -> Matrix:
        """Add two matrices.

        Args:
            other: Other matrix

        Returns:
            Sum matrix

        Raises:
            DimensionError: If shapes don't match

        Example:
            >>> result = matrix1 + matrix2
        """
        if self.shape != other.shape:
            raise DimensionError(f"Shape mismatch: {self.shape} vs {other.shape}")
        return Matrix([[self._data[i][j] + other._data[i][j] for j in range(self._cols)] for i in range(self._rows)])

    def __sub__(self, other: Matrix) -> Matrix:
        """Subtract two matrices.

        Args:
            other: Other matrix

        Returns:
            Difference matrix

        Raises:
            DimensionError: If shapes don't match

        Example:
            >>> result = matrix1 - matrix2
        """
        if self.shape != other.shape:
            raise DimensionError(f"Shape mismatch: {self.shape} vs {other.shape}")
        return Matrix([[self._data[i][j] - other._data[i][j] for j in range(self._cols)] for i in range(self._rows)])

    def __mul__(self, other: Matrix | Scalar) -> Matrix:
        """Multiply matrix by matrix or scalar.

        Args:
            other: Matrix or scalar

        Returns:
            Product matrix

        Raises:
            DimensionError: If dimensions are incompatible

        Example:
            >>> result = matrix1 * matrix2
            >>> result = matrix * 2.0
        """
        if isinstance(other, Matrix):
            if self._cols != other._rows:
                raise DimensionError(f"Cannot multiply {self.shape} by {other.shape}")
            result = [[0.0] * other._cols for _ in range(self._rows)]
            for i in range(self._rows):
                for j in range(other._cols):
                    for k in range(self._cols):
                        result[i][j] += self._data[i][k] * other._data[k][j]
            return Matrix(result)
        else:
            return Matrix([[x * other for x in row] for row in self._data])

    def __rmul__(self, scalar: Scalar) -> Matrix:
        """Multiply scalar by matrix.

        Args:
            scalar: Scalar value

        Returns:
            Scaled matrix

        Example:
            >>> result = 2.0 * matrix
        """
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Scalar) -> Matrix:
        """Divide matrix by scalar.

        Args:
            scalar: Scalar value

        Returns:
            Scaled matrix

        Raises:
            DivisionByZeroError: If scalar is zero

        Example:
            >>> result = matrix / 2.0
        """
        if scalar == 0:
            raise DivisionByZeroError("Cannot divide by zero")
        return Matrix([[x / scalar for x in row] for row in self._data])

    def transpose(self) -> Matrix:
        """Transpose the matrix.

        Returns:
            Transposed matrix

        Example:
            >>> transposed = matrix.transpose()
        """
        return Matrix([[self._data[j][i] for j in range(self._rows)] for i in range(self._cols)])

    def trace(self) -> float:
        """Calculate the trace of the matrix.

        Returns:
            Trace (sum of diagonal elements)

        Raises:
            ValueError: If matrix is not square

        Example:
            >>> tr = matrix.trace()
        """
        if not is_square(self._data):
            raise ValueError("Matrix must be square")
        return sum(self._data[i][i] for i in range(self._rows))

    def determinant(self) -> float:
        """Calculate the determinant of the matrix.

        Returns:
            Determinant

        Raises:
            ValueError: If matrix is not square

        Example:
            >>> det = matrix.determinant()
        """
        if not is_square(self._data):
            raise ValueError("Matrix must be square")
        return self._determinant_recursive(self._data)

    def _determinant_recursive(self, matrix: list[list[Scalar]]) -> float:
        """Calculate determinant recursively (for small matrices).

        Args:
            matrix: Matrix data

        Returns:
            Determinant
        """
        n = len(matrix)
        if n == 1:
            return matrix[0][0]
        if n == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

        det = 0.0
        for j in range(n):
            minor = [[matrix[i][k] for k in range(n) if k != j] for i in range(1, n)]
            cofactor = ((-1) ** j) * matrix[0][j] * self._determinant_recursive(minor)
            det += cofactor
        return det

    def inverse(self) -> Matrix:
        """Calculate the inverse of the matrix.

        Returns:
            Inverse matrix

        Raises:
            ValueError: If matrix is not square
            SingularMatrixError: If matrix is singular

        Example:
            >>> inv = matrix.inverse()
        """
        if not is_square(self._data):
            raise ValueError("Matrix must be square")

        det = self.determinant()
        if abs(det) < 1e-10:
            raise SingularMatrixError("Matrix is singular, cannot compute inverse")

        n = self._rows
        if n == 1:
            return Matrix([[1.0 / self._data[0][0]]])
        if n == 2:
            inv_det = 1.0 / det
            return Matrix([
                [inv_det * self._data[1][1], inv_det * -self._data[0][1]],
                [inv_det * -self._data[1][0], inv_det * self._data[0][0]],
            ])

        # For larger matrices, use cofactor method (simplified)
        # In production, this should use LU decomposition
        raise NotImplementedError("Inverse for matrices larger than 2x2 not yet implemented")

    def is_square_matrix(self) -> bool:
        """Check if matrix is square.

        Returns:
            True if square, False otherwise

        Example:
            >>> if matrix.is_square_matrix():
            ...     print("Square matrix")
        """
        return self._rows == self._cols

    def is_symmetric(self, tolerance: float = 1e-10) -> bool:
        """Check if matrix is symmetric.

        Args:
            tolerance: Numerical tolerance

        Returns:
            True if symmetric, False otherwise

        Example:
            >>> if matrix.is_symmetric():
            ...     print("Symmetric matrix")
        """
        if not self.is_square_matrix():
            return False
        for i in range(self._rows):
            for j in range(i + 1, self._cols):
                if abs(self._data[i][j] - self._data[j][i]) > tolerance:
                    return False
        return True

    def is_diagonal(self, tolerance: float = 1e-10) -> bool:
        """Check if matrix is diagonal.

        Args:
            tolerance: Numerical tolerance

        Returns:
            True if diagonal, False otherwise

        Example:
            >>> if matrix.is_diagonal():
            ...     print("Diagonal matrix")
        """
        if not self.is_square_matrix():
            return False
        for i in range(self._rows):
            for j in range(self._cols):
                if i != j and abs(self._data[i][j]) > tolerance:
                    return False
        return True

    def to_list(self) -> list[list[Scalar]]:
        """Convert matrix to list.

        Returns:
            List representation

        Example:
            >>> data = matrix.to_list()
        """
        return [row.copy() for row in self._data]

    def copy(self) -> Matrix:
        """Create a copy of the matrix.

        Returns:
            Copy of matrix

        Example:
            >>> copy = matrix.copy()
        """
        return Matrix(self._data)


class DenseMatrix(Matrix):
    """A dense matrix with all elements stored explicitly.

    This class represents a dense matrix where all elements are stored
    in memory, suitable for small to medium-sized matrices.

    Example:
        >>> m = DenseMatrix([[1.0, 2.0], [3.0, 4.0]])
    """

    def __init__(self, data: list[list[Scalar]]) -> None:
        """Initialize a DenseMatrix.

        Args:
            data: Matrix data

        Example:
            >>> m = DenseMatrix([[1.0, 2.0], [3.0, 4.0]])
        """
        super().__init__(data)


class SparseMatrix(Matrix):
    """A sparse matrix with efficient storage for mostly-zero matrices.

    This class represents a sparse matrix using coordinate format (COO),
    suitable for matrices with many zero elements.

    Example:
        >>> m = SparseMatrix([[0.0, 1.0], [0.0, 0.0]])
    """

    def __init__(self, data: list[list[Scalar]]) -> None:
        """Initialize a SparseMatrix.

        Args:
            data: Matrix data

        Example:
            >>> m = SparseMatrix([[0.0, 1.0], [0.0, 0.0]])
        """
        super().__init__(data)
        self._non_zero_elements = self._find_non_zero_elements()

    def _find_non_zero_elements(self) -> list[tuple[int, int, Scalar]]:
        """Find non-zero elements.

        Returns:
            List of (row, col, value) tuples
        """
        elements = []
        for i in range(self._rows):
            for j in range(self._cols):
                if abs(self._data[i][j]) > 1e-10:
                    elements.append((i, j, self._data[i][j]))
        return elements

    @property
    def sparsity(self) -> float:
        """Calculate matrix sparsity.

        Returns:
            Fraction of zero elements

        Example:
            >>> print(f"Sparsity: {sparse_matrix.sparsity}")
        """
        total_elements = self._rows * self._cols
        non_zero_count = len(self._non_zero_elements)
        return 1.0 - (non_zero_count / total_elements)


class IdentityMatrix(Matrix):
    """An identity matrix (1s on diagonal, 0s elsewhere).

    This class represents an identity matrix, which is the multiplicative
    identity for square matrices.

    Example:
        >>> I = IdentityMatrix(3)
    """

    def __init__(self, size: int) -> None:
        """Initialize an IdentityMatrix.

        Args:
            size: Size of the identity matrix

        Example:
            >>> I = IdentityMatrix(3)
        """
        data = [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]
        super().__init__(data)


class DiagonalMatrix(Matrix):
    """A diagonal matrix (non-zero elements only on diagonal).

    This class represents a diagonal matrix, which is efficient for
    certain operations.

    Example:
        >>> D = DiagonalMatrix([1.0, 2.0, 3.0])
    """

    def __init__(self, diagonal: list[Scalar]) -> None:
        """Initialize a DiagonalMatrix.

        Args:
            diagonal: Diagonal elements

        Example:
            >>> D = DiagonalMatrix([1.0, 2.0, 3.0])
        """
        size = len(diagonal)
        data = [[diagonal[i] if i == j else 0.0 for j in range(size)] for i in range(size)]
        super().__init__(data)
        self._diagonal = diagonal.copy()

    @property
    def diagonal_elements(self) -> list[Scalar]:
        """Get diagonal elements.

        Returns:
            Diagonal elements

        Example:
            >>> print(f"Diagonal: {diagonal_matrix.diagonal_elements}")
        """
        return self._diagonal.copy()


class SymmetricMatrix(Matrix):
    """A symmetric matrix (equal to its transpose).

    This class represents a symmetric matrix, which has the property
    A = A^T.

    Example:
        >>> S = SymmetricMatrix([[1.0, 2.0], [2.0, 1.0]])
    """

    def __init__(self, data: list[list[Scalar]]) -> None:
        """Initialize a SymmetricMatrix.

        Args:
            data: Matrix data (must be symmetric)

        Raises:
            ValueError: If data is not symmetric

        Example:
            >>> S = SymmetricMatrix([[1.0, 2.0], [2.0, 1.0]])
        """
        super().__init__(data)
        if not self.is_symmetric():
            raise ValueError("Matrix is not symmetric")


class OrthogonalMatrix(Matrix):
    """An orthogonal matrix (columns are orthonormal).

    This class represents an orthogonal matrix, which has the property
    A^T * A = I.

    Example:
        >>> Q = OrthogonalMatrix([[1.0, 0.0], [0.0, 1.0]])
    """

    def __init__(self, data: list[list[Scalar]]) -> None:
        """Initialize an OrthogonalMatrix.

        Args:
            data: Matrix data (must be orthogonal)

        Raises:
            ValueError: If data is not orthogonal

        Example:
            >>> Q = OrthogonalMatrix([[1.0, 0.0], [0.0, 1.0]])
        """
        super().__init__(data)
        if not self._is_orthogonal():
            raise ValueError("Matrix is not orthogonal")

    def _is_orthogonal(self, tolerance: float = 1e-10) -> bool:
        """Check if matrix is orthogonal.

        Args:
            tolerance: Numerical tolerance

        Returns:
            True if orthogonal, False otherwise
        """
        if not self.is_square_matrix():
            return False
        product = self.transpose() * self
        identity = IdentityMatrix(self._rows)
        return product == identity


# Export
__all__ = [
    "Matrix",
    "DenseMatrix",
    "SparseMatrix",
    "IdentityMatrix",
    "DiagonalMatrix",
    "SymmetricMatrix",
    "OrthogonalMatrix",
]
