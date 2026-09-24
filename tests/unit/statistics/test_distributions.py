"""Unit tests for quantsmind.statistics distributions."""

from __future__ import annotations

import pytest

from quantsmind.statistics.distribution_engine import (
    NormalDistribution,
    PoissonDistribution,
)


class TestNormal:
    def test_standard_moments(self) -> None:
        dist = NormalDistribution(0.0, 1.0)
        assert dist.mean() == 0.0
        assert dist.variance() == 1.0
        assert dist.pdf(0.0) == pytest.approx(0.3989422804014327)
        assert dist.cdf(0.0) == pytest.approx(0.5)


class TestPoisson:
    def test_lambda_two(self) -> None:
        dist = PoissonDistribution(2.0)
        assert dist.mean() == 2.0
        assert dist.variance() == 2.0
        assert dist.pdf(2) == pytest.approx(0.2706705664732254)
