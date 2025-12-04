"""
Pipeline orchestration for strata build process.
"""

from pathlib import Path
from typing import Any

import geopandas as gpd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from strata.maury.recipe import Recipe
from strata import thoreau
from strata import humboldt
from strata import kelley

console = Console()


class Pipeline:
    """
    Orchestrates the strata build process.

    prepare() -> downloads/caches all source data
    build() -> processes layers and exports outputs
    """

    def __init__(self, recipe: Recipe):
        self.recipe = recipe
        self.sources: dict[str, gpd.GeoDataFrame] = {}
        self.layers: dict[str, gpd.GeoDataFrame] = {}

    def estimate(self) -> dict:
        """
        Estimate download sizes without downloading.

        Returns:
            Dict with total_size_mb, sources list, cached count
        """
        estimates = []
        total_mb = 0
        cached_count = 0

        for name, source_config in self.recipe.sources.items():
            uri = source_config.uri
            est = thoreau.estimate_size(uri)
            est["name"] = name
            estimates.append(est)

            if est.get("cached"):
                cached_count += 1
            else:
                total_mb += est.get("estimated_size_mb", 0)

        return {
            "sources": estimates,
            "total_size_mb": total_mb,
            "cached_count": cached_count,
            "download_count": len(estimates) - cached_count,
        }

    def prepare(self, force: bool = False) -> dict[str, str]:
        """
        Download and cache all source data.

        Args:
            force: Re-download even if cached

        Returns:
            Dict of {source_name: local_path}
        """
        console.print("\n[bold]Fetching sources:[/]")

        paths = {}
        for name, source_config in self.recipe.sources.items():
            uri = source_config.uri
            try:
                path = thoreau.fetch(uri, force=force)
                paths[name] = path
            except NotImplementedError as e:
                console.print(f"  [yellow]![/] {name}: {e}")
            except Exception as e:
                console.print(f"  [red]✗[/] {name}: {e}")
                raise

        return paths

    def load_sources(self, paths: dict[str, str]) -> None:
        """
        Load source data into GeoDataFrames.

        Args:
            paths: Dict of {source_name: local_path}
        """
        console.print("\n[bold]Loading sources:[/]")

        # Get bounds for early spatial filtering if specified
        bounds_config = self.recipe.output.bounds
        bbox = None
        if isinstance(bounds_config, list) and len(bounds_config) == 4:
            bbox = tuple(bounds_config)

        for name, path in paths.items():
            console.print(f"  Loading {name}...")

            # Use bbox parameter to filter on load (reduces memory for large datasets)
            if bbox:
                gdf = gpd.read_file(path, bbox=bbox)
            else:
                gdf = gpd.read_file(path)

            # Apply filters if specified
            source_config = self.recipe.sources.get(name)
            if source_config and source_config.filter:
                gdf = self._apply_filter(gdf, source_config.filter)

            self.sources[name] = gdf
            console.print(f"  [green]✓[/] {name}: {len(gdf)} features")

    def _apply_filter(
        self,
        gdf: gpd.GeoDataFrame,
        filter_config: dict[str, Any],
    ) -> gpd.GeoDataFrame:
        """
        Apply filter configuration to a GeoDataFrame.

        Supported filter types:
        - min_area_km2: Minimum area in square kilometers
        - max_area_km2: Maximum area in square kilometers
        - {column}: Direct column match (exact match or list of values)
        - {column}_contains: Substring match (case-insensitive)
        - {column}_in: List of values to match

        Examples:
            filter:
              HYDROID: "110469638395"           # Exact match
              MTFCC: ["S1100", "S1200"]         # Match any in list
              FULLNAME_contains: "Champlain"   # Substring match
              RTTYP: "I"                        # Interstate roads only
        """
        result = gdf
        original_count = len(result)

        for key, value in filter_config.items():
            if key == "min_area_km2":
                # Filter by minimum area
                temp = result.to_crs("epsg:6933")  # Equal area projection
                area_km2 = temp.geometry.area / 1e6
                result = result[area_km2 >= value]

            elif key == "max_area_km2":
                temp = result.to_crs("epsg:6933")
                area_km2 = temp.geometry.area / 1e6
                result = result[area_km2 <= value]

            elif key.endswith("_contains"):
                # Substring match (case-insensitive)
                column = key[:-9]  # Remove "_contains" suffix
                if column in result.columns:
                    result = result[
                        result[column].str.contains(value, case=False, na=False)
                    ]

            elif key.endswith("_in"):
                # Explicit list match
                column = key[:-3]  # Remove "_in" suffix
                if column in result.columns:
                    values = value if isinstance(value, list) else [value]
                    result = result[result[column].isin(values)]

            elif key == "counties":
                # Filter by county names (for TIGER data)
                if "NAMELSAD" in result.columns:
                    # County subdivisions have NAMELSAD
                    pass  # TODO: Need county info for filtering
                elif "COUNTYFP" in result.columns:
                    # Would need county name lookup
                    pass

            elif key in result.columns:
                # Direct column filter (exact match or list)
                if isinstance(value, list):
                    result = result[result[key].isin(value)]
                else:
                    result = result[result[key] == value]

        # Log filtering result if significant reduction
        if len(result) < original_count:
            console.print(
                f"    [dim]Filtered: {original_count} → {len(result)} features[/]"
            )

        return result

    def process_layers(self) -> None:
        """Process all layers according to recipe operations."""
        console.print("\n[bold]Processing layers:[/]")

        # Sort layers by order
        sorted_layers = sorted(self.recipe.layers, key=lambda x: x.order)

        for layer_config in sorted_layers:
            name = layer_config.name
            console.print(f"  Processing {name}...")

            # Get source GeoDataFrames
            source_names = layer_config.source
            if isinstance(source_names, str):
                source_names = [source_names]

            # Combine sources
            source_gdfs = []
            for src_name in source_names:
                if src_name in self.sources:
                    source_gdfs.append(self.sources[src_name])

            if not source_gdfs:
                console.print(f"  [yellow]![/] {name}: No sources found")
                continue

            # Concatenate if multiple sources
            if len(source_gdfs) == 1:
                gdf = source_gdfs[0].copy()
            else:
                import pandas as pd
                # Normalize CRS before concatenating (US=NAD83, Canada=NAD83(CSRS))
                # Use WGS84 (EPSG:4326) as common CRS for merging
                target_crs = "EPSG:4326"
                normalized_gdfs = []
                for src_gdf in source_gdfs:
                    if src_gdf.crs and src_gdf.crs != target_crs:
                        normalized_gdfs.append(src_gdf.to_crs(target_crs))
                    else:
                        normalized_gdfs.append(src_gdf)
                gdf = gpd.GeoDataFrame(
                    pd.concat(normalized_gdfs, ignore_index=True),
                    crs=target_crs,
                )

            # Apply layer-level bounds clipping if specified
            if layer_config.bounds and len(layer_config.bounds) == 4:
                from shapely.geometry import box
                original_count = len(gdf)
                clip_box = box(*layer_config.bounds)
                gdf = gdf.clip(clip_box)
                gdf = gdf[~gdf.geometry.is_empty]
                console.print(
                    f"    [dim]Clipped to bounds: {original_count} → {len(gdf)} features[/]"
                )

            # Apply layer-level filter if specified
            if layer_config.filter:
                original_count = len(gdf)
                gdf = self._apply_filter(gdf, layer_config.filter)
                if len(gdf) < original_count:
                    console.print(
                        f"    [dim]Filtered: {original_count} → {len(gdf)} features[/]"
                    )

            # Apply operations
            operations = [op.model_dump() for op in layer_config.operations]
            if operations:
                gdf = humboldt.process_layer(gdf, operations, self.sources)

            self.layers[name] = gdf
            console.print(f"  [green]✓[/] {name}: {len(gdf)} features")

        # Clip all layers to output bounds if specified
        self._clip_to_bounds()

    def _clip_to_bounds(self) -> None:
        """Clip all layers to the output bounds if explicitly specified."""
        bounds_config = self.recipe.output.bounds

        # Only clip if bounds are explicitly specified (not "auto")
        if bounds_config == "auto" or bounds_config is None:
            return

        if isinstance(bounds_config, list) and len(bounds_config) == 4:
            from shapely.geometry import box
            clip_box = box(*bounds_config)

            console.print(f"\n[bold]Clipping to bounds:[/] {bounds_config}")

            for name, gdf in self.layers.items():
                original_count = len(gdf)
                # Clip geometries to the bounding box
                clipped = gdf.clip(clip_box)
                # Remove empty geometries
                clipped = clipped[~clipped.geometry.is_empty]
                self.layers[name] = clipped
                console.print(f"  {name}: {original_count} → {len(clipped)} features")

    def export(self, output_dir: str | Path) -> list[Path]:
        """
        Export processed layers to output formats.

        Args:
            output_dir: Base output directory

        Returns:
            List of created file paths
        """
        output_dir = Path(output_dir) / self.recipe.name
        output_dir.mkdir(parents=True, exist_ok=True)

        created_files = []

        console.print("\n[bold]Rendering outputs:[/]")

        for format_config in self.recipe.output.formats:
            fmt_type = format_config.type

            if fmt_type == "svg":
                files = self._export_svg(output_dir, format_config)
                created_files.extend(files)

            elif fmt_type == "geojson":
                files = self._export_geojson(output_dir, format_config)
                created_files.extend(files)

            elif fmt_type == "pmtiles":
                console.print("  [yellow]![/] PMTiles export not yet implemented")

        return created_files

    def _export_svg(self, output_dir: Path, format_config) -> list[Path]:
        """Export layers to SVG format."""
        created = []

        # Get output options
        options = format_config.options
        if options is None:
            from strata.maury.recipe import SVGOptions
            options = SVGOptions()

        page_size = tuple(options.page_size)
        margin = options.margin
        per_layer = options.per_layer
        combined = options.combined

        # Get quality levels
        qualities = format_config.quality or []
        if not qualities:
            # Default single quality
            qualities = [{"name": "default", "simplify": 0.0001}]

        # Calculate bounds
        bounds = self._get_output_bounds()

        # Sort layers by order
        sorted_layer_configs = sorted(self.recipe.layers, key=lambda x: x.order)

        for quality in qualities:
            q_name = quality.name if hasattr(quality, "name") else quality.get("name", "default")
            q_simplify = quality.simplify if hasattr(quality, "simplify") else quality.get("simplify", 0.0001)

            svg_dir = output_dir / "svg" / q_name
            console.print(f"  Exporting SVG ({q_name})...")

            # Prepare layers with styles
            layers_dict = {}
            for layer_config in sorted_layer_configs:
                name = layer_config.name
                if name not in self.layers:
                    continue

                gdf = self.layers[name].copy()

                # Apply quality-level simplification
                if q_simplify > 0:
                    gdf = humboldt.simplify(gdf, q_simplify)

                style = {
                    "stroke": layer_config.style.stroke,
                    "stroke_width": layer_config.style.stroke_width,
                    "fill": layer_config.style.fill or "none",
                }

                layers_dict[name] = (gdf, style)

            # Render
            files = kelley.render_svg(
                layers_dict,
                svg_dir,
                page_size=page_size,
                margin=margin,
                units="in",
                per_layer=per_layer,
                combined=combined,
                bounds=bounds,
            )
            created.extend(files)
            console.print(f"  [green]✓[/] SVG ({q_name}): {len(files)} files")

        return created

    def _export_geojson(self, output_dir: Path, format_config) -> list[Path]:
        """Export layers to GeoJSON format."""
        created = []

        geojson_dir = output_dir / "geojson"
        geojson_dir.mkdir(parents=True, exist_ok=True)

        console.print("  Exporting GeoJSON...")

        for name, gdf in self.layers.items():
            filepath = geojson_dir / f"{name}.geojson"
            gdf.to_file(filepath, driver="GeoJSON")
            created.append(filepath)

        console.print(f"  [green]✓[/] GeoJSON: {len(created)} files")
        return created

    def _get_output_bounds(self) -> tuple | None:
        """Calculate output bounds from recipe config."""
        bounds_config = self.recipe.output.bounds

        if bounds_config == "auto":
            # Calculate from all layers
            all_bounds = []
            for gdf in self.layers.values():
                if not gdf.empty:
                    all_bounds.append(gdf.total_bounds)

            if all_bounds:
                import numpy as np
                all_bounds = np.array(all_bounds)
                return (
                    all_bounds[:, 0].min(),
                    all_bounds[:, 1].min(),
                    all_bounds[:, 2].max(),
                    all_bounds[:, 3].max(),
                )
            return None

        elif isinstance(bounds_config, list):
            return tuple(bounds_config)

        elif isinstance(bounds_config, str) and bounds_config.startswith("source:"):
            source_name = bounds_config[7:]
            if source_name in self.sources:
                return tuple(self.sources[source_name].total_bounds)
            return None

        return None

    def build(self, output_dir: str | Path, force: bool = False) -> list[Path]:
        """
        Run the full build pipeline.

        Args:
            output_dir: Output directory
            force: Force re-download of sources

        Returns:
            List of created file paths
        """
        # 1. Prepare (download sources)
        paths = self.prepare(force=force)

        # 2. Load sources
        self.load_sources(paths)

        # 3. Process layers
        self.process_layers()

        # 4. Export
        return self.export(output_dir)
