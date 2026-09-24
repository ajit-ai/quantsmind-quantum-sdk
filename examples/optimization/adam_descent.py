"""Adam descent: minimize x^2 from x = 1.

Feature: `AdamOptimizer` from ``quantsmind.optimization``.
Purpose: show gradient-based optimization converging with history.
Input: f(x) = x^2 with analytic gradient, start 1.0.
Processing: Adam updates with full history.
Output: result below the start, monotone-nondecreasing history end.
Meaning: the optimizer descends; history enables inspection.

Run from the repository root::

    python examples/optimization/adam_descent.py
"""

from __future__ import annotations

from quantsmind.optimization.gradient_optimizer import AdamOptimizer


def main() -> None:
    result, history = AdamOptimizer().optimize(lambda x: x**2, lambda x: 2 * x, 1.0)
    print(f"result: {result:.4f} in {len(history)} steps")
    print(f"first/last: {history[0]:.4f} -> {history[-1]:.4f}")


if __name__ == "__main__":
    main()
