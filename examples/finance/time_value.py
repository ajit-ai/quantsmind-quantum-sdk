"""Time value of money: growth, loans, projects, and bonds.

Feature: TVM/cash-flow/bond math from ``quantsmind.finance``.
Purpose: show compounding, amortization, NPV/IRR, and par pricing.
Input: $1,000 at 5% for 10 years; $100k mortgage; sample cash flows.
Processing: closed forms plus bisection IRR.
Output: $1,628.89; $536.82/mo; 10% IRR; $1,000 par bond.
Meaning: the same discounting idea prices everything here.

Run from the repository root::

    python examples/finance/time_value.py
"""

from __future__ import annotations

from quantsmind.finance import (
    bond_price,
    compound_amount,
    internal_rate_of_return,
    loan_payment,
    net_present_value,
)


def main() -> None:
    print(f"grown: ${compound_amount(1000.0, 0.05, 10):,.2f}")
    print(f"mortgage: ${loan_payment(100000.0, 0.05 / 12, 360):,.2f}/mo")
    flows = [-100.0, 30.0, 40.0, 50.0]
    print(f"npv@10%: ${net_present_value(0.1, flows):,.2f}")
    print(f"irr: {internal_rate_of_return([-100.0, 110.0]):.1%}")
    print(f"par bond: ${bond_price(1000.0, 0.05, 0.05, 10):,.2f}")


if __name__ == "__main__":
    main()
