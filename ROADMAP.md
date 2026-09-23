# Roadmap

QuantsMind is designed for at least twenty years of evolution. The
roadmap below reflects the architecture-first philosophy: each release
implements one layer at a time, on a stable foundation.

## Where we are: 1.0.1 (current)

**QuantsMind Quantum 1.0.1** is the current stable release: a
domain-oriented quantum intelligence SDK (finance / portfolio, data, ML)
executing through classical, quantum, or hybrid strategies via the
optional MicroQuantum engine (`pip install "quantsmind[quantum]"`,
pinned to the tested `microquantum>=0.4,<0.5` series). The quantum public
API is frozen at the `api_manifest.json` baseline (117 modules,
669 symbols) and gated in CI (ruff, `mypy --strict`, full unit suite plus
a >=80% coverage gate on `quantsmind.quantum`, currently ~89%).

Beyond quantum, package maturity varies honestly:

| Status | Packages |
|---|---|
| Stable, tested | `quantum`, `foundation` (mypy-strict clean, importable, unit-tested) |
| Implemented, tested paths | `runtime` (job/task/pipeline/workflow), `calculus` (differentiation), `math` (geometry, topology, numerical), `scientific` (metadata, coordinates, time), `optimization` (gradient/Adam), `knowledge` (importable, value objects tested), `ai_reasoning` helpers |
| Contracts / skeletons | `physics`, `chemistry`, `biology`, `astronomy`, `cosmology`, `finance` (top level), `ai`, `compiler`, `providers`, `simulation`, `visualization`, `datasets`, `plugins`, `telemetry`, plus cross-cutting `config`, `io`, `logging`, `security`, `utils` |

See `docs/known-limitations.md` for the honest gap list and
`CHANGELOG.md` for per-release history.

## How we got here

- **R0.1.0 — Architecture Foundation (historical):** repository structure,
  34 package skeletons, foundation ontology interfaces, quantum skeletons,
  docs standards, ADR process, dependency rules, DevOps scaffolding. No
  algorithms implemented anywhere.
- **1.0.0 (2026-09-13) — QuantsMind Quantum, stable:** domain-oriented
  quantum intelligence SDK over MicroQuantum (QMQ-01..QMQ-12), frozen API
  manifest, release-hardening tests. Note: the quantum path went through
  MicroQuantum integration rather than the originally sketched local
  statevector provider.
- **1.0.1 (2026-09-23) — Correctness patch, API unchanged:** foundation
  `Serializable` conformance, `utcnow()` deprecation removal repo-wide,
  undefined-name andadowing fixes, two real `NameError` crashes fixed
  (galactic conversion, Newton-Raphson), `knowledge` made importable,
  regression + helper tests, quantum coverage gate in CI.

## What remains (epics, each planned separately before work starts)

- **Math backend:** `math` linear/tensor algebra on a pluggable numeric
  backend (NumPy first); complex numbers, numerical methods.
- **Runtime & providers:** local in-process executor end-to-end example
  (Bell-state style); reference local-simulator provider backend;
  minimal compiler IR.
- **Domains:** simulation engine concretely; physics (classical mechanics
  first); then chemistry, biology, astronomy, cosmology building on it;
  finance on top of `math`/`optimization`/`ai`; AI/optimization contracts.
- **Platform:** plugin discovery, telemetry exporters, visualization and
  datasets adapters, security review of credential handling.
- **Beyond:** real quantum hardware / cloud HPC providers, distributed
  runtime, GPU/TPU-backed math, expanded domain coverage.

## Working agreements

- `main` is always releasable: CI (lint, type-check, tests, quantum
  coverage gate) and docs deployment must be green before merge.
- Changes land via `develop` → `main` merges; releases are `v*` tags
  built by the release workflow. See `docs/release-strategy.md` and
  `docs/versioning-policy.md`.
- Design intent lives in `architecture/` (ADRs) and
  `docs/foundation-specification/`; what may depend on what is fixed in
  `docs/package-dependency-rules.md`.
