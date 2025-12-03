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
def preview(recipe: str):
    """Quick preview of a recipe's bounds and layers."""
    # TODO: Implement preview
    console.print(f"[bold]Preview:[/] {recipe}")
    console.print("[yellow]Preview command not yet implemented[/]")


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
