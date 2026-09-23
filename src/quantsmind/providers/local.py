"""Local simulator provider (reference implementation).

Delegates to MicroQuantum's local backends through a lazy import, so
``import quantsmind.providers`` never requires ``microquantum``. This is
the only concrete provider shipped with the SDK: it proves the ABC seam
without duplicating any simulator. Hardware and cloud providers live
behind MicroQuantum and are intentionally out of scope here.
"""

from __future__ import annotations

from typing import Any

from quantsmind.providers.exceptions import (
    BackendNotFoundError,
    ProviderError,
    ProviderUnavailableError,
)
from quantsmind.providers.interfaces import (
    IBackend,
    IProvider,
    ProviderCapabilities,
    ProviderHealth,
)

_INSTALL_HINT = (
    "Local simulator execution requires the optional 'microquantum' "
    "dependency. Install it with: pip install 'quantsmind[quantum]'"
)


def _require_microquantum() -> Any:
    """Import MicroQuantum or raise an honest typed error."""
    try:
        import microquantum
    except ImportError as exc:
        raise ProviderUnavailableError(_INSTALL_HINT) from exc
    return microquantum


class LocalBackend(IBackend):
    """An :class:`IBackend` view over one MicroQuantum local backend."""

    def __init__(self, backend_name: str) -> None:
        """Bind to a MicroQuantum local backend by name."""
        self._backend_name = backend_name

    @property
    def name(self) -> str:
        """Backend identity."""
        return self._backend_name

    def _native(self) -> Any:
        microquantum = _require_microquantum()
        provider = microquantum.LocalProvider()
        if not provider.has_backend(self._backend_name):
            raise BackendNotFoundError(
                f"unknown local backend {self._backend_name!r}",
                details={"available": [str(b) for b in provider.backends()]},
            )
        return provider.get_backend(self._backend_name)

    def capabilities(self) -> ProviderCapabilities:
        """Map the native capability model onto vendor-neutral terms."""
        native = self._native().capabilities
        kinds = frozenset({"simulator"})
        metadata = {
            "target_class": str(getattr(native, "target_class", "")),
            "execution": sorted(getattr(native, "execution", set())),
        }
        return ProviderCapabilities(
            name=self._backend_name,
            kinds=kinds,
            max_qubits=getattr(native, "max_qubits", None),
            metadata=metadata,
        )

    def is_available(self) -> bool:
        """True when MicroQuantum resolves this backend."""
        try:
            self._native()
        except ProviderError:
            return False
        return True


class LocalSimulatorProvider(IProvider):
    """Reference provider over MicroQuantum's local backends."""

    def __init__(self, default_backend: str = "statevector") -> None:
        """Create the provider (no engine import at construction)."""
        self._default_backend = default_backend

    @property
    def name(self) -> str:
        """Provider identity."""
        return "local_simulator"

    @property
    def default_backend(self) -> str:
        """Backend used when callers do not name one."""
        return self._default_backend

    def _provider(self) -> Any:
        return _require_microquantum().LocalProvider()

    def capabilities(self) -> ProviderCapabilities:
        """Describe this provider (lists exposed backend names)."""
        return ProviderCapabilities(
            name=self.name,
            kinds=frozenset({"simulator"}),
            metadata={"backends": self.backend_names()},
        )

    def health(self) -> ProviderHealth:
        """Report availability (honest when MicroQuantum is missing)."""
        try:
            names = self.backend_names()
        except ProviderUnavailableError as exc:
            return ProviderHealth(available=False, message=str(exc))
        if self._default_backend not in names:
            return ProviderHealth(
                available=False,
                message=f"default backend {self._default_backend!r} not exposed",
            )
        return ProviderHealth(available=True, message="local simulator ready")

    def backend_names(self) -> list[str]:
        """Names exposed by MicroQuantum's local provider."""
        provider = self._provider()
        return sorted(getattr(backend, "name", str(backend)) for backend in provider.backends())

    def get_backend(self, name: str) -> IBackend:
        """Return a :class:`LocalBackend` view, or raise honestly."""
        if name not in self.backend_names():
            raise BackendNotFoundError(
                f"unknown local backend {name!r}",
                details={"available": self.backend_names()},
            )
        return LocalBackend(name)


__all__ = ["LocalBackend", "LocalSimulatorProvider"]
