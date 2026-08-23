"""
Validators Module

This module provides validator definitions for the Knowledge package.

Purpose
-------
Provide validator management for knowledge validation.

Responsibilities
----------------
- Define validator structure
- Support validator operations
- Support validator validation
- Support validator metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from quantsmind.knowledge.enums import ValidationType
from quantsmind.knowledge.exceptions import ValidationError
from quantsmind.knowledge.types import ValidationResult


class Validator:
    """Concrete implementation of a validator.

    This class provides validator functionality for knowledge validation.

    Attributes:
        _id: Validator ID
        _name: Validator name
        _validation_type: Validation type
        _validate_function: Validate function
        _parameters: Validator parameters
        _metadata: Validator metadata

    Example:
        >>> validator = Validator("val_001", "Type Validator", ValidationType.TYPE)
        >>> validator.validate({"value": 42})
    """

    def __init__(
        self,
        validator_id: str,
        name: str,
        validation_type: ValidationType,
        validate_function: Callable[[Any], ValidationResult] | None = None,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Validator.

        Args:
            validator_id: Validator ID
            name: Validator name
            validation_type: Validation type
            validate_function: Validate function
            parameters: Validator parameters
            metadata: Validator metadata

        Example:
            >>> validator = Validator("val_001", "Type Validator", ValidationType.TYPE)
        """
        if not validator_id:
            raise ValidationError("Validator ID cannot be empty", {"validator_id": validator_id})

        if not name:
            raise ValidationError("Validator name cannot be empty", {"name": name})

        self._id = validator_id
        self._name = name
        self._validation_type = validation_type
        self._validate_function = validate_function
        self._parameters = parameters or {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the validator ID.

        Returns:
            Validator ID

        Example:
            >>> vid = validator.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the validator name.

        Returns:
            Validator name

        Example:
            >>> name = validator.name
        """
        return self._name

    @property
    def validation_type(self) -> ValidationType:
        """Get the validation type.

        Returns:
            Validation type

        Example:
            >>> vtype = validator.validation_type
        """
        return self._validation_type

    @property
    def parameters(self) -> dict[str, Any]:
        """Get the validator parameters.

        Returns:
            Validator parameters

        Example:
            >>> parameters = validator.parameters
        """
        return self._parameters.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the validator metadata.

        Returns:
            Validator metadata

        Example:
            >>> metadata = validator.metadata
        """
        return self._metadata.copy()

    def set_validate_function(self, validate_function: Callable[[Any], ValidationResult]) -> None:
        """Set the validate function.

        Args:
            validate_function: Validate function

        Example:
            >>> validator.set_validate_function(lambda x: (True, []))
        """
        self._validate_function = validate_function

    def set_parameter(self, key: str, value: Any) -> None:
        """Set a parameter.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> validator.set_parameter("max_length", 100)
        """
        self._parameters[key] = value

    def validate(self, data: Any) -> ValidationResult:
        """Validate data.

        Args:
            data: Data to validate

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate({"value": 42})
        """
        if self._validate_function:
            try:
                return self._validate_function(data)
            except Exception as e:
                return (False, [f"Validation error: {str(e)}"])

        # Default validation
        return (True, [])

    def validate_all(self, data_list: list[Any]) -> dict[str, ValidationResult]:
        """Validate multiple data items.

        Args:
            data_list: List of data to validate

        Returns:
            Dictionary of validation results

        Example:
            >>> results = validator.validate_all([{"value": 42}, {"value": 43}])
        """
        results = {}
        for i, data in enumerate(data_list):
            results[f"item_{i}"] = self.validate(data)
        return results

    def validate_self(self) -> ValidationResult:
        """Validate the validator itself.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_self()
        """
        errors = []

        if not self._id:
            errors.append("Validator ID cannot be empty")

        if not self._name:
            errors.append("Validator name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Validator definition

        Example:
            >>> data = validator.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "validation_type": self._validation_type.value,
            "parameters": self._parameters,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(validator)
        """
        return f"Validator(id={self._id}, name={self._name}, type={self._validation_type.value})"


class ValidatorRegistry:
    """Registry for validators.

    This class provides validator registry functionality.

    Attributes:
        _validators: Registered validators

    Example:
        >>> registry = ValidatorRegistry()
        >>> registry.register(Validator("val_001", "Type Validator", ValidationType.TYPE))
    """

    def __init__(self) -> None:
        """Initialize a ValidatorRegistry.

        Example:
            >>> registry = ValidatorRegistry()
        """
        self._validators: dict[str, Validator] = {}

    def register(self, validator: Validator) -> None:
        """Register a validator.

        Args:
            validator: Validator to register

        Example:
            >>> registry.register(Validator("val_001", "Type Validator", ValidationType.TYPE))
        """
        self._validators[validator.id] = validator

    def unregister(self, validator_id: str) -> bool:
        """Unregister a validator.

        Args:
            validator_id: Validator ID

        Returns:
            True if unregistered

        Example:
            >>> unregistered = registry.unregister("val_001")
        """
        if validator_id in self._validators:
            del self._validators[validator_id]
            return True
        return False

    def get(self, validator_id: str) -> Validator | None:
        """Get a validator by ID.

        Args:
            validator_id: Validator ID

        Returns:
            Validator or None

        Example:
            >>> validator = registry.get("val_001")
        """
        return self._validators.get(validator_id)

    def get_by_type(self, validation_type: ValidationType) -> list[Validator]:
        """Get validators by type.

        Args:
            validation_type: Validation type

        Returns:
            List of validators

        Example:
            >>> validators = registry.get_by_type(ValidationType.TYPE)
        """
        return [v for v in self._validators.values() if v.validation_type == validation_type]

    def list_all(self) -> list[Validator]:
        """List all registered validators.

        Returns:
            List of validators

        Example:
            >>> validators = registry.list_all()
        """
        return list(self._validators.values())

    def count(self) -> int:
        """Get the number of registered validators.

        Returns:
            Number of validators

        Example:
            >>> count = registry.count()
        """
        return len(self._validators)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Registry state

        Example:
            >>> data = registry.to_dict()
        """
        return {
            "validators": [validator.to_dict() for validator in self._validators.values()],
            "count": len(self._validators),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(registry)
        """
        return f"ValidatorRegistry(validators={len(self._validators)})"


# Export
__all__ = [
    "Validator",
    "ValidatorRegistry",
]
