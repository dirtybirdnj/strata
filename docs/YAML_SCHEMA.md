# Strata Recipe YAML Schema

> "I shall endeavor to find out how nature's forces act upon one another, and in what manner the geographic environment exerts its influence." — Alexander von Humboldt

## Overview

A `.strata.yaml` file is a declarative recipe for building a map. It specifies:
1. **What data to fetch** (sources)
2. **How to process it** (layers and operations)
3. **What to output** (formats and options)

## Complete Example

```yaml
# champlain.strata.yaml
name: champlain_region
description: Lake Champlain and surrounding towns, optimized for pen plotting
version: 1

# =============================================================================
# SOURCES - Where to get the data (Thoreau)
# =============================================================================
sources:
  # US Census TIGER data
  vt_towns:
    uri: census:tiger/2023/vt/cousub
    description: Vermont county subdivisions (towns/cities)

  ny_towns:
    uri: census:tiger/2023/ny/cousub
    filter:
      counties: [Clinton, Essex, Franklin, Warren, Washington]

  lake_champlain:
    uri: census:tiger/2023/vt/areawater
    filter:
      HYDROID: "110469638395"

  vt_lakes:
    uri: census:tiger/2023/vt/areawater
    filter:
      min_area_km2: 0.5

  ny_lakes:
    uri: census:tiger/2023/ny/areawater
    filter:
      min_area_km2: 0.5

  # Canadian data
  quebec_muni:
    uri: quebec:municipalities
    description: Quebec municipal boundaries

  canvec_water:
    uri: canvec:hydro/waterbody
    clip_to: bounds  # Only fetch within output bounds

  # Highways
  vt_highways:
    uri: census:tiger/2023/vt/prisecroads

  quebec_highways:
    uri: quebec:highways

# =============================================================================
# LAYERS - How to process the data (Humboldt)
# =============================================================================
layers:
  # Layer 1: Regional background (bottom)
  - name: regional_background
    source: [ny_towns, quebec_muni]
    style:
      stroke: "#8d6e63"
      stroke_width: 0.5
      fill: none
    order: 1

  # Layer 2: Major water bodies
  - name: major_water
    source: lake_champlain
    operations:
      - type: identify_islands
        min_area_km2: 0.1
        output: champlain_islands  # Creates a derived source
      - type: subtract
        target: champlain_islands
    style:
      stroke: "#0288d1"
      stroke_width: 1.0
      fill: none
    order: 2

  # Layer 3: Town boundaries with water cutouts
  - name: towns
    source: [vt_towns, ny_towns]
    operations:
      - type: subtract
        target: [lake_champlain, vt_lakes, ny_lakes]
      - type: simplify
        tolerance: 0.0001
        preserve_topology: true
    style:
      stroke: "#7b1fa2"
      stroke_width: 0.75
      fill: none
    order: 3

  # Layer 4: Small water (shows through cutouts)
  - name: small_water
    source: [vt_lakes, ny_lakes, canvec_water]
    operations:
      - type: exclude
        target: lake_champlain  # Don't duplicate the big lake
      - type: clip
        target: towns  # Only water within town bounds
    style:
      stroke: "#1976d2"
      stroke_width: 0.5
      fill: none
    order: 4

  # Layer 5: Highways (top)
  - name: highways
    source: [vt_highways, quebec_highways]
    operations:
      - type: clip
        target: bounds
    style:
      stroke: "#d32f2f"
      stroke_width: 1.5
      fill: none
    order: 5

# =============================================================================
# OUTPUT - What to produce (Kelley)
# =============================================================================
output:
  # Geographic bounds [west, south, east, north]
  bounds: [-73.5, 43.0, -71.5, 45.2]
  # Or: bounds: auto  (calculated from sources)
  # Or: bounds: source:vt_towns  (bounds of specific source)

  # Coordinate reference system
  projection: epsg:32145  # Vermont State Plane
  # Or: projection: epsg:4326  # WGS84 (default)

  formats:
    # SVG for pen plotters
    - type: svg
      quality:
        - name: ultra_fine
          simplify: 0.00001
        - name: fine
          simplify: 0.0001
        - name: medium
          simplify: 0.001
        - name: coarse
          simplify: 0.01
      options:
        per_layer: true           # Separate SVG per layer
        combined: true            # Also create combined SVG
        optimize_for: plotter     # Stroke dedup, minimize pen travel
        stroke_units: mm          # For precise pen width
        page_size: [11, 17]       # Tabloid, in inches
        margin: 0.5               # Inches

    # GeoJSON for web viewing
    - type: geojson
      options:
        per_layer: true
        precision: 6              # Decimal places for coordinates

    # PMTiles for serverless web maps
    - type: pmtiles
      options:
        minzoom: 4
        maxzoom: 14
        attribution: "Strata | Census TIGER | CanVec | Quebec Open Data"
```

## Schema Reference

### Root Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | yes | Recipe identifier (used for output directory) |
| `description` | string | no | Human-readable description |
| `version` | integer | no | Schema version (default: 1) |
| `sources` | object | yes | Named data sources |
| `layers` | array | yes | Layer definitions |
| `output` | object | yes | Output configuration |

### Source Definition

```yaml
source_name:
  uri: string           # Required: source URI
  description: string   # Optional: human description
  filter: object        # Optional: filter features
  clip_to: string       # Optional: clip to bounds or another source
```

#### Source URI Formats

| Scheme | Format | Example |
|--------|--------|---------|
| `census` | `census:tiger/{year}/{state}/{type}` | `census:tiger/2023/vt/cousub` |
| `canvec` | `canvec:{category}/{type}` | `canvec:hydro/waterbody` |
| `quebec` | `quebec:{type}` | `quebec:municipalities` |
| `file` | `file:{path}` | `file:./data/custom.geojson` |
| `url` | `url:{url}` | `url:https://example.com/data.json` |

#### Census TIGER Types

| Type | Description |
|------|-------------|
| `cousub` | County subdivisions (towns, cities, townships) |
| `areawater` | Water bodies (lakes, ponds, reservoirs) |
| `linearwater` | Streams, rivers |
| `prisecroads` | Primary and secondary roads |
| `county` | County boundaries |
| `state` | State boundaries |

#### Filter Options

```yaml
filter:
  # By property value
  HYDROID: "110469638395"

  # By property list
  counties: [Clinton, Essex, Franklin]

  # By area
  min_area_km2: 0.5
  max_area_km2: 100

  # By SQL-like expression (future)
  where: "ALAND > 1000000"
```

### Layer Definition

```yaml
- name: string          # Required: layer identifier
  source: string|array  # Required: source name(s) to use
  operations: array     # Optional: processing operations
  style: object         # Optional: rendering style
  order: integer        # Required: stacking order (1 = bottom)
```

#### Operations

##### subtract
Remove geometry of target from source.
```yaml
- type: subtract
  target: lake_champlain          # Single source
  # or
  target: [lake1, lake2, lake3]   # Multiple sources
```

##### clip
Keep only geometry within target bounds.
```yaml
- type: clip
  target: bounds          # Use output bounds
  # or
  target: vt_towns        # Use another source's bounds
```

##### simplify
Reduce geometry complexity.
```yaml
- type: simplify
  tolerance: 0.0001       # Simplification tolerance
  preserve_topology: true # Prevent self-intersection
```

##### merge
Combine all features into single geometry.
```yaml
- type: merge
```

##### identify_islands
Find enclosed land masses within water.
```yaml
- type: identify_islands
  min_area_km2: 0.1       # Minimum island size
  output: island_source   # Name for derived source
```

##### exclude
Remove features that intersect target.
```yaml
- type: exclude
  target: lake_champlain
```

##### buffer
Expand or contract geometry.
```yaml
- type: buffer
  distance: 0.001         # Positive = expand, negative = contract
```

#### Style Properties

```yaml
style:
  stroke: "#7b1fa2"       # Stroke color (hex)
  stroke_width: 0.75      # Stroke width
  fill: none              # Fill color or 'none'
  opacity: 1.0            # Overall opacity
  dash_array: [5, 3]      # Dash pattern [dash, gap]
```

### Output Configuration

```yaml
output:
  bounds: array|string    # Geographic bounds
  projection: string      # Output CRS (EPSG code)
  formats: array          # Output format configs
```

#### Bounds Options

```yaml
bounds: [-73.5, 43.0, -71.5, 45.2]  # Explicit [west, south, east, north]
bounds: auto                         # Calculate from all sources
bounds: source:vt_towns              # Use bounds of specific source
```

#### SVG Format Options

```yaml
- type: svg
  quality: array          # Quality level definitions
  options:
    per_layer: bool       # Separate file per layer
    combined: bool        # Combined file with all layers
    optimize_for: plotter # Optimize for pen plotter
    stroke_units: mm      # Unit for stroke widths
    page_size: [w, h]     # Page dimensions in inches
    margin: float         # Page margin in inches
```

#### GeoJSON Format Options

```yaml
- type: geojson
  options:
    per_layer: bool       # Separate file per layer
    precision: int        # Coordinate decimal places
```

#### PMTiles Format Options

```yaml
- type: pmtiles
  options:
    minzoom: int          # Minimum zoom level
    maxzoom: int          # Maximum zoom level
    attribution: string   # Attribution text
```

## Validation Rules

1. All sources referenced in layers must be defined in `sources`
2. Operation targets must reference valid sources or "bounds"
3. Layer `order` values must be unique positive integers
4. At least one output format must be specified
5. Bounds must be valid WGS84 coordinates if explicit

## File Naming

Recipes should be named `{name}.strata.yaml`:
- `champlain.strata.yaml`
- `new_england.strata.yaml`
- `hudson_valley.strata.yaml`

## Output Directory Structure

```
output/
└── {recipe_name}/
    ├── svg/
    │   ├── ultra_fine/
    │   │   ├── 01_regional_background.svg
    │   │   ├── 02_major_water.svg
    │   │   ├── 03_towns.svg
    │   │   ├── 04_small_water.svg
    │   │   ├── 05_highways.svg
    │   │   └── combined.svg
    │   ├── fine/
    │   ├── medium/
    │   └── coarse/
    ├── geojson/
    │   ├── regional_background.geojson
    │   ├── major_water.geojson
    │   └── ...
    └── tiles/
        └── {recipe_name}.pmtiles
```
