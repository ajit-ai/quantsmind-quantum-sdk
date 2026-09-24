"""Provider registry: locate the statevector backend honestly.

Feature: `ProviderRegistry` + `LocalSimulatorProvider`.
Purpose: show discovery, health, and capability mapping.
Input: none (uses the local MicroQuantum install when present).
Processing: register -> health check -> backend lookup.
Output: provider names, readiness flag, backend capabilities.
Meaning: backends are described and located, never faked.

Run from the repository root::

    python examples/providers/registry_demo.py
"""

from __future__ import annotations

from quantsmind.providers import LocalSimulatorProvider, ProviderRegistry


def main() -> None:
    registry = ProviderRegistry()
    registry.register(LocalSimulatorProvider())
    print(f"providers: {registry.names()}")
    provider = registry.get("local_simulator")
    health = provider.health()
    print(f"ready: {health.available}")
    if health.available:
        backend = provider.get_backend("statevector")
        print(f"backend: {backend.capabilities().name}")
    else:
        print("hint: pip install 'quantsmind[quantum]'")


if __name__ == "__main__":
    main()
