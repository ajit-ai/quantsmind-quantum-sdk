# QuantsMind SDK

**A Universal Scientific Computing SDK — hardware-independent, vendor-independent, and built to evolve for decades.**

![Version](https://img.shields.io/badge/version-1.0.0-blue) ![Python](https://img.shields.io/badge/python-3.13%2B-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green) ![Status](https://img.shields.io/badge/status-stable-green)

## What is QuantsMind?

QuantsMind is not another Quantum SDK. It is a single, coherent foundation for scientific computing across mathematics, physics, chemistry, biology, astronomy, cosmology, quantum computing, AI, finance, and simulation — all built on one first-principle model:

> A System is composed of Entities. Every Entity has Identity, Properties, State, Behaviour, Relationships, Constraints, and History. Entities evolve through Interactions. Interactions change State. State evolves over Space and Time. Observation of evolution produces Knowledge. Knowledge enables Prediction. Prediction enables Decision.

Every package in this SDK — from `quantum` to `finance` to `biology` — specializes this same ontology instead of reinventing its own.

## Release: QuantsMind Quantum 1.0.0 — Stable

The current stable release is **QuantsMind Quantum 1.0.0**: a domain-oriented quantum intelligence SDK that transforms supported real-world optimization problems (finance / portfolio, data, ML) into mathematical computational workflows and executes them through **classical, quantum, or hybrid** strategies, with benchmarking, interpretation, and provenance. The quantum public API is frozen at the `api_manifest.json` baseline (117 modules, 669 public symbols).

See the **Quantum Guide** for installation, the quick-start example, the supported domains, and honest limitations, and the **API Reference** for the full public surface of the quantum layer.

## Explore the Documentation

| Section | Description |
| --- | --- |
| [Quantum Guide](quantum.md) | Install the SDK, run your first quantum workflow, understand the supported domains and honest limitations. |
| [API Reference](reference/quantum.md) | Auto-generated reference for the `quantsmind.quantum` package. |
| [Architecture Overview](architecture-overview.md) | The full layering model of the SDK. |
| [Developer Guide](developer-guide.md) | Setting up the development environment and contributing. |
| [Package Dependency Rules](package-dependency-rules.md) | What may depend on what. |
| [Foundation Package Specification](foundation-specification/README.md) | Full design of `quantsmind.foundation` (R0.2.0). |

## Installation

```bash
pip install quantsmind              # core SDK (no engine)
pip install "quantsmind[quantum]"   # + MicroQuantum engine for the quantum layer
```

## License

Apache License 2.0 — see the repository `LICENSE`.

## Repository

Docs are built from `docs/` in the [GitHub repository](https://github.com/ajit-ai/quantsmind-quantum-sdk).