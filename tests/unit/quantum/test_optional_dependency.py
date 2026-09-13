"""Tests for optional-dependency behavior of the quantum integration layer.

The integration layer must import cleanly without ``microquantum``
installed, and only fail with a helpful error when a MicroQuantum-backed
API is actually invoked.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import quantsmind.quantum as quantum

_SRC = str(Path(__file__).parents[3] / "src")


class TestOptionalDependency:
    def test_package_imports_without_microquantum(self) -> None:
        """A subprocess that blocks microquantum must still import quantsmind.quantum."""
        code = f"""
import sys
sys.path.insert(0, {_SRC!r})

class _Block:
    def find_spec(self, name, path=None, target=None):
        if name == "microquantum" or name.startswith("microquantum."):
            raise ImportError("blocked for test")
        return None

sys.meta_path.insert(0, _Block())
import quantsmind.quantum as q
assert q.microquantum_available() is False
assert "QuantumProgram" in q.__all__
try:
    q.build_circuit(q.QuantumProgram.bell_state())
except ImportError as exc:
    assert "quantsmind[quantum]" in str(exc)
else:
    raise SystemExit("expected ImportError without microquantum")
print("OK")
"""
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, result.stderr

    def test_microquantum_available_when_installed(self) -> None:
        assert quantum.microquantum_available() is True

    def test_classical_workflow_runs_without_microquantum(self) -> None:
        """QMQ-02 classical baseline must work with microquantum blocked."""
        code = f"""
import sys
sys.path.insert(0, {_SRC!r})

class _Block:
    def find_spec(self, name, path=None, target=None):
        if name == "microquantum" or name.startswith("microquantum."):
            raise ImportError("blocked for test")
        return None

sys.meta_path.insert(0, _Block())
from quantsmind.quantum import (
    Constraint,
    Objective,
    ObjectiveSense,
    QuantumProblem,
    QuantumWorkflow,
    Variable,
)
from quantsmind.quantum.strategy.strategy import ComputationStrategy

p = QuantumProblem("knapsack", domain="optimization")
p.add_variable(Variable.binary("x0"))
p.add_variable(Variable.binary("x1"))
p.add_objective(
    Objective("value", ObjectiveSense.MAXIMIZE, expression="3*x0 + 4*x1")
)
p.add_constraint(Constraint.le("cap", expression="2*x0 + 3*x1", value=5.0))
p.preferred_strategy = ComputationStrategy.CLASSICAL
report = QuantumWorkflow(p).run()
assert report.provenance.executor == "classical/exhaustive"
assert report.solution.objective_values["value"] == 7.0
assert report.solution.assignments == {{"x0": 1, "x1": 1}}

try:
    from quantsmind.quantum.integration.microquantum import run_qaoa
    run_qaoa(None)  # type: ignore[arg-type]
except ImportError as exc:
    assert "quantsmind[quantum]" in str(exc)
else:
    raise SystemExit("expected ImportError without microquantum")
print("OK")
"""
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, result.stderr
