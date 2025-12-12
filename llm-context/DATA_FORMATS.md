# Strata Data Formats

## Recipe YAML Schema

A `.strata.yaml` file defines a complete map build. Here's the full structure:

```yaml
# Recipe metadata
name: string              # Required: used for output directory name
description: string       # Optional: human-readable description
version: 1                # Schema version (always 1)

# Data sources to fetch
sources:
  source_name:            # Arbitrary name you reference in layers
    uri: string           # Required: source URI (see URI Schemes below)
    description: string   # Optional
    filter: object        # Optional: filter features on fetch
    clip_to: string       # Optional: clip to bounds or another source

# Map layers to render
layers:
  - name: string          # Required: layer identifier
    source: string | [string, ...]  # Required: source name(s)
    bounds: [w, s, e, n]  # Optional: clip layer to these bounds
    filter: object        # Optional: filter features
    operations:           # Optional: processing operations
      - type: string      # Operation type (see Operations below)
        ...               # Operation-specific params
    style:                # Optional: rendering style
      stroke: "#hex"
      stroke_width: float
      fill: "#hex" | "none"
      ...
    order: int            # Required: stacking order (1 = bottom)

# Output configuration
output:
  bounds: [w, s, e, n] | "auto" | "source:name"
  projection: "epsg:4326"
  formats:
    - type: "svg" | "geojson" | "pmtiles"
      quality: [...]      # SVG only
      options: {...}
```

---

## Source URI Schemes

### Census TIGER (US)

```
census:tiger/{year}/{state}/{type}
```

| Type | Description |
|------|-------------|
| `cousub` | County subdivisions (towns, cities) |
| `areawater` | Water bodies (lakes, ponds) |
| `linearwater` | Streams, rivers |
| `prisecroads` | Primary/secondary roads |
| `county` | County boundaries |
| `state` | State boundaries |
| `place` | Census places |
| `tract` | Census tracts |

**Examples:**
- `census:tiger/2023/vt/cousub` - Vermont towns
- `census:tiger/2023/ny/areawater` - New York water bodies

### Canadian Data

```
canada:canvec/{layer}     # CanVec vector data
canada:nhn/{workunit}     # National Hydro Network
canada:nrn/{province}     # National Road Network
```

**Examples:**
- `canada:canvec/hydro` - Canadian hydrology
- `canada:nhn/02OJ000` - NHN work unit
- `canada:nrn/qc` - Quebec roads

### Quebec Open Data

```
quebec:{type}
```

Types: `municipalities`, `highways`, `hydrography`

### USGS National Map

```
usgs:{service}/{layer}
```

**Examples:**
- `usgs:wbd/huc12` - Watershed boundaries
- `usgs:nhd/flowline` - NHD flowlines
- `usgs:structures/schools` - Schools

### Other Sources

```
naturalearth:{scale}/{layer}   # Natural Earth data
openskimap:ski_areas           # OpenSkiMap
mexico:{type}                  # Mexico INEGI data
woodland:{type}                # Woodland Trust data
file:./path/to/file.geojson    # Local file
```

---

## Source Filters

Filters reduce data at load time:

```yaml
sources:
  large_lakes:
    uri: census:tiger/2023/vt/areawater
    filter:
      min_area_km2: 1.0           # Minimum area
      max_area_km2: 100.0         # Maximum area

  champlain:
    uri: census:tiger/2023/vt/areawater
    filter:
      FULLNAME_contains: Champlain  # Substring match (case-insensitive)

  interstates:
    uri: census:tiger/2023/vt/prisecroads
    filter:
      RTTYP: "I"                  # Exact match

  selected_towns:
    uri: census:tiger/2023/vt/cousub
    filter:
      NAMELSAD: ["Burlington city", "Montpelier city"]  # List match
```

---

## Layer Operations

Operations are applied sequentially to layer geometry:

### subtract

Remove geometry of target from source (water cutouts):
```yaml
- type: subtract
  target: lake_source          # Single source
  target: [lake1, lake2]       # Multiple sources
```

### clip

Keep only geometry within bounds:
```yaml
- type: clip
  target: bounds               # Use output bounds
  target: another_source       # Use another source's bounds
```

### simplify

Reduce geometry complexity:
```yaml
- type: simplify
  tolerance: 0.001             # Higher = more simplified
  preserve_topology: true      # Prevent self-intersection
```

### merge

Combine all features into single geometry:
```yaml
- type: merge
```

### buffer

Expand or contract geometry:
```yaml
- type: buffer
  distance: 0.001              # Positive = expand, negative = contract
```

### exclude

Remove features intersecting target:
```yaml
- type: exclude
  target: major_lake
```

### extract_islands

Extract holes from water polygons as island features:
```yaml
- type: extract_islands
  min_area_km2: 0.1
```

### dissolve

Merge geometries by attribute value:
```yaml
- type: dissolve
  by: HYDROID                  # Column to group by
```

### merge_touching

Merge features that touch (cross-border features):
```yaml
- type: merge_touching
  buffer_distance: 0.0001
```

### clean

Fix topology issues:
```yaml
- type: clean
  buffer_distance: 0.0         # Optional erosion/dilation
```

---

## Style Properties

```yaml
style:
  # Stroke (outline)
  stroke: "#7b1fa2"            # Hex color
  stroke_width: 0.75           # Width in points

  # Fill
  fill: "#a5d6a7"              # Hex color or "none"
  vary_fill: true              # Slight color variation per feature

  # Color mapping by attribute
  fill_by: COUNTYFP            # Column name
  color_map:
    "001": "#66bb6a"           # Value -> color mapping
    "003": "#42a5f5"

  # Other
  opacity: 1.0
  dash_array: [5, 3]           # Dash pattern [dash, gap]

  # Points only
  marker: circle               # circle, square, diamond, triangle, cross, x
  marker_size: 6.0
```

---

## Output Formats

### SVG Output

```yaml
- type: svg
  quality:
    - name: high_detail
      simplify: 0.0003
    - name: medium
      simplify: 0.001
    - name: draft
      simplify: 0.005
  options:
    per_layer: true            # Separate SVG per layer
    combined: true             # Combined SVG
    page_size: [12, 18]        # Width, height in inches
    margin: 0.5                # Margin in inches
    stroke_units: mm
    optimize_for: plotter

    # Optional: convert fills to hatch patterns
    plotter_fill:
      enabled: true
      spacing: 3.0             # Line spacing (smaller = denser)
      stroke_width: 0.5
      include_outlines: true
```

### GeoJSON Output

```yaml
- type: geojson
  options:
    per_layer: true
    precision: 6               # Decimal places for coordinates
```

---

## Output Directory Structure

```
output/
└── {recipe_name}/
    ├── svg/
    │   ├── high_detail/
    │   │   ├── 01_layer_name.svg
    │   │   ├── 02_another_layer.svg
    │   │   ├── combined.svg
    │   │   └── combined_plotter.svg  # If plotter_fill enabled
    │   ├── medium/
    │   └── draft/
    └── geojson/
        ├── layer_name.geojson
        └── another_layer.geojson
```

---

## Complete Example

```yaml
name: lake_region
description: Lake and surrounding towns

sources:
  towns:
    uri: census:tiger/2023/vt/cousub
  water:
    uri: census:tiger/2023/vt/areawater
    filter:
      min_area_km2: 0.5

layers:
  - name: towns
    source: towns
    operations:
      - type: subtract
        target: water
      - type: simplify
        tolerance: 0.001
    style:
      stroke: "#333333"
      stroke_width: 0.5
      fill: "#a5d6a7"
      vary_fill: true
    order: 1

  - name: lakes
    source: water
    operations:
      - type: simplify
        tolerance: 0.001
    style:
      stroke: "#0d47a1"
      stroke_width: 0.3
      fill: "#1976d2"
    order: 2

output:
  bounds: [-73.5, 42.7, -71.5, 45.0]
  projection: epsg:4326
  formats:
    - type: svg
      quality:
        - name: fine
          simplify: 0.0005
      options:
        combined: true
        page_size: [11, 17]
    - type: geojson
```
