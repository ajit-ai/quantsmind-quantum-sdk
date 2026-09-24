"""Unit tests for the SDK exception hierarchy."""

from __future__ import annotations

import pytest

from quantsmind.exceptions import QuantsMindError
from quantsmind.providers import ProviderError


class TestHierarchy:
    def test_message_details_code(self) -> None:
        error = QuantsMindError("boom", details={"op": "solve"}, error_code="E1")
        assert error.message == "boom"
        assert error.details == {"op": "solve"}
        assert str(error) == "[E1] boom"

    def test_package_errors_share_base(self) -> None:
        assert issubclass(ProviderError, QuantsMindError)
        with pytest.raises(QuantsMindError):
            raise ProviderError("provider down")
