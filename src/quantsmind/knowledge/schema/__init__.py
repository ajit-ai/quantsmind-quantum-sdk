"""
Schema Package

This package provides schema management for the Knowledge package.

Purpose
-------
Provide comprehensive schema definitions and validation.

Modules
-------
- schema: Base schema class
- field: Field management
- datatype: Datatype management
- schema_validator: Schema validation
"""

from __future__ import annotations

from quantsmind.knowledge.schema.datatype import DataType, DataTypeRegistry
from quantsmind.knowledge.schema.field import Field
from quantsmind.knowledge.schema.schema import Schema
from quantsmind.knowledge.schema.schema_validator import SchemaValidator

__all__ = [
    "Schema",
    "Field",
    "DataType",
    "DataTypeRegistry",
    "SchemaValidator",
]
