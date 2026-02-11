"""Shardplate cuisse (thigh armor) generator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .base import SymmetricArmorPieceGenerator


@dataclass
class CuisseGenerator(SymmetricArmorPieceGenerator):
    """Generator for Shardplate cuisses (thigh armor).

    Shardplate cuisses feature:
    - Full thigh coverage
    - Articulated knee cop
    - Belt attachment at top
    - Connection to greaves at knee
    """

    _base_name: str = "cuisse"
    side: str = "left"

    @property
    def armor_type(self) -> str:
        return "cuisse"

    def generate_base(self) -> Any:
        """Generate the left cuisse."""
        dims = self.dimensions
        ctx = self.ctx

        length = dims.get("length", 0.47)
        upper_circ = dims.get("upper_circumference", 0.60)
        lower_circ = dims.get("lower_circumference", 0.42)
        thickness = self.measurements.scaled(self.measurements.plate_thickness)

        # Main thigh shell
        cuisse = self._create_thigh_shell(dims, thickness)

        # Add knee cop (poleyn)
        cuisse = self._add_knee_cop(cuisse, dims, thickness)

        # Add front plate detail
        cuisse = self._add_front_plates(cuisse, dims, thickness)

        # Add side plates
        cuisse = self._add_side_plates(cuisse, dims, thickness)

        # Add belt attachment
        cuisse = self._add_belt_attachment(cuisse, dims, thickness)

        return cuisse

    def generate_segments_base(self) -> dict[str, Any]:
        """Generate segmented cuisse: thigh shell + knee cop (separate)."""
        dims = self.dimensions
        ctx = self.ctx
        thickness = self.measurements.scaled(self.measurements.plate_thickness)
        length = dims.get("length", 0.47)
        lower_circ = dims.get("lower_circumference", 0.42)
        lower_radius = lower_circ / (2 * math.pi)

        # --- Segment 1: Thigh shell ---
        thigh_shell = self._create_thigh_shell(dims, thickness)
        thigh_shell = self._add_front_plates(thigh_shell, dims, thickness)
        thigh_shell = self._add_side_plates(thigh_shell, dims, thickness)
        thigh_shell = self._add_belt_attachment(thigh_shell, dims, thickness)

        # Add pin holes at knee junction (bottom of thigh shell)
        for x_off in [-lower_radius * 0.3, lower_radius * 0.3]:
            thigh_shell = ctx.create_alignment_pin_hole(
                thigh_shell,
                location=(x_off, -length / 2, lower_radius * 0.2),
                direction=(0, -1, 0),
            )

        thigh_shell = self.add_shardplate_details(thigh_shell)
        thigh_shell.name = f"{self._base_name}_thigh_left"

        # --- Segment 2: Knee cop (separate for articulation) ---
        knee_cop = self._create_knee_cop_standalone(dims, thickness)

        # Add pin posts to mate with thigh shell
        for x_off in [-lower_radius * 0.3, lower_radius * 0.3]:
            knee_cop = ctx.create_alignment_pin_post(
                knee_cop,
                location=(x_off, -length / 2 + 0.001, lower_radius * 0.2),
                direction=(0, -1, 0),
            )

        knee_cop = self.add_shardplate_details(knee_cop)
        knee_cop.name = f"{self._base_name}_knee_left"

        return {
            f"{self._base_name}_thigh_left": thigh_shell,
            f"{self._base_name}_knee_left": knee_cop,
        }

    def _create_thigh_shell(self, dims: dict[str, float], thickness: float) -> Any:
        """Create the main thigh armor shell."""
        ctx = self.ctx
        length = dims.get("length", 0.47)
        upper_circ = dims.get("upper_circumference", 0.60)
        lower_circ = dims.get("lower_circumference", 0.42)

        upper_radius = upper_circ / (2 * math.pi) + thickness
        lower_radius = lower_circ / (2 * math.pi) + thickness

        # Tapered cylinder for thigh
        outer_shell = ctx.create_cone(
            radius1=upper_radius,
            radius2=lower_radius,
            depth=length,
            location=(0, 0, 0),
            vertices=48,
            name="CuisseOuter",
        )

        inner_shell = ctx.create_cone(
            radius1=upper_radius - thickness,
            radius2=lower_radius - thickness,
            depth=length + 0.01,
            location=(0, 0, 0),
            vertices=48,
            name="CuisseInner",
        )

        cuisse = ctx.boolean_difference(outer_shell, inner_shell, name="CuisseShell")
        ctx.rotate_object(cuisse, (90, 0, 0))

        return cuisse

    def _add_knee_cop(
        self, cuisse: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add knee cop (poleyn) protection (boolean-unioned into main mesh)."""
        ctx = self.ctx
        length = dims.get("length", 0.47)
        lower_circ = dims.get("lower_circumference", 0.42)

        knee_radius = lower_circ / (2 * math.pi) * 1.3

        # Knee dome
        knee_cop = ctx.create_uv_sphere(
            radius=knee_radius,
            location=(0, -length / 2 - knee_radius * 0.2, knee_radius * 0.3),
            segments=32,
            ring_count=16,
            name="KneeCop",
        )

        # Cut to dome shape
        cop_cutter = ctx.create_cube(
            size=knee_radius * 3,
            location=(0, -length / 2 - knee_radius * 0.2, -knee_radius),
            name="CopCutter",
        )
        knee_cop = ctx.boolean_difference(knee_cop, cop_cutter)

        # Back cutter
        back_cutter = ctx.create_cube(
            size=knee_radius * 3,
            location=(0, -length / 2 + knee_radius, knee_radius * 0.3),
            name="BackCutter",
        )
        knee_cop = ctx.boolean_difference(knee_cop, back_cutter)

        # Hollow
        inner_cop = ctx.create_uv_sphere(
            radius=knee_radius - thickness,
            location=(0, -length / 2 - knee_radius * 0.2, knee_radius * 0.3),
            segments=32,
            ring_count=16,
            name="KneeInner",
        )
        knee_cop = ctx.boolean_difference(knee_cop, inner_cop)

        cuisse = ctx.boolean_union(cuisse, knee_cop)

        # Add knee point
        knee_point = ctx.create_cone(
            radius1=knee_radius * 0.25,
            radius2=0,
            depth=knee_radius * 0.3,
            location=(0, -length / 2 - knee_radius * 0.4, knee_radius * 0.6),
            vertices=12,
            name="KneePoint",
        )
        cuisse = ctx.boolean_union(cuisse, knee_point)

        # Add side wings on knee cop
        for side in [-1, 1]:
            wing = ctx.create_cube(
                size=1.0,
                location=(side * knee_radius * 0.7, -length / 2 - knee_radius * 0.1, knee_radius * 0.2),
                name=f"KneeWing_{'L' if side < 0 else 'R'}",
            )
            ctx.scale_object(wing, (knee_radius * 0.3, knee_radius * 0.6, knee_radius * 0.4))
            ctx.rotate_object(wing, (0, side * 20, 0))
            cuisse = ctx.boolean_union(cuisse, wing)

        return cuisse

    def _create_knee_cop_standalone(
        self, dims: dict[str, float], thickness: float
    ) -> Any:
        """Create knee cop as a standalone segment."""
        ctx = self.ctx
        length = dims.get("length", 0.47)
        lower_circ = dims.get("lower_circumference", 0.42)
        knee_radius = lower_circ / (2 * math.pi) * 1.3

        knee_cop = ctx.create_uv_sphere(
            radius=knee_radius,
            location=(0, -length / 2 - knee_radius * 0.2, knee_radius * 0.3),
            segments=32,
            ring_count=16,
            name="KneeCopSeg",
        )

        cop_cutter = ctx.create_cube(
            size=knee_radius * 3,
            location=(0, -length / 2 - knee_radius * 0.2, -knee_radius),
            name="CopCutter",
        )
        knee_cop = ctx.boolean_difference(knee_cop, cop_cutter)

        back_cutter = ctx.create_cube(
            size=knee_radius * 3,
            location=(0, -length / 2 + knee_radius, knee_radius * 0.3),
            name="BackCutter",
        )
        knee_cop = ctx.boolean_difference(knee_cop, back_cutter)

        inner_cop = ctx.create_uv_sphere(
            radius=knee_radius - thickness,
            location=(0, -length / 2 - knee_radius * 0.2, knee_radius * 0.3),
            segments=32,
            ring_count=16,
            name="KneeInner",
        )
        knee_cop = ctx.boolean_difference(knee_cop, inner_cop)

        knee_point = ctx.create_cone(
            radius1=knee_radius * 0.25,
            radius2=0,
            depth=knee_radius * 0.3,
            location=(0, -length / 2 - knee_radius * 0.4, knee_radius * 0.6),
            vertices=12,
            name="KneePoint",
        )
        knee_cop = ctx.boolean_union(knee_cop, knee_point)

        for side in [-1, 1]:
            wing = ctx.create_cube(
                size=1.0,
                location=(side * knee_radius * 0.7, -length / 2 - knee_radius * 0.1, knee_radius * 0.2),
                name=f"KneeWing_{'L' if side < 0 else 'R'}",
            )
            ctx.scale_object(wing, (knee_radius * 0.3, knee_radius * 0.6, knee_radius * 0.4))
            ctx.rotate_object(wing, (0, side * 20, 0))
            knee_cop = ctx.boolean_union(knee_cop, wing)

        return knee_cop

    def _add_front_plates(
        self, cuisse: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add front thigh plate details."""
        ctx = self.ctx
        length = dims.get("length", 0.47)
        upper_circ = dims.get("upper_circumference", 0.60)

        upper_radius = upper_circ / (2 * math.pi)

        # Central front ridge
        front_ridge = ctx.create_cube(
            size=1.0,
            location=(0, length * 0.1, upper_radius),
            name="FrontRidge",
        )
        ctx.scale_object(front_ridge, (thickness * 3, length * 0.6, thickness * 2))
        cuisse = ctx.boolean_union(cuisse, front_ridge)

        # Decorative plate lines
        if self.detail_level >= 2:
            for i in range(3):
                y_pos = length * 0.3 - i * length * 0.2
                plate_line = ctx.create_cube(
                    size=1.0,
                    location=(0, y_pos, upper_radius * 0.95),
                    name=f"PlateLine_{i}",
                )
                ctx.scale_object(plate_line, (upper_radius * 1.2, thickness, thickness))
                cuisse = ctx.boolean_union(cuisse, plate_line)

        return cuisse

    def _add_side_plates(
        self, cuisse: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add side protection plates."""
        ctx = self.ctx
        length = dims.get("length", 0.47)
        upper_circ = dims.get("upper_circumference", 0.60)

        upper_radius = upper_circ / (2 * math.pi)

        # Outer side plate (larger)
        outer_plate = ctx.create_cube(
            size=1.0,
            location=(-upper_radius * 0.8, length * 0.1, 0),
            name="OuterSidePlate",
        )
        ctx.scale_object(outer_plate, (thickness * 2, length * 0.5, upper_radius * 0.8))
        cuisse = ctx.boolean_union(cuisse, outer_plate)

        return cuisse

    def _add_belt_attachment(
        self, cuisse: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add belt attachment point at top."""
        ctx = self.ctx
        length = dims.get("length", 0.47)
        upper_circ = dims.get("upper_circumference", 0.60)

        upper_radius = upper_circ / (2 * math.pi)

        # Belt loop/attachment tab
        belt_tab = ctx.create_cube(
            size=1.0,
            location=(0, length / 2 + thickness * 2, upper_radius * 0.5),
            name="BeltTab",
        )
        ctx.scale_object(belt_tab, (upper_radius * 0.4, thickness * 4, thickness * 3))
        cuisse = ctx.boolean_union(cuisse, belt_tab)

        return cuisse
