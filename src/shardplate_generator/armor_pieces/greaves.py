"""Shardplate greave (shin armor) generator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .base import SymmetricArmorPieceGenerator


@dataclass
class GreaveGenerator(SymmetricArmorPieceGenerator):
    """Generator for Shardplate greaves (shin/calf armor).

    Shardplate greaves feature:
    - Full lower leg coverage
    - Knee connection from cuisse
    - Ankle transition to sabaton
    - Front shin plate reinforcement
    """

    _base_name: str = "greave"
    side: str = "left"

    @property
    def armor_type(self) -> str:
        return "greave"

    def generate_base(self) -> Any:
        """Generate the left greave."""
        dims = self.dimensions
        ctx = self.ctx

        length = dims.get("length", 0.42)
        upper_circ = dims.get("upper_circumference", 0.42)
        lower_circ = dims.get("lower_circumference", 0.26)
        thickness = self.measurements.scaled(self.measurements.plate_thickness)

        # Main shin shell
        greave = self._create_shin_shell(dims, thickness)

        # Add shin plate
        greave = self._add_shin_plate(greave, dims, thickness)

        # Add calf plate
        greave = self._add_calf_plate(greave, dims, thickness)

        # Add knee connection flare
        greave = self._add_knee_flare(greave, dims, thickness)

        # Add ankle section
        greave = self._add_ankle_section(greave, dims, thickness)

        # Add ridge details
        if self.detail_level >= 2:
            greave = self._add_ridge_details(greave, dims, thickness)

        return greave

    def generate_segments_base(self) -> dict[str, Any]:
        """Generate segmented greave: shin shell + calf plate."""
        dims = self.dimensions
        ctx = self.ctx
        thickness = self.measurements.scaled(self.measurements.plate_thickness)
        length = dims.get("length", 0.42)
        upper_circ = dims.get("upper_circumference", 0.42)
        upper_radius = upper_circ / (2 * math.pi)

        # --- Segment 1: Shin shell (includes shin plate, knee flare, ankle) ---
        shin_shell = self._create_shin_shell(dims, thickness)
        shin_shell = self._add_shin_plate(shin_shell, dims, thickness)
        shin_shell = self._add_knee_flare(shin_shell, dims, thickness)
        shin_shell = self._add_ankle_section(shin_shell, dims, thickness)
        if self.detail_level >= 2:
            shin_shell = self._add_ridge_details(shin_shell, dims, thickness)

        # Add pin holes for calf plate attachment
        for x_off in [-upper_radius * 0.3, upper_radius * 0.3]:
            shin_shell = ctx.create_alignment_pin_hole(
                shin_shell,
                location=(x_off, length * 0.15, -upper_radius * 0.5),
                direction=(0, 0, -1),
            )

        shin_shell = self.add_shardplate_details(shin_shell)
        shin_shell.name = f"{self._base_name}_shin_left"

        # --- Segment 2: Calf plate (separate for print orientation) ---
        calf_plate = self._create_calf_plate_standalone(dims, thickness)

        # Add pin posts to mate with shin shell
        for x_off in [-upper_radius * 0.3, upper_radius * 0.3]:
            calf_plate = ctx.create_alignment_pin_post(
                calf_plate,
                location=(x_off, length * 0.15, -upper_radius * 0.5 + 0.001),
                direction=(0, 0, -1),
            )

        calf_plate = self.add_shardplate_details(calf_plate)
        calf_plate.name = f"{self._base_name}_calf_left"

        return {
            f"{self._base_name}_shin_left": shin_shell,
            f"{self._base_name}_calf_left": calf_plate,
        }

    def _create_shin_shell(self, dims: dict[str, float], thickness: float) -> Any:
        """Create the main shin armor shell."""
        ctx = self.ctx
        length = dims.get("length", 0.42)
        upper_circ = dims.get("upper_circumference", 0.42)
        lower_circ = dims.get("lower_circumference", 0.26)

        upper_radius = upper_circ / (2 * math.pi) + thickness
        lower_radius = lower_circ / (2 * math.pi) + thickness

        # Tapered cylinder
        outer_shell = ctx.create_cone(
            radius1=upper_radius,
            radius2=lower_radius,
            depth=length,
            location=(0, 0, 0),
            vertices=48,
            name="GreaveOuter",
        )

        inner_shell = ctx.create_cone(
            radius1=upper_radius - thickness,
            radius2=lower_radius - thickness,
            depth=length + 0.01,
            location=(0, 0, 0),
            vertices=48,
            name="GreaveInner",
        )

        greave = ctx.boolean_difference(outer_shell, inner_shell, name="GreaveShell")
        ctx.rotate_object(greave, (90, 0, 0))

        return greave

    def _add_shin_plate(
        self, greave: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add reinforced front shin plate."""
        ctx = self.ctx
        length = dims.get("length", 0.42)
        upper_circ = dims.get("upper_circumference", 0.42)

        upper_radius = upper_circ / (2 * math.pi)

        # Main shin guard plate
        shin_plate = ctx.create_cube(
            size=1.0,
            location=(0, 0, upper_radius + thickness),
            name="ShinPlate",
        )
        ctx.scale_object(shin_plate, (upper_radius * 0.8, length * 0.85, thickness * 3))

        # Round the front edges
        shin_plate = ctx.add_bevel(shin_plate, width=thickness, segments=3)

        greave = ctx.boolean_union(greave, shin_plate)

        # Central ridge
        ridge = ctx.create_cube(
            size=1.0,
            location=(0, 0, upper_radius + thickness * 3),
            name="ShinRidge",
        )
        ctx.scale_object(ridge, (thickness * 2, length * 0.7, thickness * 2))
        greave = ctx.boolean_union(greave, ridge)

        return greave

    def _add_calf_plate(
        self, greave: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add calf muscle protection plate (boolean-unioned into main mesh)."""
        ctx = self.ctx
        length = dims.get("length", 0.42)
        upper_circ = dims.get("upper_circumference", 0.42)

        upper_radius = upper_circ / (2 * math.pi)

        # Calf bulge plate
        calf_plate = ctx.create_uv_sphere(
            radius=upper_radius * 0.6,
            location=(0, length * 0.15, -upper_radius * 0.7),
            segments=24,
            ring_count=12,
            name="CalfPlate",
        )

        # Cut to partial sphere
        calf_cutter = ctx.create_cube(
            size=upper_radius * 2,
            location=(0, length * 0.15, -upper_radius * 1.5),
            name="CalfCutter",
        )
        calf_plate = ctx.boolean_difference(calf_plate, calf_cutter)

        # Hollow
        calf_inner = ctx.create_uv_sphere(
            radius=upper_radius * 0.6 - thickness,
            location=(0, length * 0.15, -upper_radius * 0.7),
            segments=24,
            ring_count=12,
            name="CalfInner",
        )
        calf_plate = ctx.boolean_difference(calf_plate, calf_inner)

        greave = ctx.boolean_union(greave, calf_plate)

        return greave

    def _create_calf_plate_standalone(
        self, dims: dict[str, float], thickness: float
    ) -> Any:
        """Create calf plate as a standalone segment."""
        ctx = self.ctx
        length = dims.get("length", 0.42)
        upper_circ = dims.get("upper_circumference", 0.42)
        upper_radius = upper_circ / (2 * math.pi)

        calf_plate = ctx.create_uv_sphere(
            radius=upper_radius * 0.6,
            location=(0, length * 0.15, -upper_radius * 0.7),
            segments=24,
            ring_count=12,
            name="CalfPlateSeg",
        )

        calf_cutter = ctx.create_cube(
            size=upper_radius * 2,
            location=(0, length * 0.15, -upper_radius * 1.5),
            name="CalfCutter",
        )
        calf_plate = ctx.boolean_difference(calf_plate, calf_cutter)

        calf_inner = ctx.create_uv_sphere(
            radius=upper_radius * 0.6 - thickness,
            location=(0, length * 0.15, -upper_radius * 0.7),
            segments=24,
            ring_count=12,
            name="CalfInner",
        )
        calf_plate = ctx.boolean_difference(calf_plate, calf_inner)

        return calf_plate

    def _add_knee_flare(
        self, greave: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add flared top for knee cop connection."""
        ctx = self.ctx
        length = dims.get("length", 0.42)
        upper_circ = dims.get("upper_circumference", 0.42)

        upper_radius = upper_circ / (2 * math.pi)

        # Flared rim at top
        flare = ctx.create_torus(
            major_radius=upper_radius + thickness * 2,
            minor_radius=thickness * 2,
            location=(0, length / 2, 0),
            major_segments=32,
            minor_segments=8,
            name="KneeFlare",
        )
        ctx.rotate_object(flare, (90, 0, 0))
        greave = ctx.boolean_union(greave, flare)

        return greave

    def _add_ankle_section(
        self, greave: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add ankle transition section."""
        ctx = self.ctx
        length = dims.get("length", 0.42)
        lower_circ = dims.get("lower_circumference", 0.26)

        lower_radius = lower_circ / (2 * math.pi)

        # Ankle guard plates on sides
        for side in [-1, 1]:
            ankle_plate = ctx.create_cube(
                size=1.0,
                location=(side * lower_radius * 0.8, -length / 2 + thickness * 2, 0),
                name=f"AnklePlate_{'L' if side < 0 else 'R'}",
            )
            ctx.scale_object(ankle_plate, (thickness * 3, thickness * 6, lower_radius * 0.6))
            greave = ctx.boolean_union(greave, ankle_plate)

        # Ankle rim
        ankle_rim = ctx.create_torus(
            major_radius=lower_radius + thickness,
            minor_radius=thickness,
            location=(0, -length / 2, 0),
            major_segments=32,
            minor_segments=8,
            name="AnkleRim",
        )
        ctx.rotate_object(ankle_rim, (90, 0, 0))
        greave = ctx.boolean_union(greave, ankle_rim)

        return greave

    def _add_ridge_details(
        self, greave: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add decorative ridge details."""
        ctx = self.ctx
        length = dims.get("length", 0.42)
        upper_circ = dims.get("upper_circumference", 0.42)

        upper_radius = upper_circ / (2 * math.pi)

        # Horizontal plate separation ridges
        for i in range(2):
            y_pos = length * 0.2 - i * length * 0.35
            ridge = ctx.create_torus(
                major_radius=upper_radius * (0.95 - i * 0.1),
                minor_radius=thickness * 0.6,
                location=(0, y_pos, 0),
                major_segments=32,
                minor_segments=6,
                name=f"DetailRidge_{i}",
            )
            ctx.rotate_object(ridge, (90, 0, 0))

            # Only keep front half
            ridge_cutter = ctx.create_cube(
                size=upper_radius * 3,
                location=(0, y_pos, -upper_radius),
                name=f"RidgeCutter_{i}",
            )
            ridge = ctx.boolean_difference(ridge, ridge_cutter)

            greave = ctx.boolean_union(greave, ridge)

        return greave
