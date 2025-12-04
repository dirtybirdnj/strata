"""
Fetch data from Canadian open data sources.

Supported sources:
- CanVec (Natural Resources Canada) - Hydro, roads, admin boundaries
- NRN (Statistics Canada) - National Road Network
- NHN (Natural Resources Canada) - National Hydro Network by workunit

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

# NHN (National Hydro Network) URL pattern
# Workunits are geographic areas, e.g. 02OJ000 = Richelieu River watershed
# URL structure: /shp_en/{region}/nhn_rhn_{workunit}_shp_en.zip
# Region is first 2 digits of workunit, workunit is lowercase in filename
NHN_URL_TEMPLATE = "https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/geobase_nhn_rhn/shp_en/{region}/nhn_rhn_{workunit_lower}_shp_en.zip"

# Known NHN workunits with descriptive names
NHN_WORKUNITS = {
    "02OJ000": "Richelieu River watershed (Lake Champlain to St. Lawrence)",
    "02OHA00": "Lake Champlain (Quebec portion, western)",
    "02OHB00": "Lake Champlain (Quebec portion, eastern - includes Missisquoi Bay)",
    "02OG000": "Yamaska River watershed",
    "02OA000": "St. Lawrence River (Montreal area)",
    "02OB000": "Ottawa River (lower)",
    "02OC000": "Ottawa River (middle)",
    "02OE000": "St-François River",
}

# National Road Network (NRN) URLs by province
# Statistics Canada NRN: https://www150.statcan.gc.ca/n1/pub/92-500-g/92-500-g2019001-eng.htm
NRN_URLS = {
    # Eastern provinces
    "nl": "https://geo.statcan.gc.ca/nrn_rrn/nl/nrn_rrn_nl_SHAPE.zip",  # Newfoundland & Labrador
    "pe": "https://geo.statcan.gc.ca/nrn_rrn/pe/nrn_rrn_pe_SHAPE.zip",  # Prince Edward Island
    "ns": "https://geo.statcan.gc.ca/nrn_rrn/ns/nrn_rrn_ns_SHAPE.zip",  # Nova Scotia
    "nb": "https://geo.statcan.gc.ca/nrn_rrn/nb/nrn_rrn_nb_SHAPE.zip",  # New Brunswick
    "qc": "https://geo.statcan.gc.ca/nrn_rrn/qc/nrn_rrn_qc_SHAPE.zip",  # Quebec
    "on": "https://geo.statcan.gc.ca/nrn_rrn/on/nrn_rrn_on_SHAPE.zip",  # Ontario
    # Western provinces
    "mb": "https://geo.statcan.gc.ca/nrn_rrn/mb/nrn_rrn_mb_SHAPE.zip",  # Manitoba
    "sk": "https://geo.statcan.gc.ca/nrn_rrn/sk/nrn_rrn_sk_SHAPE.zip",  # Saskatchewan
    "ab": "https://geo.statcan.gc.ca/nrn_rrn/ab/nrn_rrn_ab_SHAPE.zip",  # Alberta
    "bc": "https://geo.statcan.gc.ca/nrn_rrn/bc/nrn_rrn_bc_SHAPE.zip",  # British Columbia
    # Territories
    "yt": "https://geo.statcan.gc.ca/nrn_rrn/yt/nrn_rrn_yt_SHAPE.zip",  # Yukon
    "nt": "https://geo.statcan.gc.ca/nrn_rrn/nt/nrn_rrn_nt_SHAPE.zip",  # Northwest Territories
    "nu": "https://geo.statcan.gc.ca/nrn_rrn/nu/nrn_rrn_nu_SHAPE.zip",  # Nunavut
}

# Province/territory names
PROVINCE_NAMES = {
    "nl": "Newfoundland and Labrador",
    "pe": "Prince Edward Island",
    "ns": "Nova Scotia",
    "nb": "New Brunswick",
    "qc": "Quebec",
    "on": "Ontario",
    "mb": "Manitoba",
    "sk": "Saskatchewan",
    "ab": "Alberta",
    "bc": "British Columbia",
    "yt": "Yukon",
    "nt": "Northwest Territories",
    "nu": "Nunavut",
}

# Size estimates in MB
SIZE_ESTIMATES = {
    "canvec:hydro": 150.0,
    "nrn:nl": 25.0,
    "nrn:pe": 5.0,
    "nrn:ns": 35.0,
    "nrn:nb": 50.0,
    "nrn:qc": 200.0,
    "nrn:on": 350.0,
    "nrn:mb": 80.0,
    "nrn:sk": 100.0,
    "nrn:ab": 150.0,
    "nrn:bc": 200.0,
    "nrn:yt": 10.0,
    "nrn:nt": 15.0,
    "nrn:nu": 5.0,
    # NHN workunits
    "nhn:02OJ000": 8.5,  # Richelieu
    "nhn:02OHA00": 5.0,  # Lake Champlain west
    "nhn:02OHB00": 6.0,  # Lake Champlain east (Missisquoi Bay)
    "nhn:02OG000": 8.0,  # Yamaska
    "nhn:02OA000": 10.0,
    "nhn:02OB000": 10.0,
    "nhn:02OC000": 10.0,
    "nhn:02OE000": 8.0,
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
    if len(parts) < 2:
        raise ValueError(
            f"Invalid Canada URI format: {uri}\n"
            "Expected: canada:canvec/hydro, canada:nrn/{{province}}, or canada:nhn/{{workunit}}[/rivers]"
        )

    source_type = parts[0]
    layer = parts[1]
    sublayer = parts[2] if len(parts) > 2 else None

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

    elif source_type == "nhn":
        workunit = layer.upper()  # Workunits are uppercase like 02OJ000
        region = workunit[:2]  # First 2 digits (e.g., "02")
        workunit_lower = workunit.lower()  # Filename uses lowercase
        url = NHN_URL_TEMPLATE.format(region=region, workunit_lower=workunit_lower)
        size_mb = SIZE_ESTIMATES.get(f"nhn:{workunit}", 10.0)
        description = NHN_WORKUNITS.get(workunit, f"NHN workunit {workunit}")
        # sublayer can be "rivers" to get linear water instead of waterbodies
        nhn_layer = sublayer if sublayer in ("rivers", "waterbody") else "waterbody"
        return {
            "source_type": "nhn",
            "workunit": workunit,
            "nhn_layer": nhn_layer,
            "url": url,
            "estimated_size_mb": size_mb,
            "description": description,
        }

    else:
        raise ValueError(
            f"Unknown Canada source type: {source_type}\n"
            "Valid types: canvec, nrn, nhn"
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
            # For NHN, return waterbody or slwater based on nhn_layer
            elif source_type == "nhn":
                nhn_layer = parsed.get("nhn_layer", "waterbody")
                target = "slwater" if nhn_layer == "rivers" else "waterbody"
                for shp in shapefiles:
                    if target in shp.stem.lower():
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
    elif source_type == "nhn":
        # NHN has WATERBODY_2 (polygons) and SLWATER_1 (lines)
        nhn_layer = parsed.get("nhn_layer", "waterbody")
        target = "slwater" if nhn_layer == "rivers" else "waterbody"
        for shp in shapefiles:
            if target in shp.stem.lower():
                return str(shp)

    return str(shapefiles[0])
