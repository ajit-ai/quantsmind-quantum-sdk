"""
Schema Module

This module provides schema definitions for the Knowledge package.

Purpose
-------
Provide schema management and validation.

Responsibilities
----------------
- Define schema structure
- Support schema operations
- Support schema validation
- Support schema evolution

Dependencies
------------
typing (standard library)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.types import ValidationResult


class Schema:
    """Concrete implementation of a schema.

    This class provides schema functionality.

    Attributes:
        _schema_name: Schema name
        _fields: Schema fields
        _version: Schema version
        _metadata: Schema metadata

    Example:
        >>> schema = Schema("my_schema", [{"name": "field1", "type": "string"}])
        >>> schema.validate({"field1": "value"})
    """

    def __init__(
        self,
        schema_name: str,
        fields: list[dict[str, Any]],
        version: str = "1.0.0",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Schema.

        Args:
            schema_name: Schema name
            fields: Schema fields
            version: Schema version
            metadata: Schema metadata

        Example:
            >>> schema = Schema("my_schema", [{"name": "field1", "type": "string"}])
        """
        self._schema_name = schema_name
        self._fields = fields
        self._version = version
        self._metadata = metadata or {}

    @property
    def schema_name(self) -> str:
        """Get the schema name.

        Returns:
            Schema name

        Example:
            >>> name = schema.schema_name
        """
        return self._schema_name

    @property
    def fields(self) -> list[dict[str, Any]]:
        """Get the schema fields.

        Returns:
            Schema fields

        Example:
            >>> fields = schema.fields
        """
        return self._fields.copy()

    @property
    def version(self) -> str:
        """Get the schema version.

        Returns:
            Schema version

        Example:
            >>> version = schema.version
        """
        return self._version

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the schema metadata.

        Returns:
            Schema metadata

        Example:
            >>> metadata = schema.metadata
        """
        return self._metadata.copy()

    def add_field(self, field: dict[str, Any]) -> None:
        """Add a field to the schema.

        Args:
            field: Field definition

        Example:
            >>> schema.add_field({"name": "field2", "type": "int"})
        """
        self._fields.append(field)

    def remove_field(self, field_name: str) -> bool:
        """Remove a field from the schema.

        Args:
            field_name: Field name

        Returns:
            True if removed

        Example:
            >>> removed = schema.remove_field("field1")
        """
        for i, field in enumerate(self._fields):
            if field.get("name") == field_name:
                del self._fields[i]
                return True
        return False

    def get_field(self, field_name: str) -> dict[str, Any] | None:
        """Get a field by name.

        Args:
            field_name: Field name

        Returns:
            Field definition or None

        Example:
            >>> field = schema.get_field("field1")
        """
        for field in self._fields:
            if field.get("name") == field_name:
                return field
        return None

    def get_required_fields(self) -> list[str]:
        """Get required field names.

        Returns:
            List of required field names

        Example:
            >>> required = schema.get_required_fields()
        """
        return [field["name"] for field in self._fields if field.get("required", False)]

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        """Validate data against the schema.

        Args:
            data: Data to validate

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = schema.validate({"field1": "value"})
        """
        errors = []

        # Check required fields
        required_fields = self.get_required_fields()
        for field_name in required_fields:
            if field_name not in data:
                errors.append(f"Required field '{field_name}' is missing")

        # Validate field types
        for field in self._fields:
            field_name = field.get("name")
            field_type = field.get("type")

            if field_name in data:
                value = data[field_name]
                if not self._validate_type(value, field_type):
                    errors.append(f"Field '{field_name}' has invalid type, expected {field_type}")

                # Check constraints
                if "min" in field and isinstance(value, (int, float)):
                    if value < field["min"]:
                        errors.append(f"Field '{field_name}' is below minimum value")

                if "max" in field and isinstance(value, (int, float)):
                    if value > field["max"]:
                        errors.append(f"Field '{field_name}' is above maximum value")

                if "min_length" in field and isinstance(value, str):
                    if len(value) < field["min_length"]:
                        errors.append(f"Field '{field_name}' is below minimum length")

                if "max_length" in field and isinstance(value, str):
                    if len(value) > field["max_length"]:
                        errors.append(f"Field '{field_name}' is above maximum length")

        return (len(errors) == 0, errors)

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type.

        Args:
            value: Value to validate
            expected_type: Expected type

        Returns:
            True if valid

        Example:
            >>> valid = schema._validate_type("value", "string")
        """
        type_map = {
            "string": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "any": object,
        }

        expected_python_type = type_map.get(expected_type, str)
        if expected_type == "any":
            return True

        return isinstance(value, expected_python_type)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Schema definition

        Example:
            >>> data = schema.to_dict()
        """
        return {
            "schema_name": self._schema_name,
            "fields": self._fields,
            "version": self._version,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(schema)
        """
        return f"Schema(name={self._schema_name}, version={self._version}, fields={len(self._fields)})"


# Export
__all__ = [
    "Schema",
]
