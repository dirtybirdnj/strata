#!/usr/bin/env python3
"""
California Counties Random Fill Generator

Creates a plotter-ready SVG with each California county filled with a
randomized pattern and color using rat-king.
"""

import subprocess
import random
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Available rat-king patterns (all 30)
PATTERNS = [
    "lines", "crosshatch", "zigzag", "wiggle", "spiral", "fermat",
    "concentric", "radial", "honeycomb", "crossspiral", "hilbert",
    "guilloche", "lissajous", "rose", "phyllotaxis", "scribble",
    "gyroid", "pentagon15", "pentagon14", "grid", "brick", "truchet",
    "stipple", "peano", "sierpinski", "diagonal", "herringbone",
    "stripe", "tessellation", "harmonograph"
]

# A curated subset of patterns that work well for plotter fills
PLOTTER_FRIENDLY_PATTERNS = [
    "lines", "crosshatch", "zigzag", "wiggle", "spiral",
    "concentric", "honeycomb", "grid", "brick", "diagonal",
    "herringbone", "stripe"
]

# Color palette for plotter pens (CMYK-friendly)
COLORS = [
    "#000000",  # Black
    "#1a1a1a",  # Dark gray
    "#333333",  # Medium gray
    "#0066cc",  # Blue
    "#cc0000",  # Red
    "#009933",  # Green
    "#ff6600",  # Orange
    "#6600cc",  # Purple
    "#cc6600",  # Brown
    "#006666",  # Teal
]


def extract_paths(svg_path: Path) -> list[tuple[str, str]]:
    """Extract path data from SVG file.

    Returns list of (path_id, path_d) tuples.
    """
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Handle SVG namespace
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    paths = []
    for i, path in enumerate(root.findall('.//svg:path', ns) or root.findall('.//path')):
        d = path.get('d', '')
        path_id = path.get('id', f'county_{i}')
        if d:
            paths.append((path_id, d))

    return paths


def create_single_polygon_svg(path_d: str, viewbox: str, width: str, height: str) -> str:
    """Create a minimal SVG with a single filled polygon."""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{viewbox}">
  <path d="{path_d}" fill="#cccccc" stroke="none"/>
</svg>'''


def fill_polygon_with_pattern(svg_content: str, pattern: str, spacing: float, angle: float, rat_king_path: Path) -> str:
    """Use rat-king to fill a polygon with a pattern.

    Returns the filled SVG content (just the pattern lines).
    """
    result = subprocess.run(
        [
            str(rat_king_path),
            "fill", "-",
            "-p", pattern,
            "-s", str(spacing),
            "-a", str(angle),
            "--strokes"
        ],
        input=svg_content,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Warning: rat-king failed: {result.stderr}", file=sys.stderr)
        return ""

    return result.stdout


def extract_polylines_from_svg(svg_content: str) -> list[str]:
    """Extract polyline elements from SVG content."""
    if not svg_content.strip():
        return []

    try:
        root = ET.fromstring(svg_content)
    except ET.ParseError:
        return []

    ns = {'svg': 'http://www.w3.org/2000/svg'}

    polylines = []
    for elem in root.findall('.//svg:polyline', ns) or root.findall('.//polyline'):
        points = elem.get('points', '')
        if points:
            polylines.append(points)

    # Also check for path elements (outline)
    for elem in root.findall('.//svg:path', ns) or root.findall('.//path'):
        d = elem.get('d', '')
        if d:
            polylines.append(('path', d))

    return polylines


def main():
    # Paths
    script_dir = Path(__file__).parent
    strata_root = script_dir.parent

    input_svg = strata_root / "output/ca_counties_fill/svg/medium_detail/01_ca_counties.svg"
    boundary_svg = strata_root / "output/ca_counties_fill/svg/medium_detail/02_ca_boundary.svg"
    output_svg = strata_root / "output/ca_counties_fill/ca_counties_random_filled.svg"
    rat_king_path = strata_root / "bin" / "rat-king"

    if not input_svg.exists():
        print(f"Error: Input SVG not found: {input_svg}")
        print("Run: strata build examples/ca_counties_fill.strata.yaml")
        sys.exit(1)

    if not rat_king_path.exists():
        print(f"Error: rat-king not found: {rat_king_path}")
        print("Install: cargo install rat-king-cli")
        sys.exit(1)

    # Parse input SVG for viewBox and dimensions
    tree = ET.parse(input_svg)
    root = tree.getroot()
    viewbox = root.get('viewBox', '0 0 1056 1632')
    width = root.get('width', '11.0in')
    height = root.get('height', '17.0in')

    # Extract paths
    paths = extract_paths(input_svg)
    print(f"Found {len(paths)} counties to fill")

    # Set random seed for reproducibility (change for different results)
    random.seed(42)

    # Generate fills for each county
    all_elements = []

    for i, (path_id, path_d) in enumerate(paths):
        # Random pattern and color
        pattern = random.choice(PLOTTER_FRIENDLY_PATTERNS)
        color = random.choice(COLORS)
        spacing = random.uniform(2.0, 5.0)
        angle = random.uniform(0, 180)

        print(f"  [{i+1}/{len(paths)}] {path_id}: {pattern} @ {angle:.0f}deg, spacing={spacing:.1f}")

        # Create single-polygon SVG
        single_svg = create_single_polygon_svg(path_d, viewbox, width, height)

        # Fill with pattern
        filled_svg = fill_polygon_with_pattern(
            single_svg, pattern, spacing, angle, rat_king_path
        )

        # Extract the generated polylines/paths
        polylines = extract_polylines_from_svg(filled_svg)

        # Add to output with color
        for pl in polylines:
            if isinstance(pl, tuple) and pl[0] == 'path':
                # It's a path (outline)
                all_elements.append(
                    f'  <path d="{pl[1]}" stroke="{color}" stroke-width="0.5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
                )
            else:
                # It's a polyline (fill pattern)
                all_elements.append(
                    f'  <polyline points="{pl}" stroke="{color}" stroke-width="0.3" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
                )

    # Add boundary if it exists
    if boundary_svg.exists():
        boundary_tree = ET.parse(boundary_svg)
        boundary_root = boundary_tree.getroot()
        for path in boundary_root.findall('.//{http://www.w3.org/2000/svg}path') or boundary_root.findall('.//path'):
            d = path.get('d', '')
            if d:
                all_elements.append(
                    f'  <path d="{d}" stroke="#000000" stroke-width="2.0" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
                )

    # Write output SVG
    output_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{viewbox}">
{chr(10).join(all_elements)}
</svg>'''

    output_svg.parent.mkdir(parents=True, exist_ok=True)
    output_svg.write_text(output_content)

    print(f"\nWrote: {output_svg}")
    print(f"Total elements: {len(all_elements)}")


if __name__ == "__main__":
    main()
