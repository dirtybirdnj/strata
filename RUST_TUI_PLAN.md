# Strata Rust TUI Implementation Plan

## Executive Summary

Replace the Python Textual TUI with a Rust TUI built on rat-king's architecture. The Python GIS pipeline remains unchanged - the Rust TUI acts as an interactive frontend that:
1. Browses data sources and previews bounds
2. Configures layers with live SVG preview
3. Generates YAML recipes
4. Invokes the Python `strata build` command

## Why Rust TUI?

| Aspect | Python (Textual) | Rust (ratatui) |
|--------|------------------|----------------|
| SVG Preview | Not possible | Sixel rendering via resvg |
| Responsiveness | ~100ms input lag | <16ms input lag |
| Image display | ASCII art only | Full color Sixel/Kitty |
| Zoom/Pan | Would need external viewer | Built-in, hardware accelerated |
| Background tasks | asyncio complexity | Simple thread + channel |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Strata Rust TUI                              │
│  ┌──────────────┐  ┌──────────────────────────────────────────┐ │
│  │   Sidebar    │  │           Main Preview Area              │ │
│  │              │  │                                          │ │
│  │ Sources      │  │   ┌──────────────────────────────────┐   │ │
│  │ ├─ Census    │  │   │                                  │   │ │
│  │ │  └─ VT     │  │   │     Live SVG Map Preview         │   │ │
│  │ │  └─ NY     │  │   │     (Sixel rendered)             │   │ │
│  │ ├─ Quebec    │  │   │                                  │   │ │
│  │ └─ Canada    │  │   │     [Bounds rectangle overlay]   │   │ │
│  │              │  │   │                                  │   │ │
│  │ Layers       │  │   └──────────────────────────────────┘   │ │
│  │ ├─ towns     │  │                                          │ │
│  │ ├─ water     │  │   Bounds: -73.5, 42.7 to -71.5, 45.0     │ │
│  │ └─ roads     │  │   Zoom: 100%  Features: 2,341            │ │
│  │              │  └──────────────────────────────────────────┘ │
│  │ Settings     │                                               │
│  │ ├─ Bounds    │  ┌──────────────────────────────────────────┐ │
│  │ ├─ Output    │  │ [Tab] Navigate  [←→] Adjust  [Enter] OK  │ │
│  │ └─ Format    │  │ [Space] Toggle  [B] Set Bounds  [S] Save │ │
│  └──────────────┘  └──────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Crate Structure

```
strata-tui/
├── Cargo.toml
├── src/
│   ├── main.rs              # Entry point, terminal setup
│   ├── app.rs               # App state, event loop
│   ├── ui/
│   │   ├── mod.rs
│   │   ├── layout.rs        # Main layout (sidebar + content)
│   │   ├── sidebar.rs       # Source browser, layer list, settings
│   │   ├── preview.rs       # SVG map preview with Sixel
│   │   ├── bounds.rs        # Interactive bounds editor
│   │   └── status.rs        # Bottom status bar
│   ├── data/
│   │   ├── mod.rs
│   │   ├── sources.rs       # Source catalog (mirrors Python)
│   │   ├── loader.rs        # GeoJSON/Shapefile loading
│   │   └── cache.rs         # Cache path resolution
│   ├── render/
│   │   ├── mod.rs
│   │   ├── svg.rs           # GeoJSON → SVG conversion
│   │   ├── style.rs         # Layer styling
│   │   └── bounds.rs        # Bounds clipping
│   └── recipe/
│       ├── mod.rs
│       ├── model.rs         # Recipe data structures
│       └── yaml.rs          # YAML serialization
```

## Key Components

### 1. App State (from rat-king pattern)

```rust
pub struct App {
    // Navigation
    focus: Focus,              // Sidebar, Preview, or Settings
    sidebar_state: SidebarState,

    // Data
    sources: Vec<SourceEntry>,
    layers: Vec<LayerConfig>,
    bounds: Option<Bounds>,

    // Preview rendering
    preview_svg: Option<String>,
    preview_tree: Option<usvg::Tree>,
    image_state: Option<Box<dyn StatefulProtocol>>,

    // View transforms (from rat-king)
    zoom: f64,
    pan_x: f64,
    pan_y: f64,

    // Background loading
    loader_tx: Sender<LoadRequest>,
    loader_rx: Receiver<LoadResult>,
    is_loading: bool,

    // Recipe output
    recipe_name: String,
    output_dir: String,
}

pub enum Focus {
    SourceBrowser,
    LayerList,
    Settings,
    Preview,
    BoundsEditor,
}
```

### 2. Source Browser

Tree view of available data sources (mirrors Python catalog):

```rust
pub struct SourceBrowser {
    tree: Vec<SourceNode>,
    expanded: HashSet<String>,
    selected: Option<String>,
    list_state: ListState,
}

pub struct SourceNode {
    id: String,           // "census:tiger/2023/vt/cousub"
    label: String,        // "Vermont Towns"
    children: Vec<SourceNode>,
    is_leaf: bool,
    cached: bool,         // Already downloaded?
}

// Tree structure:
// Census TIGER
// ├─ Vermont
// │  ├─ Towns (cousub)      ✓ cached
// │  ├─ Water (areawater)   ✓ cached
// │  └─ Roads (prisecroads)
// ├─ New York
// │  └─ ...
// Quebec
// ├─ Municipalities         ✓ cached
// └─ MRC
// Canada
// ├─ CanVec Hydro
// └─ NRN Roads
//    ├─ Quebec
//    └─ Ontario
```

### 3. Live Preview Rendering

Adapts rat-king's SVG pipeline for geographic data:

```rust
pub struct PreviewRenderer {
    // Cached data
    loaded_sources: HashMap<String, GeoData>,

    // SVG generation
    svg_builder: SvgBuilder,

    // Rendering (from rat-king)
    cached_tree: Option<usvg::Tree>,
    pixmap: Option<tiny_skia::Pixmap>,
}

impl PreviewRenderer {
    /// Generate SVG from loaded GeoJSON sources
    pub fn render_preview(
        &mut self,
        layers: &[LayerConfig],
        bounds: &Bounds,
        width: u32,
        height: u32,
    ) -> Result<tiny_skia::Pixmap> {
        // 1. Build SVG string from GeoJSON features
        let svg = self.svg_builder.build(layers, bounds)?;

        // 2. Parse to usvg tree (cached)
        let tree = usvg::Tree::from_str(&svg, &usvg::Options::default())?;

        // 3. Render with zoom/pan transform (from rat-king)
        let mut pixmap = tiny_skia::Pixmap::new(width, height)?;
        let transform = self.compute_transform(bounds, width, height);
        resvg::render(&tree, transform, &mut pixmap.as_mut());

        Ok(pixmap)
    }
}
```

### 4. Interactive Bounds Editor

Key feature that Python TUI couldn't do well:

```rust
pub struct BoundsEditor {
    // Current bounds
    west: f64,
    south: f64,
    east: f64,
    north: f64,

    // Editing state
    active_handle: Option<Handle>,  // Which corner/edge being dragged
    drag_start: Option<(f64, f64)>,

    // Presets
    presets: Vec<BoundsPreset>,
}

pub enum Handle {
    Northwest, North, Northeast,
    West, Center, East,
    Southwest, South, Southeast,
}

// Visual overlay on preview:
// ┌───────────────────────────┐
// │                           │
// │    ┌─────────────┐        │
// │    │  ◆ Bounds ◆ │        │  ◆ = draggable handle
// │    │             │        │
// │    └─────────────┘        │
// │                           │
// └───────────────────────────┘
```

### 5. Background Data Loading

Uses rat-king's thread + channel pattern:

```rust
pub enum LoadRequest {
    FetchSource { uri: String },
    LoadCached { uri: String, path: PathBuf },
}

pub enum LoadResult {
    SourceLoaded { uri: String, data: GeoData },
    SourceError { uri: String, error: String },
    Progress { uri: String, percent: u8 },
}

// In app event loop (from rat-king):
fn check_load_results(&mut self) {
    while let Ok(result) = self.loader_rx.try_recv() {
        match result {
            LoadResult::SourceLoaded { uri, data } => {
                self.sources_loaded.insert(uri, data);
                self.needs_preview_update = true;
            }
            LoadResult::Progress { uri, percent } => {
                self.update_progress(&uri, percent);
            }
            // ...
        }
    }
}
```

## Integration with Python Pipeline

The Rust TUI doesn't replace Python - it orchestrates it:

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Rust TUI       │     │  Python Strata   │     │    Output        │
│                  │     │                  │     │                  │
│  Configure map   │────>│  strata build    │────>│  SVG files       │
│  Set bounds      │     │  recipe.yaml     │     │  GeoJSON         │
│  Pick layers     │     │                  │     │  Plotter fills   │
│  Save YAML       │     │  (GIS pipeline)  │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        │                         ▲
        │    Recipe YAML          │
        └─────────────────────────┘
```

### Cache Sharing

Both use the same cache directory:
```rust
fn get_cache_dir() -> PathBuf {
    // Same as Python: ~/Library/Caches/strata/
    dirs::cache_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join("strata")
}
```

### Recipe Generation

```rust
impl App {
    fn save_recipe(&self) -> Result<PathBuf> {
        let recipe = Recipe {
            name: self.recipe_name.clone(),
            description: String::new(),
            version: 1,
            sources: self.build_sources_map(),
            layers: self.build_layers_vec(),
            output: OutputConfig {
                bounds: self.bounds.clone(),
                projection: "epsg:4326".into(),
                formats: vec![SvgFormat::default()],
            },
        };

        let yaml = serde_yaml::to_string(&recipe)?;
        let path = PathBuf::from(&self.output_dir)
            .join(format!("{}.strata.yaml", self.recipe_name));
        std::fs::write(&path, yaml)?;
        Ok(path)
    }

    fn run_build(&self) -> Result<()> {
        let recipe_path = self.save_recipe()?;
        Command::new("strata")
            .args(["build", recipe_path.to_str().unwrap()])
            .spawn()?;
        Ok(())
    }
}
```

## Dependencies

```toml
[package]
name = "strata-tui"
version = "0.1.0"
edition = "2021"

[dependencies]
# TUI (from rat-king)
ratatui = "0.28"
crossterm = "0.28"
ratatui-image = "1.0"

# SVG rendering (from rat-king)
resvg = "0.45"
usvg = "0.45"
tiny-skia = "0.11"

# Image handling
image = "0.25"

# GeoJSON parsing
geojson = "0.24"
geo = "0.28"
geo-types = "0.7"

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_yaml = "0.9"
serde_json = "1.0"

# Utilities
anyhow = "1.0"
thiserror = "1.0"
dirs = "5.0"
```

## Implementation Phases

### Phase 1: Core TUI Shell (1-2 days)
- [ ] Basic ratatui app with layout from rat-king
- [ ] Sidebar with placeholder sections
- [ ] Bottom status bar with key hints
- [ ] Event loop with quit/navigation

### Phase 2: Source Browser (2-3 days)
- [ ] Tree view of source catalog
- [ ] Expand/collapse nodes
- [ ] Cache status indicators
- [ ] Source selection

### Phase 3: Preview Rendering (3-4 days)
- [ ] GeoJSON → SVG conversion
- [ ] Sixel rendering (port from rat-king)
- [ ] Zoom/pan controls
- [ ] Debounced updates

### Phase 4: Bounds Editor (2-3 days)
- [ ] Interactive bounds rectangle
- [ ] Draggable handles
- [ ] Coordinate display
- [ ] Preset bounds (Vermont, Lake Champlain, etc.)

### Phase 5: Layer Configuration (2-3 days)
- [ ] Layer list with ordering
- [ ] Style settings (color, width)
- [ ] Visibility toggle
- [ ] Operations preview

### Phase 6: Recipe Output (1-2 days)
- [ ] YAML generation
- [ ] Save dialog
- [ ] Build invocation
- [ ] Progress display

### Phase 7: Polish (2-3 days)
- [ ] Error handling
- [ ] Help screens
- [ ] Mouse support
- [ ] Terminal compatibility testing

**Total: ~15-20 days**

## Key Code to Port from Rat-King

### 1. Sixel Rendering Setup
From `rat-king-cli/src/main.rs` lines 447-496:
- Terminal protocol detection
- Pixmap → image conversion
- StatefulImage widget

### 2. Zoom/Pan Logic
From `rat-king-cli/src/main.rs` lines 923-943:
- Zoom bounds (0.5x - 10x)
- Pan with zoom scaling
- Reset view function

### 3. Event Loop Pattern
From `rat-king-cli/src/main.rs` lines 1206-1328:
- 50ms poll interval
- Background result checking
- Debounced rendering

### 4. Sidebar Layout
From `rat-king-cli/src/main.rs` lines 1393-1572:
- Horizontal split (fixed + flex)
- Vertical section stacking
- List with selection state

## Open Questions

1. **GeoJSON parsing**: Use `geojson` crate or shell out to Python for complex formats?
   - Recommendation: `geojson` for simple preview, Python for full build

2. **Projection handling**: Support projections in Rust or assume WGS84?
   - Recommendation: WGS84 only in TUI, let Python handle projection

3. **Large datasets**: How to handle 100MB+ shapefiles in preview?
   - Recommendation: Simplify on load, show feature count only until zoomed

4. **Cross-platform**: Sixel support varies by terminal
   - Recommendation: Detect protocol (like rat-king), fallback to bounds-only mode

## Success Criteria

1. Can browse all sources in the Python catalog
2. Can preview loaded GeoJSON with zoom/pan
3. Can interactively set bounds with visual feedback
4. Can configure layers with style preview
5. Generates valid YAML that `strata build` accepts
6. Responsive UI (<50ms input latency)
7. Works in iTerm2, Kitty, WezTerm (Sixel terminals)
