"""
Fetch data from Mexico INEGI (Instituto Nacional de Estadistica y Geografia).

INEGI provides authoritative geographic data for Mexico including:
- Marco Geoestadistico Nacional (MGN) - Administrative boundaries
- Red Nacional de Caminos (RNC) - National road network
- Hydrography - Rivers, lakes, watersheds

Data licensing: INEGI Open Data (free for use with attribution)
Source: https://www.inegi.org.mx/app/descarga/default.html
"""

import io
import zipfile
from pathlib import Path

import httpx
from rich.console import Console

from .cache import get_cached_path, is_cached

console = Console()

# INEGI download URLs
# MGN (Marco Geoestadistico Nacional) - Administrative boundaries
# URL structure varies by year and level
INEGI_URLS = {
    # Marco Geoestadistico 2023 (latest)
    # These are the direct download links for shapefiles
    "mgn_state": "https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/marcogeo/889463849568/mg_2023_integrado.zip",

    # geoBoundaries - Reliable source derived from INEGI data
    # These are more reliably accessible than direct HDX URLs
    # Source: https://www.geoboundaries.org/
    "hdx_admin0": "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/MEX/ADM0/geoBoundaries-MEX-ADM0-all.zip",
    "hdx_admin1": "https://github.com/wmgeolab/geoBoundaries/raw/90a1d52/releaseData/gbOpen/MEX/ADM1/geoBoundaries-MEX-ADM1-all.zip",
    "hdx_admin2": "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/MEX/ADM2/geoBoundaries-MEX-ADM2-all.zip",
}

# Mexico state codes (similar to US FIPS)
# Using standard 2-letter abbreviations
MEXICO_STATES = {
    "ags": {"code": "01", "name": "Aguascalientes"},
    "bc": {"code": "02", "name": "Baja California"},
    "bcs": {"code": "03", "name": "Baja California Sur"},
    "cam": {"code": "04", "name": "Campeche"},
    "chis": {"code": "07", "name": "Chiapas"},
    "chih": {"code": "08", "name": "Chihuahua"},
    "cdmx": {"code": "09", "name": "Ciudad de Mexico"},
    "coah": {"code": "05", "name": "Coahuila"},
    "col": {"code": "06", "name": "Colima"},
    "dgo": {"code": "10", "name": "Durango"},
    "gto": {"code": "11", "name": "Guanajuato"},
    "gro": {"code": "12", "name": "Guerrero"},
    "hgo": {"code": "13", "name": "Hidalgo"},
    "jal": {"code": "14", "name": "Jalisco"},
    "mex": {"code": "15", "name": "Mexico"},
    "mich": {"code": "16", "name": "Michoacan"},
    "mor": {"code": "17", "name": "Morelos"},
    "nay": {"code": "18", "name": "Nayarit"},
    "nl": {"code": "19", "name": "Nuevo Leon"},
    "oax": {"code": "20", "name": "Oaxaca"},
    "pue": {"code": "21", "name": "Puebla"},
    "qro": {"code": "22", "name": "Queretaro"},
    "qroo": {"code": "23", "name": "Quintana Roo"},
    "slp": {"code": "24", "name": "San Luis Potosi"},
    "sin": {"code": "25", "name": "Sinaloa"},
    "son": {"code": "26", "name": "Sonora"},
    "tab": {"code": "27", "name": "Tabasco"},
    "tamps": {"code": "28", "name": "Tamaulipas"},
    "tlax": {"code": "29", "name": "Tlaxcala"},
    "ver": {"code": "30", "name": "Veracruz"},
    "yuc": {"code": "31", "name": "Yucatan"},
    "zac": {"code": "32", "name": "Zacatecas"},
}

# Size estimates in MB
SIZE_ESTIMATES = {
    "mgn:state": 15.0,
    "mgn:municipality": 45.0,
    "mgn:national": 120.0,
    "hdx:admin0": 2.0,
    "hdx:admin1": 8.0,
    "hdx:admin2": 25.0,
}


def parse_mexico_uri(uri: str) -> dict:
    """
    Parse a Mexico data URI into components.

    Args:
        uri: Mexico URI like "mexico:mgn/state" or "mexico:hdx/admin1"

    Returns:
        Dict with source_type, layer, url, estimated_size_mb

    Supported URIs:
        mexico:mgn/state       - All 32 states (HDX source, cleaner)
        mexico:mgn/municipality - All municipalities
        mexico:hdx/admin0      - Country outline
        mexico:hdx/admin1      - States
        mexico:hdx/admin2      - Municipalities
    """
    if not uri.startswith("mexico:"):
        raise ValueError(f"Not a Mexico URI: {uri}")

    path = uri[7:]  # Remove "mexico:"
    parts = path.split("/")

    if len(parts) < 2:
        raise ValueError(
            f"Invalid Mexico URI format: {uri}\n"
            "Expected: mexico:mgn/{{level}} or mexico:hdx/{{level}}"
        )

    source_type = parts[0].lower()
    layer = parts[1].lower()

    if source_type == "mgn":
        # Marco Geoestadistico Nacional
        if layer == "state":
            # Use HDX for cleaner state-level data
            url = INEGI_URLS["hdx_admin1"]
            size_mb = SIZE_ESTIMATES.get("hdx:admin1", 8.0)
        elif layer == "municipality":
            url = INEGI_URLS["hdx_admin2"]
            size_mb = SIZE_ESTIMATES.get("hdx:admin2", 25.0)
        elif layer == "national":
            url = INEGI_URLS["mgn_state"]
            size_mb = SIZE_ESTIMATES.get("mgn:national", 120.0)
        else:
            raise ValueError(
                f"Unknown MGN layer: {layer}\n"
                "Valid layers: state, municipality, national"
            )
        return {
            "source_type": "mgn",
            "layer": layer,
            "url": url,
            "estimated_size_mb": size_mb,
        }

    elif source_type == "hdx":
        # Humanitarian Data Exchange (cleaner INEGI derivatives)
        if layer == "admin0":
            url = INEGI_URLS["hdx_admin0"]
            size_mb = SIZE_ESTIMATES.get("hdx:admin0", 2.0)
        elif layer == "admin1":
            url = INEGI_URLS["hdx_admin1"]
            size_mb = SIZE_ESTIMATES.get("hdx:admin1", 8.0)
        elif layer == "admin2":
            url = INEGI_URLS["hdx_admin2"]
            size_mb = SIZE_ESTIMATES.get("hdx:admin2", 25.0)
        else:
            raise ValueError(
                f"Unknown HDX layer: {layer}\n"
                "Valid layers: admin0, admin1, admin2"
            )
        return {
            "source_type": "hdx",
            "layer": layer,
            "url": url,
            "estimated_size_mb": size_mb,
        }

    else:
        raise ValueError(
            f"Unknown Mexico source type: {source_type}\n"
            "Valid types: mgn, hdx"
        )


def estimate_mexico_size(uri: str) -> dict:
    """
    Estimate download size for a Mexico URI without downloading.
    """
    parsed = parse_mexico_uri(uri)
    cached = is_cached(uri)
    cache_path = get_cached_path(uri)

    return {
        "uri": uri,
        "estimated_size_mb": parsed["estimated_size_mb"],
        "cached": cached,
        "cache_path": str(cache_path),
        "url": parsed["url"],
    }


def fetch_mexico(uri: str, force: bool = False) -> str:
    """
    Fetch Mexico INEGI/HDX data.

    Args:
        uri: Mexico URI like "mexico:mgn/state" or "mexico:hdx/admin1"
        force: Re-download even if cached

    Returns:
        Path to the downloaded shapefile (.shp)
    """
    parsed = parse_mexico_uri(uri)
    url = parsed["url"]

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
    timeout = httpx.Timeout(60.0, connect=30.0, read=300.0)

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

    return str(shapefiles[0])
