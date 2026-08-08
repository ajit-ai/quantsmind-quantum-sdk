"""
Quality Package

This package provides quality management for the Knowledge package.

Purpose
-------
Provide comprehensive quality definitions and checks.

Modules
-------
- quality_rule: Quality rule management
- completeness: Completeness checks
- consistency: Consistency checks
- validity: Validity checks
- freshness: Freshness checks
- uniqueness: Uniqueness checks
"""

from __future__ import annotations

from quantsmind.knowledge.quality.completeness import Completeness
from quantsmind.knowledge.quality.consistency import Consistency
from quantsmind.knowledge.quality.freshness import Freshness
from quantsmind.knowledge.quality.quality_rule import QualityRule
from quantsmind.knowledge.quality.uniqueness import Uniqueness
from quantsmind.knowledge.quality.validity import Validity

__all__ = [
    "QualityRule",
    "Completeness",
    "Consistency",
    "Validity",
    "Freshness",
    "Uniqueness",
]
