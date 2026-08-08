"""
Runtime Constants Module

This module provides constants for the Runtime package.

Purpose
-------
Provide runtime constants for the QuantsMind SDK.

Responsibilities
----------------
- Define runtime version
- Define default configuration values
- Define timeout constants
- Define resource limits

Dependencies
------------
None
"""

from __future__ import annotations

__version__ = "R0.5.0"

# Runtime Version
RUNTIME_VERSION = __version__

# Default Configuration
DEFAULT_TIMEOUT = 300.0  # seconds
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 1.0  # seconds
DEFAULT_MAX_CONCURRENT_TASKS = 10
DEFAULT_MAX_QUEUE_SIZE = 1000

# Resource Limits
DEFAULT_MEMORY_LIMIT = 8 * 1024 * 1024 * 1024  # 8 GB
DEFAULT_CPU_LIMIT = 1.0  # 100%
DEFAULT_STORAGE_LIMIT = 100 * 1024 * 1024 * 1024  # 100 GB

# Cache Settings
DEFAULT_CACHE_SIZE = 1000
DEFAULT_CACHE_TTL = 3600  # seconds

# Event Bus Settings
DEFAULT_EVENT_QUEUE_SIZE = 10000
DEFAULT_EVENT_TIMEOUT = 30.0  # seconds

# Logging Settings
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Metrics Settings
DEFAULT_METRICS_INTERVAL = 60  # seconds
DEFAULT_METRICS_RETENTION = 7 * 24 * 3600  # 7 days

# Plugin Settings
DEFAULT_PLUGIN_TIMEOUT = 60.0  # seconds
DEFAULT_PLUGIN_VERSION = "1.0.0"

# State Machine Settings
DEFAULT_STATE_TIMEOUT = 300.0  # seconds

# Export
__all__ = [
    "__version__",
    "RUNTIME_VERSION",
    "DEFAULT_TIMEOUT",
    "DEFAULT_RETRY_COUNT",
    "DEFAULT_RETRY_DELAY",
    "DEFAULT_MAX_CONCURRENT_TASKS",
    "DEFAULT_MAX_QUEUE_SIZE",
    "DEFAULT_MEMORY_LIMIT",
    "DEFAULT_CPU_LIMIT",
    "DEFAULT_STORAGE_LIMIT",
    "DEFAULT_CACHE_SIZE",
    "DEFAULT_CACHE_TTL",
    "DEFAULT_EVENT_QUEUE_SIZE",
    "DEFAULT_EVENT_TIMEOUT",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_METRICS_INTERVAL",
    "DEFAULT_METRICS_RETENTION",
    "DEFAULT_PLUGIN_TIMEOUT",
    "DEFAULT_PLUGIN_VERSION",
    "DEFAULT_STATE_TIMEOUT",
]
