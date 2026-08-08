"""
Noise Model Module

This module provides noise model definitions for the Quantum package.

Purpose
-------
Provide noise model management for quantum computing operations.

Responsibilities
----------------
- Define noise model structure
- Support noise model operations
- Support noise model validation
- Support noise model metadata

Dependencies
------------
typing (standard library)
quantsmind.quantum.algorithms.exceptions (quantum exceptions)
quantsmind.quantum.algorithms.types (quantum types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.quantum.algorithms.exceptions import NoiseError
from quantsmind.quantum.algorithms.types import ValidationResult


class NoiseModel:
    """Concrete implementation of a noise model.

    This class provides noise model functionality for quantum computing.

    Attributes:
        _name: Noise model name
        _noise_type: Noise type
        _parameters: Noise parameters
        _metadata: Noise model metadata

    Example:
        >>> noise_model = NoiseModel("bit_flip", {"probability": 0.01})
    """

    def __init__(
        self,
        name: str,
        noise_type: str,
        parameters: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a NoiseModel.

        Args:
            name: Noise model name
            noise_type: Noise type
            parameters: Noise parameters
            metadata: Noise model metadata

        Example:
            >>> noise_model = NoiseModel("bit_flip", {"probability": 0.01})
        """
        if not name:
            raise NoiseError("Noise model name cannot be empty", {"name": name})

        self._name = name
        self._noise_type = noise_type
        self._parameters = parameters or {}
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the noise model name.

        Returns:
            Noise model name

        Example:
            >>> name = noise_model.name
        """
        return self._name

    @property
    def noise_type(self) -> str:
        """Get the noise type.

        Returns:
            Noise type

        Example:
            >>> ntype = noise_model.noise_type
        """
        return self._noise_type

    @property
    def parameters(self) -> Dict[str, float]:
        """Get the noise parameters.

        Returns:
            Noise parameters

        Example:
            >>> params = noise_model.parameters
        """
        return self._parameters.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the noise model metadata.

        Returns:
            Noise model metadata

        Example:
            >>> metadata = noise_model.metadata
        """
        return self._metadata.copy()

    def set_parameter(self, key: str, value: float) -> None:
        """Set a noise parameter.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> noise_model.set_parameter("probability", 0.02)
        """
        self._parameters[key] = value

    def get_parameter(self, key: str, default: Optional[float] = None) -> Optional[float]:
        """Get a noise parameter.

        Args:
            key: Parameter key
            default: Default value

        Returns:
            Parameter value or default

        Example:
            >>> prob = noise_model.get_parameter("probability", 0.0)
        """
        return self._parameters.get(key, default)

    def validate(self) -> ValidationResult:
        """Validate the noise model.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = noise_model.validate()
        """
        errors = []

        if not self._name:
            errors.append("Noise model name cannot be empty")

        if not self._noise_type:
            errors.append("Noise type cannot be empty")

        # Validate probability parameters
        for key, value in self._parameters.items():
            if "probability" in key.lower() or "rate" in key.lower():
                if value < 0 or value > 1:
                    errors.append(f"Parameter {key} must be between 0 and 1, got {value}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Noise model definition

        Example:
            >>> data = noise_model.to_dict()
        """
        return {
            "name": self._name,
            "noise_type": self._noise_type,
            "parameters": self._parameters,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(noise_model)
        """
        return f"NoiseModel(name={self._name}, type={self._noise_type})"
