"""API models: validated polynomial and matrix requests.

Feature: pydantic models from ``quantsmind.api`` (needs `pydantic>=2`).
Purpose: show request validation without running a server.
Input: coefficients [1, 0, -4] with "evaluate"; a 2x2 matrix.
Processing: model construction with operation whitelists.
Output: dumped payloads plus one rejected bad operation.
Meaning: invalid requests fail fast at the boundary.

Run from the repository root::

    python examples/api/request_models.py
"""

from __future__ import annotations

from quantsmind.api.models import MatrixRequest, PolynomialRequest


def main() -> None:
    poly = PolynomialRequest(coefficients=[1, 0, -4], operation="evaluate", x=2)
    print(f"poly: {poly.model_dump()}")
    matrix = MatrixRequest(data=[[1, 2], [3, 4]], operation="determinant")
    print(f"matrix op: {matrix.operation}")
    try:
        PolynomialRequest(coefficients=[1.0], operation="teleport")
    except Exception as exc:
        print(f"rejected: {type(exc).__name__}")


if __name__ == "__main__":
    main()
