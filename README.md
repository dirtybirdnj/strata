# Strata

> "The same strata were found always in the same order of superposition and contained the same peculiar fossils." — William Smith

**Strata** is a CLI tool for creating plotter-ready vector maps from authoritative GIS sources. It bridges the gap between complex geospatial data and clean SVG output suitable for pen plotters.

## The Problem

Creating maps for pen plotters requires:
1. Fetching data from multiple authoritative sources (Census TIGER, CanVec, etc.)
2. Processing geometry (water cutouts, island detection, simplification)
3. Ordering layers correctly (the "layer sandwich")
4. Exporting clean vectors optimized for physical drawing

Existing GIS tools (QGIS, ArcGIS, PostGIS) require significant expertise and produce output optimized for screens, not plotters.

## The Solution

Strata lets you write **declarative recipes** in YAML:

```yaml
name: champlain_region

sources:
  vt_towns: census:tiger/2023/vt/cousub
  lake: census:tiger/2023/vt/areawater

layers:
  - name: towns
    source: vt_towns
    operations:
      - type: subtract
        target: lake
    order: 1

output:
  formats:
    - type: svg
      quality: [fine, medium]
      optimize_for: plotter
```

Then build:

```bash
strata build champlain.strata.yaml
```

## Features

- **Recipe-based** — YAML files define what you want, not how to get it
- **Interactive wizard** — TUI for creating recipes without writing YAML
- **Multi-source** — Fetch from Census TIGER, CanVec, Quebec Open Data, and more
- **Cartographic operations** — Water cutouts, island detection, layer stacking
- **Plotter-optimized** — SVG output with stroke deduplication and travel optimization
- **Multiple outputs** — SVG, GeoJSON, PMTiles from the same recipe

## Installation

```bash
pip install strata
```

## Quick Start

```bash
# Create a new recipe interactively
strata new

# Or build an existing recipe
strata build my-map.strata.yaml

# Preview what a recipe will produce
strata preview my-map.strata.yaml

# Validate a recipe
strata validate my-map.strata.yaml
```

## Documentation

- [Architecture](./docs/ARCHITECTURE.md) — How Strata is structured
- [YAML Schema](./docs/YAML_SCHEMA.md) — Complete recipe format reference
- [CLI Reference](./docs/CLI.md) — All commands and options
- [TUI Guide](./docs/TUI.md) — Using the interactive wizard
- [Branding](./docs/BRANDING.md) — The cartographers behind the module names

## Module Names

Strata's modules are named after historical cartographers:

| Module | Namesake | Role |
|--------|----------|------|
| `thoreau` | Henry David Thoreau | Data acquisition |
| `humboldt` | Alexander von Humboldt | Processing & transformation |
| `kelley` | Florence Kelley | Visualization & output |
| `maury` | Matthew Fontaine Maury | Pipeline orchestration |

The package itself is named after **William Smith**, who created the first geological map and discovered that rock layers (strata) could be identified by their contents.

## Related Projects

- [vt-geodata](https://github.com/dirtybirdnj/vt-geodata) — Vermont maps built with Strata (the first "customer")
- [vpype](https://github.com/abey79/vpype) — Plotter optimization (pairs well with Strata SVG output)
- [Textual](https://github.com/Textualize/textual) — Powers the TUI wizard

## License

MIT
