"""Unit tests for quantsmind.foundation.enums."""

from __future__ import annotations

import pytest

from quantsmind.foundation.enums import (
    EntityType,
    EventType,
    InteractionType,
    KnowledgeType,
    LifecycleStage,
    ObservationQuality,
    ObservationType,
    RelationshipType,
    SerializationFormat,
    SystemType,
    TransformationType,
)


class TestEntityType:
    """EntityType covers the entity classifications used across packages."""

    def test_has_core_members(self) -> None:
        assert {m.name for m in EntityType} >= {"GENERIC", "PHYSICAL", "QUANTUM"}

    def test_generic_is_available(self) -> None:
        assert EntityType.GENERIC is not None


class TestSystemAndInteractionTypes:
    """SystemType and InteractionType were restored in M0.2."""

    @pytest.mark.parametrize("member", ["GENERIC", "PHYSICAL", "QUANTUM", "BIOLOGICAL"])
    def test_system_type_members(self, member: str) -> None:
        assert member in SystemType.__members__

    def test_interaction_collision(self) -> None:
        assert InteractionType.COLLISION is not None

    def test_observation_measurement(self) -> None:
        assert ObservationType.MEASUREMENT is not None


class TestKnowledgeType:
    """KnowledgeType includes descriptive and predictive categories."""

    @pytest.mark.parametrize("member", ["FACT", "RULE", "MODEL", "DESCRIPTIVE", "PREDICTIVE"])
    def test_members(self, member: str) -> None:
        assert member in KnowledgeType.__members__


class TestLifecycleStage:
    """LifecycleStage includes evolving/disposed stages used by transitions."""

    @pytest.mark.parametrize(
        "member",
        ["CREATED", "ACTIVATED", "EVOLVING", "DISPOSED", "DESTROYED"],
    )
    def test_members(self, member: str) -> None:
        assert member in LifecycleStage.__members__


class TestTransformationType:
    """TransformationType includes composed transformations."""

    @pytest.mark.parametrize("member", ["LINEAR", "NONLINEAR", "STOCHASTIC", "COMPOSED", "CUSTOM"])
    def test_members(self, member: str) -> None:
        assert member in TransformationType.__members__


class TestEventAndMiscEnums:
    """Sanity checks on remaining foundation enums."""

    def test_state_changed_event_exists(self) -> None:
        # STATE_CHANGED (not STATE_CHANGE) is canonical — see M0.2 fix.
        assert "STATE_CHANGED" in EventType.__members__
        assert "STATE_CHANGE" not in EventType.__members__

    def test_serialization_text_formats(self) -> None:
        assert SerializationFormat.JSON.is_text_based()
        assert not SerializationFormat.BINARY.is_text_based()

    @pytest.mark.parametrize(
        "enum_cls",
        [EntityType, EventType, ObservationQuality, RelationshipType],
    )
    def test_enums_are_non_empty(self, enum_cls: type) -> None:
        assert len(enum_cls) > 0
