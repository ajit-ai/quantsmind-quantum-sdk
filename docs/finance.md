# Finance Foundations

## Overview

Financial mathematics in `quantsmind.finance`: time value of money,
cash-flow analysis, plain-vanilla bonds, plus the existing portfolio,
risk, option-pricing, and Monte Carlo engines under `finance.math`.

## Purpose

Let users price growth, loans, projects, and bonds with validated
closed forms — mathematical functionality, not market data.

## Concept

One discounting idea throughout: compound forward, discount back.
Annuities sum geometric series; NPV discounts cash-flow vectors; IRR
bisects NPV to zero; bonds discount coupons plus principal.

## API

`compound_amount()`, `present_value()`, `annuity_future_value()`,
`annuity_present_value()`, `loan_payment()`, `net_present_value()`,
`internal_rate_of_return()`, `bond_price()`, `macaulay_duration()`,
`modified_duration()`, `holding_return()`, `log_return()`, plus
`PortfolioMath`, `RiskEngine`, `OptionPricer`,
`MonteCarloFinanceSimulator`.

## Input / Processing / Output

Input: principals, rates, periods, cash-flow vectors. Processing:
closed forms and bisection. Output: amounts, payments, yields, prices.

## Example

`python examples/finance/time_value.py` grows $1,000, amortizes a
mortgage, prices cash flows, and checks a par bond.

## Limitations

No market data feeds, no trading, no investment advice; plain-vanilla
instruments only — no exotics, no stochastic calibration.
