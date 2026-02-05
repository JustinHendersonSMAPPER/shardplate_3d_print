"""Strap mounting system for wearable armor attachment."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .blender_utils import BlenderContext


class StrapType(Enum):
    """Types of strap mounting systems."""

    BUCKLE = "buckle"  # Standard buckle closure
    VELCRO = "velcro"  # Hook and loop attachment points
    SNAP = "snap"  # Snap button closure
    LACE = "lace"  # Lacing holes for cord
    CLIP = "clip"  # Quick-release clip mount
    INTERLOCK = "interlock"  # Interlocking plate connection


@dataclass
class StrapMount:
    """A single strap mounting point on an armor piece."""

    position: tuple[float, float, float]  # (x, y, z) position on armor
    normal: tuple[float, float, float] = (0, 1, 0)  # Direction mount faces
    strap_type: StrapType = StrapType.BUCKLE
    slot_width: float = 0.025  # Width of strap slot (25mm default)
    slot_height: float = 0.004  # Height/thickness of slot
    slot_depth: float = 0.008  # How deep the slot goes

    # For lace type
    hole_diameter: float = 0.005  # 5mm lace holes
    hole_count: int = 4  # Number of lace holes

    # For interlock type
    interlock_depth: float = 0.01  # Depth of interlock groove
    interlock_width: float = 0.02  # Width of interlock tab


@dataclass
class StrapSystem:
    """System of strap mounts for an armor piece."""

    mounts: list[StrapMount] = field(default_factory=list)

    def add_mount(
        self,
        position: tuple[float, float, float],
        strap_type: StrapType = StrapType.BUCKLE,
        **kwargs: Any,
    ) -> StrapMount:
        """Add a strap mount point."""
        mount = StrapMount(position=position, strap_type=strap_type, **kwargs)
        self.mounts.append(mount)
        return mount

    def add_paired_mounts(
        self,
        y_position: float,
        z_position: float,
        x_offset: float,
        strap_type: StrapType = StrapType.BUCKLE,
        **kwargs: Any,
    ) -> tuple[StrapMount, StrapMount]:
        """Add a pair of mounts on opposite sides (left/right)."""
        left = self.add_mount(
            position=(-x_offset, y_position, z_position),
            strap_type=strap_type,
            normal=(-1, 0, 0),
            **kwargs,
        )
        right = self.add_mount(
            position=(x_offset, y_position, z_position),
            strap_type=strap_type,
            normal=(1, 0, 0),
            **kwargs,
        )
        return left, right

    def apply_to_mesh(self, ctx: BlenderContext, obj: Any) -> Any:
        """Apply all strap mounts to a mesh object."""
        for mount in self.mounts:
            obj = self._create_mount_geometry(ctx, obj, mount)
        return obj

    def _create_mount_geometry(
        self, ctx: BlenderContext, obj: Any, mount: StrapMount
    ) -> Any:
        """Create the geometry for a single strap mount."""
        if mount.strap_type == StrapType.BUCKLE:
            return self._create_buckle_slot(ctx, obj, mount)
        elif mount.strap_type == StrapType.VELCRO:
            return self._create_velcro_pad(ctx, obj, mount)
        elif mount.strap_type == StrapType.SNAP:
            return self._create_snap_mount(ctx, obj, mount)
        elif mount.strap_type == StrapType.LACE:
            return self._create_lace_holes(ctx, obj, mount)
        elif mount.strap_type == StrapType.CLIP:
            return self._create_clip_mount(ctx, obj, mount)
        elif mount.strap_type == StrapType.INTERLOCK:
            return self._create_interlock(ctx, obj, mount)
        return obj

    def _create_buckle_slot(
        self, ctx: BlenderContext, obj: Any, mount: StrapMount
    ) -> Any:
        """Create a slot for a buckle strap to pass through."""
        # Create slot cutter
        slot = ctx.create_cube(
            size=1.0,
            location=mount.position,
            name="StrapSlot",
        )
        ctx.scale_object(slot, (mount.slot_width, mount.slot_depth * 2, mount.slot_height))

        # Orient slot based on normal
        if mount.normal[0] != 0:  # Side-facing
            ctx.rotate_object(slot, (0, 0, 90))

        # Cut slot from armor
        obj = ctx.boolean_difference(obj, slot)
        return obj

    def _create_velcro_pad(
        self, ctx: BlenderContext, obj: Any, mount: StrapMount
    ) -> Any:
        """Create a flat pad area for velcro attachment."""
        # Create a small depression for velcro backing
        pad = ctx.create_cube(
            size=1.0,
            location=mount.position,
            name="VelcroPad",
        )
        ctx.scale_object(pad, (mount.slot_width, 0.002, mount.slot_width))
        obj = ctx.boolean_difference(obj, pad)
        return obj

    def _create_snap_mount(
        self, ctx: BlenderContext, obj: Any, mount: StrapMount
    ) -> Any:
        """Create a mount point for snap buttons."""
        # Create hole for snap post
        hole = ctx.create_cylinder(
            radius=0.006,  # 6mm snap hole
            depth=mount.slot_depth,
            location=mount.position,
            name="SnapHole",
        )
        ctx.rotate_object(hole, (90, 0, 0))
        obj = ctx.boolean_difference(obj, hole)
        return obj

    def _create_lace_holes(
        self, ctx: BlenderContext, obj: Any, mount: StrapMount
    ) -> Any:
        """Create a series of holes for lacing."""
        spacing = mount.slot_width / (mount.hole_count - 1) if mount.hole_count > 1 else 0
        start_x = mount.position[0] - mount.slot_width / 2

        for i in range(mount.hole_count):
            hole_pos = (
                start_x + i * spacing,
                mount.position[1],
                mount.position[2],
            )
            hole = ctx.create_cylinder(
                radius=mount.hole_diameter / 2,
                depth=mount.slot_depth * 2,
                location=hole_pos,
                name=f"LaceHole_{i}",
            )
            ctx.rotate_object(hole, (90, 0, 0))
            obj = ctx.boolean_difference(obj, hole)

        return obj

    def _create_clip_mount(
        self, ctx: BlenderContext, obj: Any, mount: StrapMount
    ) -> Any:
        """Create a quick-release clip mounting point."""
        # Create a T-slot for clip attachment
        # Vertical slot
        slot1 = ctx.create_cube(
            size=1.0,
            location=mount.position,
            name="ClipSlot1",
        )
        ctx.scale_object(slot1, (0.008, mount.slot_depth, 0.025))

        # Horizontal slot at top
        slot2 = ctx.create_cube(
            size=1.0,
            location=(mount.position[0], mount.position[1], mount.position[2] + 0.01),
            name="ClipSlot2",
        )
        ctx.scale_object(slot2, (0.02, mount.slot_depth, 0.008))

        obj = ctx.boolean_difference(obj, slot1)
        obj = ctx.boolean_difference(obj, slot2)
        return obj

    def _create_interlock(
        self, ctx: BlenderContext, obj: Any, mount: StrapMount
    ) -> Any:
        """Create interlocking plate connection."""
        # Create groove for interlocking with adjacent plate
        groove = ctx.create_cube(
            size=1.0,
            location=mount.position,
            name="InterlockGroove",
        )
        ctx.scale_object(
            groove, (mount.interlock_width, mount.interlock_depth, mount.slot_height * 2)
        )
        obj = ctx.boolean_difference(obj, groove)

        # Create matching tab nearby
        tab_pos = (
            mount.position[0],
            mount.position[1] - mount.interlock_depth,
            mount.position[2] + mount.slot_height * 3,
        )
        tab = ctx.create_cube(
            size=1.0,
            location=tab_pos,
            name="InterlockTab",
        )
        ctx.scale_object(
            tab, (mount.interlock_width * 0.9, mount.interlock_depth * 0.8, mount.slot_height)
        )
        obj = ctx.boolean_union(obj, tab)

        return obj


def create_standard_strap_system(
    armor_type: str,
    dimensions: dict[str, float],
) -> StrapSystem:
    """Create a standard strap system for a given armor type."""
    system = StrapSystem()

    if armor_type == "helmet":
        # Chin strap mounts
        system.add_paired_mounts(
            y_position=-dimensions.get("inner_length", 0.2) / 2,
            z_position=-dimensions.get("inner_height", 0.24) / 3,
            x_offset=dimensions.get("inner_width", 0.16) / 2 - 0.01,
            strap_type=StrapType.BUCKLE,
        )

    elif armor_type == "chest":
        # Side straps
        width = dimensions.get("width", 0.5)
        height = dimensions.get("height", 0.5)
        system.add_paired_mounts(
            y_position=0,
            z_position=height * 0.3,
            x_offset=width / 2,
            strap_type=StrapType.BUCKLE,
        )
        system.add_paired_mounts(
            y_position=0,
            z_position=-height * 0.2,
            x_offset=width / 2,
            strap_type=StrapType.BUCKLE,
        )
        # Shoulder connection points
        system.add_paired_mounts(
            y_position=0,
            z_position=height / 2 - 0.02,
            x_offset=width / 2 - 0.05,
            strap_type=StrapType.INTERLOCK,
        )

    elif armor_type == "pauldron":
        # Arm strap
        width = dimensions.get("width", 0.2)
        height = dimensions.get("height", 0.12)
        system.add_mount(
            position=(0, 0, -height / 2),
            strap_type=StrapType.BUCKLE,
        )
        # Connection to chest
        system.add_mount(
            position=(0, dimensions.get("depth", 0.15) / 2, height / 3),
            strap_type=StrapType.INTERLOCK,
        )

    elif armor_type in ("vambrace", "greave"):
        # Wraparound straps
        length = dimensions.get("length", 0.3)
        system.add_paired_mounts(
            y_position=length * 0.25,
            z_position=0,
            x_offset=dimensions.get("upper_circumference", 0.3) / (2 * math.pi),
            strap_type=StrapType.BUCKLE,
        )
        system.add_paired_mounts(
            y_position=-length * 0.25,
            z_position=0,
            x_offset=dimensions.get("lower_circumference", 0.25) / (2 * math.pi),
            strap_type=StrapType.BUCKLE,
        )

    elif armor_type == "gauntlet":
        # Wrist strap
        system.add_mount(
            position=(0, -dimensions.get("hand_length", 0.19) / 2, 0),
            strap_type=StrapType.VELCRO,
            slot_width=dimensions.get("wrist_circumference", 0.17) / 4,
        )

    elif armor_type == "cuisse":
        # Thigh straps
        length = dimensions.get("length", 0.45)
        circ = dimensions.get("upper_circumference", 0.58)
        system.add_paired_mounts(
            y_position=length * 0.4,
            z_position=0,
            x_offset=circ / (2 * math.pi),
            strap_type=StrapType.BUCKLE,
        )
        # Belt connection at top
        system.add_mount(
            position=(0, length / 2, 0),
            strap_type=StrapType.CLIP,
            normal=(0, 1, 0),
        )

    elif armor_type == "sabaton":
        # Ankle straps and lacing
        system.add_paired_mounts(
            y_position=-dimensions.get("length", 0.27) * 0.3,
            z_position=dimensions.get("width", 0.1) / 2,
            x_offset=dimensions.get("width", 0.1) / 2,
            strap_type=StrapType.BUCKLE,
        )
        # Top lacing
        system.add_mount(
            position=(0, dimensions.get("length", 0.27) * 0.2, dimensions.get("width", 0.1)),
            strap_type=StrapType.LACE,
            hole_count=6,
        )

    return system
