"""Deterministic data-quality assessment of the Data Intelligence layer.

:func:`assess_data_quality` produces a :class:`DataQualityReport` with
exact counts for missing values, invalid (non-finite / out-of-bounds)
values, duplicate rows and feature-consistency across records.  The report
is JSON-safe and deterministic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.data._validation import sorted_issues
from quantsmind.quantum.data.models import DataSet

__all__ = ["DataQualityReport", "assess_data_quality"]


@dataclass
class DataQualityReport:
    """Deterministic quality assessment of one dataset.

    Args:
        valid: Whether the dataset is structurally valid (non-empty, no
            missing/invalid/duplicate entries, feature-consistent records).
        record_count: Number of records.
        feature_count: Number of features.
        missing_count: Number of missing (absent) feature values.
        invalid_count: Number of non-finite or out-of-bounds values.
        duplicate_count: Number of records identical to an earlier record.
        feature_consistency: Whether every record carries exactly the dataset
            feature set.
        issues: Deterministic, human-readable issue list.
        metadata: Free-form metadata (JSON-safe).
    """

    valid: bool = False
    record_count: int = 0
    feature_count: int = 0
    missing_count: int = 0
    invalid_count: int = 0
    duplicate_count: int = 0
    feature_consistency: bool = False
    issues: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "valid": bool(self.valid),
            "record_count": int(self.record_count),
            "feature_count": int(self.feature_count),
            "missing_count": int(self.missing_count),
            "invalid_count": int(self.invalid_count),
            "duplicate_count": int(self.duplicate_count),
            "feature_consistency": bool(self.feature_consistency),
            "issues": list(self.issues),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataQualityReport:
        """Rebuild a report from :meth:`to_dict` output."""
        return cls(
            valid=bool(data.get("valid", False)),
            record_count=int(data.get("record_count", 0)),
            feature_count=int(data.get("feature_count", 0)),
            missing_count=int(data.get("missing_count", 0)),
            invalid_count=int(data.get("invalid_count", 0)),
            duplicate_count=int(data.get("duplicate_count", 0)),
            feature_consistency=bool(data.get("feature_consistency", False)),
            issues=[str(issue) for issue in data.get("issues", [])],
            metadata=dict(data.get("metadata", {})),
        )


def assess_data_quality(dataset: DataSet) -> DataQualityReport:
    """Assess ``dataset`` quality and return a deterministic report.

    Missing values, invalid values (non-finite or outside the feature bounds
    when bounds are supplied) and duplicate rows are counted exactly.
    Duplicates are rows with identical values across the deterministic
    feature order; the first occurrence is kept and every later identical
    occurrence is counted.
    """
    issues = list(dataset.validate())
    record_count = len(dataset.records)
    feature_count = len(dataset.features)

    missing_count = 0
    invalid_count = 0
    for record in dataset.records:
        for feature in dataset.features:
            value = record.values.get(feature.name)
            if value is None:
                missing_count += 1
            else:
                number = float(value)
                if not math.isfinite(number) or not feature.allows(number):
                    invalid_count += 1

    feature_consistency = True
    if dataset.features and dataset.records:
        expected = set(dataset.feature_names)
        for record in dataset.records:
            if set(record.values) != expected:
                feature_consistency = False
                break
    else:
        feature_consistency = False

    duplicate_count = 0
    if dataset.features and dataset.records:
        seen: set[tuple[float, ...]] = set()
        for record in dataset.records:
            key = tuple(
                float(record.values.get(feature.name, float("nan"))) for feature in dataset.features
            )
            if key in seen:
                duplicate_count += 1
            else:
                seen.add(key)

    if not feature_consistency:
        issues.append("records do not carry a consistent feature set")
    if missing_count:
        issues.append(f"{missing_count} missing value(s)")
    if invalid_count:
        issues.append(f"{invalid_count} invalid value(s)")
    if duplicate_count:
        duplicate_ids: list[str] = []
        seen_rows: set[tuple[float, ...]] = set()
        for record in dataset.records:
            key = tuple(
                float(record.values.get(feature.name, float("nan"))) for feature in dataset.features
            )
            if key in seen_rows:
                duplicate_ids.append(record.record_id)
            else:
                seen_rows.add(key)
        issues.append(f"{duplicate_count} duplicate record(s): " + ", ".join(sorted(duplicate_ids)))

    valid = bool(
        record_count > 0
        and feature_count > 0
        and feature_consistency
        and missing_count == 0
        and invalid_count == 0
        and duplicate_count == 0
    )

    return DataQualityReport(
        valid=valid,
        record_count=record_count,
        feature_count=feature_count,
        missing_count=missing_count,
        invalid_count=invalid_count,
        duplicate_count=duplicate_count,
        feature_consistency=feature_consistency,
        issues=sorted_issues(issues),
    )
