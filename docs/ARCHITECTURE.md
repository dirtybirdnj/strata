# Strata Architecture

> "Organized fossils are to the naturalist as coins to the antiquary; they are the antiquities of the earth." — William Smith

## Overview

Strata is a CLI tool for creating plotter-ready vector maps from authoritative GIS sources. It bridges the gap between complex geospatial data and clean SVG output suitable for pen plotters.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sources   │ ──▶ │  Processing │ ──▶ │   Output    │ ──▶ │  Plotter    │
│  (thoreau)  │     │  (humboldt) │     │  (kelley)   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                            ▲
                            │
                    ┌───────┴───────┐
                    │ Orchestration │
                    │    (maury)    │
                    └───────────────┘
```

## Core Principles

1. **Recipes over code** — Users write YAML, not Python
2. **Vector-first** — Output is optimized for pen plotters, not screens
3. **Authoritative sources** — Fetch from Census, CanVec, Quebec Open Data
4. **Cartographic knowledge encoded** — Water cutouts, island detection, layer ordering
5. **No server required** — Everything runs locally, outputs static files

## Module Structure

```
strata/
├── __init__.py              # Package entry, version
├── cli.py                   # Click CLI commands
├── tui/                     # Textual wizard interface
│   ├── __init__.py
│   ├── app.py               # Main TUI application
│   ├── screens/
│   │   ├── welcome.py
│   │   ├── sources.py
│   │   ├── layers.py
│   │   ├── output.py
│   │   └── debug.py         # Config error debugger
│   └── widgets/
│       └── ...
├── thoreau/                 # Data acquisition
│   ├── __init__.py
│   ├── census.py            # US Census TIGER data
│   ├── canvec.py            # Canadian CanVec data
│   ├── quebec.py            # Quebec Open Data
│   ├── cache.py             # Local file caching
│   └── validate.py          # Source validation
├── humboldt/                # Processing & transformation
│   ├── __init__.py
│   ├── geometry.py          # ST_Difference, ST_Union, etc.
│   ├── cutouts.py           # Water cutout operations
│   ├── islands.py           # Island detection
│   ├── simplify.py          # Topology simplification
│   └── projection.py        # CRS transformations
├── kelley/                  # Visualization & output
│   ├── __init__.py
│   ├── svg.py               # SVG generation
│   ├── geojson.py           # GeoJSON export
│   ├── pmtiles.py           # PMTiles generation
│   ├── colors.py            # Color schemes
│   └── optimize.py          # Plotter optimization (stroke dedup, travel)
├── maury/                   # Pipeline orchestration
│   ├── __init__.py
│   ├── recipe.py            # YAML recipe parser
│   ├── pipeline.py          # Build orchestration
│   ├── layers.py            # Layer stacking logic
│   └── schema.py            # Pydantic models for validation
└── data/
    └── sources.yaml         # Registry of known data sources
```

## Data Flow

### 1. Recipe Loading (maury)

```python
recipe = Recipe.from_file("champlain.strata.yaml")
# Validates against schema
# Resolves source URIs
# Builds dependency graph
```

### 2. Source Fetching (thoreau)

```python
for source in recipe.sources:
    data = thoreau.fetch(source.uri)
    # Downloads if not cached
    # Validates geometry
    # Stores in local cache
```

### 3. Processing (humboldt)

```python
for layer in recipe.layers:
    geometry = humboldt.process(
        source=layer.source,
        operations=layer.operations  # subtract, clip, merge, etc.
    )
```

### 4. Output (kelley)

```python
for format in recipe.output.formats:
    kelley.render(
        layers=processed_layers,
        format=format,  # svg, geojson, pmtiles
        options=format.options
    )
```

## Key Abstractions

### Source URI Scheme

```
census:tiger/2023/vt/cousub      # US Census TIGER
canvec:hydro/waterbody           # Canadian CanVec
quebec:municipalities            # Quebec Open Data
file:./local/data.geojson        # Local file
url:https://example.com/data.json # Remote URL
```

### Layer Operations

```yaml
layers:
  - name: towns
    source: vt_towns
    operations:
      - type: subtract
        target: lake_champlain
      - type: simplify
        tolerance: 0.001
      - type: clip
        bounds: [-73.5, 42.7, -71.5, 45.2]
```

### Output Formats

```yaml
output:
  formats:
    - type: svg
      quality: [ultra_fine, fine, medium]
      optimize_for: plotter

    - type: geojson
      per_layer: true

    - type: pmtiles
      minzoom: 4
      maxzoom: 12
```

## Dependencies

### Core
- **click** — CLI framework
- **textual** — TUI wizard
- **rich** — Pretty terminal output
- **pydantic** — YAML schema validation
- **pyyaml** — YAML parsing

### Geospatial
- **shapely** — Geometry operations
- **pyproj** — Coordinate transformations
- **fiona** — Reading/writing geo formats
- **geopandas** — GeoDataFrame operations

### Optional
- **duckdb** — SQL queries on local data (future)
- **tippecanoe** — PMTiles generation (external binary)
- **vpype** — Plotter optimization (external)

## Configuration

### User Config (`~/.config/strata/config.yaml`)

```yaml
cache_dir: ~/.cache/strata
default_projection: epsg:4326
editor: $EDITOR
census_api_key: optional_for_higher_limits
```

### Source Registry (`data/sources.yaml`)

```yaml
census:
  base_url: https://www2.census.gov/geo/tiger
  types:
    cousub: County Subdivisions (towns)
    areawater: Water bodies
    prisecroads: Primary/secondary roads

canvec:
  base_url: https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/canvec
  types:
    hydro/waterbody: Lakes and ponds
    transport/road: Roads

quebec:
  base_url: https://www.donneesquebec.ca
  types:
    municipalities: Municipal boundaries
    highways: Provincial highways
```

## Error Handling

The TUI includes an interactive debugger for malformed configs:

1. **Schema validation** — Pydantic catches type errors, missing fields
2. **Source validation** — thoreau verifies URIs resolve
3. **Geometry validation** — humboldt checks for invalid geometries
4. **Suggestions** — Fuzzy matching for typos ("styel" → "style")

## Future Considerations

- **DuckDB integration** — SQL queries against cached sources
- **FlatGeobuf output** — Cloud-native format with spatial indexing
- **Recipe inheritance** — Base recipes that others extend
- **Plugin system** — Custom sources and operations
- **Web preview** — Optional `strata preview` with browser map (Leaflet)
