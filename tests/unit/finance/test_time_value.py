"""Unit tests for quantsmind.finance time-value mathematics."""

from __future__ import annotations

import pytest

from quantsmind.finance import (
    annuity_future_value,
    bond_price,
    compound_amount,
    holding_return,
    internal_rate_of_return,
    loan_payment,
    macaulay_duration,
    net_present_value,
    present_value,
)


class TestInterest:
    def test_compound_roundtrip(self) -> None:
        assert compound_amount(1000.0, 0.05, 10) == pytest.approx(1628.89, rel=1e-4)
        assert present_value(1628.89, 0.05, 10) == pytest.approx(1000.0, rel=1e-4)

    def test_annuity(self) -> None:
        assert annuity_future_value(100.0, 0.05, 10) == pytest.approx(1257.79, rel=1e-4)

    def test_mortgage_payment(self) -> None:
        assert loan_payment(100000.0, 0.05 / 12, 360) == pytest.approx(536.82, rel=1e-4)

    def test_negative_rate(self) -> None:
        with pytest.raises(ValueError):
            compound_amount(100.0, -0.01, 1)


class TestCashFlows:
    def test_npv(self) -> None:
        assert net_present_value(0.1, [-100.0, 30.0, 40.0, 50.0]) == pytest.approx(-2.1, rel=1e-2)

    def test_irr(self) -> None:
        assert internal_rate_of_return([-100.0, 110.0]) == pytest.approx(0.1, rel=1e-3)
        with pytest.raises(ValueError):
            internal_rate_of_return([100.0])


class TestBonds:
    def test_par_bond(self) -> None:
        assert bond_price(1000.0, 0.05, 0.05, 10) == pytest.approx(1000.0, rel=1e-4)
        assert macaulay_duration(1000.0, 0.05, 0.05, 10) == pytest.approx(8.11, rel=1e-3)


class TestReturns:
    def test_holding(self) -> None:
        assert holding_return(100.0, 110.0) == pytest.approx(0.1)
        with pytest.raises(ValueError):
            holding_return(0.0, 110.0)
