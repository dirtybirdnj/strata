"""
Strata: CLI tool for creating plotter-ready vector maps from authoritative GIS sources.

Just as the Earth reveals its history through the ordering of its strata—each layer
distinct, identifiable, and positioned in proper relation to those above and below—
so too must our maps be constructed.

Modules:
    thoreau  - Data acquisition (fetching from Census, CanVec, etc.)
    humboldt - Processing & transformation (geometry operations)
    kelley   - Visualization & output (SVG, GeoJSON, PMTiles)
    maury    - Pipeline orchestration (recipes, builds)
"""

__version__ = "0.1.0"
__author__ = "dirtybirdnj"

from strata.maury.recipe import Recipe

__all__ = ["Recipe", "__version__"]
