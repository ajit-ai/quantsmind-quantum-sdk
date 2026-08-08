# ADR 0001: Foundation Ontology

## Status
Accepted (R0.1.0)

## Context
QuantsMind must support wildly different scientific domains (quantum
computing, physics, chemistry, biology, astronomy, cosmology, finance,
AI) under one coherent model, without each domain reinventing its own
notion of "thing", "state", and "change".

## Decision
Adopt a single universal ontology: Entity, System, State, Interaction,
Identity, Property, Attribute, Relationship, Behaviour, Constraint,
Space, Time, Event, Observation, Knowledge, Transformation, Lifecycle.
Every domain package specializes these rather than defining parallel
concepts.

## Consequences
- (+) Cross-domain tooling (visualization, telemetry, datasets) can be
  written once against the foundation layer.
- (+) New domains onboard by specializing existing contracts.
- (-) The ontology must stay abstract enough to not leak
  domain-specific assumptions (mitigated: foundation has zero
  dependencies on any domain package).
