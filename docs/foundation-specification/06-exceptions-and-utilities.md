# Exceptions & Utility Modules (`exceptions.py`, `validators.py`, `serializers.py`, `factories.py`)

## Exception Hierarchy (`exceptions.py`)

`exceptions.py` is a leaf module — every other module depends on it,
it depends on nothing. Every exception documented across this
specification is a concrete leaf of the tree below.

```
QuantsMindError
└── FoundationError
    ├── EntityError
    │   ├── InvalidLifecycleTransitionError
    │   ├── InvalidStateError
    │   ├── ConstraintViolationError
    │   ├── DuplicateIdentityError
    │   ├── DuplicatePropertyError
    │   ├── PropertyNotFoundError
    │   ├── ImmutablePropertyError
    │   ├── DuplicateAttributeError
    │   ├── QmAttributeError            (aliases Attribute-related failures; avoids
    │   │                                 shadowing Python's builtin AttributeError)
    │   │   └── AttributeNotFoundError
    │   ├── RelationshipError
    │   │   └── InvalidCardinalityError
    │   ├── CloneNotSupportedError
    │   └── InvalidComparisonError
    │
    ├── SystemError                     (namespaced as quantsmind SystemError;
    │   │                                 does not shadow Python's builtin)
    │   ├── EntityNotFoundError
    │   ├── DuplicateRelationshipError
    │   └── (reuses ConstraintViolationError, InteractionError from siblings)
    │
    ├── StateError
    │   ├── InvalidStateError            (shared with EntityError — see note below)
    │   ├── IncompatibleStateError
    │   └── StateMergeConflictError
    │
    ├── InteractionError
    │   ├── TransformationError
    │   │   ├── TransformationNotReversibleError
    │   │   └── SchemaMismatchError
    │   └── InvalidInteractionStateError
    │
    ├── IdentityError
    │   └── InvalidIdentityError
    │
    ├── PropertyError
    │   └── ValidationFailedError        (shared with AttributeError — see note below)
    │
    ├── BehaviourError
    │   └── InteractionNotPermittedError
    │
    ├── RelationshipError                (also used standalone by relationship.py)
    │
    ├── ConstraintError
    │   └── InvalidConstraintExpressionError
    │
    ├── LifecycleError
    │   └── InvalidLifecycleTransitionError (shared with EntityError — see note below)
    │
    ├── EventError
    │   ├── UnknownEventTypeError
    │   └── EventBusUnavailableError
    │
    ├── ObservationError
    │   └── InvalidObservationError
    │
    ├── KnowledgeError
    │   ├── InsufficientEvidenceError
    │   └── PredictionNotSupportedError
    │
    ├── SpaceError
    │   ├── DimensionMismatchError
    │   ├── OutOfBoundsError
    │   └── MetricNotImplementedError
    │
    ├── TimeError
    │   └── IncompatibleTimeModeError
    │
    ├── UnsupportedFormatError           (serializers.py — shared across all Serializable classes)
    └── DeserializationError             (serializers.py — shared across all Serializable classes)
```

**Note on shared leaf exceptions.** A handful of leaf exceptions
(`InvalidStateError`, `ValidationFailedError`,
`InvalidLifecycleTransitionError`) are raised by more than one owning
module. They are defined **once**, in the module that most centrally
owns the concept (`InvalidStateError` in `state.py`,
`ValidationFailedError` in `validators.py`, and
`InvalidLifecycleTransitionError` in `lifecycle.py`), and re-exported
by the modules that raise them, rather than being redefined per
module — this avoids the "duplicate concepts" anti-pattern called out
in the founding architecture while keeping each exception co-located
with the concept it is most naturally about.

**Design rules for this hierarchy:**
1. Every exception carries structured context (`entity_id`,
   `field_name`, `expected`, `actual`, etc. as applicable) as
   attributes, not just a message string — required so callers (and
   the `logging`/`telemetry` hooks) can act on failures programmatically.
2. Only leaf exceptions are ever raised directly; `FoundationError` and
   the per-concept intermediate classes (`EntityError`, `SystemError`,
   ...) exist purely for `except` clause granularity.
3. No exception class may cross a package boundary undocumented —
   every `foundation` exception is documented in this file precisely
   so that `core`, `runtime`, and every domain package know the full
   catchable surface.

## `validators.py`

**Purpose.** Declares the `Validator` contract (mirrored structurally
in `protocols.py`) and a small library of reusable, composable
validation rule descriptors — no domain-specific validation logic.

**Contract.**
```
Validator.validate(value: Any) -> ValidationResult
ValidationResult { is_valid: bool, errors: list[ValidationError] }
ValidationError { field: str, message: str, code: str }
```

**Reusable built-in Validator descriptors (architecture only):**
- `TypeValidator(expected_type)` — checks `isinstance`.
- `RangeValidator(min_=None, max_=None)` — numeric bounds.
- `RegexValidator(pattern)` — string pattern matching.
- `RequiredValidator()` — rejects `None`.
- `PredicateValidator(predicate: Callable[[Any], bool], message: str)` — arbitrary custom rule, still data-free at the *class* level (the predicate itself is supplied by the caller, not stored as serialized state — see `04-interfaces-protocols.md`'s discussion of why `Constraint.expression` must be data-only while a `Validator`'s predicate may be a live callable, since Validators are not required to be `Serializable`).
- `ValidatorChain(*validators)` — composes multiple Validators, short-circuiting or collecting all errors per a `mode` flag (`FAIL_FAST` \| `COLLECT_ALL`).

**Used by:** `Property`, `Attribute`, `Entity.validate()`,
`System.validate()`.

## `serializers.py`

**Purpose.** Declares the `Serializer` contract and per-format
capability descriptors; implements none of them (concrete
implementations are an R0.3+ concern, once a concrete numeric/data
backend is chosen).

**Contract.**
```
Serializer.serialize(obj: Serializable) -> bytes | str
Serializer.deserialize(data: bytes | str, target_type: type) -> Serializable
Serializer.format: SerializationFormat  (property)
Serializer.is_binary: bool              (property)
Serializer.supports_schema_evolution: bool  (property)
```

**Format capability matrix (architecture-level guidance, not enforced
in code):**

| Format | Binary | Human-readable | Schema evolution | Recommended for |
|---|---|---|---|---|
| JSON | No | Yes | Loose (additive fields) | Debugging, REST APIs, default |
| YAML | No | Yes | Loose | Config-adjacent documents |
| MessagePack | Yes | No | Loose | Compact wire transport |
| Binary (custom) | Yes | No | None (versioned framing required) | High-performance internal transport |
| Protocol Buffers | Yes | No | Strict (schema-first) | Cross-language boundary, the future C++/Rust/Java/Go/Julia bridge |

**Envelope requirement.** Every serialized document must include an
envelope carrying `sdk_version` (from `constants.SDK_VERSION`),
`type` (fully-qualified class name), and `format` — required so a
`deserialize()` call can dispatch to the correct concrete class and
detect version skew.

## `factories.py`

**Purpose.** Declares factory contracts that centralize construction,
guaranteeing invariants that individual class constructors should not
have to re-implement themselves.

**Contracts.**
```
EntityFactory.create(type_: str, **kwargs) -> Entity
SystemFactory.create(type_: str, **kwargs) -> System
InteractionFactory.create(type_: str, participants: list[Entity], transformation: Transformation, **kwargs) -> Interaction
EventFactory.create(type_: EventType, source_id: str, payload: dict, **kwargs) -> Event
```

**Guaranteed invariants (documented, enforced by the factory, not by
the raw class constructor):**
- Every `Entity`/`System` returned has a valid, unique `Identity`
  already registered in the target scope.
- Every `Entity`/`System` returned starts in `LifecycleStage.CREATED`.
- Every `Interaction` returned has verified participant `Behaviour`
  eligibility *before* returning (fail-fast at construction rather than
  at `apply()` time).
- Every `Event` returned has a valid `EventType` and a populated
  `timestamp`.

**Registry extension point.** `factories.py` also declares a
`FactoryRegistry` contract (`register(type_name, factory)`,
`resolve(type_name) -> Factory`) so domain packages can register their
own `Qubit`/`Portfolio`/`Molecule` factories without `foundation`
needing to know about them — the mechanism `plugins.py` (in the
top-level `plugins` package, not `foundation`) will build on in a
later release.
