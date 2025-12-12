# Strata Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface                               │
├─────────────────┬───────────────────────────────────────────────────┤
│   CLI (cli.py)  │              TUI (tui/app.py)                     │
└────────┬────────┴───────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Orchestration (maury/)                            │
│  ┌──────────────────┐    ┌──────────────────────────────────────┐   │
│  │   Recipe         │    │           Pipeline                    │   │
│  │   (recipe.py)    │───▶│           (pipeline.py)               │   │
│  │   YAML parsing   │    │   prepare → load → process → export   │   │
│  │   Pydantic       │    │                                       │   │
│  └──────────────────┘    └─────────────┬────────────────────────┘   │
└────────────────────────────────────────┼────────────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────┐
         ▼                               ▼                           ▼
┌─────────────────┐         ┌─────────────────────┐      ┌───────────────────┐
│   thoreau/      │         │     humboldt/       │      │     kelley/       │
│   Data Fetch    │         │     Processing      │      │     Output        │
│                 │         │                     │      │                   │
│ • census.py     │         │ • geometry.py       │      │ • svg.py          │
│ • quebec.py     │───────▶ │   subtract, clip,   │─────▶│   SVGExporter     │
│ • canada.py     │ GeoData │   merge, simplify   │ GDF  │                   │
│ • usgs.py       │         │ • projection.py     │      │ • plotter_fill.py │
│ • cache.py      │         │   CRS transforms    │      │   rat-king        │
└─────────────────┘         └─────────────────────┘      └───────────────────┘
         │
         ▼
┌─────────────────┐
│  Local Cache    │
│  ~/.cache/      │
│  strata/        │
└─────────────────┘
```

## Data Flow

### 1. Recipe Loading

```python
# User runs: strata build recipe.strata.yaml
recipe = Recipe.from_file("recipe.strata.yaml")
# → Pydantic validates YAML structure
# → Returns typed Recipe object with sources, layers, output config
```

### 2. Source Fetching (thoreau)

```python
pipeline = Pipeline(recipe)
paths = pipeline.prepare()

# For each source in recipe:
#   1. Check cache (~/.cache/strata/{scheme}/{path})
#   2. If not cached, download from remote
#   3. Extract zip if needed
#   4. For per-county data, merge into single file
#   5. Return local file path
```

### 3. Source Loading

```python
pipeline.load_sources(paths)

# For each source:
#   1. Read file with geopandas (shapefile/geojson)
#   2. Apply bbox filter if output bounds specified
#   3. Apply source-level filters (min_area, attribute matches)
#   4. Store in pipeline.sources dict
```

### 4. Layer Processing (humboldt)

```python
pipeline.process_layers()

# For each layer (sorted by order):
#   1. Get source GeoDataFrame(s)
#   2. Merge if multiple sources
#   3. Apply layer-level bounds/filter
#   4. Apply operations sequentially:
#      - subtract: gdf.difference(target_union)
#      - clip: gdf.clip(bounds)
#      - simplify: gdf.simplify(tolerance)
#      - etc.
#   5. Store in pipeline.layers dict

# Final: clip all layers to output bounds
```

### 5. Export (kelley)

```python
files = pipeline.export(output_dir)

# For SVG format:
#   1. For each quality level:
#      a. Apply quality simplification
#      b. Create SVGExporter with page size
#      c. Export per-layer SVGs (if per_layer: true)
#      d. Export combined.svg (if combined: true)
#      e. Run plotter_fill if enabled:
#         - Extract colors from combined.svg
#         - For each color, create temp SVG
#         - Run rat-king to convert to hatch pattern
#         - Merge all patterns into combined_plotter.svg

# For GeoJSON format:
#   - Write each layer as layer_name.geojson
```

## Module Responsibilities

### strata.thoreau (Data Acquisition)

- **Purpose**: Fetch geodata from authoritative sources
- **Key Pattern**: URI scheme routing (`census:`, `quebec:`, etc.)
- **Caching**: All downloads cached locally by URI path
- **Output**: Returns path to local shapefile/geojson

**Adding a new source provider:**
1. Create `thoreau/newsource.py`
2. Implement `parse_newsource_uri()`, `fetch_newsource()`, `estimate_newsource_size()`
3. Add to `thoreau/__init__.py` routing in `fetch()` and `estimate_size()`

### strata.humboldt (Processing)

- **Purpose**: Geometry transformations
- **Key Pattern**: Operation pipeline (sequential application)
- **Input**: GeoDataFrame
- **Output**: Modified GeoDataFrame

**Adding a new operation:**
1. Add function to `humboldt/geometry.py`
2. Add case in `humboldt/__init__.py:process_layer()`
3. Add to recipe schema if needed

### strata.kelley (Visualization)

- **Purpose**: Render GeoDataFrames to output formats
- **Key Classes**: `SVGExporter`
- **Special Feature**: `plotter_fill` for converting colors to hatch patterns

**SVG rendering flow:**
1. Calculate transform (geo coords → SVG coords)
2. Account for latitude correction (longitude degrees narrower at high lat)
3. Convert geometries to SVG paths
4. Apply styles (stroke, fill, vary_fill)
5. Group by layer in combined output

### strata.maury (Orchestration)

- **Purpose**: Parse recipes, coordinate build
- **Key Classes**: `Recipe`, `Pipeline`
- **Validation**: Pydantic models for type safety

## Key Design Decisions

### 1. Declarative Recipes

Users write YAML, not code. The recipe schema is validated by Pydantic models, providing:
- Type checking at load time
- Clear error messages for invalid configs
- Autocomplete support in editors

### 2. Lazy Fetching with Caching

Data is only downloaded when needed and cached locally. Cache key is the URI path, making it easy to:
- Share cache across recipes
- Manually clear specific datasets
- Avoid re-downloading unchanged data

### 3. Layer Operations as Pipeline

Operations are applied sequentially, which:
- Makes order explicit and predictable
- Allows complex transformations via composition
- Keeps each operation simple and testable

### 4. Plotter-First SVG Output

SVG export is optimized for pen plotters:
- Coordinates transform to page dimensions
- Latitude correction for geographic accuracy
- Optional `plotter_fill` converts colors to distinguishable hatch patterns
- Stroke-only output for single-pen plotting

## Error Handling

| Stage | Error Type | Handling |
|-------|-----------|----------|
| Recipe loading | Pydantic ValidationError | Clear message with field path |
| Source fetch | Network/HTTP errors | Retry with backoff, cache partial |
| Processing | Invalid geometry | `buffer(0)` cleanup, filter empty |
| Export | File I/O | Create directories, clear errors |

## Extension Points

1. **New data sources**: Add to `thoreau/`
2. **New operations**: Add to `humboldt/geometry.py`
3. **New output formats**: Add to `kelley/`, update `pipeline.py:export()`
4. **New CLI commands**: Add to `cli.py`
