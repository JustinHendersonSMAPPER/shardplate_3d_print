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

    def generate_segments_base(self) -> dict[str, Any]:
        """Generate segmented gauntlet: hand shell, wrist cuff, knuckle plate,
        12 finger segments (4x3), 2 thumb segments.

        Each finger/thumb segment has elastic cord channels for assembly.
        Pin alignment is used for wrist cuff connection.
        """
        dims = self.dimensions
        ctx = self.ctx
        thickness = self.measurements.scaled(self.measurements.plate_thickness)
        hand_length = dims.get("hand_length", 0.21)
        hand_width = dims.get("hand_width", 0.11)
        wrist_circ = dims.get("wrist_circumference", 0.19)

        segments: dict[str, Any] = {}

        # --- Segment 1: Hand shell (palm + back of hand) ---
        hand_shell = self._create_hand_shell(dims, thickness)
        hand_shell = self._add_palm_plate(hand_shell, dims, thickness)

        # Pin holes for wrist cuff
        wrist_radius = wrist_circ / (2 * math.pi)
        for x_off in [-wrist_radius * 0.4, wrist_radius * 0.4]:
            hand_shell = ctx.create_alignment_pin_hole(
                hand_shell,
                location=(x_off, -hand_length * 0.25, 0),
                direction=(0, -1, 0),
            )

        hand_shell = self.add_shardplate_details(hand_shell)
        hand_shell.name = f"{self._base_name}_hand_left"
        segments[hand_shell.name] = hand_shell

        # --- Segment 2: Wrist cuff ---
        wrist_cuff = self._create_wrist_cuff_standalone(dims, thickness)

        for x_off in [-wrist_radius * 0.4, wrist_radius * 0.4]:
            wrist_cuff = ctx.create_alignment_pin_post(
                wrist_cuff,
                location=(x_off, -hand_length * 0.25 + 0.001, 0),
                direction=(0, -1, 0),
            )

        wrist_cuff = self.add_shardplate_details(wrist_cuff)
        wrist_cuff.name = f"{self._base_name}_wrist_left"
        segments[wrist_cuff.name] = wrist_cuff

        # --- Segment 3: Knuckle plate ---
        knuckle = self._create_knuckle_standalone(dims, thickness)
        knuckle = self.add_shardplate_details(knuckle)
        knuckle.name = f"{self._base_name}_knuckle_left"
        segments[knuckle.name] = knuckle

        # --- Segments 4-15: 12 finger segments (4 fingers x 3 segments each) ---
        finger_width = hand_width / 5
        finger_length = hand_length * 0.55
        finger_names = ["index", "middle", "ring", "pinky"]
        length_mults = [0.9, 1.0, 0.95, 0.8]
        num_segs = 3

        for finger_idx in range(4):
            x_pos = (finger_idx - 1.5) * finger_width * 1.1
            this_finger_length = finger_length * length_mults[finger_idx]
            segment_length = this_finger_length / num_segs

            for seg_idx in range(num_segs):
                y_pos = hand_length * 0.25 + seg_idx * segment_length * 0.9
                z_pos = hand_width * 0.15
                taper = 1.0 - seg_idx * 0.1
                seg_len = segment_length * 0.85

                seg = ctx.create_cube(
                    size=1.0,
                    location=(x_pos, y_pos, z_pos),
                    name=f"Finger_{finger_names[finger_idx]}_{seg_idx}",
                )
                ctx.scale_object(
                    seg,
                    (
                        finger_width * 0.8 * taper + thickness * 2,
                        seg_len,
                        finger_width * 0.6 * taper + thickness * 2,
                    ),
                )
                seg = ctx.add_bevel(seg, width=thickness * 0.5, segments=2)

                # Elastic cord channel through each finger segment
                seg = ctx.create_cord_channel(
                    seg,
                    start=(x_pos, y_pos - seg_len / 2 - 0.001, z_pos),
                    end=(x_pos, y_pos + seg_len / 2 + 0.001, z_pos),
                    diameter=0.002,
                )

                # Pin posts/holes between segments
                if seg_idx > 0:
                    seg = ctx.create_alignment_pin_post(
                        seg,
                        location=(x_pos, y_pos - seg_len / 2, z_pos),
                        direction=(0, -1, 0),
                    )
                if seg_idx < num_segs - 1:
                    seg = ctx.create_alignment_pin_hole(
                        seg,
                        location=(x_pos, y_pos + seg_len / 2, z_pos),
                        direction=(0, 1, 0),
                    )

                seg_name = f"{self._base_name}_{finger_names[finger_idx]}{seg_idx + 1}_left"
                seg.name = seg_name
                segments[seg_name] = seg

        # --- Segments 16-17: Thumb (base + tip) ---
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

        # Cord channel through thumb base
        tb_x = -hand_width / 2 - thumb_width / 3
        thumb_base = ctx.create_cord_channel(
            thumb_base,
            start=(tb_x, -hand_length * 0.1 - thumb_length * 0.25, 0),
            end=(tb_x, -hand_length * 0.1 + thumb_length * 0.25, 0),
            diameter=0.002,
        )
        # Pin hole for thumb tip
        thumb_base = ctx.create_alignment_pin_hole(
            thumb_base,
            location=(tb_x - thumb_width * 0.3, -hand_length * 0.02, 0),
            direction=(0, 1, 0),
        )

        thumb_base.name = f"{self._base_name}_thumb_base_left"
        segments[thumb_base.name] = thumb_base

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

        # Cord channel through thumb tip
        tt_x = -hand_width / 2 - thumb_width
        thumb_tip = ctx.create_cord_channel(
            thumb_tip,
            start=(tt_x, hand_length * 0.05 - thumb_length * 0.2, 0),
            end=(tt_x, hand_length * 0.05 + thumb_length * 0.2, 0),
            diameter=0.002,
        )
        # Pin post for thumb base
        thumb_tip = ctx.create_alignment_pin_post(
            thumb_tip,
            location=(tt_x + thumb_width * 0.3, hand_length * 0.05 - thumb_length * 0.2, 0),
            direction=(0, -1, 0),
        )

        thumb_tip.name = f"{self._base_name}_thumb_tip_left"
        segments[thumb_tip.name] = thumb_tip

        return segments

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

    def _create_knuckle_standalone(
        self, dims: dict[str, float], thickness: float
    ) -> Any:
        """Create knuckle plate as a standalone segment."""
        ctx = self.ctx
        hand_length = dims.get("hand_length", 0.21)
        hand_width = dims.get("hand_width", 0.11)

        knuckle = ctx.create_cube(
            size=1.0,
            location=(0, hand_length * 0.15, hand_width * 0.25),
            name="KnuckleSeg",
        )
        ctx.scale_object(
            knuckle,
            (hand_width + thickness * 2, hand_width * 0.3, thickness * 3),
        )
        knuckle = ctx.add_bevel(knuckle, width=thickness * 0.5, segments=2)
        return knuckle

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

    def _create_wrist_cuff_standalone(
        self, dims: dict[str, float], thickness: float
    ) -> Any:
        """Create wrist cuff as a standalone segment."""
        ctx = self.ctx
        hand_length = dims.get("hand_length", 0.21)
        wrist_circ = dims.get("wrist_circumference", 0.19)

        wrist_radius = wrist_circ / (2 * math.pi) + thickness

        wrist_cuff = ctx.create_cylinder(
            radius=wrist_radius, depth=hand_length * 0.25,
            location=(0, -hand_length * 0.25, 0),
            vertices=32, name="WristCuffSeg",
        )
        ctx.rotate_object(wrist_cuff, (90, 0, 0))

        inner_cuff = ctx.create_cylinder(
            radius=wrist_radius - thickness, depth=hand_length * 0.3,
            location=(0, -hand_length * 0.25, 0),
            vertices=32, name="WristInner",
        )
        ctx.rotate_object(inner_cuff, (90, 0, 0))

        wrist_cuff = ctx.boolean_difference(wrist_cuff, inner_cuff)
        return wrist_cuff

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
        left = self.generate_base()
        left = self.finalize(left)
        left.name = "gauntlet_left"

        self.side = "right"
        right = self.ctx.mirror_object(left, axis="X", name="gauntlet_right")

        return [("gauntlet_left", left), ("gauntlet_right", right)]
