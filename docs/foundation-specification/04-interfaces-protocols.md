# Interfaces & Protocols (`interfaces.py`, `protocols.py`)

`foundation` separates **nominal** contracts (`interfaces.py` —
`abc.ABC` classes requiring explicit inheritance) from **structural**
contracts (`protocols.py` — `typing.Protocol` classes usable via duck
typing). Every foundation class implements the nominal interfaces
listed in its own spec; the structural Protocols exist so external
code (domain packages, third-party plugins) can conform without
inheriting from `foundation` base classes at all — important for
future non-Python ports where "interface" maps to a trait/typeclass
rather than an abstract base class.

## `interfaces.py`

### `Identifiable`
- **Responsibility:** Guarantee every implementer exposes a stable
  identity usable for equality, hashing, and lookup.
- **Contract:**
  - `id: EntityId` (property)
  - `uuid: UUID` (property)
  - `__eq__(other) -> bool` — identity-based equality
  - `__hash__() -> int` — identity-based hash
- **Implemented by:** `Entity`, `System`, `Relationship`, `Constraint`, `Event`, `Observation`, `Knowledge`, `Interaction`.

### `Observable`
- **Responsibility:** Guarantee an implementer can produce an
  `Observation` of its current condition without mutating it, and can
  be subscribed to for its own lifecycle Events.
- **Contract:**
  - `observe(observer: str | None = None) -> Observation`
  - `subscribe(event_type: EventType, handler: EventHandler) -> SubscriptionId`
- **Implemented by:** `Entity`, `System`, `Attribute`, `Interaction`.

### `Serializable`
- **Responsibility:** Guarantee an implementer can round-trip to and
  from every supported wire format.
- **Contract:**
  - `serialize(format: SerializationFormat = SerializationFormat.JSON) -> bytes | str`
  - `deserialize(data: bytes | str, format: SerializationFormat = SerializationFormat.JSON) -> Self` (classmethod)
- **Implemented by:** every foundation class except pure-behavioral
  helpers (`Behaviour`'s hooks are the sole excluded piece, per its
  own spec).

### `Cloneable`
- **Responsibility:** Guarantee a safe, deep, Identity-refreshing copy
  operation.
- **Contract:**
  - `clone(**overrides: Any) -> Self`
- **Implemented by:** `Entity`, `System`.
- **Not implemented by `State`, `Interaction`, `Observation`,
  `Knowledge`, `Event`:** these are immutable historical facts;
  "cloning" one would misrepresent provenance. New instances are
  created via their own `create()` factory instead.

### `Validatable`
- **Responsibility:** Guarantee an implementer can self-report
  correctness against its declared rules.
- **Contract:**
  - `validate() -> ValidationResult`
- **Implemented by:** `Entity`, `System`, `Property`, `Attribute`.
- **Note:** `State` and `Constraint` expose validation-shaped methods
  (`State.validate(constraints)`, `Constraint.evaluate(state)`) with a
  different signature (they need an external argument), so they do
  **not** implement this zero-argument interface directly — documented
  explicitly to avoid an implementer assuming otherwise.

### `Comparable`
- **Responsibility:** Guarantee structural/value comparison beyond
  identity equality.
- **Contract:**
  - `compare(other: Self) -> ComparisonResult`
  - `__lt__`, `__le__`, `__gt__`, `__ge__` where a total order is
    meaningful (optional — declared per-class; e.g. `Time` and
    `Identity` support ordering, `Entity` supports only
    equality-shaped comparison by default).
- **Implemented by:** all foundation classes.

### `Timestamped`
- **Responsibility:** Guarantee an implementer exposes creation/update
  instants using the shared `Time` type.
- **Contract:**
  - `created_at: Time` (property)
  - `updated_at: Time` (property, may equal `created_at` for immutable
    value objects)
- **Implemented by:** all foundation classes.

## `protocols.py`

Structural mirrors of the above (usable without inheritance), plus
callback-shaped Protocols not modeled as classes:

### `EventHandler` (Protocol)
```
__call__(event: Event) -> None
```
Used by `EventBus.subscribe`, `Behaviour.pre_hooks`/`post_hooks`.

### `Validator` (Protocol)
```
validate(value: Any) -> ValidationResult
```
Used by `Property`, `Attribute`, `validators.py`.

### `Transformer` (Protocol)
```
apply(state: State) -> State
```
Structural mirror of `Transformation.apply` for cases where a domain
package wants to supply a bare function instead of a full
`Transformation` subclass.

### `IdentifiableP`, `ObservableP`, `SerializableP`, `ComparableP`,
`TimestampedP` — structural (Protocol) mirrors of every nominal
interface above, named with a `P` suffix to avoid clashing with the
ABC names, for callers that want `isinstance()`-style structural
checks without requiring inheritance from `interfaces.py`.

## Why both nominal and structural versions exist

- **Nominal (`interfaces.py`)** is the primary contract every
  `foundation` class inherits from — it gives shared default behavior
  hooks (e.g. `Comparable.__lt__` default implementation delegating to
  `compare()`) and a single place to document the contract.
- **Structural (`protocols.py`)** exists for interoperability: a
  third-party plugin class that cannot or should not inherit from
  `foundation` ABCs (e.g. it already inherits from something else) can
  still be accepted anywhere `foundation` code type-hints against a
  Protocol, and can still pass `isinstance()` checks against Protocols
  decorated `@runtime_checkable`.
- This mirrors the split that will be needed in the multi-language
  ports anyway: nominal interfaces map to C++ abstract classes / Java
  interfaces / Rust traits with default methods; structural Protocols
  map to Go interfaces / Rust trait bounds without inheritance / Julia
  duck-typed multiple dispatch.
