# UML Diagrams

Rendered as Mermaid so they display directly on GitHub/most Markdown
viewers. These are descriptive architecture diagrams, not
implementation-generated — keep them in sync with the class specs by
hand when the spec changes.

## 1. Package Diagram

```mermaid
graph TD
    subgraph foundation["quantsmind.foundation"]
        core_classes["entity · system · state · interaction"]
        support_classes["identity · property · attribute · behaviour
        relationship · constraint · lifecycle · event
        observation · knowledge · transformation · space · time"]
        infra["interfaces · protocols · enums
        validators · serializers · factories
        exceptions · constants · types"]
    end

    core_classes --> support_classes
    support_classes --> infra
    core_classes --> infra

    domain_quantum["quantsmind.quantum"] --> foundation
    domain_physics["quantsmind.physics"] --> foundation
    domain_finance["quantsmind.finance"] --> foundation
    domain_ai["quantsmind.ai"] --> foundation

    style foundation fill:#eef3ff,stroke:#3355aa
```

## 2. Class Diagram (core ontology)

```mermaid
classDiagram
    class Entity {
        +EntityId id
        +str name
        +dict~str,Property~ properties
        +dict~str,Attribute~ attributes
        +State state
        +list~State~ history
        +list~Relationship~ relationships
        +list~Constraint~ constraints
        +Behaviour behaviour
        +Lifecycle lifecycle
        +create()
        +initialize()
        +activate()
        +update_state(new_state)
        +interact(interaction)
        +clone()
        +observe()
        +validate()
    }

    class System {
        +dict~EntityId,Entity~ entities
        +list~Relationship~ relationships
        +State state
        +list~Constraint~ constraints
        +Lifecycle lifecycle
        +add_entity(entity)
        +run_interaction(interaction)
        +find_entity()
        +validate()
    }

    class State {
        +StateId id
        +EntityId owner_id
        +Mapping~str,AttributeValue~ values
        +Time timestamp
        +InteractionId cause
        +diff(other)
        +merge(other)
        +validate(constraints)
    }

    class Interaction {
        +InteractionId id
        +str type
        +list~EntityId~ participants
        +Transformation transformation
        +InteractionStatus status
        +dict~EntityId,State~ results
        +apply()
        +commit()
        +cancel()
    }

    class Identity
    class Property
    class Attribute
    class Behaviour
    class Relationship
    class Constraint
    class Lifecycle
    class Event
    class Observation
    class Knowledge
    class Transformation
    class Space
    class Time

    Entity "1" *-- "1" Identity
    Entity "1" *-- "1" State : current
    Entity "1" *-- "0..*" State : history
    Entity "1" *-- "0..*" Property
    Entity "1" *-- "0..*" Attribute
    Entity "1" *-- "0..*" Relationship
    Entity "1" *-- "0..*" Constraint
    Entity "1" *-- "1" Behaviour
    Entity "1" *-- "1" Lifecycle

    System "1" o-- "0..*" Entity
    System "1" *-- "0..*" Relationship
    System "1" *-- "0..*" Constraint
    System "1" *-- "1" Lifecycle

    Interaction "1" --> "1..*" Entity : participants
    Interaction "1" *-- "1" Transformation
    Interaction "1" ..> "0..*" State : produces

    State ..> Time : timestamped by
    State "0..1" --> "0..1" Interaction : caused by

    Observation "1" --> "1" State : measures
    Observation "1" --> "1" Space
    Observation "1" ..> Knowledge : contributes to

    Relationship "1" --> "2..*" Entity : connects

    <<interface>> Identifiable
    <<interface>> Observable
    <<interface>> Serializable
    <<interface>> Cloneable
    <<interface>> Validatable
    <<interface>> Comparable
    <<interface>> Timestamped

    Entity ..|> Identifiable
    Entity ..|> Observable
    Entity ..|> Serializable
    Entity ..|> Cloneable
    Entity ..|> Validatable
    Entity ..|> Comparable
    Entity ..|> Timestamped

    System ..|> Identifiable
    System ..|> Observable
    System ..|> Serializable
    System ..|> Cloneable
    System ..|> Validatable
    System ..|> Comparable
    System ..|> Timestamped

    State ..|> Serializable
    State ..|> Comparable
    State ..|> Timestamped

    Interaction ..|> Identifiable
    Interaction ..|> Observable
    Interaction ..|> Serializable
    Interaction ..|> Comparable
    Interaction ..|> Timestamped
```

## 3. Sequence Diagram — Running an Interaction inside a System

```mermaid
sequenceDiagram
    actor Caller
    participant Sys as System
    participant Ent1 as Entity (participant 1)
    participant Ent2 as Entity (participant 2)
    participant Int as Interaction
    participant Tr as Transformation
    participant Bus as EventBus

    Caller->>Sys: run_interaction(interaction)
    Sys->>Sys: _check_participant_membership(interaction)
    Sys->>Ent1: behaviour.permits(interaction.type)
    Sys->>Ent2: behaviour.permits(interaction.type)
    Sys->>Int: apply()
    Int->>Tr: apply(Ent1.state)
    Tr-->>Int: new State for Ent1
    Int->>Tr: apply(Ent2.state)
    Tr-->>Int: new State for Ent2
    Int->>Bus: publish(InteractionStarted)
    Int->>Int: commit()
    Int->>Ent1: update_state(new_state_1, cause=interaction)
    Ent1->>Ent1: validate against constraints
    alt constraint satisfied
        Ent1-->>Int: ok
    else constraint violated
        Ent1-->>Int: raise ConstraintViolationError
        Int->>Int: _rollback_partial_commit()
        Int->>Bus: publish(InteractionFailed)
        Int-->>Sys: raise ConstraintViolationError
    end
    Int->>Ent2: update_state(new_state_2, cause=interaction)
    Int->>Bus: publish(InteractionCompleted)
    Sys->>Sys: _aggregate_member_state()
    Sys->>Bus: publish(StateChanged) [system scope]
    Sys-->>Caller: return
```

## 4. Dependency Diagram (foundation modules)

```mermaid
graph LR
    exceptions[exceptions.py]
    types[types.py]
    enums[enums.py]
    constants[constants.py]

    identity[identity.py] --> exceptions
    identity --> types

    property[property.py] --> validators
    attribute[attribute.py] --> validators
    attribute --> event

    validators[validators.py] --> types
    validators --> enums
    validators --> exceptions

    serializers[serializers.py] --> enums
    serializers --> types
    serializers --> exceptions

    space[space.py] --> types
    space --> exceptions

    time[time.py] --> types
    time --> exceptions

    event[event.py] --> time
    event --> types
    event --> exceptions
    event --> enums

    state[state.py] --> time
    state --> attribute
    state --> event
    state --> exceptions

    behaviour[behaviour.py] --> constraint
    behaviour --> event
    behaviour --> exceptions

    relationship[relationship.py] --> types
    relationship --> exceptions

    constraint[constraint.py] --> state
    constraint --> exceptions

    lifecycle[lifecycle.py] --> event
    lifecycle --> enums
    lifecycle --> exceptions

    transformation[transformation.py] --> state
    transformation --> exceptions

    observation[observation.py] --> state
    observation --> space
    observation --> time
    observation --> event

    knowledge[knowledge.py] --> observation

    interfaces[interfaces.py] --> types
    interfaces --> exceptions

    protocols[protocols.py] --> types

    factories[factories.py] --> entity
    factories --> system
    factories --> interaction
    factories --> event
    factories --> identity
    factories --> lifecycle

    entity[entity.py] --> identity
    entity --> state
    entity --> property
    entity --> attribute
    entity --> behaviour
    entity --> relationship
    entity --> constraint
    entity --> lifecycle
    entity --> event
    entity --> interfaces

    system[system.py] --> entity
    system --> relationship
    system --> interaction
    system --> state
    system --> lifecycle
    system --> event
    system --> interfaces

    interaction[interaction.py] --> entity
    interaction --> state
    interaction --> transformation
    interaction --> event
    interaction --> time
    interaction --> interfaces

    style exceptions fill:#ffe8e8
    style types fill:#ffe8e8
    style enums fill:#ffe8e8
    style constants fill:#ffe8e8
```

The four modules highlighted in red (`exceptions`, `types`, `enums`,
`constants`) are the only modules with **zero** internal foundation
dependencies — every other module depends on at least one of them,
directly or transitively, and there are no cycles.
