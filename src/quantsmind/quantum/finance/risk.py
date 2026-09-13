"""Risk representation of the Finance domain layer.

:class:`RiskMatrix` is a validated covariance/risk matrix over a
deterministic asset order.  QMQ-07 validates structure (dimensions, finite
entries, symmetry, positive semidefiniteness) but deliberately does **not**
implement statistical estimation — supplied data only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.finance.errors import FinanceError, FinanceValidationError

__all__ = ["RiskMatrix"]

# Symmetry tolerance for covariance matrices.
_SYMMETRY_TOLERANCE = 1e-9
# Largest matrix size for the exact (dependency-free) PSD principal-minor check.
_PRINCIPAL_MINOR_CAP = 14


def _determinant(submatrix: list[list[float]]) -> float:
    """Determinant of a small matrix via Gaussian elimination with pivoting."""
    n = len(submatrix)
    work = [list(row) for row in submatrix]
    sign = 1.0
    for col in range(n):
        pivot = col
        while pivot < n and work[pivot][col] == 0.0:
            pivot += 1
        if pivot == n:
            return 0.0
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            sign = -sign
        pivot_value = work[col][col]
        for row in range(col + 1, n):
            factor = work[row][col] / pivot_value
            for j in range(col, n):
                work[row][j] -= factor * work[col][j]
    determinant = sign
    for index in range(n):
        determinant *= work[index][index]
    return determinant


def _principal_minors_nonnegative(matrix: list[list[float]], tolerance: float) -> bool:
    """Return whether every principal minor is ``>= -tolerance`` (PSD)."""
    n = len(matrix)
    for mask in range(1, 1 << n):
        indices = [i for i in range(n) if mask & (1 << i)]
        sub = [[matrix[row][col] for col in indices] for row in indices]
        if _determinant(sub) < -tolerance:
            return False
    return True


def _check_psd(matrix: list[list[float]], tolerance: float) -> tuple[bool, bool]:
    """Return ``(is_psd, validated)``.

    Uses numpy when available (exact eigendecomposition); otherwise an exact
    principal-minor enumeration for matrices up to
    :data:`_PRINCIPAL_MINOR_CAP` rows.  Larger dependency-free matrices are
    reported as ``(False, False)`` to be flagged rather than silently assumed.
    """
    try:
        import numpy as np

        values = np.linalg.eigvalsh(np.asarray(matrix, dtype=float))
        return bool(np.all(values >= -tolerance)), True
    except ImportError:
        pass
    n = len(matrix)
    if n > _PRINCIPAL_MINOR_CAP:
        return False, False
    return _principal_minors_nonnegative(matrix, tolerance), True


@dataclass
class RiskMatrix:
    """A covariance/risk matrix over a deterministic asset order.

    Args:
        asset_order: Ordered asset identifiers the matrix rows/columns map to.
        matrix: Covariance matrix (``n x n``); must be square, finite, and
            symmetric within :data:`_SYMMETRY_TOLERANCE` (values are
            normalized to exact symmetry).
        volatilities: Optional per-asset volatility (standard deviation),
            aligned with ``asset_order``.

    Raises:
        FinanceValidationError: On structural or numerical invalidity, or a
            confirmed non-PSD matrix (only when the PSD check is conclusive).

    Attributes:
        psd_validated: Whether the positive-semidefinite check was conclusive.
        psd: Whether the matrix is positive semidefinite (False when the
            check was inconclusive).
    """

    asset_order: list[str]
    matrix: list[list[float]]
    volatilities: list[float | None] | None = None
    psd_validated: bool = field(default=False, repr=False, compare=False)
    psd: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        order = [str(x) for x in self.asset_order]
        if not order:
            raise FinanceValidationError("asset_order must contain at least one identifier")
        if len(set(order)) != len(order):
            raise FinanceValidationError("asset_order contains duplicate identifiers")
        n = len(order)
        if len(self.matrix) != n:
            raise FinanceValidationError(
                f"risk matrix has {len(self.matrix)} rows but asset_order lists {n} assets"
            )
        for index, row in enumerate(self.matrix):
            if len(row) != n:
                raise FinanceValidationError(
                    f"risk matrix row {index} has {len(row)} columns; expected {n}"
                )
            for entry in row:
                if not math.isfinite(entry):
                    raise FinanceValidationError("risk matrix entries must be finite")
        for i in range(n):
            for j in range(i):
                difference = abs(self.matrix[i][j] - self.matrix[j][i])
                if difference > _SYMMETRY_TOLERANCE:
                    raise FinanceValidationError(
                        "risk matrix is not symmetric "
                        f"(|m[{i}][{j}] - m[{j}][{i}]| = {difference:.3g})"
                    )
        normalized = [list(row) for row in self.matrix]
        for i in range(n):
            for j in range(i + 1, n):
                average = (normalized[i][j] + normalized[j][i]) / 2.0
                normalized[i][j] = average
                normalized[j][i] = average
        self.matrix = normalized
        if self.volatilities is not None:
            if len(self.volatilities) != n:
                raise FinanceValidationError(
                    f"volatilities list has {len(self.volatilities)} values; "
                    f"expected {n} matching asset_order"
                )
            for index, value in enumerate(self.volatilities):
                if value is None:
                    continue
                if not math.isfinite(value) or value < 0.0:
                    raise FinanceValidationError(
                        f"volatility of asset {order[index]!r} must be a finite "
                        f"value >= 0, got {value!r}"
                    )
        is_psd, validated = _check_psd(normalized, _SYMMETRY_TOLERANCE)
        self.psd_validated = validated
        self.psd = is_psd
        if validated and not is_psd:
            raise FinanceValidationError(
                "risk matrix must be positive semidefinite (a covariance "
                "matrix cannot have negative eigenvalues)"
            )

    def require_psd(self) -> None:
        """Raise when the matrix is not confirmed positive semidefinite.

        Raises:
            FinanceError: If the matrix fails the PSD requirement (including
                an inconclusive check, which is reported rather than assumed).
        """
        if not self.psd:
            when = (
                "is not positive semidefinite"
                if self.psd_validated
                else ("could not be conclusively validated as positive semidefinite")
            )
            raise FinanceError(f"risk matrix {when} over {len(self.asset_order)} assets")

    # -- lookups ---------------------------------------------------------

    def index(self, identifier: str) -> int:
        """Return the row/column index of an asset identifier."""
        if identifier not in self.asset_order:
            raise KeyError(f"asset {identifier!r} not in risk matrix")
        return self.asset_order.index(identifier)

    def covariance(self, left: str, right: str) -> float:
        """Return the covariance entry between two assets."""
        return float(self.matrix[self.index(left)][self.index(right)])

    def variance(self, identifier: str) -> float:
        """Return the variance (diagonal entry) of an asset."""
        index = self.index(identifier)
        return float(self.matrix[index][index])

    def correlation(self) -> list[list[float]]:
        """Return the correlation matrix derived from this covariance matrix.

        Raises:
            FinanceError: If volatilities are missing or contain zeros.
        """
        if self.volatilities is None:
            raise FinanceError("correlation requires per-asset volatilities to be supplied")
        sigmas: list[float] = []
        for identifier, value in zip(self.asset_order, self.volatilities, strict=True):
            if value is None or value <= 0.0:
                raise FinanceError(
                    f"correlation requires a positive volatility for asset {identifier!r}"
                )
            sigmas.append(float(value))
        n = len(self.asset_order)
        correlation: list[list[float]] = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                correlation[i][j] = self.matrix[i][j] / (sigmas[i] * sigmas[j])
        return correlation

    # -- serialization ---------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "asset_order": list(self.asset_order),
            "matrix": [[float(value) for value in row] for row in self.matrix],
            "volatilities": list(self.volatilities) if self.volatilities is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RiskMatrix:
        """Rebuild a RiskMatrix from :meth:`to_dict` output."""
        raw_volatilities = data.get("volatilities")
        return cls(
            asset_order=[str(x) for x in data.get("asset_order", [])],
            matrix=[[float(value) for value in row] for row in data.get("matrix", [])],
            volatilities=(
                [None if v is None else float(v) for v in raw_volatilities]
                if raw_volatilities is not None
                else None
            ),
        )
