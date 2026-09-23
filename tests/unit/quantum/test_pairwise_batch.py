"""Oracle tests for the batch pairwise distance fast path (9-A, stdlib only).

The batch helper must agree bitwise with the per-pair functions (same
float operations in the same order) and raise the same error type for
bad input. No NumPy is involved anywhere on this path.
"""

from __future__ import annotations

import pytest

from quantsmind.quantum.data.errors import DataValidationError
from quantsmind.quantum.data.examples import dataset_example
from quantsmind.quantum.data.numerics import (
    euclidean_distance,
    pairwise_distance_matrix,
    squared_euclidean_distance,
    weighted_squared_euclidean_distance,
)
from quantsmind.quantum.data.relationship import pairwise_relationship

VECTORS = [
    [1.0, 2.0, 3.0, 4.0],
    [0.5, -1.0, 2.5, 0.0],
    [4.0, 3.0, 2.0, 1.0],
    [0.0, 0.0, 0.0, 1.0],
]
WEIGHTS = [1.0, 0.5, 2.0, 1.5]


class TestBatchMatchesPerPair:
    def test_euclidean_exact(self) -> None:
        matrix = pairwise_distance_matrix(VECTORS, metric="euclidean")
        for i, left in enumerate(VECTORS):
            for j, right in enumerate(VECTORS):
                assert matrix[i][j] == euclidean_distance(left, right)

    def test_squared_exact(self) -> None:
        matrix = pairwise_distance_matrix(VECTORS, metric="squared_euclidean")
        for i, left in enumerate(VECTORS):
            for j, right in enumerate(VECTORS):
                assert matrix[i][j] == squared_euclidean_distance(left, right)

    def test_weighted_exact(self) -> None:
        matrix = pairwise_distance_matrix(
            VECTORS, metric="weighted_euclidean", weights=WEIGHTS
        )
        for i, left in enumerate(VECTORS):
            for j, right in enumerate(VECTORS):
                assert matrix[i][j] == weighted_squared_euclidean_distance(left, right, WEIGHTS)

    def test_symmetric_and_zero_diagonal(self) -> None:
        matrix = pairwise_distance_matrix(VECTORS)
        size = len(VECTORS)
        for i in range(size):
            assert matrix[i][i] == 0.0
            for j in range(size):
                assert matrix[i][j] == matrix[j][i]

    def test_deterministic(self) -> None:
        assert pairwise_distance_matrix(VECTORS) == pairwise_distance_matrix(VECTORS)


class TestBatchErrors:
    def test_empty_input(self) -> None:
        with pytest.raises(DataValidationError):
            pairwise_distance_matrix([])

    def test_ragged_vectors(self) -> None:
        with pytest.raises(DataValidationError):
            pairwise_distance_matrix([[1.0, 2.0], [1.0]])

    def test_non_finite(self) -> None:
        with pytest.raises(DataValidationError):
            pairwise_distance_matrix([[1.0, float("inf")]])

    def test_negative_weights(self) -> None:
        with pytest.raises(DataValidationError):
            pairwise_distance_matrix(
                VECTORS, metric="weighted_euclidean", weights=[-1.0, 0.5, 2.0, 1.5]
            )

    def test_missing_weights(self) -> None:
        with pytest.raises(DataValidationError):
            pairwise_distance_matrix(VECTORS, metric="weighted_euclidean")

    def test_unknown_metric(self) -> None:
        with pytest.raises(DataValidationError):
            pairwise_distance_matrix(VECTORS, metric="manhattan")


class TestRelationshipUsesBatch:
    def test_example_dataset_stays_symmetric(self) -> None:
        dataset = dataset_example()
        for metric in ("euclidean", "squared_euclidean"):
            rel = pairwise_relationship(dataset, metric=metric)
            values = rel.values
            size = len(values)
            assert size > 0
            for i in range(size):
                assert values[i][i] == 0.0
                for j in range(size):
                    assert values[i][j] == values[j][i]

    def test_similarity_kind_bounded(self) -> None:
        dataset = dataset_example()
        rel = pairwise_relationship(dataset, kind="similarity")
        for row in rel.values:
            for value in row:
                assert 0.0 < value <= 1.0
