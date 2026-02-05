"""Shardplate pauldron (shoulder armor) generator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .base import SymmetricArmorPieceGenerator


@dataclass
class PauldronGenerator(SymmetricArmorPieceGenerator):
    """Generator for Shardplate pauldrons (shoulder armor).

    Shardplate pauldrons feature:
    - Large, imposing shoulder coverage
    - Multiple overlapping plates
    - Angular, aggressive styling
    - Connection to chest armor and upper arm
    """

    _base_name: str = "pauldron"
    side: str = "left"

    @property
    def armor_type(self) -> str:
        return "pauldron"

    def generate_base(self) -> Any:
        """Generate the left pauldron."""
        dims = self.dimensions
        ctx = self.ctx

        width = dims.get("width", 0.2)
        height = dims.get("height", 0.15)
        depth = dims.get("depth", 0.16)
        thickness = self.measurements.scaled(self.measurements.plate_thickness)

        # Main shoulder dome
        outer_dome = ctx.create_uv_sphere(
            radius=1.0,
            location=(0, 0, 0),
            segments=32,
            ring_count=16,
            name="PauldronDome",
        )
        ctx.scale_object(outer_dome, (width / 2 + thickness, depth / 2 + thickness, height + thickness))

        # Inner cavity
        inner_dome = ctx.create_uv_sphere(
            radius=1.0,
            location=(0, 0, -thickness),
            segments=32,
            ring_count=16,
            name="PauldronInner",
        )
        ctx.scale_object(inner_dome, (width / 2, depth / 2, height))

        pauldron = ctx.boolean_difference(outer_dome, inner_dome, name="PauldronShell")

        # Cut bottom half for shoulder fitting
        bottom_cutter = ctx.create_cube(
            size=max(width, depth, height) * 2,
            location=(0, 0, -height),
            name="BottomCutter",
        )
        pauldron = ctx.boolean_difference(pauldron, bottom_cutter)

        # Add layered plates
        pauldron = self._add_layered_plates(pauldron, dims, thickness)

        # Add shoulder ridge
        pauldron = self._add_shoulder_ridge(pauldron, dims, thickness)

        # Add arm connection
        pauldron = self._add_arm_guard(pauldron, dims, thickness)

        # Add decorative elements
        if self.detail_level >= 2:
            pauldron = self._add_decorative_elements(pauldron, dims, thickness)

        return pauldron

    def _add_layered_plates(
        self, pauldron: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add overlapping plate layers characteristic of Shardplate."""
        ctx = self.ctx
        width = dims.get("width", 0.2)
        height = dims.get("height", 0.15)
        depth = dims.get("depth", 0.16)

        # Create 3 overlapping lower plates
        num_plates = 3
        for i in range(num_plates):
            z_offset = -i * height * 0.15
            plate_width = width * (0.9 - i * 0.1)

            plate = ctx.create_cube(
                size=1.0,
                location=(0, 0, z_offset),
                name=f"LayerPlate_{i}",
            )
            ctx.scale_object(plate, (plate_width, depth * 0.6, thickness * 2))
            ctx.rotate_object(plate, (15 + i * 10, 0, 0))
            pauldron = ctx.boolean_union(pauldron, plate)

        return pauldron

    def _add_shoulder_ridge(
        self, pauldron: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add angular shoulder ridge."""
        ctx = self.ctx
        width = dims.get("width", 0.2)
        height = dims.get("height", 0.15)

        # Main ridge along top
        ridge = ctx.create_cube(
            size=1.0,
            location=(0, 0, height * 0.8),
            name="ShoulderRidge",
        )
        ctx.scale_object(ridge, (width * 0.8, thickness * 2, thickness * 3))
        pauldron = ctx.boolean_union(pauldron, ridge)

        return pauldron

    def _add_arm_guard(
        self, pauldron: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add upper arm guard extension."""
        ctx = self.ctx
        width = dims.get("width", 0.2)
        height = dims.get("height", 0.15)
        depth = dims.get("depth", 0.16)

        # Outer arm guard plate
        arm_guard = ctx.create_cylinder(
            radius=depth / 3,
            depth=height * 0.6,
            location=(-width / 3, 0, -height * 0.3),
            vertices=32,
            name="ArmGuard",
        )

        # Cut to half cylinder
        guard_cutter = ctx.create_cube(
            size=depth,
            location=(-width / 3, depth / 3, -height * 0.3),
            name="GuardCutter",
        )
        arm_guard = ctx.boolean_difference(arm_guard, guard_cutter)

        pauldron = ctx.boolean_union(pauldron, arm_guard)

        return pauldron

    def _add_decorative_elements(
        self, pauldron: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add decorative elements."""
        ctx = self.ctx
        height = dims.get("height", 0.15)

        # Gemstone indent on top
        pauldron = ctx.add_glyph_indent(
            pauldron,
            location=(0, 0, height * 0.7),
            size=0.012,
            depth=0.002,
        )

        return pauldron
