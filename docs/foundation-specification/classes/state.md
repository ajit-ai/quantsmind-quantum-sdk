# Class Specification: `State`

## General

- **Class Name:** `State`
- **Description:** The complete, observable, timestamped condition of
  an `Entity` or `System` at a point in `Time` — a snapshot of
  `Attribute` values plus provenance metadata.
- **Design Rationale:** `State` is an immutable value object, not a
  mutable object referenced in place. Every "change" produces a *new*
  `State` instance; `Entity.update_state()` swaps the reference and
  archives the old one. This makes diffing, history, rollback, and
  thread-safety reasoning tractable.
- **Scientific Meaning:** Generalizes the notion of a system's
  instantaneous configuration — the snapshot from which measurable
  quantities are, in principle, derivable.
- **SDK Purpose:** A single, consistent, versioned, timestamped
  container type used identically by every domain (a qubit's
  amplitude vector, a portfolio's holdings, a molecule's
  conformation).

## Relationships

- **Parent Class:** None.
- **Child Classes:** Domain-specific specializations may subclass to
  add typed accessors (e.g. `quantum.QuantumState(State)`), but must
  not break immutability.
- **Interfaces Implemented:** `Serializable`, `Comparable`,
  `Timestamped`. (*Not* `Identifiable` — a `State` has no independent
  identity apart from the Entity/System it belongs to; *not*
  `Cloneable` in the mutation sense, since it's already immutable —
  "cloning" a `State` is just handing out the same immutable value.)
- **Collaborating Classes:** `Attribute` (payload), `Time` (timestamp),
  `Entity`/`System` (owner), `Interaction` (producer of new `State`),
  `Observation` (consumer/reader), `Constraint` (validator).

## Attributes

| Attribute | Type | Explanation |
|---|---|---|
| `id` | `StateId` | Unique id for this specific snapshot (not the owning Entity's id). |
| `owner_id` | `EntityId` | Id of the Entity/System this State belongs to. |
| `values` | `dict[str, AttributeValue]` (immutable mapping) | Attribute name → current value, frozen at construction. |
| `timestamp` | `Time` | Instant this State became current. |
| `version` | `int` | Matches the owning Entity's `version` at capture time. |
| `space` | `Space \| None` | Optional coordinate context the values are expressed in. |
| `cause` | `InteractionId \| None` | Reference to the `Interaction` that produced this State, if any (`None` for initial State). |
| `metadata` | `dict[str, Any]` | Free-form provenance (e.g. simulation step, solver iteration). |

## Properties

- `is_initial` — read-only, `cause is None`.
- `attribute_names` — read-only, `frozenset(values.keys())`.

## Behaviors

| Behavior | Purpose |
|---|---|
| `create()` | Factory-invoked construction from an Attribute mapping; freezes `values`. |
| `diff()` | Computes a `StateDiff` against another `State` of the same owner. |
| `merge()` | Produces a new `State` combining values from two compatible States (non-overlapping keys only; conflicts raise). |
| `validate()` | Checks `values` against a supplied list of `Constraint`s (Constraint objects live on the owner, not on `State` itself — `State.validate()` accepts them as a parameter). |
| `compare()` | Value-level equality/ordering against another `State`. |
| `serialize()` / `deserialize()` | Standard format conversion. |
| `to_attributes()` | Reconstructs live `Attribute` objects from `values` (for handing back to an `Entity`). |

## Methods

### `create(owner_id: EntityId, values: dict[str, AttributeValue], *, cause: InteractionId | None = None, space: Space | None = None) -> State`
- **Return Type:** new immutable `State`.
- **Postconditions:** `timestamp = Time.now()`; `values` frozen (implementation detail: `MappingProxyType` or equivalent immutable mapping in the target language).
- **Exceptions Raised:** `InvalidStateError` if `values` contains a key with a type mismatch against a previously-registered `Attribute` schema (schema check is optional and delegated to the caller/`Entity`, not enforced unconditionally here).

### `diff(other: State) -> StateDiff`
- **Preconditions:** `self.owner_id == other.owner_id`.
- **Return Type:** `StateDiff` — object listing added/removed/changed keys with old/new values.
- **Exceptions Raised:** `IncompatibleStateError` if owners differ.

### `merge(other: State) -> State`
- **Preconditions:** `self.owner_id == other.owner_id`; `set(self.values) & set(other.values) == set()` (no overlapping keys) unless `overwrite=True` is passed.
- **Return Type:** new `State` with unioned `values`.
- **Exceptions Raised:** `StateMergeConflictError` on overlapping keys without `overwrite=True`.

### `validate(constraints: list[Constraint]) -> ValidationResult`
- Evaluates every `Constraint` against `self.values`; never raises for expected violations, returns them in the result.

### `compare(other: State) -> ComparisonResult`
- **Exceptions Raised:** `IncompatibleStateError` if owners differ and strict mode is requested.

### `serialize(format: SerializationFormat = SerializationFormat.JSON) -> bytes | str`
- Straightforward value-object serialization; no reference-resolution complexity (unlike `System`).

### `to_attributes() -> dict[str, Attribute]`
- Reconstructs full `Attribute` objects (with type/validator metadata looked up from the owner's attribute schema, passed in by caller) from the raw `values` mapping.

## Private Helpers (suggested)

- `_freeze(values: dict) -> Mapping` — enforce immutability at construction.
- `_compute_hash() -> int` — content-addressable hash for dedup/caching of identical States.

## Lifecycle

`State` does not have its own `Lifecycle` state machine (it is a value
object, not a stateful Entity). Its "lifecycle" is simply:
`created → (referenced as current | archived in history) → garbage-collected`.
This is intentional: modeling State-of-States would violate the "don't
duplicate concepts" quality bar from the founding architecture.

## Events

`StateCreated`, `StateMerged`, `StateDiffComputed` (optional, may be
too high-frequency to publish by default — see Metrics note),
`ValidationFailed`, `ValidationSucceeded`.

`StateChanged` is emitted by the **owner** (`Entity`/`System`), not by
`State` itself, since "changed" is a statement about the owner's
current-State pointer, not about this immutable value.

## Exceptions

`StateError` (base) →
`InvalidStateError`, `IncompatibleStateError`,
`StateMergeConflictError`, `UnsupportedFormatError`,
`DeserializationError`.

## Interfaces Implemented

`Serializable`, `Comparable`, `Timestamped`.

## Validation Rules

- `values` keys must be valid identifiers (same rule as `Attribute`
  names).
- `diff()`/`merge()`/`compare()` all require matching `owner_id` unless
  an explicit `strict=False` override is passed (useful for
  cross-Entity analytics, used sparingly).

## Serialization

Same format list as `Entity`/`System`. `State` is the simplest
serialization target in `foundation` (flat value object, no internal
object-graph references besides the optional `cause` id) and is
recommended as the first concrete `Serializer` implementation target
when R0.2.0 moves from spec to code.

## Thread Safety

`State` **is** thread-safe by construction: it is immutable after
creation. This is the primary mechanism by which the rest of the
ontology achieves any concurrency safety at all — readers can hold a
reference to a `State` indefinitely without locking, because it will
never change underneath them.

## Logging

Hooks: `on_state_created`, `on_merge_conflict`.

## Metrics

`state_created_total`, `state_diff_computed_total`,
`state_merge_conflicts_total`, `state_serialize_duration`
(histogram). `StateDiffComputed` events are opt-in (see Events) because
`diff()` may be called at high frequency during simulation loops.

## Tests

See `10-testing-strategy.md` §State.

## Documentation

See `11-documentation-structure.md`.
