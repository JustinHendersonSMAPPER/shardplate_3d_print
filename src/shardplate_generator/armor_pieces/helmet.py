"""Shardplate helmet generator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .base import ArmorPieceGenerator


@dataclass
class HelmetGenerator(ArmorPieceGenerator):
    """Generator for Shardplate helmet.

    The Shardplate helmet features:
    - Full head enclosure with overlapping plates
    - Horizontal eye slit visor
    - Angular, imposing appearance
    - No gaps - seamless construction
    - Unique styling per suit (customizable)
    """

    name: str = "helmet"
    visor_style: str = "standard"  # standard, narrow, wide

    @property
    def armor_type(self) -> str:
        return "helmet"

    def generate(self) -> Any:
        """Generate the Shardplate helmet."""
        dims = self.dimensions
        ctx = self.ctx

        # Main dome - slightly elongated sphere for the skull
        inner_width = dims.get("inner_width", 0.18)
        inner_length = dims.get("inner_length", 0.22)
        inner_height = dims.get("inner_height", 0.26)
        thickness = self.measurements.scaled(self.measurements.plate_thickness)

        # Create outer shell
        outer_shell = ctx.create_uv_sphere(
            radius=1.0,
            location=(0, 0, 0),
            segments=48,
            ring_count=32,
            name="HelmetOuter",
        )
        ctx.scale_object(
            outer_shell,
            (
                (inner_width / 2 + thickness),
                (inner_length / 2 + thickness),
                (inner_height / 2 + thickness),
            ),
        )

        # Create inner cavity
        inner_cavity = ctx.create_uv_sphere(
            radius=1.0,
            location=(0, 0, -thickness / 2),  # Offset down slightly
            segments=48,
            ring_count=32,
            name="HelmetInner",
        )
        ctx.scale_object(
            inner_cavity, (inner_width / 2, inner_length / 2, inner_height / 2)
        )

        # Hollow out the helmet
        helmet = ctx.boolean_difference(outer_shell, inner_cavity, name="HelmetShell")

        # Cut open the bottom for head entry
        bottom_cutter = ctx.create_cube(
            size=max(inner_width, inner_length) * 1.5,
            location=(0, 0, -inner_height / 2 - 0.02),
            name="BottomCutter",
        )
        helmet = ctx.boolean_difference(helmet, bottom_cutter)

        # Create face plate with angular features
        helmet = self._add_face_plate(helmet, dims, thickness)

        # Add visor slit
        helmet = self._add_visor(helmet, dims)

        # Add angular ridge details
        helmet = self._add_helmet_ridges(helmet, dims, thickness)

        # Add neck guard
        helmet = self._add_neck_guard(helmet, dims, thickness)

        # Add decorative elements if high detail
        if self.detail_level >= 2:
            helmet = self._add_decorative_elements(helmet, dims)

        return helmet

    def _add_face_plate(
        self, helmet: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add angular face plate characteristic of Shardplate."""
        ctx = self.ctx
        inner_width = dims.get("inner_width", 0.18)
        inner_length = dims.get("inner_length", 0.22)
        inner_height = dims.get("inner_height", 0.26)

        # Create angular face plate extending forward
        face_plate = ctx.create_cube(
            size=1.0,
            location=(0, -inner_length / 2 - thickness, -inner_height / 6),
            name="FacePlate",
        )
        ctx.scale_object(face_plate, (inner_width * 0.8, thickness * 2, inner_height * 0.6))

        # Angle the face plate
        ctx.rotate_object(face_plate, (15, 0, 0))

        helmet = ctx.boolean_union(helmet, face_plate)

        # Add cheek guards
        for side in [-1, 1]:
            cheek = ctx.create_cube(
                size=1.0,
                location=(
                    side * inner_width / 2.5,
                    -inner_length / 3,
                    -inner_height / 5,
                ),
                name=f"CheekGuard_{'L' if side < 0 else 'R'}",
            )
            ctx.scale_object(cheek, (thickness * 3, inner_length / 4, inner_height / 3))
            ctx.rotate_object(cheek, (0, side * 15, 0))
            helmet = ctx.boolean_union(helmet, cheek)

        return helmet

    def _add_visor(self, helmet: Any, dims: dict[str, float]) -> Any:
        """Add the characteristic horizontal eye slit visor."""
        ctx = self.ctx
        inner_width = dims.get("inner_width", 0.18)
        inner_length = dims.get("inner_length", 0.22)
        visor_width = dims.get("visor_width", inner_width * 0.7)
        visor_height = dims.get("visor_height", 0.012)

        # Visor style adjustments
        if self.visor_style == "narrow":
            visor_height *= 0.6
        elif self.visor_style == "wide":
            visor_height *= 1.5
            visor_width *= 1.1

        # Create visor slit
        visor_slit = ctx.create_cube(
            size=1.0,
            location=(0, -inner_length / 2 - 0.01, 0.02),
            name="VisorSlit",
        )
        ctx.scale_object(visor_slit, (visor_width, inner_length / 3, visor_height))

        helmet = ctx.boolean_difference(helmet, visor_slit)

        # Add visor brow ridge
        brow_ridge = ctx.create_cube(
            size=1.0,
            location=(0, -inner_length / 2 - 0.005, 0.02 + visor_height),
            name="BrowRidge",
        )
        ctx.scale_object(
            brow_ridge, (visor_width * 1.1, inner_length / 6, visor_height * 0.5)
        )
        helmet = ctx.boolean_union(helmet, brow_ridge)

        return helmet

    def _add_helmet_ridges(
        self, helmet: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add angular ridges characteristic of Shardplate."""
        ctx = self.ctx
        inner_width = dims.get("inner_width", 0.18)
        inner_height = dims.get("inner_height", 0.26)

        # Central crest ridge
        crest = ctx.create_cube(
            size=1.0,
            location=(0, 0, inner_height / 2 + thickness / 2),
            name="CentralCrest",
        )
        ctx.scale_object(crest, (thickness * 2, inner_height * 0.6, thickness * 1.5))
        helmet = ctx.boolean_union(helmet, crest)

        # Side ridges
        if self.detail_level >= 2:
            for side in [-1, 1]:
                ridge = ctx.create_cube(
                    size=1.0,
                    location=(
                        side * inner_width / 3,
                        inner_height / 6,
                        inner_height / 3,
                    ),
                    name=f"SideRidge_{'L' if side < 0 else 'R'}",
                )
                ctx.scale_object(ridge, (thickness, inner_height * 0.4, thickness))
                ctx.rotate_object(ridge, (30, side * 20, 0))
                helmet = ctx.boolean_union(helmet, ridge)

        return helmet

    def _add_neck_guard(
        self, helmet: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add neck protection plates."""
        ctx = self.ctx
        inner_width = dims.get("inner_width", 0.18)
        inner_length = dims.get("inner_length", 0.22)
        inner_height = dims.get("inner_height", 0.26)

        # Rear neck guard
        neck_guard = ctx.create_cube(
            size=1.0,
            location=(0, inner_length / 3, -inner_height / 2.5),
            name="NeckGuard",
        )
        ctx.scale_object(neck_guard, (inner_width * 0.9, inner_length / 3, inner_height / 4))
        ctx.rotate_object(neck_guard, (-20, 0, 0))
        helmet = ctx.boolean_union(helmet, neck_guard)

        # Side neck plates
        for side in [-1, 1]:
            side_plate = ctx.create_cube(
                size=1.0,
                location=(
                    side * inner_width / 2.5,
                    inner_length / 6,
                    -inner_height / 3,
                ),
                name=f"NeckSide_{'L' if side < 0 else 'R'}",
            )
            ctx.scale_object(side_plate, (thickness * 2, inner_length / 4, inner_height / 5))
            ctx.rotate_object(side_plate, (-10, side * 30, 0))
            helmet = ctx.boolean_union(helmet, side_plate)

        return helmet

    def _add_decorative_elements(self, helmet: Any, dims: dict[str, float]) -> Any:
        """Add decorative elements like glyph indents for gemstones."""
        ctx = self.ctx
        inner_width = dims.get("inner_width", 0.18)
        inner_height = dims.get("inner_height", 0.26)

        # Forehead glyph indent (for gemstone placement)
        helmet = ctx.add_glyph_indent(
            helmet,
            location=(0, -inner_width / 2 - 0.01, inner_height / 4),
            size=0.015,
            depth=0.002,
        )

        # Side decorative indents
        if self.detail_level >= 3:
            for side in [-1, 1]:
                helmet = ctx.add_glyph_indent(
                    helmet,
                    location=(side * inner_width / 2.2, 0, inner_height / 5),
                    size=0.01,
                    depth=0.001,
                )

        return helmet

    def generate_printable_parts(self) -> list[tuple[str, Any]]:
        """Generate helmet split into printable parts."""
        dims = self.dimensions
        full_helmet = self.generate()

        # For large prints, split into front and back halves
        inner_length = dims.get("inner_length", 0.22)

        # Create cutting plane
        cutter = self.ctx.create_cube(
            size=max(dims.values()) * 2,
            location=(0, 0, 0),
            name="Cutter",
        )

        # Front half
        front_cutter = self.ctx.duplicate_object(cutter, "FrontCutter")
        self.ctx.move_object(front_cutter, (0, inner_length / 2, 0))
        front_half = self.ctx.duplicate_object(full_helmet, "HelmetFront")
        front_half = self.ctx.boolean_difference(front_half, front_cutter)

        # Back half
        back_cutter = self.ctx.duplicate_object(cutter, "BackCutter")
        self.ctx.move_object(back_cutter, (0, -inner_length / 2, 0))
        back_half = self.ctx.duplicate_object(full_helmet, "HelmetBack")
        back_half = self.ctx.boolean_difference(back_half, back_cutter)

        # Clean up
        self.ctx.bpy.data.objects.remove(cutter, do_unlink=True)

        return [("helmet_front", front_half), ("helmet_back", back_half)]
