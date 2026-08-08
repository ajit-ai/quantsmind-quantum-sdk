# Class Specification: `Interaction`

## General

- **Class Name:** `Interaction`
- **Description:** An event through which one or more `Entity` objects
  exchange influence, producing a `State` transition for each
  participant (and, if run within a `System`, an aggregate System
  `State` transition).
- **Design Rationale:** `Interaction` is deliberately generic (a
  chemical reaction, a quantum gate application, a financial trade, a
  gravitational encounter are all `Interaction`s) and carries a
  `Transformation` describing *what* happens, keeping the *how* out of
  `foundation` entirely — no scientific logic here, only orchestration
  and bookkeeping.
- **Scientific Meaning:** The generalized notion of a process, force,
  or event that causes change — the mechanism, as opposed to `State`
  (the before/after snapshots) or `Behaviour` (the *rules* about which
  Interactions are permitted).
- **SDK Purpose:** Gives every domain a consistent, observable,
  serializable, replayable record of "what happened", independent of
  the specific physics/finance/AI logic that computed the new `State`.

## Relationships

- **Parent Class:** None.
- **Child Classes:** Domain-specific specializations, e.g.
  `quantum.GateApplication(Interaction)`,
  `chemistry.Reaction(Interaction)`, `finance.Trade(Interaction)`.
- **Interfaces Implemented:** `Identifiable`, `Observable`,
  `Serializable`, `Comparable`, `Timestamped`. (*Not* `Cloneable` —
  Interactions are historical facts; cloning one to "replay" it is
  represented instead by constructing a new `Interaction` referencing
  the same `Transformation`, to keep provenance honest. *Not*
  `Validatable` directly — validity is checked via the participants'
  `Behaviour`/`Constraint`s, not on `Interaction` itself.)
- **Collaborating Classes:** `Entity` (participants), `System`
  (orchestrator, optional), `Transformation` (the applied mapping),
  `State` (before/after), `Time` (timestamp), `Event` (lifecycle
  notifications).

## Attributes

| Attribute | Type | Explanation |
|---|---|---|
| `id` | `InteractionId` | Unique identifier for this Interaction instance. |
| `type` | `str` | Domain-qualified Interaction kind (e.g. `"quantum.gate_application"`). |
| `participants` | `list[EntityId]` | Ordered references to participating Entities (order matters for asymmetric Interactions, e.g. control/target qubits). |
| `transformation` | `Transformation` | The mapping applied to produce new State(s). |
| `initiated_at` | `Time` | Instant the Interaction was requested. |
| `completed_at` | `Time \| None` | Instant the Interaction finished (`None` while in progress). |
| `status` | `InteractionStatus` (enum) | `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`. |
| `results` | `dict[EntityId, State]` | New State produced per participant, populated on completion. |
| `metadata` | `dict[str, Any]` | Free-form provenance (solver used, random seed, provider backend id). |
| `parent_interaction_id` | `InteractionId \| None` | Optional link for composed/pipeline Interactions. |

## Properties

- `is_completed` — read-only, `status == InteractionStatus.COMPLETED`.
- `duration` — read-only, `completed_at - initiated_at` if both set, else `None`.
- `participant_count` — read-only, `len(participants)`.

## Behaviors

| Behavior | Purpose |
|---|---|
| `create()` | Factory-invoked construction in `PENDING` status. |
| `apply()` | Invokes `transformation` against each participant's current `State`, producing `results`; the *only* place `foundation` touches anything resembling "computation", and even here it only orchestrates — the actual numeric/scientific work lives inside the `Transformation` implementation supplied by a domain package. |
| `commit()` | Pushes `results` into each participant's `state` via `Entity.update_state()`; transitions `status` to `COMPLETED`. |
| `cancel()` | Aborts a `PENDING`/`RUNNING` Interaction without committing; transitions to `CANCELLED`. |
| `fail()` | Marks the Interaction `FAILED` with an attached error/reason; does not commit partial `results`. |
| `observe()` | Produces an `Observation` of this Interaction's record (not of a participant's State). |
| `serialize()` / `deserialize()` | Standard format conversion. |
| `compare()` | Structural comparison against another Interaction (same `type`, same `participants`, same `transformation`). |
| `emit_event()` | Publishes Interaction lifecycle Events. |

## Methods

### `create(type_: str, participants: list[Entity], transformation: Transformation, *, metadata: dict[str, Any] | None = None) -> Interaction`
- **Preconditions:** `len(participants) >= 1`; every participant's `Behaviour` permits `type_`.
- **Postconditions:** `status = PENDING`; `results = {}`.
- **Exceptions Raised:** `InteractionError` if any participant's `Behaviour` forbids `type_`.

### `apply() -> dict[EntityId, State]`
- **Preconditions:** `status == PENDING`.
- **Postconditions:** `status = RUNNING` then, on success, `results` populated (but *not yet committed* to participants); does not mutate any participant's `state` directly — this is a pure compute step.
- **Exceptions Raised:** `TransformationError` (propagated from `transformation.apply(...)`), which triggers an internal `fail()`.
- **Example Usage:** `results = interaction.apply()`

### `commit() -> None`
- **Preconditions:** `status == RUNNING` and `results` is populated (i.e. `apply()` already succeeded).
- **Postconditions:** each participant's `update_state()` is called with its corresponding `results[entity.id]`; `status = COMPLETED`; `completed_at = Time.now()`; emits `InteractionCompleted`.
- **Exceptions Raised:** `ConstraintViolationError` (propagated from a participant's `update_state()` — if this happens, the Interaction transitions to `FAILED` and **no** participant is left partially updated; see Thread Safety / atomicity note).

### `cancel(reason: str = "") -> None`
- **Preconditions:** `status in (PENDING, RUNNING)`.
- **Postconditions:** `status = CANCELLED`; emits `InteractionCancelled`.
- **Exceptions Raised:** `InvalidInteractionStateError` if already `COMPLETED`/`FAILED`/`CANCELLED`.

### `fail(reason: str) -> None`
- **Postconditions:** `status = FAILED`; `metadata["failure_reason"] = reason`; emits `InteractionFailed`.

### `observe() -> Observation`
- Produces a read-only `Observation` of `{type, participants, status, results, duration}`.

### `compare(other: Interaction) -> ComparisonResult`
- Compares `type`, `participants`, and `transformation` identity/equality; does not compare `results` (those are outcomes, not identity).

## Private Helpers (suggested)

- `_check_participant_eligibility() -> None`
- `_apply_transformation_to(entity: Entity) -> State`
- `_rollback_partial_commit(committed: list[Entity]) -> None` — used if a mid-commit `ConstraintViolationError` occurs, to keep commit atomic across participants.

## Lifecycle

```
PENDING → RUNNING → COMPLETED (terminal)
            ↓
          FAILED (terminal)
PENDING/RUNNING → CANCELLED (terminal)
```

This is a dedicated `InteractionStatus` state machine, distinct from
the `Lifecycle` class used by `Entity`/`System` — an `Interaction` is a
single historical event, not a long-lived stateful object, so it does
not need `Lifecycle`'s `ACTIVE ⇄ INACTIVE` reactivation semantics.

## Events

`InteractionCreated`, `InteractionStarted` (on `apply()`),
`InteractionCompleted` (on successful `commit()`), `InteractionFailed`,
`InteractionCancelled`, `ObservationRecorded`.

## Exceptions

`InteractionError` (base) →
`TransformationError` (propagated), `ConstraintViolationError`
(propagated from participants), `InvalidInteractionStateError`
(illegal method call for current `status`), `UnsupportedFormatError`,
`DeserializationError`.

## Interfaces Implemented

`Identifiable`, `Observable`, `Serializable`, `Comparable`,
`Timestamped`.

## Validation Rules

- Every participant must already be a member of the same `System` if
  one is supplied (checked by `System.run_interaction()`, not by
  `Interaction` itself, to keep `Interaction` System-agnostic and
  usable standalone between two free-floating Entities).
- `commit()` is all-or-nothing: if any participant's `update_state()`
  raises `ConstraintViolationError`, previously-committed participants
  in the same `commit()` call are rolled back via `_rollback_partial_commit`
  and the whole Interaction transitions to `FAILED`.

## Serialization

Same format list as other foundation classes. `results` serializes as
a map of `EntityId → State`, reusing `State`'s own serializer;
`transformation` serializes via `Transformation`'s serializer (which,
per `transformation.py`'s spec, only needs to serialize its
type/parameters — not arbitrary executable code).

## Thread Safety

`apply()` is intended to be safely computable off the critical path
(pure function of participant States + `transformation`), but `commit()`
touches multiple Entities' `state` and must be treated as a single
critical section, coordinated by `runtime.Scheduler` — the same
single-writer caveat as `Entity`/`System`. The all-or-nothing commit
rule above is the concurrency-relevant guarantee `foundation` *does*
make; true multi-entity atomicity under concurrent access is a
`runtime` concern.

## Logging

Hooks: `on_interaction_started`, `on_interaction_committed`,
`on_interaction_failed`, `on_partial_commit_rollback`.

## Metrics

`interaction_started_total`, `interaction_completed_total`,
`interaction_failed_total`, `interaction_cancelled_total`,
`interaction_duration` (histogram, by `type`),
`interaction_participants_count` (histogram).

## Tests

See `10-testing-strategy.md` §Interaction.

## Documentation

See `11-documentation-structure.md`.
