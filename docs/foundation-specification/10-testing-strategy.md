# Testing Strategy

Test plans are scenario catalogs, not code, per the "do not implement"
constraint. Each class gets Positive / Negative / Boundary / Validation
/ Serialization / Performance scenarios. These map directly onto
`tests/unit/foundation/` (see `tests/README.md` at the repo root).

## General policy

- **Positive tests** confirm documented Preconditions → Postconditions
  hold for valid input.
- **Negative tests** confirm every documented Exception is raised under
  the condition that names it.
- **Boundary tests** probe limits from `constants.py` (e.g.
  `MAX_HISTORY_LENGTH`) and empty/singleton/maximal collection sizes.
- **Validation tests** exercise every layer in
  `08-validation-and-serialization-strategy.md` independently.
- **Serialization tests** round-trip every class through every
  `SerializationFormat`, and specifically test envelope
  version-mismatch handling.
- **Performance considerations** are documented as budgets/expectations
  here, enforced later by `tests/performance/foundation/`, not
  implemented in this specification.

## `Entity`

- **Positive:** `create()` yields `CREATED` stage with empty state;
  full lifecycle walk `CREATED → INITIALIZED → ACTIVE → INACTIVE →
  ACTIVE → SUSPENDED → ACTIVE → DESTROYED` succeeds; `update_state()`
  appends to `history` and increments `version`; `clone()` produces a
  distinct `id` with equal Properties/Attributes; `observe()` does not
  mutate `state`.
- **Negative:** `activate()` before `initialize()` raises
  `InvalidLifecycleTransitionError`; `update_state()` while `SUSPENDED`
  raises; `update_state()` violating a `HARD` `Constraint` raises
  `ConstraintViolationError` and leaves `state` unchanged;
  `add_property()` with a duplicate name raises
  `DuplicatePropertyError`; `remove_property()` after `ACTIVE` raises
  `ImmutablePropertyError`; `compare()` against a different `type`
  raises `InvalidComparisonError`.
- **Boundary:** `history` at exactly `MAX_HISTORY_LENGTH` evicts the
  oldest entry on the next `snapshot()`; `restore()` with `index`
  beyond `history` bounds raises; Entity with zero Properties/
  Attributes still validates and serializes successfully; `name` at
  maximum grammar length from `ID_PATTERN` accepted, one character over
  rejected.
- **Validation:** every registered `Validator` on a `Property`/
  `Attribute` is invoked exactly once per `initialize()`/`set_value()`
  call; `SOFT` Constraint violation does not raise but appears in
  `validate()`'s `ValidationResult` and emits `ConstraintViolated`.
- **Serialization:** round-trip through JSON, YAML, MessagePack,
  Binary, Protobuf preserves `id`, `properties`, `attributes`,
  `state`, `version`; deserializing an envelope with a newer
  `sdk_version` than the running SDK surfaces a version-mismatch
  warning, not a hard failure, for additive-only formats.
- **Performance:** `update_state()` on an Entity with a `history` at
  `MAX_HISTORY_LENGTH` must not incur O(n) cost proportional to full
  history on every call (amortized O(1) eviction expected); `clone()`
  cost should scale linearly with Property/Attribute count, not
  history length (history is not cloned).

## `System`

- **Positive:** `add_entity()`/`remove_entity(cascade=True)` keep
  `relationships` consistent; `run_interaction()` across two members
  updates both and the aggregate System `state`; `find_entity()` by
  tag returns all matches; `clone()` preserves internal topology with
  fresh Identities for both the System and every member.
- **Negative:** `add_relationship()` referencing a non-member Entity
  raises `EntityNotFoundError`; `remove_entity(cascade=False)` with
  dangling Relationships raises `RelationshipError`;
  `run_interaction()` with a participant not in `entities` raises
  `EntityNotFoundError`; `run_interaction()` where one participant's
  `Behaviour` forbids the type raises `InteractionError` before any
  State mutation occurs (fail-fast, verified via unchanged `version`
  on all participants).
- **Boundary:** System with zero members validates and serializes
  successfully (empty aggregate `state`); System-of-Systems nesting at
  exactly `MAX_SYSTEM_NESTING_DEPTH` succeeds, one level deeper raises.
- **Validation:** `System.validate()` aggregates System-level
  Constraint results *and* every member's own `validate()` result into
  one `ValidationResult`.
- **Serialization:** serialized System document contains each member
  Entity exactly once even when referenced by multiple Relationships
  (no duplication); deserializing reconstructs the same topology
  (Relationship participant ids resolve to the same reconstructed
  Entity instances).
- **Performance:** `find_entity()` by `id` should be O(1) (dict
  lookup); by `type`/`tag` predicate is allowed O(n) but must be
  documented as such so callers avoid it in hot loops.

## `State`

- **Positive:** `create()` freezes `values`; `diff()` between two
  States of the same owner correctly lists added/removed/changed keys;
  `merge()` with disjoint keys unions successfully.
- **Negative:** `diff()`/`merge()`/strict `compare()` across different
  `owner_id` raise `IncompatibleStateError`; `merge()` with overlapping
  keys and no `overwrite=True` raises `StateMergeConflictError`;
  attempting to mutate `values` directly raises (immutability
  enforcement, mapped to a language-appropriate "frozen" error).
- **Boundary:** `State` with zero `values` entries is valid; `merge()`
  of two States each with the maximum representable key count still
  succeeds (or documents an explicit cap, TBD at implementation).
- **Validation:** `validate(constraints)` against an empty
  `constraints` list always returns `is_valid=True`, `errors=[]`.
- **Serialization:** round-trip preserves `values` types exactly
  (numeric vs. string vs. bool distinctions survive JSON round-trip,
  the one format most prone to type coercion bugs — explicit test
  required).
- **Performance:** `diff()` cost should be O(k) in the number of
  distinct keys across both States, not O(n) in unrelated history.

## `Interaction`

- **Positive:** `apply()` then `commit()` on a valid Interaction
  updates every participant and transitions `status` to `COMPLETED`;
  `cancel()` from `PENDING` transitions to `CANCELLED` without touching
  any participant `state`.
- **Negative:** `commit()` before `apply()` raises
  `InvalidInteractionStateError`; a `commit()` where the second of two
  participants' `update_state()` raises `ConstraintViolationError`
  results in the first participant's State being rolled back
  (`_rollback_partial_commit`) and overall `status = FAILED` — this
  atomicity guarantee is a mandatory negative-test case, not optional;
  `create()` with a participant whose `Behaviour` forbids `type_`
  raises `InteractionError` at construction, before `apply()` is ever
  called.
- **Boundary:** `Interaction` with exactly one participant (minimum
  valid count) succeeds; with the maximum practically-tested
  participant count (e.g. 100) still completes commit atomicity
  correctly.
- **Validation:** `Transformation.input_schema` mismatch (when
  declared) raises `SchemaMismatchError` from `apply()`, without
  changing `status` away from `PENDING`/`RUNNING` inconsistently
  (transitions to `FAILED` cleanly).
- **Serialization:** `results` serializes as an `EntityId → State` map
  correctly; a `PENDING` Interaction (empty `results`) serializes and
  deserializes to an equivalent `PENDING` Interaction.
- **Performance:** `apply()` (pure compute) should be safely
  parallelizable across independent Interactions in a benchmark
  scenario with disjoint participant sets — documented expectation
  for `runtime` to validate once implemented, not testable in
  `foundation` alone.

## Supporting classes (`Identity`, `Property`, `Attribute`, `Behaviour`,
`Relationship`, `Constraint`, `Lifecycle`, `Event`, `Observation`,
`Knowledge`, `Transformation`, `Space`, `Time`)

Each follows the same six-category pattern at a scope proportional to
its size; representative highlights not already covered under
`Entity`/`System`/`State`/`Interaction` above:

- **`Identity`:** Negative — `matches()` against a mismatched `scope`
  returns `False`, never raises. Boundary — `id` at the exact
  `ID_PATTERN` length limit.
- **`Property`/`Attribute`:** Validation — every `Validator` type
  (`TypeValidator`, `RangeValidator`, `RegexValidator`,
  `RequiredValidator`, `PredicateValidator`, `ValidatorChain` in both
  `FAIL_FAST` and `COLLECT_ALL` modes) gets its own scenario.
- **`Behaviour`:** Negative — `permits()` for an unregistered
  Interaction type returns `False` (never raises; only
  `check_preconditions()` participates in a raising path via its
  caller).
- **`Relationship`:** Boundary — `cardinality=ONE_TO_ONE` with three
  participants raises `InvalidCardinalityError` at construction.
- **`Constraint`:** Positive — `HARD` and `SOFT` severity both
  evaluate correctly; Negative — malformed `expression` (referencing a
  nonexistent operator) raises `InvalidConstraintExpressionError` at
  construction, not at `evaluate()` time (fail-fast).
- **`Lifecycle`:** Negative — every disallowed transition pair in the
  canonical table is exhaustively tested (`DESTROYED → *` always
  raises); Positive — `can_transition_to()` never raises, matches
  `transition_to()`'s accept/reject decision exactly (contract-
  consistency test).
- **`Event`/`EventBus`:** Boundary — publishing past
  `EVENT_BUS_DEFAULT_QUEUE_DEPTH` raises `EventBusUnavailableError`
  rather than blocking; Positive — `subscribe_all()` receives every
  published `EventType`.
- **`Observation`:** Validation — `uncertainty < 0` raises at
  construction.
- **`Knowledge`:** Negative — empty `contributing_observations` without
  `metadata["a_priori"] = True` raises `InsufficientEvidenceError`;
  default `predict()` raises `PredictionNotSupportedError`.
- **`Transformation`:** Negative — `inverse()` on a non-reversible
  Transformation raises `TransformationNotReversibleError`.
- **`Space`:** Boundary — `contains()` at exactly a declared bound
  (inclusive) vs. one unit beyond (exclusive).
- **`Time`:** Negative — `compare()`/`delta()` across mismatched
  `mode` raise `IncompatibleTimeModeError`; Boundary —
  `DISCRETE_STEP` with a negative `value` raises at construction.

## Cross-cutting test suites (not per-class)

- **Event catalog completeness test:** every `EventType` enumerated in
  `07-events.md` is actually published by at least one integration
  test path (prevents silently-dead event definitions).
- **Exception hierarchy completeness test:** every leaf exception in
  `06-exceptions-and-utilities.md` is raised by at least one negative
  test somewhere in the suite (same rationale).
- **Interface conformance test:** every class claiming to implement a
  nominal interface from `04-interfaces-protocols.md` is checked via
  `isinstance()` against both the ABC and its structural Protocol
  mirror.
- **Round-trip determinism test:** serialize → deserialize → serialize
  again must be byte-identical (or structurally identical for
  non-deterministic formats like unordered JSON keys) for every class,
  across every format.
