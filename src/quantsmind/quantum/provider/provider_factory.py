"""
Provider Factory Module

This module provides provider factory definitions for the Quantum package.

Purpose
-------
Provide provider factory management for quantum computing operations.

Responsibilities
----------------
- Define provider factory structure
- Support provider factory operations
- Support provider factory validation
- Support provider factory metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.enums (quantum enumerations)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
quantsmind.quantum.provider.provider (provider module)
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.algorithms.enums import ProviderType
from quantsmind.quantum.algorithms.exceptions import ProviderError
from quantsmind.quantum.algorithms.types import ValidationResult
from quantsmind.quantum.provider.provider import QuantumProvider


class ProviderFactory:
    """Concrete implementation of a provider factory.

    This class provides provider factory functionality for quantum computing.

    Attributes:
        _name: Factory name
        _provider_types: Supported provider types
        _metadata: Factory metadata

    Example:
        >>> factory = ProviderFactory()
        >>> provider = factory.create_provider("IBM", ProviderType.IBM)
    """

    def __init__(
        self,
        name: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a ProviderFactory.

        Args:
            name: Factory name
            metadata: Factory metadata

        Example:
            >>> factory = ProviderFactory()
        """
        self._name = name
        self._provider_types = list(ProviderType)
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the factory name.

        Returns:
            Factory name

        Example:
            >>> name = factory.name
        """
        return self._name

    @property
    def supported_types(self) -> list:
        """Get the supported provider types.

        Returns:
            List of provider types

        Example:
            >>> types = factory.supported_types
        """
        return self._provider_types.copy()

    def create_provider(
        self,
        name: str,
        provider_type: ProviderType,
        credentials: dict[str, Any] | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> QuantumProvider:
        """Create a provider instance.

        Args:
            name: Provider name
            provider_type: Provider type
            credentials: Provider credentials
            configuration: Provider configuration

        Returns:
            Provider instance

        Example:
            >>> provider = factory.create_provider("IBM", ProviderType.IBM)
        """
        if provider_type not in self._provider_types:
            raise ProviderError(f"Provider type {provider_type} not supported", {"supported_types": self._provider_types})

        return QuantumProvider(name, provider_type, credentials, configuration)

    def create_ibm_provider(
        self,
        credentials: dict[str, Any] | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> QuantumProvider:
        """Create an IBM provider.

        Args:
            credentials: Provider credentials
            configuration: Provider configuration

        Returns:
            IBM provider

        Example:
            >>> provider = factory.create_ibm_provider({"token": "my_token"})
        """
        return self.create_provider("IBM", ProviderType.IBM, credentials, configuration)

    def create_google_provider(
        self,
        credentials: dict[str, Any] | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> QuantumProvider:
        """Create a Google provider.

        Args:
            credentials: Provider credentials
            configuration: Provider configuration

        Returns:
            Google provider

        Example:
            >>> provider = factory.create_google_provider()
        """
        return self.create_provider("Google", ProviderType.GOOGLE, credentials, configuration)

    def create_aws_braket_provider(
        self,
        credentials: dict[str, Any] | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> QuantumProvider:
        """Create an AWS Braket provider.

        Args:
            credentials: Provider credentials
            configuration: Provider configuration

        Returns:
            AWS Braket provider

        Example:
            >>> provider = factory.create_aws_braket_provider()
        """
        return self.create_provider("AWS_Braket", ProviderType.AWS_BRAKET, credentials, configuration)

    def create_azure_quantum_provider(
        self,
        credentials: dict[str, Any] | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> QuantumProvider:
        """Create an Azure Quantum provider.

        Args:
            credentials: Provider credentials
            configuration: Provider configuration

        Returns:
            Azure Quantum provider

        Example:
            >>> provider = factory.create_azure_quantum_provider()
        """
        return self.create_provider("Azure_Quantum", ProviderType.AZURE_QUANTUM, credentials, configuration)

    def create_ionq_provider(
        self,
        credentials: dict[str, Any] | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> QuantumProvider:
        """Create an IonQ provider.

        Args:
            credentials: Provider credentials
            configuration: Provider configuration

        Returns:
            IonQ provider

        Example:
            >>> provider = factory.create_ionq_provider()
        """
        return self.create_provider("IonQ", ProviderType.IONQ, credentials, configuration)

    def create_rigetti_provider(
        self,
        credentials: dict[str, Any] | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> QuantumProvider:
        """Create a Rigetti provider.

        Args:
            credentials: Provider credentials
            configuration: Provider configuration

        Returns:
            Rigetti provider

        Example:
            >>> provider = factory.create_rigetti_provider()
        """
        return self.create_provider("Rigetti", ProviderType.RIGETTI, credentials, configuration)

    def create_quantinuum_provider(
        self,
        credentials: dict[str, Any] | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> QuantumProvider:
        """Create a Quantinuum provider.

        Args:
            credentials: Provider credentials
            configuration: Provider configuration

        Returns:
            Quantinuum provider

        Example:
            >>> provider = factory.create_quantinuum_provider()
        """
        return self.create_provider("Quantinuum", ProviderType.QUANTINUUM, credentials, configuration)

    def create_xanadu_provider(
        self,
        credentials: dict[str, Any] | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> QuantumProvider:
        """Create a Xanadu provider.

        Args:
            credentials: Provider credentials
            configuration: Provider configuration

        Returns:
            Xanadu provider

        Example:
            >>> provider = factory.create_xanadu_provider()
        """
        return self.create_provider("Xanadu", ProviderType.XANADU, credentials, configuration)

    def validate(self) -> ValidationResult:
        """Validate the factory.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = factory.validate()
        """
        errors = []

        if not self._name:
            errors.append("Factory name cannot be empty")

        if not self._provider_types:
            errors.append("No provider types supported")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Factory definition

        Example:
            >>> data = factory.to_dict()
        """
        return {
            "name": self._name,
            "supported_types": [pt.value for pt in self._provider_types],
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(factory)
        """
        return f"ProviderFactory(name={self._name}, types={len(self._provider_types)})"


# Export
__all__ = [
    "ProviderFactory",
]
