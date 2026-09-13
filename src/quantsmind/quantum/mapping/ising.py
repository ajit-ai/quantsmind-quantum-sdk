"""QUBO -> Ising -> quantum-representation mapping (QMQ-02).

:class:`IsingMapper` converts an energy-equivalent
:class:`~quantsmind.quantum.optimization.qubo.QUBOModel` into an
:class:`~quantsmind.quantum.optimization.ising.IsingModel` (``x = (s+1)/2``)
so the domain problem can be handed to a quantum engine.  The mapper itself
stays engine-agnostic and serializable; building MicroQuantum objects from
the Ising model happens in the integration layer.
"""

from __future__ import annotations

from typing import Any

from quantsmind.quantum.mapping.mapper import MappingError, MappingResult
from quantsmind.quantum.optimization.qubo import QUBOModel
from quantsmind.quantum.strategy.strategy import ComputationStrategy


class IsingMapper:
    """Maps a :class:`QUBOModel` to an energy-equivalent :class:`IsingModel`."""

    name = "ising"

    def map(
        self,
        qubo: QUBOModel,
        *,
        strategy: ComputationStrategy = ComputationStrategy.HYBRID,
    ) -> MappingResult:
        """Record the QUBO -> Ising conversion.

        The built :class:`~quantsmind.quantum.optimization.ising.IsingModel`
        is attached as the mapping ``payload``; MicroQuantum conversion is
        deferred to the integration layer.

        Raises:
            MappingError: If ``qubo`` is not a :class:`QUBOModel`.
        """
        if not isinstance(qubo, QUBOModel):
            raise MappingError(f"IsingMapper requires a QUBOModel, got {type(qubo).__name__}")
        from quantsmind.quantum.optimization.ising import IsingModel

        ising = IsingModel.from_qubo(qubo)
        steps = [
            "converted QUBO to Ising via x = (s + 1) / 2",
            f"fields: {len(ising.h)}, couplings: {len(ising.couplings)}",
            "energy equivalent up to the carried constant",
            "target: IsingModel",
        ]
        metadata: dict[str, Any] = {
            "source_qubo": qubo.name,
            "variables": list(ising.variables),
            "num_fields": len(ising.h),
            "num_couplings": len(ising.couplings),
            "constant": ising.constant,
            "offset": ising.offset,
        }
        return MappingResult(
            mapper=self.name,
            strategy=strategy,
            source="QUBOModel",
            target="IsingModel",
            steps=steps,
            metadata=metadata,
            payload=ising,
        )


__all__ = ["IsingMapper"]
