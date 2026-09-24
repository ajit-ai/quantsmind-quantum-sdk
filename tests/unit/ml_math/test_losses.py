"""Unit tests for ml_math loss functions."""

from __future__ import annotations

from quantsmind.ml_math import MSELoss


class TestMSELoss:
    def test_per_element_errors(self) -> None:
        assert list(MSELoss().compute([1.0, 2.0], [1.5, 2.5])) == [0.25, 0.25]
