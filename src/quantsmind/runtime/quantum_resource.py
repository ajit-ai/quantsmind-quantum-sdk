"""
Runtime Quantum Resource Module

This module provides quantum resource management for the Runtime package.

Purpose
-------
Provide quantum resource management for the QuantsMind SDK.

Responsibilities
----------------
- Manage quantum resources
- Track quantum usage
- Handle quantum allocation
- Monitor quantum performance

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.resource (resource)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quantsmind.runtime.enums import ResourceType
from quantsmind.runtime.resource import Resource
from quantsmind.runtime.types import ResourceCapacity, ResourceID

logger = logging.getLogger(__name__)


class QuantumResource(Resource):
    """Concrete implementation of a quantum resource.

    This class provides quantum resource management capabilities.

    Attributes:
        _num_qubits: Number of qubits
        _quantum_type: Quantum type (superconducting, ion trap, etc.)
        _fidelity: Qubit fidelity

    Example:
        >>> quantum = QuantumResource(num_qubits=128, quantum_type="superconducting", fidelity=0.99)
        >>> quantum.allocate(64)
    """

    def __init__(
        self,
        num_qubits: int = 128,
        quantum_type: str = "superconducting",
        fidelity: float = 0.99,
        capacity: Optional[ResourceCapacity] = None,
        resource_id: Optional[ResourceID] = None,
    ) -> None:
        """Initialize a QuantumResource.

        Args:
            num_qubits: Number of qubits
            quantum_type: Quantum type
            fidelity: Qubit fidelity
            capacity: Resource capacity (default: num_qubits)
            resource_id: Optional resource identifier

        Example:
            >>> quantum = QuantumResource(num_qubits=128, quantum_type="superconducting", fidelity=0.99)
        """
        capacity = capacity or num_qubits
        super().__init__(ResourceType.QUANTUM, capacity, resource_id)
        self._num_qubits = num_qubits
        self._quantum_type = quantum_type
        self._fidelity = fidelity
        logger.debug(f"Created quantum resource with {num_qubits} qubits, type={quantum_type}")

    @property
    def num_qubits(self) -> int:
        """Get the number of qubits.

        Returns:
            Number of qubits

        Example:
            >>> print(f"Num qubits: {quantum.num_qubits}")
        """
        return self._num_qubits

    @property
    def quantum_type(self) -> str:
        """Get the quantum type.

        Returns:
            Quantum type

        Example:
            >>> print(f"Quantum type: {quantum.quantum_type}")
        """
        return self._quantum_type

    @property
    def fidelity(self) -> float:
        """Get the qubit fidelity.

        Returns:
            Qubit fidelity

        Example:
            >>> print(f"Fidelity: {quantum.fidelity}")
        """
        return self._fidelity

    def to_dict(self) -> Dict[str, Any]:
        """Convert quantum resource to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = quantum.to_dict()
        """
        data = super().to_dict()
        data.update({
            "num_qubits": self._num_qubits,
            "quantum_type": self._quantum_type,
            "fidelity": self._fidelity,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(quantum)
        """
        return f"QuantumResource(resource_id={self._resource_id}, qubits={self._num_qubits}, type={self._quantum_type})"


# Export
__all__ = [
    "QuantumResource",
]
