"""Example execution tests: every runnable example must execute cleanly.

Examples stay outside the installed package, so they are loaded by file
location instead of being imported as modules.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_EXAMPLES = _REPO / "examples"


def _run_example(relative: str) -> None:
    path = _EXAMPLES / relative
    assert path.exists(), f"missing example: {relative}"
    spec = importlib.util.spec_from_file_location("example_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


class TestSimulationExamples:
    def test_engine_demo(self, capsys: pytest.CaptureFixture[str]) -> None:
        _run_example("simulation/engine_demo.py")
        out = capsys.readouterr().out
        assert "success: True" in out
        assert "history entries: 1" in out


class TestApiExamples:
    def test_request_models(self, capsys: pytest.CaptureFixture[str]) -> None:
        pytest.importorskip("pydantic")
        _run_example("api/request_models.py")
        out = capsys.readouterr().out
        assert "matrix op: determinant" in out
        assert "rejected: ValidationError" in out


class TestProviderExamples:
    def test_registry_demo(self, capsys: pytest.CaptureFixture[str]) -> None:
        pytest.importorskip("microquantum")
        _run_example("providers/registry_demo.py")
        out = capsys.readouterr().out
        assert "local_simulator" in out
        assert "ready: True" in out
