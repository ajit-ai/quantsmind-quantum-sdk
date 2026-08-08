# QuantsMind SDK — Foundation Package Specification

**Version:** R0.2.0 — Foundation SDK Architecture
**Status:** Specification only. No implementation code. Language-independent
by design so it can be realized in Python first, then C++, Rust, Java, Go,
Julia, and others.
**Audience:** Any engineer or AI implementing `quantsmind.foundation`.

This specification supersedes the abstract-only foundation shipped in
R0.1.0 (`src/quantsmind/foundation/*.py`) with a full, implementable
design: every class's attributes, properties, behaviors, method
contracts, lifecycle, events, exceptions, validation rules,
serialization rules, concurrency notes, telemetry hooks, UML, and test
plan.

## Universal Philosophy

```
System        → contains → Entity
Entity        → has Identity, has State, owns Properties,
                exposes Behaviors, participates in Interactions
Interaction   → changes → State
State         → evolves over → Space and Time
Observation   → produces → Knowledge
Knowledge     → enables → Prediction
Prediction    → enables → Decision
```

Every future domain package (`quantum`, `physics`, `ai`, `astronomy`,
`biology`, `finance`, ...) expresses its concepts as specializations of
this model. Nothing in `foundation` may depend on a domain package —
see `docs/package-dependency-rules.md`.

## How to read this specification

| File | Contents |
|---|---|
| [01-module-descriptions.md](01-module-descriptions.md) | Purpose / Scientific Meaning / Responsibilities / Dependencies / Future Extensions for all 26 modules |
| [classes/entity.md](classes/entity.md) | Full spec: `Entity` (the central class) |
| [classes/system.md](classes/system.md) | Full spec: `System` |
| [classes/state.md](classes/state.md) | Full spec: `State` |
| [classes/interaction.md](classes/interaction.md) | Full spec: `Interaction` |
| [03-supporting-classes.md](03-supporting-classes.md) | Full spec for the 13 supporting concept classes: `Identity`, `Property`, `Attribute`, `Behaviour`, `Relationship`, `Constraint`, `Lifecycle`, `Event`, `Observation`, `Knowledge`, `Transformation`, `Space`, `Time` |
| [04-interfaces-protocols.md](04-interfaces-protocols.md) | `Observable`, `Serializable`, `Cloneable`, `Validatable`, `Comparable`, `Identifiable`, `Timestamped`, plus `protocols.py` |
| [05-enums-types-constants.md](05-enums-types-constants.md) | `enums.py`, `types.py`, `constants.py` |
| [06-exceptions-and-utilities.md](06-exceptions-and-utilities.md) | Exception hierarchy (`exceptions.py`) and `validators.py` / `serializers.py` / `factories.py` architecture |
| [07-events.md](07-events.md) | SDK-wide event hierarchy and event bus contract |
| [08-validation-and-serialization-strategy.md](08-validation-and-serialization-strategy.md) | Cross-cutting validation and serialization strategy |
| [09-uml.md](09-uml.md) | Package, class, sequence, and dependency diagrams (Mermaid) |
| [10-testing-strategy.md](10-testing-strategy.md) | Unit test scenario catalog: positive / negative / boundary / validation / serialization / performance |
| [11-documentation-structure.md](11-documentation-structure.md) | Per-class documentation template and structure |
| [12-roadmap.md](12-roadmap.md) | Foundation-package-specific roadmap |

## Package Tree

```
src/quantsmind/foundation/
├── __init__.py           # public surface (re-exports)
├── entity.py              # Entity
├── system.py               # System
├── state.py                 # State
├── interaction.py            # Interaction
├── identity.py                # Identity
├── property.py                 # Property
├── attribute.py                 # Attribute
├── behaviour.py                   # Behaviour
├── relationship.py                 # Relationship
├── constraint.py                     # Constraint
├── lifecycle.py                       # Lifecycle
├── event.py                             # Event (+ EventBus contract)
├── observation.py                        # Observation
├── knowledge.py                            # Knowledge
├── transformation.py                        # Transformation
├── space.py                                   # Space
├── time.py                                     # Time
├── interfaces.py                                # Observable, Serializable, ...
├── protocols.py                                   # structural typing Protocols
├── enums.py                                         # EntityStatus, EventType, ...
├── validators.py                                      # Validator contracts
├── serializers.py                                       # Serializer contracts
├── factories.py                                           # EntityFactory, SystemFactory, ...
├── exceptions.py                                            # QuantsMindError hierarchy
├── constants.py                                               # SDK-wide constants
└── types.py                                                     # type aliases, TypedDicts, generics
```

This tree replaces the flatter R0.1.0 layout (which had one file per
foundation concept and no infrastructure modules). R0.2.0 adds
`interfaces.py`, `protocols.py`, `enums.py`, `validators.py`,
`serializers.py`, `factories.py`, `exceptions.py`, `constants.py`, and
`types.py` as first-class infrastructure modules that every domain
class-family (Entity/System/...) depends on.

## Design Principles Applied

1. **Composition over inheritance** — `Entity` *has* an `Identity`,
   *has* a `State`, *owns* `Property` objects; it does not inherit
   from them.
2. **Interfaces before implementation** — every capability (cloning,
   serialization, comparison, observability) is expressed as an
   interface in `interfaces.py`/`protocols.py` before any class
   implements it.
3. **Language independence** — no Python-only construct (metaclass
   magic, `__slots__` tricks) is load-bearing in the spec. Interfaces
   map cleanly to C++ abstract classes, Rust traits, Java interfaces,
   Go interfaces, and Julia abstract types + multiple dispatch.
4. **Explicit lifecycle** — every stateful class has a documented
   Lifecycle state machine (see `Lifecycle` class and each class's
   Lifecycle section).
5. **Everything is observable and serializable by default** — `Entity`,
   `System`, `State`, and `Interaction` all implement `Observable` and
   `Serializable`.
