"""
Fetch USGS Land Cover Woodland vector data.

This provides woodland polygon data derived from topographic maps,
available as state-level shapefiles from the USGS National Map.

Data source: https://www.sciencebase.gov/catalog/item/5318a64ee4b051b1b924ea2c
Download: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/LndCvr/Shape/

Data licensing: Public Domain (U.S. Government Work)
"""

import zipfile
from pathlib import Path
from io import BytesIO

import httpx
from rich.console import Console

from .cache import get_cache_dir, is_cached, get_cached_path

console = Console()

# Base URL for USGS Land Cover shapefiles
BASE_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/LndCvr/Shape"

# State name mappings (for URL construction)
STATE_NAMES = {
    "al": "Alabama", "ak": "Alaska", "az": "Arizona", "ar": "Arkansas",
    "ca": "California", "co": "Colorado", "ct": "Connecticut", "de": "Delaware",
    "fl": "Florida", "ga": "Georgia", "hi": "Hawaii", "id": "Idaho",
    "il": "Illinois", "in": "Indiana", "ia": "Iowa", "ks": "Kansas",
    "ky": "Kentucky", "la": "Louisiana", "me": "Maine", "md": "Maryland",
    "ma": "Massachusetts", "mi": "Michigan", "mn": "Minnesota", "ms": "Mississippi",
    "mo": "Missouri", "mt": "Montana", "ne": "Nebraska", "nv": "Nevada",
    "nh": "New_Hampshire", "nj": "New_Jersey", "nm": "New_Mexico", "ny": "New_York",
    "nc": "North_Carolina", "nd": "North_Dakota", "oh": "Ohio", "ok": "Oklahoma",
    "or": "Oregon", "pa": "Pennsylvania", "ri": "Rhode_Island", "sc": "South_Carolina",
    "sd": "South_Dakota", "tn": "Tennessee", "tx": "Texas", "ut": "Utah",
    "vt": "Vermont", "va": "Virginia", "wa": "Washington", "wv": "West_Virginia",
    "wi": "Wisconsin", "wy": "Wyoming", "dc": "District_of_Columbia",
    "pr": "Puerto_Rico",
}

# Approximate file sizes in MB (compressed)
SIZE_ESTIMATES = {
    "vt": 216,
    "nh": 180,
    "me": 548,
    "ny": 1500,
    "ma": 227,
    "_default": 500,
}


def parse_woodland_uri(uri: str) -> dict:
    """
    Parse a woodland URI into components.

    Format: woodland:{state}
    Example: woodland:vt

    Returns:
        Dict with 'state' key
    """
    if not uri.startswith("woodland:"):
        raise ValueError(f"Invalid woodland URI: {uri}")

    state = uri[9:].lower()  # Remove "woodland:" prefix

    if state not in STATE_NAMES:
        raise ValueError(f"Unknown state code: {state}")

    return {"state": state}


def fetch_woodland(uri: str, force: bool = False) -> str:
    """
    Fetch USGS woodland data for a state.

    Args:
        uri: Source URI (e.g., "woodland:vt")
        force: Re-download even if cached

    Returns:
        Path to shapefile
    """
    parsed = parse_woodland_uri(uri)
    state = parsed["state"]
    state_name = STATE_NAMES[state]

    # Check cache
    cache_dir = get_cache_dir() / "woodland" / state
    shapefile_path = cache_dir / "LandCover_Woodland.shp"

    if shapefile_path.exists() and not force:
        console.print(f"  [green]✓[/] {uri} [dim](cached)[/]")
        return str(shapefile_path)

    # Build URL
    filename = f"LNDCVR_{state_name}_State_Shape.zip"
    url = f"{BASE_URL}/{filename}"

    console.print(f"  [yellow]↓[/] Fetching {uri}...")
    console.print(f"    [dim]URL: {url}[/]")

    # Download
    try:
        with httpx.Client(timeout=600.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()

            # Create cache directory
            cache_dir.mkdir(parents=True, exist_ok=True)

            # Extract shapefile from zip
            with zipfile.ZipFile(BytesIO(response.content)) as zf:
                # Find and extract the shapefile components
                for name in zf.namelist():
                    if "LandCover_Woodland" in name:
                        # Extract to cache directory, flattening the path
                        filename = Path(name).name
                        target_path = cache_dir / filename
                        with zf.open(name) as src, open(target_path, "wb") as dst:
                            dst.write(src.read())

            size_mb = len(response.content) / 1024 / 1024
            console.print(f"  [green]✓[/] {uri} ({size_mb:.1f} MB)")

            return str(shapefile_path)

    except httpx.HTTPError as e:
        console.print(f"  [red]✗[/] Failed to fetch {uri}: {e}")
        raise


def estimate_woodland_size(uri: str) -> dict:
    """
    Estimate download size for a woodland URI.

    Args:
        uri: Source URI (e.g., "woodland:vt")

    Returns:
        Dict with estimated_size_mb, cached, cache_path
    """
    parsed = parse_woodland_uri(uri)
    state = parsed["state"]

    cache_dir = get_cache_dir() / "woodland" / state
    shapefile_path = cache_dir / "LandCover_Woodland.shp"

    size_mb = SIZE_ESTIMATES.get(state, SIZE_ESTIMATES["_default"])

    return {
        "uri": uri,
        "estimated_size_mb": size_mb,
        "cached": shapefile_path.exists(),
        "cache_path": str(shapefile_path),
    }
