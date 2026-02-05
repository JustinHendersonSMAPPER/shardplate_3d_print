# Shardplate 3D Print Generator

Generate 3D-printable STL files for wearable Shardplate armor from Brandon Sanderson's Stormlight Archive series.

## Features

- **Complete Armor Set**: Helmet, chest (breastplate/backplate), pauldrons, gauntlets, vambraces, cuisses, greaves, and sabatons
- **Customizable Sizing**: Standard sizes (XS-XXL), custom measurements, or scaled models
- **Authentic Color Schemes**: 12 predefined schemes based on Alethi Highprinces and Radiant orders
- **Strap Mounting System**: Built-in attachment points for wearable assembly
- **Print-Ready**: Pieces split for easier printing, with appropriate wall thickness

## Installation

### Requirements

- Python 3.10+
- Blender 3.0+ (with Python support)
- Poetry (for dependency management)

### Install with Poetry

```bash
git clone https://github.com/yourusername/shardplate_3d_print.git
cd shardplate_3d_print
poetry install
```

### Running with Blender

This project uses Blender's Python API (bpy). You can run it in several ways:

1. **From Blender's Python console**:
   ```python
   import sys
   sys.path.append('/path/to/shardplate_3d_print/src')
   from shardplate_generator import generate_with_wizard
   generate_with_wizard()
   ```

2. **Using Blender's Python**:
   ```bash
   blender --background --python scripts/generate.py
   ```

3. **Install bpy as standalone** (experimental):
   ```bash
   pip install bpy
   poetry run shardplate wizard
   ```

## Usage

### Interactive Wizard

The easiest way to generate your Shardplate:

```bash
poetry run shardplate wizard
```

This guides you through:
1. Project naming
2. Size selection (standard or custom measurements)
3. Color scheme selection
4. Armor piece selection
5. Detail level

### Quick Generation

Generate with command-line options:

```bash
# Full size, Kholin blue color scheme
poetry run shardplate quick --size L --color-scheme kholin_blue

# Scaled model (1:10) for display
poetry run shardplate quick --scale 0.1 --size M

# Specific pieces only
poetry run shardplate quick --pieces helmet,gauntlets --detail-level 3
```

### Configuration File

Create and use a config file for reproducible builds:

```bash
# Create config template
poetry run shardplate create-config my_armor.json --size L --color-scheme windrunner_blue

# Edit my_armor.json as needed, then generate
poetry run shardplate generate my_armor.json
```

### List Color Schemes

```bash
poetry run shardplate colors
```

## Color Schemes

Based on canonical Shardplate appearances:

| Scheme | Primary | Secondary | Description |
|--------|---------|-----------|-------------|
| kholin_blue | #1E3A5F | #C0C0C0 | Dalinar/Adolin - Blue and Silver |
| sadeas_green | #2D4A2D | #8B0000 | Sadeas - Green and Maroon |
| aladar_orange | #CC5500 | #1C1C1C | Aladar - Orange and Black |
| windrunner_blue | #4169E1 | #FFFFFF | Windrunner Order - Royal Blue and White |
| skybreaker_black | #1C1C1C | #C0C0C0 | Skybreaker Order - Black and Silver |
| bondsmith_gold | #FFD700 | #FFFFFF | Bondsmith Order - Gold and White |
| slate_grey | #708090 | #708090 | Natural unpainted Shardplate |

## Armor Pieces

### Generated Files

A complete set generates these STL files:

```
output/my_shardplate/
├── helmet_front.stl      # Front helmet piece
├── helmet_back.stl       # Back helmet piece
├── chest_front.stl       # Breastplate
├── chest_back.stl        # Backplate
├── pauldron_left.stl     # Left shoulder
├── pauldron_right.stl    # Right shoulder
├── gauntlet_left.stl     # Left hand
├── gauntlet_right.stl    # Right hand
├── vambrace_left.stl     # Left forearm
├── vambrace_right.stl    # Right forearm
├── cuisse_left.stl       # Left thigh
├── cuisse_right.stl      # Right thigh
├── greave_left.stl       # Left shin
├── greave_right.stl      # Right shin
├── sabaton_left.stl      # Left foot
├── sabaton_right.stl     # Right foot
└── config.json           # Configuration used
```

## Assembly Instructions

### Materials Needed

- 3D printed armor pieces
- 25mm nylon webbing straps
- Side-release buckles (various sizes)
- Velcro strips (hook and loop)
- Foam padding (EVA foam recommended)
- Spray paint in chosen colors
- Clear coat sealant

### Printing Recommendations

| Piece | Layer Height | Infill | Supports | Print Time (estimate) |
|-------|-------------|--------|----------|----------------------|
| Helmet | 0.2mm | 15% | Yes | 20-30 hours |
| Chest (each half) | 0.2mm | 15% | Yes | 30-40 hours |
| Pauldrons | 0.2mm | 15% | Yes | 8-12 hours each |
| Gauntlets | 0.15mm | 20% | Yes | 10-15 hours each |
| Vambraces | 0.2mm | 15% | Yes | 6-10 hours each |
| Cuisses | 0.2mm | 15% | Yes | 15-20 hours each |
| Greaves | 0.2mm | 15% | Yes | 12-18 hours each |
| Sabatons | 0.2mm | 20% | Yes | 8-12 hours each |

**Material**: PLA or PETG recommended. ABS for higher durability.

### Assembly Steps

#### 1. Post-Processing
- Remove support material
- Sand seams and layer lines (80-400 grit progression)
- Fill gaps with body filler if needed
- Apply filler primer, sand smooth

#### 2. Painting
- Apply primer coat
- Base coat with primary color
- Detail with secondary color on edges/accents
- Add weathering if desired
- Apply clear coat for durability

#### 3. Strapping System

**Helmet**:
- Thread chin strap through slots on each side
- Attach buckle under chin
- Add foam padding inside for comfort

**Chest Armor**:
- Connect front and back plates with side straps (2 per side)
- Add shoulder straps connecting to pauldron mounts
- Use velcro for fine adjustment

**Pauldrons**:
- Attach to chest armor shoulder mounts using buckles
- Add arm strap through lower slot
- Should overlap with vambrace top

**Arms (Vambraces + Gauntlets)**:
- Vambraces wrap around forearm with 2 straps
- Gauntlets connect to vambraces at wrist
- Use velcro for wrist closure

**Legs (Cuisses + Greaves + Sabatons)**:
- Cuisses attach to belt with clips at top
- Wrap around thigh with side straps
- Greaves connect below knee cop
- Sabatons attach at ankle with straps and lacing

#### 4. Wearing Order

1. Sabatons (feet)
2. Greaves (shins)
3. Cuisses (thighs) - attach to belt
4. Chest armor (front then connect back)
5. Vambraces (forearms)
6. Gauntlets (hands)
7. Pauldrons (attach to chest)
8. Helmet (last)

## Lore Accuracy

This generator follows canonical Shardplate descriptions:

- **Appearance**: Overlapping plates with no visible gaps
- **Material**: Resembles metal but with stone-like properties
- **Helmet**: Horizontal eye slit visor
- **Natural Color**: Slate-grey (unpainted)
- **Customization**: Commonly painted and decorated

Sources: [Coppermind Wiki - Shardplate](https://coppermind.net/wiki/Shardplate), [17th Shard](https://www.17thshard.com/)

## Development

### Linting

```bash
poetry run ruff check src/
poetry run black --check src/
poetry run mypy src/
```

### Testing

```bash
poetry run pytest
```

## License

MIT License - See LICENSE file.

## Disclaimer

This is a fan project. Shardplate and the Stormlight Archive are creations of Brandon Sanderson. This project is not affiliated with or endorsed by Brandon Sanderson or Dragonsteel Entertainment.

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.
