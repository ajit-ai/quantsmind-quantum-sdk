"""
Runtime Logging Module

This module provides logging management for the Runtime package.

Purpose
-------
Provide logging management for the QuantsMind SDK.

Responsibilities
----------------
- Configure logging
- Support structured logging
- Handle context-aware logging
- Support execution tracing

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from quantsmind.runtime.constants import DEFAULT_LOG_FORMAT
from quantsmind.runtime.enums import LogLevel

logger = logging.getLogger(__name__)


class RuntimeLogger:
    """Concrete implementation of runtime logging.

    This class provides logging management capabilities.

    Attributes:
        _logger: Logger instance
        _context: Logging context

    Example:
        >>> runtime_logger = RuntimeLogger("my_module")
        >>> runtime_logger.info("Message", extra={"key": "value"})
    """

    def __init__(self, name: str, level: LogLevel = LogLevel.INFO) -> None:
        """Initialize a RuntimeLogger.

        Args:
            name: Logger name
            level: Log level

        Example:
            >>> runtime_logger = RuntimeLogger("my_module")
        """
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.value))
        self._context: dict[str, Any] = {}
        
        # Configure handler if not already configured
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
            self._logger.addHandler(handler)

    def set_level(self, level: LogLevel) -> None:
        """Set the log level.

        Args:
            level: Log level

        Example:
            >>> runtime_logger.set_level(LogLevel.DEBUG)
        """
        self._logger.setLevel(getattr(logging, level.value))

    def set_context(self, key: str, value: Any) -> None:
        """Set a context value.

        Args:
            key: Context key
            value: Context value

        Example:
            >>> runtime_logger.set_context("session_id", "session_123")
        """
        self._context[key] = value

    def _add_context(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        """Add context to extra.

        Args:
            extra: Extra dictionary

        Returns:
            Extra with context
        """
        result = extra or {}
        result.update(self._context)
        return result

    def debug(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log a debug message.

        Args:
            message: Log message
            extra: Extra context

        Example:
            >>> runtime_logger.debug("Debug message")
        """
        self._logger.debug(message, extra=self._add_context(extra))

    def info(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log an info message.

        Args:
            message: Log message
            extra: Extra context

        Example:
            >>> runtime_logger.info("Info message")
        """
        self._logger.info(message, extra=self._add_context(extra))

    def warning(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log a warning message.

        Args:
            message: Log message
            extra: Extra context

        Example:
            >>> runtime_logger.warning("Warning message")
        """
        self._logger.warning(message, extra=self._add_context(extra))

    def error(self, message: str, extra: dict[str, Any] | None = None, exc_info: bool = False) -> None:
        """Log an error message.

        Args:
            message: Log message
            extra: Extra context
            exc_info: Include exception info

        Example:
            >>> runtime_logger.error("Error message", exc_info=True)
        """
        self._logger.error(message, extra=self._add_context(extra), exc_info=exc_info)

    def critical(self, message: str, extra: dict[str, Any] | None = None, exc_info: bool = False) -> None:
        """Log a critical message.

        Args:
            message: Log message
            extra: Extra context
            exc_info: Include exception info

        Example:
            >>> runtime_logger.critical("Critical message")
        """
        self._logger.critical(message, extra=self._add_context(extra), exc_info=exc_info)

    def clear_context(self) -> None:
        """Clear the logging context.

        Example:
            >>> runtime_logger.clear_context()
        """
        self._context.clear()


# Export
__all__ = [
    "RuntimeLogger",
]
