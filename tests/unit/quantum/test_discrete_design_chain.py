"""Scientific chain test: physics -> QUBO -> classical execution (11/§12)."""

from __future__ import annotations

from quantsmind.physics import heat_conduction
from quantsmind.quantum.optimization.classical import ExhaustiveSolver
from quantsmind.quantum.optimization.qubo import QUBOModel


class TestDiscreteDesignChain:
    def test_thickest_insulation_wins(self) -> None:
        options = {"d5cm": 0.05, "d10cm": 0.10, "d15cm": 0.15, "d20cm": 0.20}
        names = sorted(options)
        losses = {
            name: heat_conduction(0.04, 10.0, 20.0, options[name]) for name in names
        }
        model = QUBOModel(variables=names, linear=dict(losses))
        result = ExhaustiveSolver().solve(model, is_feasible=lambda a: sum(a.values()) == 1)
        pick = next(name for name, bit in result.assignment.items() if bit == 1)
        assert pick == "d20cm"
        assert result.energy == losses["d20cm"] == 40.0
