"""Unit tests for quantsmind.foundation.entity."""

from __future__ import annotations

from quantsmind.foundation.entity import Entity
from quantsmind.foundation.enums import EntityType


class TestEntity:
    """The atomic unit of the ontology must instantiate and identify itself."""

    def test_default_construction(self) -> None:
        entity = Entity()
        assert entity is not None
        assert entity.entity_type == EntityType.GENERIC

    def test_identity_is_unique_per_entity(self) -> None:
        a, b = Entity(), Entity()
        assert a.identity is not b.identity
        assert a.identity.id != b.identity.id

    def test_explicit_entity_type(self) -> None:
        entity = Entity(entity_type=EntityType.QUANTUM)
        assert entity.entity_type == EntityType.QUANTUM
