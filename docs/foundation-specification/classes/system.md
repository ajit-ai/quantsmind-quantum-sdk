# Class Specification: `System`

## General

- **Class Name:** `System`
- **Description:** A bounded composition of `Entity` objects and the
  `Relationship`s / `Interaction`s among them — the "unit of study" a
  domain package operates on (a quantum circuit's register, a
  molecule, a portfolio, a solar system).
- **Design Rationale:** `System` is a container/orchestrator, not a
  superclass of `Entity` — composition again. A `System` *may itself
  be registered as an `Entity`* in a parent `System` (see Future
  Extensions: System-of-Systems), which is why `System` also
  implements `Identifiable`/`Observable`/`Serializable`.
- **Scientific Meaning:** The boundary drawn around interacting
  components for the purpose of analysis — what conserves quantities,
  what has emergent aggregate State.
- **SDK Purpose:** Gives every domain package a consistent container
  type with membership management, topology, aggregate State, and
  Interaction orchestration, instead of each domain inventing its own
  "circuit"/"molecule"/"portfolio" container from scratch.

## Relationships

- **Parent Class:** None.
- **Child Classes:** Domain-specific specializations, e.g.
  `quantum.Circuit`, `chemistry.Molecule`, `finance.Portfolio`.
- **Interfaces Implemented:** `Identifiable`, `Observable`,
  `Serializable`, `Cloneable`, `Validatable`, `Comparable`,
  `Timestamped`.
- **Collaborating Classes:** `Entity` (membership), `Relationship`
  (topology), `Interaction` (orchestration), `State` (aggregate
  snapshot), `Constraint` (system-level rules), `Lifecycle`, `Event`.

## Attributes

| Attribute | Type | Explanation |
|---|---|---|
| `id`, `uuid`, `name`, `label`, `type`, `metadata`, `tags`, `version`, `created_at`, `updated_at` | *(same as `Entity`)* | Identity/bookkeeping fields, identical rationale. |
| `entities` | `dict[EntityId, Entity]` | Membership registry keyed by Entity id. |
| `relationships` | `list[Relationship]` | Topology: connections among member Entities. |
| `state` | `State` | Aggregate System-level State (may be derived from member States or independently tracked). |
| `history` | `list[State]` | Aggregate State history. |
| `constraints` | `list[Constraint]` | System-wide invariants (e.g. conservation laws) evaluated across member States. |
| `lifecycle` | `Lifecycle` | System-level lifecycle, independent of member Entity lifecycles. |
| `boundary` | `Space \| None` | Optional explicit `Space` defining what "inside the System" means geometrically. |
| `parent_system` | `System \| None` | Optional reference for System-of-Systems composition. |

## Properties

- `entity_count` — read-only, `len(entities)`.
- `relationship_count` — read-only, `len(relationships)`.
- `is_composite` — read-only, `True` if any member `Entity` is itself a `System`.
- `is_active` — read-only, derived from `lifecycle.stage`.

## Behaviors

| Behavior | Purpose |
|---|---|
| `create()` | Factory-invoked construction with empty membership. |
| `initialize()` | Populate initial membership/topology; validate; transition to `INITIALIZED`. |
| `activate()` / `deactivate()` / `suspend()` / `destroy()` | Same semantics as `Entity`, applied at System scope. |
| `clone()` | Deep-copies the System *and* all member Entities with fresh Identities, preserving internal topology. |
| `observe()` | Produces a System-level `Observation` (may aggregate member Observations). |
| `snapshot()` / `restore()` | System-level State history operations. |
| `validate()` | Validates System-level Constraints *and* delegates to each member Entity's `validate()`. |
| `compare()` | Structural comparison (membership + topology + state). |
| `serialize()` / `deserialize()` | Serializes the System *and* its member Entities/Relationships as one document graph. |
| `add_entity()` / `remove_entity()` | Membership management. |
| `add_relationship()` / `remove_relationship()` | Topology management. |
| `add_constraint()` | System-level Constraint registration. |
| `run_interaction()` | Orchestrates an `Interaction` across two or more member Entities. |
| `find_entity()` | Query membership by id, type, or tag predicate. |
| `emit_event()` | Publishes a System-scoped Event. |

## Methods

### `create(name: str = "", type_: str = "") -> System`
- **Postconditions:** empty `entities`, empty `relationships`, lifecycle `CREATED`.

### `add_entity(entity: Entity) -> None`
- **Preconditions:** `entity.id` not already present in `entities`.
- **Postconditions:** `entity` registered; emits `EntityAddedToSystem`.
- **Exceptions Raised:** `DuplicateIdentityError`.

### `remove_entity(entity_id: EntityId, *, cascade: bool = True) -> None`
- **Input Parameters:** `cascade` — if `True`, also removes any `Relationship` referencing the Entity.
- **Exceptions Raised:** `EntityNotFoundError`; `RelationshipError` if `cascade=False` and dangling Relationships would result.

### `add_relationship(relationship: Relationship) -> None`
- **Preconditions:** all participant Entities of `relationship` are already members of `entities`.
- **Exceptions Raised:** `EntityNotFoundError` (participant missing), `DuplicateRelationshipError`.

### `run_interaction(interaction: Interaction) -> None`
- **Preconditions:** all `interaction.participants` are members; each participant's `Behaviour` permits it.
- **Postconditions:** delegates State transitions to each participant via `Entity.interact()`; aggregates resulting System `state`; emits `InteractionStarted`/`InteractionCompleted` at System scope.
- **Exceptions Raised:** `EntityNotFoundError`, `InteractionError`, `ConstraintViolationError` (if resulting aggregate State violates a System Constraint).

### `find_entity(*, id: EntityId | None = None, type: str | None = None, tag: str | None = None) -> list[Entity]`
- **Return Type:** list of matching members (empty if none).
- Pure query method — no exceptions for "not found"; empty list instead.

### `validate() -> ValidationResult`
- Aggregates System-level Constraint checks with the `ValidationResult` of every member Entity's own `validate()`.

### `serialize(format: SerializationFormat = SerializationFormat.JSON) -> bytes | str`
- Produces a single document containing member Entities, Relationships, and System-level State/metadata as one connected graph (avoids dangling references on deserialize).

## Private Helpers (suggested)

- `_check_participant_membership(interaction: Interaction) -> None`
- `_aggregate_member_state() -> State`
- `_cascade_remove_relationships(entity_id: EntityId) -> None`
- `_detect_orphaned_relationships() -> list[Relationship]`

## Lifecycle

Same shape as `Entity`'s (`CREATED → INITIALIZED → ACTIVE ⇄ INACTIVE →
SUSPENDED → ACTIVE`, `→ DESTROYED` terminal), evaluated independently
of member Entity lifecycles — a `System` can be `ACTIVE` while
individual members are `INACTIVE`, and vice versa is disallowed for
`run_interaction()` (see Preconditions above).

## Events

`SystemCreated`, `SystemInitialized`, `SystemActivated`,
`SystemDeactivated`, `SystemDestroyed`, `EntityAddedToSystem`,
`EntityRemovedFromSystem`, `RelationshipAdded`, `RelationshipRemoved`,
`InteractionStarted`, `InteractionCompleted`, `StateChanged`,
`ConstraintViolated`, `ValidationFailed`.

## Exceptions

`SystemError` (base) →
`DuplicateIdentityError`, `EntityNotFoundError`,
`DuplicateRelationshipError`, `RelationshipError`,
`ConstraintViolationError`, `InteractionError`,
`InvalidLifecycleTransitionError`, `UnsupportedFormatError`,
`DeserializationError`.

## Interfaces Implemented

`Identifiable`, `Observable`, `Serializable`, `Cloneable`,
`Validatable`, `Comparable`, `Timestamped` — identical contract shapes
to `Entity` (see `04-interfaces-protocols.md`); `System` satisfies them
at System scope rather than single-Entity scope.

## Validation Rules

- No two members may share an `id`.
- Every `Relationship` in `relationships` must reference only current
  members.
- System-level `Constraint`s are evaluated against the *aggregate*
  `state`, not any single member's State.
- `run_interaction()` refuses to start if any participant fails its own
  `validate()` first (fail-fast).

## Serialization

Same format list as `Entity`. The System serializer must handle
reference resolution (Entities referenced by `Relationship`s must
serialize once and be referenced by id elsewhere in the document, not
duplicated) — an explicit requirement on any concrete `Serializer`
implementation for `System`.

## Thread Safety

Same single-writer assumption as `Entity`. `run_interaction()` is the
primary critical section: it mutates multiple member Entities'
`state`, so callers must not run two `run_interaction()` calls
concurrently on overlapping membership. Left to `runtime` scheduling
policy, not solved inside `foundation`.

## Logging

Hooks: `on_membership_change`, `on_topology_change`,
`on_interaction_orchestrated`, `on_constraint_violation` — same
decoupled-from-`logging` design as `Entity`.

## Metrics

`system_entity_count` (gauge), `system_relationship_count` (gauge),
`system_interactions_total`, `system_constraint_violations_total`,
`system_interaction_duration` (histogram).

## Tests

See `10-testing-strategy.md` §System.

## Documentation

See `11-documentation-structure.md`.
