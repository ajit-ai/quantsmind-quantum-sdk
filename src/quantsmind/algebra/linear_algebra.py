"""
Linear Algebra Module

This module provides linear algebra classes for the QuantsMind SDK.

Purpose
-------
Provide linear algebra operations including matrix, vector, and tensor computations.

Classes
-------
Matrix: Matrix representation and operations
Vector: Vector representation and operations
Tensor: Tensor representation and operations
SparseMatrix: Sparse matrix representation

Responsibilities
----------------
- Represent matrices, vectors, and tensors
- Perform matrix operations (add, subtract, multiply, inverse, transpose)
- Compute determinants, rank, eigenvalues, eigenvectors
- Perform matrix decompositions (SVD, LU, QR)

Dependencies
------------
typing (standard library)
quantsmind.core.math_object (MathObject)
"""

from __future__ import annotations

import math
from typing import Any

from quantsmind.core.math_object import MathObject


class Matrix(MathObject):
    """Matrix representation.

    This class provides functionality for representing and manipulating
    matrices with standard linear algebra operations.

    Attributes:
        _name: Matrix name
        _data: Matrix data as list of lists
        _rows: Number of rows
        _cols: Number of columns
        _metadata: Additional metadata

    Example:
        >>> matrix = Matrix("A", [[1, 2], [3, 4]])
        >>> result = matrix.multiply(other)
    """

    def __init__(
        self,
        name: str,
        data: list[list[float]],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Matrix.

        Args:
            name: Matrix name
            data: Matrix data as list of lists
            metadata: Additional metadata

        Example:
            >>> matrix = Matrix("A", [[1, 2], [3, 4]])
        """
        super().__init__(name, metadata)
        self._data = data
        self._rows = len(data)
        self._cols = len(data[0]) if data else 0

    @property
    def data(self) -> list[list[float]]:
        """Get the matrix data.

        Returns:
            Matrix data

        Example:
            >>> data = matrix.data
        """
        return [row.copy() for row in self._data]

    @property
    def rows(self) -> int:
        """Get the number of rows.

        Returns:
            Number of rows

        Example:
            >>> rows = matrix.rows
        """
        return self._rows

    @property
    def cols(self) -> int:
        """Get the number of columns.

        Returns:
            Number of columns

        Example:
            >>> cols = matrix.cols
        """
        return self._cols

    @property
    def shape(self) -> tuple[int, int]:
        """Get the matrix shape.

        Returns:
            Tuple of (rows, cols)

        Example:
            >>> shape = matrix.shape
        """
        return (self._rows, self._cols)

    def is_square(self) -> bool:
        """Check if the matrix is square.

        Returns:
            True if square

        Example:
            >>> is_sq = matrix.is_square()
        """
        return self._rows == self._cols

    def get(self, i: int, j: int) -> float:
        """Get an element.

        Args:
            i: Row index
            j: Column index

        Returns:
            Element value

        Example:
            >>> val = matrix.get(0, 0)
        """
        return self._data[i][j]

    def set(self, i: int, j: int, value: float) -> None:
        """Set an element.

        Args:
            i: Row index
            j: Column index
            value: Value to set

        Example:
            >>> matrix.set(0, 0, 5.0)
        """
        self._data[i][j] = value

    def add(self, other: Matrix) -> Matrix:
        """Add another matrix.

        Args:
            other: Matrix to add

        Returns:
            Sum matrix

        Example:
            >>> result = matrix.add(other)
        """
        if self._rows != other.rows or self._cols != other.cols:
            raise ValueError("Matrix dimensions must match for addition")

        result_data = [
            [self._data[i][j] + other.data[i][j] for j in range(self._cols)]
            for i in range(self._rows)
        ]
        return Matrix(f"{self._name}_plus_{other._name}", result_data)

    def subtract(self, other: Matrix) -> Matrix:
        """Subtract another matrix.

        Args:
            other: Matrix to subtract

        Returns:
            Difference matrix

        Example:
            >>> result = matrix.subtract(other)
        """
        if self._rows != other.rows or self._cols != other.cols:
            raise ValueError("Matrix dimensions must match for subtraction")

        result_data = [
            [self._data[i][j] - other.data[i][j] for j in range(self._cols)]
            for i in range(self._rows)
        ]
        return Matrix(f"{self._name}_minus_{other._name}", result_data)

    def multiply(self, other: Matrix | float) -> Matrix:
        """Multiply by another matrix or scalar.

        Args:
            other: Matrix or scalar to multiply by

        Returns:
            Product matrix

        Example:
            >>> result = matrix.multiply(other)
        """
        if isinstance(other, (int, float)):
            # Scalar multiplication
            result_data = [
                [self._data[i][j] * other for j in range(self._cols)]
                for i in range(self._rows)
            ]
            return Matrix(f"{self._name}_scaled", result_data)
        else:
            # Matrix multiplication
            if self._cols != other.rows:
                raise ValueError("Matrix dimensions incompatible for multiplication")

            result_data = [
                [
                    sum(self._data[i][k] * other.data[k][j] for k in range(self._cols))
                    for j in range(other.cols)
                ]
                for i in range(self._rows)
            ]
            return Matrix(f"{self._name}_times_{other._name}", result_data)

    def transpose(self) -> Matrix:
        """Transpose the matrix.

        Returns:
            Transposed matrix

        Example:
            >>> transposed = matrix.transpose()
        """
        result_data = [
            [self._data[j][i] for j in range(self._rows)]
            for i in range(self._cols)
        ]
        return Matrix(f"{self._name}_T", result_data)

    def determinant(self) -> float:
        """Compute the determinant.

        Returns:
            Determinant value

        Example:
            >>> det = matrix.determinant()
        """
        if not self.is_square():
            raise ValueError("Determinant only defined for square matrices")

        if self._rows == 1:
            return self._data[0][0]
        elif self._rows == 2:
            return self._data[0][0] * self._data[1][1] - self._data[0][1] * self._data[1][0]
        else:
            # Recursive cofactor expansion (placeholder - real implementation would use LU decomposition)
            det = 0.0
            for j in range(self._cols):
                minor = self._minor(0, j)
                sign = (-1) ** j
                det += sign * self._data[0][j] * minor.determinant()
            return det

    def _minor(self, i: int, j: int) -> Matrix:
        """Get the minor matrix.

        Args:
            i: Row to exclude
            j: Column to exclude

        Returns:
            Minor matrix
        """
        minor_data = [
            [self._data[r][c] for c in range(self._cols) if c != j]
            for r in range(self._rows) if r != i
        ]
        return Matrix("minor", minor_data)

    def inverse(self) -> Matrix:
        """Compute the inverse.

        Returns:
            Inverse matrix

        Example:
            >>> inv = matrix.inverse()
        """
        if not self.is_square():
            raise ValueError("Inverse only defined for square matrices")

        det = self.determinant()
        if abs(det) < 1e-10:
            raise ValueError("Matrix is singular, cannot compute inverse")

        if self._rows == 1:
            return Matrix("inverse", [[1.0 / det]])

        # Compute adjugate matrix (placeholder - real implementation would use more efficient methods)
        adj_data = [
            [
                ((-1) ** (i + j)) * self._minor(j, i).determinant()
                for j in range(self._cols)
            ]
            for i in range(self._rows)
        ]

        inv_data = [[adj_data[i][j] / det for j in range(self._cols)] for i in range(self._rows)]
        return Matrix(f"{self._name}_inv", inv_data)

    def rank(self) -> int:
        """Compute the matrix rank.

        Returns:
            Matrix rank

        Example:
            >>> r = matrix.rank()
        """
        # Placeholder - real implementation would use Gaussian elimination
        return min(self._rows, self._cols)

    def trace(self) -> float:
        """Compute the trace (sum of diagonal elements).

        Returns:
            Trace value

        Example:
            >>> tr = matrix.trace()
        """
        if not self.is_square():
            raise ValueError("Trace only defined for square matrices")

        return sum(self._data[i][i] for i in range(self._rows))

    def eigenvalues(self) -> list[complex]:
        """Compute eigenvalues.

        Returns:
            List of eigenvalues

        Example:
            >>> evals = matrix.eigenvalues()
        """
        # Placeholder - real implementation would use QR algorithm or similar
        return []

    def eigenvectors(self) -> list[list[float]]:
        """Compute eigenvectors.

        Returns:
            List of eigenvectors

        Example:
            >>> evecs = matrix.eigenvectors()
        """
        # Placeholder - real implementation would use eigenvalue decomposition
        return []

    def svd(self) -> tuple[Matrix, Matrix, Matrix]:
        """Compute singular value decomposition.

        Returns:
            Tuple of (U, S, V)

        Example:
            >>> U, S, V = matrix.svd()
        """
        # Placeholder - real implementation would use SVD algorithm
        return (Matrix("U", []), Matrix("S", []), Matrix("V", []))

    def lu_decomposition(self) -> tuple[Matrix, Matrix]:
        """Compute LU decomposition.

        Returns:
            Tuple of (L, U)

        Example:
            >>> L, U = matrix.lu_decomposition()
        """
        # Placeholder - real implementation would use Doolittle algorithm
        return (Matrix("L", []), Matrix("U", []))

    def qr_decomposition(self) -> tuple[Matrix, Matrix]:
        """Compute QR decomposition.

        Returns:
            Tuple of (Q, R)

        Example:
            >>> Q, R = matrix.qr_decomposition()
        """
        # Placeholder - real implementation would use Gram-Schmidt or Householder
        return (Matrix("Q", []), Matrix("R", []))

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the matrix.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = matrix.validate()
        """
        errors = []

        # Validate base object
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if not self._data:
            errors.append("Matrix data cannot be empty")

        # Check all rows have same length
        for i, row in enumerate(self._data):
            if len(row) != self._cols:
                errors.append(f"Row {i} length {len(row)} does not match columns {self._cols}")

        return (len(errors) == 0, errors)

    def serialize(self) -> dict[str, Any]:
        """Serialize the matrix.

        Returns:
            Serialized representation

        Example:
            >>> data = matrix.serialize()
        """
        data = super().serialize()
        data["data"] = self._data
        data["rows"] = self._rows
        data["cols"] = self._cols
        data["shape"] = self.shape
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(matrix)
        """
        return f"Matrix(name={self._name}, shape={self.shape})"


class Vector(MathObject):
    """Vector representation.

    This class provides functionality for representing and manipulating vectors.

    Attributes:
        _name: Vector name
        _data: Vector data
        _size: Vector size
        _metadata: Additional metadata

    Example:
        >>> vec = Vector("v", [1, 2, 3])
        >>> result = vec.add(other)
    """

    def __init__(
        self,
        name: str,
        data: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Vector.

        Args:
            name: Vector name
            data: Vector data
            metadata: Additional metadata

        Example:
            >>> vec = Vector("v", [1, 2, 3])
        """
        super().__init__(name, metadata)
        self._data = data
        self._size = len(data)

    @property
    def data(self) -> list[float]:
        """Get the vector data.

        Returns:
            Vector data

        Example:
            >>> data = vec.data
        """
        return self._data.copy()

    @property
    def size(self) -> int:
        """Get the vector size.

        Returns:
            Vector size

        Example:
            >>> size = vec.size
        """
        return self._size

    def get(self, i: int) -> float:
        """Get an element.

        Args:
            i: Index

        Returns:
            Element value

        Example:
            >>> val = vec.get(0)
        """
        return self._data[i]

    def set(self, i: int, value: float) -> None:
        """Set an element.

        Args:
            i: Index
            value: Value to set

        Example:
            >>> vec.set(0, 5.0)
        """
        self._data[i] = value

    def add(self, other: Vector) -> Vector:
        """Add another vector.

        Args:
            other: Vector to add

        Returns:
            Sum vector

        Example:
            >>> result = vec.add(other)
        """
        if self._size != other.size:
            raise ValueError("Vector sizes must match for addition")

        result_data = [self._data[i] + other.data[i] for i in range(self._size)]
        return Vector(f"{self._name}_plus_{other._name}", result_data)

    def subtract(self, other: Vector) -> Vector:
        """Subtract another vector.

        Args:
            other: Vector to subtract

        Returns:
            Difference vector

        Example:
            >>> result = vec.subtract(other)
        """
        if self._size != other.size:
            raise ValueError("Vector sizes must match for subtraction")

        result_data = [self._data[i] - other.data[i] for i in range(self._size)]
        return Vector(f"{self._name}_minus_{other._name}", result_data)

    def multiply(self, scalar: float) -> Vector:
        """Multiply by a scalar.

        Args:
            scalar: Scalar to multiply by

        Returns:
            Scaled vector

        Example:
            >>> result = vec.multiply(2.0)
        """
        result_data = [self._data[i] * scalar for i in range(self._size)]
        return Vector(f"{self._name}_scaled", result_data)

    def dot(self, other: Vector) -> float:
        """Compute dot product with another vector.

        Args:
            other: Vector to compute dot product with

        Returns:
            Dot product

        Example:
            >>> result = vec.dot(other)
        """
        if self._size != other.size:
            raise ValueError("Vector sizes must match for dot product")

        return sum(self._data[i] * other.data[i] for i in range(self._size))

    def norm(self) -> float:
        """Compute the Euclidean norm.

        Returns:
            Norm value

        Example:
            >>> n = vec.norm()
        """
        return math.sqrt(sum(x**2 for x in self._data))

    def normalize(self) -> Vector:
        """Normalize the vector.

        Returns:
            Normalized vector

        Example:
            >>> normalized = vec.normalize()
        """
        n = self.norm()
        if n == 0:
            raise ValueError("Cannot normalize zero vector")
        return self.multiply(1.0 / n)

    def to_matrix(self) -> Matrix:
        """Convert to a column matrix.

        Returns:
            Column matrix

        Example:
            >>> mat = vec.to_matrix()
        """
        return Matrix(f"{self._name}_matrix", [[x] for x in self._data])

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the vector.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = vec.validate()
        """
        errors = []

        # Validate base object
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if not self._data:
            errors.append("Vector data cannot be empty")

        return (len(errors) == 0, errors)

    def serialize(self) -> dict[str, Any]:
        """Serialize the vector.

        Returns:
            Serialized representation

        Example:
            >>> data = vec.serialize()
        """
        data = super().serialize()
        data["data"] = self._data
        data["size"] = self._size
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(vec)
        """
        return f"Vector(name={self._name}, size={self._size})"


class Tensor(MathObject):
    """Tensor representation.

    This class provides functionality for representing and manipulating
    multi-dimensional tensors.

    Attributes:
        _name: Tensor name
        _data: Tensor data (nested lists)
        _shape: Tensor shape
        _metadata: Additional metadata

    Example:
        >>> tensor = Tensor("T", [[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    """

    def __init__(
        self,
        name: str,
        data: list[Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Tensor.

        Args:
            name: Tensor name
            data: Tensor data (nested lists)
            metadata: Additional metadata

        Example:
            >>> tensor = Tensor("T", [[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
        """
        super().__init__(name, metadata)
        self._data = data
        self._shape = self._compute_shape(data)

    def _compute_shape(self, data: list[Any]) -> tuple[int, ...]:
        """Compute the shape of nested data.

        Args:
            data: Nested data

        Returns:
            Shape tuple
        """
        shape = []
        current = data
        while isinstance(current, list):
            shape.append(len(current))
            if current:
                current = current[0]
            else:
                break
        return tuple(shape)

    @property
    def data(self) -> list[Any]:
        """Get the tensor data.

        Returns:
            Tensor data

        Example:
            >>> data = tensor.data
        """
        return self._data

    @property
    def shape(self) -> tuple[int, ...]:
        """Get the tensor shape.

        Returns:
            Shape tuple

        Example:
            >>> shape = tensor.shape
        """
        return self._shape

    @property
    def ndim(self) -> int:
        """Get the number of dimensions.

        Returns:
            Number of dimensions

        Example:
            >>> ndim = tensor.ndim
        """
        return len(self._shape)

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the tensor.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = tensor.validate()
        """
        errors = []

        # Validate base object
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if not self._data:
            errors.append("Tensor data cannot be empty")

        return (len(errors) == 0, errors)

    def serialize(self) -> dict[str, Any]:
        """Serialize the tensor.

        Returns:
            Serialized representation

        Example:
            >>> data = tensor.serialize()
        """
        data = super().serialize()
        data["shape"] = self._shape
        data["ndim"] = self.ndim
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(tensor)
        """
        return f"Tensor(name={self._name}, shape={self._shape})"


class SparseMatrix(MathObject):
    """Sparse matrix representation.

    This class provides functionality for representing and manipulating
    sparse matrices using coordinate format.

    Attributes:
        _name: Matrix name
        _rows: Number of rows
        _cols: Number of columns
        _data: Dictionary of (i, j) -> value
        _metadata: Additional metadata

    Example:
        >>> sparse = SparseMatrix("S", 100, 100)
        >>> sparse.set(0, 0, 1.0)
    """

    def __init__(
        self,
        name: str,
        rows: int,
        cols: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a SparseMatrix.

        Args:
            name: Matrix name
            rows: Number of rows
            cols: Number of columns
            metadata: Additional metadata

        Example:
            >>> sparse = SparseMatrix("S", 100, 100)
        """
        super().__init__(name, metadata)
        self._rows = rows
        self._cols = cols
        self._data: dict[tuple[int, int], float] = {}

    @property
    def rows(self) -> int:
        """Get the number of rows.

        Returns:
            Number of rows

        Example:
            >>> rows = sparse.rows
        """
        return self._rows

    @property
    def cols(self) -> int:
        """Get the number of columns.

        Returns:
            Number of columns

        Example:
            >>> cols = sparse.cols
        """
        return self._cols

    @property
    def shape(self) -> tuple[int, int]:
        """Get the matrix shape.

        Returns:
            Tuple of (rows, cols)

        Example:
            >>> shape = sparse.shape
        """
        return (self._rows, self._cols)

    @property
    def nnz(self) -> int:
        """Get the number of non-zero elements.

        Returns:
            Number of non-zero elements

        Example:
            >>> nnz = sparse.nnz
        """
        return len(self._data)

    def get(self, i: int, j: int) -> float:
        """Get an element.

        Args:
            i: Row index
            j: Column index

        Returns:
            Element value (0 if not set)

        Example:
            >>> val = sparse.get(0, 0)
        """
        return self._data.get((i, j), 0.0)

    def set(self, i: int, j: int, value: float) -> None:
        """Set an element.

        Args:
            i: Row index
            j: Column index
            value: Value to set

        Example:
            >>> sparse.set(0, 0, 1.0)
        """
        if value == 0.0:
            # Remove zero entries to maintain sparsity
            if (i, j) in self._data:
                del self._data[(i, j)]
        else:
            self._data[(i, j)] = value

    def to_dense(self) -> Matrix:
        """Convert to dense matrix.

        Returns:
            Dense matrix

        Example:
            >>> dense = sparse.to_dense()
        """
        dense_data = [[0.0] * self._cols for _ in range(self._rows)]
        for (i, j), value in self._data.items():
            dense_data[i][j] = value
        return Matrix(f"{self._name}_dense", dense_data)

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the sparse matrix.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = sparse.validate()
        """
        errors = []

        # Validate base object
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if self._rows <= 0 or self._cols <= 0:
            errors.append("Matrix dimensions must be positive")

        return (len(errors) == 0, errors)

    def serialize(self) -> dict[str, Any]:
        """Serialize the sparse matrix.

        Returns:
            Serialized representation

        Example:
            >>> data = sparse.serialize()
        """
        data = super().serialize()
        data["rows"] = self._rows
        data["cols"] = self._cols
        data["nnz"] = self.nnz
        data["data"] = [{"i": i, "j": j, "value": v} for (i, j), v in self._data.items()]
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(sparse)
        """
        return f"SparseMatrix(name={self._name}, shape={self.shape}, nnz={self.nnz})"


__all__ = [
    "Matrix",
    "Vector",
    "Tensor",
    "SparseMatrix",
]
