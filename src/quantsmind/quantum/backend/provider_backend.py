"""
Provider Backend Module

This module provides provider backend definitions for the Quantum package.

Purpose
-------
Provide provider backend management for quantum computing operations.

Responsibilities
----------------
- Define provider backend structure
- Support provider backend operations
- Support provider backend validation
- Support provider backend metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.backend.backend (backend module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.enums import BackendType, ProviderType
from quantsmind.quantum.algorithms.exceptions import BackendError
from quantsmind.quantum.algorithms.types import BackendConfig, ValidationResult
from quantsmind.quantum.backend.backend import QuantumBackend
from quantsmind.quantum.circuit.circuit import QuantumCircuit


class ProviderBackend(QuantumBackend):
    """Concrete implementation of a provider backend.

    This class provides provider backend functionality for quantum computing.
    Provider backends connect to external quantum hardware providers.

    Attributes:
        _name: Backend name
        _num_qubits: Number of qubits
        _provider_type: Provider type
        _provider_name: Provider name
        _configuration: Backend configuration
        _metadata: Backend metadata

    Example:
        >>> backend = ProviderBackend("ibmq_manila", ProviderType.IBM, "IBM", 5)
        >>> result = backend.run(circuit, shots=1024)
    """

    def __init__(
        self,
        name: str,
        provider_type: ProviderType,
        provider_name: str,
        num_qubits: int,
        configuration: BackendConfig | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a ProviderBackend.

        Args:
            name: Backend name
            provider_type: Provider type
            provider_name: Provider name
            num_qubits: Number of qubits
            configuration: Backend configuration
            metadata: Backend metadata

        Example:
            >>> backend = ProviderBackend("ibmq_manila", ProviderType.IBM, "IBM", 5)
        """
        super().__init__(name, BackendType.PROVIDER, num_qubits, configuration, metadata)
        self._provider_type = provider_type
        self._provider_name = provider_name

    @property
    def provider_type(self) -> ProviderType:
        """Get the provider type.

        Returns:
            Provider type

        Example:
            >>> ptype = backend.provider_type
        """
        return self._provider_type

    @property
    def provider_name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name

        Example:
            >>> pname = backend.provider_name
        """
        return self._provider_name

    def set_provider_type(self, provider_type: ProviderType) -> None:
        """Set the provider type.

        Args:
            provider_type: Provider type

        Example:
            >>> backend.set_provider_type(ProviderType.GOOGLE)
        """
        self._provider_type = provider_type

    def set_provider_name(self, provider_name: str) -> None:
        """Set the provider name.

        Args:
            provider_name: Provider name

        Example:
            >>> backend.set_provider_name("Google")
        """
        self._provider_name = provider_name

    def run(self, circuit: QuantumCircuit, shots: int = 1024) -> dict[str, Any]:
        """Run a circuit on the provider backend.

        Args:
            circuit: Circuit to run
            shots: Number of shots

        Returns:
            Job result

        Example:
            >>> result = backend.run(circuit, shots=1000)
        """
        # Validate circuit
        if circuit.num_qubits > self._num_qubits:
            raise BackendError(f"Circuit requires {circuit.num_qubits} qubits, backend has {self._num_qubits}", {"circuit_qubits": circuit.num_qubits, "backend_qubits": self._num_qubits})

        # Placeholder implementation - actual execution requires provider connection
        result = super().run(circuit, shots)
        result["provider_type"] = self._provider_type.value
        result["provider_name"] = self._provider_name
        result["job_id"] = "placeholder_job_id"
        return result

    def validate(self) -> ValidationResult:
        """Validate the provider backend.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = backend.validate()
        """
        errors = []

        # Validate base backend
        is_valid, base_errors = super().validate()
        errors.extend(base_errors)

        if self._provider_type not in ProviderType:
            errors.append(f"Invalid provider type: {self._provider_type}")

        if not self._provider_name:
            errors.append("Provider name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Provider backend definition

        Example:
            >>> data = backend.to_dict()
        """
        data = super().to_dict()
        data["provider_type"] = self._provider_type.value
        data["provider_name"] = self._provider_name
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(backend)
        """
        return f"ProviderBackend(name={self._name}, provider={self._provider_name}, qubits={self._num_qubits})"


# Export
__all__ = [
    "ProviderBackend",
]
