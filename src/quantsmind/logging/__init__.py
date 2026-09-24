"""Logging Package — Defines the vendor-independent logging interface.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational implementation (Phase 11): contextual loggers over the
standard library plus an in-process capture handler for tests.
"""

from __future__ import annotations

from quantsmind.logging.logging import LogRecord, MemoryHandler, SDKLogger, get_logger

__all__: list[str] = [
    "LogRecord",
    "MemoryHandler",
    "SDKLogger",
    "get_logger",
]
