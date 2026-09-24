"""Time value of money, cash flows, and bond mathematics.

Compound interest, present/future values, annuities, NPV/IRR, and
plain-vanilla bond price/duration. Deterministic and dependency-free;
educational scope only — not investment advice.
"""

from __future__ import annotations

import math

__all__ = [
    "compound_amount",
    "present_value",
    "annuity_future_value",
    "annuity_present_value",
    "loan_payment",
    "net_present_value",
    "internal_rate_of_return",
    "bond_price",
    "macaulay_duration",
    "modified_duration",
    "holding_return",
    "log_return",
]


def _require_rate(rate: float, name: str = "rate") -> float:
    if rate < 0.0:
        raise ValueError(f"{name} must be non-negative, got {rate!r}")
    return float(rate)


def compound_amount(
    principal: float, rate: float, periods: float, compounds_per_period: int = 1
) -> float:
    """Future amount with compound interest."""
    if principal < 0.0:
        raise ValueError(f"principal must be non-negative, got {principal!r}")
    _require_rate(rate)
    if periods < 0.0:
        raise ValueError(f"periods must be non-negative, got {periods!r}")
    if compounds_per_period <= 0:
        raise ValueError(f"compounds_per_period must be positive, got {compounds_per_period!r}")
    growth = (1.0 + rate / compounds_per_period) ** (compounds_per_period * periods)
    return float(principal * growth)


def present_value(
    future_value: float, rate: float, periods: float, compounds_per_period: int = 1
) -> float:
    """Present value by discounting at the compound rate."""
    _require_rate(rate)
    if periods < 0.0:
        raise ValueError(f"periods must be non-negative, got {periods!r}")
    if compounds_per_period <= 0:
        raise ValueError(f"compounds_per_period must be positive, got {compounds_per_period!r}")
    return float(
        future_value / (1.0 + rate / compounds_per_period) ** (compounds_per_period * periods)
    )


def annuity_future_value(payment: float, rate: float, periods: int) -> float:
    """Future value of an ordinary annuity."""
    _require_rate(rate)
    if periods < 0:
        raise ValueError(f"periods must be non-negative, got {periods!r}")
    if periods == 0:
        return 0.0
    if rate == 0.0:
        return payment * periods
    return payment * ((1.0 + rate) ** periods - 1.0) / rate


def annuity_present_value(payment: float, rate: float, periods: int) -> float:
    """Present value of an ordinary annuity."""
    _require_rate(rate)
    if periods < 0:
        raise ValueError(f"periods must be non-negative, got {periods!r}")
    if periods == 0:
        return 0.0
    if rate == 0.0:
        return payment * periods
    return payment * (1.0 - (1.0 + rate) ** -periods) / rate


def loan_payment(principal: float, rate_per_period: float, periods: int) -> float:
    """Level payment amortizing ``principal`` over ``periods``."""
    if principal < 0.0:
        raise ValueError(f"principal must be non-negative, got {principal!r}")
    _require_rate(rate_per_period)
    if periods <= 0:
        raise ValueError(f"periods must be positive, got {periods!r}")
    if rate_per_period == 0.0:
        return principal / periods
    factor = (1.0 + rate_per_period) ** periods
    return principal * rate_per_period * factor / (factor - 1.0)


def net_present_value(rate: float, cashflows: list[float]) -> float:
    """NPV of time-0..n cash flows discounted at ``rate``."""
    _require_rate(rate)
    return sum(cf / (1.0 + rate) ** index for index, cf in enumerate(cashflows))


def internal_rate_of_return(cashflows: list[float], tolerance: float = 1e-9) -> float:
    """IRR via bisection (requires a sign change in NPV).

    Raises:
        ValueError: For too few flows, no sign change, or bad tolerance.
    """
    if len(cashflows) < 2:
        raise ValueError("IRR needs at least two cash flows")
    if tolerance <= 0.0:
        raise ValueError(f"tolerance must be positive, got {tolerance!r}")
    low, high = -0.999999, 10.0
    npv_low = net_present_value(max(low, 0.0), cashflows)
    npv_high = net_present_value(high, cashflows)
    if npv_low * npv_high > 0.0:
        raise ValueError("no sign change: IRR is not bracketed")
    while high - low > tolerance:
        mid = (low + high) / 2.0
        if net_present_value(max(mid, 0.0), cashflows) > 0.0:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def bond_price(
    face_value: float, coupon_rate: float, yield_rate: float, periods: int, frequency: int = 1
) -> float:
    """Clean price of a plain-vanilla bond."""
    if face_value <= 0.0:
        raise ValueError(f"face value must be positive, got {face_value!r}")
    _require_rate(coupon_rate, "coupon_rate")
    _require_rate(yield_rate, "yield_rate")
    if periods <= 0:
        raise ValueError(f"periods must be positive, got {periods!r}")
    if frequency <= 0:
        raise ValueError(f"frequency must be positive, got {frequency!r}")
    coupon = face_value * coupon_rate / frequency
    per = yield_rate / frequency
    price = sum(coupon / (1.0 + per) **index for index in range(1, periods * frequency + 1))
    return price + face_value / (1.0 + per) ** (periods * frequency)


def macaulay_duration(
    face_value: float, coupon_rate: float, yield_rate: float, periods: int, frequency: int = 1
) -> float:
    """Macaulay duration in years (cash-flow-weighted average time)."""
    price = bond_price(face_value, coupon_rate, yield_rate, periods, frequency)
    if price == 0.0:
        raise ValueError("bond price is zero")
    coupon = face_value * coupon_rate / frequency
    per = yield_rate / frequency
    weighted = sum(
        (index / frequency) * coupon / (1.0 + per) ** index
        for index in range(1, periods * frequency + 1)
    )
    total_periods = periods * frequency
    weighted += periods * face_value / (1.0 + per) ** total_periods
    return weighted / price


def modified_duration(
    face_value: float, coupon_rate: float, yield_rate: float, periods: int, frequency: int = 1
) -> float:
    """Modified duration (price sensitivity to yield)."""
    return macaulay_duration(face_value, coupon_rate, yield_rate, periods, frequency) / (
        1.0 + yield_rate / frequency
    )


def holding_return(start_value: float, end_value: float) -> float:
    """Simple holding-period return."""
    if start_value <= 0.0:
        raise ValueError(f"start value must be positive, got {start_value!r}")
    return (end_value - start_value) / start_value


def log_return(start_value: float, end_value: float) -> float:
    """Continuously compounded return."""
    if start_value <= 0.0 or end_value <= 0.0:
        raise ValueError("values must be positive for log returns")
    return math.log(end_value / start_value)
