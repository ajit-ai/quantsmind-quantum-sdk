"""
Statistics Package

This package provides statistics and probability functionality for the QuantsMind SDK.

Purpose
-------
Provide comprehensive statistical analysis and probability distributions.

Modules
-------
- probability_engine: Probability computation engine
- statistical_analyzer: Statistical analysis engine
- distribution_engine: Probability distribution engine
"""

from __future__ import annotations

from quantsmind.statistics.distribution_engine import (
    BetaDistribution,
    BinomialDistribution,
    DistributionEngine,
    ExponentialDistribution,
    GammaDistribution,
    NormalDistribution,
    PoissonDistribution,
)
from quantsmind.statistics.probability_engine import ProbabilityEngine
from quantsmind.statistics.statistical_analyzer import StatisticalAnalyzer

__all__: list[str] = [
    "ProbabilityEngine",
    "StatisticalAnalyzer",
    "DistributionEngine",
    "NormalDistribution",
    "BinomialDistribution",
    "PoissonDistribution",
    "GammaDistribution",
    "BetaDistribution",
    "ExponentialDistribution",
]
