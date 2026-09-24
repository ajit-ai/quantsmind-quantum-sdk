"""Unit tests for quantsmind.api request models (optional extra)."""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

from pydantic import ValidationError

from quantsmind.api.models import MatrixRequest, PolynomialRequest


class TestPolynomialRequest:
    def test_valid(self) -> None:
        request = PolynomialRequest(coefficients=[1, 0, -4], operation="evaluate", x=2)
        assert request.coefficients == [1.0, 0.0, -4.0]
        assert request.operation == "evaluate"

    def test_bad_operation(self) -> None:
        with pytest.raises(ValidationError):
            PolynomialRequest(coefficients=[1.0], operation="teleport")


class TestMatrixRequest:
    def test_valid(self) -> None:
        request = MatrixRequest(data=[[1.0, 2.0], [3.0, 4.0]], operation="determinant")
        assert request.data == [[1.0, 2.0], [3.0, 4.0]]
