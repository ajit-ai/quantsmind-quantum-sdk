"""
Hamiltonian Module

This module provides Hamiltonian definitions for the Quantum package.

Purpose
-------
Provide Hamiltonian management for quantum computing operations.

Responsibilities
----------------
- Define Hamiltonian structure
- Support Hamiltonian operations
- Support Hamiltonian validation
- Support Hamiltonian metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.operator.operator (operator module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.exceptions import CircuitError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.operator.operator import QuantumOperator


class Hamiltonian(QuantumOperator):
    """Concrete implementation of a Hamiltonian.

    This class provides Hamiltonian functionality for quantum computing.
    A Hamiltonian represents the total energy operator of a quantum system.

    Attributes:
        _name: Hamiltonian name
        _num_qubits: Number of qubits
        _terms: Hamiltonian terms
        _coefficients: Term coefficients
        _matrix: Hamiltonian matrix
        _metadata: Hamiltonian metadata

    Example:
        >>> hamiltonian = Hamiltonian("ising", 2)
        >>> hamiltonian.add_term(pauli_z, 1.0, [0])
    """

    def __init__(
        self,
        name: str,
        num_qubits: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Hamiltonian.

        Args:
            name: Hamiltonian name
            num_qubits: Number of qubits
            metadata: Hamiltonian metadata

        Example:
            >>> hamiltonian = Hamiltonian("ising", 2)
        """
        super().__init__(name, num_qubits, metadata=metadata)
        self._terms: list[QuantumOperator] = []
        self._coefficients: list[float] = []
        self._qubit_indices: list[list[int]] = []

    @property
    def terms(self) -> list[QuantumOperator]:
        """Get the Hamiltonian terms.

        Returns:
            List of terms

        Example:
            >>> terms = hamiltonian.terms
        """
        return self._terms.copy()

    @property
    def coefficients(self) -> list[float]:
        """Get the term coefficients.

        Returns:
            List of coefficients

        Example:
            >>> coeffs = hamiltonian.coefficients
        """
        return self._coefficients.copy()

    def add_term(self, operator: QuantumOperator, coefficient: float, qubits: list[int]) -> None:
        """Add a term to the Hamiltonian.

        Args:
            operator: Operator term
            coefficient: Term coefficient
            qubits: Qubit indices

        Example:
            >>> hamiltonian.add_term(pauli_z, 1.0, [0])
        """
        if operator is None:
            raise CircuitError("Operator cannot be None", {"operator": None})

        if len(qubits) != operator.num_qubits:
            raise CircuitError(f"Operator requires {operator.num_qubits} qubits, but {len(qubits)} provided", {"operator": operator.name})

        for qubit in qubits:
            if qubit < 0 or qubit >= self._num_qubits:
                raise CircuitError(f"Qubit index {qubit} out of range [0, {self._num_qubits})", {"qubit": qubit})

        self._terms.append(operator)
        self._coefficients.append(coefficient)
        self._qubit_indices.append(qubits)

    def remove_term(self, index: int) -> bool:
        """Remove a term from the Hamiltonian.

        Args:
            index: Term index

        Returns:
            True if removed

        Example:
            >>> removed = hamiltonian.remove_term(0)
        """
        if 0 <= index < len(self._terms):
            del self._terms[index]
            del self._coefficients[index]
            del self._qubit_indices[index]
            return True
        return False

    def get_term(self, index: int) -> tuple[QuantumOperator, float, list[int]] | None:
        """Get a term by index.

        Args:
            index: Term index

        Returns:
            Tuple of (operator, coefficient, qubits) or None

        Example:
            >>> term = hamiltonian.get_term(0)
        """
        if 0 <= index < len(self._terms):
            return (self._terms[index], self._coefficients[index], self._qubit_indices[index])
        return None

    def count_terms(self) -> int:
        """Get the number of terms.

        Returns:
            Number of terms

        Example:
            >>> count = hamiltonian.count_terms()
        """
        return len(self._terms)

    def clear(self) -> None:
        """Clear all terms.

        Example:
            >>> hamiltonian.clear()
        """
        self._terms.clear()
        self._coefficients.clear()
        self._qubit_indices.clear()

    def validate(self) -> ValidationResult:
        """Validate the Hamiltonian.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = hamiltonian.validate()
        """
        errors = []

        # Validate base operator
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate all terms
        for i, (term, _coeff, _qubits) in enumerate(zip(self._terms, self._coefficients, self._qubit_indices, strict=False)):
            is_valid, term_errors = term.validate()
            errors.extend([f"Term {i}: {err}" for err in term_errors])

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Hamiltonian definition

        Example:
            >>> data = hamiltonian.to_dict()
        """
        data = super().to_dict()
        data["term_count"] = len(self._terms)
        data["terms"] = [
            {"operator": term.name, "coefficient": coeff, "qubits": qubits}
            for term, coeff, qubits in zip(self._terms, self._coefficients, self._qubit_indices, strict=False)
        ]
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(hamiltonian)
        """
        return f"Hamiltonian(name={self._name}, num_qubits={self._num_qubits}, terms={len(self._terms)})"
