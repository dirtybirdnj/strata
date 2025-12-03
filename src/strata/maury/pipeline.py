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

        for name, path in paths.items():
            console.print(f"  Loading {name}...")
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
        """Apply filter configuration to a GeoDataFrame."""
        result = gdf

        for key, value in filter_config.items():
            if key == "min_area_km2":
                # Filter by minimum area
                # Convert to equal area projection for accurate area calc
                temp = result.to_crs("epsg:6933")  # Equal area projection
                area_km2 = temp.geometry.area / 1e6
                result = result[area_km2 >= value]

            elif key == "max_area_km2":
                temp = result.to_crs("epsg:6933")
                area_km2 = temp.geometry.area / 1e6
                result = result[area_km2 <= value]

            elif key == "counties":
                # Filter by county names (for TIGER data)
                if "NAMELSAD" in result.columns:
                    # County subdivisions have NAMELSAD
                    pass  # TODO: Need county info for filtering
                elif "COUNTYFP" in result.columns:
                    # Would need county name lookup
                    pass

            elif key in result.columns:
                # Direct column filter
                if isinstance(value, list):
                    result = result[result[key].isin(value)]
                else:
                    result = result[result[key] == value]

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
                gdf = gpd.GeoDataFrame(
                    pd.concat(source_gdfs, ignore_index=True),
                    crs=source_gdfs[0].crs,
                )

            # Apply operations
            operations = [op.model_dump() for op in layer_config.operations]
            if operations:
                gdf = humboldt.process_layer(gdf, operations, self.sources)

            self.layers[name] = gdf
            console.print(f"  [green]✓[/] {name}: {len(gdf)} features")

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
