# Strata Codebase Overview

## What is Strata?

Strata is a CLI tool for creating **plotter-ready vector maps** from authoritative GIS sources. It bridges the gap between complex geospatial data and clean SVG output suitable for pen plotters.

Users write declarative YAML "recipes" that specify:
1. What data to fetch (sources)
2. How to process it (layers and operations)
3. What to output (SVG, GeoJSON)

## Directory Structure

```
strata/
├── src/strata/           # Main package
│   ├── cli.py            # Click CLI entry point
│   ├── thoreau/          # Data acquisition (fetch from Census, Quebec, etc.)
│   │   ├── census.py     # US Census TIGER data
│   │   ├── quebec.py     # Quebec Open Data
│   │   ├── canada.py     # Canadian CanVec/NHN data
│   │   ├── usgs.py       # USGS National Map services
│   │   ├── naturalearth.py
│   │   ├── openskimap.py
│   │   ├── mexico.py
│   │   └── cache.py      # Local file caching
│   ├── humboldt/         # Processing & transformation
│   │   ├── geometry.py   # subtract, clip, merge, simplify, etc.
│   │   └── projection.py # CRS transformations
│   ├── kelley/           # Visualization & output
│   │   ├── svg.py        # SVG generation for plotters
│   │   └── plotter_fill.py # Color-to-hatch pattern conversion
│   ├── maury/            # Pipeline orchestration
│   │   ├── recipe.py     # YAML recipe parser (Pydantic models)
│   │   └── pipeline.py   # Build orchestration
│   └── tui/              # Textual TUI wizard (interactive recipe creation)
│       ├── app.py
│       └── screens/
├── examples/             # Example .strata.yaml recipes
├── tests/                # pytest test files
├── docs/                 # Documentation
├── bin/                  # Bundled binaries (rat-king)
└── output/               # Default build output directory
```

## Tech Stack

| Category | Libraries |
|----------|-----------|
| CLI | Click |
| TUI | Textual, Rich |
| Config/Validation | Pydantic, PyYAML |
| Geospatial | Shapely, GeoPandas, Fiona, PyProj |
| HTTP | httpx |
| Build System | Hatch |
| Testing | pytest, pytest-cov |

## Module Names (Cartographer Theme)

| Module | Namesake | Role |
|--------|----------|------|
| `thoreau` | Henry David Thoreau | Data acquisition - fetching from remote sources |
| `humboldt` | Alexander von Humboldt | Processing & transformation - geometry operations |
| `kelley` | Florence Kelley | Visualization & output - SVG generation |
| `maury` | Matthew Fontaine Maury | Pipeline orchestration - recipe parsing, build coordination |

## Key CLI Commands

```bash
# Create a new recipe interactively
strata new

# Build a recipe to SVG/GeoJSON
strata build recipe.strata.yaml

# Preview bounds and feature counts
strata preview recipe.strata.yaml --open

# Validate a recipe
strata validate recipe.strata.yaml

# Prepare (download) sources without building
strata prepare recipe.strata.yaml --dry-run

# Convert colored SVG to plotter-ready hatch patterns
strata plotter-fill combined.svg

# Cache management
strata cache list
strata cache clear --all
```

## Development Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=strata

# Type checking
mypy src/strata

# Linting
ruff check src/

# Run the CLI
python -m strata.cli build examples/champlain.strata.yaml
```

## Data Source Providers

Strata can fetch from these authoritative sources:

| Provider | URI Prefix | Data Types |
|----------|------------|------------|
| US Census TIGER | `census:` | Towns, water, roads, boundaries |
| Quebec Open Data | `quebec:` | Municipalities, highways |
| Canadian CanVec/NHN | `canada:` | Hydrology, roads, boundaries |
| USGS National Map | `usgs:` | Elevation, hydrology (WFS services) |
| Natural Earth | `naturalearth:` | Country/state boundaries |
| OpenSkiMap | `openskimap:` | Ski runs, lifts |
| Mexico INEGI | `mexico:` | Administrative boundaries |
| Local files | `file:` | Any GeoJSON/Shapefile |

## Output Formats

| Format | Use Case |
|--------|----------|
| SVG | Pen plotter output (with optional plotter_fill for hatch patterns) |
| GeoJSON | Web viewing, further processing |
| PMTiles | Serverless web maps (planned) |

## Key Concepts

1. **Recipe**: A YAML file defining sources, layers, and output options
2. **Source**: A data provider URI that resolves to geodata (e.g., `census:tiger/2023/vt/cousub`)
3. **Layer**: A processed view of one or more sources with styling
4. **Operation**: A geometry transformation (subtract, clip, simplify, etc.)
5. **Quality Level**: Simplification tolerance for different output detail levels

## External Dependencies

- **rat-king**: Rust CLI for converting SVG polygon fills to hatch patterns (bundled in `bin/`)
