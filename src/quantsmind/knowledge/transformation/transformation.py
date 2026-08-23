"""
Transformation Module

This module provides transformation definitions for the Knowledge package.

Purpose
-------
Provide transformation management for data transformations.

Responsibilities
----------------
- Define transformation structure
- Support transformation operations
- Support transformation validation
- Support transformation metadata

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

from quantsmind.knowledge.enums import TransformationType
from quantsmind.knowledge.exceptions import TransformationError
from quantsmind.knowledge.types import ValidationResult


class Transformation:
    """Concrete implementation of a transformation.

    This class provides transformation functionality.

    Attributes:
        _id: Transformation ID
        _name: Transformation name
        _transformation_type: Transformation type
        _transform_function: Transform function
        _parameters: Transformation parameters
        _metadata: Transformation metadata

    Example:
        >>> transformation = Transformation("trans_001", "normalize", "normalization")
        >>> transformation.apply({"value": 42})
    """

    def __init__(
        self,
        transformation_id: str,
        name: str,
        transformation_type: TransformationType,
        transform_function: Callable[[Any], Any] | None = None,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Transformation.

        Args:
            transformation_id: Transformation ID
            name: Transformation name
            transformation_type: Transformation type
            transform_function: Transform function
            parameters: Transformation parameters
            metadata: Transformation metadata

        Example:
            >>> transformation = Transformation("trans_001", "normalize", TransformationType.NORMALIZATION)
        """
        if not transformation_id:
            raise TransformationError("Transformation ID cannot be empty", {"transformation_id": transformation_id})

        if not name:
            raise TransformationError("Transformation name cannot be empty", {"name": name})

        self._id = transformation_id
        self._name = name
        self._transformation_type = transformation_type
        self._transform_function = transform_function
        self._parameters = parameters or {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the transformation ID.

        Returns:
            Transformation ID

        Example:
            >>> tid = transformation.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the transformation name.

        Returns:
            Transformation name

        Example:
            >>> name = transformation.name
        """
        return self._name

    @property
    def transformation_type(self) -> TransformationType:
        """Get the transformation type.

        Returns:
            Transformation type

        Example:
            >>> ttype = transformation.transformation_type
        """
        return self._transformation_type

    @property
    def parameters(self) -> dict[str, Any]:
        """Get the transformation parameters.

        Returns:
            Transformation parameters

        Example:
            >>> parameters = transformation.parameters
        """
        return self._parameters.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the transformation metadata.

        Returns:
            Transformation metadata

        Example:
            >>> metadata = transformation.metadata
        """
        return self._metadata.copy()

    def set_transform_function(self, transform_function: Callable[[Any], Any]) -> None:
        """Set the transform function.

        Args:
            transform_function: Transform function

        Example:
            >>> transformation.set_transform_function(lambda x: x / max_value)
        """
        self._transform_function = transform_function

    def set_parameter(self, key: str, value: Any) -> None:
        """Set a parameter.

        Args:
            key: Parameter key
            value: Parameter value

        Example:
            >>> transformation.set_parameter("scale", 1.0)
        """
        self._parameters[key] = value

    def apply(self, data: Any) -> Any:
        """Apply the transformation to data.

        Args:
            data: Data to transform

        Returns:
            Transformed data

        Example:
            >>> result = transformation.apply({"value": 42})
        """
        if self._transform_function:
            try:
                return self._transform_function(data)
            except Exception as e:
                raise TransformationError(f"Transformation failed: {str(e)}", {"transformation_id": self._id})

        return data

    def validate(self) -> ValidationResult:
        """Validate the transformation.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = transformation.validate()
        """
        errors = []

        if not self._id:
            errors.append("Transformation ID cannot be empty")

        if not self._name:
            errors.append("Transformation name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Transformation definition

        Example:
            >>> data = transformation.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "transformation_type": self._transformation_type.value,
            "parameters": self._parameters,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(transformation)
        """
        return f"Transformation(id={self._id}, name={self._name}, type={self._transformation_type.value})"


# Export
__all__ = [
    "Transformation",
]
