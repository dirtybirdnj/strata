"""
Fetch data from Natural Earth.

Natural Earth is a public domain map dataset available at 1:10m, 1:50m,
and 1:110m scales. It provides essential global base map data including
countries, states/provinces, coastlines, lakes, rivers, and more.

Data licensing: Public Domain (free for any use)
Source: https://www.naturalearthdata.com/
"""

import io
import zipfile
from pathlib import Path

import httpx
from rich.console import Console

from .cache import get_cached_path, is_cached

console = Console()

# Natural Earth base URL
NE_BASE_URL = "https://naciscdn.org/naturalearth"

# Available scales
SCALES = ["10m", "50m", "110m"]

# Layer definitions with URL paths and descriptions
# Format: {category}/{layer}: {description}
LAYERS = {
    # Cultural layers (human-made features)
    "cultural": {
        "admin_0_countries": "Country polygons",
        "admin_0_boundary_lines_land": "Country boundary lines (land only)",
        "admin_0_boundary_lines_disputed_areas": "Disputed boundary lines",
        "admin_1_states_provinces": "First-level admin (states, provinces)",
        "admin_1_states_provinces_lines": "State/province boundary lines",
        "populated_places": "Cities and towns (points)",
        "populated_places_simple": "Simplified cities (points)",
        "roads": "Major roads (10m only)",
        "railroads": "Rail lines (10m only)",
        "airports": "Airport locations (points)",
        "ports": "Port locations (points)",
        "urban_areas": "Urban area polygons",
        "parks_and_protected_lands": "Protected areas (10m only)",
        "time_zones": "Time zone polygons",
    },
    # Physical layers (natural features)
    "physical": {
        "coastline": "Global coastline",
        "land": "Land polygons",
        "ocean": "Ocean polygon",
        "rivers_lake_centerlines": "Major rivers and lake centerlines",
        "rivers_lake_centerlines_scale_rank": "Rivers with scale ranks",
        "lakes": "Major lakes",
        "lakes_historic": "Historic lake extents",
        "glaciated_areas": "Glaciers and ice sheets",
        "antarctic_ice_shelves_polys": "Antarctic ice shelves",
        "bathymetry": "Ocean depth contours (multiple files)",
        "geographic_lines": "Equator, tropics, polar circles",
        "graticules_1": "1-degree graticule",
        "graticules_5": "5-degree graticule",
        "graticules_10": "10-degree graticule",
        "graticules_15": "15-degree graticule",
        "graticules_20": "20-degree graticule",
        "graticules_30": "30-degree graticule",
        "playas": "Dry lake beds",
        "minor_islands": "Small islands",
        "reefs": "Coral reefs",
    },
}

# Size estimates in MB by scale
SIZE_ESTIMATES = {
    "10m": {
        "admin_0_countries": 5.0,
        "admin_1_states_provinces": 15.0,
        "coastline": 8.0,
        "land": 12.0,
        "rivers_lake_centerlines": 3.0,
        "lakes": 2.0,
        "populated_places": 1.5,
        "roads": 20.0,
        "_default": 5.0,
    },
    "50m": {
        "admin_0_countries": 1.5,
        "admin_1_states_provinces": 4.0,
        "coastline": 2.0,
        "land": 3.0,
        "_default": 1.0,
    },
    "110m": {
        "_default": 0.3,
    },
}


def _build_ne_url(scale: str, category: str, layer: str) -> str:
    """
    Build the download URL for a Natural Earth layer.

    Natural Earth URL structure:
    https://naciscdn.org/naturalearth/{scale}/{category}/ne_{scale}_{layer}.zip

    Args:
        scale: Resolution scale (10m, 50m, 110m)
        category: Category (cultural, physical)
        layer: Layer name

    Returns:
        Download URL
    """
    return f"{NE_BASE_URL}/{scale}/{category}/ne_{scale}_{layer}.zip"


def parse_naturalearth_uri(uri: str) -> dict:
    """
    Parse a Natural Earth URI into components.

    Args:
        uri: Natural Earth URI like "naturalearth:10m/cultural/admin_0_countries"

    Returns:
        Dict with scale, category, layer, url, estimated_size_mb

    Supported URI formats:
        naturalearth:{scale}/{category}/{layer}

    Examples:
        naturalearth:10m/cultural/admin_0_countries
        naturalearth:50m/physical/coastline
        naturalearth:110m/cultural/admin_1_states_provinces
    """
    if not uri.startswith("naturalearth:"):
        raise ValueError(f"Not a Natural Earth URI: {uri}")

    path = uri[13:]  # Remove "naturalearth:"
    parts = path.split("/")

    if len(parts) != 3:
        raise ValueError(
            f"Invalid Natural Earth URI format: {uri}\n"
            "Expected: naturalearth:{{scale}}/{{category}}/{{layer}}\n"
            "Example: naturalearth:10m/cultural/admin_0_countries"
        )

    scale, category, layer = parts

    # Validate scale
    if scale not in SCALES:
        raise ValueError(
            f"Invalid scale: {scale}\n"
            f"Valid scales: {', '.join(SCALES)}"
        )

    # Validate category
    if category not in LAYERS:
        raise ValueError(
            f"Invalid category: {category}\n"
            f"Valid categories: {', '.join(LAYERS.keys())}"
        )

    # Validate layer (warning only - Natural Earth has many unlisted layers)
    if layer not in LAYERS[category]:
        console.print(
            f"  [yellow]Note: '{layer}' not in known layers - attempting download anyway[/]"
        )

    url = _build_ne_url(scale, category, layer)

    # Estimate size
    scale_estimates = SIZE_ESTIMATES.get(scale, {})
    size_mb = scale_estimates.get(layer, scale_estimates.get("_default", 2.0))

    return {
        "scale": scale,
        "category": category,
        "layer": layer,
        "url": url,
        "estimated_size_mb": size_mb,
    }


def estimate_naturalearth_size(uri: str) -> dict:
    """
    Estimate download size for a Natural Earth URI without downloading.
    """
    parsed = parse_naturalearth_uri(uri)
    cached = is_cached(uri)
    cache_path = get_cached_path(uri)

    return {
        "uri": uri,
        "estimated_size_mb": parsed["estimated_size_mb"],
        "cached": cached,
        "cache_path": str(cache_path),
        "url": parsed["url"],
    }


def fetch_naturalearth(uri: str, force: bool = False) -> str:
    """
    Fetch Natural Earth data.

    Args:
        uri: Natural Earth URI like "naturalearth:10m/cultural/admin_0_countries"
        force: Re-download even if cached

    Returns:
        Path to the downloaded shapefile (.shp)
    """
    parsed = parse_naturalearth_uri(uri)
    url = parsed["url"]
    layer = parsed["layer"]

    cache_path = get_cached_path(uri)

    # Check cache first
    if not force and is_cached(uri):
        shapefiles = list(cache_path.rglob("*.shp"))
        if shapefiles:
            console.print(f"  [green]✓[/] {uri} [dim](cached)[/]")
            return str(shapefiles[0])

    # Download the archive
    console.print(f"  [cyan]↓[/] Downloading {uri}...")

    cache_path.mkdir(parents=True, exist_ok=True)

    max_retries = 3
    timeout = httpx.Timeout(60.0, connect=30.0, read=120.0)

    for attempt in range(max_retries):
        try:
            with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                response = client.get(url)
                response.raise_for_status()
            break
        except httpx.HTTPError as e:
            if attempt < max_retries - 1:
                import time
                console.print(f"  [yellow]Retry {attempt + 1}...[/]")
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Failed to download {url}: {e}")

    # Extract the archive
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        zf.extractall(cache_path)

    bytes_downloaded = len(response.content)

    # Find the shapefile
    shapefiles = list(cache_path.rglob("*.shp"))
    if not shapefiles:
        raise RuntimeError(f"No shapefile found in downloaded archive: {url}")

    console.print(f"  [green]✓[/] {uri} [dim]({bytes_downloaded / 1024 / 1024:.1f} MB)[/]")

    # Return the most appropriate shapefile (should match layer name)
    for shp in shapefiles:
        if layer in shp.stem:
            return str(shp)

    return str(shapefiles[0])


def list_layers(scale: str = "10m") -> dict:
    """
    List all available layers for a given scale.

    Args:
        scale: Resolution scale (10m, 50m, 110m)

    Returns:
        Dict of {category: {layer: description}}
    """
    if scale not in SCALES:
        raise ValueError(f"Invalid scale: {scale}. Valid: {', '.join(SCALES)}")

    result = {}
    for category, layers in LAYERS.items():
        result[category] = {}
        for layer, description in layers.items():
            # Some layers are scale-specific (noted in description)
            if "(10m only)" in description and scale != "10m":
                continue
            result[category][layer] = description

    return result
