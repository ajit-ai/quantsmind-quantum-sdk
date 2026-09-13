# QuantsMind SDK

**A Universal Scientific Computing SDK — hardware-independent,
vendor-independent, and built to evolve for decades.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue)]()
[![Python](https://img.shields.io/badge/python-3.13%2B-blue)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-green)]()
[![Status](https://img.shields.io/badge/status-stable-green)]()

## What is QuantsMind?

QuantsMind is not another Quantum SDK. It is a single, coherent
foundation for scientific computing across mathematics, physics,
chemistry, biology, astronomy, cosmology, quantum computing, AI,
finance, and simulation — all built on one first-principle model:

> A System is composed of Entities. Every Entity has Identity,
> Properties, State, Behaviour, Relationships, Constraints, and
> History. Entities evolve through Interactions. Interactions change
> State. State evolves over Space and Time. Observation of evolution
> produces Knowledge. Knowledge enables Prediction. Prediction enables
> Decision.

Every package in this SDK — from `quantum` to `finance` to `biology` —
specializes this same ontology instead of reinventing its own.

## Release: QuantsMind Quantum 1.0.0 — Stable

The current stable release is **QuantsMind Quantum 1.0.0**: a domain-oriented
quantum intelligence SDK that transforms supported real-world optimization
problems (finance / portfolio, data, ML) into mathematical computational
workflows and executes them through **classical, quantum, or hybrid**
strategies, with benchmarking, interpretation, and provenance.  See
`src/quantsmind/quantum/README.md` for installation, the quick-start example,
the supported domains, and honest limitations.  The quantum public API is
frozen at the `api_manifest.json` baseline.

The R0.1.0 architecture-only foundation below is **historical** — the initial
package layout, public interface contracts, and documentation standards that
the current release builds on.  See `ROADMAP.md` for the broader SDK.

## Repository Layout

```
quantsmind-sdk/
├── src/quantsmind/        # all installable packages (architecture-only)
├── docs/                  # architecture, developer & contribution docs
├── architecture/          # architecture decision records (ADRs)
├── research/              # exploratory notes, not part of public API
├── examples/              # usage examples (shape-only in R0.1.0)
├── tutorials/             # onboarding material
├── tests/                 # unit / integration / regression / performance
├── benchmarks/            # long-running performance tracking
├── scripts/               # developer & CI utility scripts
├── configs/               # default non-secret configuration
├── assets/                # docs/branding static assets
├── tools/                 # internal dev tooling (not shipped)
└── .github/                # CI workflows, issue/PR templates
```

See `docs/architecture-overview.md` for the full layering model and
`docs/package-dependency-rules.md` for what may depend on what.

## Packages (`src/quantsmind`)

| Package | Purpose |
|---|---|
| `foundation` | Universal ontology: Entity, System, State, Interaction, ... |
| `core` | Shared abstractions built on foundation |
| `runtime` | Execution model: scheduling & dispatch |
| `compiler` | IR and transformation pipeline contracts |
| `providers` | Vendor-independent hardware/cloud/simulator backend contracts |
| `simulation` | Generic System-evolution-over-time contracts |
| `math` | Linear algebra, tensors, geometry, probability, statistics, calculus, optimization primitives, graph theory, complex numbers, numerical methods |
| `algebra` | Polynomial/matrix/vector/tensor engines |
| `calculus` | Differentiation, integration, ODE solvers |
| `numerical` | Root finding, interpolation, curve fitting, error analysis |
| `statistics` | Probability & distribution engines, statistical analysis |
| `optimization` | Objective/constraint/solver contracts |
| `quantum` | Integration layer over MicroQuantum: QuantumProgram, QuantumExperiment, QuantumResult, algorithm delegation |
| `physics` | Physical systems domain model |
| `chemistry` | Molecular/chemical systems domain model |
| `biology` | Biological systems domain model |
| `astronomy` | Astronomical systems domain model |
| `cosmology` | Universe-scale structure/evolution domain model |
| `finance` | Quantitative finance domain model |
| `ai` | AI/ML domain model |
| `ai_reasoning` | AI-assisted mathematical reasoning agents |
| `ml_math` | Loss/activation functions, feature transforms |
| `scientific` | Units, constants, coordinates, measurements |
| `knowledge` | Knowledge graphs, provenance, ontologies |
| `visualization` | Rendering-agnostic visualization contracts |
| `datasets` | Dataset discovery/loading contracts |
| `plugins` | Third-party extension mechanism |
| `utils` | Dependency-free helper contracts |
| `logging` | Vendor-independent logging interface |
| `config` | Configuration loading/resolution contracts |
| `exceptions` | SDK-wide exception hierarchy |
| `io` | File/stream/network I/O contracts |
| `security` | Auth, credentials, secrets contracts |
| `telemetry` | Metrics, tracing, observability contracts |
| `api` | Optional REST API layer (requires `[api]` extra) |

## Installation (future)

```bash
pip install quantsmind
```

## Development

```bash
git clone <repo-url>
cd quantsmind-sdk
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
pytest tests/unit
```

## Documentation

Start at `docs/README.md`. Key entry points:

- [Architecture Overview](docs/architecture-overview.md)
- [Developer Guide](docs/developer-guide.md)
- [Package Dependency Rules](docs/package-dependency-rules.md)
- [Roadmap](ROADMAP.md)

## Contributing

See `CONTRIBUTING.md`. All new packages must follow the documentation
standard in `docs/documentation-standards.md`.

## Security

See `SECURITY.md` for how to report vulnerabilities.

## License

Apache License 2.0 — see `LICENSE`.
