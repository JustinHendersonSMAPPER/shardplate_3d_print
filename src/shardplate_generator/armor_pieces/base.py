"""Base class for armor piece generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..utils.blender_utils import BlenderContext
    from ..utils.measurements import HumanMeasurements
    from ..utils.strap_system import StrapSystem


@dataclass
class ArmorPieceGenerator(ABC):
    """Abstract base class for generating armor pieces."""

    name: str
    measurements: HumanMeasurements | None = None
    include_straps: bool = True
    detail_level: int = 2  # 0=minimal, 1=basic, 2=standard, 3=high
    _ctx: Any = field(default=None, repr=False)
    _strap_system: Any = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize measurements if not provided."""
        if self.measurements is None:
            from ..utils.measurements import HumanMeasurements

            self.measurements = HumanMeasurements()

    @property
    def ctx(self) -> BlenderContext:
        """Get or create Blender context."""
        if self._ctx is None:
            from ..utils.blender_utils import BlenderContext

            self._ctx = BlenderContext()
        return self._ctx

    @property
    def dimensions(self) -> dict[str, float]:
        """Get armor dimensions from measurements."""
        if self.measurements is None:
            from ..utils.measurements import HumanMeasurements

            self.measurements = HumanMeasurements()
        all_dims = self.measurements.get_armor_dimensions()
        return all_dims.get(self.armor_type, {})

    @property
    @abstractmethod
    def armor_type(self) -> str:
        """Return the type identifier for this armor piece."""
        ...

    @abstractmethod
    def generate(self) -> Any:
        """Generate the armor piece mesh."""
        ...

    def get_strap_system(self) -> StrapSystem:
        """Get or create the strap system for this piece."""
        if self._strap_system is None:
            from ..utils.strap_system import create_standard_strap_system

            self._strap_system = create_standard_strap_system(
                self.armor_type, self.dimensions
            )
        return self._strap_system

    def apply_straps(self, obj: Any) -> Any:
        """Apply strap mounting points to the armor piece."""
        if self.include_straps:
            strap_system = self.get_strap_system()
            obj = strap_system.apply_to_mesh(self.ctx, obj)
        return obj

    def add_shardplate_details(self, obj: Any) -> Any:
        """Add characteristic Shardplate surface details."""
        if self.detail_level >= 1:
            # Add edge details characteristic of Shardplate
            obj = self.ctx.add_edge_detail(obj, pattern="angular")

        if self.detail_level >= 2:
            # Add subtle bevel for print quality
            obj = self.ctx.add_bevel(obj, width=0.001, segments=2)

        return obj

    def finalize(self, obj: Any) -> Any:
        """Apply final processing to the armor piece."""
        obj = self.add_shardplate_details(obj)
        obj = self.apply_straps(obj)
        return obj

    def export(self, obj: Any, output_dir: str | Path) -> Path:
        """Export the armor piece to STL."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / f"{self.name}.stl"
        self.ctx.export_stl(obj, str(filepath))
        return filepath

    def generate_and_export(self, output_dir: str | Path) -> Path:
        """Generate the armor piece and export to STL."""
        obj = self.generate()
        obj = self.finalize(obj)
        return self.export(obj, output_dir)

    # --- Segmented articulation methods ---

    def generate_segments(self) -> dict[str, Any]:
        """Generate named segments instead of one monolithic mesh.

        Override in subclasses to produce articulated segments.
        Default returns the monolithic mesh as a single segment.
        """
        obj = self.generate()
        obj = self.finalize(obj)
        return {self.name: obj}

    def export_segments(
        self,
        segments: dict[str, Any],
        output_dir: str | Path,
    ) -> list[Path]:
        """Export each segment as a separate STL into a subdirectory."""
        output_dir = Path(output_dir) / self.name
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        for seg_name, obj in segments.items():
            filepath = output_dir / f"{seg_name}.stl"
            self.ctx.export_stl(obj, str(filepath))
            paths.append(filepath)
        return paths

    def split_for_build_plate(
        self,
        segments: dict[str, Any],
        plate_x: float = 256.0,
        plate_y: float = 256.0,
        plate_z: float = 256.0,
    ) -> dict[str, Any]:
        """Check each segment against build plate, split any that don't fit.

        Naming convention: segment_name_sec1, segment_name_sec2, etc.
        """
        result: dict[str, Any] = {}
        for seg_name, obj in segments.items():
            parts = self.ctx.split_object_for_plate(
                obj, plate_x, plate_y, plate_z, base_name=seg_name
            )
            for part_name, part_obj in parts:
                result[part_name] = part_obj
        return result

    def generate_and_export_segmented(
        self,
        output_dir: str | Path,
        plate_x: float = 256.0,
        plate_y: float = 256.0,
        plate_z: float = 256.0,
        auto_split: bool = True,
    ) -> list[Path]:
        """Full pipeline: generate segments -> split for plate -> export."""
        segments = self.generate_segments()
        if auto_split:
            segments = self.split_for_build_plate(segments, plate_x, plate_y, plate_z)
        return self.export_segments(segments, output_dir)


@dataclass
class SymmetricArmorPieceGenerator(ArmorPieceGenerator):
    """Base class for armor pieces that come in left/right pairs."""

    side: str = "left"  # "left" or "right"

    @property
    def name(self) -> str:
        """Get name including side."""
        return f"{self._base_name}_{self.side}"

    @name.setter
    def name(self, value: str) -> None:
        """Set base name."""
        self._base_name = value.replace("_left", "").replace("_right", "")

    @abstractmethod
    def generate_base(self) -> Any:
        """Generate the base (left side) armor piece."""
        ...

    def generate(self) -> Any:
        """Generate the armor piece, mirroring if necessary."""
        obj = self.generate_base()
        if self.side == "right":
            obj = self.ctx.mirror_object(obj, axis="X", name=self.name)
        return obj

    def generate_pair(self) -> tuple[Any, Any]:
        """Generate both left and right pieces."""
        left_obj = self.generate_base()
        left_obj.name = f"{self._base_name}_left"

        self.side = "right"
        right_obj = self.ctx.mirror_object(left_obj, axis="X", name=f"{self._base_name}_right")

        return left_obj, right_obj

    def export_pair(self, output_dir: str | Path) -> tuple[Path, Path]:
        """Generate and export both left and right pieces."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        left_obj, right_obj = self.generate_pair()

        left_obj = self.finalize(left_obj)
        right_obj = self.finalize(right_obj)

        left_path = output_dir / f"{self._base_name}_left.stl"
        right_path = output_dir / f"{self._base_name}_right.stl"

        self.ctx.export_stl(left_obj, str(left_path))
        self.ctx.export_stl(right_obj, str(right_path))

        return left_path, right_path

    # --- Segmented articulation methods for symmetric pieces ---

    def generate_segments_base(self) -> dict[str, Any]:
        """Generate segmented output for the base (left) side.

        Override in subclasses to produce articulated segments.
        Default returns the monolithic left mesh as a single segment.
        """
        obj = self.generate_base()
        obj = self.finalize(obj)
        return {f"{self._base_name}_left": obj}

    def _mirror_segments(self, segments: dict[str, Any]) -> dict[str, Any]:
        """Mirror a dict of segments from left to right."""
        mirrored: dict[str, Any] = {}
        for seg_name, obj in segments.items():
            right_name = seg_name.replace("_left", "_right")
            mirrored[right_name] = self.ctx.mirror_object(obj, axis="X", name=right_name)
        return mirrored

    def export_pair_segmented(
        self,
        output_dir: str | Path,
        plate_x: float = 256.0,
        plate_y: float = 256.0,
        plate_z: float = 256.0,
        auto_split: bool = True,
    ) -> list[Path]:
        """Generate and export segmented pairs for both sides."""
        self.side = "left"
        left_segments = self.generate_segments_base()
        right_segments = self._mirror_segments(left_segments)

        all_paths: list[Path] = []

        for side_label, segments in [("left", left_segments), ("right", right_segments)]:
            if auto_split:
                segments = self.split_for_build_plate(segments, plate_x, plate_y, plate_z)
            seg_dir = Path(output_dir) / f"{self._base_name}_{side_label}"
            seg_dir.mkdir(parents=True, exist_ok=True)
            for seg_name, obj in segments.items():
                filepath = seg_dir / f"{seg_name}.stl"
                self.ctx.export_stl(obj, str(filepath))
                all_paths.append(filepath)

        return all_paths
