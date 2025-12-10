"""
Fetch vector data from USGS National Map WFS services.

USGS provides OGC Web Feature Services (WFS) for various themes including
transportation, contours, hydrography, government units, and structures.
These services provide live, queryable vector data without needing to
download and decompose GeoPDF files.

Data licensing: Public Domain (U.S. Government Work)
Source: https://apps.nationalmap.gov/services/

Note on NHD: As of October 2023, the National Hydrography Dataset was
retired in favor of the 3D Hydrography Program (3DHP). WFS endpoints
still function but data is no longer being updated.
"""

import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode

import httpx
from rich.console import Console

from .cache import get_cached_path, is_cached, get_cache_dir

console = Console()

# WFS service definitions
# Each service has a base URL and available layers with their IDs
WFS_SERVICES = {
    "transportation": {
        "base": "https://cartowfs.nationalmap.gov/arcgis/services/transportation/MapServer/WFSServer",
        "rest": "https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/MapServer",
        "srs": "EPSG:4326",
        "layers": {
            "airport": {"id": 1, "geometry": "Point", "description": "Airport locations"},
            "airport_runway": {"id": 2, "geometry": "Polygon", "description": "Airport runways"},
            "interstate": {"id": 3, "geometry": "Polyline", "description": "Interstate highways"},
            "us_route": {"id": 4, "geometry": "Polyline", "description": "U.S. numbered routes"},
            "state_route": {"id": 5, "geometry": "Polyline", "description": "State highways"},
            "railroad": {"id": 6, "geometry": "Polyline", "description": "Railroad lines"},
            "local_road": {"id": 7, "geometry": "Polyline", "description": "Local streets"},
            "trail": {"id": 8, "geometry": "Polyline", "description": "Trails and paths"},
        },
    },
    "contours": {
        "base": "https://cartowfs.nationalmap.gov/arcgis/services/contours/MapServer/WFSServer",
        "rest": "https://cartowfs.nationalmap.gov/arcgis/rest/services/contours/MapServer",
        "srs": "EPSG:4326",  # Service uses 3857 but we'll request 4326
        "layers": {
            "100ft": {"id": 1, "geometry": "Polyline", "description": "100-foot contour lines"},
            "50ft": {"id": 3, "geometry": "Polyline", "description": "50-foot contour lines"},
            "large_scale": {"id": 5, "geometry": "Polyline", "description": "Large-scale contours"},
        },
    },
    "nhd": {
        "base": "https://hydro.nationalmap.gov/arcgis/services/nhd/MapServer/WFSServer",
        "rest": "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer",
        "srs": "EPSG:4326",
        "layers": {
            "point": {"id": 0, "geometry": "Point", "description": "Springs, wells, gages, dams"},
            "flowline_small": {"id": 4, "geometry": "Polyline", "description": "Streams/rivers (small scale)"},
            "flowline": {"id": 6, "geometry": "Polyline", "description": "Streams/rivers (large scale)"},
            "area_small": {"id": 7, "geometry": "Polygon", "description": "Water areas (small scale)"},
            "area": {"id": 9, "geometry": "Polygon", "description": "Water areas (large scale)"},
            "waterbody_small": {"id": 10, "geometry": "Polygon", "description": "Lakes/ponds (small scale)"},
            "waterbody": {"id": 12, "geometry": "Polygon", "description": "Lakes/ponds (large scale)"},
        },
    },
    "govunits": {
        "base": "https://cartowfs.nationalmap.gov/arcgis/services/govunits/MapServer/WFSServer",
        "rest": "https://cartowfs.nationalmap.gov/arcgis/rest/services/govunits/MapServer",
        "srs": "EPSG:4326",
        "layers": {
            # Feature layers (polygons) - IDs 19-37
            "state": {"id": 19, "geometry": "Polygon", "description": "State/territory boundaries"},
            "county": {"id": 20, "geometry": "Polygon", "description": "County boundaries"},
            "congressional_district": {"id": 21, "geometry": "Polygon", "description": "Congressional districts"},
            "incorporated_place": {"id": 22, "geometry": "Polygon", "description": "Cities/towns"},
            "unincorporated_place": {"id": 23, "geometry": "Polygon", "description": "Unincorporated communities"},
            "minor_civil_division": {"id": 24, "geometry": "Polygon", "description": "Townships, etc."},
            "native_american_area": {"id": 25, "geometry": "Polygon", "description": "Tribal lands"},
            "national_park": {"id": 26, "geometry": "Polygon", "description": "National parks"},
            "national_forest": {"id": 27, "geometry": "Polygon", "description": "National forests"},
            "national_wilderness": {"id": 28, "geometry": "Polygon", "description": "Wilderness areas"},
            "fish_wildlife": {"id": 29, "geometry": "Polygon", "description": "USFWS areas"},
            "national_grassland": {"id": 30, "geometry": "Polygon", "description": "National grasslands"},
            "blm": {"id": 31, "geometry": "Polygon", "description": "BLM lands"},
            "tva": {"id": 32, "geometry": "Polygon", "description": "TVA areas"},
            "military": {"id": 33, "geometry": "Polygon", "description": "Military installations"},
            "national_cemetery": {"id": 34, "geometry": "Polygon", "description": "National cemeteries"},
            "nasa": {"id": 35, "geometry": "Polygon", "description": "NASA facilities"},
            "airport_area": {"id": 36, "geometry": "Polygon", "description": "Metro Washington airports"},
        },
    },
    "structures": {
        "base": "https://cartowfs.nationalmap.gov/arcgis/services/structures/MapServer/WFSServer",
        "rest": "https://cartowfs.nationalmap.gov/arcgis/rest/services/structures/MapServer",
        "srs": "EPSG:4326",
        "layers": {
            "all": {"id": 0, "geometry": "Point", "description": "All structure types"},
        },
    },
    "wbd": {
        "base": "https://hydro-wfs.nationalmap.gov/arcgis/services/wbd/MapServer/WFSServer",
        "rest": "https://hydro-wfs.nationalmap.gov/arcgis/rest/services/wbd/MapServer",
        "srs": "EPSG:4326",
        "layers": {
            "huc2": {"id": 1, "geometry": "Polygon", "description": "2-digit HUC regions"},
            "huc4": {"id": 2, "geometry": "Polygon", "description": "4-digit HUC subregions"},
            "huc6": {"id": 3, "geometry": "Polygon", "description": "6-digit HUC basins"},
            "huc8": {"id": 4, "geometry": "Polygon", "description": "8-digit HUC subbasins"},
            "huc10": {"id": 5, "geometry": "Polygon", "description": "10-digit HUC watersheds"},
            "huc12": {"id": 6, "geometry": "Polygon", "description": "12-digit HUC subwatersheds"},
        },
    },
    "geonames": {
        "base": "https://cartowfs.nationalmap.gov/arcgis/services/geonames/MapServer/WFSServer",
        "rest": "https://cartowfs.nationalmap.gov/arcgis/rest/services/geonames/MapServer",
        "srs": "EPSG:4326",
        "layers": {
            "all": {"id": 0, "geometry": "Point", "description": "Geographic place names"},
        },
    },
}

# Approximate size estimates per layer per 0.5 degree cell (in MB)
SIZE_ESTIMATES = {
    "transportation": {
        "interstate": 0.1,
        "us_route": 0.2,
        "state_route": 0.5,
        "railroad": 0.3,
        "local_road": 5.0,  # Can be large in urban areas
        "trail": 0.5,
        "_default": 0.5,
    },
    "contours": {
        "100ft": 2.0,
        "50ft": 5.0,
        "large_scale": 10.0,
        "_default": 5.0,
    },
    "nhd": {
        "flowline": 3.0,
        "waterbody": 1.0,
        "_default": 2.0,
    },
    "_default": 1.0,
}


def parse_usgs_uri(uri: str) -> dict:
    """
    Parse a USGS URI into components.

    Args:
        uri: USGS URI like "usgs:transportation/trail?bbox=-73.5,44.0,-72.5,45.0"
             or "usgs:nhd/flowline" (bbox provided at fetch time)

    Returns:
        Dict with service, layer, bbox (if present), and metadata

    URI format:
        usgs:{service}/{layer}[?bbox=west,south,east,north]

    Examples:
        usgs:transportation/interstate
        usgs:transportation/trail?bbox=-73.5,44.0,-72.5,45.0
        usgs:nhd/flowline
        usgs:contours/50ft
        usgs:govunits/national_park
    """
    if not uri.startswith("usgs:"):
        raise ValueError(f"Not a USGS URI: {uri}")

    # Split off query string
    path = uri[5:]  # Remove "usgs:"
    bbox = None

    if "?" in path:
        path, query = path.split("?", 1)
        # Parse query parameters
        for param in query.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                if key == "bbox":
                    try:
                        coords = [float(x) for x in value.split(",")]
                        if len(coords) == 4:
                            bbox = tuple(coords)
                    except ValueError:
                        pass

    parts = path.split("/")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid USGS URI format: {uri}\n"
            "Expected: usgs:{{service}}/{{layer}}[?bbox=w,s,e,n]\n"
            "Example: usgs:transportation/trail?bbox=-73.5,44.0,-72.5,45.0"
        )

    service, layer = parts

    # Validate service
    if service not in WFS_SERVICES:
        raise ValueError(
            f"Unknown USGS service: {service}\n"
            f"Valid services: {', '.join(WFS_SERVICES.keys())}"
        )

    service_info = WFS_SERVICES[service]

    # Validate layer
    if layer not in service_info["layers"]:
        raise ValueError(
            f"Unknown layer '{layer}' for service '{service}'\n"
            f"Valid layers: {', '.join(service_info['layers'].keys())}"
        )

    layer_info = service_info["layers"][layer]

    # Estimate size
    service_sizes = SIZE_ESTIMATES.get(service, {})
    size_mb = service_sizes.get(layer, service_sizes.get("_default", SIZE_ESTIMATES["_default"]))

    return {
        "service": service,
        "layer": layer,
        "layer_id": layer_info["id"],
        "geometry": layer_info["geometry"],
        "description": layer_info["description"],
        "wfs_base": service_info["base"],
        "rest_base": service_info["rest"],
        "srs": service_info["srs"],
        "bbox": bbox,
        "estimated_size_mb": size_mb,
    }


def _bbox_hash(bbox: tuple) -> str:
    """Create a short hash of a bounding box for cache paths."""
    bbox_str = f"{bbox[0]:.4f},{bbox[1]:.4f},{bbox[2]:.4f},{bbox[3]:.4f}"
    return hashlib.md5(bbox_str.encode()).hexdigest()[:8]


def _get_cache_path_with_bbox(uri: str, bbox: tuple) -> Path:
    """Get cache path for a USGS URI with a specific bounding box."""
    # Create path like: usgs/transportation/trail/bbox_a1b2c3d4
    base_path = get_cached_path(uri)
    bbox_dir = f"bbox_{_bbox_hash(bbox)}"
    return base_path / bbox_dir


def _is_cached_with_bbox(uri: str, bbox: tuple) -> bool:
    """Check if data is cached for a specific URI and bounding box."""
    cache_path = _get_cache_path_with_bbox(uri, bbox)
    if not cache_path.exists():
        return False
    geojsons = list(cache_path.glob("*.geojson"))
    return len(geojsons) > 0


def estimate_usgs_size(uri: str) -> dict:
    """
    Estimate download size for a USGS URI without downloading.

    Note: Actual size depends heavily on the bounding box used at fetch time.
    Estimates are per ~0.5 degree cell.
    """
    parsed = parse_usgs_uri(uri)
    bbox = parsed.get("bbox")

    # Can only check cache if bbox is in URI
    cached = False
    cache_path = None
    if bbox:
        cached = _is_cached_with_bbox(uri, bbox)
        cache_path = str(_get_cache_path_with_bbox(uri, bbox))

    return {
        "uri": uri,
        "estimated_size_mb": parsed["estimated_size_mb"],
        "cached": cached,
        "cache_path": cache_path,
        "description": parsed["description"],
        "note": "Size varies with bbox; estimate is per ~0.5 degree cell",
    }


def _fetch_wfs_geojson(
    rest_base: str,
    layer_id: int,
    bbox: tuple,
    srs: str = "EPSG:4326",
    max_features: int = 50000,
) -> dict:
    """
    Fetch features from an ArcGIS REST endpoint as GeoJSON.

    Uses the ArcGIS Server REST API query endpoint which supports GeoJSON output.

    Args:
        rest_base: REST service base URL (e.g., .../MapServer)
        layer_id: Layer ID to query
        bbox: Bounding box (west, south, east, north)
        srs: Spatial reference system
        max_features: Maximum features to return

    Returns:
        GeoJSON FeatureCollection dict
    """
    # Build the REST query URL
    rest_url = f"{rest_base}/{layer_id}/query"

    params = {
        "where": "1=1",
        "geometry": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "outSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "resultRecordCount": max_features,
    }

    timeout = httpx.Timeout(120.0, connect=30.0, read=180.0)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                response = client.get(rest_url, params=params)
                response.raise_for_status()

                data = response.json()

                # Check for ArcGIS error response
                if "error" in data:
                    error = data["error"]
                    raise RuntimeError(
                        f"USGS service error: {error.get('message', 'Unknown error')}"
                    )

                return data

        except httpx.HTTPError as e:
            if attempt < max_retries - 1:
                import time
                console.print(f"  [yellow]Retry {attempt + 1}...[/]")
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Failed to fetch from {rest_url}: {e}")


def fetch_usgs(uri: str, bbox: tuple | None = None, force: bool = False) -> str:
    """
    Fetch USGS WFS data and return path to GeoJSON file.

    Args:
        uri: USGS URI like "usgs:transportation/trail"
        bbox: Bounding box (west, south, east, north). Required unless in URI.
        force: Re-download even if cached

    Returns:
        Path to the downloaded GeoJSON file

    Example:
        # With bbox in URI
        path = fetch_usgs("usgs:transportation/trail?bbox=-73.5,44.0,-72.5,45.0")

        # With bbox as parameter
        path = fetch_usgs("usgs:transportation/trail", bbox=(-73.5, 44.0, -72.5, 45.0))
    """
    parsed = parse_usgs_uri(uri)

    # Get bbox from URI or parameter
    effective_bbox = parsed.get("bbox") or bbox
    if effective_bbox is None:
        raise ValueError(
            f"Bounding box required for USGS sources.\n"
            f"Either include in URI: {uri}?bbox=west,south,east,north\n"
            f"Or pass bbox parameter to fetch_usgs()"
        )

    # Check cache
    cache_path = _get_cache_path_with_bbox(uri, effective_bbox)
    geojson_path = cache_path / f"{parsed['layer']}.geojson"

    if not force and geojson_path.exists():
        console.print(f"  [green]✓[/] {uri} [dim](cached)[/]")
        return str(geojson_path)

    # Fetch from WFS
    console.print(f"  [cyan]↓[/] Fetching {uri}...")
    console.print(f"    [dim]bbox: {effective_bbox}[/]")

    cache_path.mkdir(parents=True, exist_ok=True)

    try:
        geojson_data = _fetch_wfs_geojson(
            rest_base=parsed["rest_base"],
            layer_id=parsed["layer_id"],
            bbox=effective_bbox,
            srs=parsed["srs"],
        )

        # Save to cache
        with open(geojson_path, "w") as f:
            json.dump(geojson_data, f)

        feature_count = len(geojson_data.get("features", []))
        file_size = geojson_path.stat().st_size / 1024 / 1024

        console.print(f"  [green]✓[/] {uri} [dim]({file_size:.1f} MB, {feature_count} features)[/]")

        return str(geojson_path)

    except Exception as e:
        console.print(f"  [red]✗[/] {uri}: {e}")
        raise


def list_services() -> dict:
    """
    List all available USGS WFS services and their layers.

    Returns:
        Dict of {service: {layer: description}}
    """
    result = {}
    for service, info in WFS_SERVICES.items():
        result[service] = {}
        for layer, layer_info in info["layers"].items():
            result[service][layer] = layer_info["description"]
    return result


def list_layers(service: str) -> dict:
    """
    List available layers for a specific service.

    Args:
        service: Service name (transportation, contours, nhd, govunits, structures, wbd, geonames)

    Returns:
        Dict of {layer: {"id": int, "geometry": str, "description": str}}
    """
    if service not in WFS_SERVICES:
        raise ValueError(
            f"Unknown service: {service}\n"
            f"Valid services: {', '.join(WFS_SERVICES.keys())}"
        )
    return WFS_SERVICES[service]["layers"]
