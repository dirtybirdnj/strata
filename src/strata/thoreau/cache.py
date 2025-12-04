"""
Cache management for downloaded data.
"""

from pathlib import Path

from platformdirs import user_cache_dir


def get_cache_dir() -> Path:
    """Get the strata cache directory, creating it if needed."""
    cache_dir = Path(user_cache_dir("strata", "dirtybirdnj"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cached_path(uri: str) -> Path:
    """
    Get the cache path for a given URI.

    Args:
        uri: Source URI (e.g., "census:tiger/2023/vt/cousub")

    Returns:
        Path where this data would be cached
    """
    # Convert URI to filesystem-safe path
    # census:tiger/2023/vt/cousub -> census/tiger/2023/vt/cousub
    safe_path = uri.replace(":", "/")
    return get_cache_dir() / safe_path


def is_cached(uri: str) -> bool:
    """
    Check if data for a URI is already cached.

    Args:
        uri: Source URI

    Returns:
        True if data exists in cache
    """
    cache_path = get_cached_path(uri)
    if not cache_path.exists():
        return False

    # Check for shapefile or geojson (recursively for nested archives)
    shapefiles = list(cache_path.rglob("*.shp"))
    geojsons = list(cache_path.rglob("*.geojson"))

    return len(shapefiles) > 0 or len(geojsons) > 0


def clear_cache(uri: str | None = None) -> None:
    """
    Clear cached data.

    Args:
        uri: Specific URI to clear, or None to clear all
    """
    import shutil

    if uri:
        cache_path = get_cached_path(uri)
        if cache_path.exists():
            shutil.rmtree(cache_path)
    else:
        cache_dir = get_cache_dir()
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
