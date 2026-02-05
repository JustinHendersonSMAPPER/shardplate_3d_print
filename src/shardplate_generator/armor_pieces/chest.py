"""Shardplate chest armor (breastplate and back plate) generator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .base import ArmorPieceGenerator


@dataclass
class ChestGenerator(ArmorPieceGenerator):
    """Generator for Shardplate chest armor.

    The Shardplate chest armor features:
    - Full torso coverage with overlapping plates
    - Breastplate with angular, imposing design
    - Back plate with similar construction
    - Connection points for pauldrons
    - Smooth, seamless appearance when assembled
    """

    name: str = "chest"
    split_front_back: bool = True  # Generate as separate front/back pieces

    @property
    def armor_type(self) -> str:
        return "chest"

    def generate(self) -> Any:
        """Generate the full chest armor (front and back together)."""
        if self.split_front_back:
            front = self.generate_breastplate()
            back = self.generate_backplate()
            return self.ctx.join_objects([front, back], name="ChestArmor")
        else:
            return self._generate_unified_chest()

    def generate_breastplate(self) -> Any:
        """Generate the front breastplate."""
        dims = self.dimensions
        ctx = self.ctx

        width = dims.get("width", 0.5)
        height = dims.get("height", 0.5)
        depth = dims.get("depth", 0.32)
        thickness = self.measurements.scaled(self.measurements.plate_thickness)

        # Create main breastplate shell - curved cylinder section
        outer_shell = ctx.create_cylinder(
            radius=depth / 2 + thickness,
            depth=height,
            location=(0, 0, 0),
            vertices=64,
            name="BreastplateOuter",
        )
        ctx.rotate_object(outer_shell, (90, 0, 0))

        # Inner cavity
        inner_shell = ctx.create_cylinder(
            radius=depth / 2,
            depth=height + 0.01,
            location=(0, 0, 0),
            vertices=64,
            name="BreastplateInner",
        )
        ctx.rotate_object(inner_shell, (90, 0, 0))

        breastplate = ctx.boolean_difference(outer_shell, inner_shell, name="BreastplateShell")

        # Cut to half cylinder (front only)
        back_cutter = ctx.create_cube(
            size=max(width, height, depth) * 2,
            location=(0, depth / 2, 0),
            name="BackCutter",
        )
        breastplate = ctx.boolean_difference(breastplate, back_cutter)

        # Trim width
        for side in [-1, 1]:
            side_cutter = ctx.create_cube(
                size=max(width, height, depth) * 2,
                location=(side * (width / 2 + depth), 0, 0),
                name=f"SideCutter_{side}",
            )
            breastplate = ctx.boolean_difference(breastplate, side_cutter)

        # Add chest muscle definition
        breastplate = self._add_chest_definition(breastplate, dims, thickness)

        # Add abdominal plates
        breastplate = self._add_abdominal_plates(breastplate, dims, thickness)

        # Add collar/neck opening shaping
        breastplate = self._add_collar(breastplate, dims, thickness)

        # Add pauldron connection points
        breastplate = self._add_pauldron_mounts(breastplate, dims, thickness)

        return breastplate

    def generate_backplate(self) -> Any:
        """Generate the back plate."""
        dims = self.dimensions
        ctx = self.ctx

        width = dims.get("width", 0.5)
        height = dims.get("height", 0.5)
        depth = dims.get("depth", 0.32)
        thickness = self.measurements.scaled(self.measurements.plate_thickness)

        # Create main backplate shell
        outer_shell = ctx.create_cylinder(
            radius=depth / 2 + thickness,
            depth=height,
            location=(0, 0, 0),
            vertices=64,
            name="BackplateOuter",
        )
        ctx.rotate_object(outer_shell, (90, 0, 0))

        inner_shell = ctx.create_cylinder(
            radius=depth / 2,
            depth=height + 0.01,
            location=(0, 0, 0),
            vertices=64,
            name="BackplateInner",
        )
        ctx.rotate_object(inner_shell, (90, 0, 0))

        backplate = ctx.boolean_difference(outer_shell, inner_shell, name="BackplateShell")

        # Cut to half cylinder (back only)
        front_cutter = ctx.create_cube(
            size=max(width, height, depth) * 2,
            location=(0, -depth / 2, 0),
            name="FrontCutter",
        )
        backplate = ctx.boolean_difference(backplate, front_cutter)

        # Trim width
        for side in [-1, 1]:
            side_cutter = ctx.create_cube(
                size=max(width, height, depth) * 2,
                location=(side * (width / 2 + depth), 0, 0),
                name=f"SideCutter_{side}",
            )
            backplate = ctx.boolean_difference(backplate, side_cutter)

        # Add spine ridge
        backplate = self._add_spine_ridge(backplate, dims, thickness)

        # Add shoulder blade definition
        backplate = self._add_shoulder_blade_plates(backplate, dims, thickness)

        # Add lower back support
        backplate = self._add_lower_back_plates(backplate, dims, thickness)

        return backplate

    def _generate_unified_chest(self) -> Any:
        """Generate chest armor as a single piece (for display/small prints)."""
        front = self.generate_breastplate()
        back = self.generate_backplate()
        return self.ctx.join_objects([front, back], name="ChestArmorUnified")

    def _add_chest_definition(
        self, breastplate: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add angular chest muscle plate definition."""
        ctx = self.ctx
        width = dims.get("width", 0.5)
        height = dims.get("height", 0.5)
        depth = dims.get("depth", 0.32)

        # Upper pectoral plates
        for side in [-1, 1]:
            pec_plate = ctx.create_cube(
                size=1.0,
                location=(side * width / 4, -depth / 3, height / 4),
                name=f"PecPlate_{'L' if side < 0 else 'R'}",
            )
            ctx.scale_object(pec_plate, (width / 3, thickness * 2, height / 4))
            ctx.rotate_object(pec_plate, (10, side * 5, 0))
            breastplate = ctx.boolean_union(breastplate, pec_plate)

        # Central sternum plate
        sternum = ctx.create_cube(
            size=1.0,
            location=(0, -depth / 2.5, height / 6),
            name="SternumPlate",
        )
        ctx.scale_object(sternum, (width / 8, thickness * 2, height / 3))
        breastplate = ctx.boolean_union(breastplate, sternum)

        return breastplate

    def _add_abdominal_plates(
        self, breastplate: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add segmented abdominal armor plates."""
        ctx = self.ctx
        width = dims.get("width", 0.5)
        height = dims.get("height", 0.5)
        depth = dims.get("depth", 0.32)

        # Create overlapping ab plates for flexibility
        num_plates = 3
        plate_height = height / 6
        start_z = -height / 8

        for i in range(num_plates):
            z_pos = start_z - i * plate_height * 0.8

            ab_plate = ctx.create_cube(
                size=1.0,
                location=(0, -depth / 3, z_pos),
                name=f"AbPlate_{i}",
            )
            # Each plate slightly smaller going down
            plate_width = width * 0.8 - i * width * 0.05
            ctx.scale_object(ab_plate, (plate_width, thickness * 1.5, plate_height))
            ctx.rotate_object(ab_plate, (5 + i * 3, 0, 0))
            breastplate = ctx.boolean_union(breastplate, ab_plate)

        return breastplate

    def _add_collar(
        self, breastplate: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add collar/gorget connection area."""
        ctx = self.ctx
        width = dims.get("width", 0.5)
        height = dims.get("height", 0.5)
        depth = dims.get("depth", 0.32)

        # Raised collar rim
        collar = ctx.create_torus(
            major_radius=width / 4,
            minor_radius=thickness,
            location=(0, -depth / 6, height / 2 - 0.02),
            name="CollarRim",
        )
        # Only keep front half
        collar_cutter = ctx.create_cube(
            size=width,
            location=(0, depth / 4, height / 2),
            name="CollarCutter",
        )
        collar = ctx.boolean_difference(collar, collar_cutter)
        breastplate = ctx.boolean_union(breastplate, collar)

        return breastplate

    def _add_pauldron_mounts(
        self, breastplate: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add mounting points for pauldrons."""
        ctx = self.ctx
        width = dims.get("width", 0.5)
        height = dims.get("height", 0.5)

        # Shoulder ridge mounts
        for side in [-1, 1]:
            mount = ctx.create_cube(
                size=1.0,
                location=(side * width / 2.2, 0, height / 2.2),
                name=f"PauldronMount_{'L' if side < 0 else 'R'}",
            )
            ctx.scale_object(mount, (thickness * 4, thickness * 6, thickness * 2))
            breastplate = ctx.boolean_union(breastplate, mount)

        return breastplate

    def _add_spine_ridge(
        self, backplate: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add protective spine ridge."""
        ctx = self.ctx
        height = dims.get("height", 0.5)
        depth = dims.get("depth", 0.32)

        # Central spine protection
        spine = ctx.create_cube(
            size=1.0,
            location=(0, depth / 3, 0),
            name="SpineRidge",
        )
        ctx.scale_object(spine, (thickness * 3, thickness * 2, height * 0.8))
        backplate = ctx.boolean_union(backplate, spine)

        # Spine segments
        if self.detail_level >= 2:
            num_segments = 5
            segment_height = height * 0.12
            for i in range(num_segments):
                z_pos = height / 3 - i * segment_height * 1.2
                segment = ctx.create_cube(
                    size=1.0,
                    location=(0, depth / 2.5, z_pos),
                    name=f"SpineSegment_{i}",
                )
                ctx.scale_object(segment, (thickness * 5, thickness, segment_height))
                backplate = ctx.boolean_union(backplate, segment)

        return backplate

    def _add_shoulder_blade_plates(
        self, backplate: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add shoulder blade area plates."""
        ctx = self.ctx
        width = dims.get("width", 0.5)
        height = dims.get("height", 0.5)
        depth = dims.get("depth", 0.32)

        for side in [-1, 1]:
            blade_plate = ctx.create_cube(
                size=1.0,
                location=(side * width / 3.5, depth / 4, height / 4),
                name=f"ShoulderBladePlate_{'L' if side < 0 else 'R'}",
            )
            ctx.scale_object(blade_plate, (width / 4, thickness * 2, height / 3))
            ctx.rotate_object(blade_plate, (-5, side * 10, 0))
            backplate = ctx.boolean_union(backplate, blade_plate)

        return backplate

    def _add_lower_back_plates(
        self, backplate: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add lower back support plates."""
        ctx = self.ctx
        width = dims.get("width", 0.5)
        height = dims.get("height", 0.5)
        depth = dims.get("depth", 0.32)

        # Kidney protection plates
        for side in [-1, 1]:
            kidney_plate = ctx.create_cube(
                size=1.0,
                location=(side * width / 4, depth / 4, -height / 5),
                name=f"KidneyPlate_{'L' if side < 0 else 'R'}",
            )
            ctx.scale_object(kidney_plate, (width / 4, thickness * 1.5, height / 4))
            backplate = ctx.boolean_union(backplate, kidney_plate)

        return backplate

    def generate_printable_parts(self) -> list[tuple[str, Any]]:
        """Generate chest armor split into printable parts."""
        front = self.generate_breastplate()
        front = self.finalize(front)

        back = self.generate_backplate()
        back = self.finalize(back)

        return [("chest_front", front), ("chest_back", back)]
