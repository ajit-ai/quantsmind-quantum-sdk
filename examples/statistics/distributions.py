"""Distributions: standard normal moments and a Poisson check.

Feature: distribution engines from ``quantsmind.statistics``.
Purpose: show pdf/cdf/mean/variance calls with no dependencies.
Input: Normal(0, 1) at 0; Poisson(2) at 2.
Processing: closed-form density evaluation.
Output: 0.3989, 0.5, 0.2707 with matching moments.
Meaning: textbook values, reproduced exactly.

Run from the repository root::

    python examples/statistics/distributions.py
"""

from __future__ import annotations

from quantsmind.statistics.distribution_engine import NormalDistribution, PoissonDistribution


def main() -> None:
    normal = NormalDistribution(0.0, 1.0)
    print(f"pdf(0)={normal.pdf(0.0):.4f} cdf(0)={normal.cdf(0.0):.1f}")
    print(f"mean={normal.mean()} var={normal.variance()}")
    fish = PoissonDistribution(2.0)
    print(f"P(2;2)={fish.pdf(2):.4f} mean={fish.mean()}")


if __name__ == "__main__":
    main()
