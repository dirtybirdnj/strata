"""
strata.thoreau: Data acquisition from authoritative sources.

"I fathomed it easily with a cod-line and a stone weighing about a pound
and a half, and could tell accurately when the stone left the bottom,
by having to pull so much harder before the water got underneath to help me."
    — Henry David Thoreau, Walden
"""

from .census import fetch_census, parse_census_uri, estimate_census_size
from .quebec import fetch_quebec, parse_quebec_uri, estimate_quebec_size
from .cache import get_cache_dir, is_cached, get_cached_path, clear_cache

__all__ = [
    "fetch",
    "estimate_size",
    "fetch_census",
    "parse_census_uri",
    "estimate_census_size",
    "fetch_quebec",
    "parse_quebec_uri",
    "estimate_quebec_size",
    "get_cache_dir",
    "is_cached",
    "get_cached_path",
    "clear_cache",
]


def fetch(uri: str, force: bool = False) -> str:
    """
    Fetch data from a source URI and return the local path.

    Args:
        uri: Source URI (e.g., "census:tiger/2023/vt/cousub")
        force: Re-download even if cached

    Returns:
        Path to local data file (shapefile or geojson)

    Raises:
        ValueError: If URI scheme is not recognized
        FileNotFoundError: If local file doesn't exist
    """
    from pathlib import Path
    from rich.console import Console
    console = Console()

    if uri.startswith("census:"):
        return fetch_census(uri, force=force)
    elif uri.startswith("canvec:"):
        raise NotImplementedError("CanVec fetching not yet implemented")
    elif uri.startswith("quebec:"):
        return fetch_quebec(uri, force=force)
    elif uri.startswith("file:"):
        # Local file - validate and return the path
        local_path = uri[5:]  # Strip "file:" prefix

        # Handle relative paths
        path = Path(local_path)
        if not path.is_absolute():
            # Try relative to cwd
            path = Path.cwd() / local_path

        if not path.exists():
            raise FileNotFoundError(f"Local file not found: {path}")

        console.print(f"  [green]✓[/] {uri} [dim](local)[/]")
        return str(path)
    else:
        raise ValueError(f"Unknown source URI scheme: {uri}")


def estimate_size(uri: str) -> dict:
    """
    Estimate download size for a URI without downloading.

    Args:
        uri: Source URI (e.g., "census:tiger/2023/vt/cousub")

    Returns:
        Dict with estimated_size_mb, cached, cache_path, url
    """
    if uri.startswith("census:"):
        return estimate_census_size(uri)
    elif uri.startswith("canvec:"):
        return {"uri": uri, "estimated_size_mb": 50.0, "cached": False, "note": "CanVec not yet implemented"}
    elif uri.startswith("quebec:"):
        return estimate_quebec_size(uri)
    elif uri.startswith("file:"):
        from pathlib import Path
        path = Path(uri[5:])
        size_mb = path.stat().st_size / 1024 / 1024 if path.exists() else 0
        return {"uri": uri, "estimated_size_mb": size_mb, "cached": True, "cache_path": str(path)}
    else:
        return {"uri": uri, "estimated_size_mb": 0, "cached": False, "error": "Unknown scheme"}
