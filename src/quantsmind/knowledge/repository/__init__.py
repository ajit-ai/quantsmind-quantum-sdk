"""
Repository Package

This package provides repository management for the Knowledge package.

Purpose
-------
Provide comprehensive repository definitions and operations.

Modules
-------
- repository: Base repository class
- knowledge_repository: Knowledge repository management
"""

from __future__ import annotations

from quantsmind.knowledge.repository.knowledge_repository import KnowledgeRepository
from quantsmind.knowledge.repository.repository import Repository

__all__ = [
    "Repository",
    "KnowledgeRepository",
]
