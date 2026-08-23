"""
Quantum Matrix Module

This module provides quantum matrix operations for the QuantsMind SDK.

Purpose
-------
Provide mathematical operations on quantum matrices, integrating with the classical algebra engine.

Classes
-------
QuantumMatrix: Quantum matrix operations

Responsibilities
----------------
- Convert quantum matrices to classical matrices
- Perform matrix operations on quantum states
- Support tensor products
- Support matrix decompositions

Dependencies
------------
typing (standard library)
quantsmind.algebra.linear_algebra (Matrix, Vector)
"""

from __future__ import annotations

from typing import Any

from quantsmind.algebra.linear_algebra import Matrix


class QuantumMatrix:
    """Quantum matrix operations.

    This class provides functionality for mathematical operations on quantum matrices,
    bridging quantum computing with classical linear algebra.

    Attributes:
        _name: Matrix name
        _data: Matrix data (complex numbers)
        _metadata: Additional metadata

    Example:
        >>> qm = QuantumMatrix("hadamard", [[1, 1], [1, -1]])
        >>> classical = qm.to_classical_matrix()
    """

    def __init__(
        self,
        name: str,
        data: list[list[complex]],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a QuantumMatrix.

        Args:
            name: Matrix name
            data: Matrix data (complex numbers)
            metadata: Additional metadata

        Example:
            >>> qm = QuantumMatrix("hadamard", [[1, 1], [1, -1]])
        """
        self._name = name
        self._data = data
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the matrix name.

        Returns:
            Matrix name

        Example:
            >>> name = qm.name
        """
        return self._name

    @property
    def data(self) -> list[list[complex]]:
        """Get the matrix data.

        Returns:
            Matrix data

        Example:
            >>> data = qm.data
        """
        return [row.copy() for row in self._data]

    @property
    def rows(self) -> int:
        """Get the number of rows.

        Returns:
            Number of rows

        Example:
            >>> rows = qm.rows
        """
        return len(self._data)

    @property
    def cols(self) -> int:
        """Get the number of columns.

        Returns:
            Number of columns

        Example:
            >>> cols = qm.cols
        """
        return len(self._data[0]) if self._data else 0

    def to_classical_matrix(self) -> Matrix:
        """Convert to classical matrix (real part only).

        Returns:
            Classical matrix

        Example:
            >>> classical = qm.to_classical_matrix()
        """
        real_data = [[complex(val).real for val in row] for row in self._data]
        return Matrix(f"{self._name}_classical", real_data)

    def hermitian_conjugate(self) -> QuantumMatrix:
        """Compute Hermitian conjugate.

        Returns:
            Hermitian conjugate matrix

        Example:
            >>> hc = qm.hermitian_conjugate()
        """
        transposed = [[self._data[j][i].conjugate() for j in range(self.cols)] for i in range(self.rows)]
        return QuantumMatrix(f"{self._name}_dagger", transposed)

    def tensor_product(self, other: QuantumMatrix) -> QuantumMatrix:
        """Compute tensor product (Kronecker product).

        Args:
            other: Other matrix

        Returns:
            Tensor product matrix

        Example:
            >>> product = qm.tensor_product(other)
        """
        result_rows = self.rows * other.rows
        result_cols = self.cols * other.cols
        result = [[0j] * result_cols for _ in range(result_rows)]

        for i in range(self.rows):
            for j in range(self.cols):
                for k in range(other.rows):
                    for l in range(other.cols):
                        result[i * other.rows + k][j * other.cols + l] = self._data[i][j] * other._data[k][l]

        return QuantumMatrix(f"{self._name}_tensor_{other._name}", result)

    def multiply(self, other: QuantumMatrix) -> QuantumMatrix:
        """Multiply with another matrix.

        Args:
            other: Other matrix

        Returns:
            Product matrix

        Example:
            >>> product = qm.multiply(other)
        """
        if self.cols != other.rows:
            raise ValueError("Matrix dimensions incompatible for multiplication")

        result = [[0j] * other.cols for _ in range(self.rows)]

        for i in range(self.rows):
            for j in range(other.cols):
                for k in range(self.cols):
                    result[i][j] += self._data[i][k] * other._data[k][j]

        return QuantumMatrix(f"{self._name}_times_{other._name}", result)

    def trace(self) -> complex:
        """Compute the trace.

        Returns:
            Trace value

        Example:
            >>> tr = qm.trace()
        """
        if not self.is_square():
            raise ValueError("Trace only defined for square matrices")

        return sum(self._data[i][i] for i in range(min(self.rows, self.cols)))

    def is_square(self) -> bool:
        """Check if the matrix is square.

        Returns:
            True if square

        Example:
            >>> is_sq = qm.is_square()
        """
        return self.rows == self.cols

    def is_unitary(self, tolerance: float = 1e-10) -> bool:
        """Check if the matrix is unitary.

        Args:
            tolerance: Numerical tolerance

        Returns:
            True if unitary

        Example:
            >>> is_unitary = qm.is_unitary()
        """
        if not self.is_square():
            return False

        # Check if U * U† = I
        hc = self.hermitian_conjugate()
        product = self.multiply(hc)

        # Check if product is identity
        for i in range(self.rows):
            for j in range(self.cols):
                expected = 1.0 if i == j else 0.0
                if abs(product._data[i][j] - expected) > tolerance:
                    return False

        return True

    def is_hermitian(self, tolerance: float = 1e-10) -> bool:
        """Check if the matrix is Hermitian.

        Args:
            tolerance: Numerical tolerance

        Returns:
            True if Hermitian

        Example:
            >>> is_herm = qm.is_hermitian()
        """
        if not self.is_square():
            return False

        hc = self.hermitian_conjugate()

        for i in range(self.rows):
            for j in range(self.cols):
                if abs(self._data[i][j] - hc._data[i][j]) > tolerance:
                    return False

        return True

    def eigenvalues(self) -> list[complex]:
        """Compute eigenvalues (simplified).

        Returns:
            List of eigenvalues

        Example:
            >>> evals = qm.eigenvalues()
        """
        # Placeholder - real implementation would use numerical methods
        return []

    def determinant(self) -> complex:
        """Compute the determinant.

        Returns:
            Determinant value

        Example:
            >>> det = qm.determinant()
        """
        if not self.is_square():
            raise ValueError("Determinant only defined for square matrices")

        if self.rows == 1:
            return self._data[0][0]
        elif self.rows == 2:
            return self._data[0][0] * self._data[1][1] - self._data[0][1] * self._data[1][0]
        else:
            # Recursive cofactor expansion (placeholder)
            return 0j

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(qm)
        """
        return f"QuantumMatrix(name={self._name}, shape=({self.rows}, {self.cols}))"


__all__ = [
    "QuantumMatrix",
]
