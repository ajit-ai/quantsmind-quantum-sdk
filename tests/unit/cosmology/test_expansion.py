"""Unit tests for quantsmind.cosmology.expansion."""

from __future__ import annotations

import pytest

from quantsmind.cosmology import (
    density_scaling,
    doppler_redshift,
    hubble_distance_mpc,
    hubble_time_gyr,
    hubble_velocity,
    luminosity_distance_linear_mpc,
    redshift_from_scale,
    scale_factor,
)


class TestExpansion:
    def test_hubble_velocity(self) -> None:
        assert hubble_velocity(100.0) == pytest.approx(7000.0)

    def test_scale_roundtrip(self) -> None:
        assert scale_factor(1.0) == pytest.approx(0.5)
        assert redshift_from_scale(0.5) == pytest.approx(1.0)

    def test_hubble_scales(self) -> None:
        assert hubble_distance_mpc() == pytest.approx(4282.7, rel=1e-3)
        assert hubble_time_gyr() == pytest.approx(13.97, rel=1e-3)

    def test_doppler_small_velocity(self) -> None:
        assert doppler_redshift(100000.0) == pytest.approx(0.0003336, rel=1e-3)
        with pytest.raises(ValueError):
            doppler_redshift(299792458.0)

    def test_density_scalings(self) -> None:
        assert density_scaling("matter", 1.0) == pytest.approx(8.0)
        assert density_scaling("radiation", 1.0) == pytest.approx(16.0)
        assert density_scaling("lambda", 5.0) == pytest.approx(1.0)
        with pytest.raises(ValueError):
            density_scaling("dark", 1.0)

    def test_linear_distance(self) -> None:
        assert luminosity_distance_linear_mpc(0.1) == pytest.approx(428.3, rel=1e-3)

    def test_negative_redshift(self) -> None:
        with pytest.raises(ValueError):
            scale_factor(-0.5)
