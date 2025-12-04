"""
Strata CLI entry point.

"I have been consulting the records of the winds and currents...
the results are startling." — Matthew Fontaine Maury
"""

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option()
def main():
    """Strata: Create plotter-ready vector maps from GIS sources."""
    pass


@main.command()
@click.argument("name", required=False)
@click.option("--from", "template", help="Start from a template recipe")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
def new(name: str | None, template: str | None, output: str | None):
    """Launch the interactive wizard to create a new recipe."""
    from strata.tui.app import StrataWizard

    app = StrataWizard(initial_name=name, template=template, output_dir=output)
    app.run()


@main.command()
@click.argument("recipe", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Show what would be downloaded")
@click.option("--force", is_flag=True, help="Re-download even if cached")
def prepare(recipe: str, dry_run: bool, force: bool):
    """Download and cache all sources for a recipe."""
    from strata.maury import Recipe, Pipeline

    console.print(f"\n[bold]Preparing:[/] {recipe}\n")

    # Load recipe
    try:
        r = Recipe.from_file(recipe)
    except Exception as e:
        console.print(f"[red]Error loading recipe:[/] {e}")
        raise SystemExit(1)

    pipeline = Pipeline(r)

    if dry_run:
        # Show what would be downloaded
        estimate = pipeline.estimate()

        console.print("[bold]Sources:[/]")
        for src in estimate["sources"]:
            status = "[green]cached[/]" if src.get("cached") else f"[cyan]~{src.get('estimated_size_mb', 0):.1f} MB[/]"
            console.print(f"  {src['name']}: {status}")

        console.print(f"\n[bold]Summary:[/]")
        console.print(f"  Cached: {estimate['cached_count']}")
        console.print(f"  To download: {estimate['download_count']}")
        console.print(f"  Estimated size: ~{estimate['total_size_mb']:.1f} MB")
    else:
        # Actually download
        try:
            paths = pipeline.prepare(force=force)
            console.print(f"\n[green]✓[/] Prepared {len(paths)} sources")
        except Exception as e:
            console.print(f"\n[red]Error:[/] {e}")
            raise SystemExit(1)


@main.command()
@click.argument("recipe", type=click.Path(exists=True))
@click.option("--format", "-f", help="Only build specific format (svg, geojson, pmtiles)")
@click.option("--quality", "-q", help="Only build specific quality level")
@click.option("--layer", "-l", multiple=True, help="Only build specific layer(s)")
@click.option("--output", "-o", type=click.Path(), default="./output", help="Output directory")
@click.option("--no-cache", is_flag=True, help="Don't use cached source data")
@click.option("--dry-run", is_flag=True, help="Show what would be built")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed progress")
def build(
    recipe: str,
    format: str | None,
    quality: str | None,
    layer: tuple[str, ...],
    output: str,
    no_cache: bool,
    dry_run: bool,
    verbose: bool,
):
    """Build outputs from a recipe file."""
    from strata.maury import Recipe, Pipeline

    console.print(f"\n[bold]Building:[/] {recipe}\n")

    # Load recipe
    try:
        r = Recipe.from_file(recipe)
    except Exception as e:
        console.print(f"[red]Error loading recipe:[/] {e}")
        raise SystemExit(1)

    # Validate references
    errors = r.validate_references()
    if errors:
        console.print("[red]Recipe validation errors:[/]")
        for err in errors:
            console.print(f"  - {err}")
        raise SystemExit(1)

    if dry_run:
        console.print("[bold]Recipe summary:[/]")
        console.print(f"  Name: {r.name}")
        console.print(f"  Sources: {len(r.sources)}")
        console.print(f"  Layers: {len(r.layers)}")
        console.print(f"  Output formats: {[f.type for f in r.output.formats]}")
        return

    # Run build pipeline
    pipeline = Pipeline(r)
    try:
        files = pipeline.build(output, force=no_cache)

        console.print(f"\n[green]✓[/] Build complete!")
        console.print(f"[bold]Output:[/] {output}/{r.name}/")
        console.print(f"  Created {len(files)} files")

    except Exception as e:
        console.print(f"\n[red]Build failed:[/] {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise SystemExit(1)


@main.command()
@click.argument("recipe", type=click.Path(exists=True))
@click.option("--source", "-s", multiple=True, help="Only fetch specific source(s)")
@click.option("--force", is_flag=True, help="Re-download even if cached")
def fetch(recipe: str, source: tuple[str, ...], force: bool):
    """Download and cache sources without processing."""
    # TODO: Implement fetch
    console.print(f"[bold]Fetching sources from:[/] {recipe}")
    console.print("[yellow]Fetch command not yet implemented[/]")


@main.command()
@click.argument("recipe", type=click.Path(exists=True))
@click.option("--bounds", "-b", help="Override bounds: 'minx,miny,maxx,maxy'")
@click.option("--open", "open_svg", is_flag=True, help="Open a quick SVG preview")
@click.option("--output", "-o", type=click.Path(), help="Save preview SVG to path")
def preview(recipe: str, bounds: str | None, open_svg: bool, output: str | None):
    """Preview what data falls within the recipe bounds.

    Shows feature counts per source/layer within the bounding box.
    Use --open to generate and view a quick SVG preview.

    Examples:
        strata preview recipe.yaml
        strata preview recipe.yaml --bounds="-73.5,42.7,-71.5,45.0"
        strata preview recipe.yaml --open
    """
    from strata.maury import Recipe, Pipeline
    import geopandas as gpd
    from shapely.geometry import box

    console.print(f"\n[bold]Preview:[/] {recipe}\n")

    # Load recipe
    try:
        r = Recipe.from_file(recipe)
    except Exception as e:
        console.print(f"[red]Error loading recipe:[/] {e}")
        raise SystemExit(1)

    # Determine bounds
    if bounds:
        # Parse CLI bounds
        try:
            bbox = [float(x.strip()) for x in bounds.split(",")]
            if len(bbox) != 4:
                raise ValueError("Need exactly 4 values")
        except ValueError as e:
            console.print(f"[red]Invalid bounds format:[/] {e}")
            console.print("Expected: minx,miny,maxx,maxy (e.g., -73.5,42.7,-71.5,45.0)")
            raise SystemExit(1)
    elif isinstance(r.output.bounds, list) and len(r.output.bounds) == 4:
        bbox = r.output.bounds
    else:
        console.print("[yellow]No bounds specified in recipe or CLI.[/]")
        console.print("Use --bounds or set output.bounds in recipe.")
        console.print("\nShowing recipe summary instead:\n")
        console.print(f"  [bold]Sources:[/] {len(r.sources)}")
        for name in r.sources:
            console.print(f"    - {name}")
        console.print(f"  [bold]Layers:[/] {len(r.layers)}")
        for layer in r.layers:
            console.print(f"    - {layer.name}")
        return

    console.print(f"[bold]Bounds:[/] [{bbox[0]:.3f}, {bbox[1]:.3f}, {bbox[2]:.3f}, {bbox[3]:.3f}]")
    console.print(f"        (west, south, east, north)\n")

    # Prepare sources
    pipeline = Pipeline(r)
    try:
        paths = pipeline.prepare(force=False)
    except Exception as e:
        console.print(f"[red]Error preparing sources:[/] {e}")
        raise SystemExit(1)

    # Load and analyze each source
    clip_box = box(*bbox)

    console.print("[bold]Sources within bounds:[/]")
    source_stats = {}

    for name, path in paths.items():
        try:
            gdf = gpd.read_file(path)
            total = len(gdf)

            # Count features intersecting bounds
            intersecting = gdf[gdf.geometry.intersects(clip_box)]
            inside_count = len(intersecting)

            # Clip and count what remains
            clipped = gdf.clip(clip_box)
            clipped = clipped[~clipped.geometry.is_empty]
            clipped_count = len(clipped)

            source_stats[name] = {
                "total": total,
                "intersecting": inside_count,
                "clipped": clipped_count,
                "gdf": clipped,
            }

            pct = (inside_count / total * 100) if total > 0 else 0
            console.print(f"  {name}: {inside_count}/{total} features ({pct:.0f}%) → {clipped_count} after clip")

        except Exception as e:
            console.print(f"  [red]{name}: Error - {e}[/]")

    # Generate preview SVG if requested
    if open_svg or output:
        from pathlib import Path
        from strata.kelley import SVGExporter
        import tempfile

        console.print("\n[bold]Generating preview...[/]")

        # Create exporter
        exporter = SVGExporter(width=11, height=8.5, units="in", margin=0.5)

        # Separate polygon sources from line sources
        # Polygons (towns) get fills, lines (roads) just get strokes
        polygon_colors = ["#81c784", "#64b5f6", "#ffca28", "#ef9a9a", "#ce93d8", "#80cbc4"]
        line_color = "#424242"

        layers_dict = {}
        polygon_idx = 0

        # First pass: add polygon layers (towns)
        for name, stats in source_stats.items():
            if stats["clipped"] > 0:
                gdf = stats["gdf"]
                # Check if this is polygon data (towns) vs line data (roads)
                geom_types = gdf.geometry.geom_type.unique()
                is_polygon = any(t in ["Polygon", "MultiPolygon"] for t in geom_types)

                if is_polygon:
                    color = polygon_colors[polygon_idx % len(polygon_colors)]
                    polygon_idx += 1
                    layers_dict[name] = (gdf, {
                        "stroke": "#37474f",
                        "stroke_width": 0.4,
                        "fill": color,
                    })

        # Second pass: add line layers (roads) on top
        for name, stats in source_stats.items():
            if stats["clipped"] > 0:
                gdf = stats["gdf"]
                geom_types = gdf.geometry.geom_type.unique()
                is_line = any(t in ["LineString", "MultiLineString"] for t in geom_types)

                if is_line:
                    layers_dict[name] = (gdf, {
                        "stroke": line_color,
                        "stroke_width": 0.3,
                        "fill": "none",
                        "vary_fill": False,
                    })

        if not layers_dict:
            console.print("[yellow]No features within bounds to preview.[/]")
            return

        # Determine output path
        if output:
            svg_path = Path(output)
        else:
            svg_path = Path(tempfile.gettempdir()) / "strata_preview.svg"

        exporter.export_multi_layer(layers_dict, svg_path, bounds=tuple(bbox))
        console.print(f"[green]✓[/] Preview saved to: {svg_path}")

        if open_svg:
            import subprocess
            subprocess.run(["open", str(svg_path)])


@main.command()
@click.argument("recipe", type=click.Path(exists=True))
@click.option("--fix", is_flag=True, help="Launch TUI to interactively fix errors")
@click.option("--json", "as_json", is_flag=True, help="Output errors as JSON")
def validate(recipe: str, fix: bool, as_json: bool):
    """Check a recipe for errors without building."""
    # TODO: Implement validation
    if fix:
        from strata.tui.debug import ConfigDebugger

        app = ConfigDebugger(recipe_path=recipe)
        app.run()
    else:
        console.print(f"[bold]Validating:[/] {recipe}")
        console.print("[yellow]Validate command not yet implemented[/]")


@main.group()
def sources():
    """Manage data sources."""
    pass


@sources.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def sources_list(as_json: bool):
    """List all available source types."""
    # TODO: Implement source listing
    console.print("[yellow]Sources list not yet implemented[/]")


@sources.command("search")
@click.argument("query")
@click.option("--state", help="Filter by US state")
@click.option("--type", "source_type", help="Filter by source type")
def sources_search(query: str, state: str | None, source_type: str | None):
    """Search for sources."""
    # TODO: Implement source search
    console.print(f"[bold]Searching for:[/] {query}")
    console.print("[yellow]Sources search not yet implemented[/]")


@sources.command("info")
@click.argument("uri")
def sources_info(uri: str):
    """Get info about a specific source."""
    # TODO: Implement source info
    console.print(f"[bold]Source info:[/] {uri}")
    console.print("[yellow]Sources info not yet implemented[/]")


@main.group()
def cache():
    """Manage local cache."""
    pass


@cache.command("list")
def cache_list():
    """List cached data."""
    # TODO: Implement cache listing
    console.print("[yellow]Cache list not yet implemented[/]")


@cache.command("clear")
@click.argument("source", required=False)
@click.option("--all", "clear_all", is_flag=True, help="Clear all cached data")
def cache_clear(source: str | None, clear_all: bool):
    """Clear cache."""
    # TODO: Implement cache clearing
    console.print("[yellow]Cache clear not yet implemented[/]")


@cache.command("path")
def cache_path():
    """Show cache directory."""
    from platformdirs import user_cache_dir

    path = user_cache_dir("strata", "dirtybirdnj")
    console.print(path)


@main.group()
def config():
    """Manage configuration."""
    pass


@config.command("show")
def config_show():
    """Show current config."""
    # TODO: Implement config display
    console.print("[yellow]Config show not yet implemented[/]")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a config value."""
    # TODO: Implement config setting
    console.print(f"[yellow]Config set not yet implemented: {key}={value}[/]")


@config.command("path")
def config_path():
    """Show config file path."""
    from platformdirs import user_config_dir

    path = user_config_dir("strata", "dirtybirdnj")
    console.print(f"{path}/config.yaml")


if __name__ == "__main__":
    main()
