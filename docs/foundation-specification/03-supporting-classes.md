# Supporting Class Specifications

Full specifications for the 13 supporting classes that `Entity`,
`System`, `State`, and `Interaction` compose. Each follows the same
template as the four core classes (`classes/*.md`) at a scope
appropriate to a smaller, more focused class.

---

## `Identity`

**General.** Description: the stable identifier for an `Entity`/`System`
across its lifetime, independent of mutable State. Design rationale:
separated from `Entity` so identity-comparison and identity-generation
policy can evolve (e.g. swap UUID4 for a content hash) without touching
`Entity`. Scientific meaning: "is this the same thing I measured
before?" SDK purpose: single source of truth for equality/hashing
across the whole ontology.

**Relationships.** Parent: none. Children: none expected. Interfaces:
`Comparable`. Collaborators: `Entity`, `System`.

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `id` | `str` | Canonical string identifier, unique within scope. |
| `uuid` | `UUID` | Machine-generated universally unique form. |
| `scope` | `str \| None` | Optional namespace (e.g. a `System` id) the uniqueness guarantee is bounded to. |
| `alias` | `str \| None` | Optional human-friendly alternate name (non-unique). |

**Properties.** `is_scoped` (read-only, `scope is not None`).

**Behaviors.** `create()`, `compare()`, `matches(other_or_str)`.

**Methods.**
- `create(scope: str | None = None, alias: str | None = None) -> Identity` — generates `id`/`uuid`; no preconditions; never raises.
- `compare(other: Identity) -> ComparisonResult` — equality by `(scope, id)` pair.
- `matches(value: str | Identity) -> bool` — convenience equality check against a raw string or another `Identity`.

**Private Helpers.** `_generate_uuid()`, `_normalize_id(raw: str) -> str`.

**Lifecycle.** Immutable value object — no lifecycle machine.

**Events.** `IdentityGenerated` (optional, low-value; typically not published).

**Exceptions.** `IdentityError` (base) → `InvalidIdentityError` (malformed `id`), `DuplicateIdentityError` (raised by the *registrar*, e.g. `System.add_entity`, not by `Identity` itself).

**Interfaces Implemented.** `Comparable`.

**Validation.** `id` must be non-empty and match the identifier grammar in `constants.py` (`ID_PATTERN`).

**Serialization.** Trivial flat value; all formats supported.

**Thread Safety.** Immutable → inherently thread-safe.

**Logging/Metrics.** None dedicated; identity generation is cheap and high-frequency, not separately instrumented.

---

## `Property`

**General.** Immutable, intrinsic, typed characteristic of an `Entity`
(e.g. `mass`, `symbol`). Design rationale: separated from `Attribute`
specifically to make the intrinsic/extrinsic distinction explicit and
enforce immutability by construction rather than by convention.

**Relationships.** Interfaces: `Comparable`, `Serializable`. Collaborators: `Entity`, `Validator`.

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `name` | `str` | Property name, unique within its owning Entity. |
| `value` | `PropertyValue` | The immutable value. |
| `value_type` | `type` | Declared type for validation. |
| `unit` | `str \| None` | Optional unit-of-measure label. |
| `validator` | `Validator \| None` | Optional validation rule. |
| `description` | `str \| None` | Human-readable documentation string. |

**Behaviors.** `create()`, `validate()`, `compare()`, `serialize()`/`deserialize()`.

**Methods.**
- `create(name, value, *, unit=None, validator=None) -> Property` — Preconditions: `name` matches identifier grammar. Postconditions: value frozen. Exceptions: `ValidationFailedError` if `validator` rejects `value` at construction.
- `validate() -> ValidationResult` — re-runs `validator` against `value` (useful after a schema change).
- `compare(other: Property) -> ComparisonResult` — compares `name` + `value`.

**Lifecycle.** Immutable value object — no lifecycle machine (a *new* `Property` replaces an old one; `Entity.add_property`/`remove_property` manage that, not `Property` itself).

**Events.** None dedicated (covered by `Entity`'s `PropertyAdded`/`PropertyRemoved`).

**Exceptions.** `PropertyError` (base) → `ValidationFailedError`, `ImmutablePropertyError` (raised on any attempted post-construction mutation).

**Validation.** `name` non-empty and unique per owner (uniqueness enforced by `Entity`, not `Property`); `value` must satisfy `validator` if present.

**Serialization.** Flat value; trivial across all formats.

**Thread Safety.** Immutable → thread-safe.

---

## `Attribute`

**General.** Named, typed, *mutable* characteristic captured inside
`State` snapshots. Design rationale: unlike `Property`, `Attribute`
tracks a change history and participates directly in State diffing.

**Relationships.** Interfaces: `Comparable`, `Observable`, `Serializable`. Collaborators: `Entity`, `State`, `Validator`, `Event`.

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `name` | `str` | Unique within owning Entity. |
| `value` | `AttributeValue` | Current value (mutable via `set_value`, never in place — see Methods). |
| `value_type` | `type` | Declared type. |
| `unit` | `str \| None` | Optional unit label. |
| `validator` | `Validator \| None` | Optional validation rule, re-run on every mutation. |
| `history` | `list[tuple[Time, AttributeValue]]` | Change log. |

**Behaviors.** `create()`, `set_value()`, `validate()`, `compare()`, `observe()`, `serialize()`/`deserialize()`.

**Methods.**
- `set_value(new_value: AttributeValue) -> None` — Preconditions: `new_value` passes `validator`. Postconditions: `value` updated; `(Time.now(), new_value)` appended to `history`; emits `AttributeChanged`. Exceptions: `ValidationFailedError`.
- `observe() -> Observation` — snapshot read without mutation.
- `compare(other: Attribute) -> ComparisonResult` — compares `name` + current `value`.

**Private Helpers.** `_append_history(value)`, `_trim_history()` (bounded by `constants.MAX_ATTRIBUTE_HISTORY_LENGTH`).

**Lifecycle.** No independent lifecycle; lives and dies with its owning `Entity`.

**Events.** `AttributeChanged`, `ValidationFailed`.

**Exceptions.** `AttributeError` (base, note: shadows Python builtin name — SDK will alias as `QmAttributeError` internally) → `ValidationFailedError`, `AttributeNotFoundError` (raised by `Entity`).

**Validation.** Same as `Property` but re-checked on every `set_value()`, not just at construction.

**Serialization.** Flat value plus optional `history` (history inclusion is a serializer option — full history is often omitted from wire format and reconstructed from `Entity.history` instead, to avoid duplication).

**Thread Safety.** **Not** thread-safe — `set_value()` mutates in place; same single-writer caveat as `Entity.update_state()`.

---

## `Behaviour`

**General.** Declares which `Interaction` types an `Entity` may
participate in, and under what `Constraint`s, plus pre/post hooks.
Design rationale: keeps "what am I allowed to do" declarative and
inspectable, separate from `Interaction`'s "what actually happened".

**Relationships.** Interfaces: `Serializable`. Collaborators: `Entity`, `Interaction`, `Constraint`, `Event`.

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `permitted_interaction_types` | `set[str]` | Whitelist of `Interaction.type` values. |
| `preconditions` | `list[Constraint]` | Must hold before participation is allowed. |
| `pre_hooks` | `list[EventHandler]` | Invoked before an Interaction is applied. |
| `post_hooks` | `list[EventHandler]` | Invoked after an Interaction commits. |

**Behaviors.** `create()`, `permits()`, `add_hook()`, `remove_hook()`.

**Methods.**
- `permits(interaction_type: str) -> bool` — pure predicate, never raises.
- `check_preconditions(state: State) -> ValidationResult` — evaluates `preconditions` against a candidate `state`.
- `add_hook(when: Literal["pre","post"], handler: EventHandler) -> None`.

**Lifecycle.** No independent lifecycle; attached to an `Entity` at `initialize()` time and generally immutable thereafter (hooks may be added while `INACTIVE`, not while `ACTIVE`, to avoid races — enforced by `Entity`, not `Behaviour`).

**Events.** None dedicated.

**Exceptions.** `BehaviourError` (base) → `InteractionNotPermittedError`.

**Validation.** `permitted_interaction_types` entries must be non-empty strings; duplicate hook registration is a no-op, not an error.

**Serialization.** Hooks (callables) are **not** serialized — only `permitted_interaction_types` and `preconditions` are part of the wire format; hooks are re-attached programmatically on deserialization by the owning domain package.

**Thread Safety.** Read-mostly after attachment; safe for concurrent `permits()` calls.

---

## `Relationship`

**General.** Typed, directed or undirected connection between two or
more Entities within a `System`. Design rationale: kept generic enough
to represent bonds, forces, correlations, or business associations
without a combinatorial explosion of Relationship subclasses.

**Relationships (meta).** Interfaces: `Identifiable`, `Serializable`, `Comparable`. Collaborators: `Entity`, `System`.

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `id` | `RelationshipId` | Unique id. |
| `type` | `str` | Domain-qualified kind (e.g. `"chemistry.covalent_bond"`). |
| `participants` | `list[EntityId]` | Ordered if `direction == DIRECTED`. |
| `direction` | `RelationshipDirection` (enum) | `DIRECTED` \| `UNDIRECTED`. |
| `cardinality` | `RelationshipCardinality` (enum) | `ONE_TO_ONE` \| `ONE_TO_MANY` \| `MANY_TO_MANY`. |
| `strength` | `float \| None` | Optional weight/strength metric. |
| `metadata` | `dict[str, Any]` | Free-form extension data. |

**Behaviors.** `create()`, `involves()`, `other_end()`, `compare()`, `serialize()`/`deserialize()`.

**Methods.**
- `involves(entity_id: EntityId) -> bool` — membership predicate.
- `other_end(entity_id: EntityId) -> list[EntityId]` — Preconditions: `entity_id` in `participants`. Returns the remaining participant(s). Exceptions: `EntityNotFoundError` if not a participant.

**Lifecycle.** No independent lifecycle; created/destroyed via `System.add_relationship`/`remove_relationship`.

**Events.** None dedicated (covered by `System`'s `RelationshipAdded`/`RelationshipRemoved`).

**Exceptions.** `RelationshipError` (base) → `EntityNotFoundError`, `InvalidCardinalityError` (raised if `participants` count violates `cardinality`).

**Validation.** `len(participants) >= 2`; count consistent with `cardinality`.

**Serialization.** Participants serialize as id references, never embedded copies (avoids duplication when the same Entity appears in many Relationships).

**Thread Safety.** Effectively immutable after creation (mutation = remove + re-add via `System`).

---

## `Constraint`

**General.** A rule restricting the valid State space of an
Entity/System. Design rationale: expressed as an evaluatable predicate
object rather than inline code, so Constraints can be introspected,
serialized, and (in later releases) fed to an external solver.

**Relationships.** Interfaces: `Identifiable`, `Serializable`. Collaborators: `State`, `Entity`, `System`.

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `id` | `ConstraintId` | Unique id. |
| `name` | `str` | Human-readable name. |
| `expression` | `ConstraintExpression` | Structured predicate descriptor (not raw code — see `types.py`). |
| `severity` | `ConstraintSeverity` (enum) | `HARD` \| `SOFT`. |
| `description` | `str \| None` | Documentation string. |

**Behaviors.** `create()`, `evaluate()`, `serialize()`/`deserialize()`.

**Methods.**
- `evaluate(state: State) -> ConstraintResult` — Preconditions: none. Return: `ConstraintResult{satisfied: bool, detail: str}`. Never raises for an unmet Constraint — the *caller* (`Entity.update_state()`) decides whether to raise `ConstraintViolationError` based on `severity`.

**Lifecycle.** No independent lifecycle.

**Events.** None dedicated (covered by `ConstraintViolated`, emitted by the evaluating owner).

**Exceptions.** `ConstraintError` (base) → `InvalidConstraintExpressionError` (malformed `expression` at construction time).

**Validation.** `expression` must reference only Attribute/Property names declared on the target Entity type (soft-checked; hard enforcement is a domain-package concern).

**Serialization.** `expression` must be representable as data (no embedded closures/lambdas) precisely so it can cross the language boundary to future C++/Rust/Java/Go/Julia ports.

**Thread Safety.** Immutable after creation → thread-safe; `evaluate()` is a pure function of the input `state`.

---

## `Lifecycle`

**General.** The ordered set of stages an `Entity`/`System` passes
through, and the state-machine contract governing valid transitions.
Design rationale: extracted into its own class (rather than inlined
enum + if/else in `Entity`) so the transition table is declarative,
testable in isolation, and reusable by `System` and future domain
classes without duplication.

**Relationships.** Interfaces: `Serializable`. Collaborators: `Entity`, `System`, `Event`.

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `stage` | `LifecycleStage` (enum) | Current stage. |
| `history` | `list[tuple[Time, LifecycleStage]]` | Full transition log. |
| `transition_table` | `dict[LifecycleStage, set[LifecycleStage]]` | Allowed `from -> {to...}` transitions. |

**Behaviors.** `create()`, `transition_to()`, `can_transition_to()`.

**Methods.**
- `transition_to(target: LifecycleStage) -> None` — Preconditions: `target in transition_table[stage]`. Postconditions: `stage = target`; entry appended to `history`; emits a stage-specific Event (e.g. `EntityActivated`). Exceptions: `InvalidLifecycleTransitionError`.
- `can_transition_to(target: LifecycleStage) -> bool` — pure predicate, never raises.

**Canonical stage sequence (see `entity.md`/`system.md` §Lifecycle):**
```
CREATED → INITIALIZED → ACTIVE ⇄ INACTIVE
                          ↓
                       SUSPENDED → ACTIVE
                          ↓
                       DESTROYED (terminal)
```

**Events.** `EntityCreated`/`SystemCreated` and every other
`*Activated`/`*Deactivated`/`*Suspended`/`*Destroyed` event listed
under `Entity`/`System` originate from `Lifecycle.transition_to()`
internally, parametrized by which owner type is transitioning.

**Exceptions.** `LifecycleError` (base) → `InvalidLifecycleTransitionError`.

**Validation.** `transition_table` must not contain unreachable stages or a path out of `DESTROYED` (terminal-state invariant, checked at `Lifecycle` construction/registration time).

**Serialization.** `history` is fully serializable; `transition_table` is typically a class-level constant, not re-serialized per instance.

**Thread Safety.** `transition_to()` must be treated as a critical section — same single-writer caveat as `Entity.update_state()`.

---

## `Event`

**General.** A discrete, timestamped record of something happening,
published through an `EventBus`. Design rationale: every other class
in `foundation` emits `Event`s rather than calling
subscriber-callback lists directly, decoupling producers from
consumers (logging, telemetry, domain listeners) entirely.

**Relationships.** Interfaces: `Identifiable`, `Serializable`, `Timestamped`. Collaborators: every other foundation class (as producers), `runtime`/`telemetry`/`logging` (as consumers, outside `foundation`).

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `id` | `EventId` | Unique id. |
| `type` | `EventType` (enum) | Kind of event (see `07-events.md`). |
| `source_id` | `EntityId \| SystemId \| InteractionId` | Id of the object that emitted it. |
| `timestamp` | `Time` | Instant of occurrence. |
| `payload` | `dict[str, Any]` | Event-specific structured data. |

**Behaviors.** `create()`, `serialize()`/`deserialize()`.

**`EventBus` contract (companion, not a separate module):**
- `publish(event: Event) -> None`
- `subscribe(event_type: EventType, handler: EventHandler) -> SubscriptionId`
- `unsubscribe(subscription_id: SubscriptionId) -> None`

**Methods.**
- `create(type_, source_id, payload) -> Event` — Preconditions: `type_` is a registered `EventType`. Postconditions: `timestamp = Time.now()`. Never raises under normal use.

**Lifecycle.** Immutable, fire-and-forget value object — no lifecycle machine.

**Events.** N/A (an `Event` does not itself emit Events).

**Exceptions.** `EventError` (base) → `UnknownEventTypeError`, `EventBusUnavailableError` (raised by `EventBus.publish` if no bus is configured — publishing is best-effort and must never crash the producing operation; see Thread Safety note).

**Validation.** `payload` keys must match the schema declared for `type_` in `enums.py`/`types.py` (soft validation, warning-level by default to avoid breaking producers on schema evolution).

**Serialization.** Fully flat, trivial across all formats — this is the natural format for audit logs and event-sourced replay.

**Thread Safety.** `EventBus.publish()` must be safe to call from any thread/task without blocking the producer on slow subscribers — architecture mandates an async-dispatch or bounded-queue contract at the `EventBus` implementation level (implementation deferred to `runtime`).

**Metrics.** `events_published_total` (by `type`), `event_bus_queue_depth` (gauge), `event_dispatch_duration` (histogram).

---

## `Observation`

**General.** A recorded measurement of `State` at a point in `Space`
and `Time`. Design rationale: separated from `State` itself because an
Observation carries *measurement* semantics (observer, method,
uncertainty) that a raw State snapshot does not.

**Relationships.** Interfaces: `Identifiable`, `Serializable`, `Timestamped`. Collaborators: `Entity`, `System`, `State`, `Space`, `Time`, `Knowledge` (consumer).

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `id` | `ObservationId` | Unique id. |
| `subject_id` | `EntityId \| SystemId` | What was observed. |
| `state` | `State` | The measured State (may be a partial projection, not necessarily the full State). |
| `observer` | `str \| None` | Identifier of the observing agent/service. |
| `method` | `ObservationMethod` (enum) | How the measurement was taken (e.g. `DIRECT`, `DERIVED`, `SIMULATED`). |
| `uncertainty` | `float \| None` | Optional measurement uncertainty metric. |
| `timestamp` | `Time` | Instant of observation. |

**Behaviors.** `create()`, `serialize()`/`deserialize()`.

**Methods.**
- `create(subject_id, state, *, observer=None, method=ObservationMethod.DIRECT, uncertainty=None) -> Observation` — never raises under normal use; emits `ObservationRecorded`.

**Lifecycle.** Immutable value object — no lifecycle machine.

**Events.** `ObservationRecorded`.

**Exceptions.** `ObservationError` (base) → `InvalidObservationError` (e.g. `state` inconsistent with `subject_id`'s declared type).

**Validation.** `uncertainty`, if present, must be `>= 0`.

**Serialization.** Straightforward; embeds or references its `state` depending on serializer policy (embed by default, since Observations are often exported standalone for analysis).

**Thread Safety.** Immutable → thread-safe.

---

## `Knowledge`

**General.** Structured information derived from one or more
`Observation`s, usable for Prediction. Design rationale: kept
deliberately thin in `foundation` — it is a *container and provenance
tracker* for models/rules/statistics, not a machine-learning engine
(that lives in the `ai` domain package).

**Relationships.** Interfaces: `Identifiable`, `Serializable`. Collaborators: `Observation`, future `ai`/`math` packages (as producers of the actual `payload`).

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `id` | `KnowledgeId` | Unique id. |
| `subject_type` | `str` | Domain type this Knowledge applies to (e.g. `"finance.Instrument"`). |
| `payload` | `dict[str, Any]` | The structured model/rule/statistic itself (opaque to `foundation`). |
| `contributing_observations` | `list[ObservationId]` | Provenance references. |
| `confidence` | `float \| None` | Optional confidence score in `[0, 1]`. |
| `created_at` | `Time` | Derivation instant. |

**Behaviors.** `create()`, `predict()` (interface point only — raises `NotImplementedError` in `foundation`; concrete Prediction logic belongs to domain/`ai` packages), `serialize()`/`deserialize()`.

**Methods.**
- `create(subject_type, payload, contributing_observations, *, confidence=None) -> Knowledge` — Preconditions: `contributing_observations` non-empty (Knowledge must be traceable to at least one Observation) unless explicitly marked `metadata["a_priori"] = True`.
- `predict(input_: Any) -> Any` — architecture-only interface point; `foundation`'s implementation raises `NotImplementedError`, documenting the contract signature for `ai`/domain packages to override.

**Lifecycle.** Immutable value object once created (a new derivation produces a new `Knowledge`, preserving the provenance chain) — no lifecycle machine.

**Events.** `KnowledgeGenerated`.

**Exceptions.** `KnowledgeError` (base) → `InsufficientEvidenceError` (raised if `contributing_observations` is empty and not marked a priori), `PredictionNotSupportedError` (raised by the default `predict()`).

**Validation.** `confidence`, if present, in `[0.0, 1.0]`.

**Serialization.** `payload` serialization depends on its internal shape and is delegated to a format-aware `Serializer`; provenance references serialize as ids only.

**Thread Safety.** Immutable → thread-safe.

---

## `Transformation`

**General.** A mapping that converts an Entity/State/System from one
representation or form to another. Design rationale: the *only*
extension point in `foundation` explicitly designed to be subclassed
with real computational logic by domain packages — `Interaction`
delegates all actual "what happens" logic to a `Transformation`.

**Relationships.** Interfaces: `Serializable`. Collaborators: `Interaction`, `State`.

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `type` | `str` | Domain-qualified kind (e.g. `"quantum.hadamard_gate"`). |
| `parameters` | `dict[str, Any]` | Data-only parameters (no closures) needed to apply the mapping. |
| `input_schema` | `TypeSchema \| None` | Optional declared input shape. |
| `output_schema` | `TypeSchema \| None` | Optional declared output shape. |
| `is_reversible` | `bool` | Whether `inverse()` is supported. |

**Behaviors.** `apply()` (abstract — domain packages implement), `inverse()` (optional, only if `is_reversible`), `compose()`, `serialize()`/`deserialize()`.

**Methods.**
- `apply(state: State) -> State` — abstract method; `foundation` defines only the contract (`raise NotImplementedError`), never scientific logic, per project constraints.
- `inverse() -> Transformation` — Preconditions: `is_reversible`. Exceptions: `TransformationNotReversibleError`.
- `compose(other: Transformation) -> Transformation` — returns a new `Transformation` representing `self` followed by `other` (a `CompositeTransformation`, still data-only at the `parameters` level where possible).

**Lifecycle.** Stateless/immutable value object — no lifecycle machine.

**Events.** None dedicated (covered by `Interaction`'s events, since `Transformation.apply()` is always invoked from within `Interaction.apply()`).

**Exceptions.** `TransformationError` (base) → `TransformationNotReversibleError`, `SchemaMismatchError` (raised if input `State` doesn't match `input_schema`, when declared).

**Validation.** If `input_schema`/`output_schema` are declared, `apply()` implementations are expected (by contract, not by enforced runtime check in `foundation`) to validate against them.

**Serialization.** `parameters` must be plain data; the *behavior* of `apply()` itself is identified by `type` (a registry lookup at deserialize time resolves `type` back to a concrete class in the receiving process/language) — this is what makes `Transformation` portable across the future multi-language SDK ports.

**Thread Safety.** `apply()` is expected to be a pure function of its input `State` and `parameters` — no hidden mutable state — making it trivially safe for concurrent/parallel Interaction pipelines.

---

## `Space`

**General.** The coordinate/topological context in which Entities and
their State are situated. Design rationale: kept abstract enough to
cover physical space, Hilbert space, feature space, or portfolio space
under one contract, so `visualization`/`simulation` can reason about
"where" generically.

**Relationships.** Interfaces: `Serializable`, `Comparable`. Collaborators: `State`, `Observation`, `Entity`, `System`.

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `name` | `str` | Human-readable identifier (e.g. `"3D Euclidean"`, `"2-qubit Hilbert space"`). |
| `dimensionality` | `int` | Number of coordinate axes/basis vectors. |
| `coordinate_system` | `str` | Descriptive label (e.g. `"cartesian"`, `"computational_basis"`). |
| `metric` | `str \| None` | Optional metric/distance-function label. |
| `bounds` | `tuple[Any, Any] \| None` | Optional min/max per-axis bounds. |

**Behaviors.** `create()`, `contains()`, `distance()` (interface point only), `compare()`.

**Methods.**
- `contains(point: Any) -> bool` — Preconditions: `point` matches `dimensionality`. Returns whether `point` lies within `bounds` (if declared; else always `True`).
- `distance(a: Any, b: Any) -> float` — architecture-only interface point (`raise NotImplementedError` in `foundation`; concrete metric math belongs to `math`).

**Lifecycle.** Stateless/immutable value object — no lifecycle machine.

**Events.** None dedicated.

**Exceptions.** `SpaceError` (base) → `DimensionMismatchError`, `OutOfBoundsError`, `MetricNotImplementedError` (default `distance()`).

**Validation.** `dimensionality >= 1`; `bounds`, if present, must have matching arity.

**Serialization.** Flat value; trivial.

**Thread Safety.** Immutable → thread-safe.

---

## `Time`

**General.** The ordering dimension over which `State` evolves,
supporting both discrete (simulation timestep) and continuous
(wall-clock) representations under one contract.

**Relationships.** Interfaces: `Comparable`, `Serializable`. Collaborators: every timestamped class (`Entity`, `State`, `Event`, `Observation`, `Interaction`).

**Attributes.**
| Attribute | Type | Explanation |
|---|---|---|
| `mode` | `TimeMode` (enum) | `WALL_CLOCK` \| `DISCRETE_STEP` \| `LOGICAL`. |
| `value` | `float \| int` | Numeric instant (seconds since epoch, step index, or logical counter depending on `mode`). |
| `unit` | `str \| None` | Optional unit label for `DISCRETE_STEP` (e.g. `"fs"`, `"iteration"`). |

**Behaviors.** `now()` (factory, `WALL_CLOCK` mode), `create()`, `compare()`, `delta()`, `advance()`.

**Methods.**
- `now() -> Time` — classmethod; wall-clock factory.
- `compare(other: Time) -> ComparisonResult` — Preconditions: same `mode` (mixing modes requires explicit conversion). Exceptions: `IncompatibleTimeModeError`.
- `delta(other: Time) -> float | int` — signed difference; same preconditions as `compare`.
- `advance(by: float | int) -> Time` — returns a new `Time` instance (immutable) advanced by `by`.

**Lifecycle.** Immutable value object — no lifecycle machine.

**Events.** None dedicated.

**Exceptions.** `TimeError` (base) → `IncompatibleTimeModeError`.

**Validation.** `value` must be finite (no `NaN`/`inf` for `WALL_CLOCK`); `DISCRETE_STEP` `value` must be a non-negative integer.

**Serialization.** Flat value; trivial. `WALL_CLOCK` recommended wire format: ISO-8601 string for cross-language portability.

**Thread Safety.** Immutable → thread-safe.

---

## Cross-Cutting Note on Attribute-Naming Collisions

`Attribute` as a class name shadows Python's built-in exception-related
naming conventions in some tooling (`AttributeError` is a Python
builtin). The exception hierarchy in `06-exceptions-and-utilities.md`
therefore aliases the foundation `AttributeError` as `QmAttributeError`
internally to avoid confusing shadowing, while the *class* `Attribute`
itself is unaffected since it does not collide with any builtin.
