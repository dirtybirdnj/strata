"""
SVG export for pen plotters.

Based on the SVGPlotterExporter from vt-geodata, adapted for strata.
"""

import colorsys
import hashlib
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import (
    LineString,
    MultiLineString,
    MultiPolygon,
    Polygon,
)


def vary_color(base_hex: str, index: int, variation: float = 0.15) -> str:
    """
    Create a varied shade of a base color.

    Args:
        base_hex: Base color in hex format (#RRGGBB)
        index: Index used to determine variation (can be feature index or hash)
        variation: Amount of variation (0.0-1.0), default 0.15 = 15%

    Returns:
        Varied color in hex format
    """
    # Parse hex color
    base_hex = base_hex.lstrip('#')
    r = int(base_hex[0:2], 16) / 255.0
    g = int(base_hex[2:4], 16) / 255.0
    b = int(base_hex[4:6], 16) / 255.0

    # Convert to HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Use index to create consistent but varied adjustments
    # Create a pseudo-random but deterministic offset
    offset = ((index * 7919) % 100) / 100.0  # Prime number for better distribution

    # Vary saturation and value slightly
    s_adjust = (offset - 0.5) * variation * 0.5  # Smaller sat variation
    v_adjust = (offset - 0.5) * variation  # Larger value variation

    new_s = max(0.1, min(1.0, s + s_adjust))
    new_v = max(0.3, min(1.0, v + v_adjust))

    # Convert back to RGB
    new_r, new_g, new_b = colorsys.hsv_to_rgb(h, new_s, new_v)

    return f"#{int(new_r * 255):02x}{int(new_g * 255):02x}{int(new_b * 255):02x}"


class SVGExporter:
    """
    Export GeoDataFrames to SVG optimized for pen plotters.
    """

    def __init__(
        self,
        width: float = 12,
        height: float = 18,
        units: str = "in",
        margin: float = 0.5,
        dpi: float = 96,
    ):
        """
        Initialize exporter with page size.

        Args:
            width: Page width (default 12 inches)
            height: Page height (default 18 inches)
            units: Units (in, mm, px)
            margin: Page margin in same units
            dpi: DPI for px conversion (default 96)
        """
        self.width = width
        self.height = height
        self.units = units
        self.margin = margin
        self.dpi = dpi

        # Convert to pixels for internal calculations
        if units == "in":
            self.width_px = width * dpi
            self.height_px = height * dpi
            self.margin_px = margin * dpi
        elif units == "mm":
            self.width_px = width * dpi / 25.4
            self.height_px = height * dpi / 25.4
            self.margin_px = margin * dpi / 25.4
        else:
            self.width_px = width
            self.height_px = height
            self.margin_px = margin

    def _calculate_transform(
        self,
        bounds: tuple,
    ) -> tuple[float, float, float, float]:
        """
        Calculate scale and translation to fit geometry in page bounds.

        Args:
            bounds: (minx, miny, maxx, maxy) of the geometry

        Returns:
            (scale_x, scale_y, offset_x, offset_y)
        """
        import math

        minx, miny, maxx, maxy = bounds

        geo_width = maxx - minx
        geo_height = maxy - miny

        # For unprojected lat/lon (EPSG:4326), we need to account for
        # the convergence of meridians. At the equator, 1° lon = 1° lat,
        # but at higher latitudes, longitude degrees are "narrower".
        # Use cosine of the center latitude as correction factor.
        center_lat = (miny + maxy) / 2
        lat_correction = math.cos(math.radians(center_lat))

        # Effective geographic dimensions (in "lat-equivalent" units)
        effective_geo_width = geo_width * lat_correction
        effective_geo_height = geo_height

        # Drawable area
        drawable_width = self.width_px - 2 * self.margin_px
        drawable_height = self.height_px - 2 * self.margin_px

        # Scale to fit (uniform scaling based on effective dimensions)
        scale_x_candidate = drawable_width / effective_geo_width if effective_geo_width > 0 else 1
        scale_y_candidate = drawable_height / effective_geo_height if effective_geo_height > 0 else 1
        base_scale = min(scale_x_candidate, scale_y_candidate)

        # Apply lat correction to x scale
        scale_x = base_scale * lat_correction
        scale_y = base_scale

        # Center in drawable area
        scaled_width = geo_width * scale_x
        scaled_height = geo_height * scale_y

        offset_x = self.margin_px + (drawable_width - scaled_width) / 2 - minx * scale_x
        offset_y = self.margin_px + (drawable_height - scaled_height) / 2 - miny * scale_y

        return scale_x, scale_y, offset_x, offset_y

    def _transform_coords(
        self,
        x: float,
        y: float,
        scale_x: float,
        scale_y: float,
        offset_x: float,
        offset_y: float,
    ) -> tuple[float, float]:
        """Transform geographic coordinates to SVG coordinates."""
        svg_x = x * scale_x + offset_x
        # Flip Y axis (SVG origin is top-left, geo origin is bottom-left)
        svg_y = self.height_px - (y * scale_y + offset_y)
        return svg_x, svg_y

    def _polygon_to_path(
        self,
        poly: Polygon,
        scale_x: float,
        scale_y: float,
        offset_x: float,
        offset_y: float,
    ) -> str | None:
        """Convert a Polygon to SVG path data."""
        if poly.is_empty:
            return None

        coords = list(poly.exterior.coords)
        if not coords:
            return None

        path_parts = []

        # Exterior ring
        x, y = self._transform_coords(coords[0][0], coords[0][1], scale_x, scale_y, offset_x, offset_y)
        path_parts.append(f"M {x:.3f} {y:.3f}")

        for coord in coords[1:]:
            x, y = self._transform_coords(coord[0], coord[1], scale_x, scale_y, offset_x, offset_y)
            path_parts.append(f"L {x:.3f} {y:.3f}")

        path_parts.append("Z")

        # Interior rings (holes)
        for interior in poly.interiors:
            coords = list(interior.coords)
            if coords:
                x, y = self._transform_coords(coords[0][0], coords[0][1], scale_x, scale_y, offset_x, offset_y)
                path_parts.append(f"M {x:.3f} {y:.3f}")
                for coord in coords[1:]:
                    x, y = self._transform_coords(coord[0], coord[1], scale_x, scale_y, offset_x, offset_y)
                    path_parts.append(f"L {x:.3f} {y:.3f}")
                path_parts.append("Z")

        return " ".join(path_parts)

    def _linestring_to_path(
        self,
        line: LineString,
        scale_x: float,
        scale_y: float,
        offset_x: float,
        offset_y: float,
    ) -> str | None:
        """Convert a LineString to SVG path data."""
        if line.is_empty:
            return None

        coords = list(line.coords)
        if not coords:
            return None

        path_parts = []
        x, y = self._transform_coords(coords[0][0], coords[0][1], scale_x, scale_y, offset_x, offset_y)
        path_parts.append(f"M {x:.3f} {y:.3f}")

        for coord in coords[1:]:
            x, y = self._transform_coords(coord[0], coord[1], scale_x, scale_y, offset_x, offset_y)
            path_parts.append(f"L {x:.3f} {y:.3f}")

        return " ".join(path_parts)

    def _geometry_to_paths(
        self,
        geom: Any,
        scale_x: float,
        scale_y: float,
        offset_x: float,
        offset_y: float,
    ) -> list[str]:
        """Convert any Shapely geometry to list of SVG path strings."""
        paths = []

        if isinstance(geom, Polygon):
            path = self._polygon_to_path(geom, scale_x, scale_y, offset_x, offset_y)
            if path:
                paths.append(path)

        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                path = self._polygon_to_path(poly, scale_x, scale_y, offset_x, offset_y)
                if path:
                    paths.append(path)

        elif isinstance(geom, LineString):
            path = self._linestring_to_path(geom, scale_x, scale_y, offset_x, offset_y)
            if path:
                paths.append(path)

        elif isinstance(geom, MultiLineString):
            for line in geom.geoms:
                path = self._linestring_to_path(line, scale_x, scale_y, offset_x, offset_y)
                if path:
                    paths.append(path)

        return paths

    def export_layer(
        self,
        gdf: gpd.GeoDataFrame,
        output_path: str | Path,
        stroke: str = "#000000",
        stroke_width: float = 0.5,
        fill: str = "none",
        bounds: tuple | None = None,
    ) -> None:
        """
        Export a single layer to SVG.

        Args:
            gdf: GeoDataFrame to export
            output_path: Output file path
            stroke: Stroke color (hex)
            stroke_width: Stroke width in points
            fill: Fill color or "none"
            bounds: Optional fixed bounds; if None, uses gdf bounds
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Calculate transform
        if bounds is None:
            bounds = tuple(gdf.total_bounds)
        scale_x, scale_y, offset_x, offset_y = self._calculate_transform(bounds)

        # Build SVG
        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}{self.units}" height="{self.height}{self.units}" '
            f'viewBox="0 0 {self.width_px:.3f} {self.height_px:.3f}">',
        ]

        # Add paths
        for idx, row in enumerate(gdf.itertuples()):
            geom = row.geometry
            paths = self._geometry_to_paths(geom, scale_x, scale_y, offset_x, offset_y)

            # Vary fill color if it's not "none"
            if fill and fill.lower() != "none":
                feature_fill = vary_color(fill, idx)
            else:
                feature_fill = fill

            for path_data in paths:
                svg_parts.append(
                    f'  <path d="{path_data}" '
                    f'stroke="{stroke}" stroke-width="{stroke_width}" '
                    f'fill="{feature_fill}" stroke-linejoin="round" stroke-linecap="round"/>'
                )

        svg_parts.append("</svg>")

        # Write file
        output_path.write_text("\n".join(svg_parts))

    def export_multi_layer(
        self,
        layers: dict[str, tuple[gpd.GeoDataFrame, dict]],
        output_path: str | Path,
        bounds: tuple | None = None,
    ) -> None:
        """
        Export multiple layers to a single SVG with groups.

        Args:
            layers: Dict of {layer_name: (gdf, style_dict)}
                    style_dict should have: stroke, stroke_width, fill
            output_path: Output file path
            bounds: Optional fixed bounds; if None, uses combined bounds
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Calculate bounds from all layers
        if bounds is None:
            all_bounds = []
            for gdf, _ in layers.values():
                if not gdf.empty:
                    all_bounds.append(gdf.total_bounds)

            if all_bounds:
                import numpy as np
                all_bounds = np.array(all_bounds)
                bounds = (
                    all_bounds[:, 0].min(),
                    all_bounds[:, 1].min(),
                    all_bounds[:, 2].max(),
                    all_bounds[:, 3].max(),
                )
            else:
                bounds = (0, 0, 1, 1)

        scale_x, scale_y, offset_x, offset_y = self._calculate_transform(bounds)

        # Build SVG
        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}{self.units}" height="{self.height}{self.units}" '
            f'viewBox="0 0 {self.width_px:.3f} {self.height_px:.3f}">',
        ]

        # Add each layer as a group
        for layer_name, (gdf, style) in layers.items():
            stroke = style.get("stroke", "#000000")
            stroke_width = style.get("stroke_width", 0.5)
            base_fill = style.get("fill", "none")
            vary_fill = style.get("vary_fill", True)  # Default to varying fill colors

            group_id = layer_name.replace(" ", "_").replace("-", "_")
            svg_parts.append(f'  <g id="{group_id}">')

            for idx, row in enumerate(gdf.itertuples()):
                geom = row.geometry
                paths = self._geometry_to_paths(geom, scale_x, scale_y, offset_x, offset_y)

                # Vary fill color if it's not "none"
                if base_fill and base_fill.lower() != "none" and vary_fill:
                    fill = vary_color(base_fill, idx)
                else:
                    fill = base_fill

                for path_data in paths:
                    svg_parts.append(
                        f'    <path d="{path_data}" '
                        f'stroke="{stroke}" stroke-width="{stroke_width}" '
                        f'fill="{fill}" stroke-linejoin="round" stroke-linecap="round"/>'
                    )

            svg_parts.append("  </g>")

        svg_parts.append("</svg>")

        # Write file
        output_path.write_text("\n".join(svg_parts))


def render_svg(
    layers: dict[str, tuple[gpd.GeoDataFrame, dict]],
    output_dir: str | Path,
    page_size: tuple[float, float] = (12, 18),
    margin: float = 0.5,
    units: str = "in",
    per_layer: bool = True,
    combined: bool = True,
    bounds: tuple | None = None,
) -> list[Path]:
    """
    Render layers to SVG files.

    Args:
        layers: Dict of {layer_name: (gdf, style_dict)}
        output_dir: Output directory
        page_size: (width, height) in units
        margin: Page margin in units
        units: "in" or "mm"
        per_layer: Create separate SVG per layer
        combined: Create combined SVG with all layers
        bounds: Fixed bounds or None for auto

    Returns:
        List of created file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    exporter = SVGExporter(
        width=page_size[0],
        height=page_size[1],
        units=units,
        margin=margin,
    )

    created_files = []

    # Calculate combined bounds for consistent scaling
    if bounds is None:
        all_bounds = []
        for gdf, _ in layers.values():
            if not gdf.empty:
                all_bounds.append(gdf.total_bounds)

        if all_bounds:
            import numpy as np
            all_bounds = np.array(all_bounds)
            bounds = (
                all_bounds[:, 0].min(),
                all_bounds[:, 1].min(),
                all_bounds[:, 2].max(),
                all_bounds[:, 3].max(),
            )

    # Export individual layers
    if per_layer:
        for i, (layer_name, (gdf, style)) in enumerate(layers.items(), 1):
            if gdf.empty:
                continue

            filename = f"{i:02d}_{layer_name}.svg"
            filepath = output_dir / filename

            exporter.export_layer(
                gdf,
                filepath,
                stroke=style.get("stroke", "#000000"),
                stroke_width=style.get("stroke_width", 0.5),
                fill=style.get("fill", "none"),
                bounds=bounds,
            )
            created_files.append(filepath)

    # Export combined
    if combined:
        filepath = output_dir / "combined.svg"
        exporter.export_multi_layer(layers, filepath, bounds=bounds)
        created_files.append(filepath)

    return created_files
