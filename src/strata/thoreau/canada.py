"""
Fetch data from Canadian open data sources.

Supported sources:
- CanVec (Natural Resources Canada) - Hydro, roads, admin boundaries
- NRN (Statistics Canada) - National Road Network

Data licensing: Open Government Licence - Canada
"""

import io
import zipfile
from pathlib import Path

import httpx
from rich.console import Console

from .cache import get_cached_path, is_cached

console = Console()

# CanVec data URLs from Natural Resources Canada
# CanVec is available at different scales: 1M, 250K, 50K
CANVEC_URLS = {
    # CanVec 1:1,000,000 scale - national coverage
    "hydro_1m": "https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/canvec/shp/Hydro/canvec_1M_CA_Hydro_shp.zip",
}

# National Road Network (NRN) URLs by province
NRN_URLS = {
    "qc": "https://geo.statcan.gc.ca/nrn_rrn/qc/nrn_rrn_qc_SHAPE.zip",
    "on": "https://geo.statcan.gc.ca/nrn_rrn/on/nrn_rrn_on_SHAPE.zip",
    "nb": "https://geo.statcan.gc.ca/nrn_rrn/nb/nrn_rrn_nb_SHAPE.zip",
}

# Size estimates in MB
SIZE_ESTIMATES = {
    "canvec:hydro": 150.0,
    "nrn:qc": 200.0,
    "nrn:on": 350.0,
    "nrn:nb": 50.0,
}


def parse_canada_uri(uri: str) -> dict:
    """
    Parse a Canada data URI into components.

    Args:
        uri: Canada URI like "canada:canvec/hydro" or "canada:nrn/qc"

    Returns:
        Dict with source_type, province/layer, url, estimated_size_mb
    """
    if not uri.startswith("canada:"):
        raise ValueError(f"Not a Canada URI: {uri}")

    # Strip scheme
    path = uri[7:]  # Remove "canada:"

    parts = path.split("/")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid Canada URI format: {uri}\n"
            "Expected: canada:canvec/hydro or canada:nrn/{{province}}"
        )

    source_type, layer = parts

    if source_type == "canvec":
        if layer == "hydro":
            url = CANVEC_URLS["hydro_1m"]
            size_mb = SIZE_ESTIMATES.get("canvec:hydro", 150.0)
        else:
            raise ValueError(
                f"Unknown CanVec layer: {layer}\n"
                "Valid layers: hydro"
            )
        return {
            "source_type": "canvec",
            "layer": layer,
            "url": url,
            "estimated_size_mb": size_mb,
        }

    elif source_type == "nrn":
        province = layer.lower()
        if province not in NRN_URLS:
            raise ValueError(
                f"Unknown NRN province: {province}\n"
                f"Valid provinces: {', '.join(NRN_URLS.keys())}"
            )
        url = NRN_URLS[province]
        size_mb = SIZE_ESTIMATES.get(f"nrn:{province}", 100.0)
        return {
            "source_type": "nrn",
            "province": province,
            "url": url,
            "estimated_size_mb": size_mb,
        }

    else:
        raise ValueError(
            f"Unknown Canada source type: {source_type}\n"
            "Valid types: canvec, nrn"
        )


def estimate_canada_size(uri: str) -> dict:
    """
    Estimate download size for a Canada URI without downloading.
    """
    parsed = parse_canada_uri(uri)
    cached = is_cached(uri)
    cache_path = get_cached_path(uri)

    return {
        "uri": uri,
        "estimated_size_mb": parsed["estimated_size_mb"],
        "cached": cached,
        "cache_path": str(cache_path),
        "url": parsed["url"],
    }


def fetch_canada(uri: str, force: bool = False) -> str:
    """
    Fetch Canadian open data.

    Args:
        uri: Canada URI like "canada:canvec/hydro" or "canada:nrn/qc"
        force: Re-download even if cached

    Returns:
        Path to the downloaded shapefile (.shp)
    """
    parsed = parse_canada_uri(uri)
    source_type = parsed["source_type"]
    url = parsed["url"]

    cache_path = get_cached_path(uri)

    # Check cache first
    if not force and is_cached(uri):
        # Find any shapefile
        shapefiles = list(cache_path.rglob("*.shp"))
        if shapefiles:
            console.print(f"  [green]✓[/] {uri} [dim](cached)[/]")
            # For CanVec hydro, return waterbody file
            if source_type == "canvec":
                for shp in shapefiles:
                    if "waterbody" in shp.stem.lower():
                        return str(shp)
            # For NRN, return road segment file
            elif source_type == "nrn":
                for shp in shapefiles:
                    if "roadseg" in shp.stem.lower():
                        return str(shp)
            return str(shapefiles[0])

    # Download the archive
    console.print(f"  [cyan]↓[/] Downloading {uri}...")
    console.print(f"      (this is a large file, please wait)")

    cache_path.mkdir(parents=True, exist_ok=True)

    max_retries = 3
    timeout = httpx.Timeout(60.0, connect=30.0, read=600.0)  # Long timeout for large files

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

    # Find the appropriate shapefile
    shapefiles = list(cache_path.rglob("*.shp"))
    if not shapefiles:
        raise RuntimeError(f"No shapefile found in downloaded archive: {url}")

    console.print(f"  [green]✓[/] {uri} [dim]({bytes_downloaded / 1024 / 1024:.1f} MB)[/]")

    # Return the most appropriate shapefile
    if source_type == "canvec":
        for shp in shapefiles:
            if "waterbody" in shp.stem.lower():
                return str(shp)
    elif source_type == "nrn":
        for shp in shapefiles:
            if "roadseg" in shp.stem.lower():
                return str(shp)

    return str(shapefiles[0])
