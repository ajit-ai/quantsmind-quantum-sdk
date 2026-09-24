"""Datasets Package — Defines dataset discovery/loading contracts.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational implementation (Phase 11): schema-validated in-memory
datasets with deterministic split/batch/transform and statistics.
"""

from __future__ import annotations

from quantsmind.datasets.dataset import Dataset, Schema, SchemaError, describe_numeric

__all__: list[str] = [
    "Dataset",
    "Schema",
    "SchemaError",
    "describe_numeric",
]
