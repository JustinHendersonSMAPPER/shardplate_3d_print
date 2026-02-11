"""Blender utility functions for 3D model generation."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

# Type alias for when bpy is available
BpyModule = Any


@dataclass
class BlenderContext:
    """Context manager for Blender operations."""

    bpy: BpyModule = field(default=None, repr=False)
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Initialize Blender context."""
        if self.bpy is None:
            try:
                import bpy

                self.bpy = bpy
                self._initialized = True
            except ImportError:
                raise ImportError(
                    "Blender Python module (bpy) not available. "
                    "Run this script from within Blender or install bpy."
                )

    def clear_scene(self) -> None:
        """Remove all objects from the current scene."""
        bpy = self.bpy
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

    def create_cube(
        self,
        size: float = 1.0,
        location: tuple[float, float, float] = (0, 0, 0),
        name: str = "Cube",
    ) -> Any:
        """Create a cube primitive."""
        bpy = self.bpy
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        obj = bpy.context.active_object
        obj.name = name
        return obj

    def create_cylinder(
        self,
        radius: float = 1.0,
        depth: float = 2.0,
        location: tuple[float, float, float] = (0, 0, 0),
        vertices: int = 32,
        name: str = "Cylinder",
    ) -> Any:
        """Create a cylinder primitive."""
        bpy = self.bpy
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius, depth=depth, location=location, vertices=vertices
        )
        obj = bpy.context.active_object
        obj.name = name
        return obj

    def create_uv_sphere(
        self,
        radius: float = 1.0,
        location: tuple[float, float, float] = (0, 0, 0),
        segments: int = 32,
        ring_count: int = 16,
        name: str = "Sphere",
    ) -> Any:
        """Create a UV sphere primitive."""
        bpy = self.bpy
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius, location=location, segments=segments, ring_count=ring_count
        )
        obj = bpy.context.active_object
        obj.name = name
        return obj

    def create_cone(
        self,
        radius1: float = 1.0,
        radius2: float = 0.0,
        depth: float = 2.0,
        location: tuple[float, float, float] = (0, 0, 0),
        vertices: int = 32,
        name: str = "Cone",
    ) -> Any:
        """Create a cone primitive."""
        bpy = self.bpy
        bpy.ops.mesh.primitive_cone_add(
            radius1=radius1, radius2=radius2, depth=depth, location=location, vertices=vertices
        )
        obj = bpy.context.active_object
        obj.name = name
        return obj

    def create_torus(
        self,
        major_radius: float = 1.0,
        minor_radius: float = 0.25,
        location: tuple[float, float, float] = (0, 0, 0),
        major_segments: int = 48,
        minor_segments: int = 12,
        name: str = "Torus",
    ) -> Any:
        """Create a torus primitive."""
        bpy = self.bpy
        bpy.ops.mesh.primitive_torus_add(
            major_radius=major_radius,
            minor_radius=minor_radius,
            location=location,
            major_segments=major_segments,
            minor_segments=minor_segments,
        )
        obj = bpy.context.active_object
        obj.name = name
        return obj

    def boolean_union(self, obj1: Any, obj2: Any, name: str | None = None) -> Any:
        """Perform boolean union of two objects."""
        bpy = self.bpy
        bpy.context.view_layer.objects.active = obj1
        modifier = obj1.modifiers.new(name="Boolean", type="BOOLEAN")
        modifier.operation = "UNION"
        modifier.object = obj2
        bpy.ops.object.modifier_apply(modifier="Boolean")
        bpy.data.objects.remove(obj2, do_unlink=True)
        if name:
            obj1.name = name
        return obj1

    def boolean_difference(self, obj1: Any, obj2: Any, name: str | None = None) -> Any:
        """Perform boolean difference (subtract obj2 from obj1)."""
        bpy = self.bpy
        bpy.context.view_layer.objects.active = obj1
        modifier = obj1.modifiers.new(name="Boolean", type="BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.object = obj2
        bpy.ops.object.modifier_apply(modifier="Boolean")
        bpy.data.objects.remove(obj2, do_unlink=True)
        if name:
            obj1.name = name
        return obj1

    def boolean_intersect(self, obj1: Any, obj2: Any, name: str | None = None) -> Any:
        """Perform boolean intersection of two objects."""
        bpy = self.bpy
        bpy.context.view_layer.objects.active = obj1
        modifier = obj1.modifiers.new(name="Boolean", type="BOOLEAN")
        modifier.operation = "INTERSECT"
        modifier.object = obj2
        bpy.ops.object.modifier_apply(modifier="Boolean")
        bpy.data.objects.remove(obj2, do_unlink=True)
        if name:
            obj1.name = name
        return obj1

    def add_solidify(self, obj: Any, thickness: float = 0.003) -> Any:
        """Add solidify modifier to give thickness to a surface."""
        bpy = self.bpy
        bpy.context.view_layer.objects.active = obj
        modifier = obj.modifiers.new(name="Solidify", type="SOLIDIFY")
        modifier.thickness = thickness
        bpy.ops.object.modifier_apply(modifier="Solidify")
        return obj

    def add_subdivision(self, obj: Any, levels: int = 2) -> Any:
        """Add subdivision surface modifier for smoothing."""
        bpy = self.bpy
        bpy.context.view_layer.objects.active = obj
        modifier = obj.modifiers.new(name="Subdivision", type="SUBSURF")
        modifier.levels = levels
        modifier.render_levels = levels
        bpy.ops.object.modifier_apply(modifier="Subdivision")
        return obj

    def add_bevel(self, obj: Any, width: float = 0.002, segments: int = 3) -> Any:
        """Add bevel modifier for edge smoothing."""
        bpy = self.bpy
        bpy.context.view_layer.objects.active = obj
        modifier = obj.modifiers.new(name="Bevel", type="BEVEL")
        modifier.width = width
        modifier.segments = segments
        bpy.ops.object.modifier_apply(modifier="Bevel")
        return obj

    def scale_object(self, obj: Any, scale: tuple[float, float, float]) -> Any:
        """Scale an object."""
        obj.scale = scale
        self.bpy.context.view_layer.objects.active = obj
        self.bpy.ops.object.transform_apply(scale=True)
        return obj

    def rotate_object(
        self, obj: Any, rotation: tuple[float, float, float], degrees: bool = True
    ) -> Any:
        """Rotate an object (angles in degrees by default)."""
        if degrees:
            rotation = tuple(math.radians(r) for r in rotation)
        obj.rotation_euler = rotation
        self.bpy.context.view_layer.objects.active = obj
        self.bpy.ops.object.transform_apply(rotation=True)
        return obj

    def move_object(self, obj: Any, location: tuple[float, float, float]) -> Any:
        """Move an object to a location."""
        obj.location = location
        return obj

    def duplicate_object(self, obj: Any, name: str | None = None) -> Any:
        """Duplicate an object."""
        bpy = self.bpy
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        bpy.context.collection.objects.link(new_obj)
        if name:
            new_obj.name = name
        return new_obj

    def mirror_object(self, obj: Any, axis: str = "X", name: str | None = None) -> Any:
        """Mirror an object along an axis."""
        bpy = self.bpy
        new_obj = self.duplicate_object(obj, name)
        axis_map = {"X": (0, 1), "Y": (1, 1), "Z": (2, 1)}
        if axis.upper() in axis_map:
            idx, _ = axis_map[axis.upper()]
            scale = [1, 1, 1]
            scale[idx] = -1
            new_obj.scale = tuple(scale)
            bpy.context.view_layer.objects.active = new_obj
            bpy.ops.object.transform_apply(scale=True)
        return new_obj

    def join_objects(self, objects: list[Any], name: str | None = None) -> Any:
        """Join multiple objects into one."""
        bpy = self.bpy
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join()
        result = bpy.context.active_object
        if name:
            result.name = name
        return result

    def export_stl(self, obj: Any, filepath: str) -> None:
        """Export an object to STL format."""
        bpy = self.bpy
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.wm.stl_export(
            filepath=filepath, export_selected_objects=True, global_scale=1000.0
        )

    def export_all_stl(self, filepath: str) -> None:
        """Export all visible objects to STL format."""
        bpy = self.bpy
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.wm.stl_export(
            filepath=filepath, export_selected_objects=True, global_scale=1000.0
        )

    def add_edge_detail(
        self, obj: Any, pattern: str = "angular", depth: float = 0.002
    ) -> Any:
        """Add Shardplate-style edge details using displacement."""
        bpy = self.bpy
        bpy.context.view_layer.objects.active = obj

        # Add edge split for sharp edges characteristic of Shardplate
        modifier = obj.modifiers.new(name="EdgeSplit", type="EDGE_SPLIT")
        modifier.split_angle = math.radians(30)
        bpy.ops.object.modifier_apply(modifier="EdgeSplit")

        return obj

    def create_plate_segment(
        self,
        width: float,
        height: float,
        depth: float,
        curvature: float = 0.0,
        name: str = "PlateSegment",
    ) -> Any:
        """Create a curved plate segment typical of Shardplate armor."""
        bpy = self.bpy

        # Create base cube
        obj = self.create_cube(size=1.0, name=name)
        self.scale_object(obj, (width, depth, height))

        if curvature > 0:
            # Add simple deform for curvature
            bpy.context.view_layer.objects.active = obj
            modifier = obj.modifiers.new(name="SimpleDeform", type="SIMPLE_DEFORM")
            modifier.deform_method = "BEND"
            modifier.angle = math.radians(curvature)
            bpy.ops.object.modifier_apply(modifier="SimpleDeform")

        return obj

    def add_glyph_indent(
        self,
        obj: Any,
        location: tuple[float, float, float],
        size: float = 0.02,
        depth: float = 0.002,
    ) -> Any:
        """Add a glyph-style indent for gemstone placement or decoration."""
        # Create a small geometric shape for the indent
        indent = self.create_cube(size=size, location=location, name="GlyphIndent")
        self.rotate_object(indent, (0, 0, 45))
        obj = self.boolean_difference(obj, indent)
        return obj

    # --- Assembly feature methods ---

    def create_alignment_pin_hole(
        self,
        obj: Any,
        location: tuple[float, float, float],
        direction: tuple[float, float, float] = (0, 0, 1),
        diameter: float = 0.002,
        depth: float = 0.003,
    ) -> Any:
        """Create a 2mm diameter, 3mm deep alignment pin hole.

        Used on one side of a joint/cut face so a matching post can slot in.
        """
        radius = diameter / 2
        pin_hole = self.create_cylinder(
            radius=radius,
            depth=depth * 2,  # Extend through to ensure clean boolean
            location=location,
            vertices=16,
            name="AlignPinHole",
        )
        # Orient the hole along the specified direction
        if direction == (1, 0, 0):
            self.rotate_object(pin_hole, (0, 90, 0))
        elif direction == (0, 1, 0):
            self.rotate_object(pin_hole, (90, 0, 0))
        # Default (0, 0, 1) needs no rotation

        obj = self.boolean_difference(obj, pin_hole)
        return obj

    def create_alignment_pin_post(
        self,
        obj: Any,
        location: tuple[float, float, float],
        direction: tuple[float, float, float] = (0, 0, 1),
        diameter: float = 0.002,
        height: float = 0.003,
        clearance: float = 0.0001,
    ) -> Any:
        """Create a matching alignment pin post (0.1mm undersize for clearance)."""
        radius = diameter / 2 - clearance
        pin_post = self.create_cylinder(
            radius=radius,
            depth=height,
            location=location,
            vertices=16,
            name="AlignPinPost",
        )
        # Orient the post along the specified direction
        if direction == (1, 0, 0):
            self.rotate_object(pin_post, (0, 90, 0))
        elif direction == (0, 1, 0):
            self.rotate_object(pin_post, (90, 0, 0))

        obj = self.boolean_union(obj, pin_post)
        return obj

    def create_cord_channel(
        self,
        obj: Any,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        diameter: float = 0.002,
    ) -> Any:
        """Create a 2mm through-hole for elastic cord (finger/toe segments).

        Bores a cylindrical channel from start to end through the object.
        """
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = end[2] - start[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, (start[2] + end[2]) / 2)

        channel = self.create_cylinder(
            radius=diameter / 2,
            depth=length + diameter,  # Extra length for clean boolean
            location=mid,
            vertices=16,
            name="CordChannel",
        )

        # Calculate rotation to align cylinder with start->end direction
        if length > 0:
            # Cylinder default axis is Z, compute rotation to align with direction
            dir_norm = (dx / length, dy / length, dz / length)
            # Rotation from Z-axis to direction vector
            if abs(dir_norm[2]) < 0.999:
                angle = math.acos(max(-1.0, min(1.0, dir_norm[2])))
                # Cross product of Z-axis and direction for rotation axis
                ax = -dir_norm[1]
                ay = dir_norm[0]
                az = 0.0
                axis_len = math.sqrt(ax * ax + ay * ay)
                if axis_len > 0:
                    ax /= axis_len
                    ay /= axis_len
                    # Use Euler approximation: rotate around the axis
                    channel.rotation_euler = (
                        math.atan2(dir_norm[1], math.sqrt(dir_norm[0] ** 2 + dir_norm[2] ** 2)),
                        0,
                        math.atan2(-dir_norm[0], dir_norm[2]),
                    )
                    self.bpy.context.view_layer.objects.active = channel
                    self.bpy.ops.object.transform_apply(rotation=True)

        obj = self.boolean_difference(obj, channel)
        return obj

    # --- Build plate dimension and splitting methods ---

    def get_object_dimensions_mm(self, obj: Any) -> tuple[float, float, float]:
        """Return (x, y, z) bounding box dimensions in mm.

        Internal geometry is in meters, so multiply by 1000.
        """
        dims = obj.dimensions  # Blender reports in scene units (meters)
        return (dims.x * 1000.0, dims.y * 1000.0, dims.z * 1000.0)

    def split_object_for_plate(
        self,
        obj: Any,
        plate_x: float = 256.0,
        plate_y: float = 256.0,
        plate_z: float = 256.0,
        base_name: str | None = None,
        _depth: int = 0,
    ) -> list[tuple[str, Any]]:
        """Bisect an object along its longest oversize axis if it exceeds build plate.

        Returns a list of (name, object) tuples. Recursively splits if halves
        still exceed plate size. Adds alignment pin holes/posts on cut faces.

        Args:
            obj: Blender object to check/split
            plate_x: Build plate X dimension in mm
            plate_y: Build plate Y dimension in mm
            plate_z: Build plate Z dimension in mm
            base_name: Name prefix for split parts
            _depth: Recursion depth (internal)
        """
        if _depth > 4:
            # Safety limit on recursive splits
            name = base_name or obj.name
            return [(name, obj)]

        if base_name is None:
            base_name = obj.name

        dims_mm = self.get_object_dimensions_mm(obj)
        plate_dims = (plate_x, plate_y, plate_z)

        # Check if object fits within build plate
        oversize = [
            (dims_mm[0] - plate_dims[0], 0),  # X
            (dims_mm[1] - plate_dims[1], 1),  # Y
            (dims_mm[2] - plate_dims[2], 2),  # Z
        ]

        # Find the most oversize axis
        oversize.sort(key=lambda x: x[0], reverse=True)
        max_over, split_axis = oversize[0]

        if max_over <= 0:
            # Fits on plate — return as-is
            return [(base_name, obj)]

        # Split along the most oversize axis at the midpoint
        bbox_min = [obj.bound_box[0][i] + obj.location[i] for i in range(3)]
        bbox_max = [obj.bound_box[6][i] + obj.location[i] for i in range(3)]
        midpoint = (bbox_min[split_axis] + bbox_max[split_axis]) / 2

        # Determine a cutting plane size large enough to cover the object
        max_dim = max(obj.dimensions) * 2

        # Create cutting box for first half (keep the lower half)
        cut_loc_1 = [0.0, 0.0, 0.0]
        cut_loc_1[split_axis] = midpoint - max_dim / 2
        half1 = self.duplicate_object(obj, f"{base_name}_sec1")
        cutter1 = self.create_cube(size=max_dim, location=tuple(cut_loc_1), name="Cutter1")
        half1 = self.boolean_difference(half1, cutter1)

        # Create cutting box for second half (keep the upper half)
        cut_loc_2 = [0.0, 0.0, 0.0]
        cut_loc_2[split_axis] = midpoint + max_dim / 2
        half2 = self.duplicate_object(obj, f"{base_name}_sec2")
        cutter2 = self.create_cube(size=max_dim, location=tuple(cut_loc_2), name="Cutter2")
        half2 = self.boolean_difference(half2, cutter2)

        # Remove original
        self.bpy.data.objects.remove(obj, do_unlink=True)

        # Add alignment pins on cut faces (2 pins per cut)
        # Pin positions are on the cut plane, offset from center
        pin_offsets = []
        other_axes = [a for a in range(3) if a != split_axis]
        for ax in other_axes:
            offset = [0.0, 0.0, 0.0]
            offset[split_axis] = midpoint
            offset[ax] = (bbox_min[ax] + bbox_max[ax]) / 2 + obj.dimensions[ax] * 0.15
            pin_offsets.append(tuple(offset))

        pin_direction = [0.0, 0.0, 0.0]
        pin_direction[split_axis] = 1.0
        pin_dir_tuple = tuple(pin_direction)

        for pin_loc in pin_offsets:
            half1 = self.create_alignment_pin_hole(half1, pin_loc, direction=pin_dir_tuple)
            half2 = self.create_alignment_pin_post(half2, pin_loc, direction=pin_dir_tuple)

        # Recursively check each half
        results = []
        results.extend(self.split_object_for_plate(
            half1, plate_x, plate_y, plate_z, f"{base_name}_sec1", _depth + 1
        ))
        results.extend(self.split_object_for_plate(
            half2, plate_x, plate_y, plate_z, f"{base_name}_sec2", _depth + 1
        ))

        return results
