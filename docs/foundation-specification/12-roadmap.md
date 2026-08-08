# Foundation Package Roadmap

This specializes the SDK-wide `ROADMAP.md` for the `foundation`
package specifically. R0.2.0 (this specification) is design-only; the
items below sequence how it becomes real code.

## R0.2.0 — Specification (this release)
- Complete module descriptions for all 26 `foundation` modules.
- Full class specifications for `Entity`, `System`, `State`,
  `Interaction` (core) and the 13 supporting classes.
- Interface/Protocol contracts, enum/type/constant catalog, exception
  hierarchy, event hierarchy.
- Validation and serialization cross-cutting strategy.
- UML (package, class, sequence, dependency).
- Testing strategy (scenario catalog, not test code).
- Documentation structure and completeness gate.
- **No implementation code.**

## R0.2.1 — Infrastructure-first implementation
- Implement `exceptions.py`, `types.py`, `enums.py`, `constants.py`
  (the four zero-dependency leaf modules) exactly as specified here.
- Implement `interfaces.py` and `protocols.py`.
- Unit tests for all of the above (they are the easiest to fully
  cover — pure data/contract definitions).

## R0.2.2 — Value objects
- Implement `Identity`, `Time`, `Space`, `Property` — the immutable,
  dependency-light value classes.
- Implement `validators.py`'s built-in Validator library.

## R0.2.3 — Stateful primitives
- Implement `State`, `Attribute`, `Event` + reference `EventBus`.
- Implement `serializers.py`'s JSON serializer first (per the
  recommendation in `state.md`'s Serialization section — `State` is
  the simplest target).

## R0.2.4 — Core ontology classes
- Implement `Lifecycle`, `Behaviour`, `Relationship`, `Constraint`.
- Implement `Entity` in full, satisfying every method contract in
  `classes/entity.md`.
- Full `tests/unit/foundation/entity` suite per
  `10-testing-strategy.md` §Entity.

## R0.2.5 — Composition & orchestration
- Implement `Transformation`, `Interaction` (including the
  atomic-commit rollback guarantee).
- Implement `System`.
- Full `tests/unit/foundation/{system,interaction}` suites.

## R0.2.6 — Knowledge layer & factories
- Implement `Observation`, `Knowledge`.
- Implement `factories.py` (`EntityFactory`, `SystemFactory`,
  `InteractionFactory`, `EventFactory`, `FactoryRegistry`).
- Implement remaining `SerializationFormat`s (YAML, MessagePack,
  Binary) — Protocol Buffers deferred to R0.3.0 pending schema design.

## R0.2.7 — Documentation & hardening
- Generate full API reference site per `11-documentation-structure.md`.
- Complete `tests/integration/foundation` scenarios (cross-class
  interactions: `System.run_interaction()` end-to-end, serialization
  round-trips across the full object graph).
- `tests/performance/foundation` budgets from
  `10-testing-strategy.md`'s Performance Considerations turned into
  enforced CI thresholds.

## R0.3.0 — First consumer: `quantum` domain package
- `quantum.Qubit(Entity)`, `quantum.Circuit(System)`,
  `quantum.GateApplication(Interaction)` implemented against the
  now-stable `foundation` API — the first real validation that the
  ontology generalizes as designed.
- Any friction discovered here feeds back as `foundation` patch
  releases (R0.2.x) before `quantum` proceeds, per the "architecture
  before code" and "interfaces before implementations" principles.

## Beyond R0.3.0
- Protocol Buffers schema generation, enabling the C++/Rust/Java/Go/
  Julia ports referenced throughout this specification.
- `EventType` open-enumeration/registry mechanism finalized based on
  real multi-domain usage (see `07-events.md` extension policy).
- Distributed `EventBus` implementation (`runtime` package).
- Constraint-solver integration for `Constraint` (`optimization`
  package collaboration).
