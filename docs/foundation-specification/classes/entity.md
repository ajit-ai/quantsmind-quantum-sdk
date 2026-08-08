# Class Specification: `Entity`

## General

- **Class Name:** `Entity`
- **Description:** The atomic unit of the QuantsMind ontology. Anything
  that can be identified, measured, and reasoned about — a qubit, a
  particle, a portfolio, a molecule, an AI model — is represented as an
  `Entity` or a domain-specific subclass of it.
- **Design Rationale:** Composition over inheritance: `Entity` *owns*
  an `Identity`, a `State`, a set of `Property` and `Attribute`
  objects, a `Behaviour` set, `Relationship`s, and `Constraint`s,
  rather than mixing all of that into one monolithic class hierarchy.
  This keeps `Entity` stable while every concern it delegates to can
  evolve independently.
- **Scientific Meaning:** The referent that persists across
  measurements — the "thing" whose State changes while its Identity
  does not.
- **SDK Purpose:** The single class every domain package specializes
  (`Qubit(Entity)`, `Particle(Entity)`, `Portfolio(Entity)`, ...) to
  get Identity, State, lifecycle, events, validation, and
  serialization for free.

## Relationships

- **Parent Class:** None (root of the ontology hierarchy). Implements
  interfaces directly.
- **Child Classes:** Domain-specific specializations, e.g.
  `quantum.Qubit`, `physics.Particle`, `finance.Instrument` (defined in
  their respective domain packages, not in `foundation`).
- **Interfaces Implemented:** `Identifiable`, `Observable`,
  `Serializable`, `Cloneable`, `Validatable`, `Comparable`,
  `Timestamped`.
- **Collaborating Classes:** `Identity`, `State`, `Property`,
  `Attribute`, `Behaviour`, `Relationship`, `Constraint`, `Lifecycle`,
  `Event`, `System` (containment), `Interaction` (participation).

## Attributes

| Attribute | Type | Explanation |
|---|---|---|
| `id` | `EntityId` (alias of `str`/`UUID`) | Machine-generated unique identifier, delegated to `Identity.id`. |
| `uuid` | `UUID` | Canonical universally-unique identifier form of `id`. |
| `name` | `str` | Human-readable, non-unique display name. |
| `label` | `str \| None` | Optional short label for UI/diagram rendering. |
| `type` | `str` | Fully-qualified domain type name (e.g. `"quantum.Qubit"`), set by subclasses. |
| `metadata` | `dict[str, Any]` | Free-form, non-schema-validated key/value bag for extensions. |
| `properties` | `dict[str, Property]` | Immutable, intrinsic characteristics keyed by name. |
| `attributes` | `dict[str, Attribute]` | Mutable, extrinsic characteristics keyed by name. |
| `state` | `State` | Current State snapshot. |
| `history` | `list[State]` | Ordered, append-only sequence of past State snapshots (bounded by policy; see Constants). |
| `relationships` | `list[Relationship]` | Relationships this Entity participates in. |
| `constraints` | `list[Constraint]` | Constraints this Entity's State must satisfy. |
| `behaviour` | `Behaviour` | Declares which Interactions this Entity may participate in. |
| `lifecycle` | `Lifecycle` | Current lifecycle stage and transition history. |
| `tags` | `set[str]` | Free-form categorization tags for querying/filtering. |
| `version` | `int` | Monotonically increasing optimistic-concurrency version, incremented on every State change. |
| `created_at` | `Time` | Instant of creation (from `Timestamped`). |
| `updated_at` | `Time` | Instant of last modification (from `Timestamped`). |

## Properties (Python `@property` candidates)

- `id` — read-only, derived from `identity.id`.
- `is_active` — read-only, derived from `lifecycle.stage == LifecycleStage.ACTIVE`.
- `current_state` — read-only alias for `state` (explicit name for
  clarity in Interaction code).
- `age` — read-only, computed as `Time.now() - created_at`.
- `relationship_count` — read-only, `len(relationships)`.

## Behaviors (conceptual)

| Behavior | Purpose |
|---|---|
| `create()` | Factory-invoked construction; assigns Identity, initializes empty State, sets lifecycle to `CREATED`. |
| `initialize()` | Populate initial Properties/Attributes from constructor input; validates them; transitions lifecycle to `INITIALIZED`. |
| `activate()` | Marks the Entity as eligible to participate in Interactions; transitions lifecycle to `ACTIVE`. |
| `deactivate()` | Temporarily excludes the Entity from new Interactions without destroying it; transitions lifecycle to `INACTIVE`. |
| `suspend()` | Freezes State mutation (used during audits/migrations); transitions lifecycle to `SUSPENDED`. |
| `destroy()` | Terminal transition; releases resources, emits `EntityDestroyed`; transitions lifecycle to `DESTROYED`. |
| `clone()` | Produces a deep copy with a new Identity but identical Properties/Attributes/State. |
| `observe()` | Produces an `Observation` of current State without mutating it. |
| `snapshot()` | Pushes the current State onto `history` and returns it. |
| `restore()` | Replaces current State with a prior entry from `history` (rollback). |
| `validate()` | Runs all registered `Validator`s against current Properties/Attributes/State; returns `ValidationResult`. |
| `compare()` | Structural/value comparison against another `Entity` (via `Comparable`). |
| `serialize()` | Produces a format-specific representation via a `Serializer`. |
| `deserialize()` | Class method; reconstructs an `Entity` from serialized data. |
| `update_state()` | Applies a new `State` (typically the result of an `Interaction`), validating Constraints first. |
| `interact()` | Participates in an `Interaction`, delegating to `Behaviour` to check eligibility. |
| `add_property()` | Registers a new immutable `Property`. |
| `remove_property()` | Removes a `Property` (only permitted pre-`ACTIVE` lifecycle stage, else raises). |
| `add_attribute()` | Registers a new mutable `Attribute`. |
| `remove_attribute()` | Removes an `Attribute`. |
| `add_relationship()` | Registers participation in a `Relationship`. |
| `remove_relationship()` | Removes a `Relationship` reference. |
| `add_constraint()` | Registers a `Constraint` the Entity's State must satisfy going forward. |
| `emit_event()` | Publishes an `Event` to the `EventBus` on behalf of this Entity. |

## Methods

### `create(identity: Identity | None = None, name: str = "", type_: str = "", metadata: dict[str, Any] | None = None) -> Entity`
- **Signature:** classmethod / factory entry point.
- **Input Parameters:** `identity` (optional, auto-generated if omitted); `name`; `type_`; `metadata`.
- **Return Type:** `Entity` (or subclass, via covariant factory pattern).
- **Preconditions:** If `identity` is supplied, it must not already be registered in the target `System`'s Identity scope.
- **Postconditions:** Returned Entity has lifecycle stage `CREATED`, empty `state`, empty `history`.
- **Exceptions Raised:** `DuplicateIdentityError` if `identity` already exists in scope.
- **Example Usage:** `qubit = Entity.create(name="q0", type_="quantum.Qubit")`

### `initialize(properties: dict[str, Any] | None = None, attributes: dict[str, Any] | None = None) -> None`
- **Input Parameters:** initial property/attribute values.
- **Return Type:** `None`.
- **Preconditions:** lifecycle stage must be `CREATED`.
- **Postconditions:** lifecycle stage becomes `INITIALIZED`; `properties`/`attributes` populated and validated.
- **Exceptions Raised:** `InvalidLifecycleTransitionError`, `ValidationFailedError`.
- **Example Usage:** `qubit.initialize(properties={"dimension": 2})`

### `activate() -> None`
- **Preconditions:** lifecycle stage is `INITIALIZED` or `INACTIVE`.
- **Postconditions:** lifecycle stage becomes `ACTIVE`; emits `EntityActivated`.
- **Exceptions Raised:** `InvalidLifecycleTransitionError`.

### `deactivate() -> None`
- **Preconditions:** lifecycle stage is `ACTIVE`.
- **Postconditions:** lifecycle stage becomes `INACTIVE`; emits `EntityDeactivated`.
- **Exceptions Raised:** `InvalidLifecycleTransitionError`.

### `suspend(reason: str = "") -> None`
- **Postconditions:** lifecycle stage becomes `SUSPENDED`; further `update_state()` calls raise until `resume()`.
- **Exceptions Raised:** `InvalidLifecycleTransitionError`.

### `destroy() -> None`
- **Preconditions:** lifecycle stage is not already `DESTROYED`.
- **Postconditions:** lifecycle stage becomes `DESTROYED` (terminal); emits `EntityDestroyed`; further mutation raises.
- **Exceptions Raised:** `InvalidLifecycleTransitionError`.

### `clone(new_name: str | None = None) -> Entity`
- **Return Type:** new `Entity` instance, new `Identity`, `version = 0`.
- **Postconditions:** returned Entity is deep-equal to the original except Identity/timestamps/version.
- **Exceptions Raised:** `CloneNotSupportedError` if a Property is declared non-cloneable.
- **Example Usage:** `q0_copy = qubit.clone(new_name="q0-copy")`

### `observe(observer: str | None = None) -> Observation`
- **Return Type:** `Observation` referencing this Entity's current `state`.
- **Postconditions:** does not mutate `state`; emits `ObservationRecorded`.
- **Example Usage:** `obs = qubit.observe(observer="measurement-service")`

### `snapshot() -> State`
- **Postconditions:** current `state` appended to `history`; returns the appended `State`.

### `restore(index: int = -1) -> None`
- **Input Parameters:** `index` into `history` (default: most recent prior State).
- **Postconditions:** `state` replaced with `history[index]`; `version` incremented; emits `StateChanged`.
- **Exceptions Raised:** `IndexError` (mapped to `InvalidStateError`) if `index` out of range.

### `validate() -> ValidationResult`
- **Return Type:** `ValidationResult` (see `validators.py`), never raises for *expected* validation failures — callers inspect `.is_valid`.
- **Exceptions Raised:** only for programming errors (e.g. missing Validator implementation).

### `compare(other: Entity) -> ComparisonResult`
- **Return Type:** `ComparisonResult` describing equal/differing fields.
- **Exceptions Raised:** `TypeError` (mapped to `InvalidComparisonError`) if `other` is not comparable (different `type`).

### `serialize(format: SerializationFormat = SerializationFormat.JSON) -> bytes | str`
- **Exceptions Raised:** `UnsupportedFormatError` if no `Serializer` is registered for `format`.

### `deserialize(data: bytes | str, format: SerializationFormat = SerializationFormat.JSON) -> Entity`
- classmethod; inverse of `serialize`.
- **Exceptions Raised:** `DeserializationError` on malformed input.

### `update_state(new_state: State, cause: Interaction | None = None) -> None`
- **Preconditions:** lifecycle stage is `ACTIVE`; `new_state` satisfies all registered `constraints`.
- **Postconditions:** `state` replaced; previous `state` pushed to `history`; `version += 1`; emits `StateChanged`.
- **Exceptions Raised:** `ConstraintViolationError`, `InvalidStateError`, `InvalidLifecycleTransitionError` (if not `ACTIVE`).

### `interact(interaction: Interaction) -> None`
- **Preconditions:** `behaviour` permits participation in `interaction.type`.
- **Postconditions:** delegates to `interaction.apply(self)`; emits `InteractionStarted` then `InteractionCompleted`.
- **Exceptions Raised:** `InteractionError` if `behaviour` forbids participation.

### `add_property(prop: Property) -> None` / `remove_property(name: str) -> None`
- **Exceptions Raised:** `DuplicatePropertyError`; `PropertyNotFoundError`; `ImmutablePropertyError` if removal attempted post-`ACTIVE`.

### `add_attribute(attr: Attribute) -> None` / `remove_attribute(name: str) -> None`
- **Exceptions Raised:** `DuplicateAttributeError`; `AttributeNotFoundError`.

### `add_relationship(rel: Relationship) -> None` / `remove_relationship(rel: Relationship) -> None`
- **Exceptions Raised:** `RelationshipError` if `self` is not a participant of `rel`.

### `add_constraint(constraint: Constraint) -> None`
- **Postconditions:** current `state` is re-validated against the new Constraint immediately; raises if violated.
- **Exceptions Raised:** `ConstraintViolationError`.

### `emit_event(event: Event) -> None`
- **Postconditions:** `event` published to the active `EventBus`.

## Private Helpers (suggested)

- `_generate_id() -> EntityId`
- `_validate_lifecycle_transition(target: LifecycleStage) -> None`
- `_apply_validators(scope: Literal["properties","attributes","state"]) -> ValidationResult`
- `_diff_state(a: State, b: State) -> StateDiff`
- `_trim_history() -> None` (enforces `constants.MAX_HISTORY_LENGTH`)

## Lifecycle

```
CREATED → INITIALIZED → ACTIVE ⇄ INACTIVE
                          ↓
                       SUSPENDED → ACTIVE
                          ↓
                       DESTROYED (terminal)
```

Additional narrative stages requested by the prompt (Validated,
Updated, Observed, Serialized, Archived) are modeled as **events**, not
lifecycle stages, because they are not mutually exclusive states an
Entity occupies — they can happen repeatedly at any point after
`INITIALIZED`. See `Lifecycle` class spec in
`03-supporting-classes.md` for the full state machine and rationale.

## Events

`EntityCreated`, `EntityInitialized`, `EntityActivated`,
`EntityDeactivated`, `EntitySuspended`, `EntityDestroyed`,
`StateChanged`, `ValidationFailed`, `ValidationSucceeded`,
`ObservationRecorded`, `PropertyAdded`, `PropertyRemoved`,
`AttributeAdded`, `AttributeRemoved`, `RelationshipAdded`,
`RelationshipRemoved`, `ConstraintAdded`, `ConstraintViolated`.

## Exceptions

`EntityError` (base) →
`InvalidLifecycleTransitionError`,
`InvalidStateError`,
`ConstraintViolationError`,
`DuplicateIdentityError`,
`DuplicatePropertyError`,
`PropertyNotFoundError`,
`ImmutablePropertyError`,
`DuplicateAttributeError`,
`AttributeNotFoundError`,
`RelationshipError`,
`CloneNotSupportedError`,
`InvalidComparisonError`,
`UnsupportedFormatError`,
`DeserializationError`,
`InteractionError` (raised, defined in `interaction.py`).

## Interfaces Implemented

- **`Identifiable`** — exposes `id`, `uuid`; guarantees `__eq__`/`__hash__` by Identity.
- **`Observable`** — exposes `observe()`; supports Event subscription for its own lifecycle/state events.
- **`Serializable`** — exposes `serialize()`/`deserialize()`.
- **`Cloneable`** — exposes `clone()`.
- **`Validatable`** — exposes `validate()`.
- **`Comparable`** — exposes `compare()` and ordering/equality operators.
- **`Timestamped`** — exposes `created_at`/`updated_at`.

## Validation Rules

- `name` must be non-empty after `initialize()`.
- `type` must match a registered domain type string (soft-warning only
  in `foundation`; hard-enforced by domain packages).
- Every `Property` value must pass its own declared `Validator`.
- Every `Attribute` value must pass its own declared `Validator` on
  every mutation, not only at `initialize()`.
- `state` must satisfy every entry in `constraints` before
  `update_state()` commits.

## Serialization

Supported formats (architecture only, no implementation in R0.2.0):
JSON (default, human-debuggable), YAML (config-friendly), MessagePack
(compact binary), raw Binary (custom framing), Protocol Buffers
(schema-first, cross-language — the natural bridge to the future
C++/Rust/Java/Go/Julia ports). Every format is implemented by a
`Serializer` from `serializers.py`; `Entity` never encodes format logic
itself — it only orchestrates.

## Thread Safety

`Entity` instances are **not** thread-safe by default in R0.2.0; the
SDK targets a single-writer execution model per `runtime.Scheduler`.
`update_state()` must be treated as a critical section by callers that
share an Entity across threads/tasks. Future versions may introduce an
`AtomicEntity` variant or a `runtime`-level lock/actor wrapper — tracked
as a Future Extension, not solved by `foundation` itself (no
concurrency primitives belong in an ontology-layer package).

## Logging

Hooks (interface points, not implementations): `on_lifecycle_transition`,
`on_state_change`, `on_validation_failure`, `on_constraint_violation` —
each receives structured context (`entity.id`, `entity.type`, old/new
value) and is expected to be wired to `quantsmind.logging` by the
runtime, not called directly by `Entity` internals via a concrete
logger dependency (keeps `foundation` decoupled from `logging`'s
implementation).

## Metrics

Telemetry points (published as `quantsmind.telemetry` counters/
histograms once wired, architecture only here): `entity_created_total`,
`entity_destroyed_total`, `entity_state_changes_total`,
`entity_validation_failures_total`, `entity_history_length` (gauge),
`entity_lifecycle_transition_duration` (histogram).

## Tests

See `10-testing-strategy.md` §Entity for the full scenario catalog
(positive, negative, boundary, validation, serialization, performance).

## Documentation

See `11-documentation-structure.md` for the per-class doc template this
class must ship with at implementation time (Overview, Responsibilities,
API Reference, Examples, Developer Notes, Extension Guidelines).
