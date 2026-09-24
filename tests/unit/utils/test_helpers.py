"""Unit tests for quantsmind.utils helpers."""

from __future__ import annotations

import pytest

from quantsmind.utils import (
    chunk_list,
    clamp,
    flatten_list,
    format_number,
    is_close,
    safe_division,
    unique_preserve_order,
    validate_type,
)


class TestHelpers:
    def test_clamp(self) -> None:
        assert clamp(5, 0, 10) == 5
        assert clamp(-1, 0, 10) == 0
        assert clamp(11, 0, 10) == 10

    def test_safe_division(self) -> None:
        assert safe_division(1.0, 2.0) == 0.5
        assert safe_division(1.0, 0.0) == 0.0

    def test_is_close(self) -> None:
        assert is_close(1.0, 1.0 + 1e-10) is True
        assert is_close(1.0, 2.0) is False

    def test_lists(self) -> None:
        assert chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
        assert flatten_list([[1, 2], [3]]) == [1, 2, 3]
        assert unique_preserve_order([3, 1, 3, 2, 1]) == [3, 1, 2]

    def test_format_and_validate(self) -> None:
        assert format_number(3.14159, 2) == "3.14"
        assert validate_type(5, int) == 5
        with pytest.raises(TypeError):
            validate_type("x", int)
