"""
Dimensions Package

This package provides dimension management for the Scientific package.

Purpose
-------
Provide comprehensive dimension definitions and dimensional analysis.

Modules
-------
- dimension: Dimension class
- dimensional_analysis: Dimensional analysis operations
"""

from __future__ import annotations

from quantsmind.scientific.dimensions.dimension import Dimension
from quantsmind.scientific.dimensions.dimensional_analysis import DimensionalAnalysis

__all__ = [
    "Dimension",
    "DimensionalAnalysis",
]
