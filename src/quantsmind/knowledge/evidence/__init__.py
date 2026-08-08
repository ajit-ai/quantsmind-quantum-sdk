"""
Evidence Package

This package provides evidence management for the Knowledge package.

Purpose
-------
Provide comprehensive evidence definitions and operations.

Modules
-------
- evidence: Evidence management
- hypothesis: Hypothesis management
- theory: Theory management
- law: Law management
- fact: Fact management
- rule: Rule management
"""

from __future__ import annotations

from quantsmind.knowledge.evidence.evidence import Evidence
from quantsmind.knowledge.evidence.fact import Fact
from quantsmind.knowledge.evidence.hypothesis import Hypothesis
from quantsmind.knowledge.evidence.law import Law
from quantsmind.knowledge.evidence.rule import Rule
from quantsmind.knowledge.evidence.theory import Theory

__all__ = [
    "Evidence",
    "Hypothesis",
    "Theory",
    "Law",
    "Fact",
    "Rule",
]
