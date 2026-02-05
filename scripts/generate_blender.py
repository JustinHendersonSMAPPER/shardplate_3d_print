#!/usr/bin/env python3
"""
Blender script wrapper for Shardplate generation.

Run this script from Blender:
    blender --background --python scripts/generate_blender.py -- [options]

Or from Blender's Python console:
    exec(open('scripts/generate_blender.py').read())
"""

import sys
from pathlib import Path

# Add src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))


def main() -> None:
    """Run Shardplate generator."""
    # Parse arguments after '--'
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    # Check for config file argument
    if argv and Path(argv[0]).exists():
        from shardplate_generator.generator import generate_from_file
        print(f"Generating from config: {argv[0]}")
        generate_from_file(argv[0])
    else:
        # Run interactive wizard
        from shardplate_generator.generator import generate_with_wizard
        print("Starting Shardplate Configuration Wizard...")
        generate_with_wizard()


if __name__ == "__main__":
    main()
