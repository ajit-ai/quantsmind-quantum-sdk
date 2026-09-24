"""Example execution tests: every runnable example must execute cleanly.

Examples stay outside the installed package, so they are loaded by file
location instead of being imported as modules. Output assertions use
stable key substrings verified against real runs, never fragile
formatting.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_EXAMPLES = _REPO / "examples"


def _run_example(relative: str) -> str:
    path = _EXAMPLES / relative
    assert path.exists(), f"missing example: {relative}"
    spec = importlib.util.spec_from_file_location("example_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()
    return ""


def _run_and_capture(relative: str, capsys: pytest.CaptureFixture[str]) -> str:
    _run_example(relative)
    return capsys.readouterr().out


class TestQuantumExamples:
    def test_bell_state(self, capsys: pytest.CaptureFixture[str]) -> None:
        pytest.importorskip("microquantum")
        out = _run_and_capture("bell_state.py", capsys)
        assert "validation: OK" in out
        assert "success: True" in out

    def test_discrete_design(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = _run_and_capture("quantum/discrete_design.py", capsys)
        assert "selected: d20cm" in out


class TestScienceExamples:
    def test_projectile(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "optimal angle: 45.0" in _run_and_capture("physics/projectile.py", capsys)

    def test_water(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "molar mass: 18.015" in _run_and_capture("chemistry/water.py", capsys)

    def test_central_dogma(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "protein: MAIVMGR" in _run_and_capture("biology/central_dogma.py", capsys)

    def test_earth_orbit(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "365.25 days" in _run_and_capture("astronomy/earth_orbit.py", capsys)

    def test_hubble_flow(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "13.97 Gyr" in _run_and_capture("cosmology/hubble_flow.py", capsys)


class TestMathExamples:
    def test_linear_algebra(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "det: -2.0" in _run_and_capture("math/linear_algebra.py", capsys)

    def test_differentiation(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "[2.0, 0.0]" in _run_and_capture("calculus/differentiation.py", capsys)

    def test_distributions(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "P(2;2)=0.2707" in _run_and_capture("statistics/distributions.py", capsys)

    def test_adam(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "first/last: 1.0000" in _run_and_capture("optimization/adam_descent.py", capsys)

    def test_expressions(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "satisfied at x=3: True" in _run_and_capture("core/expressions.py", capsys)

    def test_compiler(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "value: 14.0 == 14.0" in _run_and_capture("compiler/expr_eval.py", capsys)

    def test_finance(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "par bond: $1,000.00" in _run_and_capture("finance/time_value.py", capsys)


class TestAppliedExamples:
    def test_tool_loop(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "answer: 20" in _run_and_capture("ai/tool_loop.py", capsys)

    def test_graph_demo(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = _run_and_capture("knowledge/graph_demo.py", capsys)
        assert "path a->c: ['a', 'b', 'c']" in out

    def test_split_batch(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "mean age: 33.5" in _run_and_capture("datasets/split_batch.py", capsys)

    def test_roundtrip(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "json: True" in _run_and_capture("io/roundtrip.py", capsys)

    def test_sdk_base(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "plugin enabled: True" in _run_and_capture("infrastructure/sdk_base.py", capsys)

    def test_engine_demo(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = _run_and_capture("simulation/engine_demo.py", capsys)
        assert "success: True" in out

    def test_projectile_sweep(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert "best angle: 45" in _run_and_capture("simulation/projectile_sweep.py", capsys)


class TestIntegrationExamples:
    def test_request_models(self, capsys: pytest.CaptureFixture[str]) -> None:
        pytest.importorskip("pydantic")
        out = _run_and_capture("api/request_models.py", capsys)
        assert "matrix op: determinant" in out

    def test_registry_demo(self, capsys: pytest.CaptureFixture[str]) -> None:
        pytest.importorskip("microquantum")
        out = _run_and_capture("providers/registry_demo.py", capsys)
        assert "local_simulator" in out
