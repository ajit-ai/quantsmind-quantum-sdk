"""
Factories Module

This module provides factory functions and classes for creating Foundation package objects.
Factories provide convenient creation methods for foundation objects with common configurations.

Purpose
-------
Provide factory functions and classes for the Foundation package.

Scientific Meaning
------------------
Factories simplify object creation in scientific computing applications,
ensuring consistent initialization and reducing boilerplate code.

Responsibilities
----------------
- Provide factory functions for common objects
- Support builder patterns
- Enable object configuration
- Support custom factories

Dependencies
------------
typing (standard library)
quantsmind.foundation.identity (identity module)
quantsmind.foundation.attribute (attribute module)
quantsmind.foundation.property (property module)
quantsmind.foundation.state (state module)
quantsmind.foundation.space (space module)
quantsmind.foundation.time (time module)
quantsmind.foundation.behaviour (behaviour module)
quantsmind.foundation.relationship (relationship module)
quantsmind.foundation.constraint (constraint module)
quantsmind.foundation.lifecycle (lifecycle module)
quantsmind.foundation.event (event module)
quantsmind.foundation.transformation (transformation module)
quantsmind.foundation.observation (observation module)
quantsmind.foundation.knowledge (knowledge module)
quantsmind.foundation.entity (entity module)
quantsmind.foundation.system (system module)
quantsmind.foundation.interaction (interaction module)

Future Extensions
-----------------
- Async factories
- Configurable factories
- Factory composition
- Factory caching
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from quantsmind.foundation.attribute import Attribute
from quantsmind.foundation.behaviour import Behaviour
from quantsmind.foundation.constraint import Constraint
from quantsmind.foundation.entity import Entity
from quantsmind.foundation.enums import (
    BehaviourType,
    ConstraintSeverity,
    ConstraintType,
    EntityType,
    EventType,
    InteractionType,
    KnowledgeType,
    LifecycleStage,
    ObservationType,
    RelationshipType,
    SpaceType,
    SystemType,
    TimeType,
    TransformationType,
)
from quantsmind.foundation.event import Event
from quantsmind.foundation.identity import Identity
from quantsmind.foundation.interaction import Interaction
from quantsmind.foundation.knowledge import Knowledge
from quantsmind.foundation.lifecycle import Lifecycle
from quantsmind.foundation.observation import Observation
from quantsmind.foundation.property import Property
from quantsmind.foundation.relationship import Relationship
from quantsmind.foundation.space import Space
from quantsmind.foundation.state import State
from quantsmind.foundation.system import System
from quantsmind.foundation.time import Time
from quantsmind.foundation.transformation import Transformation

logger = logging.getLogger(__name__)


class EntityFactory:
    """Factory for creating Entity instances.

    This class provides convenient methods for creating entities with common configurations.

    Example:
        >>> factory = EntityFactory()
        >>> entity = factory.create_physical_entity()
    """

    def create_entity(
        self,
        entity_type: EntityType = EntityType.GENERIC,
        properties: Optional[Dict[str, Property]] = None,
        state: Optional[State] = None,
    ) -> Entity:
        """Create an Entity instance.

        Args:
            entity_type: Type of entity
            properties: Optional properties
            state: Optional state

        Returns:
            Entity instance

        Example:
            >>> entity = factory.create_entity(entity_type=EntityType.PHYSICAL)
        """
        return Entity(
            entity_type=entity_type,
            properties=properties,
            state=state,
        )

    def create_physical_entity(
        self,
        properties: Optional[Dict[str, Property]] = None,
        state: Optional[State] = None,
    ) -> Entity:
        """Create a physical entity.

        Args:
            properties: Optional properties
            state: Optional state

        Returns:
            Physical Entity instance

        Example:
            >>> entity = factory.create_physical_entity()
        """
        return self.create_entity(
            entity_type=EntityType.PHYSICAL,
            properties=properties,
            state=state,
        )

    def create_quantum_entity(
        self,
        properties: Optional[Dict[str, Property]] = None,
        state: Optional[State] = None,
    ) -> Entity:
        """Create a quantum entity.

        Args:
            properties: Optional properties
            state: Optional state

        Returns:
            Quantum Entity instance

        Example:
            >>> entity = factory.create_quantum_entity()
        """
        return self.create_entity(
            entity_type=EntityType.QUANTUM,
            properties=properties,
            state=state,
        )


class SystemFactory:
    """Factory for creating System instances.

    This class provides convenient methods for creating systems with common configurations.

    Example:
        >>> factory = SystemFactory()
        >>> system = factory.create_physical_system()
    """

    def create_system(
        self,
        system_type: SystemType = SystemType.GENERIC,
        entities: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[Relationship]] = None,
        state: Optional[State] = None,
    ) -> System:
        """Create a System instance.

        Args:
            system_type: Type of system
            entities: Optional entities
            relationships: Optional relationships
            state: Optional state

        Returns:
            System instance

        Example:
            >>> system = factory.create_system(system_type=SystemType.PHYSICAL)
        """
        return System(
            system_type=system_type,
            entities=entities,
            relationships=relationships,
            state=state,
        )

    def create_physical_system(
        self,
        entities: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[Relationship]] = None,
        state: Optional[State] = None,
    ) -> System:
        """Create a physical system.

        Args:
            entities: Optional entities
            relationships: Optional relationships
            state: Optional state

        Returns:
            Physical System instance

        Example:
            >>> system = factory.create_physical_system()
        """
        return self.create_system(
            system_type=SystemType.PHYSICAL,
            entities=entities,
            relationships=relationships,
            state=state,
        )


class StateFactory:
    """Factory for creating State instances.

    This class provides convenient methods for creating states with common configurations.

    Example:
        >>> factory = StateFactory()
        >>> state = factory.create_state({"position": [1.0, 2.0]})
    """

    def create_state(self, data: Optional[Dict[str, Any]] = None) -> State:
        """Create a State instance.

        Args:
            data: Optional state data

        Returns:
            State instance

        Example:
            >>> state = factory.create_state({"position": [1.0, 2.0]})
        """
        return State(data=data)

    def create_empty_state(self) -> State:
        """Create an empty State instance.

        Returns:
            Empty State instance

        Example:
            >>> state = factory.create_empty_state()
        """
        return self.create_state(data={})


class RelationshipFactory:
    """Factory for creating Relationship instances.

    This class provides convenient methods for creating relationships with common configurations.

    Example:
        >>> factory = RelationshipFactory()
        >>> rel = factory.create_directed_relationship("entity1", "entity2")
    """

    def create_relationship(
        self,
        relationship_type: RelationshipType = RelationshipType.DIRECTED,
        source: Optional[str] = None,
        target: Optional[str] = None,
        weight: Optional[float] = None,
    ) -> Relationship:
        """Create a Relationship instance.

        Args:
            relationship_type: Type of relationship
            source: Source entity ID
            target: Target entity ID
            weight: Optional weight

        Returns:
            Relationship instance

        Example:
            >>> rel = factory.create_relationship(source="entity1", target="entity2")
        """
        return Relationship(
            relationship_type=relationship_type,
            source=source,
            target=target,
            weight=weight,
        )

    def create_directed_relationship(
        self,
        source: str,
        target: str,
        weight: Optional[float] = None,
    ) -> Relationship:
        """Create a directed relationship.

        Args:
            source: Source entity ID
            target: Target entity ID
            weight: Optional weight

        Returns:
            Directed Relationship instance

        Example:
            >>> rel = factory.create_directed_relationship("entity1", "entity2")
        """
        return self.create_relationship(
            relationship_type=RelationshipType.DIRECTED,
            source=source,
            target=target,
            weight=weight,
        )

    def create_undirected_relationship(
        self,
        entity1: str,
        entity2: str,
        weight: Optional[float] = None,
    ) -> Relationship:
        """Create an undirected relationship.

        Args:
            entity1: First entity ID
            entity2: Second entity ID
            weight: Optional weight

        Returns:
            Undirected Relationship instance

        Example:
            >>> rel = factory.create_undirected_relationship("entity1", "entity2")
        """
        return self.create_relationship(
            relationship_type=RelationshipType.UNDIRECTED,
            source=entity1,
            target=entity2,
            weight=weight,
        )


class ConstraintFactory:
    """Factory for creating Constraint instances.

    This class provides convenient methods for creating constraints with common configurations.

    Example:
        >>> factory = ConstraintFactory()
        >>> constraint = factory.create_constraint("positive_mass", lambda ctx: ctx["mass"] > 0)
    """

    def create_constraint(
        self,
        name: str,
        rule: Callable[[Dict[str, Any]], Any],
        constraint_type: ConstraintType = ConstraintType.CUSTOM,
        severity: ConstraintSeverity = ConstraintSeverity.ERROR,
    ) -> Constraint:
        """Create a Constraint instance.

        Args:
            name: Constraint name
            rule: Constraint rule
            constraint_type: Type of constraint
            severity: Constraint severity

        Returns:
            Constraint instance

        Example:
            >>> constraint = factory.create_constraint("positive_mass", lambda ctx: ctx["mass"] > 0)
        """
        return Constraint(
            name=name,
            rule=rule,
            constraint_type=constraint_type,
            severity=severity,
        )

    def create_error_constraint(
        self,
        name: str,
        rule: Callable[[Dict[str, Any]], Any],
    ) -> Constraint:
        """Create an error-level constraint.

        Args:
            name: Constraint name
            rule: Constraint rule

        Returns:
            Error Constraint instance

        Example:
            >>> constraint = factory.create_error_constraint("positive_mass", lambda ctx: ctx["mass"] > 0)
        """
        return self.create_constraint(
            name=name,
            rule=rule,
            severity=ConstraintSeverity.ERROR,
        )

    def create_warning_constraint(
        self,
        name: str,
        rule: Callable[[Dict[str, Any]], Any],
    ) -> Constraint:
        """Create a warning-level constraint.

        Args:
            name: Constraint name
            rule: Constraint rule

        Returns:
            Warning Constraint instance

        Example:
            >>> constraint = factory.create_warning_constraint("high_mass", lambda ctx: ctx["mass"] > 100)
        """
        return self.create_constraint(
            name=name,
            rule=rule,
            severity=ConstraintSeverity.WARNING,
        )


# Export
__all__ = [
    "EntityFactory",
    "SystemFactory",
    "StateFactory",
    "RelationshipFactory",
    "ConstraintFactory",
]
