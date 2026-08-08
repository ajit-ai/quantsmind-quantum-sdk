"""
Mapper Module

This module provides mapper definitions for the Knowledge package.

Purpose
-------
Provide mapper management for data mapping transformations.

Responsibilities
----------------
- Define mapper structure
- Support mapper operations
- Support mapper validation
- Support mapper metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from quantsmind.knowledge.enums import TransformationType
from quantsmind.knowledge.exceptions import TransformationError
from quantsmind.knowledge.types import ValidationResult


class Mapper:
    """Concrete implementation of a mapper.

    This class provides mapper functionality for mapping data between schemas.

    Attributes:
        _id: Mapper ID
        _name: Mapper name
        _source_schema: Source schema
        _target_schema: Target schema
        _field_mappings: Field mappings
        _metadata: Mapper metadata

    Example:
        >>> mapper = Mapper("mapper_001", "Schema A to B")
        >>> mapper.add_field_mapping("field_a", "field_b")
    """

    def __init__(
        self,
        mapper_id: str,
        name: str,
        source_schema: Optional[str] = None,
        target_schema: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Mapper.

        Args:
            mapper_id: Mapper ID
            name: Mapper name
            source_schema: Source schema name
            target_schema: Target schema name
            metadata: Mapper metadata

        Example:
            >>> mapper = Mapper("mapper_001", "Schema A to B")
        """
        if not mapper_id:
            raise TransformationError("Mapper ID cannot be empty", {"mapper_id": mapper_id})

        if not name:
            raise TransformationError("Mapper name cannot be empty", {"name": name})

        self._id = mapper_id
        self._name = name
        self._source_schema = source_schema
        self._target_schema = target_schema
        self._field_mappings: Dict[str, tuple[str, Optional[Callable[[Any], Any]]]] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the mapper ID.

        Returns:
            Mapper ID

        Example:
            >>> mid = mapper.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the mapper name.

        Returns:
            Mapper name

        Example:
            >>> name = mapper.name
        """
        return self._name

    @property
    def source_schema(self) -> Optional[str]:
        """Get the source schema.

        Returns:
            Source schema name

        Example:
            >>> source = mapper.source_schema
        """
        return self._source_schema

    @property
    def target_schema(self) -> Optional[str]:
        """Get the target schema.

        Returns:
            Target schema name

        Example:
            >>> target = mapper.target_schema
        """
        return self._target_schema

    @property
    def field_mappings(self) -> Dict[str, str]:
        """Get the field mappings.

        Returns:
            Field mappings (source -> target)

        Example:
            >>> mappings = mapper.field_mappings
        """
        return {source: target for source, (target, _) in self._field_mappings.items()}

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the mapper metadata.

        Returns:
            Mapper metadata

        Example:
            >>> metadata = mapper.metadata
        """
        return self._metadata.copy()

    def add_field_mapping(self, source_field: str, target_field: str, transform: Optional[Callable[[Any], Any]] = None) -> None:
        """Add a field mapping.

        Args:
            source_field: Source field name
            target_field: Target field name
            transform: Optional transform function

        Example:
            >>> mapper.add_field_mapping("field_a", "field_b")
        """
        self._field_mappings[source_field] = (target_field, transform)

    def remove_field_mapping(self, source_field: str) -> bool:
        """Remove a field mapping.

        Args:
            source_field: Source field name

        Returns:
            True if removed

        Example:
            >>> removed = mapper.remove_field_mapping("field_a")
        """
        if source_field in self._field_mappings:
            del self._field_mappings[source_field]
            return True
        return False

    def map(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map data from source to target schema.

        Args:
            data: Source data

        Returns:
            Mapped data

        Example:
            >>> result = mapper.map({"field_a": 42})
        """
        result = {}

        for source_field, (target_field, transform) in self._field_mappings.items():
            if source_field in data:
                value = data[source_field]
                if transform:
                    try:
                        value = transform(value)
                    except Exception as e:
                        raise TransformationError(f"Transform failed for field '{source_field}': {str(e)}", {"mapper_id": self._id})
                result[target_field] = value

        return result

    def validate(self) -> ValidationResult:
        """Validate the mapper.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = mapper.validate()
        """
        errors = []

        if not self._id:
            errors.append("Mapper ID cannot be empty")

        if not self._name:
            errors.append("Mapper name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Mapper definition

        Example:
            >>> data = mapper.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "source_schema": self._source_schema,
            "target_schema": self._target_schema,
            "field_mappings": self.field_mappings,
            "mapping_count": len(self._field_mappings),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(mapper)
        """
        return f"Mapper(id={self._id}, name={self._name}, mappings={len(self._field_mappings)})"


# Export
__all__ = [
    "Mapper",
]
