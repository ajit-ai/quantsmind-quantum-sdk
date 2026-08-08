"""
Versioning Package

This package provides versioning management for the Knowledge package.

Purpose
-------
Provide comprehensive versioning definitions and operations.

Modules
-------
- version: Version management
"""

from __future__ import annotations

from quantsmind.knowledge.versioning.version import Version, VersionHistory

__all__ = [
    "Version",
    "VersionHistory",
]
