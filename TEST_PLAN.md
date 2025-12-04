# Strata Test Plan & vt-geodata Integration Guide

## Quick Test Commands

```bash
cd ~/Code/strata
source .venv/bin/activate

# 1. Test TUI wizard launches
strata new
# Press Escape to exit after verifying it launches

# 2. Test data fetching (uses cached data if available)
strata prepare examples/vermont_regional_12x18.strata.yaml

# 3. Build and generate outputs
strata build examples/vermont_regional_12x18.strata.yaml -o output/test

# 4. Open the result
open output/test/vermont_regional_12x18/svg/fine/combined.svg
```

## Feature Tests

### Test 1: TUI Wizard Flow
```bash
strata new
```
**Expected:**
- Welcome screen appears with ASCII logo
- Can enter recipe name and description
- "Continue" navigates to Source Browser
- Source Browser shows:
  - US Census TIGER (all 50 states by region)
  - Quebec (Canada) with municipalities, MRC, regions
  - Canada (National) with CanVec hydro and NRN roads for all 13 provinces
- Can select sources with Enter key
- Can search/filter with "/" key
- Continue → Bounds screen with presets
- Continue → Layer config with auto-configured layers
- Continue → Output config with YAML preview
- "Generate Recipe" creates `.strata.yaml` file

### Test 2: merge_touching Operation
```bash
# Build the recipe that uses merge_touching for Lake Memphremagog
strata build examples/lake_champlain_quebec_12x24.strata.yaml -o output/memphremagog_test

# Check that cross-border features are merged
open output/memphremagog_test/lake_champlain_quebec_12x24/svg/fine/combined.svg
```
**Expected:**
- Lake Memphremagog layer shows unified lake (not split at border)
- VT and Quebec portions merged into single polygon

### Test 3: Canada Data Sources
```bash
# Test CanVec hydro
strata prepare examples/lake_champlain_quebec_12x24.strata.yaml
# Should download canada:canvec/hydro (~150MB) if not cached

# Verify cache
ls -la ~/Library/Caches/strata/canada/
```
**Expected:**
- Downloads CanVec hydro shapefile
- Caches at `~/Library/Caches/strata/canada/canada_canvec_hydro/`

### Test 4: Layer Filtering
The `lake_champlain_quebec_12x24.strata.yaml` uses `min_area_km2` filter:
```yaml
filter:
  min_area_km2: 5  # Only lakes >= 5 sq km
```
**Expected:**
- Small ponds filtered out
- Only major lakes appear in output

### Test 5: Hawaii Recipe (Non-VT Data)
```bash
strata build examples/hawaii_islands.strata.yaml -o output/hawaii_test
open output/hawaii_test/hawaii_islands/svg/fine/combined.svg
```
**Expected:**
- Downloads Hawaii TIGER data
- Shows all major Hawaiian islands
- Proper water features, roads, places

### Test 6: Niagara Falls Recipe (NY Focus)
```bash
strata build examples/niagara_falls.strata.yaml -o output/niagara_test
open output/niagara_test/niagara_falls/svg/fine/combined.svg
```
**Expected:**
- Shows Niagara Falls region
- NY towns with water cutouts
- Niagara River visible

## vt-geodata Comparison

### Layer Mapping: vt-geodata → Strata

| vt-geodata Layer | Strata Source URI | Notes |
|-----------------|-------------------|-------|
| `vt_towns_with_water_cutouts.json` | `census:tiger/2023/vt/cousub` + subtract `vt_water` | Water cutout via operation |
| `ny_towns_with_water_cutouts.json` | `census:tiger/2023/ny/cousub` + subtract `ny_water` | Water cutout via operation |
| `quebec_municipalities_with_water_cutouts.json` | `quebec:municipalities` + subtract `quebec_hydro` | Need to add quebec water cutout |
| `lake_champlain_with_island_cutouts.json` | `census:tiger/2023/vt/areawater` + `ny` filtered by FULLNAME | Use `dissolve` by HYDROID |
| `lake_memphremagog_full.json` | VT areawater + `canada:canvec/hydro` | Use `merge_touching` |
| `quebec_lakes.json` | `canada:canvec/hydro` | Clip to Quebec bounds |
| `regional_interstates.json` | `census:tiger/2023/{state}/prisecroads` filtered RTTYP="I" | Multiple states |
| `quebec_highways.json` | `canada:nrn/qc` filtered ROADCLASS="Freeway" | Or use quebec:highways |

### To Replace vt-geodata with Strata

1. **Create Master Regional Recipe**
   ```yaml
   name: vermont_regional_master
   sources:
     # All the states
     vt_towns: {uri: "census:tiger/2023/vt/cousub"}
     ny_towns: {uri: "census:tiger/2023/ny/cousub"}
     nh_towns: {uri: "census:tiger/2023/nh/cousub"}
     ma_towns: {uri: "census:tiger/2023/ma/cousub"}
     me_towns: {uri: "census:tiger/2023/me/cousub"}

     # Water
     vt_water: {uri: "census:tiger/2023/vt/areawater"}
     ny_water: {uri: "census:tiger/2023/ny/areawater"}
     quebec_hydro: {uri: "canada:canvec/hydro"}

     # Roads
     vt_roads: {uri: "census:tiger/2023/vt/prisecroads"}
     quebec_roads: {uri: "canada:nrn/qc"}
     # etc...
   ```

2. **Missing from Strata (Need to Add)**
   - [ ] Quebec water cutouts for municipalities
   - [ ] Richelieu corridor (river system)
   - [ ] County-based color maps (vary_fill by county)
   - [ ] Linear water (rivers) - currently only areawater

3. **Already Supported**
   - [x] VT/NY/NH/MA town boundaries with water cutouts
   - [x] Lake Champlain (multi-county merge via dissolve)
   - [x] Lake Memphremagog (cross-border via merge_touching)
   - [x] Quebec municipalities and MRCs
   - [x] Interstate/highway filtering
   - [x] Quebec highways (NRN)
   - [x] Per-layer and combined SVG output
   - [x] Multiple simplification levels

## Data Source Coverage

### US Census TIGER (Strata: `census:tiger/2023/{state}/{layer}`)
- **States:** All 50 + DC + PR
- **Layers:**
  - `cousub` - Towns/townships
  - `areawater` - Lakes/ponds
  - `linearwater` - Rivers/streams
  - `prisecroads` - Primary/secondary roads
  - `county` - County boundaries
  - `state` - State boundary
  - `place` - Cities/CDPs
  - `tract` - Census tracts

### Quebec (Strata: `quebec:{layer}`)
- `municipalities` - ~2,263 municipal boundaries
- `mrc` - 138 regional county municipalities
- `regions` - 17 administrative regions
- `metropolitan` - 2 metro communities

### Canada (Strata: `canada:{source}/{layer}`)
- `canvec/hydro` - National hydro from NRCan (~150MB)
- `nrn/{prov}` - Roads for all 13 provinces/territories

## Performance Notes

- First run downloads ~500MB+ of data
- Subsequent runs use cache at `~/Library/Caches/strata/`
- Large builds (vermont_regional) take 2-5 minutes
- Use `strata cache --clear` to reset

## Known Issues

1. **Geographic CRS Warning** - `merge_touching` shows warning about buffer in geographic CRS. Safe to ignore for small buffers.

2. **Quebec Water Cutouts** - Quebec municipalities don't have water subtracted yet (vt-geodata has this)

3. **Linear Water** - Rivers (linearwater) not yet integrated into examples

## Next Steps for Full vt-geodata Replacement

1. Create `examples/vermont_regional_master.strata.yaml` matching all vt-geodata layers
2. Add `linearwater` source and layers for rivers
3. Implement Quebec municipality water cutouts
4. Add Richelieu corridor (St. Lawrence connector)
5. Verify SVG output matches vt-geodata quality
