# Strata Ratatui TUI - Architecture & Refactoring Plan

## Part 1: Rat-King Codebase Analysis

### Current State

**Library (`rat-king`)** - Well-structured (7 modules, ~50KB total):
```
src/
├── lib.rs          (30 lines)  - Clean re-exports
├── geometry.rs     (200 lines) - Point, Line, Polygon
├── clip.rs         (400 lines) - Clipping algorithms
├── hatch.rs        (150 lines) - Basic line generation
├── order.rs        (200 lines) - Travel optimization
├── svg.rs          (250 lines) - SVG parsing
├── rng.rs          (100 lines) - RNG utilities
└── patterns/       (29 files)  - Pattern generators
```

**CLI (`rat-king-cli`)** - **MONOLITH** (1 file, 98KB, 2698 lines):
```
src/
└── main.rs         (2698 lines) - EVERYTHING
```

### Monolith Breakdown

| Lines | Content | Should Be |
|-------|---------|-----------|
| 56-127 | Constants, RenderStyle, SketchyConfig | `lib: style.rs` |
| 128-263 | Sketchy effect functions | `lib: sketchy.rs` |
| 264-497 | SVG building (build_svg_content, render_tree) | `lib: render.rs` |
| 498-517 | PatternResult struct | `cli: tui/state.rs` |
| 518-1112 | App struct + impl (595 lines!) | `cli: tui/app.rs` |
| 1113-1205 | Main entry, CLI parsing | `cli: main.rs` |
| 1206-1329 | Event loop (run_app) | `cli: tui/event.rs` |
| 1330-1392 | Pattern settings info | `lib: patterns/info.rs` |
| 1393-1572 | UI rendering (ui function) | `cli: tui/ui.rs` |
| 1573-2029 | cmd_fill, cmd_benchmark | `cli: commands/fill.rs` |
| 2030-2622 | cmd_harness, analysis | `cli: commands/harness.rs` |
| 2623-2698 | generate_pattern, utilities | `lib: patterns/dispatch.rs` |

### Key Issues

1. **No module separation** - Everything in one file makes it hard to:
   - Understand the codebase
   - Reuse components
   - Test individual pieces
   - Navigate during development

2. **Duplicated logic** - `generate_pattern()` is a 35-case match that duplicates info from `Pattern::from_name()`

3. **Mixed concerns** - TUI code, CLI commands, and rendering logic are interleaved

4. **Missing abstraction** - No `TuiApp` trait or reusable TUI components

---

## Part 2: Proposed Refactoring

### New Structure for rat-king-cli

```
rat-king-cli/src/
├── main.rs              # Entry point, CLI parsing only
├── tui/
│   ├── mod.rs           # TUI module exports
│   ├── app.rs           # App struct + core logic
│   ├── state.rs         # UI state (ListState, focus, etc.)
│   ├── event.rs         # Event loop, input handling
│   ├── ui/
│   │   ├── mod.rs
│   │   ├── layout.rs    # Main layout (sidebar + content)
│   │   ├── sidebar.rs   # Patterns list, stats, settings panels
│   │   ├── preview.rs   # Image rendering area
│   │   └── widgets.rs   # Reusable widgets
│   └── render.rs        # Sixel/image rendering pipeline
├── commands/
│   ├── mod.rs
│   ├── fill.rs          # `rat-king fill` command
│   ├── benchmark.rs     # `rat-king benchmark` command
│   ├── harness.rs       # `rat-king harness` command
│   └── patterns.rs      # `rat-king patterns` command
└── config.rs            # RenderStyle, constants
```

### New Structure for rat-king (library)

```
rat-king/src/
├── lib.rs
├── geometry.rs          # (existing)
├── clip.rs              # (existing)
├── hatch.rs             # (existing)
├── order.rs             # (existing)
├── svg.rs               # (existing)
├── rng.rs               # (existing)
├── patterns/
│   ├── mod.rs           # (existing) + add dispatch()
│   ├── info.rs          # NEW: Pattern metadata (labels, descriptions)
│   └── ... (29 pattern files)
├── render/              # NEW: SVG rendering utilities
│   ├── mod.rs
│   ├── svg_builder.rs   # build_svg_content, build_solid_fill_svg
│   └── style.rs         # RenderStyle, SketchyConfig
└── sketchy.rs           # NEW: Sketchy effect (hand-drawn lines)
```

---

## Part 3: Reusable TUI Components

### Core Abstraction: `TuiApp` Trait

```rust
/// Trait for TUI applications using ratatui
pub trait TuiApp {
    /// Initialize the app
    fn new() -> Result<Self, String> where Self: Sized;

    /// Handle a key event
    fn handle_key(&mut self, key: KeyEvent);

    /// Handle a mouse event
    fn handle_mouse(&mut self, mouse: MouseEvent);

    /// Check for background task results
    fn poll_background(&mut self);

    /// Render the UI
    fn render(&mut self, frame: &mut Frame);

    /// Should the app quit?
    fn should_quit(&self) -> bool;
}
```

### Reusable Layout: `SidebarLayout`

```rust
/// Standard sidebar + content layout
pub struct SidebarLayout {
    pub sidebar_width: u16,
    pub sidebar_sections: Vec<SidebarSection>,
}

pub struct SidebarSection {
    pub title: String,
    pub height: Constraint,
    pub render: Box<dyn Fn(&mut Frame, Rect, &dyn Any)>,
}

impl SidebarLayout {
    pub fn render(&self, frame: &mut Frame, app: &dyn Any) {
        let chunks = Layout::horizontal([
            Constraint::Length(self.sidebar_width),
            Constraint::Min(40),
        ]).split(frame.area());

        // Render sidebar sections
        let sidebar_chunks = Layout::vertical(
            self.sidebar_sections.iter().map(|s| s.height).collect()
        ).split(chunks[0]);

        for (i, section) in self.sidebar_sections.iter().enumerate() {
            (section.render)(frame, sidebar_chunks[i], app);
        }
    }
}
```

### Reusable Widget: `SelectableList`

```rust
/// A list with keyboard/mouse selection
pub struct SelectableList<T> {
    items: Vec<T>,
    state: ListState,
    title: String,
    render_item: fn(&T) -> String,
}

impl<T> SelectableList<T> {
    pub fn selected(&self) -> Option<&T> {
        self.state.selected().map(|i| &self.items[i])
    }

    pub fn handle_key(&mut self, key: KeyCode) {
        match key {
            KeyCode::Up | KeyCode::Char('k') => self.previous(),
            KeyCode::Down | KeyCode::Char('j') => self.next(),
            _ => {}
        }
    }

    pub fn handle_click(&mut self, row: u16, area: Rect) {
        if let Some(index) = self.row_to_index(row, area) {
            self.state.select(Some(index));
        }
    }
}
```

### Reusable Widget: `ImagePreview`

```rust
/// Sixel image preview with zoom/pan
pub struct ImagePreview {
    picker: Picker,
    image_state: Option<Box<dyn StatefulProtocol>>,
    zoom: f64,
    pan: (f64, f64),
    bounds: (f64, f64, f64, f64),
    debounce: Option<Instant>,
}

impl ImagePreview {
    pub fn set_image(&mut self, pixmap: &Pixmap) {
        let image = pixmap_to_dynamic_image(pixmap);
        self.image_state = Some(self.picker.new_resize_protocol(image));
    }

    pub fn handle_zoom(&mut self, delta: f64) {
        self.zoom = (self.zoom * delta).clamp(0.5, 10.0);
        self.debounce = Some(Instant::now());
    }

    pub fn handle_pan(&mut self, dx: f64, dy: f64) {
        self.pan.0 += dx / self.zoom;
        self.pan.1 += dy / self.zoom;
        self.debounce = Some(Instant::now());
    }

    pub fn needs_redraw(&self) -> bool {
        self.debounce.map_or(false, |t| t.elapsed() > Duration::from_millis(100))
    }
}
```

---

## Part 4: Strata TUI Design Questions

Before implementing, we need to discuss the user experience:

### 1. Navigation Model

**Option A: Modal (like vim)**
- `s` = Sources mode, `l` = Layers mode, `b` = Bounds mode, `o` = Output mode
- Tab/Shift-Tab to cycle between modes
- Each mode has its own key bindings

**Option B: Single-focus (like rat-king)**
- One sidebar with multiple sections
- Tab cycles through focusable elements
- Arrow keys adjust the focused element

**Option C: Panel-based (like tmux)**
- Multiple panels visible at once
- Ctrl+arrows to move between panels
- Each panel is independently scrollable

### 2. Source Selection

**Question**: How do users add sources to their recipe?

**Option A: Tree browser**
```
Sources (Tab to expand)
├─ Census TIGER
│  ├─ Vermont
│  │  ├─ [x] Towns (cousub)
│  │  ├─ [x] Water (areawater)
│  │  └─ [ ] Roads (prisecroads)
│  └─ New York
├─ Quebec
└─ Canada
```
- Checkboxes to select/deselect
- Space to toggle, Enter to expand/collapse

**Option B: Two-panel (available → selected)**
```
┌─ Available ────────┐  ┌─ Selected ─────────┐
│ census:vt/cousub   │  │ vt_towns           │
│ census:vt/water    │→→│ vt_water           │
│ census:ny/cousub   │  │ lake_champlain     │
│ quebec:muni        │  │                    │
└────────────────────┘  └────────────────────┘
```
- Arrow keys to navigate
- Enter to add, Delete to remove

### 3. Bounds Selection

**Question**: How do users set the map bounds?

**Option A: Numeric entry**
```
Bounds: [-73.5, 42.7, -71.5, 45.0]
        West  South  East  North
        [Tab to edit, Enter to confirm]
```

**Option B: Interactive rectangle**
```
┌─────────────────────────────┐
│  ┌─────────┐                │
│  │ ◆─────◆ │  ← Drag corners│
│  │ │     │ │                │
│  │ ◆─────◆ │                │
│  └─────────┘                │
│                             │
│  Click to set center        │
│  Scroll to resize           │
└─────────────────────────────┘
```

**Option C: Preset + adjust**
```
Presets: [Vermont] [Lake Champlain] [Quebec Border]

Current: Vermont Regional
Bounds: -73.93, 42.43, -71.17, 45.50

[←] Shrink  [→] Expand  [↑↓] Pan  [R] Reset
```

### 4. Layer Configuration

**Question**: How do users configure layer styling?

**Option A: Inline editing**
```
Layers:
► towns     ██ #66bb6a  0.5px  [E]dit [D]elete
  water     ██ #1976d2  0.3px
  roads     ── #424242  0.8px
```

**Option B: Detail panel**
```
┌─ Layers ──────┐  ┌─ Layer: towns ──────────┐
│ ► towns       │  │ Source: vt_towns        │
│   water       │  │ Fill: #66bb6a           │
│   roads       │  │ Stroke: #424242  0.5px  │
└───────────────┘  │ Operations:             │
                   │   - subtract: vt_water  │
                   │   - simplify: 0.0003    │
                   └─────────────────────────┘
```

### 5. Preview Updates

**Question**: When should the preview update?

**Option A: Manual refresh**
- Press `R` or `Enter` to regenerate preview
- Shows "stale" indicator when config changed

**Option B: Debounced auto-update**
- Updates 500ms after last change
- Shows spinner during generation

**Option C: Instant preview for small datasets**
- Auto-update for <1000 features
- Manual refresh for larger datasets
- Shows feature count with warning

### 6. Output/Build

**Question**: How do users trigger the build?

**Option A: Save & Exit**
- `S` saves YAML
- `B` runs `strata build` in background
- `Q` quits

**Option B: Integrated build**
- Build runs within TUI
- Progress shown in status bar
- Opens output folder when complete

---

## Part 5: Implementation Phases

### Phase 0: Refactor rat-king (3-4 days)
- [ ] Extract TUI into `tui/` module
- [ ] Extract CLI commands into `commands/`
- [ ] Move rendering utilities to library
- [ ] Create reusable widgets (SelectableList, ImagePreview)
- [ ] Test that rat-king still works

### Phase 1: Strata TUI Shell (2 days)
- [ ] Create `strata-tui` crate in rat-king workspace
- [ ] Set up basic ratatui app with layout
- [ ] Implement sidebar skeleton
- [ ] Test Sixel rendering

### Phase 2: Source Browser (3 days)
- [ ] Port source catalog from Python
- [ ] Implement tree browser widget
- [ ] Add cache status detection
- [ ] Test source selection

### Phase 3: Map Preview (4 days)
- [ ] Implement GeoJSON → SVG conversion
- [ ] Port ImagePreview from rat-king
- [ ] Add zoom/pan controls
- [ ] Test with real data

### Phase 4: Bounds Editor (3 days)
- [ ] Implement bounds display
- [ ] Add numeric editing
- [ ] Add visual overlay (if time permits)
- [ ] Test bounds clipping

### Phase 5: Layer Config (3 days)
- [ ] Implement layer list
- [ ] Add style editing
- [ ] Add operation configuration
- [ ] Test layer rendering

### Phase 6: Recipe Output (2 days)
- [ ] Implement YAML generation
- [ ] Add save dialog
- [ ] Add build invocation
- [ ] Test end-to-end

**Total: ~20 days**

---

## Part 6: File Locations

### Rat-King (after refactor)
```
~/Code/rat-king/crates/
├── rat-king/               # Library
│   └── src/
│       ├── render/         # NEW
│       └── sketchy.rs      # NEW
├── rat-king-cli/           # CLI + TUI
│   └── src/
│       ├── tui/            # NEW
│       └── commands/       # NEW
└── rat-king-tui/           # NEW: Shared TUI components
    └── src/
        ├── app.rs          # TuiApp trait
        ├── layout.rs       # SidebarLayout
        ├── widgets/        # Reusable widgets
        └── image.rs        # ImagePreview
```

### Strata TUI
```
~/Code/rat-king/crates/
└── strata-tui/             # NEW
    ├── Cargo.toml
    └── src/
        ├── main.rs
        ├── app.rs          # StrataApp implements TuiApp
        ├── sources/        # Source browser
        ├── layers/         # Layer configuration
        ├── bounds/         # Bounds editor
        └── recipe/         # YAML generation
```

---

## Next Steps

**Before coding, please answer:**

1. Navigation model preference? (A/B/C)
2. Source selection style? (A/B)
3. Bounds selection approach? (A/B/C)
4. Layer configuration style? (A/B)
5. Preview update behavior? (A/B/C)
6. Build integration level? (A/B)

These answers will shape the implementation.
