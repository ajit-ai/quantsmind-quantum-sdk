"""
Datasource Package

This package provides datasource management for the Knowledge package.

Purpose
-------
Provide comprehensive datasource definitions and operations.

Modules
-------
- datasource: Base datasource class
- file_source: File-based datasource
- database_source: Database datasource
- stream_source: Stream datasource
- api_source: API datasource
"""

from __future__ import annotations

from quantsmind.knowledge.datasource.api_source import APISource
from quantsmind.knowledge.datasource.database_source import DatabaseSource
from quantsmind.knowledge.datasource.datasource import DataSource
from quantsmind.knowledge.datasource.file_source import FileSource
from quantsmind.knowledge.datasource.stream_source import StreamSource

__all__ = [
    "DataSource",
    "FileSource",
    "DatabaseSource",
    "StreamSource",
    "APISource",
]
