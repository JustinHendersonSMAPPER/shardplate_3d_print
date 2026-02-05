"""Shardplate sabaton (foot armor) generator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .base import SymmetricArmorPieceGenerator


@dataclass
class SabatonGenerator(SymmetricArmorPieceGenerator):
    """Generator for Shardplate sabatons (foot armor).

    Shardplate sabatons feature:
    - Full foot enclosure
    - Articulated toe plates
    - Ankle guard integration
    - Sole plate for ground contact
    """

    _base_name: str = "sabaton"
    side: str = "left"
    articulated_toes: bool = True

    @property
    def armor_type(self) -> str:
        return "sabaton"

    def generate_base(self) -> Any:
        """Generate the left sabaton."""
        dims = self.dimensions
        ctx = self.ctx

        foot_length = dims.get("length", 0.29)
        foot_width = dims.get("width", 0.12)
        ankle_circ = dims.get("ankle_circumference", 0.26)
        thickness = self.measurements.scaled(self.measurements.plate_thickness)

        # Main foot shell
        sabaton = self._create_foot_shell(dims, thickness)

        # Add toe section
        if self.articulated_toes:
            sabaton = self._add_articulated_toes(sabaton, dims, thickness)
        else:
            sabaton = self._add_solid_toe(sabaton, dims, thickness)

        # Add ankle cuff
        sabaton = self._add_ankle_cuff(sabaton, dims, thickness)

        # Add instep plate
        sabaton = self._add_instep_plate(sabaton, dims, thickness)

        # Add sole
        sabaton = self._add_sole(sabaton, dims, thickness)

        # Add heel guard
        sabaton = self._add_heel_guard(sabaton, dims, thickness)

        return sabaton

    def _create_foot_shell(self, dims: dict[str, float], thickness: float) -> Any:
        """Create the main foot armor shell."""
        ctx = self.ctx
        foot_length = dims.get("length", 0.29)
        foot_width = dims.get("width", 0.12)
        ankle_circ = dims.get("ankle_circumference", 0.26)

        # Create main foot body as elongated box with rounded edges
        outer_shell = ctx.create_cube(
            size=1.0,
            location=(0, 0, 0),
            name="SabatonOuter",
        )
        ctx.scale_object(
            outer_shell,
            (foot_width + thickness * 2, foot_length * 0.7, foot_width * 0.5 + thickness * 2),
        )
        outer_shell = ctx.add_bevel(outer_shell, width=thickness * 2, segments=4)

        # Inner cavity
        inner_shell = ctx.create_cube(
            size=1.0,
            location=(0, 0, thickness),
            name="SabatonInner",
        )
        ctx.scale_object(inner_shell, (foot_width, foot_length * 0.7 + 0.01, foot_width * 0.5))

        sabaton = ctx.boolean_difference(outer_shell, inner_shell, name="SabatonShell")

        # Cut bottom open for foot entry and ground contact
        bottom_cutter = ctx.create_cube(
            size=max(foot_length, foot_width) * 2,
            location=(0, 0, -foot_width * 0.5),
            name="BottomCutter",
        )
        sabaton = ctx.boolean_difference(sabaton, bottom_cutter)

        return sabaton

    def _add_articulated_toes(
        self, sabaton: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add articulated toe plates."""
        ctx = self.ctx
        foot_length = dims.get("length", 0.29)
        foot_width = dims.get("width", 0.12)

        toe_length = foot_length * 0.35
        num_segments = 3

        # Toe section tapers toward front
        for i in range(num_segments):
            y_pos = foot_length * 0.35 + i * toe_length / num_segments * 0.85
            taper = 1.0 - i * 0.15

            toe_segment = ctx.create_cube(
                size=1.0,
                location=(0, y_pos, foot_width * 0.15),
                name=f"ToeSegment_{i}",
            )
            ctx.scale_object(
                toe_segment,
                (
                    foot_width * taper + thickness * 2,
                    toe_length / num_segments * 0.9,
                    foot_width * 0.35 * taper + thickness * 2,
                ),
            )
            toe_segment = ctx.add_bevel(toe_segment, width=thickness, segments=2)

            sabaton = ctx.boolean_union(sabaton, toe_segment)

        return sabaton

    def _add_solid_toe(
        self, sabaton: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add solid toe cap (simpler print)."""
        ctx = self.ctx
        foot_length = dims.get("length", 0.29)
        foot_width = dims.get("width", 0.12)

        toe_cap = ctx.create_cube(
            size=1.0,
            location=(0, foot_length * 0.4, foot_width * 0.15),
            name="ToeCap",
        )
        ctx.scale_object(
            toe_cap,
            (foot_width * 0.9 + thickness * 2, foot_length * 0.3, foot_width * 0.35 + thickness * 2),
        )
        toe_cap = ctx.add_bevel(toe_cap, width=thickness * 1.5, segments=3)

        sabaton = ctx.boolean_union(sabaton, toe_cap)

        return sabaton

    def _add_ankle_cuff(
        self, sabaton: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add ankle cuff for greave connection."""
        ctx = self.ctx
        foot_length = dims.get("length", 0.29)
        foot_width = dims.get("width", 0.12)
        ankle_circ = dims.get("ankle_circumference", 0.26)

        ankle_radius = ankle_circ / (2 * math.pi) + thickness
        cuff_height = foot_width * 0.6

        # Ankle cuff cylinder
        cuff_outer = ctx.create_cylinder(
            radius=ankle_radius,
            depth=cuff_height,
            location=(0, -foot_length * 0.15, foot_width * 0.35),
            vertices=32,
            name="AnkleCuffOuter",
        )

        cuff_inner = ctx.create_cylinder(
            radius=ankle_radius - thickness,
            depth=cuff_height + 0.01,
            location=(0, -foot_length * 0.15, foot_width * 0.35),
            vertices=32,
            name="AnkleCuffInner",
        )

        cuff = ctx.boolean_difference(cuff_outer, cuff_inner, name="AnkleCuff")

        # Cut front opening for flexibility
        front_cutter = ctx.create_cube(
            size=ankle_radius,
            location=(0, -foot_length * 0.15 + ankle_radius * 0.7, foot_width * 0.35),
            name="CuffFrontCutter",
        )
        cuff = ctx.boolean_difference(cuff, front_cutter)

        sabaton = ctx.boolean_union(sabaton, cuff)

        # Add ankle guard ridges
        for side in [-1, 1]:
            guard = ctx.create_cube(
                size=1.0,
                location=(side * ankle_radius * 0.7, -foot_length * 0.15, foot_width * 0.5),
                name=f"AnkleGuard_{'L' if side < 0 else 'R'}",
            )
            ctx.scale_object(guard, (thickness * 3, ankle_radius * 0.5, cuff_height * 0.4))
            sabaton = ctx.boolean_union(sabaton, guard)

        return sabaton

    def _add_instep_plate(
        self, sabaton: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add top of foot (instep) plate."""
        ctx = self.ctx
        foot_length = dims.get("length", 0.29)
        foot_width = dims.get("width", 0.12)

        # Raised instep ridge
        instep = ctx.create_cube(
            size=1.0,
            location=(0, foot_length * 0.05, foot_width * 0.3),
            name="InstepPlate",
        )
        ctx.scale_object(instep, (foot_width * 0.6, foot_length * 0.35, thickness * 2))
        sabaton = ctx.boolean_union(sabaton, instep)

        # Lacing ridge detail
        if self.detail_level >= 2:
            lace_ridge = ctx.create_cube(
                size=1.0,
                location=(0, foot_length * 0.1, foot_width * 0.35),
                name="LaceRidge",
            )
            ctx.scale_object(lace_ridge, (thickness * 2, foot_length * 0.25, thickness))
            sabaton = ctx.boolean_union(sabaton, lace_ridge)

        return sabaton

    def _add_sole(self, sabaton: Any, dims: dict[str, float], thickness: float) -> Any:
        """Add sole plate for ground contact."""
        ctx = self.ctx
        foot_length = dims.get("length", 0.29)
        foot_width = dims.get("width", 0.12)

        # Sole plate
        sole = ctx.create_cube(
            size=1.0,
            location=(0, foot_length * 0.1, -foot_width * 0.25 - thickness),
            name="SolePlate",
        )
        ctx.scale_object(sole, (foot_width * 1.1, foot_length * 0.85, thickness * 2))

        sabaton = ctx.boolean_union(sabaton, sole)

        return sabaton

    def _add_heel_guard(
        self, sabaton: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add heel protection."""
        ctx = self.ctx
        foot_length = dims.get("length", 0.29)
        foot_width = dims.get("width", 0.12)

        # Heel cup
        heel = ctx.create_cube(
            size=1.0,
            location=(0, -foot_length * 0.3, foot_width * 0.1),
            name="HeelGuard",
        )
        ctx.scale_object(
            heel, (foot_width * 0.8 + thickness * 2, foot_length * 0.15, foot_width * 0.4)
        )
        heel = ctx.add_bevel(heel, width=thickness, segments=2)

        sabaton = ctx.boolean_union(sabaton, heel)

        # Heel ridge
        heel_ridge = ctx.create_cube(
            size=1.0,
            location=(0, -foot_length * 0.35, foot_width * 0.2),
            name="HeelRidge",
        )
        ctx.scale_object(heel_ridge, (foot_width * 0.4, thickness * 2, foot_width * 0.25))
        sabaton = ctx.boolean_union(sabaton, heel_ridge)

        return sabaton
