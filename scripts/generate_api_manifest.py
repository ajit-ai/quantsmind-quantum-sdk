"""Generate the QuantsMind Quantum public API manifest (QMQ-12).

The manifest is a deterministic, machine-readable snapshot of the public
1.0 API surface. It lists, per public module, the sorted ``__all__``
symbols.  A future release can re-run this script and diff the output to
detect accidental public-API breakage; the committed manifest is also
verified by ``tests/unit/quantum/test_release_qmq12.py``.

Usage (from the repository root):

    python scripts/generate_api_manifest.py [output.json]

Only *public* modules are included: any module whose name contains a
leading-underscore segment (``_mq``, ``_expr``, ``_validation``) is
treated as internal and excluded, matching the package convention that
internal modules are private.
"""

from __future__ import annotations

import importlib
import json
import pkgutil
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
_PACKAGE = "quantsmind.quantum"

_MANIFEST_HEADER = {
    "version": "1.0.0",
    "package": "quantsmind",
    "api": "quantsmind.quantum",
    "generated_by": "scripts/generate_api_manifest.py",
    "scope": "public modules of quantsmind.quantum and its subpackages",
}


def is_public_module(module_name: str) -> bool:
    parts = module_name.split(".")
    return not any(part.startswith("_") for part in parts[1:])


def collect_modules() -> list[str]:
    if str(_SRC) not in sys.path:
        sys.path.insert(0, str(_SRC))
    pkg = importlib.import_module(_PACKAGE)
    module_names = [info.name for info in pkgutil.walk_packages(pkg.__path__, _PACKAGE + ".")]
    return sorted(module for module in module_names if is_public_module(module))


def build_manifest() -> dict[str, object]:
    if str(_SRC) not in sys.path:
        sys.path.insert(0, str(_SRC))
    modules = collect_modules()
    surface: dict[str, list[str]] = {}
    for module_name in modules:
        module = importlib.import_module(module_name)
        all_names = getattr(module, "__all__", None)
        if all_names is None:
            continue
        duplicates = sorted({name for name in all_names if all_names.count(name) > 1})
        if duplicates:
            raise SystemExit(f"module {module_name} has duplicate __all__ entries: {duplicates}")
        missing = sorted(name for name in all_names if not hasattr(module, name))
        if missing:
            raise SystemExit(f"module {module_name} has unresolved __all__ entries: {missing}")
        surface[module_name] = sorted(all_names)
    return {**_MANIFEST_HEADER, "modules": surface}


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else _ROOT / "api_manifest.json"
    manifest = build_manifest()
    target.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    module_count = len(manifest["modules"])
    symbol_count = sum(len(names) for names in manifest["modules"].values())
    print(f"wrote {target} ({module_count} modules, {symbol_count} symbols)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
