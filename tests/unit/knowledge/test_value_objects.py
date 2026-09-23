"""Unit tests for knowledge value objects and package surface."""

from __future__ import annotations

from quantsmind.knowledge.constants import SDK_VERSION
from quantsmind.knowledge.enums import (
    ProvenanceType,
    ReasoningType,
    RepositoryType,
    ValidationType,
)
from quantsmind.knowledge.exceptions import (
    KnowledgeError,
    ObservationError,
    SchemaError,
)
from quantsmind.knowledge.types import SearchResult
from quantsmind.knowledge.validation.validators import KnowledgeValidator


class TestEnums:
    def test_added_members_exist(self) -> None:
        assert ProvenanceType.DATASET.value == "dataset"
        assert ReasoningType.PREDICTION.value == "prediction"
        assert ReasoningType.EXPLANATION.value == "explanation"
        assert RepositoryType.MEMORY.value == "memory"
        assert ValidationType.TYPE.value == "type"


class TestTypes:
    def test_search_result_dataclass(self) -> None:
        result = SearchResult("d1", 0.9, {"text": "hi"})
        assert result.doc_id == "d1"
        assert result.score == 0.9


class TestValidators:
    def test_knowledge_validator_defaults(self) -> None:
        validator = KnowledgeValidator()
        valid, errors = validator.validate({})
        assert valid is True
        assert errors == []


class TestExceptions:
    def test_context_in_message(self) -> None:
        error = KnowledgeError("boom", {"k": "v"})
        assert "boom" in str(error)
        assert isinstance(ObservationError("o"), KnowledgeError)
        assert isinstance(SchemaError("s"), KnowledgeError)


class TestConstants:
    def test_sdk_version_matches_package(self) -> None:
        import quantsmind

        assert quantsmind.__version__ == SDK_VERSION
