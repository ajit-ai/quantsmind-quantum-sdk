"""
Schema Validator Module

This module provides schema validation functionality for the Knowledge package.

Purpose
-------
Provide schema validation and verification.

Responsibilities
----------------
- Validate schemas
- Validate data against schemas
- Support schema evolution
- Support schema migration

Dependencies
------------
typing (standard library)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
quantsmind.knowledge.schema.schema (schema)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.schema.schema import Schema
from quantsmind.knowledge.types import ValidationResult


class SchemaValidator:
    """Schema validator for validating schemas and data.

    This class provides schema validation functionality.

    Attributes:
        _schema: Schema to validate against
        _strict_mode: Whether to use strict validation

    Example:
        >>> validator = SchemaValidator(schema)
        >>> is_valid, errors = validator.validate(data)
    """

    def __init__(self, schema: Schema, strict_mode: bool = True) -> None:
        """Initialize a SchemaValidator.

        Args:
            schema: Schema to validate against
            strict_mode: Whether to use strict validation

        Example:
            >>> validator = SchemaValidator(schema)
        """
        self._schema = schema
        self._strict_mode = strict_mode

    @property
    def schema(self) -> Schema:
        """Get the schema.

        Returns:
            Schema

        Example:
            >>> schema = validator.schema
        """
        return self._schema

    @property
    def strict_mode(self) -> bool:
        """Get the strict mode.

        Returns:
            True if strict mode enabled

        Example:
            >>> strict = validator.strict_mode
        """
        return self._strict_mode

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        """Validate data against the schema.

        Args:
            data: Data to validate

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate(data)
        """
        return self._schema.validate(data)

    def validate_schema(self) -> ValidationResult:
        """Validate the schema itself.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_schema()
        """
        errors = []

        # Check schema name
        if not self._schema.schema_name:
            errors.append("Schema name cannot be empty")

        # Check fields
        if not self._schema.fields:
            errors.append("Schema must have at least one field")

        # Validate each field
        for i, field in enumerate(self._schema.fields):
            if "name" not in field:
                errors.append(f"Field {i} missing name")

            if "type" not in field:
                errors.append(f"Field {i} missing type")

            # Check for duplicate field names
            field_names = [f.get("name") for f in self._schema.fields if "name" in f]
            if len(field_names) != len(set(field_names)):
                errors.append("Schema has duplicate field names")

        return (len(errors) == 0, errors)

    def validate_field(self, field_name: str, value: Any) -> ValidationResult:
        """Validate a single field value.

        Args:
            field_name: Field name
            value: Field value

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_field("name", "value")
        """
        field = self._schema.get_field(field_name)
        if not field:
            return (False, [f"Field '{field_name}' not found in schema"])

        errors = []

        # Validate type
        field_type = field.get("type")
        if not self._validate_type(value, field_type):
            errors.append(f"Field '{field_name}' has invalid type, expected {field_type}")

        # Validate constraints
        if "min" in field and isinstance(value, (int, float)) and value < field["min"]:
            errors.append(f"Field '{field_name}' is below minimum value")

        if "max" in field and isinstance(value, (int, float)) and value > field["max"]:
            errors.append(f"Field '{field_name}' is above maximum value")

        if "min_length" in field and isinstance(value, str):
            if len(value) < field["min_length"]:
                errors.append(f"Field '{field_name}' is below minimum length")

        if "max_length" in field and isinstance(value, str):
            if len(value) > field["max_length"]:
                errors.append(f"Field '{field_name}' is above maximum length")

        if "pattern" in field and isinstance(value, str):
            import re
            if not re.match(field["pattern"], value):
                errors.append(f"Field '{field_name}' does not match pattern")

        if "enum" in field and value not in field["enum"]:
            errors.append(f"Field '{field_name}' not in allowed values")

        return (len(errors) == 0, errors)

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type.

        Args:
            value: Value to validate
            expected_type: Expected type

        Returns:
            True if valid

        Example:
            >>> valid = validator._validate_type("value", "string")
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

    def get_validation_report(self, data: dict[str, Any]) -> dict[str, Any]:
        """Get detailed validation report.

        Args:
            data: Data to validate

        Returns:
            Validation report

        Example:
            >>> report = validator.get_validation_report(data)
        """
        is_valid, errors = self.validate(data)

        return {
            "is_valid": is_valid,
            "errors": errors,
            "error_count": len(errors),
            "schema_name": self._schema.schema_name,
            "schema_version": self._schema.version,
            "field_count": len(self._schema.fields),
            "strict_mode": self._strict_mode,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Validator state

        Example:
            >>> data = validator.to_dict()
        """
        return {
            "schema_name": self._schema.schema_name,
            "schema_version": self._schema.version,
            "strict_mode": self._strict_mode,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(validator)
        """
        return f"SchemaValidator(schema={self._schema.schema_name}, strict={self._strict_mode})"


# Export
__all__ = [
    "SchemaValidator",
]
