"""
Rule Engine Module

This module provides rule engine definitions for the Knowledge package.

Purpose
-------
Provide rule engine management for rule-based reasoning.

Responsibilities
----------------
- Define rule engine structure
- Support rule engine operations
- Support rule engine validation
- Support rule engine metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.interfaces (knowledge interfaces)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from quantsmind.knowledge.enums import ReasoningType
from quantsmind.knowledge.exceptions import ReasoningError
from quantsmind.knowledge.interfaces import IReasoner
from quantsmind.knowledge.types import ValidationResult


class RuleEngine(IReasoner):
    """Concrete implementation of a rule engine.

    This class provides rule engine functionality for rule-based reasoning.

    Attributes:
        _id: Rule engine ID
        _name: Rule engine name
        _reasoning_type: Reasoning type
        _rules: Rule definitions
        _rule_executions: Rule execution history
        _metadata: Rule engine metadata

    Example:
        >>> engine = RuleEngine("rule_001", "Business Rule Engine", ReasoningType.RULE_BASED)
        >>> engine.add_rule({"condition": lambda x: x > 0, "action": lambda x: x * 2})
    """

    def __init__(
        self,
        engine_id: str,
        name: str,
        reasoning_type: ReasoningType = ReasoningType.RULE_BASED,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a RuleEngine.

        Args:
            engine_id: Rule engine ID
            name: Rule engine name
            reasoning_type: Reasoning type
            metadata: Rule engine metadata

        Example:
            >>> engine = RuleEngine("rule_001", "Business Rule Engine", ReasoningType.RULE_BASED)
        """
        if not engine_id:
            raise ReasoningError("Rule engine ID cannot be empty", {"engine_id": engine_id})

        if not name:
            raise ReasoningError("Rule engine name cannot be empty", {"name": name})

        self._id = engine_id
        self._name = name
        self._reasoning_type = reasoning_type
        self._rules: list[dict[str, Any]] = []
        self._rule_executions: list[dict[str, Any]] = []
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the rule engine ID.

        Returns:
            Rule engine ID

        Example:
            >>> eid = engine.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the rule engine name.

        Returns:
            Rule engine name

        Example:
            >>> name = engine.name
        """
        return self._name

    @property
    def reasoning_type(self) -> ReasoningType:
        """Get the reasoning type.

        Returns:
            Reasoning type

        Example:
            >>> rtype = engine.reasoning_type
        """
        return self._reasoning_type

    @property
    def rules(self) -> list[dict[str, Any]]:
        """Get the rules.

        Returns:
            List of rules

        Example:
            >>> rules = engine.rules
        """
        return self._rules.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the rule engine metadata.

        Returns:
            Rule engine metadata

        Example:
            >>> metadata = engine.metadata
        """
        return self._metadata.copy()

    def add_rule(self, rule: dict[str, Any]) -> None:
        """Add a rule to the engine.

        Args:
            rule: Rule definition with condition and action

        Example:
            >>> engine.add_rule({"condition": lambda x: x > 0, "action": lambda x: x * 2})
        """
        if "condition" not in rule or "action" not in rule:
            raise ReasoningError("Rule must have condition and action", {"rule": rule})

        self._rules.append(rule)

    def remove_rule(self, rule_index: int) -> bool:
        """Remove a rule from the engine.

        Args:
            rule_index: Rule index

        Returns:
            True if removed

        Example:
            >>> removed = engine.remove_rule(0)
        """
        if 0 <= rule_index < len(self._rules):
            del self._rules[rule_index]
            return True
        return False

    def add_knowledge(self, knowledge_id: str, knowledge: Any) -> None:
        """Add knowledge (rule) to the engine.

        Args:
            knowledge_id: Knowledge ID
            knowledge: Knowledge to add

        Example:
            >>> engine.add_knowledge("rule_001", {"condition": lambda x: x > 0, "action": lambda x: x * 2})
        """
        if isinstance(knowledge, dict):
            knowledge["id"] = knowledge_id
            self.add_rule(knowledge)

    def remove_knowledge(self, knowledge_id: str) -> bool:
        """Remove knowledge (rule) from the engine.

        Args:
            knowledge_id: Knowledge ID

        Returns:
            True if removed

        Example:
            >>> removed = engine.remove_knowledge("rule_001")
        """
        for i, rule in enumerate(self._rules):
            if rule.get("id") == knowledge_id:
                del self._rules[i]
                return True
        return False

    def reason(self, query: dict[str, Any]) -> dict[str, Any]:
        """Execute rules on the query.

        Args:
            query: Query data

        Returns:
            Reasoning result

        Example:
            >>> result = engine.reason({"value": 5})
        """
        results = []
        executed_rules = []

        for rule in self._rules:
            condition = rule.get("condition")
            action = rule.get("action")

            if condition and action:
                try:
                    if callable(condition) and condition(query):
                        result = action(query)
                        results.append(result)
                        executed_rules.append(rule.get("id", "unknown"))

                        # Record execution
                        self._rule_executions.append({
                            "rule_id": rule.get("id", "unknown"),
                            "timestamp": str(datetime.now(UTC).replace(tzinfo=None)),
                            "input": query,
                            "output": result,
                        })
                except Exception:
                    # Skip rules that cause errors
                    continue

        return {
            "results": results,
            "executed_rules": executed_rules,
            "rule_count": len(executed_rules),
        }

    def execute_all(self, data: Any) -> list[Any]:
        """Execute all applicable rules on data.

        Args:
            data: Input data

        Returns:
            List of results

        Example:
            >>> results = engine.execute_all({"value": 5})
        """
        result = self.reason(data)
        return result.get("results", [])

    def get_execution_history(self) -> list[dict[str, Any]]:
        """Get the rule execution history.

        Returns:
            Execution history

        Example:
            >>> history = engine.get_execution_history()
        """
        return self._rule_executions.copy()

    def clear_execution_history(self) -> None:
        """Clear the execution history.

        Example:
            >>> engine.clear_execution_history()
        """
        self._rule_executions.clear()

    def validate(self) -> ValidationResult:
        """Validate the rule engine.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = engine.validate()
        """
        errors = []

        if not self._id:
            errors.append("Rule engine ID cannot be empty")

        if not self._name:
            errors.append("Rule engine name cannot be empty")

        # Validate rules
        for i, rule in enumerate(self._rules):
            if "condition" not in rule:
                errors.append(f"Rule {i} missing condition")
            if "action" not in rule:
                errors.append(f"Rule {i} missing action")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Rule engine definition

        Example:
            >>> data = engine.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "reasoning_type": self._reasoning_type.value,
            "rule_count": len(self._rules),
            "execution_count": len(self._rule_executions),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(engine)
        """
        return f"RuleEngine(id={self._id}, name={self._name}, type={self._reasoning_type.value}, rules={len(self._rules)}, executions={len(self._rule_executions)})"


# Export
__all__ = [
    "RuleEngine",
]
