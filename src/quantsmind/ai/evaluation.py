"""Response evaluation metrics.

Deterministic, reference-based scores for model outputs: exact match
and token F1. No model calls happen here.
"""

from __future__ import annotations

__all__ = [
    "exact_match",
    "token_f1",
]


def _tokens(text: str) -> list[str]:
    return text.lower().split()


def exact_match(prediction: str, reference: str) -> float:
    """1.0 for exact match after stripping, else 0.0."""
    return 1.0 if prediction.strip() == reference.strip() else 0.0


def token_f1(prediction: str, reference: str) -> float:
    """Token-level F1 between whitespace-tokenized strings."""
    predicted = _tokens(prediction)
    expected = _tokens(reference)
    if not predicted and not expected:
        return 1.0
    if not predicted or not expected:
        return 0.0
    shared = 0
    remaining = list(expected)
    for token in predicted:
        if token in remaining:
            shared += 1
            remaining.remove(token)
    if shared == 0:
        return 0.0
    precision = shared / len(predicted)
    recall = shared / len(expected)
    return 2.0 * precision * recall / (precision + recall)
