# TUI Golden Path Design

A design document for Strata's streamlined map creation workflow.

## Vision

Enable users to go from "I want a map of X" to a high-quality print-ready output in under 2 minutes, with visual feedback at every step.

---

## Core Principles

1. **Progressive Disclosure** - Start simple, reveal complexity only when needed
2. **Visual Feedback** - Show don't tell; render previews at every decision point
3. **Smart Defaults** - Make reasonable choices automatically, let users override
4. **Geographic Drill-Down** - Navigate spatially, not through menus

---

## Terminal Graphics Technology

### Options for High-Resolution Terminal Rendering

| Technology | Resolution | Terminal Support | Notes |
|------------|------------|------------------|-------|
| **Braille characters** | 2x4 dots per cell | Universal | ~160x80 "pixels" in 80x40 terminal |
| **Block elements** | 2x2 per cell | Universal | Half/quarter blocks, lower res than braille |
| **Sixel graphics** | True pixels | xterm, mlterm, foot | Legacy but wide support |
| **Kitty graphics protocol** | True pixels + alpha | Kitty, WezTerm | Modern, high quality |
| **iTerm2 inline images** | True pixels | iTerm2, VSCode | macOS focused |
| **Überzug++** | Overlay images | X11/Wayland | External process |

### Recommended Approach

**Primary**: Kitty graphics protocol via `term-image` or `pixcat`
- Works in Kitty, WezTerm (common dev terminals)
- Full color, arbitrary resolution
- Can overlay on Textual TUI

**Fallback**: Braille rendering via `drawille` or custom
- Universal terminal support
- Surprisingly good for geographic outlines
- ~160x80 effective resolution in standard terminal

**Detection**: Check `$TERM`, `$KITTY_WINDOW_ID`, `$WEZTERM_PANE` at startup

### Python Libraries to Evaluate

```
term-image          # Multi-protocol image rendering
plotext             # Braille/block plotting
drawille            # Braille canvas
rich                # Has basic image support
chafa               # CLI tool, Python bindings available
```

---

## Geographic Drill-Down Model

### Hierarchy Concept

```
World
├── North America
│   ├── Canada
│   │   ├── British Columbia
│   │   ├── Ontario
│   │   ├── Quebec
│   │   │   ├── Montérégie
│   │   │   ├── Montréal
│   │   │   └── ...
│   │   └── ...
│   ├── United States
│   │   ├── Northeast
│   │   │   ├── Vermont
│   │   │   │   ├── Chittenden County
│   │   │   │   │   ├── Burlington
│   │   │   │   │   ├── South Burlington
│   │   │   │   │   ├── Winooski
│   │   │   │   │   └── ...
│   │   │   │   ├── Washington County
│   │   │   │   └── ...
│   │   │   ├── New Hampshire
│   │   │   └── ...
│   │   └── ...
│   └── Mexico
└── ...
```

### Navigation Modes

#### Mode 1: Hierarchical Browse
```
┌─ Select Region ─────────────────────────────────────────────┐
│                                                             │
│  ◉ North America          ┌─────────────────────────────┐  │
│    ○ South America        │     ╭───╮                   │  │
│    ○ Europe               │   ╭─╯   ╰─╮    ▪ CANADA     │  │
│    ○ Asia                 │  ╭╯       ╰╮               │  │
│    ○ Africa               │  │   USA    │               │  │
│    ○ Oceania              │  ╰╮       ╭╯               │  │
│                           │   ╰─╮ ╭──╯    ▪ MEXICO     │  │
│  [↑↓] Navigate            │     ╰─╯                     │  │
│  [Enter] Drill down       └─────────────────────────────┘  │
│  [Backspace] Go up                                          │
└─────────────────────────────────────────────────────────────┘
```

#### Mode 2: Search + Autocomplete
```
┌─ Find Location ─────────────────────────────────────────────┐
│                                                             │
│  > burling_                                                 │
│                                                             │
│    Burlington, VT, USA                                      │
│    Burlington, Ontario, Canada                              │
│    Burlington, NC, USA                                      │
│    Burlington County, NJ, USA                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Mode 3: Multi-Select Within Level
```
┌─ Chittenden County Towns ───────────────────────────────────┐
│                                                             │
│  [✓] Burlington         ┌─────────────────────────────────┐│
│  [✓] South Burlington   │    ┌───┐                        ││
│  [✓] Winooski           │ ┌──┤ W ├──┐    Selected: 5     ││
│  [✓] Colchester         │ │ B├───┤SB│    Area: 89 sq mi  ││
│  [✓] Essex              │ │  │ C │  │                     ││
│  [ ] Williston          │ └──┤   ├──┘                     ││
│  [ ] Shelburne          │    │ E │                        ││
│  [ ] Charlotte          │    └───┘                        ││
│                         └─────────────────────────────────┘│
│  [Space] Toggle  [a] Select all  [Enter] Confirm           │
└─────────────────────────────────────────────────────────────┘
```

### Data Requirements

For drill-down to work, we need boundary data at each level:

| Level | Source | Notes |
|-------|--------|-------|
| Continents | Natural Earth 110m | 7 features |
| Countries | Natural Earth 10m | ~250 features |
| US States | Census TIGER | 56 features |
| US Counties | Census TIGER | ~3,200 features |
| US County Subdivisions | Census TIGER | ~36,000 features |
| Canada Provinces | StatCan | 13 features |
| Canada Census Divisions | StatCan | ~300 features |
| Quebec Municipalities | MERN | ~1,100 features |

**Caching Strategy**: Pre-cache simplified boundaries for navigation; fetch full detail on selection.

---

## Scale-Aware Data Selection

### Problem

Different zoom levels need different data:
- World map → Country outlines only
- State map → Counties, major water, highways
- City map → All roads, buildings, parks

### Solution: Scale Presets

```python
SCALE_PRESETS = {
    "continental": {
        "min_area_km2": 10000,
        "simplify_tolerance": 0.1,
        "suggested_layers": ["countries", "major_water"],
    },
    "regional": {
        "min_area_km2": 100,
        "simplify_tolerance": 0.01,
        "suggested_layers": ["states", "counties", "lakes", "rivers"],
    },
    "local": {
        "min_area_km2": 1,
        "simplify_tolerance": 0.001,
        "suggested_layers": ["towns", "all_water", "roads"],
    },
    "detail": {
        "min_area_km2": 0,
        "simplify_tolerance": 0.0001,
        "suggested_layers": ["parcels", "buildings", "trails"],
    },
}
```

### Auto-Detection

Based on selected bounds area:
- \> 1M km² → Continental
- 10K - 1M km² → Regional
- 100 - 10K km² → Local
- < 100 km² → Detail

---

## Crop/Bounds Workflow

### Step 1: Coarse Selection via Drill-Down
User navigates hierarchy to select a region (e.g., "Chittenden County")

### Step 2: Fine Crop Adjustment
```
┌─ Adjust Crop Area ──────────────────────────────────────────┐
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    ▲                                 │   │
│  │        ╔═══════════════════════╗                    │   │
│  │      ◄ ║   SELECTED AREA      ║ ►                   │   │
│  │        ║                       ║                    │   │
│  │        ║     Burlington        ║                    │   │
│  │        ║         ⊕             ║                    │   │
│  │        ╚═══════════════════════╝                    │   │
│  │                    ▼                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Bounds: -73.25, 44.42, -73.15, 44.52                      │
│  Size: 5.2 × 7.1 miles (8.4 × 11.4 km)                     │
│                                                             │
│  [←→↑↓] Move  [+/-] Zoom  [Shift+Arrow] Resize  [Enter] OK │
└─────────────────────────────────────────────────────────────┘
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| Arrow keys | Pan view |
| Shift + Arrow | Resize crop box |
| `+` / `-` | Zoom in/out |
| `[` / `]` | Aspect ratio presets (letter, tabloid, square) |
| `c` | Center crop on cursor |
| `f` | Fit crop to selected features |
| `Enter` | Confirm bounds |

---

## Layer Auto-Configuration

### Based on Scale + Region

When user selects "Burlington area at local scale":

```yaml
# Auto-suggested layers:
layers:
  - name: town_boundaries
    source: census:tiger/2023/vt/cousub
    style: {stroke: "#424242", fill: "#f5f5f5"}

  - name: lakes
    source: census:tiger/2023/vt/areawater
    style: {stroke: "#1565c0", fill: "#b3e5fc"}
    operations: [{type: filter, min_area_sqm: 10000}]

  - name: rivers
    source: census:tiger/2023/vt/linearwater
    style: {stroke: "#1976d2", stroke_width: 1}

  - name: roads
    source: census:tiger/2023/vt/prisecroads
    style: {stroke: "#757575", stroke_width: 0.5}
```

### User Adjustments

```
┌─ Layer Configuration ───────────────────────────────────────┐
│                                                             │
│  Suggested layers for Burlington area:                      │
│                                                             │
│  [✓] Town boundaries    [████] #f5f5f5   [Simplify: 0.001] │
│  [✓] Lakes & ponds      [████] #b3e5fc   [Min area: 10000] │
│  [✓] Rivers & streams   [────] #1976d2   [Width: 1.0]      │
│  [✓] Roads              [────] #757575   [Width: 0.5]      │
│  [ ] Trails             [····] #4caf50   (not cached)      │
│  [ ] Buildings          [████] #9e9e9e   (not cached)      │
│                                                             │
│  [+] Add custom layer   [Auto] Reset to suggestions        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Output Generation

### PDF/Raster Comparison Needed

#### CairoSVG
```python
import cairosvg
cairosvg.svg2pdf(url="map.svg", write_to="map.pdf")
cairosvg.svg2png(url="map.svg", write_to="map.png", dpi=300)
```
- Pure Python (via cairocffi)
- Good SVG support
- May struggle with very complex paths

#### Inkscape CLI
```bash
inkscape map.svg --export-type=pdf --export-filename=map.pdf
inkscape map.svg --export-type=png --export-dpi=300 --export-filename=map.png
```
- Best SVG compatibility
- Requires Inkscape installed
- Slower startup but excellent output

#### Evaluation Criteria
- [ ] Complex path handling (thousands of polygons)
- [ ] Text rendering quality
- [ ] Pattern fill support
- [ ] File size comparison
- [ ] Processing speed
- [ ] Memory usage with large SVGs

### Output Options UI

```
┌─ Output Settings ───────────────────────────────────────────┐
│                                                             │
│  Format:                                                    │
│    (•) PDF - Print ready, vector                           │
│    ( ) PNG - Raster image                                  │
│    ( ) SVG - For plotters/editing                          │
│    ( ) GeoJSON - For web maps                              │
│                                                             │
│  Page Size:            Quality:                             │
│    (•) 12" × 18"         (•) Print (300 DPI)               │
│    ( ) 18" × 24"         ( ) Web (150 DPI)                 │
│    ( ) 24" × 36"         ( ) Draft (72 DPI)                │
│    ( ) Custom: [__] × [__]                                 │
│                                                             │
│  Margin: [0.5] inches                                       │
│                                                             │
│  [ ] Include plotter fill patterns                         │
│  [ ] Include legend                                         │
│  [ ] Include scale bar                                      │
│                                                             │
│  Output: ~/Maps/burlington_2025.pdf                        │
│                                                             │
│  [Preview]                    [Build]                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Preview System

### Quick Preview (During Navigation)

Lightweight rendering for responsiveness:
- Simplified geometries (aggressive tolerance)
- Limited feature count (first 1000)
- Braille/block rendering for universal support
- Updates on every bounds change

### Full Preview (Before Build)

Higher fidelity check before committing:
- Actual geometries at target simplification
- Kitty/iTerm2 graphics if available
- Shows exact feature counts
- Warns about potential issues (too many features, missing data)

### Preview Data Structure

```python
@dataclass
class PreviewData:
    bounds: tuple[float, float, float, float]
    features_by_layer: dict[str, int]
    estimated_file_size_mb: float
    estimated_build_time_sec: float
    warnings: list[str]
    thumbnail: bytes  # PNG data for terminal display
```

---

## Workflow State Machine

```
                    ┌──────────────┐
                    │    START     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
              ┌─────│   BROWSE     │◄────────────┐
              │     │  (Drill-down) │             │
              │     └──────┬───────┘             │
              │            │ [Enter]             │
              │            ▼                     │
              │     ┌──────────────┐             │
              │     │   SELECT     │             │
              │     │  (Multi-pick)│             │
              │     └──────┬───────┘             │
              │            │ [Enter]             │
              │            ▼                     │
              │     ┌──────────────┐             │
    [Backspace]     │    CROP      │             │
              │     │ (Fine-tune)  │             │
              │     └──────┬───────┘             │
              │            │ [Enter]             │
              │            ▼                     │
              │     ┌──────────────┐             │
              │     │   LAYERS     │─────────────┘
              │     │ (Configure)  │  [Backspace]
              │     └──────┬───────┘
              │            │ [Enter]
              │            ▼
              │     ┌──────────────┐
              └────►│   OUTPUT     │
                    │  (Generate)  │
                    └──────┬───────┘
                           │ [Build]
                           ▼
                    ┌──────────────┐
                    │    DONE      │
                    └──────────────┘
```

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Terminal graphics detection (Kitty, iTerm2, Sixel, fallback)
- [ ] Graphics abstraction layer (render same content to any protocol)
- [ ] Braille renderer for geographic outlines (universal fallback)
- [ ] Geographic hierarchy data structure
- [ ] Simplified boundary data for navigation (bundled or fetched)

### Phase 2: Drill-Down Navigation
- [ ] Hierarchical browse screen (World → Continent → Country → State → County → Town)
- [ ] Visual preview updates at each level
- [ ] Multi-select within a level
- [ ] Search/filter within current level
- [ ] Scale auto-detection from selection

### Phase 3: Visual Crop
- [ ] Bounds preview rendering (show selected features)
- [ ] Keyboard-driven crop adjustment (arrows, shift+arrows)
- [ ] Aspect ratio presets (letter, tabloid, square)
- [ ] Real-time coordinate and area display
- [ ] Padding controls

### Phase 4: Cache Management
- [ ] Cache dashboard screen (list sources, sizes, last used)
- [ ] Delete individual cached sources
- [ ] Pre-cache by region
- [ ] Cache status indicators throughout TUI (●/○/◐)
- [ ] Config file for cache settings

### Phase 5: Layer Configuration
- [ ] Scale-aware layer suggestions
- [ ] Quick toggle interface with style preview
- [ ] Layer reordering
- [ ] Basic style editing (colors, widths)

### Phase 6: Output Generation
- [ ] Cairo vs Inkscape comparison testing
- [ ] PDF generation pipeline
- [ ] PNG export with DPI options
- [ ] SVG (existing) improvements
- [ ] Progress indication

### Phase 7: Batch Mode
- [ ] Batch selection screen (select parent, choose children)
- [ ] Filter by sub-region (e.g., by county)
- [ ] Batch output configuration (bounds mode, padding, naming)
- [ ] Batch progress screen
- [ ] Batch recipe YAML schema
- [ ] CLI `strata batch` command

### Phase 8: Polish (Lower Priority)
- [ ] State persistence / resume workflows
- [ ] Recent maps / favorites
- [ ] Template system
- [ ] Error recovery
- [ ] SSH/degraded terminal support

---

## Cache Management

### The Problem

GIS data adds up fast:
- Census TIGER for one state: ~50-200 MB
- All 50 states: ~5-10 GB
- Canada CanVec hydro: ~150 MB
- OpenSkiMap worldwide: ~200 MB

Users need visibility into what they've downloaded and control over storage.

### Cache Dashboard Screen

```
┌─ Data Cache ────────────────────────────────────────────────┐
│                                                             │
│  Cache Location: ~/Library/Caches/strata/                   │
│  Total Size: 847 MB                                         │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ SOURCE                        SIZE      LAST USED       ││
│  │─────────────────────────────────────────────────────────││
│  │ [✓] census/tiger/2023/vt      156 MB    2 hours ago     ││
│  │ [✓] census/tiger/2023/nh       98 MB    3 days ago      ││
│  │ [✓] census/tiger/2023/ny      312 MB    1 week ago      ││
│  │ [✓] quebec/municipalities      47 MB    2 weeks ago     ││
│  │ [✓] canada/canvec/hydro       148 MB    1 month ago     ││
│  │ [ ] openskimap (not cached)     —       —               ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  [Space] Toggle  [d] Delete selected  [D] Delete all       │
│  [r] Refresh     [p] Pre-cache region  [q] Back            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Pre-Cache by Region

Allow users to download all data for a region before going offline:

```
┌─ Pre-Cache Region ──────────────────────────────────────────┐
│                                                             │
│  Select region to cache:                                    │
│                                                             │
│    (•) Vermont (all layers)           ~156 MB              │
│    ( ) New England (6 states)         ~890 MB              │
│    ( ) Northeast US (9 states)        ~1.4 GB              │
│    ( ) Quebec                         ~85 MB               │
│    ( ) Custom selection...                                  │
│                                                             │
│  Layers to include:                                         │
│    [✓] County subdivisions (towns)                         │
│    [✓] Area water (lakes, ponds)                           │
│    [✓] Linear water (rivers, streams)                      │
│    [✓] Roads (primary & secondary)                         │
│    [ ] Counties                                             │
│    [ ] Census tracts                                        │
│                                                             │
│  Estimated download: 156 MB                                 │
│  Estimated time: ~2 minutes                                 │
│                                                             │
│  [Enter] Start download    [Escape] Cancel                  │
└─────────────────────────────────────────────────────────────┘
```

### Cache Status Indicators

Throughout the TUI, show cache status:

```
Source Browser:
  ● Vermont Towns (cached, 23 MB)
  ○ Vermont Roads (not cached, ~45 MB)
  ◐ New Hampshire (partial, 12/45 MB)
```

### Cache Location & Config

```yaml
# ~/.config/strata/config.yaml
cache:
  path: ~/Library/Caches/strata/
  max_size_gb: 10          # Warn when approaching
  auto_cleanup_days: 90    # Remove unused after N days
  prefer_offline: false    # Use cached even if stale
```

---

## Batch Mode

### Use Case

"I want to make individual maps for all 251 towns in Vermont" or "Generate a map for each county in the selected state."

### Workflow

1. User navigates drill-down to select a **parent region** (e.g., Vermont)
2. User chooses **"Batch: One map per child"**
3. System shows list of children (251 towns)
4. User configures layers & output settings ONCE
5. System generates 251 maps with consistent styling

### Batch Selection Screen

```
┌─ Batch Mode ────────────────────────────────────────────────┐
│                                                             │
│  Parent Region: Vermont                                     │
│  Batch by: County Subdivisions (Towns)                      │
│                                                             │
│  Found 251 towns. Select which to include:                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ [✓] Addison           [✓] Highgate        [✓] Rutland   ││
│  │ [✓] Albany            [✓] Hinesburg       [✓] Ryegate   ││
│  │ [✓] Alburgh           [✓] Holland         [✓] St. Albans││
│  │ [✓] Andover           [✓] Hubbardton      [✓] St. George││
│  │ ... (251 total)                                         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  Quick select:                                              │
│    [a] All    [n] None    [c] By county...    [f] Filter...│
│                                                             │
│  Selected: 251 of 251                                       │
│                                                             │
│  [Enter] Configure layers    [Escape] Back                  │
└─────────────────────────────────────────────────────────────┘
```

### Batch by County Filter

```
┌─ Select by County ──────────────────────────────────────────┐
│                                                             │
│  [✓] Addison County (23 towns)                             │
│  [✓] Bennington County (17 towns)                          │
│  [✓] Caledonia County (17 towns)                           │
│  [ ] Chittenden County (18 towns)                          │
│  [ ] Essex County (9 towns)                                │
│  ...                                                        │
│                                                             │
│  Selected: 57 towns across 3 counties                       │
└─────────────────────────────────────────────────────────────┘
```

### Batch Output Configuration

```
┌─ Batch Output Settings ─────────────────────────────────────┐
│                                                             │
│  Generating 251 maps...                                     │
│                                                             │
│  Bounds per map:                                            │
│    (•) Fit to feature bounds (auto-crop each)              │
│    ( ) Fixed size centered on feature                       │
│    ( ) Uniform bounds (same crop for all)                  │
│                                                             │
│  Padding: [10] % around each feature                        │
│                                                             │
│  Context layers (appear in all maps):                       │
│    [✓] Neighboring towns (ghosted)                         │
│    [✓] Water bodies                                         │
│    [ ] Roads                                                │
│                                                             │
│  Naming pattern:                                            │
│    vermont_towns/{name}.pdf                                 │
│    Preview: vermont_towns/burlington.pdf                    │
│                                                             │
│  Output: ~/Maps/vermont_towns/                              │
│  Estimated: 251 files, ~125 MB total                        │
│  Estimated time: ~8 minutes                                 │
│                                                             │
│  [Enter] Start batch    [p] Preview first 3    [Escape] Back│
└─────────────────────────────────────────────────────────────┘
```

### Batch Progress

```
┌─ Batch Processing ──────────────────────────────────────────┐
│                                                             │
│  Processing 251 town maps...                                │
│                                                             │
│  [████████████████░░░░░░░░░░░░░░░░░░░░░░░░] 42%            │
│                                                             │
│  Current: Middlebury (106 of 251)                          │
│  Elapsed: 3:24                                              │
│  Remaining: ~4:42                                           │
│                                                             │
│  ✓ 105 completed                                            │
│  ⚠ 0 warnings                                               │
│  ✗ 0 errors                                                 │
│                                                             │
│  Recent:                                                    │
│    ✓ ludlow.pdf (245 KB)                                   │
│    ✓ lyndon.pdf (312 KB)                                   │
│    ✓ maidstone.pdf (89 KB)                                 │
│    → middlebury.pdf (processing...)                        │
│                                                             │
│  [Space] Pause    [Escape] Cancel (keeps completed)        │
└─────────────────────────────────────────────────────────────┘
```

### Batch Recipe YAML

For reproducibility, batch mode generates a special recipe:

```yaml
name: vermont_towns_batch
description: Individual maps for all Vermont towns
version: 1
batch:
  mode: per_feature
  source: census:tiger/2023/vt/cousub
  name_field: NAME
  output_pattern: "{name}.pdf"
  bounds_mode: fit_with_padding
  padding_percent: 10

sources:
  vt_towns:
    uri: census:tiger/2023/vt/cousub
  vt_water:
    uri: census:tiger/2023/vt/areawater
  vt_neighbors:
    uri: census:tiger/2023/vt/cousub
    role: context  # Ghosted in background

layers:
  - name: neighbors
    source: vt_neighbors
    style: {stroke: "#e0e0e0", fill: "#fafafa"}
    filter: "NAME != {batch.current.NAME}"  # Exclude current feature

  - name: water
    source: vt_water
    style: {stroke: "#1565c0", fill: "#b3e5fc"}

  - name: focus
    source: vt_towns
    filter: "NAME == {batch.current.NAME}"  # Only current feature
    style: {stroke: "#424242", fill: "#ffffff", stroke_width: 2}

output:
  formats:
    - type: pdf
      options: {page_size: [8.5, 11], margin: 0.5}
```

### CLI Support for Batch

```bash
# Run batch from recipe
strata batch examples/vermont_towns_batch.strata.yaml -o output/

# Quick batch from selections
strata batch --parent "Vermont" --by cousub --format pdf -o output/

# List what would be generated
strata batch examples/vermont_towns_batch.strata.yaml --dry-run
```

---

## Design Decisions

1. **Online-First with Cache Management**: Tool requires internet for fetching. Users can cache data for offline use. TUI includes cache management screen showing what's downloaded and disk usage.

2. **State Persistence**: Lower priority. Defer to Phase 5.

3. **Batch Mode**: HIGH PRIORITY. Enable "make 50 town maps" from TUI selections. See Batch Mode section below.

4. **Mobile/SSH**: Low priority. Basic functionality should work, but advanced graphics are not required.

5. **Pattern Fills**: Defer. Focus on solid fills and paths first. Plotter patterns are an output option, not a TUI preview concern.

---

## References

- [Textual](https://textual.textualize.io/) - TUI framework
- [term-image](https://github.com/AnonymouX47/term-image) - Terminal image rendering
- [drawille](https://github.com/asciimoo/drawille) - Braille canvas
- [Kitty Graphics Protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/)
- [Natural Earth](https://www.naturalearthdata.com/) - Global boundary data
- [CairoSVG](https://cairosvg.org/) - SVG conversion
