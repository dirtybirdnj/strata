"""
Plotter fill output using rat-king linefill patterns.

This module provides an optional post-processing step that converts
colored SVG polygons into hatched line patterns suitable for pen plotters.

Each unique fill color in the input SVG is mapped to a different
pattern/angle combination, creating visual distinction without relying on
color - perfect for single-pen plotter output.

Requires: rat-king CLI (https://github.com/dirtybirdnj/rat-king)
"""

import colorsys
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def _find_rat_king_binary() -> str:
    """
    Find the rat-king binary in order of preference:
    1. Bundled binary in strata's bin/ directory
    2. System PATH (from cargo install or manual installation)
    """
    # Check bundled binary (relative to this file's package)
    package_dir = Path(__file__).parent.parent.parent.parent  # strata repo root
    bundled = package_dir / "bin" / "rat-king"
    if bundled.exists() and bundled.is_file():
        return str(bundled)

    # Check system PATH
    system_bin = shutil.which("rat-king")
    if system_bin:
        return system_bin

    # Fallback to bundled path (will fail with helpful error if missing)
    return str(bundled)


# Default rat-king binary path - auto-detected
RAT_KING_BIN = _find_rat_king_binary()

# Available patterns from rat-king, ordered by visual density/complexity
# We'll cycle through these for different colors
PATTERNS = [
    "lines",
    "diagonal",
    "crosshatch",
    "zigzag",
    "honeycomb",
    "brick",
    "herringbone",
    "grid",
    "wiggle",
    "spiral",
    "concentric",
    "scribble",
]

# Base angles to vary patterns further (combined with pattern choice)
BASE_ANGLES = [0, 30, 45, 60, 90, 120, 135, 150]


def check_rat_king_available(bin_path: str = RAT_KING_BIN) -> bool:
    """Check if rat-king CLI is available."""
    try:
        result = subprocess.run(
            [bin_path, "patterns"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def extract_colors_from_svg(svg_content: str) -> set[str]:
    """
    Extract unique fill colors from SVG content.

    Returns set of hex colors (lowercase, 6-digit format).
    """
    colors = set()

    # Match fill="..." or fill='...'
    fill_pattern = r'fill=["\']([^"\']+)["\']'
    matches = re.findall(fill_pattern, svg_content, re.IGNORECASE)

    for match in matches:
        color = match.strip().lower()
        # Skip "none" and empty
        if color in ("none", ""):
            continue
        # Normalize to 6-digit hex
        if color.startswith("#"):
            if len(color) == 4:  # #RGB -> #RRGGBB
                color = f"#{color[1]*2}{color[2]*2}{color[3]*2}"
            colors.add(color.lower())

    return colors


def color_to_pattern_config(color: str, index: int, total_colors: int) -> dict:
    """
    Map a color to a pattern configuration.

    Uses a combination of pattern type and angle to create unique
    visual signatures for each color.

    Args:
        color: Hex color string
        index: Index of this color in the sorted color list
        total_colors: Total number of unique colors

    Returns:
        Dict with pattern, spacing, angle
    """
    # Select pattern based on index
    pattern_idx = index % len(PATTERNS)
    pattern = PATTERNS[pattern_idx]

    # Select base angle - rotate through angles as we cycle patterns
    cycle = index // len(PATTERNS)
    angle_idx = (index + cycle * 3) % len(BASE_ANGLES)
    angle = BASE_ANGLES[angle_idx]

    # Vary spacing slightly based on color luminance
    # Darker colors get denser fill (smaller spacing)
    try:
        r = int(color[1:3], 16) / 255.0
        g = int(color[3:5], 16) / 255.0
        b = int(color[5:7], 16) / 255.0
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
    except (ValueError, IndexError):
        luminance = 0.5

    # Spacing range: 2.0 (dark) to 4.0 (light)
    spacing = 2.0 + luminance * 2.0

    return {
        "pattern": pattern,
        "spacing": spacing,
        "angle": angle,
        "color": color,
    }


def create_color_svg(
    svg_content: str,
    target_color: str,
    output_path: Path,
) -> bool:
    """
    Create an SVG containing only polygons of a specific color.

    Extracts paths with the target fill color and creates a new SVG
    with those paths (fill set to black for rat-king processing).
    """
    # Parse viewBox and dimensions from original SVG
    viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
    width_match = re.search(r'width="([^"]+)"', svg_content)
    height_match = re.search(r'height="([^"]+)"', svg_content)

    viewbox = viewbox_match.group(1) if viewbox_match else "0 0 1152 1728"
    width = width_match.group(1) if width_match else "12in"
    height = height_match.group(1) if height_match else "18in"

    # Find all paths with this fill color
    # Match: <path ... fill="color" .../>
    path_pattern = rf'<path[^>]*fill=["\']({re.escape(target_color)})["\'][^>]*/>'
    matches = re.findall(rf'(<path[^>]*fill=["\']({re.escape(target_color)})["\'][^>]*/>)', svg_content, re.IGNORECASE)

    if not matches:
        # Try alternate pattern where fill comes before d
        matches = re.findall(rf'(<path[^>]*/>)', svg_content, re.IGNORECASE)
        matches = [(m, target_color) for m in matches if f'fill="{target_color}"' in m.lower() or f"fill='{target_color}'" in m.lower()]

    if not matches:
        return False

    # Build new SVG with just these paths (fill set to black)
    paths = []
    for match in matches:
        path_elem = match[0] if isinstance(match, tuple) else match
        # Replace fill color with black (rat-king needs filled shapes)
        modified = re.sub(r'fill=["\'][^"\']+["\']', 'fill="#000000"', path_elem)
        paths.append(modified)

    svg_out = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{viewbox}">
{chr(10).join(paths)}
</svg>'''

    output_path.write_text(svg_out)
    return True


def apply_rat_king_pattern(
    svg_path: Path,
    pattern: str,
    spacing: float,
    angle: float,
    output_path: Path,
    bin_path: str = RAT_KING_BIN,
    include_strokes: bool = True,
) -> bool:
    """
    Apply rat-king pattern fill to an SVG.

    Args:
        svg_path: Input SVG path
        pattern: Pattern name (lines, crosshatch, etc.)
        spacing: Line spacing
        angle: Pattern angle in degrees
        output_path: Output SVG path
        bin_path: Path to rat-king binary
        include_strokes: Include polygon outlines in output

    Returns:
        True if successful, False otherwise
    """
    cmd = [
        bin_path, "fill",
        str(svg_path),
        "-p", pattern,
        "-s", str(spacing),
        "-a", str(angle),
        "-o", str(output_path),
    ]

    if include_strokes:
        cmd.append("--strokes")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        console.print(f"  [red]Error running rat-king: {e}[/]")
        return False


def merge_pattern_svgs(
    pattern_svgs: list[Path],
    output_path: Path,
    viewbox: str,
    width: str,
    height: str,
    stroke_color: str = "#000000",
    stroke_width: float = 0.5,
) -> None:
    """
    Merge multiple pattern SVGs into a single output SVG.

    Extracts all line/path elements from each input SVG and combines
    them into a single SVG file.
    """
    all_elements = []

    for svg_path in pattern_svgs:
        if not svg_path.exists():
            continue

        content = svg_path.read_text()

        # Extract line elements
        lines = re.findall(r'<line[^>]+/>', content)
        all_elements.extend(lines)

        # Extract path elements (for strokes/outlines)
        paths = re.findall(r'<path[^>]+/>', content)
        all_elements.extend(paths)

    # Build merged SVG
    svg_out = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{viewbox}">
  <g stroke="{stroke_color}" stroke-width="{stroke_width}" stroke-linecap="round" fill="none">
{chr(10).join(f"    {e}" for e in all_elements)}
  </g>
</svg>'''

    output_path.write_text(svg_out)


def generate_plotter_fill(
    input_svg: Path,
    output_svg: Path,
    bin_path: str = RAT_KING_BIN,
    stroke_color: str = "#000000",
    stroke_width: float = 0.5,
    include_outlines: bool = True,
    base_spacing: float = 3.0,
) -> bool:
    """
    Generate plotter-ready fill patterns for an SVG.

    Takes an SVG with colored polygons and converts each color to a
    unique hatch pattern, producing a line-only SVG suitable for
    pen plotters.

    Args:
        input_svg: Input SVG path (with colored fills)
        output_svg: Output SVG path (line patterns only)
        bin_path: Path to rat-king binary
        stroke_color: Output stroke color
        stroke_width: Output stroke width
        include_outlines: Include polygon outlines in output
        base_spacing: Base spacing for patterns (adjusted per color)

    Returns:
        True if successful, False otherwise
    """
    if not check_rat_king_available(bin_path):
        console.print(f"  [red]Error: rat-king not found at {bin_path}[/]")
        return False

    # Read input SVG
    svg_content = input_svg.read_text()

    # Extract SVG metadata
    viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
    width_match = re.search(r'width="([^"]+)"', svg_content)
    height_match = re.search(r'height="([^"]+)"', svg_content)

    viewbox = viewbox_match.group(1) if viewbox_match else "0 0 1152 1728"
    width = width_match.group(1) if width_match else "12in"
    height = height_match.group(1) if height_match else "18in"

    # Extract unique colors
    colors = extract_colors_from_svg(svg_content)

    if not colors:
        console.print("  [yellow]No fill colors found in SVG[/]")
        return False

    console.print(f"  Found {len(colors)} unique fill colors")

    # Sort colors for consistent pattern assignment
    sorted_colors = sorted(colors)

    # Create pattern configs for each color
    color_configs = {}
    for i, color in enumerate(sorted_colors):
        config = color_to_pattern_config(color, i, len(sorted_colors))
        # Scale spacing by base_spacing factor
        config["spacing"] = config["spacing"] * (base_spacing / 3.0)
        color_configs[color] = config

    # Process each color with rat-king
    pattern_svgs = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        for color, config in color_configs.items():
            console.print(f"    {color} -> {config['pattern']} @ {config['angle']}°")

            # Create SVG with just this color's polygons
            color_svg = tmpdir / f"color_{color.replace('#', '')}.svg"
            if not create_color_svg(svg_content, color, color_svg):
                console.print(f"    [yellow]No paths found for {color}[/]")
                continue

            # Apply pattern
            pattern_svg = tmpdir / f"pattern_{color.replace('#', '')}.svg"
            success = apply_rat_king_pattern(
                color_svg,
                config["pattern"],
                config["spacing"],
                config["angle"],
                pattern_svg,
                bin_path=bin_path,
                include_strokes=include_outlines,
            )

            if success and pattern_svg.exists():
                pattern_svgs.append(pattern_svg)
            else:
                console.print(f"    [yellow]Pattern generation failed for {color}[/]")

        if not pattern_svgs:
            console.print("  [red]No patterns generated[/]")
            return False

        # Merge all patterns into output
        merge_pattern_svgs(
            pattern_svgs,
            output_svg,
            viewbox,
            width,
            height,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
        )

    console.print(f"  [green]✓[/] Generated plotter fill: {output_svg.name}")
    return True


def process_plotter_output(
    svg_dir: Path,
    output_dir: Optional[Path] = None,
    bin_path: str = RAT_KING_BIN,
    stroke_width: float = 0.5,
    base_spacing: float = 3.0,
) -> list[Path]:
    """
    Process all combined SVGs in a directory to create plotter fill versions.

    Looks for combined.svg files and creates corresponding _plotter.svg files
    with hatch patterns instead of color fills.

    Args:
        svg_dir: Directory containing SVG files
        output_dir: Output directory (default: same as svg_dir)
        bin_path: Path to rat-king binary
        stroke_width: Output stroke width
        base_spacing: Base spacing for patterns

    Returns:
        List of created plotter fill SVG paths
    """
    if output_dir is None:
        output_dir = svg_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    created = []

    # Find combined SVGs (these have all layers with colors)
    for svg_path in svg_dir.glob("**/combined.svg"):
        output_name = svg_path.stem + "_plotter.svg"
        output_path = output_dir / svg_path.parent.name / output_name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        console.print(f"  Processing {svg_path.parent.name}/combined.svg...")

        success = generate_plotter_fill(
            svg_path,
            output_path,
            bin_path=bin_path,
            stroke_width=stroke_width,
            base_spacing=base_spacing,
        )

        if success:
            created.append(output_path)

    return created
