"""
strata.kelley: Visualization that reveals what raw data cannot.

"So that the plain man who pays for the census gets what he pays for,
statistical data in a form in which they are ready for him to understand."
    — Florence Kelley
"""

from .svg import render_svg, SVGExporter
from .plotter_fill import (
    generate_plotter_fill,
    process_plotter_output,
    check_rat_king_available,
    RAT_KING_BIN,
)

__all__ = [
    "render_svg",
    "SVGExporter",
    "generate_plotter_fill",
    "process_plotter_output",
    "check_rat_king_available",
    "RAT_KING_BIN",
]
