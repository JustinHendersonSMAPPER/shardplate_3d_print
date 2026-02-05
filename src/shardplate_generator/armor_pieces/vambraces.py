"""Shardplate vambrace (forearm armor) generator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .base import SymmetricArmorPieceGenerator


@dataclass
class VambraceGenerator(SymmetricArmorPieceGenerator):
    """Generator for Shardplate vambraces (forearm armor).

    Shardplate vambraces feature:
    - Full forearm enclosure
    - Elbow articulation plates
    - Connection to gauntlet at wrist
    - Overlapping plate design
    """

    _base_name: str = "vambrace"
    side: str = "left"

    @property
    def armor_type(self) -> str:
        return "vambrace"

    def generate_base(self) -> Any:
        """Generate the left vambrace."""
        dims = self.dimensions
        ctx = self.ctx

        length = dims.get("length", 0.28)
        upper_circ = dims.get("upper_circumference", 0.30)
        lower_circ = dims.get("lower_circumference", 0.19)
        thickness = self.measurements.scaled(self.measurements.plate_thickness)

        # Main forearm shell - tapered cylinder
        vambrace = self._create_tapered_shell(dims, thickness)

        # Add elbow cup
        vambrace = self._add_elbow_cup(vambrace, dims, thickness)

        # Add overlapping plates
        vambrace = self._add_plate_segments(vambrace, dims, thickness)

        # Add ridge details
        vambrace = self._add_ridge_details(vambrace, dims, thickness)

        # Add wrist flare
        vambrace = self._add_wrist_section(vambrace, dims, thickness)

        return vambrace

    def _create_tapered_shell(self, dims: dict[str, float], thickness: float) -> Any:
        """Create the main tapered forearm shell."""
        ctx = self.ctx
        length = dims.get("length", 0.28)
        upper_circ = dims.get("upper_circumference", 0.30)
        lower_circ = dims.get("lower_circumference", 0.19)

        upper_radius = upper_circ / (2 * math.pi) + thickness
        lower_radius = lower_circ / (2 * math.pi) + thickness

        # Create tapered cone for outer shell
        outer_shell = ctx.create_cone(
            radius1=upper_radius,
            radius2=lower_radius,
            depth=length,
            location=(0, 0, 0),
            vertices=48,
            name="VambraceOuter",
        )

        # Inner cavity (slightly smaller taper)
        inner_shell = ctx.create_cone(
            radius1=upper_radius - thickness,
            radius2=lower_radius - thickness,
            depth=length + 0.01,
            location=(0, 0, 0),
            vertices=48,
            name="VambraceInner",
        )

        vambrace = ctx.boolean_difference(outer_shell, inner_shell, name="VambraceShell")

        # Rotate to orient along arm (Y axis)
        ctx.rotate_object(vambrace, (90, 0, 0))

        return vambrace

    def _add_elbow_cup(
        self, vambrace: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add elbow protection cup."""
        ctx = self.ctx
        length = dims.get("length", 0.28)
        upper_circ = dims.get("upper_circumference", 0.30)

        elbow_radius = upper_circ / (2 * math.pi) * 1.2

        # Elbow cup dome
        elbow_cup = ctx.create_uv_sphere(
            radius=elbow_radius,
            location=(0, length / 2 + elbow_radius * 0.3, 0),
            segments=24,
            ring_count=12,
            name="ElbowCup",
        )

        # Cut to half sphere
        cup_cutter = ctx.create_cube(
            size=elbow_radius * 3,
            location=(0, length / 2 + elbow_radius * 1.3, 0),
            name="CupCutter",
        )
        elbow_cup = ctx.boolean_difference(elbow_cup, cup_cutter)

        # Hollow it out
        inner_cup = ctx.create_uv_sphere(
            radius=elbow_radius - thickness,
            location=(0, length / 2 + elbow_radius * 0.3, 0),
            segments=24,
            ring_count=12,
            name="ElbowInner",
        )
        elbow_cup = ctx.boolean_difference(elbow_cup, inner_cup)

        vambrace = ctx.boolean_union(vambrace, elbow_cup)

        # Add elbow point
        elbow_point = ctx.create_cone(
            radius1=elbow_radius * 0.3,
            radius2=0,
            depth=elbow_radius * 0.4,
            location=(0, length / 2 + elbow_radius * 0.5, 0),
            vertices=16,
            name="ElbowPoint",
        )
        ctx.rotate_object(elbow_point, (-90, 0, 0))
        vambrace = ctx.boolean_union(vambrace, elbow_point)

        return vambrace

    def _add_plate_segments(
        self, vambrace: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add overlapping plate segment details."""
        ctx = self.ctx
        length = dims.get("length", 0.28)
        upper_circ = dims.get("upper_circumference", 0.30)
        lower_circ = dims.get("lower_circumference", 0.19)

        if self.detail_level < 2:
            return vambrace

        # Add 3 overlapping ridge lines
        num_ridges = 3
        for i in range(num_ridges):
            y_pos = length * 0.1 - i * length * 0.25
            # Interpolate radius
            t = (length / 2 - y_pos) / length + 0.5
            radius = upper_circ / (2 * math.pi) * (1 - t) + lower_circ / (2 * math.pi) * t

            ridge = ctx.create_torus(
                major_radius=radius + thickness * 0.5,
                minor_radius=thickness * 0.8,
                location=(0, y_pos, 0),
                major_segments=32,
                minor_segments=8,
                name=f"PlateRidge_{i}",
            )
            ctx.rotate_object(ridge, (90, 0, 0))
            vambrace = ctx.boolean_union(vambrace, ridge)

        return vambrace

    def _add_ridge_details(
        self, vambrace: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add angular ridge details along the vambrace."""
        ctx = self.ctx
        length = dims.get("length", 0.28)
        upper_circ = dims.get("upper_circumference", 0.30)

        upper_radius = upper_circ / (2 * math.pi)

        # Central ridge on top of forearm
        ridge = ctx.create_cube(
            size=1.0,
            location=(0, 0, upper_radius),
            name="CentralRidge",
        )
        ctx.scale_object(ridge, (thickness * 2, length * 0.7, thickness * 2))
        vambrace = ctx.boolean_union(vambrace, ridge)

        return vambrace

    def _add_wrist_section(
        self, vambrace: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add wrist flare for gauntlet connection."""
        ctx = self.ctx
        length = dims.get("length", 0.28)
        lower_circ = dims.get("lower_circumference", 0.19)

        wrist_radius = lower_circ / (2 * math.pi)

        # Wrist flare ring
        wrist_flare = ctx.create_torus(
            major_radius=wrist_radius + thickness,
            minor_radius=thickness * 1.5,
            location=(0, -length / 2, 0),
            major_segments=32,
            minor_segments=8,
            name="WristFlare",
        )
        ctx.rotate_object(wrist_flare, (90, 0, 0))
        vambrace = ctx.boolean_union(vambrace, wrist_flare)

        return vambrace
