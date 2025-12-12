# Strata API Reference

## Module: strata.thoreau (Data Acquisition)

### Main Entry Point

```python
# src/strata/thoreau/__init__.py:55
def fetch(uri: str, force: bool = False, bbox: tuple | None = None) -> str:
    """
    Fetch data from a source URI and return the local path.

    Args:
        uri: Source URI (e.g., "census:tiger/2023/vt/cousub")
        force: Re-download even if cached
        bbox: Bounding box for spatial queries (required for usgs: sources)

    Returns:
        Path to local data file (shapefile or geojson)

    Raises:
        ValueError: If URI scheme is not recognized
        FileNotFoundError: If local file doesn't exist

    Supported URI schemes:
        census:, canada:, quebec:, openskimap:, mexico:,
        naturalearth:, usgs:, woodland:, file:
    """
```

```python
# src/strata/thoreau/__init__.py:111
def estimate_size(uri: str) -> dict:
    """
    Estimate download size for a URI without downloading.

    Returns:
        Dict with keys: uri, estimated_size_mb, cached, cache_path, url
    """
```

### Cache Functions

```python
# src/strata/thoreau/cache.py:10
def get_cache_dir() -> Path:
    """Get the strata cache directory (~/.cache/strata/)."""

# src/strata/thoreau/cache.py:17
def get_cached_path(uri: str) -> Path:
    """Get the cache path for a given URI."""

# src/strata/thoreau/cache.py:42
def is_cached(uri: str) -> bool:
    """Check if data for a URI is already cached."""

# src/strata/thoreau/cache.py:64
def clear_cache(uri: str | None = None) -> None:
    """Clear cached data. Pass None to clear all."""
```

### Census TIGER Functions

```python
# src/strata/thoreau/census.py:150
def parse_census_uri(uri: str) -> dict:
    """
    Parse a census URI into components.

    Args:
        uri: "census:tiger/2023/vt/cousub"

    Returns:
        Dict with: year, state, type, fips, url, urls, per_county,
                   national, estimated_size_mb
    """

# src/strata/thoreau/census.py:288
def fetch_census(uri: str, force: bool = False) -> str:
    """
    Fetch Census TIGER data and return path to shapefile.
    Handles per-county merging automatically.
    """
```

---

## Module: strata.humboldt (Processing)

### Main Entry Point

```python
# src/strata/humboldt/__init__.py:28
def process_layer(
    gdf: GeoDataFrame,
    operations: list[dict],
    sources: dict[str, GeoDataFrame],
) -> GeoDataFrame:
    """
    Apply a sequence of operations to a GeoDataFrame.

    Args:
        gdf: Input GeoDataFrame
        operations: List of operation configs from recipe
        sources: Dict of loaded source GeoDataFrames (for operation targets)

    Supported operation types:
        subtract, clip, simplify, merge, buffer, exclude,
        extract_islands, remove_holes, dissolve, clean, merge_touching
    """
```

### Geometry Functions

```python
# src/strata/humboldt/geometry.py:10
def subtract(gdf: GeoDataFrame, subtract_gdf: GeoDataFrame) -> GeoDataFrame:
    """
    Subtract geometry of one GeoDataFrame from another.
    Used for water cutouts - removing lake geometry from town boundaries.
    """

# src/strata/humboldt/geometry.py:43
def clip(gdf: GeoDataFrame, bounds: tuple | list) -> GeoDataFrame:
    """Clip GeoDataFrame to bounding box (minx, miny, maxx, maxy)."""

# src/strata/humboldt/geometry.py:83
def merge(gdf: GeoDataFrame) -> GeoDataFrame:
    """Merge all features into a single geometry."""

# src/strata/humboldt/geometry.py:100
def simplify(
    gdf: GeoDataFrame,
    tolerance: float,
    preserve_topology: bool = True,
) -> GeoDataFrame:
    """
    Simplify geometries to reduce complexity.
    Higher tolerance = more simplified.
    """

# src/strata/humboldt/geometry.py:124
def buffer(gdf: GeoDataFrame, distance: float) -> GeoDataFrame:
    """Buffer geometries. Positive = expand, negative = contract."""

# src/strata/humboldt/geometry.py:145
def extract_islands(gdf: GeoDataFrame, min_area: float = 0.0) -> GeoDataFrame:
    """
    Extract islands (interior rings/holes) from polygon geometries.
    Water bodies have holes where islands exist.
    """

# src/strata/humboldt/geometry.py:206
def dissolve_by(gdf: GeoDataFrame, column: str) -> GeoDataFrame:
    """
    Dissolve (merge) geometries sharing the same attribute value.
    Essential for water bodies spanning multiple counties (by HYDROID).
    """

# src/strata/humboldt/geometry.py:232
def merge_touching(
    gdf: GeoDataFrame,
    buffer_distance: float = 0.0001,
) -> GeoDataFrame:
    """
    Merge features whose geometries touch or overlap.
    For cross-border features like Lake Memphremagog.
    """

# src/strata/humboldt/geometry.py:312
def clean_geometry(
    gdf: GeoDataFrame,
    buffer_distance: float = 0.0,
) -> GeoDataFrame:
    """Fix topology issues using buffer(0) trick."""

# src/strata/humboldt/geometry.py:346
def remove_holes(
    gdf: GeoDataFrame,
    min_hole_area: float = 0.0,
) -> GeoDataFrame:
    """Remove interior rings (holes) from polygons."""
```

---

## Module: strata.kelley (Visualization)

### SVG Export

```python
# src/strata/kelley/svg.py:602
def render_svg(
    layers: dict[str, tuple[GeoDataFrame, dict]],
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
                style_dict: {stroke, stroke_width, fill, vary_fill, ...}
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
```

### SVGExporter Class

```python
# src/strata/kelley/svg.py:125
class SVGExporter:
    """Export GeoDataFrames to SVG optimized for pen plotters."""

    def __init__(
        self,
        width: float = 12,
        height: float = 18,
        units: str = "in",
        margin: float = 0.5,
        dpi: float = 96,
    ):
        """Initialize with page size."""

    def export_layer(
        self,
        gdf: GeoDataFrame,
        output_path: str | Path,
        stroke: str = "#000000",
        stroke_width: float = 0.5,
        fill: str = "none",
        bounds: tuple | None = None,
        style: dict | None = None,
    ) -> None:
        """Export a single layer to SVG."""

    def export_multi_layer(
        self,
        layers: dict[str, tuple[GeoDataFrame, dict]],
        output_path: str | Path,
        bounds: tuple | None = None,
    ) -> None:
        """Export multiple layers to a single SVG with groups."""
```

### Plotter Fill (Color to Hatch Conversion)

```python
# src/strata/kelley/plotter_fill.py:300
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

    Takes SVG with colored polygons and converts each color to a
    unique hatch pattern using rat-king CLI.

    Returns:
        True if successful, False otherwise
    """

# src/strata/kelley/plotter_fill.py:74
def check_rat_king_available(bin_path: str = RAT_KING_BIN) -> bool:
    """Check if rat-king CLI is available."""
```

---

## Module: strata.maury (Orchestration)

### Recipe Class

```python
# src/strata/maury/recipe.py:138
class Recipe(BaseModel):
    """A complete Strata recipe."""

    name: str
    description: str = ""
    version: int = 1
    sources: dict[str, SourceConfig]
    layers: list[LayerConfig]
    output: OutputConfig

    @classmethod
    def from_file(cls, path: str | Path) -> "Recipe":
        """Load a recipe from a YAML file."""

    @classmethod
    def from_yaml(cls, yaml_string: str) -> "Recipe":
        """Load a recipe from a YAML string."""

    def to_yaml(self) -> str:
        """Export recipe as YAML."""

    def validate_references(self) -> list[str]:
        """Check that all source references in layers are valid."""
```

### Pipeline Class

```python
# src/strata/maury/pipeline.py:20
class Pipeline:
    """Orchestrates the strata build process."""

    def __init__(self, recipe: Recipe):
        self.recipe = recipe
        self.sources: dict[str, GeoDataFrame] = {}
        self.layers: dict[str, GeoDataFrame] = {}

    def estimate(self) -> dict:
        """Estimate download sizes without downloading."""

    def prepare(self, force: bool = False) -> dict[str, str]:
        """
        Download and cache all source data.
        Returns: Dict of {source_name: local_path}
        """

    def load_sources(self, paths: dict[str, str]) -> None:
        """Load source data into GeoDataFrames."""

    def process_layers(self) -> None:
        """Process all layers according to recipe operations."""

    def export(self, output_dir: str | Path) -> list[Path]:
        """Export processed layers to output formats."""

    def build(self, output_dir: str | Path, force: bool = False) -> list[Path]:
        """
        Run the full build pipeline:
        1. prepare() - download sources
        2. load_sources() - load into GeoDataFrames
        3. process_layers() - apply operations
        4. export() - write output files
        """
```

---

## Pydantic Config Models

```python
# src/strata/maury/recipe.py

class SourceConfig(BaseModel):
    uri: str
    description: str | None = None
    filter: dict[str, Any] | None = None
    clip_to: str | None = None

class OperationConfig(BaseModel):
    type: str  # subtract, clip, simplify, merge, buffer, etc.
    target: str | list[str] | None = None
    tolerance: float | None = None
    preserve_topology: bool = True
    min_area_km2: float | None = None
    output: str | None = None
    distance: float | None = None

class StyleConfig(BaseModel):
    stroke: str = "#333333"
    stroke_width: float = 1.0
    fill: str | None = None
    fill_by: str | None = None      # Column name for color mapping
    color_map: dict[str, str] | None = None
    vary_fill: bool = True
    opacity: float = 1.0
    dash_array: list[float] | None = None
    marker: str = "circle"          # For points
    marker_size: float = 6.0

class LayerConfig(BaseModel):
    name: str
    source: str | list[str]
    bounds: list[float] | None = None
    filter: dict[str, Any] | None = None
    operations: list[OperationConfig] = []
    style: StyleConfig = StyleConfig()
    order: int

class OutputConfig(BaseModel):
    bounds: list[float] | str = "auto"  # [w, s, e, n] or "auto"
    projection: str = "epsg:4326"
    formats: list[FormatConfig]

class PlotterFillConfig(BaseModel):
    enabled: bool = True
    spacing: float = 3.0
    stroke_width: float = 0.5
    include_outlines: bool = True
    rat_king_bin: str | None = None
```
