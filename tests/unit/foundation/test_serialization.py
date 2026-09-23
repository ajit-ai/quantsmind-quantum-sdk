"""Unit tests for Serializable conformance of foundation value objects.

Regression cover for the Liskov fixes: concrete classes must accept the
``SerializationFormat`` enum (and plain ``"json"`` for backward
compatibility), round-trip through bytes, and report enum formats.
"""

from __future__ import annotations

from typing import Any

import pytest

from quantsmind.foundation.enums import SerializationFormat
from quantsmind.foundation.identity import Identity
from quantsmind.foundation.transformation import Transformation


def _scale_rule(context: dict[str, Any]) -> tuple[bool, Any, list[str]]:
    return (True, context.get("value", 0) * 2, [])


class TestTransformationSerialization:
    def test_roundtrip_with_enum_default(self) -> None:
        transform = Transformation(name="scale", rule=_scale_rule)
        data = transform.serialize()
        assert isinstance(data, bytes)
        rebuilt = Transformation.deserialize(data)
        assert rebuilt.name == "scale"

    def test_plain_json_string_accepted(self) -> None:
        transform = Transformation(name="scale", rule=_scale_rule)
        data = transform.serialize(format="json")
        rebuilt = Transformation.deserialize(data, format="json")
        assert rebuilt.name == "scale"

    def test_supported_formats_are_enums(self) -> None:
        assert Transformation.get_supported_formats() == [SerializationFormat.JSON]

    def test_unsupported_format_raises(self) -> None:
        transform = Transformation(name="scale", rule=_scale_rule)
        with pytest.raises(NotImplementedError):
            transform.serialize(format=SerializationFormat.YAML)


class TestIdentitySerialization:
    def test_roundtrip_preserves_id(self) -> None:
        identity = Identity(namespace="quantum")
        data = identity.serialize()
        rebuilt = Identity.deserialize(data)
        assert rebuilt.id == identity.id

    def test_timestamps_stay_naive(self) -> None:
        # Naive-preserving utcnow() replacement: no tzinfo attached.
        identity = Identity()
        assert identity._created_at.tzinfo is None

    def test_supported_formats_are_enums(self) -> None:
        assert Identity.get_supported_formats() == [SerializationFormat.JSON]
