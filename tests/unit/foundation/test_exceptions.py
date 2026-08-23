"""Unit tests for the SDK-wide and foundation exception hierarchies."""

from __future__ import annotations

import pytest

from quantsmind.exceptions import QuantsMindError
from quantsmind.foundation.exceptions import (
    EntityNotFoundError,
    FoundationError,
    FoundationTypeError,
    InvalidObservationError,
    InvalidSystemError,
    ObservationError,
    SystemError,
    TransformationError,
    TransformationExecutionError,
)


class TestQuantsMindError:
    """The SDK base exception carries message, details, and error codes."""

    def test_is_an_exception(self) -> None:
        assert issubclass(QuantsMindError, Exception)

    def test_message_only(self) -> None:
        err = QuantsMindError("boom")
        assert err.message == "boom"
        assert err.details == {}
        assert err.error_code is None
        assert str(err) == "boom"

    def test_details_and_error_code(self) -> None:
        err = QuantsMindError("bad input", details={"op": "solve"}, error_code="QM-042")
        assert err.details == {"op": "solve"}
        assert str(err) == "[QM-042] bad input"

    def test_catchable_as_base(self) -> None:
        with pytest.raises(QuantsMindError):
            raise FoundationError("foundation failure")


class TestFoundationHierarchy:
    """Foundation exceptions root at QuantsMindError via FoundationError."""

    def test_foundation_error_inherits_sdk_base(self) -> None:
        assert issubclass(FoundationError, QuantsMindError)

    @pytest.mark.parametrize(
        ("exc_cls", "parent"),
        [
            (EntityNotFoundError, SystemError),
            (InvalidSystemError, SystemError),
            (InvalidObservationError, ObservationError),
            (TransformationExecutionError, TransformationError),
            (FoundationTypeError, FoundationError),
        ],
    )
    def test_leaf_exceptions_inherit_expected_parents(
        self, exc_cls: type[Exception], parent: type[Exception]
    ) -> None:
        assert issubclass(exc_cls, parent)
        assert issubclass(exc_cls, QuantsMindError)

    def test_foundation_error_to_dict(self) -> None:
        err = FoundationError("failed", details={"ctx": 1}, error_code="F-1")
        payload = err.to_dict()
        assert payload["error_type"] == "FoundationError"
        assert payload["message"] == "failed"
        assert payload["details"] == {"ctx": 1}
        assert payload["error_code"] == "F-1"
