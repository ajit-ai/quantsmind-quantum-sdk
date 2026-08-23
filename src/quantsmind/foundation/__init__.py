"""
Foundation Package — the universal ontology underlying QuantsMind SDK.

A System is composed of Entities. Every Entity has Identity, Properties,
State, Behaviour, Relationships, Constraints, and History. Entities evolve
through Interactions. Interactions change State. State evolves over Space
and Time. Observation of evolution produces Knowledge. Knowledge enables
Prediction. Prediction enables Decision.

R0.2.0: Concrete implementations with full support for validation, serialization,
metadata, and object protocol methods.
"""

from quantsmind.foundation.attribute import Attribute
from quantsmind.foundation.behaviour import Behaviour
from quantsmind.foundation.constraint import Constraint
from quantsmind.foundation.entity import Entity
from quantsmind.foundation.event import Event
from quantsmind.foundation.factories import (
    ConstraintFactory,
    EntityFactory,
    RelationshipFactory,
    StateFactory,
    SystemFactory,
)
from quantsmind.foundation.identity import Identity
from quantsmind.foundation.interaction import Interaction
from quantsmind.foundation.knowledge import Knowledge
from quantsmind.foundation.lifecycle import Lifecycle
from quantsmind.foundation.observation import Observation
from quantsmind.foundation.property import Property
from quantsmind.foundation.relationship import Relationship
from quantsmind.foundation.serializers import JSONSerializer, Serializer
from quantsmind.foundation.space import Space
from quantsmind.foundation.state import State
from quantsmind.foundation.system import System
from quantsmind.foundation.time import Time
from quantsmind.foundation.transformation import Transformation
from quantsmind.foundation.validators import (
    Validator,
    validate_all,
    validate_custom,
    validate_non_negative,
    validate_not_none,
    validate_positive,
    validate_range,
    validate_string_length,
    validate_type,
)

__all__ = [
    # Core ontology
    "Identity",
    "Property",
    "Attribute",
    "Entity",
    "System",
    # State and context
    "State",
    "Space",
    "Time",
    # Entity behavior
    "Behaviour",
    "Relationship",
    "Constraint",
    # Evolution
    "Lifecycle",
    "Event",
    "Transformation",
    # Knowledge
    "Observation",
    "Knowledge",
    # Interactions
    "Interaction",
    # Support modules
    "validate_type",
    "validate_range",
    "validate_string_length",
    "validate_not_none",
    "validate_positive",
    "validate_non_negative",
    "validate_custom",
    "validate_all",
    "Validator",
    "Serializer",
    "JSONSerializer",
    "EntityFactory",
    "SystemFactory",
    "StateFactory",
    "RelationshipFactory",
    "ConstraintFactory",
]
