"""QMQ-03 capability detection layer.

A :class:`CapabilityModel` answers *what can actually run in this
environment*.  It always distinguishes:

* Whether MicroQuantum is installed.
* Which MicroQuantum algorithms the installed version exposes (public API
  probes only — never private internals, never source copies).
* Whether classical baselines are available (always, in QuantsMind Quantum).

Nothing in this module imports ``microquantum`` at import time; probes are
lazy and graceful, so classical-only environments remain fully functional.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

from quantsmind.quantum._mq import microquantum_available, require_microquantum

# Canonical QuantsMind algorithm id -> public MicroQuantum class name.
# This is the *discovery* mapping: a capability flag exists iff the installed
# MicroQuantum exposes the corresponding class.
_ALGORITHM_PROBES: dict[str, str] = {
    "qaoa": "QAOA",
    "vqe": "VQE",
    "vqd": "VQD",
    "adapt_vqe": "AdaptVQE",
    "grover": "GroverSearch",
    "shor": "ShorsAlgorithm",
    "bernstein_vazirani": "BernsteinVazirani",
    "deutsch_jozsa": "DeutschJozsa",
    "qft": "QFT",
    "phase_estimation": "PhaseEstimation",
    "amplitude_estimation": "AmplitudeEstimation",
    "hamiltonian_simulation": "HamiltonianSimulation",
    "hhl": "HHL",
    "discrete_quantum_walk": "DiscreteQuantumWalk",
    "continuous_quantum_walk": "ContinuousQuantumWalk",
}

# Public MicroQuantum names that indicate quantum machine-learning support.
_QML_NAMES = ("QuantumKernel", "QuantumClassifier", "VQC", "QuantumModel")


@dataclass
class CapabilityModel:
    """Snapshot of what the current environment can execute.

    Args:
        microquantum_installed: The optional ``microquantum`` package is
            importable.
        quantum_enabled: Master switch for quantum-family execution.
        simulator_available: A local simulator backend is exposed by
            MicroQuantum.
        backend_available: A backend can be resolved for execution.
        qml_available: MicroQuantum exposes a quantum machine-learning class.
        quantum_execution_enabled: MicroQuantum can actually be executed
            (installed and enabled).
        classical_baseline_available: The QMQ-02 classical exhaustive
            baseline exists (always true).
        algorithm_available: Algorithm id -> probe result.
        metadata: Free-form detection metadata.
    """

    microquantum_installed: bool = False
    quantum_enabled: bool = True
    simulator_available: bool = False
    backend_available: bool = False
    qml_available: bool = False
    quantum_execution_enabled: bool = False
    classical_baseline_available: bool = True
    algorithm_available: dict[str, bool] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # detection
    # ------------------------------------------------------------------

    @classmethod
    def detect(
        cls,
        *,
        quantum_enabled: bool = True,
        backend_available: bool | None = None,
    ) -> CapabilityModel:
        """Probe the environment using public APIs only.

        Args:
            quantum_enabled: Whether quantum execution is enabled by policy.
            backend_available: Explicit backend signal; ``None`` falls back
                to local-simulator availability.
        """
        installed = microquantum_available()
        algorithm_available: dict[str, bool] = {}
        simulator_available = False
        qml_available = False
        if installed:
            mq = require_microquantum()
            for algorithm_id, class_name in _ALGORITHM_PROBES.items():
                algorithm_available[algorithm_id] = hasattr(mq, class_name)
            simulator_available = hasattr(mq, "LocalSimulatorBackend")
            qml_available = any(hasattr(mq, name) for name in _QML_NAMES)
        resolved_backend = (
            backend_available if backend_available is not None else simulator_available
        )
        return cls(
            microquantum_installed=installed,
            quantum_enabled=quantum_enabled,
            simulator_available=simulator_available,
            backend_available=resolved_backend,
            qml_available=qml_available,
            quantum_execution_enabled=installed and quantum_enabled,
            classical_baseline_available=True,
            algorithm_available=algorithm_available,
            metadata={
                "detected": True,
                "probe": "public-API capability detection (QMQ-03)",
            },
        )

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------

    def is_available(self, capability: str) -> bool:
        """Return whether a named capability holds.

        Accepts canonical aliases: ``"qaoa_available"``, ``"qaoa"``,
        ``"microquantum"``, or any attribute of this model.
        """
        key = capability.strip()
        if key in {"microquantum", "microquantum_available"}:
            return self.microquantum_installed
        if key.endswith("_available"):
            base = key[: -len("_available")]
            if base in self.algorithm_available:
                return self.algorithm_available[base]
            return bool(getattr(self, f"{base}_available", False))
        if key in self.algorithm_available:
            return self.algorithm_available[key]
        return bool(getattr(self, key, False))

    def executable_algorithms(self) -> list[str]:
        """Sorted ids of algorithms currently executable in this environment."""
        return sorted(
            algorithm_id
            for algorithm_id, available in self.algorithm_available.items()
            if available
        )

    def required_caps_met(self, required_capabilities: tuple[str, ...]) -> bool:
        """True when every required capability is available."""
        return all(self.is_available(name) for name in required_capabilities)

    def capability_flags(self) -> dict[str, bool]:
        """All boolean capability flags as a flat dictionary.

        Algorithm probes are also included as ``"<id>_available"`` keys.
        """
        flags = {
            "microquantum_installed": self.microquantum_installed,
            "quantum_enabled": self.quantum_enabled,
            "simulator_available": self.simulator_available,
            "backend_available": self.backend_available,
            "qml_available": self.qml_available,
            "quantum_execution_enabled": self.quantum_execution_enabled,
            "classical_baseline_available": self.classical_baseline_available,
        }
        for algorithm_id, available in self.algorithm_available.items():
            flags[f"{algorithm_id}_available"] = available
        return flags

    # ------------------------------------------------------------------
    # serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "microquantum_installed": self.microquantum_installed,
            "quantum_enabled": self.quantum_enabled,
            "simulator_available": self.simulator_available,
            "backend_available": self.backend_available,
            "qml_available": self.qml_available,
            "quantum_execution_enabled": self.quantum_execution_enabled,
            "classical_baseline_available": self.classical_baseline_available,
            "algorithm_available": dict(self.algorithm_available),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a CapabilityModel from :meth:`to_dict` output."""
        return cls(
            microquantum_installed=bool(data.get("microquantum_installed", False)),
            quantum_enabled=bool(data.get("quantum_enabled", True)),
            simulator_available=bool(data.get("simulator_available", False)),
            backend_available=bool(data.get("backend_available", False)),
            qml_available=bool(data.get("qml_available", False)),
            quantum_execution_enabled=bool(data.get("quantum_execution_enabled", False)),
            classical_baseline_available=bool(data.get("classical_baseline_available", True)),
            algorithm_available={
                str(k): bool(v) for k, v in data.get("algorithm_available", {}).items()
            },
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"CapabilityModel(microquantum={self.microquantum_installed}, "
            f"algorithms={len(self.executable_algorithms())}, "
            f"qml={self.qml_available})"
        )


__all__ = ["CapabilityModel", "_ALGORITHM_PROBES"]
