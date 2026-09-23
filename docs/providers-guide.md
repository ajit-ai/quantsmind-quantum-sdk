# Providers Guide

How backends plug into the SDK: vendor-neutral contracts plus one
reference local provider. This guide describes what exists today.

## Roles

| Symbol | Role |
|---|---|
| `IProvider` | Registry of named backends: `capabilities()`, `health()`, `backend_names()`, `get_backend(name)` |
| `IBackend` | One executable backend: `name`, `capabilities()`, `is_available()` |
| `ProviderCapabilities` | Vendor-neutral description (kinds, max qubits, metadata) |
| `ProviderHealth` | Availability flag plus honest message |
| `ProviderRegistry` | Name → provider map with duplicate protection |
| `LocalSimulatorProvider` | Reference implementation over MicroQuantum local backends |
| `ProviderError` (+ `ProviderUnavailableError`, `BackendNotFoundError`, `BackendUnavailableError`) | Typed failures; SDK-wide catch via `QuantsMindError` |

## Local simulator

```python
from quantsmind.providers import LocalSimulatorProvider, ProviderRegistry

registry = ProviderRegistry()
registry.register(LocalSimulatorProvider())
provider = registry.get("local_simulator")
backend = provider.get_backend("statevector")
print(provider.health())          # available=True when microquantum is installed
print(backend.capabilities())     # vendor-neutral view of the native model
```

Importing `quantsmind.providers` never requires MicroQuantum; the engine
is imported lazily and absence surfaces as `ProviderUnavailableError`
— never a silent substitution.

## Boundaries (intentional)

- No simulator is implemented here: execution delegates to
  MicroQuantum's backends (local today; IBM/IonQ hardware stays behind
  MicroQuantum, never a direct SDK dependency).
- No credentials are stored: providers accept passthrough config only.
- No network access in tests: unavailable paths are exercised with
  fakes and import blocking.
- Circuit, algorithm, and optimizer logic stays in MicroQuantum;
  domain orchestration stays in `quantsmind.quantum` and
  `quantsmind.runtime`. This package only describes and locates
  backends.

Pinned by `tests/unit/providers/test_provider_abcs.py`.
