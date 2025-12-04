"""
Fetch data from Quebec Données ouvertes (Open Data).

Quebec administrative boundaries from MERN (Ministère de l'Énergie et
des Ressources naturelles du Québec).

Data source: https://www.donneesquebec.ca/recherche/dataset/decoupages-administratifs
License: CC-BY 4.0
"""

import io
import zipfile
from pathlib import Path

import httpx
from rich.console import Console

from .cache import get_cached_path, is_cached

console = Console()

# Quebec data URLs from MERN
QUEBEC_URLS = {
    # Administrative boundaries at 1/20,000 scale (88 MB)
    "sda_20k": "https://diffusion.mern.gouv.qc.ca/Diffusion/RGQ/Vectoriel/Theme/Local/SDA_20k/SHP/SHP.zip",
    # Administrative boundaries at 1/100,000 scale (47 MB) - faster downloads
    "sda_100k": "https://diffusion.mern.gouv.qc.ca/diffusion/RGQ/Vectoriel/Theme/Regional/SDA_100k/SHP/BDAT(adm)_SHP.zip",
}

# Size estimates in MB
QUEBEC_SIZE_ESTIMATES = {
    "sda_20k": 88.0,
    "sda_100k": 47.0,
    "municipalities": 47.0,  # Alias for sda_100k
    "mrc": 10.0,  # MRC boundaries only (subset)
}

# Layer name mappings within the Quebec SDA shapefile archives
# The sda_100k archive contains: munic_s, mrc_s, regio_s, comet_s (and _l line versions)
QUEBEC_LAYERS = {
    # sda_100k layers (from BDAT(adm)_SHP.zip)
    "municipalities": "munic_s",  # Municipal boundaries (surface)
    "mrc": "mrc_s",  # Regional county municipalities (MRC)
    "regions": "regio_s",  # Administrative regions
    "metropolitan": "comet_s",  # Metropolitan communities
}


def parse_quebec_uri(uri: str) -> dict:
    """
    Parse a Quebec data URI into components.

    Args:
        uri: Quebec URI like "quebec:municipalities" or "quebec:mrc"

    Returns:
        Dict with layer, url, estimated_size_mb
    """
    if not uri.startswith("quebec:"):
        raise ValueError(f"Not a Quebec URI: {uri}")

    # Strip scheme
    path = uri[7:]  # Remove "quebec:"

    # Handle simple layer names
    layer = path.lower()

    # Map layer names to data source
    if layer in ("municipalities", "mrc", "regions", "metropolitan"):
        source = "sda_100k"
        shapefile_prefix = QUEBEC_LAYERS.get(layer, "munic_s")
    elif layer in ("sda_20k", "sda_100k"):
        source = layer
        shapefile_prefix = "munic_s"  # Default to municipalities
    else:
        raise ValueError(
            f"Unknown Quebec layer: {layer}\n"
            f"Valid layers: {', '.join(QUEBEC_LAYERS.keys())}"
        )

    url = QUEBEC_URLS[source]
    size_mb = QUEBEC_SIZE_ESTIMATES.get(layer, 50.0)

    return {
        "layer": layer,
        "source": source,
        "shapefile_prefix": shapefile_prefix,
        "url": url,
        "estimated_size_mb": size_mb,
    }


def estimate_quebec_size(uri: str) -> dict:
    """
    Estimate download size for a Quebec URI without downloading.

    Args:
        uri: Quebec URI like "quebec:municipalities"

    Returns:
        Dict with estimated_size_mb, cached, cache_path
    """
    parsed = parse_quebec_uri(uri)
    cached = is_cached(uri)
    cache_path = get_cached_path(uri)

    return {
        "uri": uri,
        "estimated_size_mb": parsed["estimated_size_mb"],
        "cached": cached,
        "cache_path": str(cache_path),
        "url": parsed["url"],
    }


def fetch_quebec(uri: str, force: bool = False) -> str:
    """
    Fetch Quebec administrative boundary data.

    Args:
        uri: Quebec URI like "quebec:municipalities" or "quebec:mrc"
        force: Re-download even if cached

    Returns:
        Path to the downloaded shapefile (.shp)
    """
    parsed = parse_quebec_uri(uri)
    layer = parsed["layer"]
    source = parsed["source"]
    shapefile_prefix = parsed["shapefile_prefix"]
    url = parsed["url"]

    # Use source (sda_100k or sda_20k) as cache key
    cache_uri = f"quebec:{source}"
    cache_path = get_cached_path(cache_uri)

    # Check cache first
    if not force and is_cached(cache_uri):
        # Find the requested layer shapefile
        shapefiles = list(cache_path.rglob(f"{shapefile_prefix}*.shp"))
        if shapefiles:
            console.print(f"  [green]✓[/] {uri} [dim](cached)[/]")
            return str(shapefiles[0])

    # Download the archive
    console.print(f"  [cyan]↓[/] Downloading {uri}...")

    cache_path.mkdir(parents=True, exist_ok=True)

    max_retries = 3
    timeout = httpx.Timeout(30.0, connect=10.0, read=300.0)  # Longer read timeout for large files

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

    # Find the requested layer shapefile
    shapefiles = list(cache_path.rglob(f"{shapefile_prefix}*.shp"))
    if not shapefiles:
        # Try any shapefile
        shapefiles = list(cache_path.rglob("*.shp"))

    if not shapefiles:
        raise RuntimeError(f"No shapefile found in downloaded archive: {url}")

    console.print(f"  [green]✓[/] {uri} [dim]({bytes_downloaded / 1024 / 1024:.1f} MB)[/]")

    # Return the matching shapefile
    for shp in shapefiles:
        if shapefile_prefix in shp.stem:
            return str(shp)

    # Return first shapefile if no match
    return str(shapefiles[0])
