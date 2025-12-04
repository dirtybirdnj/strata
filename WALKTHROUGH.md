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
│   │   ├── canada.py       # Canada federal data (CanVec hydro, NRN roads)
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
| `strata validate <recipe>` | 🟡 Partial | Basic validation only |
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

**Province codes:** nl, pe, ns, nb, qc, on, mb, sk, ab, bc, yt, nt, nu

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
      fill: none
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

| Recipe | Description | Layers |
|--------|-------------|--------|
| `vermont_12x18.strata.yaml` | VT towns with water cutouts | 5 |
| `vermont_regional_12x18.strata.yaml` | VT + neighboring states | 15+ |
| `vermont_regional_master.strata.yaml` | Full vt-geodata replacement | 20+ |
| `lake_champlain_12x24.strata.yaml` | Champlain focus with islands | 10 |
| `lake_champlain_quebec_12x24.strata.yaml` | Champlain + Memphremagog | 12 |
| `hawaii_islands.strata.yaml` | Hawaii test (non-VT) | 6 |
| `niagara_falls.strata.yaml` | NY focus test | 6 |
| `vt_fishing_access_12x24.strata.yaml` | Points/markers demo | 8 |

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

## vt-geodata Feature Parity Checklist

### Already Implemented ✅

| vt-geodata Feature | Strata Implementation |
|--------------------|----------------------|
| VT towns with water cutouts | `subtract` operation |
| NY/NH/MA/ME towns with water cutouts | `subtract` operation (ME has no cutouts) |
| Lake Champlain (multi-county merge) | `dissolve` by HYDROID |
| Lake Memphremagog (cross-border) | `merge_touching` operation |
| Quebec municipalities with water cutouts | `subtract` quebec_hydro ✅ |
| Quebec MRC backgrounds | `quebec:mrc` source |
| ME (Maine) backgrounds and towns | ✅ Added to master recipe |
| VT state boundary (thick green) | ✅ Order 100, stroke 2.5 |
| Linear water (rivers) all states | ✅ VT/NY/NH/MA/ME rivers |
| Interstate filtering | `filter: {RTTYP: "I"}` |
| US highway filtering | `filter: {RTTYP: "U"}` |
| State route filtering | `filter: {RTTYP: "S"}` |
| Quebec highways | `canada:nrn/qc` + filter |
| Per-layer SVG output | `per_layer: true` |
| Combined SVG output | `combined: true` |
| Multiple simplification levels | `quality:` section |

### Missing / Needs Work 🟡

| vt-geodata Feature | Status | Notes |
|--------------------|--------|-------|
| Richelieu corridor | ❌ Missing | Requires NHN data source handler |
| Missisquoi Bay Quebec waters | ❌ Missing | Cross-border hydro filtering |
| County-based color maps | 🟡 Partial | `vary_fill` exists but limited |

### vt-geodata Layers to Replicate

From `generate_plotter_svgs.py`, the complete layer stack is:

1. **Background Regions:** quebec, ny, nh, ma, me (counties/MRC)
2. **Major Water:** lake_champlain, lake_memphremagog, richelieu_corridor, missisquoi_quebec
3. **Town Boundaries:** quebec_municipalities, ny_towns, nh_towns, ma_towns, me_towns, vt_towns
4. **Regional Hydro:** {state}_rivers, {state}_lakes for each state
5. **Roads:** regional_interstates, regional_us_highways, regional_state_routes, quebec_highways
6. **VT Boundary:** thick green outline

---

## Work Items by Priority

### High Priority (vt-geodata Parity) - MOSTLY DONE ✅

1. ~~**Add ME support to examples**~~ ✅ DONE
2. ~~**Quebec municipality water cutouts**~~ ✅ DONE
3. ~~**Linear water (rivers)**~~ ✅ DONE (VT, NY, NH, MA, ME)
4. ~~**VT state boundary layer**~~ ✅ DONE (order 100, thick green)

5. **Richelieu corridor** ❌ REMAINING
   - Requires adding NHN (National Hydro Network) data source
   - vt-geodata uses `nhn_richelieu.zip` from GeoGratis
   - Would need new handler in `thoreau/canada.py`

6. **Missisquoi Bay Quebec waters** 🟡 OPTIONAL
   - Cross-border water filtering
   - Could use bounding box on CanVec hydro

### Medium Priority (Polish)

7. **County-based color maps**
   - Implement `vary_fill: by_county` or similar
   - Match vt-geodata VT_COUNTY_COLORS

8. **Improve TUI wizard**
   - Add bounds preview map
   - Better layer configuration UI

9. **Add missing CLI commands**
   - `strata sources list/search/info`
   - `strata fetch`

### Lower Priority (Nice to Have)

10. **More example recipes**
    - Other regions (Pacific NW, New England, etc.)
    - International examples

---

## Testing Commands

```bash
# Activate environment
cd ~/Code/strata
source .venv/bin/activate

# Test TUI
strata new

# Test prepare
strata prepare examples/vermont_regional_12x18.strata.yaml

# Test build
strata build examples/vermont_regional_12x18.strata.yaml -o output/test

# View result
open output/test/vermont_regional_12x18/svg/fine/combined.svg

# Check cache
strata cache list
```

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
