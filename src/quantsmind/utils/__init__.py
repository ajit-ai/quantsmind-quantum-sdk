"""
Utilities Package — Provides small, dependency-free helper interfaces shared across the SDK
(e.g. identifiers, decorators, type helpers).

This package is part of the QuantsMind SDK (R0.1.0).
Architecture-only: no implementations, only public interface surface.

Utilities Framework
-------------------
Provides common utility functions used across the SDK.
"""

from quantsmind.utils.helpers import (
    chunk_list,
    clamp,
    flatten_list,
    format_number,
    is_close,
    safe_division,
    unique_preserve_order,
    validate_type,
)

__all__: list[str] = [
    "validate_type",
    "clamp",
    "safe_division",
    "format_number",
    "is_close",
    "chunk_list",
    "flatten_list",
    "unique_preserve_order",
]
