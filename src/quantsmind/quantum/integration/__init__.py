"""Integration layer of QuantsMind Quantum.

Wraps the MicroQuantum runtime behind a stable facade so the domain,
formulation, strategy, mapping, workflow and result layers never import
``microquantum`` directly.
"""

from __future__ import annotations

from quantsmind.quantum.integration.microquantum import (
    microquantum_available,
    require_microquantum,
    resolve_backend,
)

__all__ = ["microquantum_available", "require_microquantum", "resolve_backend"]
