"""Command-line interface for Shardplate generator."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from . import __version__
from .config import (
    ColorConfig,
    GenerationConfig,
    ShardplateColorScheme,
    ShardplateConfig,
    SizeConfig,
)
from .generator import generate_from_config, generate_from_file, generate_with_wizard


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Shardplate 3D Print Generator.

    Generate STL files for 3D printable Shardplate armor from
    Brandon Sanderson's Stormlight Archive.

    Run with 'wizard' for interactive configuration, or use 'generate'
    with a config file.
    """
    pass


@main.command()
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="./output",
    help="Output directory for generated files",
)
@click.option(
    "--save-config", "-s",
    type=click.Path(),
    help="Save configuration to file after wizard",
)
def wizard(output: str, save_config: str | None) -> None:
    """Run interactive configuration wizard.

    Guides you through selecting size, colors, and armor pieces
    to generate a complete Shardplate suit.
    """
    try:
        from .config import ConfigWizard

        wizard = ConfigWizard()
        config = wizard.run()
        config.generation.output_directory = output

        if save_config:
            config.save(save_config)
            click.echo(f"Configuration saved to: {save_config}")

        click.echo("\nStarting generation...")
        results = generate_from_config(config)

        click.echo("\nDone! Your Shardplate armor files are ready.")
        click.echo(f"Files saved to: {output}/{config.name}/")

    except ImportError as e:
        click.echo(f"Error: Missing dependency - {e}", err=True)
        click.echo("Make sure Blender Python (bpy) is available.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error during generation: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Override output directory from config",
)
def generate(config_file: str, output: str | None) -> None:
    """Generate Shardplate from configuration file.

    CONFIG_FILE should be a JSON configuration file created by
    the wizard or manually.
    """
    try:
        config = ShardplateConfig.load(config_file)

        if output:
            config.generation.output_directory = output

        click.echo(f"Loading configuration: {config_file}")
        click.echo(f"Project: {config.name}")
        click.echo(f"Size: {config.size.size_name}")
        click.echo(f"Scale: {config.size.print_scale}")

        results = generate_from_config(config)

        click.echo("\nDone! Your Shardplate armor files are ready.")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--size", "-s",
    type=click.Choice(["XS", "S", "M", "L", "XL", "XXL"]),
    default="M",
    help="Standard size designation",
)
@click.option(
    "--scale",
    type=float,
    default=1.0,
    help="Print scale (1.0 = full size, 0.1 = 1:10)",
)
@click.option(
    "--color-scheme", "-c",
    type=click.Choice(ShardplateColorScheme.list_schemes()),
    default="kholin_blue",
    help="Predefined color scheme",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="./output",
    help="Output directory",
)
@click.option(
    "--name", "-n",
    default="shardplate",
    help="Project name",
)
@click.option(
    "--detail-level", "-d",
    type=click.IntRange(0, 3),
    default=2,
    help="Detail level (0-3)",
)
@click.option(
    "--no-straps",
    is_flag=True,
    help="Exclude strap mounting points",
)
@click.option(
    "--pieces",
    help="Comma-separated list of pieces to generate (helmet,chest,pauldrons,gauntlets,vambraces,cuisses,greaves,sabatons)",
)
def quick(
    size: str,
    scale: float,
    color_scheme: str,
    output: str,
    name: str,
    detail_level: int,
    no_straps: bool,
    pieces: str | None,
) -> None:
    """Quick generation with command-line options.

    Generate Shardplate without interactive wizard using
    command-line arguments.

    Examples:

        shardplate quick --size L --scale 0.1 --color-scheme windrunner_blue

        shardplate quick --pieces helmet,gauntlets --detail-level 3
    """
    try:
        # Build configuration
        scheme = ShardplateColorScheme.from_name(color_scheme)
        colors = ColorConfig.from_scheme(scheme)

        size_config = SizeConfig(size_name=size, print_scale=scale)

        gen_config = GenerationConfig(
            output_directory=output,
            detail_level=detail_level,
            include_strap_mounts=not no_straps,
        )

        # Handle piece selection
        if pieces:
            piece_list = [p.strip().lower() for p in pieces.split(",")]
            all_pieces = [
                "helmet", "chest", "pauldrons", "gauntlets",
                "vambraces", "cuisses", "greaves", "sabatons"
            ]
            for piece in all_pieces:
                setattr(gen_config, f"generate_{piece}", piece in piece_list)

        config = ShardplateConfig(
            name=name,
            colors=colors,
            size=size_config,
            generation=gen_config,
        )

        click.echo(f"Generating Shardplate: {name}")
        click.echo(f"Size: {size}, Scale: {scale}")
        click.echo(f"Color scheme: {color_scheme}")

        results = generate_from_config(config)

        click.echo("\nDone! Your Shardplate armor files are ready.")
        click.echo(f"Files saved to: {output}/{name}/")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def colors() -> None:
    """List available color schemes.

    Shows all predefined color schemes based on Shardplate
    appearances in the Stormlight Archive.
    """
    click.echo("\nAvailable Color Schemes:")
    click.echo("=" * 50)

    for scheme in ShardplateColorScheme:
        click.echo(f"\n  {scheme.scheme_name}")
        click.echo(f"    Primary:   {scheme.primary_hex}")
        click.echo(f"    Secondary: {scheme.secondary_hex}")

    click.echo("\n" + "=" * 50)
    click.echo("\nUse with: shardplate quick --color-scheme <name>")


@main.command()
@click.argument("output_file", type=click.Path())
@click.option(
    "--size", "-s",
    type=click.Choice(["XS", "S", "M", "L", "XL", "XXL"]),
    default="M",
    help="Standard size designation",
)
@click.option(
    "--color-scheme", "-c",
    type=click.Choice(ShardplateColorScheme.list_schemes()),
    default="kholin_blue",
    help="Predefined color scheme",
)
def create_config(output_file: str, size: str, color_scheme: str) -> None:
    """Create a configuration file template.

    Creates a JSON configuration file that can be customized
    and used with the 'generate' command.

    Example:

        shardplate create-config my_config.json --size L
        # Edit my_config.json as needed
        shardplate generate my_config.json
    """
    scheme = ShardplateColorScheme.from_name(color_scheme)
    config = ShardplateConfig(
        name="my_shardplate",
        colors=ColorConfig.from_scheme(scheme),
        size=SizeConfig(size_name=size),
        generation=GenerationConfig(),
    )

    config.save(output_file)
    click.echo(f"Configuration template saved to: {output_file}")
    click.echo("Edit this file to customize your Shardplate, then run:")
    click.echo(f"  shardplate generate {output_file}")


@main.command()
def info() -> None:
    """Show information about Shardplate armor.

    Displays lore information about Shardplate from
    Brandon Sanderson's Stormlight Archive.
    """
    info_text = """
SHARDPLATE - Information
========================

Shardplate is a type of magical armor from Brandon Sanderson's
Stormlight Archive series. Key characteristics:

APPEARANCE:
- Natural color is slate-grey, like unfinished steel
- Often painted or adorned with decorative details
- No visible gaps - overlapping plates create seamless look
- Helmets have horizontal eye slit visors
- Each suit has unique styling

PHYSICAL PROPERTIES:
- Weighs approximately 250kg (550 lbs)
- Powered by gemstones that provide Stormlight
- Looks like metal but shatters like stone when damaged
- Conforms to the shape of its wearer
- Adds several inches to wearer's height

CONSTRUCTION:
- Strictly solid plates - no chain or cloth inherent to suit
- Living Shardplate (Radiant) is comprised of spren
- Damage causes cracks, then explosive shattering

FAMOUS SETS:
- Dalinar Kholin: Unpainted slate-grey
- Adolin Kholin: Blue with silver trim
- Sadeas: Green with maroon
- Various Radiant orders have distinct appearances

This generator creates 3D-printable armor pieces based on
these canonical descriptions.
"""
    click.echo(info_text)


if __name__ == "__main__":
    main()
