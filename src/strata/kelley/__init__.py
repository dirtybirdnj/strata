"""
strata.kelley: Visualization that reveals what raw data cannot.

"So that the plain man who pays for the census gets what he pays for,
statistical data in a form in which they are ready for him to understand."
    — Florence Kelley

A map is not decoration. A map is evidence.

When we render these geometries to SVG or display them on the web, we do so
with purpose: so that the reader can easily see the patterns that would
remain hidden in tables of coordinates. The clustering of towns, the threading
of rivers, the way Lake Champlain carves through the landscape—these
relationships become visible only when properly presented.

I have no patience for visualizations that obscure rather than reveal. Every
color choice, every line weight, every layer ordering must serve the goal of
comprehension. Statistical projections which speak to the senses without
fatiguing the mind possess the advantage of fixing attention on a great
number of important facts.

The plain citizen who uses these maps deserves data in a form ready to
understand.

Functions:
    render_svg() - Generate scalable vector graphics
    render_geojson() - Export as GeoJSON
    render_pmtiles() - Create PMTiles archive
    apply_style() - Apply stroke, fill, and other styling
    optimize_for_plotter() - Deduplicate strokes, minimize pen travel
"""

# TODO: Implement output rendering
