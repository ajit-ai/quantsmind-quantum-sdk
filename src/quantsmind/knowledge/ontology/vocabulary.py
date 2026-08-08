"""
Vocabulary Module

This module provides vocabulary definitions for the Knowledge package.

Purpose
-------
Provide vocabulary management for ontologies.

Responsibilities
----------------
- Define vocabulary structure
- Support vocabulary operations
- Support vocabulary validation
- Support term management

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import OntologyType
from quantsmind.knowledge.exceptions import OntologyError
from quantsmind.knowledge.types import VocabularyID, ValidationResult


class Vocabulary:
    """Concrete implementation of a vocabulary.

    This class provides vocabulary functionality.

    Attributes:
        _id: Vocabulary ID
        _name: Vocabulary name
        _language: Vocabulary language
        _terms: Terms in the vocabulary
        _description: Vocabulary description
        _metadata: Vocabulary metadata

    Example:
        >>> vocab = Vocabulary("vocab_001", "Scientific Terms", "en")
        >>> vocab.name
    """

    def __init__(
        self,
        vocabulary_id: VocabularyID,
        name: str,
        language: str = "en",
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Vocabulary.

        Args:
            vocabulary_id: Vocabulary ID
            name: Vocabulary name
            language: Vocabulary language code
            description: Vocabulary description
            metadata: Vocabulary metadata

        Example:
            >>> vocab = Vocabulary("vocab_001", "Scientific Terms", "en")
        """
        if not vocabulary_id:
            raise OntologyError("Vocabulary ID cannot be empty")

        if not name:
            raise OntologyError("Vocabulary name cannot be empty")

        self._id = vocabulary_id
        self._name = name
        self._language = language
        self._terms: Dict[str, Dict[str, Any]] = {}
        self._description = description
        self._metadata = metadata or {}

    @property
    def id(self) -> VocabularyID:
        """Get the vocabulary ID.

        Returns:
            Vocabulary ID

        Example:
            >>> vid = vocab.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the vocabulary name.

        Returns:
            Vocabulary name

        Example:
            >>> name = vocab.name
        """
        return self._name

    @property
    def language(self) -> str:
        """Get the vocabulary language.

        Returns:
            Language code

        Example:
            >>> language = vocab.language
        """
        return self._language

    @property
    def terms(self) -> Dict[str, Dict[str, Any]]:
        """Get the terms.

        Returns:
            Terms dictionary

        Example:
            >>> terms = vocab.terms
        """
        return self._terms.copy()

    @property
    def description(self) -> Optional[str]:
        """Get the vocabulary description.

        Returns:
            Vocabulary description

        Example:
            >>> description = vocab.description
        """
        return self._description

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the vocabulary metadata.

        Returns:
            Vocabulary metadata

        Example:
            >>> metadata = vocab.metadata
        """
        return self._metadata.copy()

    def add_term(self, term: str, definition: Optional[str] = None, synonyms: Optional[List[str]] = None) -> None:
        """Add a term to the vocabulary.

        Args:
            term: Term string
            definition: Term definition
            synonyms: List of synonyms

        Example:
            >>> vocab.add_term("quantum", "Smallest unit of energy", ["quantum mechanics"])
        """
        if not term:
            raise OntologyError("Term cannot be empty")

        self._terms[term] = {
            "definition": definition,
            "synonyms": synonyms or [],
        }

    def remove_term(self, term: str) -> bool:
        """Remove a term from the vocabulary.

        Args:
            term: Term string

        Returns:
            True if removed

        Example:
            >>> removed = vocab.remove_term("quantum")
        """
        if term in self._terms:
            del self._terms[term]
            return True
        return False

    def get_term(self, term: str) -> Optional[Dict[str, Any]]:
        """Get a term definition.

        Args:
            term: Term string

        Returns:
            Term definition or None

        Example:
            >>> term_def = vocab.get_term("quantum")
        """
        return self._terms.get(term)

    def search_terms(self, query: str) -> List[str]:
        """Search for terms matching a query.

        Args:
            query: Search query

        Returns:
            List of matching terms

        Example:
            >>> matches = vocab.search_terms("quant")
        """
        query_lower = query.lower()
        matches = []

        for term in self._terms:
            if query_lower in term.lower():
                matches.append(term)
            else:
                # Check synonyms
                synonyms = self._terms[term].get("synonyms", [])
                for synonym in synonyms:
                    if query_lower in synonym.lower():
                        matches.append(term)
                        break

        return matches

    def get_synonyms(self, term: str) -> List[str]:
        """Get synonyms for a term.

        Args:
            term: Term string

        Returns:
            List of synonyms

        Example:
            >>> synonyms = vocab.get_synonyms("quantum")
        """
        term_data = self._terms.get(term)
        if term_data:
            return term_data.get("synonyms", []).copy()
        return []

    def add_synonym(self, term: str, synonym: str) -> None:
        """Add a synonym to a term.

        Args:
            term: Term string
            synonym: Synonym to add

        Example:
            >>> vocab.add_synonym("quantum", "quantum mechanics")
        """
        if term in self._terms:
            if synonym not in self._terms[term]["synonyms"]:
                self._terms[term]["synonyms"].append(synonym)

    def validate(self) -> ValidationResult:
        """Validate the vocabulary.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = vocab.validate()
        """
        errors = []

        if not self._id:
            errors.append("Vocabulary ID cannot be empty")

        if not self._name:
            errors.append("Vocabulary name cannot be empty")

        if not self._language:
            errors.append("Vocabulary language cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Vocabulary definition

        Example:
            >>> data = vocab.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "language": self._language,
            "terms": self._terms,
            "term_count": len(self._terms),
            "description": self._description,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(vocab)
        """
        return f"Vocabulary(id={self._id}, name={self._name}, language={self._language}, terms={len(self._terms)})"


# Export
__all__ = [
    "Vocabulary",
]
