"""Internal helpers for the optional MicroQuantum integration.

This module centralises the lazy, optional import of MicroQuantum so that
``import quantsmind.quantum`` never requires ``microquantum`` to be
installed.  All MicroQuantum access from the integration layer flows
through :func:`require_microquantum`.
"""

from __future__ import annotations

from types import ModuleType
from typing import Any

_INSTALL_HINT = (
    "Quantum integration requires the optional 'microquantum' dependency. "
    "Install it with: pip install 'quantsmind[quantum]'"
)


def microquantum_available() -> bool:
    """Return True when the optional ``microquantum`` package is installed."""
    try:
        import microquantum  # noqa: F401
    except ImportError:
        return False
    return True


def require_microquantum() -> ModuleType:
    """Import and return the ``microquantum`` module, with a clear error."""
    try:
        import microquantum
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(_INSTALL_HINT) from exc
    return microquantum


def resolve_backend(backend: Any) -> Any:
    """Resolve a backend name or instance into a MicroQuantum Backend.

    ``None`` is passed through so MicroQuantum picks its default.  A string
    is looked up on MicroQuantum's local provider.  Anything else is
    assumed to already be a MicroQuantum Backend instance.
    """
    if backend is None or not isinstance(backend, str):
        return backend
    mq = require_microquantum()
    provider = mq.LocalProvider()
    if not provider.has_backend(backend):
        available = ", ".join(str(b) for b in provider.backends())
        raise ValueError(f"unknown backend {backend!r}; available: {available}")
    return provider.get_backend(backend)


__all__ = ["microquantum_available", "require_microquantum", "resolve_backend"]
