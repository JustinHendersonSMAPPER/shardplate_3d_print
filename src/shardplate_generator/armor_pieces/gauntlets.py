"""Shardplate gauntlet (hand armor) generator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .base import SymmetricArmorPieceGenerator


@dataclass
class GauntletGenerator(SymmetricArmorPieceGenerator):
    """Generator for Shardplate gauntlets (hand armor).

    Shardplate gauntlets feature:
    - Articulated finger plates
    - Reinforced knuckles
    - Palm protection
    - Wrist guard integration
    - Full hand enclosure with no gaps
    """

    _base_name: str = "gauntlet"
    side: str = "left"
    articulated_fingers: bool = True

    @property
    def armor_type(self) -> str:
        return "gauntlet"

    def generate_base(self) -> Any:
        """Generate the left gauntlet."""
        dims = self.dimensions
        ctx = self.ctx

        hand_length = dims.get("hand_length", 0.21)
        hand_width = dims.get("hand_width", 0.11)
        wrist_circ = dims.get("wrist_circumference", 0.19)
        thickness = self.measurements.scaled(self.measurements.plate_thickness)

        # Create main hand shell
        gauntlet = self._create_hand_shell(dims, thickness)

        # Add finger plates
        if self.articulated_fingers:
            gauntlet = self._add_articulated_fingers(gauntlet, dims, thickness)
        else:
            gauntlet = self._add_mitten_style(gauntlet, dims, thickness)

        # Add thumb
        gauntlet = self._add_thumb(gauntlet, dims, thickness)

        # Add knuckle reinforcement
        gauntlet = self._add_knuckle_plates(gauntlet, dims, thickness)

        # Add wrist cuff
        gauntlet = self._add_wrist_cuff(gauntlet, dims, thickness)

        # Add palm plate
        gauntlet = self._add_palm_plate(gauntlet, dims, thickness)

        return gauntlet

    def _create_hand_shell(self, dims: dict[str, float], thickness: float) -> Any:
        """Create the main hand shell."""
        ctx = self.ctx
        hand_length = dims.get("hand_length", 0.21)
        hand_width = dims.get("hand_width", 0.11)

        # Main hand body (palm area)
        outer_hand = ctx.create_cube(
            size=1.0,
            location=(0, 0, 0),
            name="HandOuter",
        )
        ctx.scale_object(outer_hand, (hand_width + thickness * 2, hand_length * 0.5, hand_width * 0.4 + thickness * 2))

        # Round the edges
        outer_hand = ctx.add_bevel(outer_hand, width=thickness, segments=3)

        # Inner cavity
        inner_hand = ctx.create_cube(
            size=1.0,
            location=(0, 0, 0),
            name="HandInner",
        )
        ctx.scale_object(inner_hand, (hand_width, hand_length * 0.5 + 0.01, hand_width * 0.4))

        gauntlet = ctx.boolean_difference(outer_hand, inner_hand, name="GauntletShell")

        return gauntlet

    def _add_articulated_fingers(
        self, gauntlet: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add individual articulated finger plates."""
        ctx = self.ctx
        hand_length = dims.get("hand_length", 0.21)
        hand_width = dims.get("hand_width", 0.11)

        finger_width = hand_width / 5  # 4 fingers + gaps
        finger_length = hand_length * 0.55
        num_segments = 3  # Proximal, middle, distal phalanges

        # Four fingers
        for finger_idx in range(4):
            # Finger position (index to pinky)
            x_pos = (finger_idx - 1.5) * finger_width * 1.1

            # Vary finger lengths (middle longest, pinky shortest)
            length_mult = [0.9, 1.0, 0.95, 0.8][finger_idx]
            this_finger_length = finger_length * length_mult

            segment_length = this_finger_length / num_segments

            for seg_idx in range(num_segments):
                y_pos = hand_length * 0.25 + seg_idx * segment_length * 0.9
                z_pos = hand_width * 0.15

                # Finger segment (slightly tapered)
                taper = 1.0 - seg_idx * 0.1
                segment = ctx.create_cube(
                    size=1.0,
                    location=(x_pos, y_pos, z_pos),
                    name=f"Finger_{finger_idx}_Seg_{seg_idx}",
                )
                ctx.scale_object(
                    segment,
                    (
                        finger_width * 0.8 * taper + thickness * 2,
                        segment_length * 0.85,
                        finger_width * 0.6 * taper + thickness * 2,
                    ),
                )

                # Round edges
                segment = ctx.add_bevel(segment, width=thickness * 0.5, segments=2)

                gauntlet = ctx.boolean_union(gauntlet, segment)

        return gauntlet

    def _add_mitten_style(
        self, gauntlet: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add mitten-style finger covering (simpler print)."""
        ctx = self.ctx
        hand_length = dims.get("hand_length", 0.21)
        hand_width = dims.get("hand_width", 0.11)

        # Single finger covering
        finger_cover = ctx.create_cube(
            size=1.0,
            location=(0, hand_length * 0.35, hand_width * 0.1),
            name="FingerCover",
        )
        ctx.scale_object(
            finger_cover,
            (hand_width * 0.9 + thickness * 2, hand_length * 0.5, hand_width * 0.35 + thickness * 2),
        )
        finger_cover = ctx.add_bevel(finger_cover, width=thickness, segments=3)

        gauntlet = ctx.boolean_union(gauntlet, finger_cover)

        return gauntlet

    def _add_thumb(
        self, gauntlet: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add thumb armor."""
        ctx = self.ctx
        hand_length = dims.get("hand_length", 0.21)
        hand_width = dims.get("hand_width", 0.11)

        thumb_length = hand_length * 0.35
        thumb_width = hand_width * 0.25

        # Thumb base
        thumb_base = ctx.create_cube(
            size=1.0,
            location=(-hand_width / 2 - thumb_width / 3, -hand_length * 0.1, 0),
            name="ThumbBase",
        )
        ctx.scale_object(
            thumb_base,
            (thumb_width + thickness * 2, thumb_length * 0.5, thumb_width * 0.8 + thickness * 2),
        )
        ctx.rotate_object(thumb_base, (0, 0, 30))
        thumb_base = ctx.add_bevel(thumb_base, width=thickness * 0.5, segments=2)
        gauntlet = ctx.boolean_union(gauntlet, thumb_base)

        # Thumb tip
        thumb_tip = ctx.create_cube(
            size=1.0,
            location=(-hand_width / 2 - thumb_width, hand_length * 0.05, 0),
            name="ThumbTip",
        )
        ctx.scale_object(
            thumb_tip,
            (thumb_width * 0.9 + thickness * 2, thumb_length * 0.4, thumb_width * 0.7 + thickness * 2),
        )
        ctx.rotate_object(thumb_tip, (0, 0, 45))
        thumb_tip = ctx.add_bevel(thumb_tip, width=thickness * 0.5, segments=2)
        gauntlet = ctx.boolean_union(gauntlet, thumb_tip)

        return gauntlet

    def _add_knuckle_plates(
        self, gauntlet: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add reinforced knuckle plates."""
        ctx = self.ctx
        hand_length = dims.get("hand_length", 0.21)
        hand_width = dims.get("hand_width", 0.11)

        # Knuckle guard ridge
        knuckle_guard = ctx.create_cube(
            size=1.0,
            location=(0, hand_length * 0.15, hand_width * 0.25),
            name="KnuckleGuard",
        )
        ctx.scale_object(
            knuckle_guard,
            (hand_width + thickness * 2, hand_width * 0.3, thickness * 3),
        )
        knuckle_guard = ctx.add_bevel(knuckle_guard, width=thickness * 0.5, segments=2)
        gauntlet = ctx.boolean_union(gauntlet, knuckle_guard)

        return gauntlet

    def _add_wrist_cuff(
        self, gauntlet: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add wrist cuff that connects to vambrace."""
        ctx = self.ctx
        hand_length = dims.get("hand_length", 0.21)
        hand_width = dims.get("hand_width", 0.11)
        wrist_circ = dims.get("wrist_circumference", 0.19)

        wrist_radius = wrist_circ / (2 * math.pi) + thickness

        # Wrist cuff cylinder
        wrist_cuff = ctx.create_cylinder(
            radius=wrist_radius,
            depth=hand_length * 0.25,
            location=(0, -hand_length * 0.25, 0),
            vertices=32,
            name="WristCuff",
        )
        ctx.rotate_object(wrist_cuff, (90, 0, 0))

        # Inner cavity
        inner_cuff = ctx.create_cylinder(
            radius=wrist_radius - thickness,
            depth=hand_length * 0.3,
            location=(0, -hand_length * 0.25, 0),
            vertices=32,
            name="WristInner",
        )
        ctx.rotate_object(inner_cuff, (90, 0, 0))

        wrist_cuff = ctx.boolean_difference(wrist_cuff, inner_cuff)
        gauntlet = ctx.boolean_union(gauntlet, wrist_cuff)

        return gauntlet

    def _add_palm_plate(
        self, gauntlet: Any, dims: dict[str, float], thickness: float
    ) -> Any:
        """Add palm protection plate."""
        ctx = self.ctx
        hand_length = dims.get("hand_length", 0.21)
        hand_width = dims.get("hand_width", 0.11)

        # Palm plate on underside
        palm = ctx.create_cube(
            size=1.0,
            location=(0, 0, -hand_width * 0.2),
            name="PalmPlate",
        )
        ctx.scale_object(palm, (hand_width * 0.85, hand_length * 0.45, thickness * 2))
        gauntlet = ctx.boolean_union(gauntlet, palm)

        return gauntlet

    def generate_printable_parts(self) -> list[tuple[str, Any]]:
        """Generate gauntlet parts for easier printing."""
        # For gauntlets, we might want to print fingers separately
        # This returns the whole gauntlet; could be extended for finger separation
        left = self.generate_base()
        left = self.finalize(left)
        left.name = "gauntlet_left"

        self.side = "right"
        right = self.ctx.mirror_object(left, axis="X", name="gauntlet_right")

        return [("gauntlet_left", left), ("gauntlet_right", right)]
