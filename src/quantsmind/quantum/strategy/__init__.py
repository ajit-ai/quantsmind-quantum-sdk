"""Strategy layer of QuantsMind Quantum.

The strategy layer selects how a domain problem should be computed:
classically, with a quantum kernel, hybrid, or quantum-inspired.
"""

from __future__ import annotations

from quantsmind.quantum.strategy.selector import StrategySelector
from quantsmind.quantum.strategy.strategy import ComputationStrategy

__all__ = ["ComputationStrategy", "StrategySelector"]
