"""
Numerical Package

This package provides numerical computing functionality for the QuantsMind SDK.

Purpose
-------
Provide comprehensive numerical methods including root finding, interpolation,
curve fitting, approximation, and error analysis.

Modules
-------
- numerical_engine: Numerical computing engine
"""

from __future__ import annotations

from quantsmind.numerical.numerical_engine import approximation, curve_fit, error_analysis, extrapolation, interpolation, root_finding

__all__: list[str] = [
    "root_finding",
    "interpolation",
    "extrapolation",
    "curve_fit",
    "approximation",
    "error_analysis",
]
