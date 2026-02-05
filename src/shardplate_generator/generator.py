"""Main Shardplate generator that orchestrates armor piece generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .armor_pieces import (
    ChestGenerator,
    CuisseGenerator,
    GauntletGenerator,
    GreaveGenerator,
    HelmetGenerator,
    PauldronGenerator,
    SabatonGenerator,
    VambraceGenerator,
)
from .config import ColorConfig, GenerationConfig, ShardplateConfig, SizeConfig
from .utils.measurements import HumanMeasurements

if TYPE_CHECKING:
    from .utils.blender_utils import BlenderContext


@dataclass
class ShardplateGenerator:
    """Main generator for complete Shardplate armor sets."""

    config: ShardplateConfig
    _ctx: Any = field(default=None, repr=False)
    _measurements: HumanMeasurements | None = field(default=None, repr=False)

    @property
    def ctx(self) -> BlenderContext:
        """Get or create Blender context."""
        if self._ctx is None:
            from .utils.blender_utils import BlenderContext

            self._ctx = BlenderContext()
        return self._ctx

    @property
    def measurements(self) -> HumanMeasurements:
        """Get measurements from config."""
        if self._measurements is None:
            self._measurements = self._create_measurements()
        return self._measurements

    def _create_measurements(self) -> HumanMeasurements:
        """Create HumanMeasurements from config."""
        size_config = self.config.size

        # Start with standard size or custom
        if size_config.size_name.upper() in ["XS", "S", "M", "L", "XL", "XXL"]:
            measurements = HumanMeasurements.from_size(size_config.size_name)
        else:
            measurements = HumanMeasurements()

        # Apply custom measurements if provided
        custom = size_config.get_measurements()
        for attr, value in custom.items():
            if value is not None and hasattr(measurements, attr):
                setattr(measurements, attr, value)

        # Apply scale
        measurements.scale = size_config.print_scale

        # Apply clearance
        measurements.clearance = size_config.clearance_mm / 1000  # Convert mm to m

        return measurements

    def generate_all(self) -> dict[str, list[Path]]:
        """Generate all configured armor pieces and export to files."""
        gen_config = self.config.generation
        output_dir = Path(gen_config.output_directory) / self.config.name
        output_dir.mkdir(parents=True, exist_ok=True)

        results: dict[str, list[Path]] = {}

        print(f"\nGenerating Shardplate: {self.config.name}")
        print(f"Output directory: {output_dir}")
        print(f"Scale: {self.config.size.print_scale}")
        print(f"Colors: Primary {self.config.colors.primary_color}, "
              f"Secondary {self.config.colors.secondary_color}")
        print("-" * 50)

        # Generate each piece
        if gen_config.generate_helmet:
            results["helmet"] = self._generate_helmet(output_dir)

        if gen_config.generate_chest:
            results["chest"] = self._generate_chest(output_dir)

        if gen_config.generate_pauldrons:
            results["pauldrons"] = self._generate_pauldrons(output_dir)

        if gen_config.generate_gauntlets:
            results["gauntlets"] = self._generate_gauntlets(output_dir)

        if gen_config.generate_vambraces:
            results["vambraces"] = self._generate_vambraces(output_dir)

        if gen_config.generate_cuisses:
            results["cuisses"] = self._generate_cuisses(output_dir)

        if gen_config.generate_greaves:
            results["greaves"] = self._generate_greaves(output_dir)

        if gen_config.generate_sabatons:
            results["sabatons"] = self._generate_sabatons(output_dir)

        # Save config alongside output
        config_path = output_dir / "config.json"
        self.config.save(config_path)

        print("-" * 50)
        print(f"Generation complete! Files saved to: {output_dir}")
        self._print_summary(results)

        return results

    def _generate_helmet(self, output_dir: Path) -> list[Path]:
        """Generate helmet."""
        print("  Generating helmet...")
        self.ctx.clear_scene()

        generator = HelmetGenerator(
            name="helmet",
            measurements=self.measurements,
            include_straps=self.config.generation.include_strap_mounts,
            detail_level=self.config.generation.detail_level,
        )

        if self.config.generation.split_for_printing:
            parts = generator.generate_printable_parts()
            paths = []
            for name, obj in parts:
                filepath = output_dir / f"{name}.stl"
                self.ctx.export_stl(obj, str(filepath))
                paths.append(filepath)
            return paths
        else:
            filepath = generator.generate_and_export(output_dir)
            return [filepath]

    def _generate_chest(self, output_dir: Path) -> list[Path]:
        """Generate chest armor."""
        print("  Generating chest armor...")
        self.ctx.clear_scene()

        generator = ChestGenerator(
            name="chest",
            measurements=self.measurements,
            include_straps=self.config.generation.include_strap_mounts,
            detail_level=self.config.generation.detail_level,
            split_front_back=self.config.generation.split_for_printing,
        )

        if self.config.generation.split_for_printing:
            parts = generator.generate_printable_parts()
            paths = []
            for name, obj in parts:
                filepath = output_dir / f"{name}.stl"
                self.ctx.export_stl(obj, str(filepath))
                paths.append(filepath)
            return paths
        else:
            filepath = generator.generate_and_export(output_dir)
            return [filepath]

    def _generate_pauldrons(self, output_dir: Path) -> list[Path]:
        """Generate pauldrons (pair)."""
        print("  Generating pauldrons...")
        self.ctx.clear_scene()

        generator = PauldronGenerator(
            _base_name="pauldron",
            measurements=self.measurements,
            include_straps=self.config.generation.include_strap_mounts,
            detail_level=self.config.generation.detail_level,
        )

        left_path, right_path = generator.export_pair(output_dir)
        return [left_path, right_path]

    def _generate_gauntlets(self, output_dir: Path) -> list[Path]:
        """Generate gauntlets (pair)."""
        print("  Generating gauntlets...")
        self.ctx.clear_scene()

        generator = GauntletGenerator(
            _base_name="gauntlet",
            measurements=self.measurements,
            include_straps=self.config.generation.include_strap_mounts,
            detail_level=self.config.generation.detail_level,
        )

        left_path, right_path = generator.export_pair(output_dir)
        return [left_path, right_path]

    def _generate_vambraces(self, output_dir: Path) -> list[Path]:
        """Generate vambraces (pair)."""
        print("  Generating vambraces...")
        self.ctx.clear_scene()

        generator = VambraceGenerator(
            _base_name="vambrace",
            measurements=self.measurements,
            include_straps=self.config.generation.include_strap_mounts,
            detail_level=self.config.generation.detail_level,
        )

        left_path, right_path = generator.export_pair(output_dir)
        return [left_path, right_path]

    def _generate_cuisses(self, output_dir: Path) -> list[Path]:
        """Generate cuisses (pair)."""
        print("  Generating cuisses...")
        self.ctx.clear_scene()

        generator = CuisseGenerator(
            _base_name="cuisse",
            measurements=self.measurements,
            include_straps=self.config.generation.include_strap_mounts,
            detail_level=self.config.generation.detail_level,
        )

        left_path, right_path = generator.export_pair(output_dir)
        return [left_path, right_path]

    def _generate_greaves(self, output_dir: Path) -> list[Path]:
        """Generate greaves (pair)."""
        print("  Generating greaves...")
        self.ctx.clear_scene()

        generator = GreaveGenerator(
            _base_name="greave",
            measurements=self.measurements,
            include_straps=self.config.generation.include_strap_mounts,
            detail_level=self.config.generation.detail_level,
        )

        left_path, right_path = generator.export_pair(output_dir)
        return [left_path, right_path]

    def _generate_sabatons(self, output_dir: Path) -> list[Path]:
        """Generate sabatons (pair)."""
        print("  Generating sabatons...")
        self.ctx.clear_scene()

        generator = SabatonGenerator(
            _base_name="sabaton",
            measurements=self.measurements,
            include_straps=self.config.generation.include_strap_mounts,
            detail_level=self.config.generation.detail_level,
        )

        left_path, right_path = generator.export_pair(output_dir)
        return [left_path, right_path]

    def _print_summary(self, results: dict[str, list[Path]]) -> None:
        """Print generation summary."""
        print("\nGenerated Files:")
        total_files = 0
        for piece_type, paths in results.items():
            print(f"  {piece_type}:")
            for path in paths:
                print(f"    - {path.name}")
                total_files += 1
        print(f"\nTotal: {total_files} STL files")


def generate_from_config(config: ShardplateConfig) -> dict[str, list[Path]]:
    """Generate Shardplate from a configuration object."""
    generator = ShardplateGenerator(config=config)
    return generator.generate_all()


def generate_from_file(config_path: str | Path) -> dict[str, list[Path]]:
    """Generate Shardplate from a configuration file."""
    config = ShardplateConfig.load(config_path)
    return generate_from_config(config)


def generate_with_wizard() -> dict[str, list[Path]]:
    """Generate Shardplate using interactive wizard."""
    config = ShardplateConfig.from_wizard()
    return generate_from_config(config)
