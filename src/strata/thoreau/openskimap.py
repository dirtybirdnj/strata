"""
Fetch data from OpenSkiMap.

OpenSkiMap provides worldwide ski area data including:
- Ski runs (downhill trails)
- Ski lifts (chairlifts, gondolas, etc.)
- Ski areas (resort boundaries)

Data source: https://openskimap.org
GeoPackage: https://tiles.openskimap.org/openskidata.gpkg

Data is derived from OpenStreetMap and released under ODbL.

NOTE: OpenSkiMap only allows downloading the GeoPackage once per day.
The file is stored in the repo's data/ directory (gitignored) to avoid
re-downloading.
"""

from pathlib import Path

import httpx
from rich.console import Console

console = Console()

# OpenSkiMap GeoPackage URL
OPENSKIMAP_URL = "https://tiles.openskimap.org/openskidata.gpkg"

# Layers available in the GeoPackage
# Actual layer names discovered from the GeoPackage:
# - ski_areas_point, ski_areas_multipolygon
# - lifts_linestring
# - runs_multipolygon, runs_linestring
LAYERS = {
    "runs": "runs_linestring",           # Ski runs/trails (LineString)
    "lifts": "lifts_linestring",         # Ski lifts (LineString)
    "areas": "ski_areas_multipolygon",   # Ski area boundaries (Polygon)
}

# Estimated size (the GeoPackage is ~200MB)
ESTIMATED_SIZE_MB = 200.0


def _get_data_dir() -> Path:
    """Get the local data directory in the repo for large files."""
    # Walk up from this file to find the repo root (where pyproject.toml is)
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            data_dir = parent / "data"
            data_dir.mkdir(exist_ok=True)
            return data_dir
    # Fallback to cwd/data if we can't find repo root
    data_dir = Path.cwd() / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def _get_gpkg_path() -> Path:
    """Get the path to the OpenSkiMap GeoPackage file."""
    return _get_data_dir() / "openskidata.gpkg"


def parse_openskimap_uri(uri: str) -> dict:
    """
    Parse an OpenSkiMap data URI into components.

    Args:
        uri: OpenSkiMap URI like "openskimap:runs" or "openskimap:lifts"

    Returns:
        Dict with layer, gpkg_layer, url, estimated_size_mb
    """
    if not uri.startswith("openskimap:"):
        raise ValueError(f"Not an OpenSkiMap URI: {uri}")

    # Strip scheme
    layer = uri[11:]  # Remove "openskimap:"

    if layer not in LAYERS:
        raise ValueError(
            f"Unknown OpenSkiMap layer: {layer}\n"
            f"Valid layers: {', '.join(LAYERS.keys())}"
        )

    return {
        "layer": layer,
        "gpkg_layer": LAYERS[layer],
        "url": OPENSKIMAP_URL,
        "estimated_size_mb": ESTIMATED_SIZE_MB,
    }


def estimate_openskimap_size(uri: str) -> dict:
    """
    Estimate download size for an OpenSkiMap URI without downloading.
    """
    parsed = parse_openskimap_uri(uri)
    gpkg_path = _get_gpkg_path()
    cached = gpkg_path.exists()

    return {
        "uri": uri,
        "estimated_size_mb": parsed["estimated_size_mb"],
        "cached": cached,
        "cache_path": str(gpkg_path),
        "url": parsed["url"],
    }


def fetch_openskimap(uri: str, force: bool = False) -> str:
    """
    Fetch OpenSkiMap data.

    Args:
        uri: OpenSkiMap URI like "openskimap:runs", "openskimap:lifts", "openskimap:areas"
        force: Re-download even if cached

    Returns:
        Path to the GeoPackage file with layer name appended (path:layer_name)
        This format is understood by fiona/geopandas for reading specific layers.

    NOTE: OpenSkiMap only allows one download per day. The file is stored in
    the repo's data/ directory to avoid re-downloading.
    """
    parsed = parse_openskimap_uri(uri)
    gpkg_layer = parsed["gpkg_layer"]
    url = parsed["url"]

    # Store in repo's data/ directory (not the cache)
    gpkg_path = _get_gpkg_path()

    # Check if file exists locally
    if not force and gpkg_path.exists():
        console.print(f"  [green]✓[/] {uri} [dim](local: {gpkg_path})[/]")
        # Return path with layer specification for geopandas
        return f"{gpkg_path}:{gpkg_layer}"

    # Download the GeoPackage
    console.print(f"  [cyan]↓[/] Downloading OpenSkiMap data (~200MB)...")
    console.print(f"      [yellow]WARNING: OpenSkiMap only allows 1 download per day![/]")
    console.print(f"      Saving to: {gpkg_path}")

    max_retries = 3
    timeout = httpx.Timeout(60.0, connect=30.0, read=600.0)  # Long timeout for large file

    for attempt in range(max_retries):
        try:
            with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                # Stream the download to avoid memory issues with large file
                with client.stream("GET", url) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get("content-length", 0))

                    with open(gpkg_path, "wb") as f:
                        downloaded = 0
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                pct = (downloaded / total_size) * 100
                                console.print(
                                    f"\r      Downloaded {downloaded / 1024 / 1024:.1f} MB "
                                    f"({pct:.0f}%)",
                                    end="",
                                )
                    console.print()  # Newline after progress
            break
        except httpx.HTTPError as e:
            if attempt < max_retries - 1:
                import time
                console.print(f"  [yellow]Retry {attempt + 1}...[/]")
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Failed to download {url}: {e}")

    console.print(f"  [green]✓[/] {uri} [dim]({gpkg_path.stat().st_size / 1024 / 1024:.1f} MB)[/]")

    # Return path with layer specification
    return f"{gpkg_path}:{gpkg_layer}"
