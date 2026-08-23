"""
Quantum Operator Math Module

This module provides quantum operator mathematics for the QuantsMind SDK.

Purpose
-------
Provide mathematical operations on quantum operators, integrating with classical mathematics.

Classes
-------
QuantumOperatorMath: Quantum operator mathematical operations

Responsibilities
----------------
- Convert quantum operators to classical matrices
- Perform operator operations
- Compute commutators
- Support operator decompositions

Dependencies
------------
typing (standard library)
quantsmind.algebra.linear_algebra (Matrix)
"""

from __future__ import annotations

from typing import Any

from quantsmind.algebra.linear_algebra import Matrix


class QuantumOperatorMath:
    """Quantum operator mathematical operations.

    This class provides functionality for mathematical operations on quantum operators,
    bridging quantum computing with classical linear algebra.

    Attributes:
        _name: Operator name
        _data: Operator data (complex numbers)
        _metadata: Additional metadata

    Example:
        >>> qom = QuantumOperatorMath("pauli_x", [[0, 1], [1, 0]])
        >>> classical = qom.to_classical_matrix()
    """

    def __init__(
        self,
        name: str,
        data: list[list[complex]],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a QuantumOperatorMath.

        Args:
            name: Operator name
            data: Operator data (complex numbers)
            metadata: Additional metadata

        Example:
            >>> qom = QuantumOperatorMath("pauli_x", [[0, 1], [1, 0]])
        """
        self._name = name
        self._data = data
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the operator name.

        Returns:
            Operator name

        Example:
            >>> name = qom.name
        """
        return self._name

    @property
    def data(self) -> list[list[complex]]:
        """Get the operator data.

        Returns:
            Operator data

        Example:
            >>> data = qom.data
        """
        return [row.copy() for row in self._data]

    @property
    def rows(self) -> int:
        """Get the number of rows.

        Returns:
            Number of rows

        Example:
            >>> rows = qom.rows
        """
        return len(self._data)

    @property
    def cols(self) -> int:
        """Get the number of columns.

        Returns:
            Number of columns

        Example:
            >>> cols = qom.cols
        """
        return len(self._data[0]) if self._data else 0

    def to_classical_matrix(self) -> Matrix:
        """Convert to classical matrix (real part only).

        Returns:
            Classical matrix

        Example:
            >>> classical = qom.to_classical_matrix()
        """
        real_data = [[complex(val).real for val in row] for row in self._data]
        return Matrix(f"{self._name}_classical", real_data)

    def hermitian_conjugate(self) -> QuantumOperatorMath:
        """Compute Hermitian conjugate.

        Returns:
            Hermitian conjugate operator

        Example:
            >>> hc = qom.hermitian_conjugate()
        """
        transposed = [[self._data[j][i].conjugate() for j in range(self.cols)] for i in range(self.rows)]
        return QuantumOperatorMath(f"{self._name}_dagger", transposed)

    def commutator(self, other: QuantumOperatorMath) -> QuantumOperatorMath:
        """Compute commutator [A, B] = AB - BA.

        Args:
            other: Other operator

        Returns:
            Commutator

        Example:
            >>> comm = qom.commutator(other)
        """
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Operators must have same dimensions")

        # Compute AB
        ab = self._multiply_matrices(self._data, other._data)

        # Compute BA
        ba = self._multiply_matrices(other._data, self._data)

        # Compute AB - BA
        comm_data = [[ab[i][j] - ba[i][j] for j in range(self.cols)] for i in range(self.rows)]
        return QuantumOperatorMath(f"[{self._name},{other._name}]", comm_data)

    def anti_commutator(self, other: QuantumOperatorMath) -> QuantumOperatorMath:
        """Compute anti-commutator {A, B} = AB + BA.

        Args:
            other: Other operator

        Returns:
            Anti-commutator

        Example:
            >>> anti_comm = qom.anti_commutator(other)
        """
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Operators must have same dimensions")

        # Compute AB
        ab = self._multiply_matrices(self._data, other._data)

        # Compute BA
        ba = self._multiply_matrices(other._data, self._data)

        # Compute AB + BA
        anti_comm_data = [[ab[i][j] + ba[i][j] for j in range(self.cols)] for i in range(self.rows)]
        return QuantumOperatorMath(f"{{{self._name},{other._name}}}", anti_comm_data)

    def _multiply_matrices(self, A: list[list[complex]], B: list[list[complex]]) -> list[list[complex]]:
        """Multiply two matrices.

        Args:
            A: First matrix
            B: Second matrix

        Returns:
            Product matrix
        """
        n = len(A)
        m = len(B[0])
        p = len(B)

        result = [[0j] * m for _ in range(n)]

        for i in range(n):
            for j in range(m):
                for k in range(p):
                    result[i][j] += A[i][k] * B[k][j]

        return result

    def tensor_product(self, other: QuantumOperatorMath) -> QuantumOperatorMath:
        """Compute tensor product (Kronecker product).

        Args:
            other: Other operator

        Returns:
            Tensor product operator

        Example:
            >>> product = qom.tensor_product(other)
        """
        result_rows = self.rows * other.rows
        result_cols = self.cols * other.cols
        result = [[0j] * result_cols for _ in range(result_rows)]

        for i in range(self.rows):
            for j in range(self.cols):
                for k in range(other.rows):
                    for l in range(other.cols):
                        result[i * other.rows + k][j * other.cols + l] = self._data[i][j] * other._data[k][l]

        return QuantumOperatorMath(f"{self._name}_tensor_{other._name}", result)

    def is_hermitian(self, tolerance: float = 1e-10) -> bool:
        """Check if the operator is Hermitian.

        Args:
            tolerance: Numerical tolerance

        Returns:
            True if Hermitian

        Example:
            >>> is_herm = qom.is_hermitian()
        """
        if not self.is_square():
            return False

        hc = self.hermitian_conjugate()

        for i in range(self.rows):
            for j in range(self.cols):
                if abs(self._data[i][j] - hc._data[i][j]) > tolerance:
                    return False

        return True

    def is_unitary(self, tolerance: float = 1e-10) -> bool:
        """Check if the operator is unitary.

        Args:
            tolerance: Numerical tolerance

        Returns:
            True if unitary

        Example:
            >>> is_unitary = qom.is_unitary()
        """
        if not self.is_square():
            return False

        # Check if U * U† = I
        hc = self.hermitian_conjugate()
        product = self._multiply_matrices(self._data, hc._data)

        # Check if product is identity
        for i in range(self.rows):
            for j in range(self.cols):
                expected = 1.0 if i == j else 0.0
                if abs(product[i][j] - expected) > tolerance:
                    return False

        return True

    def is_square(self) -> bool:
        """Check if the operator is square.

        Returns:
            True if square

        Example:
            >>> is_sq = qom.is_square()
        """
        return self.rows == self.cols

    def trace(self) -> complex:
        """Compute the trace.

        Returns:
            Trace value

        Example:
            >>> tr = qom.trace()
        """
        if not self.is_square():
            raise ValueError("Trace only defined for square operators")

        return sum(self._data[i][i] for i in range(min(self.rows, self.cols)))

    def eigenvalues(self) -> list[complex]:
        """Compute eigenvalues (simplified).

        Returns:
            List of eigenvalues

        Example:
            >>> evals = qom.eigenvalues()
        """
        # Placeholder - real implementation would use numerical methods
        return []

    def eigenvectors(self) -> list[list[complex]]:
        """Compute eigenvectors (simplified).

        Returns:
            List of eigenvectors

        Example:
            >>> evecs = qom.eigenvectors()
        """
        # Placeholder - real implementation would use numerical methods
        return []

    def determinant(self) -> complex:
        """Compute the determinant.

        Returns:
            Determinant value

        Example:
            >>> det = qom.determinant()
        """
        if not self.is_square():
            raise ValueError("Determinant only defined for square operators")

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
            >>> repr(qom)
        """
        return f"QuantumOperatorMath(name={self._name}, shape=({self.rows}, {self.cols}))"


__all__ = [
    "QuantumOperatorMath",
]
