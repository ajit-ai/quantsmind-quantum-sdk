"""Unit tests for the top-level quantsmind package surface (lazy loading)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import quantsmind

_SRC = str(Path(__file__).parents[2] / "src")


class TestPackageMetadata:
    """Version metadata must stay consistent with pyproject."""

    def test_version_matches_pyproject(self) -> None:
        import tomllib

        pyproject = Path(__file__).parents[2] / "pyproject.toml"
        expected = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]
        assert quantsmind.__version__ == expected


class TestLazyImports:
    """PEP 562 lazy attribute access keeps the base import dependency-free."""

    def test_lazy_table_is_declared(self) -> None:
        assert isinstance(quantsmind._LAZY_ATTRS, dict)
        assert len(quantsmind._LAZY_ATTRS) > 50

    def test_base_import_pulls_no_optional_deps(self) -> None:
        # In a pristine interpreter, importing quantsmind must not import
        # optional heavy dependencies such as pydantic/fastapi.
        code = (
            f"import sys; sys.path.insert(0, r'{_SRC}'); "
            "import quantsmind; "
            "banned = {'pydantic', 'fastapi', 'numpy'} & set(sys.modules); "
            "assert not banned, f'eager imports: {banned}'"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, result.stderr

    def test_lazy_name_resolution_caches(self) -> None:
        first = quantsmind.clamp
        second = quantsmind.clamp
        assert first is second  # cached in globals after first access

    def test_lazy_resolution_returns_working_objects(self) -> None:
        assert quantsmind.clamp(5, 0, 3) == 3
        assert quantsmind.safe_division(1, 0) == 0.0

    def test_unknown_attribute_raises_attribute_error(self) -> None:
        try:
            quantsmind.definitely_not_a_real_name  # noqa: B018
        except AttributeError as exc:
            assert "definitely_not_a_real_name" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("expected AttributeError")

    def test_dir_exposes_public_names(self) -> None:
        listing = dir(quantsmind)
        for name in ("Matrix", "clamp", "__version__"):
            assert name in listing
