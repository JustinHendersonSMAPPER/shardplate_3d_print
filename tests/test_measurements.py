"""Tests for measurement system."""

import pytest

from shardplate_generator.utils.measurements import HumanMeasurements


class TestHumanMeasurements:
    """Tests for HumanMeasurements dataclass."""

    def test_default_measurements(self) -> None:
        """Test default measurement values."""
        m = HumanMeasurements()
        assert m.height == 1.75
        assert m.chest_circumference == 1.00
        assert m.scale == 1.0

    def test_scaled_value(self) -> None:
        """Test scale application."""
        m = HumanMeasurements(scale=0.5)
        assert m.scaled(1.0) == 0.5
        assert m.scaled(0.2) == 0.1

    def test_with_clearance(self) -> None:
        """Test clearance addition."""
        m = HumanMeasurements(clearance=0.02, scale=1.0)
        # 0.5 + 0.02 clearance = 0.52
        assert m.with_clearance(0.5) == 0.52

    def test_from_size_medium(self) -> None:
        """Test medium size creation."""
        m = HumanMeasurements.from_size("M")
        # Medium should use default values (multiplier = 1.0)
        assert m.height == 1.75
        assert m.chest_circumference == 1.00

    def test_from_size_large(self) -> None:
        """Test large size creation."""
        m = HumanMeasurements.from_size("L")
        # Large has 1.05 multiplier
        assert m.height == pytest.approx(1.75 * 1.05)
        assert m.chest_circumference == pytest.approx(1.00 * 1.05)

    def test_from_size_small(self) -> None:
        """Test small size creation."""
        m = HumanMeasurements.from_size("S")
        # Small has 0.95 multiplier
        assert m.height == pytest.approx(1.75 * 0.95)

    def test_for_print_scale(self) -> None:
        """Test print scale configuration."""
        m = HumanMeasurements.for_print_scale(0.1)
        assert m.scale == 0.1
        # Plate thickness should be adjusted for printability
        assert m.plate_thickness >= 0.002

    def test_get_armor_dimensions(self) -> None:
        """Test armor dimension calculation."""
        m = HumanMeasurements()
        dims = m.get_armor_dimensions()

        assert "helmet" in dims
        assert "chest" in dims
        assert "pauldron" in dims
        assert "gauntlet" in dims
        assert "vambrace" in dims
        assert "cuisse" in dims
        assert "greave" in dims
        assert "sabaton" in dims

        # Helmet should have expected keys
        helmet = dims["helmet"]
        assert "inner_width" in helmet
        assert "inner_height" in helmet
        assert "visor_width" in helmet

    def test_armor_dimensions_include_clearance(self) -> None:
        """Test that armor dimensions include clearance."""
        m = HumanMeasurements(head_width=0.16, clearance=0.02)
        dims = m.get_armor_dimensions()

        # Inner width should be head_width + clearance
        expected = (0.16 + 0.02) * m.scale
        assert dims["helmet"]["inner_width"] == pytest.approx(expected)
