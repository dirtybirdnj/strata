# Feature Gap: Strata vs vt-geodata

This document outlines the features needed in Strata to fully recreate the maps produced by the vt-geodata project.

## Current Status

Strata can now produce Vermont regional maps with:
- ✅ Vermont 256 towns with water cutouts
- ✅ Neighboring states (NY, NH, MA, ME) for regional context
- ✅ Water bodies from TIGER/Line areawater
- ✅ Rivers and streams from TIGER/Line linearwater
- ✅ Primary and secondary roads from TIGER/Line prisecroads
- ✅ Multiple output quality levels
- ✅ Per-layer and combined SVG output
- ✅ Attribute-based filtering (HYDROID, FULLNAME, etc.)
- ✅ Road classification filtering (RTTYP, MTFCC)
- ✅ **NEW** County-based color maps (fill_by + color_map)

## Implemented Features

### Attribute-Based Filtering

Strata now supports flexible attribute filtering in source definitions:

```yaml
sources:
  # Exact match
  lake_champlain:
    uri: census:tiger/2023/vt/areawater
    filter:
      HYDROID: "110469638395"

  # Substring match (case-insensitive)
  champlain_water:
    uri: census:tiger/2023/vt/areawater
    filter:
      FULLNAME_contains: "Champlain"

  # List match
  major_roads:
    uri: census:tiger/2023/vt/prisecroads
    filter:
      MTFCC: ["S1100", "S1200"]

  # Road type filtering
  interstates:
    uri: census:tiger/2023/vt/prisecroads
    filter:
      RTTYP: "I"  # I=Interstate, U=US Route, S=State Route
```

### Road Classification (RTTYP values)

| Code | Description | Example |
|------|-------------|---------|
| I | Interstate | I-89, I-91 |
| U | US Route | US-2, US-7 |
| S | State Route | VT-100, VT-15 |
| M | Common name | Main St, Lake Rd |
| O | Other | Old Rte 101 |
| C | County | County Rd 5 |

### County-Based Color Maps

Strata supports attribute-based fill coloring:

```yaml
layers:
  - name: vt_towns
    source: vt_towns
    style:
      stroke: "#424242"
      stroke_width: 0.5
      fill: "#e0e0e0"  # Fallback color
      fill_by: COUNTYFP  # Column to use for color lookup
      color_map:
        "001": "#a5d6a7"  # Addison - light green
        "003": "#90caf9"  # Bennington - light blue
        "005": "#ffcc80"  # Caledonia - orange
        "007": "#ce93d8"  # Chittenden - purple
        # ... etc
```

Features:
- `fill_by`: Specify which column determines fill color
- `color_map`: Dict mapping column values to hex colors
- `vary_fill`: Boolean (default true) to add slight color variation per feature

## Feature Gaps

### 1. Quebec Data Source

**vt-geodata**: Uses custom Quebec municipality and MRC (regional county municipality) boundary data.

**Strata**: No Quebec source handler.

**Implementation needed**:
- Add `quebec:municipalities` URI handler in `thoreau/`
- Quebec data sources:
  - Statistics Canada boundary files
  - Quebec Open Data Portal (données ouvertes)
  - Natural Resources Canada CanVec data

**Example recipe syntax**:
```yaml
sources:
  quebec_muni:
    uri: quebec:municipalities/2023
    description: Quebec municipal boundaries
```

---

### 2. County-Based Color Maps

**vt-geodata**: Colors Vermont towns by county using a predefined color palette.

**Strata**: No support for attribute-based styling or color maps.

**Implementation needed**:
- Add `color_map` property to layer styles
- Support mapping attribute values to colors
- Add `fill_by` property to specify which column determines fill color

**Example recipe syntax**:
```yaml
layers:
  - name: vt_towns
    source: vt_towns
    style:
      stroke: "#424242"
      stroke_width: 0.5
      fill_by: COUNTYFP  # Color by county FIPS code
      color_map:
        "001": "#a5d6a7"  # Addison - green
        "003": "#90caf9"  # Bennington - blue
        "005": "#ffcc80"  # Caledonia - orange
        # ... etc
```

---

### 4. Island Detection Operation

**vt-geodata**: Automatically identifies islands within Lake Champlain geometry and creates cutouts so islands render with town boundaries visible.

**Strata**: Has `identify_islands` operation stub but not implemented.

**Implementation needed**:
- Implement ring analysis to find interior rings (holes/islands)
- Create separate geometries for islands above a size threshold
- Allow outputting islands as a separate layer

**Example recipe syntax**:
```yaml
layers:
  - name: lake_champlain
    source: lake_champlain
    operations:
      - type: identify_islands
        min_area_km2: 0.1
        output: champlain_islands  # Creates new source
```

---

### 5. Road Classification Filtering

**vt-geodata**: Separates roads into interstates, US highways, and state routes with different styles.

**Strata**: Downloads all prisecroads together without classification filtering.

**Implementation needed**:
- Add filter support for TIGER road classification codes (MTFCC)
- MTFCC codes: S1100 (primary), S1200 (secondary), S1400 (local)

**Example recipe syntax**:
```yaml
sources:
  vt_interstates:
    uri: census:tiger/2023/vt/prisecroads
    filter:
      MTFCC: "S1100"  # Primary roads (interstates)

  vt_us_routes:
    uri: census:tiger/2023/vt/prisecroads
    filter:
      RTTYP: "U"  # US routes
```

---

### 6. Geometry Merge by Attribute

**vt-geodata**: Merges multi-part features (like Lake Champlain which spans VT and NY) into single geometries.

**Strata**: Has `merge` operation but merges all features, not by attribute.

**Implementation needed**:
- Add `merge_by` parameter to merge features sharing an attribute value

**Example recipe syntax**:
```yaml
operations:
  - type: merge
    by: HYDROID  # Merge features with same HYDROID
```

---

### 7. Linear Water Features

**vt-geodata**: Includes rivers and streams from TIGER linearwater.

**Strata**: Supports linearwater in census.py but not demonstrated in examples.

**Implementation needed**:
- No code changes needed - linearwater already supported
- Just needs example usage

**Example recipe syntax**:
```yaml
sources:
  vt_rivers:
    uri: census:tiger/2023/vt/linearwater
    description: Vermont rivers and streams
```

---

### 8. Custom Bounds Adjustment Tool

**vt-geodata**: Has an interactive web-based crop tool for adjusting map bounds while maintaining aspect ratio.

**Strata**: Has `strata preview` command but no interactive bounds adjustment.

**Implementation needed**:
- Add `--interactive` flag to preview command
- Or create `strata bounds` command with TUI for adjusting bounds
- Calculate aspect ratio-locked bounds for print sizes

---

## Priority Ranking

| Feature | Priority | Complexity | Status |
|---------|----------|------------|--------|
| HYDROID filtering | High | Low | ✅ **Implemented** |
| Road classification | High | Low | ✅ **Implemented** |
| Color maps | Medium | Medium | ✅ **Implemented** |
| Linear water | Low | None | ✅ **Implemented** |
| Quebec source | Medium | High | ❌ Not started |
| Island detection | Medium | Medium | ❌ Not started |
| Geometry merge by attr | Low | Low | ❌ Not started |
| Interactive bounds | Low | High | ❌ Not started |

## Recommended Implementation Order

1. ~~Attribute filtering (HYDROID, MTFCC)~~ ✅ **Done**
2. ~~Color maps~~ ✅ **Done**
3. ~~Linear water (rivers)~~ ✅ **Done**
4. Island detection - accurate lake rendering
5. Quebec source - complete regional map coverage
