"""Unit tests for the provider ABCs and the local reference provider (9-C)."""

from __future__ import annotations

import pytest

from quantsmind.providers import (
    BackendNotFoundError,
    IBackend,
    IProvider,
    LocalSimulatorProvider,
    ProviderCapabilities,
    ProviderError,
    ProviderHealth,
    ProviderRegistry,
)

pytest.importorskip("microquantum")


class FakeBackend(IBackend):
    def __init__(self, name: str = "fake") -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(name=self._name, kinds=frozenset({"simulator"}))

    def is_available(self) -> bool:
        return True


class FakeProvider(IProvider):
    def __init__(self, name: str = "fake") -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(name=self._name)

    def health(self) -> ProviderHealth:
        return ProviderHealth(available=True, message="fake ready")

    def backend_names(self) -> list[str]:
        return ["fake"]

    def get_backend(self, name: str) -> FakeBackend:
        if name != "fake":
            raise BackendNotFoundError(f"unknown backend {name!r}")
        return FakeBackend(name)


class TestInterfaces:
    def test_fakes_satisfy_abcs(self) -> None:
        provider = FakeProvider()
        backend = provider.get_backend("fake")
        assert isinstance(backend, IBackend)
        assert backend.is_available() is True
        assert provider.health() == ProviderHealth(available=True, message="fake ready")

    def test_unknown_backend_raises_typed_error(self) -> None:
        with pytest.raises(BackendNotFoundError):
            FakeProvider().get_backend("nope")

    def test_provider_errors_share_base(self) -> None:
        assert issubclass(BackendNotFoundError, ProviderError)


class TestRegistry:
    def test_register_get_unregister(self) -> None:
        registry = ProviderRegistry()
        registry.register(FakeProvider("a"))
        assert registry.provider_count == 1
        assert registry.names() == ["a"]
        assert isinstance(registry.get("a"), FakeProvider)
        assert registry.get("missing") is None
        assert registry.unregister("a") is True
        assert registry.unregister("a") is False

    def test_duplicate_rejected(self) -> None:
        registry = ProviderRegistry()
        registry.register(FakeProvider("a"))
        with pytest.raises(ProviderError):
            registry.register(FakeProvider("a"))


class TestLocalSimulatorProvider:
    def test_lists_statevector(self) -> None:
        assert "statevector" in LocalSimulatorProvider().backend_names()

    def test_health_ready(self) -> None:
        health = LocalSimulatorProvider().health()
        assert health.available is True

    def test_capabilities_map_natively(self) -> None:
        backend = LocalSimulatorProvider().get_backend("statevector")
        capabilities = backend.capabilities()
        assert capabilities.name == "statevector"
        assert "simulator" in capabilities.kinds
        assert "statevector" in capabilities.metadata["execution"]
        assert backend.is_available() is True

    def test_unknown_backend_honest(self) -> None:
        with pytest.raises(BackendNotFoundError):
            LocalSimulatorProvider().get_backend("nope")

    def test_missing_engine_honest(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import sys

        monkeypatch.setitem(sys.modules, "microquantum", None)
        from quantsmind.providers import ProviderUnavailableError

        provider = LocalSimulatorProvider()
        assert provider.health().available is False
        with pytest.raises(ProviderUnavailableError):
            provider.backend_names()
