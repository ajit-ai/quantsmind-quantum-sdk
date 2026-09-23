"""QMQ-12 release-hardening regression tests (release properties only).

These tests verify release properties of QuantsMind Quantum 1.0.1:

- single authoritative version (``quantsmind.__version__`` == pyproject ``version``)
- package metadata (classifier, declared dependencies)
- public ``__all__`` integrity across the top-level public packages
- the committed API manifest matches the live import surface
- serialization round-trips for representative public objects
- the canonical documented example values (as printed in the README)
- honest optional-MicroQuantum behavior in a blocked subprocess

They intentionally do NOT duplicate the QMQ-01..11 feature tests.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]

PUBLIC_PACKAGES = [
    "quantsmind.quantum",
    "quantsmind.quantum.finance",
    "quantsmind.quantum.data",
    "quantsmind.quantum.ml",
    "quantsmind.quantum.domain",
]

_MANIFEST_PATH = _REPO / "api_manifest.json"


def _load_pyproject() -> dict:
    with open(_REPO / "pyproject.toml", "rb") as handle:
        return tomllib.load(handle)


def _load_generator() -> object:
    path = _REPO / "scripts" / "generate_api_manifest.py"
    spec = importlib.util.spec_from_file_location("_qmq12_manifest_gen", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestVersionAndMetadata:
    def test_version_is_101_everywhere(self) -> None:
        import quantsmind

        pyproject = _load_pyproject()
        assert pyproject["project"]["version"] == "1.0.1"
        assert quantsmind.__version__ == "1.0.1"
        assert quantsmind.__version__ == pyproject["project"]["version"]

    def test_production_classifier(self) -> None:
        classifiers = _load_pyproject()["project"]["classifiers"]
        assert "Development Status :: 5 - Production/Stable" in classifiers
        assert "2 - Pre-Alpha" not in classifiers

    def test_zero_required_dependencies(self) -> None:
        assert _load_pyproject()["project"]["dependencies"] == []

    def test_microquantum_is_optional_extra(self) -> None:
        extras = _load_pyproject()["project"]["optional-dependencies"]
        assert "quantum" in extras
        assert "microquantum" in "".join(extras["quantum"])
        assert "microquantum" not in _load_pyproject()["project"]["dependencies"]


class TestPublicExports:
    @pytest.mark.parametrize("package", PUBLIC_PACKAGES)
    def test_all_exports_resolve(self, package: str) -> None:
        module = importlib.import_module(package)
        all_names = module.__all__
        assert all_names, "empty __all__"
        assert len(set(all_names)) == len(all_names), "duplicate __all__ entries"
        missing = [name for name in all_names if not hasattr(module, name)]
        assert missing == [], f"unresolved exports: {missing}"

    @pytest.mark.parametrize("package", PUBLIC_PACKAGES)
    def test_no_private_exports(self, package: str) -> None:
        module = importlib.import_module(package)
        private = [name for name in module.__all__ if name.startswith("_")]
        assert private == [], f"accidental internal exports: {private}"


class TestApiManifest:
    def test_manifest_is_valid_json(self) -> None:
        data = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
        assert data["version"] == "1.0.1"
        assert data["package"] == "quantsmind"
        assert isinstance(data["modules"], dict)
        assert data["modules"]

    def test_manifest_matches_live_surface(self) -> None:
        generator = _load_generator()
        committed = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
        recomputed = generator.build_manifest()
        assert recomputed["version"] == "1.0.1"
        assert recomputed["modules"] == committed["modules"], (
            "the committed API manifest (api_manifest.json) no longer matches "
            "the import surface; re-run scripts/generate_api_manifest.py"
        )
        total_symbols = sum(len(names) for names in committed["modules"].values())
        assert total_symbols >= 600


class TestReleaseSmoke:
    def test_canonical_documented_finance_values(self) -> None:
        from quantsmind.quantum import domain_finance_example

        artifacts = domain_finance_example()
        solve = artifacts["solve"]
        assert solve.feasible is True
        assert solve.fallback_used is False
        assert abs(float(solve.objective_value) - 0.038) < 1e-6
        assert solve.interpretation.status.value == "executed"
        assert artifacts["interpretation"].status.value == "executed"
        assert artifacts["plan"].problem_type == "FinancialProblem"
        assert artifacts["plan"].domain.value == "finance"
        assert artifacts["plan"].strategy_requested == ""  # AUTO by default

    def test_serialization_roundtrip_plan_and_result(self) -> None:
        from quantsmind.quantum import DomainIntelligence
        from quantsmind.quantum.domain import DomainRunResult, ExecutionPlan
        from quantsmind.quantum.finance.portfolio_examples import (
            example_portfolio_problem,
        )

        intelligence = DomainIntelligence()
        problem = example_portfolio_problem().to_financial_problem()
        plan = intelligence.plan(problem)
        rebuilt_plan = ExecutionPlan.from_dict(plan.to_dict())
        assert rebuilt_plan.problem_type == plan.problem_type
        assert rebuilt_plan.strategy_requested == plan.strategy_requested
        assert rebuilt_plan.metadata == plan.metadata
        assert rebuilt_plan.to_dict() == plan.to_dict()

        result = intelligence.solve(problem, strategy="classical")
        rebuilt = DomainRunResult.from_dict(result.to_dict())
        assert rebuilt.strategy_executed == result.strategy_executed
        assert rebuilt.fallback_used == result.fallback_used
        assert rebuilt.feasible == result.feasible
        assert round(float(rebuilt.objective_value), 6) == round(float(result.objective_value), 6)
        assert rebuilt.interpretation.status.value == result.interpretation.status.value

    def test_report_roundtrip_carries_provenance(self) -> None:
        from quantsmind.quantum import DomainIntelligence
        from quantsmind.quantum.finance.portfolio_examples import (
            example_portfolio_problem,
        )
        from quantsmind.quantum.result.provenance import Provenance
        from quantsmind.quantum.result.result_interpretation import (
            ResultInterpretation,
        )

        problem = example_portfolio_problem().to_financial_problem()
        result = DomainIntelligence().solve(problem, strategy="classical")
        report = result.report
        assert report is not None
        assert report.provenance.strategy == "CLASSICAL"
        assert report.provenance.sdk_version, "provenance must record the SDK version"
        # SolutionReport is a read-only composite record: its to_dict() is an
        # export/inspection view; its round-trippable members serialize below.
        exported = report.to_dict()
        for key in ("problem", "strategy", "formulation", "provenance", "execution"):
            assert key in exported
        rebuilt_provenance = Provenance.from_dict(report.provenance.to_dict())
        assert rebuilt_provenance.to_dict() == report.provenance.to_dict()
        rebuilt_interpretation = ResultInterpretation.from_dict(result.interpretation.to_dict())
        assert rebuilt_interpretation.to_dict() == result.interpretation.to_dict()


class TestOptionalMicroQuantum:
    def test_availability_contract(self) -> None:
        from quantsmind.quantum import (
            microquantum_available,
            qaoa_available,
        )

        spec = importlib.util.find_spec("microquantum")
        assert microquantum_available() == (spec is not None)
        if qaoa_available():
            assert spec is not None

    def test_blocked_microquantum_is_honest(self) -> None:
        script = (
            "import sys; sys.path[0:0] = [r'{src}']\n"
            "import builtins\n"
            "_real_import = builtins.__import__\n"
            "def _block(name, *a, **k):\n"
            "    if name == 'microquantum' or name.startswith('microquantum.'):\n"
            "        raise ImportError('blocked')\n"
            "    return _real_import(name, *a, **k)\n"
            "builtins.__import__ = _block\n"
            "from quantsmind.quantum import DomainIntelligence\n"
            "from quantsmind.quantum.finance.portfolio_examples import example_portfolio_problem\n"
            "p = example_portfolio_problem().to_financial_problem()\n"
            "r = DomainIntelligence().solve(p, strategy='classical')\n"
            "assert r.feasible is True and r.fallback_used is False\n"
            "r2 = DomainIntelligence().solve(p, strategy='quantum')\n"
            "# honest downgrade: no fake quantum result\n"
            "assert r2.strategy_requested == 'quantum'\n"
            "assert r2.strategy_executed == 'classical'\n"
            "assert r2.fallback_used is True\n"
            "assert r2.feasible is True\n"
            "assert any('no quantum execution' in limitation.lower()\n"
            "               for limitation in r2.limitations)\n"
            "print('HONEST_DOWNGRADE')\n"
        ).format(src=_REPO / "src")
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=240,
        )
        assert proc.returncode == 0, proc.stderr
        assert "HONEST_DOWNGRADE" in proc.stdout


class TestDocumentationLanguage:
    def test_readme_declares_stable_release(self) -> None:
        readme = (_REPO / "src" / "quantsmind" / "quantum" / "README.md").read_text(
            encoding="utf-8"
        )
        assert "QuantsMind Quantum 1.0.1" in readme
        assert "Stable" in readme
        assert "Developer Preview" not in readme
        assert "Pre-Alpha" not in readme
