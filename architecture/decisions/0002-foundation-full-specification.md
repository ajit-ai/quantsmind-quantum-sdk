# ADR 0002: Foundation Package Full Specification (R0.2.0)

## Status
Accepted (R0.2.0)

## Context
R0.1.0 shipped `foundation` as bare `ABC` skeletons (one `describe()`
method each) — enough to prove the ontology's shape and dependency
graph, but not enough for another engineer or AI to implement it
consistently. QuantsMind also commits to eventual C++/Rust/Java/Go/
Julia ports, which means the Python implementation cannot rely on
Python-only idioms to convey the contract.

## Decision
Produce a complete, language-independent specification for every
`foundation` module and class *before* writing implementation code:
attributes, properties, behaviors, method contracts (signature,
pre/postconditions, exceptions), private helpers, lifecycle, events,
exceptions, interfaces, validation rules, serialization rules, thread
safety, logging/telemetry hooks, UML, and a test-scenario catalog.
Nine infrastructure modules (`interfaces`, `protocols`, `enums`,
`validators`, `serializers`, `factories`, `exceptions`, `constants`,
`types`) are added as first-class modules, splitting off
cross-cutting concerns that R0.1.0 had not yet identified as needing
their own home.

The specification lives at `docs/foundation-specification/` rather
than as inline code comments, so it can be reviewed, versioned, and
implemented independently of any single language binding.

## Consequences
- (+) An implementer (human or AI) can build `foundation` from this
  spec without re-deriving design decisions already made here.
- (+) The nominal/structural interface split (`interfaces.py` vs.
  `protocols.py`) gives a documented mapping onto every target
  language's contract mechanism (ABC/trait/interface).
- (+) Cross-cutting concerns (validation, serialization, events,
  exceptions) are specified once, centrally, and referenced by every
  class spec — avoiding the "duplicate concepts" anti-pattern.
- (-) The specification is large (16 files); mitigated by the index in
  `docs/foundation-specification/README.md` and consistent per-class
  structure so any single file is self-contained once the shared
  cross-cutting files are read once.
- Implementation now proceeds per
  `docs/foundation-specification/12-roadmap.md` (R0.2.1 through
  R0.2.7), replacing the R0.1.0 abstract skeletons module by module.
