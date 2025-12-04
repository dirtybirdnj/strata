# Strata Application Walkthrough

## What is Strata?

Strata is a declarative cartographic data processing toolkit that generates plotter-ready SVG maps from GIS data sources. It replaces the collection of Python scripts in `vt-geodata` with a unified YAML-based recipe system.

**Named after William Smith's geological strata** - the package embodies his insight that layer order matters.

---

## Architecture Overview

```
strata/
├── src/strata/
│   ├── cli.py              # Click-based CLI (strata new, build, prepare, etc.)
│   ├── thoreau/            # Data acquisition (Census, Quebec, Canada)
│   │   ├── census.py       # US Census TIGER data
│   │   ├── quebec.py       # Quebec open data (municipalities, MRC, regions)
│   │   ├── canada.py       # Canada federal data (CanVec hydro, NRN roads, NHN hydro)
│   │   └── cache.py        # Local caching system
│   ├── humboldt/           # Processing & transformation
│   │   ├── geometry.py     # Geometry operations (subtract, merge, dissolve, etc.)
│   │   └── projection.py   # CRS transformations
│   ├── maury/              # Pipeline orchestration
│   │   ├── recipe.py       # YAML recipe parser
│   │   └── pipeline.py     # Build pipeline execution
│   ├── kelley/             # Visualization & output
│   │   └── svg.py          # SVG generation
│   └── tui/                # Terminal UI wizard
│       ├── app.py          # Main TUI app (Textual)
│       ├── catalog.py      # Source catalog for browser
│       └── screens/        # TUI screens (welcome, source_browser, bounds, etc.)
```

---

## CLI Commands

| Command | Status | Description |
|---------|--------|-------------|
| `strata new` | ✅ Working | Launch TUI wizard to create recipe |
| `strata prepare <recipe>` | ✅ Working | Download and cache all sources |
| `strata build <recipe>` | ✅ Working | Process layers and generate outputs |
| `strata preview <recipe>` | ✅ Working | Preview data within bounds |
| `strata cache list` | ✅ Working | Show cached datasets |
| `strata cache clear` | ✅ Working | Clear cache |
| `strata validate <recipe>` | 🟡 Partial | Basic validation only (see improvement note below) |
| `strata fetch <recipe>` | ❌ Not implemented | Download without processing |
| `strata sources list` | ❌ Not implemented | List available sources |
| `strata sources search` | ❌ Not implemented | Search for sources |

---

## Data Sources

### US Census TIGER (`census:tiger/2023/{state}/{layer}`)

| Layer | Description | Example |
|-------|-------------|---------|
| `cousub` | Town/township boundaries | `census:tiger/2023/vt/cousub` |
| `areawater` | Lakes and ponds | `census:tiger/2023/vt/areawater` |
| `linearwater` | Rivers and streams | `census:tiger/2023/vt/linearwater` |
| `prisecroads` | Primary/secondary roads | `census:tiger/2023/vt/prisecroads` |
| `county` | County boundaries | `census:tiger/2023/vt/county` |
| `state` | State boundary | `census:tiger/2023/vt/state` |
| `place` | Cities and CDPs | `census:tiger/2023/vt/place` |
| `tract` | Census tracts | `census:tiger/2023/vt/tract` |

**Coverage:** All 50 states + DC + PR

### Quebec (`quebec:{layer}`)

| Layer | Description | Records |
|-------|-------------|---------|
| `municipalities` | Municipal boundaries | ~2,263 |
| `mrc` | Regional county municipalities | 138 |
| `regions` | Administrative regions | 17 |
| `metropolitan` | Metro communities | 2 |

### Canada Federal (`canada:{source}/{layer}`)

| Source | Description | Coverage |
|--------|-------------|----------|
| `canvec/hydro` | Lakes from CanVec 1M | All Canada (~150MB) |
| `nrn/{prov}` | National Road Network | All 13 provinces/territories |
| `nhn/{workunit}` | National Hydro Network | By watershed workunit |
| `nhn/{workunit}/rivers` | NHN linear water (rivers) | By watershed workunit |

**Province codes:** nl, pe, ns, nb, qc, on, mb, sk, ab, bc, yt, nt, nu

**NHN Workunits (Quebec/VT border):**
- `02OJ000` - Richelieu River watershed
- `02OHA00` - Lake Champlain (western Quebec)
- `02OHB00` - Lake Champlain (eastern Quebec, includes Missisquoi Bay)
- `02OG000` - Yamaska River watershed

---

## Geometry Operations (`strata.humboldt`)

| Operation | Description | Example Use |
|-----------|-------------|-------------|
| `subtract` | Cut geometry from features | Water cutouts in towns |
| `clip` | Clip to bounding box | Limit to map extent |
| `merge` | Union all features into one | Combine fragmented polygons |
| `dissolve` | Merge by attribute | Lake Champlain by HYDROID |
| `simplify` | Reduce vertices | Different quality levels |
| `buffer` | Expand/contract geometry | Safety margins |
| `clean` | Fix topology issues | Remove slivers |
| `remove_holes` | Fill interior rings | Remove islands from water |
| `extract_islands` | Get holes as features | Extract lake islands |
| `merge_touching` | Union connected features | Cross-border lakes (Memphremagog) |

---

## Recipe Format (`.strata.yaml`)

```yaml
name: my_map
description: A sample map
version: 1

sources:
  vt_towns:
    uri: census:tiger/2023/vt/cousub
  vt_water:
    uri: census:tiger/2023/vt/areawater
  vt_roads:
    uri: census:tiger/2023/vt/prisecroads

layers:
  - name: towns
    source: vt_towns
    operations:
      - type: subtract
        target: vt_water
      - type: simplify
        tolerance: 0.0003
    style:
      stroke: "#424242"
      stroke_width: 0.5
      fill: "#66bb6a"
      fill_by: COUNTYFP          # Color by county
      color_map:                  # County FIPS to color
        "001": "#66bb6a"
        "003": "#42a5f5"
      vary_fill: true            # Slight variation per feature
    order: 10

  - name: lakes
    source: vt_water
    filter:
      min_area_km2: 0.5
    style:
      stroke: "#1976d2"
      fill: "#64b5f6"
    order: 5

output:
  bounds: [-73.5, 42.7, -71.5, 45.0]
  projection: epsg:4326
  formats:
    - type: svg
      quality:
        - name: fine
          simplify: 0.0005
      options:
        per_layer: true
        combined: true
        page_size: [12, 18]
```

---

## Example Recipes

| Recipe | Description | Page Size |
|--------|-------------|-----------|
| `vermont_plotter.strata.yaml` | VT-centered with all neighbors, county colors | 12×18 |
| `lake_champlain_plotter.strata.yaml` | Lake Champlain focus | 12×24 |
| `vermont_regional_master.strata.yaml` | Full vt-geodata replacement | 12×18 |

---

## vt-geodata Feature Parity - COMPLETE ✅

All major features from vt-geodata are now implemented in strata:

| Feature | Status |
|---------|--------|
| VT towns with water cutouts | ✅ |
| NY/NH/MA/ME towns with water cutouts | ✅ |
| Lake Champlain with island cutouts | ✅ (30 islands preserved) |
| Lake Memphremagog (cross-border) | ✅ |
| Quebec municipalities with water cutouts | ✅ |
| Quebec MRC backgrounds | ✅ |
| Richelieu corridor (NHN data) | ✅ |
| Missisquoi Bay Quebec waters (NHN data) | ✅ |
| Quebec rivers (NHN data) | ✅ |
| Linear water (rivers) all states | ✅ |
| VT state boundary (thick green) | ✅ |
| Interstate filtering (RTTYP: I) | ✅ |
| US highway filtering (RTTYP: U) | ✅ |
| State route filtering (RTTYP: S) | ✅ |
| Quebec highways (Autoroutes) | ✅ |
| VT county-based color map | ✅ |
| Per-layer SVG output | ✅ |
| Combined SVG output | ✅ |
| Multiple simplification levels | ✅ |
| Lake Champlain 12×24 focused view | ✅ |

---

## Historical Branding Assets

### Portraits (5)
- `smith_portrait.jpg` - William Smith (USGS)
- `thoreau_1856_daguerreotype.jpg` - Thoreau (Wikimedia)
- `humboldt_portrait.jpg` - Humboldt (Smithsonian NPG)
- `maury_portrait.jpg` - Maury (LOC)
- `kelley_portrait.jpg` - Kelley (LOC)

### Maps & Documents (6)
- `smith_1815_map.jpg` - 1815 geological map (NASA)
- `smith_1815_map_nhm.pdf` - High-res map (NHM, 6.8MB)
- `smith_strata_identified_fossils_1816.pdf` - Fossil plates (23MB)
- `smith_memoirs_phillips_1844.pdf` - Biography (22MB)
- `humboldt_chimborazo.jpg` - Chimborazo diagram
- `hull_house_maps_1895.pdf` - Hull House maps (13.8MB)

### Documentation
- `historical_artifacts.html` - Asset catalog with citations
- `historical-docs.html` - Narrative docs (William Smith as host)
- `strata.html` - Technical documentation
- `DEEP_DIVE_*.md` - 5 biographical research files

---

## Testing Commands

```bash
# Activate environment
cd ~/Code/strata
source .venv/bin/activate

# Test TUI
strata new

# Test prepare
strata prepare examples/vermont_plotter.strata.yaml

# Test build
strata build examples/vermont_plotter.strata.yaml

# Build Lake Champlain focused map
strata build examples/lake_champlain_plotter.strata.yaml

# View result
open output/vermont_plotter/svg/medium_detail/combined.svg

# Check cache
strata cache list
```

---

## Next Improvement: Recipe Validation

**Priority:** High (quick win)

The `strata validate` command should be enhanced to:
1. Validate all source URIs are well-formed and reference known data sources
2. Check that all layer `source` references point to defined sources
3. Verify `filter` field names exist in the source schema
4. Confirm `operations` reference valid target sources (e.g., `subtract` targets)

This would catch typos early and provide clear error messages instead of cryptic failures mid-pipeline during `prepare` or `build`.

---

## File Locations

| Type | Path |
|------|------|
| Source code | `src/strata/` |
| Examples | `examples/` |
| Output | `output/` |
| Cache | `~/Library/Caches/strata/` |
| Historical assets | `historical-assets/` |
| Documentation | `*.html`, `docs/`, `*.md` |
