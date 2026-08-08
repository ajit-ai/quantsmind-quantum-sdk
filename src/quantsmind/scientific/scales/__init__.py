"""
Scales Package

This package provides scale management for the Scientific package.

Purpose
-------
Provide comprehensive scale definitions and operations.

Modules
-------
- scale: Base scale class
- logarithmic: Logarithmic scale
- linear: Linear scale
"""

from __future__ import annotations

from quantsmind.scientific.scales.linear import LinearScale
from quantsmind.scientific.scales.logarithmic import LogarithmicScale
from quantsmind.scientific.scales.scale import Scale

__all__ = [
    "Scale",
    "LinearScale",
    "LogarithmicScale",
]
