"""
Fetch data from US Census TIGER/Line.

TIGER URL structure:
https://www2.census.gov/geo/tiger/TIGER{year}/{type}/tl_{year}_{fips}_{type}.zip

State FIPS codes: VT=50, NY=36, NH=33, MA=25, ME=23
"""

import io
import zipfile
from pathlib import Path

import httpx
from rich.console import Console

from .cache import get_cached_path, is_cached

console = Console()

# Approximate file sizes in MB for common TIGER datasets (2023)
# These are estimates to help users understand download scale
TIGER_SIZE_ESTIMATES = {
    # Format: (state, type): size_mb
    # Small states
    ("vt", "cousub"): 2.5,
    ("vt", "areawater"): 3.2,
    ("vt", "linearwater"): 4.1,
    ("vt", "prisecroads"): 1.8,
    ("nh", "cousub"): 2.0,
    ("nh", "areawater"): 2.8,
    ("me", "cousub"): 3.5,
    ("me", "areawater"): 8.5,
    # Medium states
    ("ny", "cousub"): 18.0,
    ("ny", "areawater"): 25.0,
    ("ny", "linearwater"): 35.0,
    ("ma", "cousub"): 4.5,
    ("ma", "areawater"): 5.2,
    # Default estimate per type
    "_default_cousub": 5.0,
    "_default_areawater": 8.0,
    "_default_linearwater": 10.0,
    "_default_prisecroads": 5.0,
    "_default_county": 0.5,
    "_default_state": 2.0,
    "_default_place": 3.0,
    "_default_tract": 5.0,
}

# State FIPS codes
STATE_FIPS = {
    "al": "01", "ak": "02", "az": "04", "ar": "05", "ca": "06",
    "co": "08", "ct": "09", "de": "10", "fl": "12", "ga": "13",
    "hi": "15", "id": "16", "il": "17", "in": "18", "ia": "19",
    "ks": "20", "ky": "21", "la": "22", "me": "23", "md": "24",
    "ma": "25", "mi": "26", "mn": "27", "ms": "28", "mo": "29",
    "mt": "30", "ne": "31", "nv": "32", "nh": "33", "nj": "34",
    "nm": "35", "ny": "36", "nc": "37", "nd": "38", "oh": "39",
    "ok": "40", "or": "41", "pa": "42", "ri": "44", "sc": "45",
    "sd": "46", "tn": "47", "tx": "48", "ut": "49", "vt": "50",
    "va": "51", "wa": "53", "wv": "54", "wi": "55", "wy": "56",
    "dc": "11", "pr": "72",
}

# TIGER layer types and their URL patterns
# Some types are per-state (2-digit FIPS), others per-county (5-digit FIPS)
# National types use "us" instead of state FIPS and are filtered client-side
TIGER_TYPES = {
    "cousub": {"folder": "COUSUB", "per_county": False, "national": False},
    "areawater": {"folder": "AREAWATER", "per_county": True, "national": False},
    "linearwater": {"folder": "LINEARWATER", "per_county": True, "national": False},
    "prisecroads": {"folder": "PRISECROADS", "per_county": False, "national": False},
    "county": {"folder": "COUNTY", "per_county": False, "national": True},  # US-wide file
    "state": {"folder": "STATE", "per_county": False, "national": True},  # US-wide file
    "place": {"folder": "PLACE", "per_county": False, "national": False},
    "tract": {"folder": "TRACT", "per_county": True, "national": False},
}

# County FIPS codes by state (we'll fetch the list dynamically or use known ones)
# Vermont counties (FIPS 50)
VT_COUNTIES = [
    "001",  # Addison
    "003",  # Bennington
    "005",  # Caledonia
    "007",  # Chittenden
    "009",  # Essex
    "011",  # Franklin
    "013",  # Grand Isle
    "015",  # Lamoille
    "017",  # Orange
    "019",  # Orleans
    "021",  # Rutland
    "023",  # Washington
    "025",  # Windham
    "027",  # Windsor
]

# NY counties bordering Lake Champlain
NY_CHAMPLAIN_COUNTIES = [
    "019",  # Clinton
    "031",  # Essex
    "033",  # Franklin
    "113",  # Warren
    "115",  # Washington
]

# NY counties in western NY (Niagara region)
NY_NIAGARA_COUNTIES = [
    "029",  # Erie (Buffalo)
    "063",  # Niagara
    "073",  # Orleans
    "037",  # Genesee
    "121",  # Wyoming
    "009",  # Cattaraugus
    "013",  # Chautauqua
]

# Combined NY counties (we'll merge these for statewide coverage)
NY_ALL_COUNTIES = NY_CHAMPLAIN_COUNTIES + NY_NIAGARA_COUNTIES

STATE_COUNTIES = {
    "vt": VT_COUNTIES,
    "ny": NY_ALL_COUNTIES,  # Champlain + Niagara region counties
    "nh": ["001", "003", "005", "007", "009", "011", "013", "015", "017", "019"],  # All NH counties
    "me": ["001", "003", "005", "007", "009", "011", "013", "015", "017", "019", "021", "023", "025", "027", "029", "031"],
    "ma": ["001", "003", "005", "007", "009", "011", "013", "015", "017", "019", "021", "023", "025", "027"],
    # Hawaii counties (all 5)
    "hi": ["001", "003", "005", "007", "009"],  # Hawaii, Honolulu, Kalawao, Kauai, Maui
}


def parse_census_uri(uri: str) -> dict:
    """
    Parse a census URI into components.

    Args:
        uri: Census URI like "census:tiger/2023/vt/cousub"

    Returns:
        Dict with year, state, type, fips, url(s), per_county flag
    """
    if not uri.startswith("census:"):
        raise ValueError(f"Not a census URI: {uri}")

    # Strip scheme
    path = uri[7:]  # Remove "census:"

    # Expected format: tiger/{year}/{state}/{type}
    parts = path.split("/")
    if len(parts) != 4 or parts[0] != "tiger":
        raise ValueError(
            f"Invalid census URI format: {uri}\n"
            "Expected: census:tiger/{year}/{state}/{type}"
        )

    _, year, state, layer_type = parts

    state_lower = state.lower()
    if state_lower not in STATE_FIPS:
        raise ValueError(f"Unknown state: {state}")

    if layer_type not in TIGER_TYPES:
        raise ValueError(
            f"Unknown TIGER type: {layer_type}\n"
            f"Valid types: {', '.join(TIGER_TYPES.keys())}"
        )

    fips = STATE_FIPS[state_lower]
    type_info = TIGER_TYPES[layer_type]
    tiger_folder = type_info["folder"]
    per_county = type_info["per_county"]
    is_national = type_info.get("national", False)

    # Build URL(s)
    if is_national:
        # National file (e.g., county, state) - single US-wide file
        url = (
            f"https://www2.census.gov/geo/tiger/TIGER{year}/{tiger_folder}/"
            f"tl_{year}_us_{layer_type}.zip"
        )
        urls = [url]
    elif per_county:
        # Per-county files - need to download multiple
        counties = STATE_COUNTIES.get(state_lower, [])
        urls = []
        for county_fips in counties:
            full_fips = f"{fips}{county_fips}"
            url = (
                f"https://www2.census.gov/geo/tiger/TIGER{year}/{tiger_folder}/"
                f"tl_{year}_{full_fips}_{layer_type}.zip"
            )
            urls.append(url)
        url = urls[0] if urls else None  # Primary URL for display
    else:
        # Per-state file
        url = (
            f"https://www2.census.gov/geo/tiger/TIGER{year}/{tiger_folder}/"
            f"tl_{year}_{fips}_{layer_type}.zip"
        )
        urls = [url]

    # Estimate file size
    size_key = (state_lower, layer_type)
    if size_key in TIGER_SIZE_ESTIMATES:
        size_mb = TIGER_SIZE_ESTIMATES[size_key]
    else:
        default_key = f"_default_{layer_type}"
        size_mb = TIGER_SIZE_ESTIMATES.get(default_key, 5.0)

    return {
        "year": year,
        "state": state_lower,
        "type": layer_type,
        "fips": fips,
        "url": url,
        "urls": urls,
        "per_county": per_county,
        "national": is_national,
        "estimated_size_mb": size_mb,
    }


def estimate_census_size(uri: str) -> dict:
    """
    Estimate download size for a Census URI without downloading.

    Args:
        uri: Census URI like "census:tiger/2023/vt/cousub"

    Returns:
        Dict with estimated_size_mb, cached, cache_path
    """
    parsed = parse_census_uri(uri)
    cached = is_cached(uri)
    cache_path = get_cached_path(uri)

    return {
        "uri": uri,
        "estimated_size_mb": parsed["estimated_size_mb"],
        "cached": cached,
        "cache_path": str(cache_path),
        "url": parsed["url"],
    }


def _download_single_file(url: str, cache_path: Path) -> int:
    """Download a single file and extract to cache. Returns bytes downloaded."""
    max_retries = 3
    timeout = httpx.Timeout(30.0, connect=10.0, read=120.0)

    for attempt in range(max_retries):
        try:
            with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                response = client.get(url)
                response.raise_for_status()
            break
        except httpx.HTTPError as e:
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Failed to download {url}: {e}")

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        zf.extractall(cache_path)

    return len(response.content)


def fetch_census(uri: str, force: bool = False) -> str:
    """
    Fetch Census TIGER data and return path to shapefile.

    For per-county data (areawater, linearwater), downloads all county
    files and merges them into a single shapefile.

    Args:
        uri: Census URI like "census:tiger/2023/vt/cousub"
        force: Re-download even if cached

    Returns:
        Path to the downloaded/merged shapefile (.shp)
    """
    # Check cache first
    if not force and is_cached(uri):
        cache_path = get_cached_path(uri)
        # For merged per-county data, look for merged.shp
        merged = cache_path / "merged.shp"
        if merged.exists():
            console.print(f"  [green]✓[/] {uri} [dim](cached)[/]")
            return str(merged)
        # For filtered national data, look for filtered.shp
        filtered = cache_path / "filtered.shp"
        if filtered.exists():
            console.print(f"  [green]✓[/] {uri} [dim](cached)[/]")
            return str(filtered)
        # For regular per-state files
        shapefiles = list(cache_path.glob("*.shp"))
        if shapefiles:
            console.print(f"  [green]✓[/] {uri} [dim](cached)[/]")
            return str(shapefiles[0])

    # Parse URI to get URL(s)
    parsed = parse_census_uri(uri)
    urls = parsed["urls"]
    per_county = parsed["per_county"]
    is_national = parsed.get("national", False)
    state_fips = parsed["fips"]

    cache_path = get_cached_path(uri)
    cache_path.mkdir(parents=True, exist_ok=True)

    if is_national:
        # National file - download once and filter by state FIPS
        url = urls[0]
        console.print(f"  [cyan]↓[/] Downloading {uri} (national file, filtering to state)...")

        bytes_downloaded = _download_single_file(url, cache_path)

        # Find the shapefile and filter by state
        shapefiles = list(cache_path.glob("*.shp"))
        if not shapefiles:
            raise RuntimeError(f"No shapefile found in downloaded archive: {url}")

        import geopandas as gpd

        gdf = gpd.read_file(shapefiles[0])

        # Filter by state FIPS (STATEFP column)
        if "STATEFP" in gdf.columns:
            state_gdf = gdf[gdf["STATEFP"] == state_fips].copy()
        elif "STATEFP20" in gdf.columns:
            state_gdf = gdf[gdf["STATEFP20"] == state_fips].copy()
        else:
            # Try to infer from GEOID
            if "GEOID" in gdf.columns:
                state_gdf = gdf[gdf["GEOID"].str.startswith(state_fips)].copy()
            else:
                console.print(f"  [yellow]Warning: Could not filter national file by state[/]")
                state_gdf = gdf

        # Save filtered file
        filtered_path = cache_path / "filtered.shp"
        state_gdf.to_file(filtered_path)

        console.print(f"  [green]✓[/] {uri} [dim]({bytes_downloaded / 1024 / 1024:.1f} MB, {len(state_gdf)} features)[/]")
        return str(filtered_path)

    elif per_county and len(urls) > 1:
        # Download multiple county files and merge
        console.print(f"  [cyan]↓[/] Downloading {uri} ({len(urls)} counties)...")

        total_bytes = 0
        all_gdfs = []

        for i, url in enumerate(urls):
            county_dir = cache_path / f"county_{i:03d}"
            county_dir.mkdir(parents=True, exist_ok=True)

            try:
                bytes_downloaded = _download_single_file(url, county_dir)
                total_bytes += bytes_downloaded

                # Load the shapefile
                shapefiles = list(county_dir.glob("*.shp"))
                if shapefiles:
                    import geopandas as gpd
                    gdf = gpd.read_file(shapefiles[0])
                    all_gdfs.append(gdf)
            except Exception as e:
                # Some counties might not have data, skip them
                console.print(f"  [dim]Skipped county {i+1}: {e}[/]")
                continue

        if not all_gdfs:
            raise RuntimeError(f"No data found for {uri}")

        # Merge all county data
        import pandas as pd
        import geopandas as gpd

        merged_gdf = gpd.GeoDataFrame(
            pd.concat(all_gdfs, ignore_index=True),
            crs=all_gdfs[0].crs
        )

        # Save merged file
        merged_path = cache_path / "merged.shp"
        merged_gdf.to_file(merged_path)

        console.print(f"  [green]✓[/] {uri} [dim]({total_bytes / 1024 / 1024:.1f} MB, {len(merged_gdf)} features)[/]")
        return str(merged_path)

    else:
        # Single file download
        url = urls[0]
        console.print(f"  [cyan]↓[/] Downloading {uri}...")

        bytes_downloaded = _download_single_file(url, cache_path)

        # Find the shapefile
        shapefiles = list(cache_path.glob("*.shp"))
        if not shapefiles:
            raise RuntimeError(f"No shapefile found in downloaded archive: {url}")

        console.print(f"  [green]✓[/] {uri} [dim]({bytes_downloaded / 1024 / 1024:.1f} MB)[/]")
        return str(shapefiles[0])
