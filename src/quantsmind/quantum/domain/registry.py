"""Explicit, registered cross-domain dispatch (QMQ-11 §10).

A :class:`DomainRegistry` maps each supported domain to an explicit
:class:`DomainBinding`.  The built-in registry pre-registers the Finance,
Portfolio, Data and ML domains; new domains register themselves through the
same public API — there is no central ``if/elif`` monolith.

Each binding exposes four capabilities that the domain intelligence layer
reuses:

* ``validate`` / ``raise_if_invalid`` — domain validation.
* ``to_quantum_problem`` — formulate the domain problem into the existing
  QMQ pipeline.
* ``solve`` / ``benchmark`` — execute the existing QMQ-03..06 pipeline
  through the per-domain optimizer.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.domain.errors import UnsupportedDomainError

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem


__all__ = [
    "DomainKind",
    "DomainBinding",
    "DomainRegistry",
]


class DomainKind(Enum):
    """Registered quantum-enabled domains (QMQ-11)."""

    FINANCE = "finance"
    PORTFOLIO = "portfolio"
    DATA = "data"
    ML = "ml"

    @classmethod
    def parse(cls, value: Any) -> DomainKind:
        """Coerce a label or member to a :class:`DomainKind`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.value == text or member.name.lower() == text:
                return member
        raise ValueError(f"unknown domain kind {value!r}")


@dataclass
class DomainBinding:
    """Explicit binding between a domain and its execution capabilities.

    Args:
        kind: The registered :class:`DomainKind`.
        label: Human-readable sub-label of the binding.
        problem_types: ``isinstance``-matchable problem types this binding
            owns.
        validate: Callable(problem) -> list[str] of validation issues.
        raise_if_invalid: Callable(problem) -> None raising the domain's
            validation error.
        to_quantum_problem: Callable(problem, *,
            preferred_strategy=None) -> :class:`QuantumProblem`.  Reuses the
            existing per-domain formulation adapter.
        solve: Callable(problem, *, strategy=None, config=None, seed=None)
            through the per-domain optimizer.
        benchmark: Callable(problem, *, strategy=None, known_optimum=None,
            runs=1, raise_on_error=False, config=None, seed=None).
        description: Human-readable description of the binding.
        metadata: Free-form metadata (module path, rule path, ...).
    """

    kind: DomainKind
    label: str
    problem_types: tuple[type, ...]
    validate: Callable[[Any], list[str]]
    raise_if_invalid: Callable[[Any], None]
    to_quantum_problem: Callable[..., QuantumProblem]
    solve: Callable[..., Any]
    benchmark: Callable[..., Any]
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def accepts(self, problem: Any) -> bool:
        """True when this binding owns the given problem instance."""
        return any(isinstance(problem, problem_type) for problem_type in self.problem_types)

    def __repr__(self) -> str:
        return f"DomainBinding({self.kind.value!r}{' / ' + str(self.label) if self.label else ''})"


class DomainRegistry:
    """Registered dispatch table for supported domains (QMQ-11 §10).

    The registry is extensible through :meth:`register`: an external domain
    supplies its own :class:`DomainBinding` (wrapping any problem types,
    formulation adapters and optimizers) and becomes dispatachable by the
    shared :class:`~quantsmind.quantum.domain.intelligence.DomainIntelligence`
    layer without changing core code.
    """

    def __init__(self, *, defaults: bool = True) -> None:
        self._bindings: list[DomainBinding] = []
        if defaults:
            self.register_defaults()

    # ------------------------------------------------------------------
    # registration
    # ------------------------------------------------------------------

    def register(self, binding: DomainBinding) -> DomainBinding:
        """Register a :class:`DomainBinding` (explicit dispatch entry)."""
        if not isinstance(binding, DomainBinding):
            raise TypeError("registry.register requires a DomainBinding instance")
        for existing in self._bindings:
            if existing.kind == binding.kind:
                raise ValueError(f"domain kind {binding.kind.value!r} is already registered")
        self._bindings.append(binding)
        return binding

    def register_defaults(self) -> None:
        """Register the four built-in domain bindings.

        The bindings live in :mod:`quantsmind.quantum.domain.adapters` and
        wrap the existing per-domain formulation adapters and optimizers.
        Registration order is stable: finance, portfolio, data, ml.
        """
        from quantsmind.quantum.domain.adapters import (
            data_binding,
            finance_binding,
            ml_binding,
            portfolio_binding,
        )

        for binding in (finance_binding(), portfolio_binding(), data_binding(), ml_binding()):
            self.register(binding)

    # ------------------------------------------------------------------
    # dispatch
    # ------------------------------------------------------------------

    def resolve(self, problem: Any) -> DomainBinding:
        """Return the :class:`DomainBinding` owning ``problem``.

        Raises:
            UnsupportedDomainError: When no binding accepts the problem.
        """
        for binding in self._bindings:
            if binding.accepts(problem):
                return binding
        raise UnsupportedDomainError(
            f"no registered domain binding supports {type(problem).__name__}; "
            "register one via DomainRegistry.register(DomainBinding(...))",
            problem=problem,
        )

    def resolve_kind(self, kind: DomainKind | str) -> DomainBinding:
        """Return the binding registered for a :class:`DomainKind`."""
        try:
            parsed = DomainKind.parse(kind)
        except ValueError as exc:
            raise UnsupportedDomainError(f"unknown domain kind {kind!r}") from exc
        for binding in self._bindings:
            if binding.kind == parsed:
                return binding
        raise UnsupportedDomainError(f"domain kind {parsed.value!r} is not registered")

    def kind_of(self, problem: Any) -> DomainKind:
        """Return the :class:`DomainKind` of a problem instance."""
        return self.resolve(problem).kind

    def is_registered(self, problem: Any) -> bool:
        """True when a binding accepts the problem."""
        return any(binding.accepts(problem) for binding in self._bindings)

    def domains(self) -> list[DomainKind]:
        """Registered :class:`DomainKind` values in registration order."""
        return [binding.kind for binding in self._bindings]

    def bindings(self) -> list[DomainBinding]:
        """Registered bindings (copy) in registration order."""
        return list(self._bindings)

    def __len__(self) -> int:
        return len(self._bindings)

    def __contains__(self, kind: DomainKind | str) -> bool:
        try:
            self.resolve_kind(kind)
        except UnsupportedDomainError:
            return False
        return True
