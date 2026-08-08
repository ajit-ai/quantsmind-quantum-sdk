"""
Knowledge Module

This module provides structured information derived from observations within the QuantsMind SDK.
Knowledge represents structured information derived from observations, usable for prediction.

Purpose
-------
Provide structured information for entities and systems in the Foundation package.

Scientific Meaning
------------------
Knowledge represents structured information: physical laws, quantum state information,
chemical reaction knowledge, biological knowledge, financial market knowledge.

Responsibilities
----------------
- Manage knowledge data
- Support knowledge derivation
- Enable knowledge serialization
- Handle knowledge validation
- Support knowledge queries

Dependencies
------------
typing (standard library)
logging (standard library)
datetime (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.enums (enumeration types)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Knowledge learning
- Knowledge inference
- Distributed knowledge sharing
- Knowledge versioning
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from quantsmind.foundation.constants import DEFAULT_KNOWLEDGE_TYPE
from quantsmind.foundation.enums import KnowledgeType
from quantsmind.foundation.exceptions import (
    InvalidKnowledgeError,
    KnowledgeError,
)
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation.types import (
    MetadataDict,
    SerializedData,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Knowledge(Serializable, Validatable):
    """Concrete implementation of structured information derived from observations.

    This class provides a flexible knowledge representation with support for
    various knowledge types, derivation sources, and validation.

    Scientific Meaning
    ------------------
    In scientific computing, knowledge represents structured information:
    physical laws, quantum state information, chemical reaction knowledge,
    biological knowledge, financial market knowledge.

    Attributes:
        _id: Unique knowledge identifier
        _knowledge_type: Type of knowledge
        _data: Knowledge data
        _sources: List of source observation IDs
        _confidence: Confidence level
        _metadata: Additional metadata

    Example:
        >>> knowledge = Knowledge(knowledge_type=KnowledgeType.PREDICTIVE, data={"model": "linear"})
        >>> print(f"Knowledge: {knowledge.knowledge_type}")
    """

    def __init__(
        self,
        knowledge_type: KnowledgeType = KnowledgeType.DESCRIPTIVE,
        data: Optional[Dict[str, Any]] = None,
        sources: Optional[List[str]] = None,
        confidence: Optional[float] = None,
        metadata: Optional[MetadataDict] = None,
    ) -> None:
        """Initialize a Knowledge.

        Args:
            knowledge_type: Type of knowledge
            data: Knowledge data dictionary
            sources: List of source observation IDs
            confidence: Optional confidence level (0-1)
            metadata: Optional metadata dictionary

        Raises:
            InvalidKnowledgeError: If confidence is out of range

        Example:
            >>> knowledge = Knowledge(knowledge_type=KnowledgeType.PREDICTIVE, data={"model": "linear"})
        """
        self._id: str = str(uuid.uuid4())
        self._knowledge_type: KnowledgeType = knowledge_type
        self._data: Dict[str, Any] = data or {}
        self._sources: List[str] = sources or []
        self._confidence: Optional[float] = confidence
        self._metadata: MetadataDict = metadata or {}

        self._validate_confidence()
        logger.debug(f"Created knowledge: {knowledge_type.value}")

    def _validate_confidence(self) -> None:
        """Validate the confidence level.

        Raises:
            InvalidKnowledgeError: If confidence is out of range
        """
        if self._confidence is not None and (self._confidence < 0 or self._confidence > 1):
            raise InvalidKnowledgeError("Confidence must be between 0 and 1")

    @property
    def id(self) -> str:
        """Get the knowledge ID.

        Returns:
            Knowledge ID

        Example:
            >>> print(f"ID: {knowledge.id}")
        """
        return self._id

    @property
    def knowledge_type(self) -> KnowledgeType:
        """Get the knowledge type.

        Returns:
            Knowledge type

        Example:
            >>> print(f"Type: {knowledge.knowledge_type}")
        """
        return self._knowledge_type

    @property
    def data(self) -> Dict[str, Any]:
        """Get the knowledge data.

        Returns:
            Knowledge data dictionary

        Example:
            >>> print(f"Data: {knowledge.data}")
        """
        return self._data.copy()

    @property
    def sources(self) -> List[str]:
        """Get the source observation IDs.

        Returns:
            List of source IDs

        Example:
            >>> print(f"Sources: {knowledge.sources}")
        """
        return self._sources.copy()

    @property
    def confidence(self) -> Optional[float]:
        """Get the confidence level.

        Returns:
            Confidence level or None

        Example:
            >>> print(f"Confidence: {knowledge.confidence}")
        """
        return self._confidence

    @property
    def metadata(self) -> MetadataDict:
        """Get the knowledge metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {knowledge.metadata}")
        """
        return self._metadata.copy()

    @property
    def has_confidence(self) -> bool:
        """Check if knowledge has confidence level.

        Returns:
            True if has confidence, False otherwise

        Example:
            >>> if knowledge.has_confidence:
            ...     print(f"Confidence: {knowledge.confidence}")
        """
        return self._confidence is not None

    def add_source(self, source_id: str) -> None:
        """Add a source observation ID.

        Args:
            source_id: Source observation ID

        Example:
            >>> knowledge.add_source("observation_123")
        """
        if source_id not in self._sources:
            self._sources.append(source_id)
            logger.debug(f"Added source: {source_id}")

    def set_data(self, key: str, value: Any) -> None:
        """Set knowledge data.

        Args:
            key: Data key
            value: Data value

        Example:
            >>> knowledge.set_data("model", "linear")
        """
        self._data[key] = value
        logger.debug(f"Updated knowledge data: {key} = {value}")

    def set_confidence(self, confidence: float) -> None:
        """Set the confidence level.

        Args:
            confidence: New confidence level

        Raises:
            InvalidKnowledgeError: If confidence is out of range

        Example:
            >>> knowledge.set_confidence(0.95)
        """
        old_confidence = self._confidence
        self._confidence = confidence
        try:
            self._validate_confidence()
            logger.debug(f"Updated confidence: {old_confidence} -> {confidence}")
        except InvalidKnowledgeError:
            self._confidence = old_confidence
            raise

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the knowledge to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = knowledge.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "id": self._id,
            "type": self._knowledge_type.value,
            "data": self._data,
            "sources": self._sources,
            "confidence": self._confidence,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> "Knowledge":
        """Deserialize the knowledge from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Knowledge instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidKnowledgeError: If data is invalid

        Example:
            >>> knowledge = Knowledge.deserialize(data, format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            return cls(
                knowledge_type=KnowledgeType(obj["type"]),
                data=obj.get("data"),
                sources=obj.get("sources"),
                confidence=obj.get("confidence"),
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidKnowledgeError(f"Failed to deserialize knowledge: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the knowledge is serializable.

        Returns:
            True (knowledge is always serializable)

        Example:
            >>> if knowledge.is_serializable():
            ...     data = knowledge.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Knowledge.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the knowledge.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = knowledge.validate()
        """
        errors: list[str] = []

        if not isinstance(self._knowledge_type, KnowledgeType):
            errors.append("Knowledge type must be a KnowledgeType")

        try:
            self._validate_confidence()
        except InvalidKnowledgeError as e:
            errors.append(str(e))

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = knowledge.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = knowledge.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the knowledge.

        Returns:
            String representation

        Example:
            >>> repr(knowledge)
        """
        return f"Knowledge(type={self._knowledge_type.value}, sources={len(self._sources)}, confidence={self._confidence})"

    def __str__(self) -> str:
        """Return string representation of the knowledge.

        Returns:
            String representation

        Example:
            >>> str(knowledge)
        """
        return f"{self._knowledge_type.value} knowledge ({len(self._sources)} sources)"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> knowledge1 == knowledge2
        """
        if not isinstance(other, Knowledge):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash of the knowledge.

        Returns:
            Hash value

        Example:
            >>> hash(knowledge)
        """
        return hash(self._id)


# Export
__all__ = ["Knowledge"]
