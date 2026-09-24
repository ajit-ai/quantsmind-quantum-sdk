"""
Finance Math Package

This package provides financial mathematics functionality for the QuantsMind SDK.

Purpose
-------
Provide comprehensive financial mathematics including portfolio optimization,
risk analysis, option pricing, and Monte Carlo simulation.

Modules
-------
- portfolio_math: Portfolio mathematics
- risk_engine: Risk analysis engine
- option_pricer: Option pricing engine
- monte_carlo_finance: Monte Carlo financial simulation
"""

from __future__ import annotations

from quantsmind.finance.math.monte_carlo_finance import MonteCarloFinanceSimulator
from quantsmind.finance.math.option_pricer import OptionPricer
from quantsmind.finance.math.portfolio_math import PortfolioMath
from quantsmind.finance.math.risk_engine import RiskEngine
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
    "PortfolioMath",
    "RiskEngine",
    "OptionPricer",
    "MonteCarloFinanceSimulator",
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
