# Strata TUI Design

> "It is remarkable how long men will believe in the bottomlessness of a pond without taking the trouble to sound it." — Henry David Thoreau

## Overview

The Strata TUI provides a 1980s BIOS-style wizard experience for creating recipes and debugging configuration errors. Built with [Textual](https://textual.textualize.io/).

## Design Principles

1. **Keyboard-first** — Every action has a hotkey
2. **Progressive disclosure** — Simple defaults, advanced options available
3. **Immediate feedback** — Show what your choices mean
4. **Recoverable errors** — Never lose work, always offer fixes
5. **No mouse required** — Full functionality via keyboard

## Color Scheme

```
Background:   #1a1a2e (dark blue-black)
Foreground:   #eaeaea (off-white)
Accent:       #4fc3f7 (cyan)
Success:      #81c784 (green)
Warning:      #ffb74d (orange)
Error:        #e57373 (red)
Muted:        #666666 (gray)
Highlight:    #3d5a80 (blue highlight)
```

## Wizard Flow

```
strata new
    │
    ▼
┌─────────────┐
│  Welcome    │  Intro, name your recipe
└──────┬──────┘
       ▼
┌─────────────┐
│  Sources    │  Select data sources
└──────┬──────┘
       ▼
┌─────────────┐
│  Layers     │  Define layer operations
└──────┬──────┘
       ▼
┌─────────────┐
│  Output     │  Configure output formats
└──────┬──────┘
       ▼
┌─────────────┐
│  Review     │  Preview YAML, confirm
└──────┬──────┘
       ▼
    recipe.strata.yaml created!
```

## Screen Designs

### Welcome Screen (1/5)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗                                                          │
│  ╚═╗ ║ ╠╦╝╠═╣ ║ ╠═╣                                                          │
│  ╚═╝ ╩ ╩╚═╩ ╩ ╩ ╩ ╩  Recipe Wizard                              [1/5]       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Welcome! Let's create a new map recipe.                                     │
│                                                                              │
│  A recipe defines:                                                           │
│    • Where to get geographic data (sources)                                  │
│    • How to process it (layers with operations)                              │
│    • What to output (SVG, GeoJSON, tiles)                                    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Recipe name:                                                           │  │
│  │ ┌────────────────────────────────────────────────────────────────────┐ │  │
│  │ │ champlain_region_                                                  │ │  │
│  │ └────────────────────────────────────────────────────────────────────┘ │  │
│  │ (lowercase, underscores, used for output directory)                    │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Description (optional):                                                │  │
│  │ ┌────────────────────────────────────────────────────────────────────┐ │  │
│  │ │ Lake Champlain and surrounding towns                               │ │  │
│  │ └────────────────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [Tab] Next field   [Enter] Continue   [Esc] Cancel   [F1] Help              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Sources Screen (2/5)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  STRATA - Select Data Sources                                       [2/5]   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Select the data sources for your map:                                       │
│                                                                              │
│  Region: [Vermont & Neighbors ▼]                                             │
│                                                                              │
│  ┌─ US Census TIGER ─────────────────────────────────────────────────────┐   │
│  │ [x] Vermont Towns           census:tiger/2023/vt/cousub               │   │
│  │ [x] Vermont Water           census:tiger/2023/vt/areawater            │   │
│  │ [x] Vermont Roads           census:tiger/2023/vt/prisecroads          │   │
│  │ [x] New York Towns          census:tiger/2023/ny/cousub               │   │
│  │ [x] New York Water          census:tiger/2023/ny/areawater            │   │
│  │ [ ] New Hampshire Towns     census:tiger/2023/nh/cousub               │   │
│  │ [ ] Massachusetts Towns     census:tiger/2023/ma/cousub               │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ Canadian Data ───────────────────────────────────────────────────────┐   │
│  │ [x] Quebec Municipalities   quebec:municipalities                     │   │
│  │ [x] Quebec Highways         quebec:highways                           │   │
│  │ [ ] CanVec Water           canvec:hydro/waterbody                     │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ Custom ──────────────────────────────────────────────────────────────┐   │
│  │ [ + Add custom source... ]                                            │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Selected: 7 sources (~85 MB estimated)                                      │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [Space] Toggle   [/] Search   [Enter] Next   [Backspace] Back   [F1] Help   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Layers Screen (3/5)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  STRATA - Configure Layers                                          [3/5]   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Define how layers are processed and stacked (bottom to top):                │
│                                                                              │
│  ┌─ Layer Stack ─────────────────────────────────────────────────────────┐   │
│  │                                                                       │   │
│  │  5. ▲ highways            [vt_roads, quebec_highways]      [Edit]    │   │
│  │        Style: stroke #d32f2f, width 1.5                              │   │
│  │                                                                       │   │
│  │  4.   small_water         [vt_water, ny_water]             [Edit]    │   │
│  │        Operations: exclude lake_champlain                            │   │
│  │        Style: stroke #1976d2, width 0.5                              │   │
│  │                                                                       │   │
│  │  3.   towns               [vt_towns, ny_towns]             [Edit]    │   │
│  │  ───▶ Operations: subtract [lake_champlain, vt_water]  ◀── SELECTED  │   │
│  │        Style: stroke #7b1fa2, width 0.75                             │   │
│  │                                                                       │   │
│  │  2.   major_water         [lake_champlain]                 [Edit]    │   │
│  │        Operations: identify_islands, subtract islands                │   │
│  │        Style: stroke #0288d1, width 1.0                              │   │
│  │                                                                       │   │
│  │  1. ▼ regional_background [ny_towns, quebec_muni]          [Edit]    │   │
│  │        Style: stroke #8d6e63, width 0.5                              │   │
│  │                                                                       │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  [ + Add Layer ]                                                             │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [↑↓] Navigate  [Enter] Edit  [+] Add  [D] Delete  [U/J] Move  [F1] Help     │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Layer Edit Modal

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Edit Layer: towns                                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Name: [towns_______________]                                                │
│                                                                              │
│  Sources:                                                                    │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ [x] vt_towns                                                          │  │
│  │ [x] ny_towns                                                          │  │
│  │ [ ] nh_towns                                                          │  │
│  │ [ ] quebec_muni                                                       │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Operations:                                                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ 1. subtract: [lake_champlain, vt_water, ny_water]           [Edit] [X]│  │
│  │ 2. simplify: tolerance=0.0001, preserve_topology=true       [Edit] [X]│  │
│  │ [ + Add operation ]                                                   │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Style:                                                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Stroke: [#7b1fa2] ████  Width: [0.75]  Fill: [none]                   │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Preview: ──▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓──  (purple stroke, 0.75pt)             │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [Tab] Next field   [Enter] Save   [Esc] Cancel                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Output Screen (4/5)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  STRATA - Configure Output                                          [4/5]   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Bounds:                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ (•) Auto-detect from sources                                          │  │
│  │ ( ) From specific source: [vt_towns ▼]                                │  │
│  │ ( ) Manual: W[_______] S[_______] E[_______] N[_______]               │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Projection:                                                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ [EPSG:32145 - Vermont State Plane (meters) ▼]                         │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Output Formats:                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ [x] SVG (for pen plotters)                                            │  │
│  │     Quality levels: [x] ultra_fine [x] fine [x] medium [ ] coarse     │  │
│  │     Page size: [11 x 17 in ▼]  Optimize for: [Plotter ▼]              │  │
│  │                                                                       │  │
│  │ [x] GeoJSON (for web/analysis)                                        │  │
│  │     [x] Separate file per layer                                       │  │
│  │                                                                       │  │
│  │ [ ] PMTiles (for serverless web maps)                                 │  │
│  │     Zoom: min [4] max [14]                                            │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Estimated output size: ~45 MB                                               │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [Space] Toggle   [Tab] Next   [Enter] Next Step   [Backspace] Back          │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Review Screen (5/5)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  STRATA - Review Recipe                                             [5/5]   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─ champlain_region.strata.yaml ────────────────────────────────────────┐   │
│  │  1 │ name: champlain_region                                           │   │
│  │  2 │ description: Lake Champlain and surrounding towns                │   │
│  │  3 │ version: 1                                                       │   │
│  │  4 │                                                                  │   │
│  │  5 │ sources:                                                         │   │
│  │  6 │   vt_towns:                                                      │   │
│  │  7 │     uri: census:tiger/2023/vt/cousub                             │   │
│  │  8 │   ny_towns:                                                      │   │
│  │  9 │     uri: census:tiger/2023/ny/cousub                             │   │
│  │ 10 │   lake_champlain:                                                │   │
│  │ 11 │     uri: census:tiger/2023/vt/areawater                          │   │
│  │ 12 │     filter:                                                      │   │
│  │ 13 │       HYDROID: "110469638395"                                    │   │
│  │    │ ... (scroll for more)                                            │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Summary:                                                                    │
│    Sources: 7 defined                                                        │
│    Layers: 5 defined                                                         │
│    Output: SVG (3 qualities), GeoJSON                                        │
│    File: ./champlain_region.strata.yaml                                      │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [E] Edit in $EDITOR   [Enter] Create Recipe   [Backspace] Back   [Esc] Exit │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Config Debugger

Launched via `strata validate --fix` or when loading a malformed recipe.

### Error Overview Screen

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  STRATA - Configuration Errors                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ❌ Found 3 errors in champlain.strata.yaml                                  │
│                                                                              │
│  ┌─ Errors ──────────────────────────────────────────────────────────────┐   │
│  │                                                                       │   │
│  │  1. [Line 16] Unknown field 'styel'                          [Fix]   │   │
│  │     └─ Did you mean: 'style'?                                        │   │
│  │                                                                       │   │
│  │  2. [Line 24] Source 'lake_chaplain' not defined             [Fix]   │   │
│  │     └─ Did you mean: 'lake_champlain'?                               │   │
│  │                                                                       │   │
│  │  3. [Line 38] Invalid bounds: south > north                  [Fix]   │   │
│  │     └─ Values appear swapped                                         │   │
│  │                                                                       │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ Preview ─────────────────────────────────────────────────────────────┐   │
│  │  14 │     - name: towns                                               │   │
│  │  15 │       source: vt_towns                                          │   │
│  │▶ 16 │       styel: { stroke: "#333" }  ◀── ERROR                      │   │
│  │  17 │       order: 3                                                  │   │
│  │  18 │                                                                 │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [↑↓] Select   [Enter] Fix Selected   [A] Fix All   [E] Edit   [Q] Quit      │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Fix Modal

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Fix Error: Unknown field 'styel' (Line 16)                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Current:  styel: { stroke: "#333" }                                         │
│                                                                              │
│  Choose a fix:                                                               │
│                                                                              │
│    (•) Replace with 'style'                    ← Recommended                 │
│    ( ) Delete this line                                                      │
│    ( ) Keep as-is (will cause build error)                                   │
│    ( ) Enter custom replacement: [________________]                          │
│                                                                              │
│  Preview after fix:                                                          │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  15 │       source: vt_towns                                          │  │
│  │  16 │       style: { stroke: "#333" }  ◀── FIXED                      │  │
│  │  17 │       order: 3                                                  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [↑↓] Select   [Enter] Apply Fix   [Esc] Cancel                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

### Global
| Key | Action |
|-----|--------|
| `F1` | Help |
| `Esc` | Cancel / Back |
| `Ctrl+C` | Quit |
| `Ctrl+S` | Save (where applicable) |

### Navigation
| Key | Action |
|-----|--------|
| `Tab` | Next field |
| `Shift+Tab` | Previous field |
| `Enter` | Confirm / Next screen |
| `Backspace` | Previous screen |
| `↑` `↓` | Navigate lists |
| `Page Up/Down` | Scroll |

### Selection
| Key | Action |
|-----|--------|
| `Space` | Toggle checkbox |
| `a` | Select all |
| `n` | Select none |
| `/` | Search/filter |

### Editing
| Key | Action |
|-----|--------|
| `e` | Edit selected |
| `d` | Delete selected |
| `+` | Add new item |
| `u` / `k` | Move up |
| `j` / `d` | Move down |

## Implementation Notes

### Textual App Structure

```python
from textual.app import App
from textual.screen import Screen

class StrataWizard(App):
    SCREENS = {
        "welcome": WelcomeScreen,
        "sources": SourcesScreen,
        "layers": LayersScreen,
        "output": OutputScreen,
        "review": ReviewScreen,
    }

    BINDINGS = [
        ("f1", "help", "Help"),
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.recipe_data = RecipeBuilder()

    def on_mount(self):
        self.push_screen("welcome")
```

### State Management

Recipe data flows through screens via a shared `RecipeBuilder` object:

```python
class RecipeBuilder:
    name: str = ""
    description: str = ""
    sources: dict[str, SourceConfig] = {}
    layers: list[LayerConfig] = []
    output: OutputConfig = OutputConfig()

    def to_yaml(self) -> str:
        """Generate YAML from current state."""
        ...

    def validate(self) -> list[ValidationError]:
        """Check for errors."""
        ...
```

### CSS Theming

```css
/* strata.tcss */
Screen {
    background: #1a1a2e;
}

.title {
    color: #4fc3f7;
    text-style: bold;
}

.error {
    color: #e57373;
}

.success {
    color: #81c784;
}

Button {
    background: #3d5a80;
}

Button:hover {
    background: #4fc3f7;
    color: #1a1a2e;
}
```
