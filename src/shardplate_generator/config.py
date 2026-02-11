"""Configuration system for Shardplate generator with sizing and color preferences."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ShardplateColorScheme(Enum):
    """Predefined Shardplate color schemes based on canonical descriptions."""

    # Alethi Highprince schemes
    KHOLIN_BLUE = ("kholin_blue", "#1E3A5F", "#C0C0C0")  # Dalinar/Adolin - Blue and Silver
    SADEAS_GREEN = ("sadeas_green", "#2D4A2D", "#8B0000")  # Sadeas - Green and Maroon
    ALADAR_ORANGE = ("aladar_orange", "#CC5500", "#1C1C1C")  # Aladar - Orange and Black
    HATHAM_PURPLE = ("hatham_purple", "#4B0082", "#FFD700")  # Purple and Gold
    ROION_YELLOW = ("roion_yellow", "#DAA520", "#2F4F4F")  # Gold and Dark Slate

    # Radiant Orders
    WINDRUNNER_BLUE = ("windrunner_blue", "#4169E1", "#FFFFFF")  # Royal Blue and White
    SKYBREAKER_BLACK = ("skybreaker_black", "#1C1C1C", "#C0C0C0")  # Black and Silver
    EDGEDANCER_BRONZE = ("edgedancer_bronze", "#CD7F32", "#228B22")  # Bronze and Forest Green
    STONEWARD_AMBER = ("stoneward_amber", "#FFBF00", "#8B4513")  # Amber and Brown
    BONDSMITH_GOLD = ("bondsmith_gold", "#FFD700", "#FFFFFF")  # Gold and White

    # Classic/Natural
    SLATE_GREY = ("slate_grey", "#708090", "#708090")  # Natural unpainted Shardplate
    BURNISHED_STEEL = ("burnished_steel", "#71797E", "#B8860B")  # Steel and Dark Gold

    def __init__(self, scheme_name: str, primary: str, secondary: str) -> None:
        self.scheme_name = scheme_name
        self.primary_hex = primary
        self.secondary_hex = secondary

    @classmethod
    def from_name(cls, name: str) -> ShardplateColorScheme:
        """Get color scheme by name."""
        name_lower = name.lower().replace(" ", "_").replace("-", "_")
        for scheme in cls:
            if scheme.scheme_name == name_lower:
                return scheme
        raise ValueError(f"Unknown color scheme: {name}")

    @classmethod
    def list_schemes(cls) -> list[str]:
        """List all available color scheme names."""
        return [scheme.scheme_name for scheme in cls]


@dataclass
class ColorConfig:
    """Color configuration for Shardplate materials."""

    primary_color: str = "#708090"  # Slate grey (natural Shardplate)
    secondary_color: str = "#C0C0C0"  # Silver accents
    accent_color: str = "#FFD700"  # Gold for gemstone areas
    glow_color: str = "#00BFFF"  # Stormlight blue glow

    # Material properties for rendering (if using Blender materials)
    metallic: float = 0.8
    roughness: float = 0.3
    emission_strength: float = 0.0  # Set > 0 for glowing Radiant plate

    @classmethod
    def from_scheme(cls, scheme: ShardplateColorScheme) -> ColorConfig:
        """Create color config from a predefined scheme."""
        return cls(
            primary_color=scheme.primary_hex,
            secondary_color=scheme.secondary_hex,
        )

    @classmethod
    def custom(cls, primary: str, secondary: str) -> ColorConfig:
        """Create custom color configuration."""
        return cls(primary_color=primary, secondary_color=secondary)

    def to_rgb(self, hex_color: str) -> tuple[float, float, float]:
        """Convert hex color to RGB tuple (0-1 range)."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))

    @property
    def primary_rgb(self) -> tuple[float, float, float]:
        return self.to_rgb(self.primary_color)

    @property
    def secondary_rgb(self) -> tuple[float, float, float]:
        return self.to_rgb(self.secondary_color)


@dataclass
class SizeConfig:
    """Body size configuration for armor fitting."""

    # Standard size designation
    size_name: str = "M"

    # Individual measurements (in meters) - override defaults if provided
    height: float | None = None
    chest_circumference: float | None = None
    waist_circumference: float | None = None
    hip_circumference: float | None = None
    shoulder_width: float | None = None
    arm_length: float | None = None
    leg_length: float | None = None
    head_circumference: float | None = None
    hand_length: float | None = None
    foot_length: float | None = None

    # Print scaling
    print_scale: float = 1.0  # 1.0 = full size, 0.1 = 1/10 scale

    # Fit adjustment
    clearance_mm: float = 20.0  # Extra space for comfort (millimeters)

    def get_measurements(self) -> dict[str, float | None]:
        """Get all custom measurements as dict."""
        return {
            "height": self.height,
            "chest_circumference": self.chest_circumference,
            "waist_circumference": self.waist_circumference,
            "hip_circumference": self.hip_circumference,
            "shoulder_width": self.shoulder_width,
            "arm_length": self.arm_length,
            "leg_length": self.leg_length,
            "head_circumference": self.head_circumference,
            "hand_length": self.hand_length,
            "foot_length": self.foot_length,
        }


@dataclass
class GenerationConfig:
    """Configuration for what to generate and how."""

    # Armor pieces to generate
    generate_helmet: bool = True
    generate_chest: bool = True
    generate_pauldrons: bool = True
    generate_gauntlets: bool = True
    generate_vambraces: bool = True
    generate_cuisses: bool = True
    generate_greaves: bool = True
    generate_sabatons: bool = True

    # Generation options
    include_strap_mounts: bool = True
    detail_level: int = 2  # 0-3
    split_for_printing: bool = True  # Split large pieces
    hollow_pieces: bool = True  # Hollow for material savings

    # Articulation / segmentation
    segmented_output: bool = True  # Separate articulated segments (vs monolithic)

    # Build plate dimensions (mm) for auto-splitting
    build_plate_x: float = 256.0
    build_plate_y: float = 256.0
    build_plate_z: float = 256.0
    auto_split_for_plate: bool = True  # Auto-split pieces exceeding build volume

    # Output options
    output_format: str = "stl"  # stl, obj, blend
    output_directory: str = "./output"


@dataclass
class ShardplateConfig:
    """Complete configuration for Shardplate generation."""

    name: str = "my_shardplate"
    colors: ColorConfig = field(default_factory=ColorConfig)
    size: SizeConfig = field(default_factory=SizeConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)

    def save(self, filepath: str | Path) -> None:
        """Save configuration to JSON file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        config_dict = {
            "name": self.name,
            "colors": asdict(self.colors),
            "size": asdict(self.size),
            "generation": asdict(self.generation),
        }

        with open(filepath, "w") as f:
            json.dump(config_dict, f, indent=2)

    @classmethod
    def load(cls, filepath: str | Path) -> ShardplateConfig:
        """Load configuration from JSON file."""
        with open(filepath) as f:
            data = json.load(f)

        return cls(
            name=data.get("name", "my_shardplate"),
            colors=ColorConfig(**data.get("colors", {})),
            size=SizeConfig(**data.get("size", {})),
            generation=GenerationConfig(**data.get("generation", {})),
        )

    @classmethod
    def from_wizard(cls) -> ShardplateConfig:
        """Create configuration using interactive wizard."""
        from .wizard import ConfigWizard

        wizard = ConfigWizard()
        return wizard.run()


class ConfigWizard:
    """Interactive configuration wizard for terminal use."""

    def __init__(self) -> None:
        self.config = ShardplateConfig()

    def run(self) -> ShardplateConfig:
        """Run the interactive wizard."""
        print("\n" + "=" * 60)
        print("  SHARDPLATE ARMOR GENERATOR - Configuration Wizard")
        print("  Based on Brandon Sanderson's Stormlight Archive")
        print("=" * 60 + "\n")

        self._get_name()
        self._get_size()
        self._get_colors()
        self._get_generation_options()

        print("\n" + "=" * 60)
        print("  Configuration Complete!")
        print("=" * 60 + "\n")

        return self.config

    def _get_name(self) -> None:
        """Get project name."""
        print("PROJECT NAME")
        print("-" * 40)
        name = input("Enter a name for your Shardplate project [my_shardplate]: ").strip()
        if name:
            self.config.name = name.replace(" ", "_").lower()
        print()

    def _get_size(self) -> None:
        """Get size configuration."""
        print("SIZING OPTIONS")
        print("-" * 40)
        print("Choose sizing method:")
        print("  1. Standard size (XS, S, M, L, XL, XXL)")
        print("  2. Custom measurements")
        print("  3. Scaled model (for display/miniature)")
        print()

        choice = input("Select option [1]: ").strip() or "1"

        if choice == "1":
            self._get_standard_size()
        elif choice == "2":
            self._get_custom_measurements()
        elif choice == "3":
            self._get_scale_size()
        else:
            self._get_standard_size()

        print()

    def _get_standard_size(self) -> None:
        """Get standard size selection."""
        print("\nStandard Sizes:")
        print("  XS  - Extra Small (150-160cm height)")
        print("  S   - Small (160-170cm height)")
        print("  M   - Medium (170-180cm height)")
        print("  L   - Large (180-190cm height)")
        print("  XL  - Extra Large (190-200cm height)")
        print("  XXL - Double Extra Large (200cm+ height)")
        print()

        size = input("Enter size [M]: ").strip().upper() or "M"
        if size in ["XS", "S", "M", "L", "XL", "XXL"]:
            self.config.size.size_name = size
        else:
            print(f"Invalid size '{size}', using M")
            self.config.size.size_name = "M"

    def _get_custom_measurements(self) -> None:
        """Get custom body measurements."""
        print("\nEnter your measurements in centimeters.")
        print("Press Enter to skip any measurement (will use default).\n")

        measurements = [
            ("height", "Height (cm)", 175),
            ("chest_circumference", "Chest circumference (cm)", 100),
            ("waist_circumference", "Waist circumference (cm)", 85),
            ("hip_circumference", "Hip circumference (cm)", 100),
            ("shoulder_width", "Shoulder width (cm)", 46),
            ("head_circumference", "Head circumference (cm)", 57),
            ("hand_length", "Hand length (cm)", 19),
            ("foot_length", "Foot length (cm)", 27),
        ]

        for attr, prompt, default in measurements:
            value = input(f"  {prompt} [{default}]: ").strip()
            if value:
                try:
                    # Convert cm to meters
                    setattr(self.config.size, attr, float(value) / 100)
                except ValueError:
                    print(f"    Invalid value, using default {default}cm")

        self.config.size.size_name = "custom"

    def _get_scale_size(self) -> None:
        """Get scale for miniature/display models."""
        print("\nScale Options:")
        print("  0.1  - 1:10 scale (~17cm tall)")
        print("  0.2  - 1:5 scale (~35cm tall)")
        print("  0.25 - 1:4 scale (~44cm tall)")
        print("  0.5  - 1:2 scale (~88cm tall)")
        print("  1.0  - Full size (wearable)")
        print()

        scale = input("Enter scale [1.0]: ").strip() or "1.0"
        try:
            self.config.size.print_scale = float(scale)
        except ValueError:
            print("Invalid scale, using 1.0")
            self.config.size.print_scale = 1.0

    def _get_colors(self) -> None:
        """Get color configuration."""
        print("COLOR SCHEME")
        print("-" * 40)
        print("Shardplate can be painted in various colors.")
        print("Choose a color scheme:\n")

        schemes = ShardplateColorScheme.list_schemes()
        for i, scheme in enumerate(schemes, 1):
            scheme_obj = ShardplateColorScheme.from_name(scheme)
            print(f"  {i:2}. {scheme.replace('_', ' ').title()}")
            print(f"      Primary: {scheme_obj.primary_hex}  Secondary: {scheme_obj.secondary_hex}")

        print(f"  {len(schemes) + 1}. Custom colors")
        print()

        choice = input(f"Select scheme [1-{len(schemes) + 1}] or name [1]: ").strip() or "1"

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(schemes):
                scheme = ShardplateColorScheme.from_name(schemes[idx])
                self.config.colors = ColorConfig.from_scheme(scheme)
                print(f"\n  Selected: {schemes[idx].replace('_', ' ').title()}")
            elif idx == len(schemes):
                self._get_custom_colors()
            else:
                self.config.colors = ColorConfig.from_scheme(ShardplateColorScheme.KHOLIN_BLUE)
        except ValueError:
            # Try to match by name
            try:
                scheme = ShardplateColorScheme.from_name(choice)
                self.config.colors = ColorConfig.from_scheme(scheme)
            except ValueError:
                print("Invalid choice, using Kholin Blue")
                self.config.colors = ColorConfig.from_scheme(ShardplateColorScheme.KHOLIN_BLUE)

        print()

    def _get_custom_colors(self) -> None:
        """Get custom color values."""
        print("\nEnter colors as hex values (e.g., #1E3A5F) or color names.\n")

        primary = input("  Primary color [#708090]: ").strip() or "#708090"
        secondary = input("  Secondary color [#C0C0C0]: ").strip() or "#C0C0C0"

        # Basic validation
        if not primary.startswith("#"):
            primary = f"#{primary}"
        if not secondary.startswith("#"):
            secondary = f"#{secondary}"

        self.config.colors = ColorConfig.custom(primary, secondary)

    def _get_generation_options(self) -> None:
        """Get generation options."""
        print("GENERATION OPTIONS")
        print("-" * 40)

        # Armor pieces
        print("Which armor pieces to generate?")
        print("  Enter 'all' for complete set, or list piece numbers.\n")

        pieces = [
            ("generate_helmet", "Helmet"),
            ("generate_chest", "Chest (breastplate + backplate)"),
            ("generate_pauldrons", "Pauldrons (shoulders) - pair"),
            ("generate_gauntlets", "Gauntlets (hands) - pair"),
            ("generate_vambraces", "Vambraces (forearms) - pair"),
            ("generate_cuisses", "Cuisses (thighs) - pair"),
            ("generate_greaves", "Greaves (shins) - pair"),
            ("generate_sabatons", "Sabatons (feet) - pair"),
        ]

        for i, (_, name) in enumerate(pieces, 1):
            print(f"  {i}. {name}")

        print()
        selection = input("Select pieces [all]: ").strip().lower() or "all"

        if selection != "all":
            # Disable all first
            for attr, _ in pieces:
                setattr(self.config.generation, attr, False)

            # Enable selected
            try:
                indices = [int(x.strip()) - 1 for x in selection.replace(",", " ").split()]
                for idx in indices:
                    if 0 <= idx < len(pieces):
                        setattr(self.config.generation, pieces[idx][0], True)
            except ValueError:
                print("Invalid selection, generating all pieces")
                for attr, _ in pieces:
                    setattr(self.config.generation, attr, True)

        # Detail level
        print("\nDetail level:")
        print("  0 - Minimal (fastest print)")
        print("  1 - Basic (simple details)")
        print("  2 - Standard (recommended)")
        print("  3 - High (finest details)")
        print()

        detail = input("Select detail level [2]: ").strip() or "2"
        try:
            self.config.generation.detail_level = min(3, max(0, int(detail)))
        except ValueError:
            self.config.generation.detail_level = 2

        # Strap mounts
        straps = input("\nInclude strap mounting points? [Y/n]: ").strip().lower()
        self.config.generation.include_strap_mounts = straps != "n"

        # Output directory
        output = input("\nOutput directory [./output]: ").strip() or "./output"
        self.config.generation.output_directory = output

        print()
