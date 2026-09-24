"""SDK logging layer over the standard library.

:class:`SDKLogger` binds contextual fields to every record, and
:class:`MemoryHandler` captures records in-process so tests and tools
can assert on log output without touching handlers or files.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "LogRecord",
    "MemoryHandler",
    "SDKLogger",
    "get_logger",
]


@dataclass(frozen=True)
class LogRecord:
    """One captured log entry."""

    logger: str
    level: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)


class MemoryHandler(logging.Handler):
    """In-process handler collecting :class:`LogRecord` entries."""

    def __init__(self) -> None:
        """Initialize with an empty record list."""
        super().__init__()
        self.records: list[LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Append a record (never raises)."""
        try:
            context = dict(getattr(record, "qm_context", {}))
            self.records.append(
                LogRecord(
                    logger=record.name,
                    level=record.levelname,
                    message=record.getMessage(),
                    context=context,
                )
            )
        except Exception:
            self.handleError(record)

    def clear(self) -> None:
        """Drop captured records."""
        self.records.clear()


class SDKLogger:
    """Logger with bound context fields.

    Args:
        name: Logger name (a standard library logger is used).
        context: Fields attached to every emitted record.
    """

    def __init__(self, name: str, context: dict[str, Any] | None = None) -> None:
        """Initialize with a name and optional context."""
        self._logger = logging.getLogger(name)
        self._context = dict(context or {})

    @property
    def name(self) -> str:
        """Logger name."""
        return self._logger.name

    def bind(self, **fields: Any) -> SDKLogger:
        """Return a child logger with merged context."""
        return SDKLogger(self._logger.name, {**self._context, **fields})

    def _emit(self, level: int, message: str) -> None:
        self._logger.log(level, message, extra={"qm_context": dict(self._context)})

    def debug(self, message: str) -> None:
        """Emit a debug record."""
        self._emit(logging.DEBUG, message)

    def info(self, message: str) -> None:
        """Emit an info record."""
        self._emit(logging.INFO, message)

    def warning(self, message: str) -> None:
        """Emit a warning record."""
        self._emit(logging.WARNING, message)

    def error(self, message: str) -> None:
        """Emit an error record."""
        self._emit(logging.ERROR, message)


def get_logger(name: str, context: dict[str, Any] | None = None) -> SDKLogger:
    """Create an :class:`SDKLogger` (standard library underneath)."""
    return SDKLogger(name, context)
