"""Unit tests for quantsmind.simulation engine."""

from __future__ import annotations

import pytest

from quantsmind.simulation.simulation_engine import Experiment, SimulationEngine


class TestEngine:
    def test_register_run_history(self) -> None:
        engine = SimulationEngine()
        engine.register_simulator("double", lambda p: {"x": p["x"] * 2})
        result = engine.run_simulation("double", {"x": 21})
        assert result.success is True
        history = engine.get_simulation_history()
        assert len(history) == 1
        assert history[0]["simulator_name"] == "double"
        engine.clear_history()
        assert engine.get_simulation_history() == []

    def test_unknown_simulator(self) -> None:
        with pytest.raises(ValueError, match="not registered"):
            SimulationEngine().run_simulation("nope", {})

    def test_experiment_holds_metadata(self) -> None:
        experiment = Experiment("exp1", metadata={"k": "v"})
        assert experiment.name == "exp1"
