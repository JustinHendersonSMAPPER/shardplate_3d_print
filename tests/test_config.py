"""Tests for configuration system."""

import json
import tempfile
from pathlib import Path

import pytest

from shardplate_generator.config import (
    ColorConfig,
    GenerationConfig,
    ShardplateColorScheme,
    ShardplateConfig,
    SizeConfig,
)


class TestColorScheme:
    """Tests for ShardplateColorScheme enum."""

    def test_list_schemes(self) -> None:
        """Test listing all color schemes."""
        schemes = ShardplateColorScheme.list_schemes()
        assert len(schemes) > 0
        assert "kholin_blue" in schemes
        assert "slate_grey" in schemes

    def test_from_name(self) -> None:
        """Test getting scheme by name."""
        scheme = ShardplateColorScheme.from_name("kholin_blue")
        assert scheme == ShardplateColorScheme.KHOLIN_BLUE
        assert scheme.primary_hex == "#1E3A5F"

    def test_from_name_invalid(self) -> None:
        """Test invalid scheme name raises error."""
        with pytest.raises(ValueError):
            ShardplateColorScheme.from_name("invalid_scheme")


class TestColorConfig:
    """Tests for ColorConfig dataclass."""

    def test_default_colors(self) -> None:
        """Test default color values."""
        config = ColorConfig()
        assert config.primary_color == "#708090"
        assert config.secondary_color == "#C0C0C0"

    def test_from_scheme(self) -> None:
        """Test creating config from scheme."""
        config = ColorConfig.from_scheme(ShardplateColorScheme.WINDRUNNER_BLUE)
        assert config.primary_color == "#4169E1"
        assert config.secondary_color == "#FFFFFF"

    def test_custom_colors(self) -> None:
        """Test custom color configuration."""
        config = ColorConfig.custom("#FF0000", "#00FF00")
        assert config.primary_color == "#FF0000"
        assert config.secondary_color == "#00FF00"

    def test_to_rgb(self) -> None:
        """Test hex to RGB conversion."""
        config = ColorConfig()
        rgb = config.to_rgb("#FF0000")
        assert rgb == (1.0, 0.0, 0.0)

        rgb = config.to_rgb("#00FF00")
        assert rgb == (0.0, 1.0, 0.0)


class TestSizeConfig:
    """Tests for SizeConfig dataclass."""

    def test_default_size(self) -> None:
        """Test default size values."""
        config = SizeConfig()
        assert config.size_name == "M"
        assert config.print_scale == 1.0

    def test_custom_measurements(self) -> None:
        """Test custom measurement values."""
        config = SizeConfig(
            size_name="custom",
            height=1.85,
            chest_circumference=1.05,
        )
        measurements = config.get_measurements()
        assert measurements["height"] == 1.85
        assert measurements["chest_circumference"] == 1.05


class TestGenerationConfig:
    """Tests for GenerationConfig dataclass."""

    def test_default_generates_all(self) -> None:
        """Test that default config generates all pieces."""
        config = GenerationConfig()
        assert config.generate_helmet is True
        assert config.generate_chest is True
        assert config.generate_pauldrons is True
        assert config.generate_gauntlets is True
        assert config.generate_vambraces is True
        assert config.generate_cuisses is True
        assert config.generate_greaves is True
        assert config.generate_sabatons is True

    def test_default_options(self) -> None:
        """Test default generation options."""
        config = GenerationConfig()
        assert config.include_strap_mounts is True
        assert config.detail_level == 2
        assert config.split_for_printing is True


class TestShardplateConfig:
    """Tests for ShardplateConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = ShardplateConfig()
        assert config.name == "my_shardplate"
        assert isinstance(config.colors, ColorConfig)
        assert isinstance(config.size, SizeConfig)
        assert isinstance(config.generation, GenerationConfig)

    def test_save_and_load(self) -> None:
        """Test saving and loading configuration."""
        config = ShardplateConfig(
            name="test_armor",
            colors=ColorConfig.from_scheme(ShardplateColorScheme.KHOLIN_BLUE),
            size=SizeConfig(size_name="L", print_scale=0.5),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "config.json"
            config.save(filepath)

            # Verify file exists and is valid JSON
            assert filepath.exists()
            with open(filepath) as f:
                data = json.load(f)
            assert data["name"] == "test_armor"
            assert data["size"]["size_name"] == "L"

            # Load and verify
            loaded = ShardplateConfig.load(filepath)
            assert loaded.name == "test_armor"
            assert loaded.size.size_name == "L"
            assert loaded.size.print_scale == 0.5
            assert loaded.colors.primary_color == "#1E3A5F"
