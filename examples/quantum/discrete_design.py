"""Scientific chain: physics -> math -> QUBO -> classical execution -> pick.

Feature: a full cross-layer workflow using only existing public APIs.
Purpose: show how a scientific problem feeds the quantum formulation layer.
Input: wall insulation options (thickness in m); k = 0.04 W/m/K, A = 10 m^2.
Processing: heat loss per option -> one-hot QUBO -> exhaustive baseline.
Output: thickest option wins (25.0 W), selection assignment, energy.
Meaning: each SDK layer does one job; the chain stays inspectable.

Run from the repository root::

    python examples/quantum/discrete_design.py
"""

from __future__ import annotations

from quantsmind.physics import heat_conduction
from quantsmind.quantum.optimization.classical import ExhaustiveSolver
from quantsmind.quantum.optimization.qubo import QUBOModel

CONDUCTIVITY = 0.04  # W/m/K, glass wool
AREA = 10.0  # m^2
DELTA_T = 20.0  # K indoor-outdoor
OPTIONS = {"d5cm": 0.05, "d10cm": 0.10, "d15cm": 0.15, "d20cm": 0.20}


def main() -> None:
    names = sorted(OPTIONS)
    # Scientific problem: heat loss per discrete design choice.
    losses = {name: heat_conduction(CONDUCTIVITY, AREA, DELTA_T, OPTIONS[name]) for name in names}
    for name in names:
        print(f"{name}: {losses[name]:.1f} W")
    # Mathematical formulation: one-hot QUBO over the options.
    model = QUBOModel(variables=names, linear=dict(losses))
    # Execution: deterministic classical baseline, exactly one option.
    result = ExhaustiveSolver().solve(model, is_feasible=lambda a: sum(a.values()) == 1)
    pick = next(name for name, bit in result.assignment.items() if bit == 1)
    print(f"selected: {pick} at {result.energy:.1f} W")


if __name__ == "__main__":
    main()
