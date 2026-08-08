"""
Transformation Module

This module provides transformation mappings within the QuantsMind SDK.
Transformation represents mappings that convert entities, states, or systems from one representation to another.

Purpose
-------
Provide transformation mappings for entities and systems in the Foundation package.

Scientific Meaning
------------------
Transformation represents mappings: coordinate transformations, basis changes,
quantum gate operations, chemical reaction transformations, biological state transitions,
financial instrument conversions.

Responsibilities
----------------
- Manage transformation rules
- Support transformation execution
- Enable transformation serialization
- Handle transformation composition
- Support transformation validation

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.enums (enumeration types)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Transformation optimization
- Transformation caching
- Distributed transformation
- Transformation versioning
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable, Dict, Optional, Tuple

from quantsmind.foundation.constants import DEFAULT_TRANSFORMATION_TYPE
from quantsmind.foundation.enums import TransformationType
from quantsmind.foundation.exceptions import (
    CompositionError,
    ExecutionError as TransformationExecutionError,
    InvalidTransformationError,
    TransformationError,
)
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation/types import (
    MetadataDict,
    SerializedData,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Transformation(Serializable, Validatable):
    """Concrete implementation of transformation mappings.

    This class provides a flexible transformation representation with support for
    callable transformation functions, composition, and validation.

    Scientific Meaning
    ------------------
    In scientific computing, transformations represent mappings:
    coordinate transformations, basis changes, quantum gate operations,
    chemical reaction transformations, biological state transitions.

    Attributes:
        _id: Unique transformation identifier
        _name: Transformation name
        _rule: Transformation rule (callable)
        _transformation_type: Type of transformation
        _metadata: Additional metadata

    Example:
        >>> def scale_transform(context):
        ...     return (True, context["value"] * 2, [])
        >>> transform = Transformation(name="scale", rule=scale_transform)
        >>> result = transform.apply({"value": 5})
    """

    def __init__(
        self,
        name: str,
        rule: Callable[[Dict[str, Any]], Tuple[bool, Any, list[str]]],
        transformation_type: TransformationType = TransformationType.CUSTOM,
        metadata: Optional[MetadataDict] = None,
    ) -> None:
        """Initialize a Transformation.

        Args:
            name: Transformation name
            rule: Transformation rule (callable)
            transformation_type: Type of transformation
            metadata: Optional metadata dictionary

        Raises:
            InvalidTransformationError: If rule is invalid

        Example:
            >>> def scale_transform(context):
            ...     return (True, context["value"] * 2, [])
            >>> transform = Transformation(name="scale", rule=scale_transform)
        """
        self._id: str = str(uuid.uuid4())
        self._name: str = name
        self._rule: Callable[[Dict[str, Any]], tuple[bool, Any, list[str]]] = rule
        self._transformation_type: TransformationType = transformation_type
        self._metadata: MetadataDict = metadata or {}

        self._validate_rule()
        logger.debug(f"Created transformation: {name}")

    def _validate_rule(self) -> None:
        """Validate the transformation rule.

        Raises:
            InvalidTransformationError: If rule is invalid
        """
        if not callable(self._rule):
            raise InvalidTransformationError("Transformation rule must be callable")

    @property
    def id(self) -> str:
        """Get the transformation ID.

        Returns:
            Transformation ID

        Example:
            >>> print(f"ID: {transformation.id}")
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the transformation name.

        Returns:
            Transformation name

        Example:
            >>> print(f"Name: {transformation.name}")
        """
        return self._name

    @property
    def rule(self) -> Callable[[Dict[str, Any]], Tuple[bool, Any, list[str]]]:
        """Get the transformation rule.

        Returns:
            Transformation rule

        Example:
            >>> print(f"Rule: {transformation.rule}")
        """
        return self._rule

    @property
    def transformation_type(self) -> TransformationType:
        """Get the transformation type.

        Returns:
            Transformation type

        Example:
            >>> print(f"Type: {transformation.transformation_type}")
        """
        return self._transformation_type

    @property
    def metadata(self) -> MetadataDict:
        """Get the transformation metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {transformation.metadata}")
        """
        return self._metadata.copy()

    def apply(self, context: Dict[str, Any]) -> Tuple[bool, Any, list[str]]:
        """Apply the transformation.

        Args:
            context: Application context

        Returns:
            Tuple of (success, result, messages)

        Raises:
            TransformationExecutionError: If execution fails

        Example:
            >>> result = transformation.apply({"value": 5})
        """
        try:
            logger.debug(f"Applying transformation {self._name}")
            return self._rule(context)
        except Exception as e:
            raise TransformationExecutionError(f"Transformation execution failed: {e}") from e

    def compose(self, other: "Transformation") -> "Transformation":
        """Compose this transformation with another.

        Args:
            other: Other transformation to compose with

        Returns:
            New composed transformation

        Raises:
            CompositionError: If composition fails

        Example:
            >>> composed = transform1.compose(transform2)
        """
        def composed_rule(context: Dict[str, Any]) -> Tuple[bool, Any, list[str]]:
            success1, result1, messages1 = self._rule(context)
            if not success1:
                return (False, result1, messages1)
            context["intermediate"] = result1
            return other._rule(context)

        return Transformation(
            name=f"{self._name}_then_{other._name}",
            rule=composed_rule,
            transformation_type=TransformationType.COMPOSED,
        )

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the transformation to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = transformation.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "id": self._id,
            "name": self._name,
            "rule": self._rule.__name__ if callable(self._rule) else str(self._rule),
            "type": self._transformation_type.value,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> "Transformation":
        """Deserialize the transformation from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Transformation instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidTransformationError: If data is invalid

        Note:
            Callable rules cannot be fully serialized. This method creates
            a placeholder transformation that must be configured with actual rules.
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            # Create a placeholder rule
            def placeholder_rule(context: Dict[str, Any]) -> Tuple[bool, Any, list[str]]:
                return (True, None, ["Placeholder rule executed"])

            return cls(
                name=obj["name"],
                rule=placeholder_rule,
                transformation_type=TransformationType(obj["type"]),
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidTransformationError(f"Failed to deserialize transformation: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the transformation is serializable.

        Returns:
            True (transformations are serializable, but callables are not fully preserved)

        Example:
            >>> if transformation.is_serializable():
            ...     data = transformation.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Transformation.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the transformation.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = transformation.validate()
        """
        errors: list[str] = []

        try:
            self._validate_rule()
        except InvalidTransformationError as e:
            errors.append(str(e))

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = transformation.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = transformation.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the transformation.

        Returns:
            String representation

        Example:
            >>> repr(transformation)
        """
        return f"Transformation(name='{self._name}', type={self._transformation_type.value})"

    def __str__(self) -> str:
        """Return string representation of the transformation.

        Returns:
            String representation

        Example:
            >>> str(transformation)
        """
        return self._name

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> transform1 == transform2
        """
        if not isinstance(other, Transformation):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash of the transformation.

        Returns:
            Hash value

        Example:
            >>> hash(transformation)
        """
        return hash(self._id)


# Export
__all__ = ["Transformation"]
