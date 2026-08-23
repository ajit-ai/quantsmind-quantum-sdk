"""
Math Object Module

This module provides the base mathematical object for the QuantsMind SDK.

Purpose
-------
Provide the foundational class for all mathematical objects in the SDK.

Classes
-------
MathObject: Base class for all mathematical objects

Responsibilities
----------------
- Provide common mathematical object interface
- Support validation
- Support serialization
- Support comparison
- Support evaluation

Dependencies
------------
typing (standard library)
abc (standard library)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MathObject(ABC):
    """Abstract base class for all mathematical objects.

    This class provides the foundational interface for all mathematical objects
    in the QuantsMind SDK, including expressions, formulas, equations, variables,
    and parameters.

    Attributes:
        _id: Unique identifier
        _name: Object name
        _metadata: Additional metadata

    Example:
        >>> class MyMathObject(MathObject):
        ...     def evaluate(self, **kwargs):
        ...         return 42
        >>> obj = MyMathObject("my_object")
    """

    def __init__(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a MathObject.

        Args:
            name: Object name
            metadata: Additional metadata

        Example:
            >>> obj = MathObject("my_object")
        """
        self._id = id(self)
        self._name = name
        self._metadata = metadata or {}

    @property
    def id(self) -> int:
        """Get the unique identifier.

        Returns:
            Unique identifier

        Example:
            >>> obj_id = obj.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the object name.

        Returns:
            Object name

        Example:
            >>> name = obj.name
        """
        return self._name

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> metadata = obj.metadata
        """
        return self._metadata.copy()

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the mathematical object.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = obj.validate()
        """
        errors = []

        if not self._name:
            errors.append("Name cannot be empty")

        return (len(errors) == 0, errors)

    @abstractmethod
    def evaluate(self, **kwargs: Any) -> Any:
        """Evaluate the mathematical object.

        Args:
            **kwargs: Evaluation context variables

        Returns:
            Evaluated result

        Example:
            >>> result = obj.evaluate(x=1, y=2)
        """
        pass

    def serialize(self) -> dict[str, Any]:
        """Serialize the mathematical object to a dictionary.

        Returns:
            Serialized representation

        Example:
            >>> data = obj.serialize()
        """
        return {
            "id": self._id,
            "name": self._name,
            "type": self.__class__.__name__,
            "metadata": self._metadata,
        }

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> MathObject:
        """Deserialize a dictionary to a mathematical object.

        Args:
            data: Serialized data

        Returns:
            Mathematical object

        Example:
            >>> obj = MathObject.deserialize(data)
        """
        # Base implementation - subclasses should override
        return cls(data.get("name", ""), data.get("metadata"))

    def clone(self) -> MathObject:
        """Clone the mathematical object.

        Returns:
            Cloned object

        Example:
            >>> cloned = obj.clone()
        """
        # Base implementation - subclasses may override for deep copy
        return self.__class__(self._name, self._metadata.copy())

    def compare(self, other: MathObject) -> int:
        """Compare with another mathematical object.

        Args:
            other: Object to compare with

        Returns:
            -1 if less, 0 if equal, 1 if greater

        Example:
            >>> cmp = obj.compare(other)
        """
        if not isinstance(other, MathObject):
            raise TypeError(f"Cannot compare MathObject with {type(other)}")

        if self._id == other._id:
            return 0
        return -1 if self._id < other._id else 1

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare

        Returns:
            True if equal

        Example:
            >>> is_equal = obj == other
        """
        if not isinstance(other, MathObject):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Get hash value.

        Returns:
            Hash value

        Example:
            >>> h = hash(obj)
        """
        return hash(self._id)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(obj)
        """
        return f"{self.__class__.__name__}(name={self._name})"


__all__ = [
    "MathObject",
]
