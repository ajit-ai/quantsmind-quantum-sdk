"""Finance Package — Defines the domain model for quantitative finance (instruments, portfolios,
risk, pricing), building on math, optimization, and AI.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational implementation (Phase 11): time-value/cash-flow/bond
mathematics re-exported from ``finance.math`` (mathematical
functionality only — no market data, trading, or advice).
"""

from __future__ import annotations

from quantsmind.finance.math.time_value import (
    annuity_future_value,
    annuity_present_value,
    bond_price,
    compound_amount,
    holding_return,
    internal_rate_of_return,
    loan_payment,
    log_return,
    macaulay_duration,
    modified_duration,
    net_present_value,
    present_value,
)

__all__: list[str] = [
    "annuity_future_value",
    "annuity_present_value",
    "bond_price",
    "compound_amount",
    "holding_return",
    "internal_rate_of_return",
    "loan_payment",
    "log_return",
    "macaulay_duration",
    "modified_duration",
    "net_present_value",
    "present_value",
]
