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
        bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True)

    def export_all_stl(self, filepath: str) -> None:
        """Export all visible objects to STL format."""
        bpy = self.bpy
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True)

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
