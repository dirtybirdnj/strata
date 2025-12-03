# Strata CLI Design

> "I have been consulting the records of the winds and currents... the results are startling." — Matthew Fontaine Maury

## Overview

The `strata` CLI provides commands for building maps from recipes, managing data sources, and running the interactive wizard.

## Command Structure

```
strata
├── new           # Interactive wizard to create a recipe
├── build         # Build outputs from a recipe
├── fetch         # Download/cache sources without building
├── preview       # Quick preview of a recipe
├── validate      # Check a recipe for errors
├── sources       # Manage data sources
│   ├── list      # List available sources
│   ├── search    # Search for sources
│   └── info      # Get info about a source
├── cache         # Manage local cache
│   ├── list      # List cached data
│   ├── clear     # Clear cache
│   └── path      # Show cache directory
└── config        # Manage configuration
    ├── show      # Show current config
    ├── set       # Set a config value
    └── path      # Show config file path
```

## Commands

### `strata new`

Launch the interactive TUI wizard to create a new recipe.

```bash
strata new [NAME]

# Examples
strata new                      # Start wizard, prompt for name
strata new champlain            # Start wizard with name preset
strata new --from template      # Start from a template
```

**Options:**
- `--from TEMPLATE` — Start from a template recipe
- `--output DIR` — Output directory (default: current)

### `strata build`

Build all outputs from a recipe file.

```bash
strata build RECIPE [OPTIONS]

# Examples
strata build champlain.strata.yaml
strata build champlain.strata.yaml --format svg
strata build champlain.strata.yaml --format svg --quality fine
strata build champlain.strata.yaml --output ./maps
strata build champlain.strata.yaml --layer towns --layer highways
```

**Options:**
- `--format FORMAT` — Only build specific format (svg, geojson, pmtiles)
- `--quality QUALITY` — Only build specific quality level
- `--layer LAYER` — Only build specific layer(s) (repeatable)
- `--output DIR` — Output directory (default: ./output)
- `--no-cache` — Don't use cached source data
- `--dry-run` — Show what would be built without building
- `--verbose` — Show detailed progress

**Output:**
```
$ strata build champlain.strata.yaml

Building champlain_region...

Fetching sources:
  ✓ vt_towns (cached)
  ✓ ny_towns (cached)
  ⠋ lake_champlain (downloading...)
  ✓ lake_champlain (1.2 MB)
  ✓ quebec_muni (cached)

Processing layers:
  ✓ regional_background (2,341 features)
  ✓ major_water (1 feature, 12 islands detected)
  ✓ towns (487 features, water cutouts applied)
  ✓ small_water (156 features)
  ✓ highways (892 features)

Rendering outputs:
  ✓ svg/ultra_fine (5 layers + combined)
  ✓ svg/fine (5 layers + combined)
  ✓ svg/medium (5 layers + combined)
  ✓ geojson (5 files)
  ✓ pmtiles (champlain_region.pmtiles)

Done! Output in: ./output/champlain_region/
```

### `strata fetch`

Download and cache sources without processing.

```bash
strata fetch RECIPE [OPTIONS]

# Examples
strata fetch champlain.strata.yaml
strata fetch champlain.strata.yaml --source vt_towns
```

**Options:**
- `--source SOURCE` — Only fetch specific source(s)
- `--force` — Re-download even if cached

### `strata preview`

Quick ASCII preview of a recipe's bounds and layers.

```bash
strata preview RECIPE

# Example output:
$ strata preview champlain.strata.yaml

champlain_region
Bounds: [-73.5, 43.0, -71.5, 45.2]

Layers (bottom to top):
  1. regional_background  ░░░░  2,341 features
  2. major_water          ████  1 feature
  3. towns                ▓▓▓▓  487 features
  4. small_water          ░░░░  156 features
  5. highways             ────  892 features

Sources: 8 defined, 5 cached
Output formats: svg (4 qualities), geojson, pmtiles
```

### `strata validate`

Check a recipe for errors without building.

```bash
strata validate RECIPE [OPTIONS]

# Examples
strata validate champlain.strata.yaml
strata validate champlain.strata.yaml --fix  # Launch interactive fixer
```

**Options:**
- `--fix` — Launch TUI to interactively fix errors
- `--json` — Output errors as JSON

**Output (errors):**
```
$ strata validate broken.strata.yaml

❌ Validation failed with 3 errors:

Line 24: Unknown field 'styel'
  Did you mean: 'style'?

Line 31: Source 'lake_chaplain' not defined
  Did you mean: 'lake_champlain'?

Line 45: Invalid bounds format
  Expected: [west, south, east, north]
  Got: [-73.5, 45.2, -71.5, 43.0] (south > north)

Run with --fix to repair interactively.
```

**Output (success):**
```
$ strata validate champlain.strata.yaml

✓ Recipe is valid

  8 sources defined
  5 layers defined
  3 output formats configured
  Estimated output: ~15 MB
```

### `strata sources`

Manage and explore data sources.

```bash
# List all available source types
strata sources list

# Search for sources
strata sources search "vermont water"
strata sources search --state VT --type water

# Get info about a specific source
strata sources info census:tiger/2023/vt/areawater
```

**Example output:**
```
$ strata sources list

Census TIGER (census:tiger)
  cousub        County subdivisions (towns)
  areawater     Lakes, ponds, reservoirs
  linearwater   Streams, rivers
  prisecroads   Primary/secondary roads
  county        County boundaries
  state         State boundaries

CanVec (canvec:)
  hydro/waterbody    Lakes and ponds
  hydro/river        Rivers and streams
  transport/road     Roads

Quebec Open Data (quebec:)
  municipalities     Municipal boundaries
  highways          Provincial highways

$ strata sources info census:tiger/2023/vt/areawater

census:tiger/2023/vt/areawater
Vermont Area Water Features (2023)

URL: https://www2.census.gov/geo/tiger/TIGER2023/AREAWATER/
Format: Shapefile (zipped)
Projection: NAD83 (EPSG:4269)
Features: ~2,400
Size: ~3.2 MB

Properties:
  HYDROID     Unique water feature ID
  FULLNAME    Feature name
  ALAND       Land area (sq meters)
  AWATER      Water area (sq meters)

Example filter:
  filter:
    HYDROID: "110469638395"  # Lake Champlain
```

### `strata cache`

Manage the local data cache.

```bash
# List cached data
strata cache list

# Clear all cached data
strata cache clear

# Clear specific source
strata cache clear census:tiger/2023/vt/areawater

# Show cache directory
strata cache path
```

**Example output:**
```
$ strata cache list

Cache directory: ~/.cache/strata (234 MB)

census:tiger/2023/vt/cousub      12 MB   2 days ago
census:tiger/2023/vt/areawater    3 MB   2 days ago
census:tiger/2023/ny/cousub      45 MB   1 week ago
quebec:municipalities            18 MB   3 days ago
canvec:hydro/waterbody          156 MB   1 week ago

Total: 5 sources, 234 MB
```

### `strata config`

Manage configuration.

```bash
# Show current config
strata config show

# Set a value
strata config set cache_dir ~/my-cache
strata config set default_projection epsg:32145

# Show config file location
strata config path
```

## Global Options

Available on all commands:

```bash
--help          Show help for command
--version       Show strata version
--verbose, -v   Increase verbosity (use -vv for debug)
--quiet, -q     Suppress non-error output
--no-color      Disable colored output
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid recipe |
| 3 | Source fetch failed |
| 4 | Processing failed |
| 5 | Output failed |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `STRATA_CACHE_DIR` | Override cache directory |
| `STRATA_CONFIG` | Override config file path |
| `STRATA_NO_COLOR` | Disable colors |
| `CENSUS_API_KEY` | Census API key (optional) |

## Shell Completion

```bash
# Bash
eval "$(_STRATA_COMPLETE=bash_source strata)"

# Zsh
eval "$(_STRATA_COMPLETE=zsh_source strata)"

# Fish
_STRATA_COMPLETE=fish_source strata | source
```

## Piping and Scripting

Commands are designed for unix pipelines:

```bash
# Build and pipe to vpype for plotter optimization
strata build map.strata.yaml --format svg --quality fine | \
  vpype read - linemerge linesort write optimized.svg

# List sources as JSON for scripting
strata sources list --json | jq '.census.types'

# Validate multiple recipes
for f in recipes/*.strata.yaml; do
  strata validate "$f" || echo "FAILED: $f"
done
```
