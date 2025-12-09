# Strata → Rust Conversion Proposal

## Executive Summary

Converting Strata to Rust is **feasible but non-trivial**. The biggest challenge isn't algorithmic—it's the **geospatial ecosystem maturity gap** between Python (GeoPandas/Shapely) and Rust (geo-rs). I recommend a **phased hybrid approach** that captures performance gains while managing risk.

**Expected gains:**
- 2-3x faster downloads (parallel with tokio)
- 1.5-2x faster geometry operations (compiled + rayon)
- Single binary distribution (no Python environment)
- Native integration with rat-king for linefill patterns

---

## Dependency Mapping

| Python | Rust Equivalent | Parity |
|--------|-----------------|--------|
| Click | `clap` | ✅ Excellent |
| Textual | `ratatui` | ⚠️ Lower-level, more work |
| Rich | `colored`, `indicatif` | ✅ Good |
| Pydantic | `serde` + `validator` | ✅ Good (less ergonomic) |
| PyYAML | `serde_yaml` | ✅ Excellent |
| Shapely | `geo-rs` | ⚠️ 70% coverage |
| GeoPandas | **None** | 🔴 Major gap |
| Pyproj | `proj` | ✅ Good |
| Fiona | `gdal` or `shapefile` | ⚠️ FFI or limited |
| httpx | `reqwest` | ✅ Excellent |

### The GeoPandas Problem

GeoPandas provides:
- DataFrame + geometry column (tabular spatial data)
- Spatial operations on entire columns (`gdf.geometry.difference()`)
- Automatic CRS handling
- Spatial indexing (`.sindex`)
- `dissolve()`, `clip()`, `sjoin()` on DataFrames

**Rust has no equivalent.** Options:
1. **Polars + geo-rs wrapper** - Build custom `GeoDataFrame` type
2. **gdal-rs** - Heavy FFI, but full functionality
3. **Arrow + GeoArrow** - Emerging standard, not mature

---

## Proposed Architecture

```
strata-rs/
├── Cargo.toml              # Workspace root
├── crates/
│   ├── strata-core/        # Core library
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── recipe.rs       # YAML parsing + validation
│   │   │   ├── geodataframe.rs # Custom Polars + geometry type
│   │   │   ├── thoreau/        # Data acquisition
│   │   │   │   ├── mod.rs
│   │   │   │   ├── census.rs   # TIGER downloads
│   │   │   │   ├── canada.rs   # CanVec/NRN
│   │   │   │   ├── quebec.rs
│   │   │   │   ├── openskimap.rs
│   │   │   │   └── cache.rs
│   │   │   ├── humboldt/       # Geometry operations
│   │   │   │   ├── mod.rs
│   │   │   │   ├── ops.rs      # subtract, clip, merge, simplify
│   │   │   │   ├── spatial_index.rs
│   │   │   │   └── projection.rs
│   │   │   ├── kelley/         # Output generation
│   │   │   │   ├── mod.rs
│   │   │   │   ├── svg.rs
│   │   │   │   ├── geojson.rs
│   │   │   │   └── linefill.rs # rat-king integration!
│   │   │   └── maury/          # Pipeline orchestration
│   │   │       ├── mod.rs
│   │   │       └── pipeline.rs
│   │   └── Cargo.toml
│   │
│   └── strata-cli/         # Binary
│       ├── src/
│       │   ├── main.rs
│       │   ├── commands/
│       │   │   ├── build.rs
│       │   │   ├── prepare.rs
│       │   │   ├── preview.rs
│       │   │   └── new.rs      # TUI wizard
│       │   └── tui/
│       │       ├── mod.rs
│       │       ├── app.rs
│       │       └── screens/
│       └── Cargo.toml
│
├── rat-king/               # Git submodule or workspace member
└── examples/
    └── *.strata.yaml
```

---

## Core Dependencies

```toml
[workspace.dependencies]
# CLI/TUI
clap = { version = "4", features = ["derive"] }
ratatui = "0.28"
crossterm = "0.28"
indicatif = "0.17"        # Progress bars
colored = "2"

# Serialization
serde = { version = "1", features = ["derive"] }
serde_yaml = "0.9"
serde_json = "1"

# Geospatial
geo = "0.28"              # Core geometry types + algorithms
geo-types = "0.7"
proj = "0.27"             # CRS transformations
shapefile = "0.6"         # Pure Rust shapefile reader
geozero = "0.13"          # Format conversion (GeoJSON, WKB)
rstar = "0.12"            # R-tree spatial indexing

# Data
polars = { version = "0.44", features = ["lazy", "parquet"] }

# Networking
reqwest = { version = "0.12", features = ["stream", "gzip"] }
tokio = { version = "1", features = ["full"] }

# Utilities
thiserror = "2"
anyhow = "1"
directories = "5"         # Cross-platform cache paths
zip = "2"                 # ZIP extraction
rayon = "1.10"            # Parallel iteration

# Linefill (rat-king)
rat-king = { path = "../rat-king/crates/rat-king" }
```

---

## Module-by-Module Conversion Plan

### Phase 1: Foundation (Weeks 1-4)

#### 1.1 Recipe Parsing (`recipe.rs`)

```rust
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Deserialize, Serialize)]
pub struct Recipe {
    pub name: String,
    #[serde(default)]
    pub description: String,
    pub sources: HashMap<String, SourceConfig>,
    pub layers: Vec<LayerConfig>,
    pub output: OutputConfig,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct SourceConfig {
    pub uri: String,
    pub filter: Option<HashMap<String, serde_yaml::Value>>,
    pub clip_to: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct LayerConfig {
    pub name: String,
    pub source: StringOrVec,  // Handle both "source" and ["source1", "source2"]
    #[serde(default)]
    pub operations: Vec<OperationConfig>,
    #[serde(default)]
    pub style: StyleConfig,
    #[serde(default)]
    pub order: i32,
}

impl Recipe {
    pub fn from_file(path: impl AsRef<Path>) -> Result<Self> {
        let content = std::fs::read_to_string(path)?;
        let recipe: Recipe = serde_yaml::from_str(&content)?;
        recipe.validate()?;
        Ok(recipe)
    }
}
```

**Effort:** Low - serde_yaml handles this well

#### 1.2 Custom GeoDataFrame (`geodataframe.rs`)

This is the **critical piece** - a Polars DataFrame with a geometry column:

```rust
use geo::{Geometry, MultiPolygon, LineString};
use polars::prelude::*;
use std::sync::Arc;

pub struct GeoDataFrame {
    pub df: DataFrame,
    pub geometries: Vec<Geometry>,  // Parallel to df rows
    pub crs: Option<String>,
}

impl GeoDataFrame {
    /// Load from shapefile
    pub fn from_shapefile(path: impl AsRef<Path>) -> Result<Self> {
        let mut reader = shapefile::Reader::from_path(path)?;
        let mut geometries = Vec::new();
        let mut records = Vec::new();

        for result in reader.iter_shapes_and_records() {
            let (shape, record) = result?;
            geometries.push(shape_to_geo(&shape)?);
            records.push(record);
        }

        let df = records_to_dataframe(records)?;
        Ok(Self { df, geometries, crs: None })
    }

    /// Filter by attribute
    pub fn filter(&self, column: &str, value: &str) -> Result<Self> {
        let mask = self.df.column(column)?.equal(value)?;
        let indices: Vec<usize> = mask.iter()
            .enumerate()
            .filter_map(|(i, b)| b.then_some(i))
            .collect();

        Ok(Self {
            df: self.df.filter(&mask)?,
            geometries: indices.iter().map(|&i| self.geometries[i].clone()).collect(),
            crs: self.crs.clone(),
        })
    }

    /// Spatial filter by bounding box
    pub fn clip_to_bbox(&self, bbox: &Rect) -> Self {
        // Use rstar for spatial indexing
        todo!()
    }

    /// Apply geometry operation to all features
    pub fn map_geometry<F>(&self, f: F) -> Self
    where F: Fn(&Geometry) -> Geometry
    {
        Self {
            df: self.df.clone(),
            geometries: self.geometries.iter().map(f).collect(),
            crs: self.crs.clone(),
        }
    }
}
```

**Effort:** High - core abstraction, needs thorough testing

#### 1.3 Cache System (`thoreau/cache.rs`)

```rust
use directories::ProjectDirs;
use std::path::PathBuf;

pub struct Cache {
    base_dir: PathBuf,
}

impl Cache {
    pub fn new() -> Result<Self> {
        let dirs = ProjectDirs::from("", "", "strata")
            .ok_or_else(|| anyhow!("Could not determine cache directory"))?;
        Ok(Self { base_dir: dirs.cache_dir().to_path_buf() })
    }

    pub fn path_for(&self, uri: &str) -> PathBuf {
        // census:tiger/2023/vt/cousub -> cache/census/tiger/2023/vt/cousub/
        let parts: Vec<&str> = uri.split(':').collect();
        let scheme = parts[0];
        let path = parts.get(1).unwrap_or(&"");
        self.base_dir.join(scheme).join(path.replace('/', std::path::MAIN_SEPARATOR_STR))
    }

    pub fn is_cached(&self, uri: &str) -> bool {
        self.path_for(uri).exists()
    }
}
```

**Effort:** Low

### Phase 2: Data Acquisition (Weeks 5-8)

#### 2.1 TIGER Downloads (`thoreau/census.rs`)

```rust
use reqwest::Client;
use tokio::fs;
use zip::ZipArchive;

pub struct TigerFetcher {
    client: Client,
    cache: Cache,
}

impl TigerFetcher {
    pub async fn fetch(&self, uri: &str) -> Result<PathBuf> {
        // Parse URI: census:tiger/2023/vt/cousub
        let parts = parse_tiger_uri(uri)?;

        if self.cache.is_cached(uri) {
            return Ok(self.cache.path_for(uri));
        }

        // Build URL
        let url = format!(
            "https://www2.census.gov/geo/tiger/TIGER{}/{}/tl_{}_{}{}.zip",
            parts.year, parts.folder, parts.year, parts.state_fips, parts.layer
        );

        // Download with retry
        let bytes = self.download_with_retry(&url, 3).await?;

        // Extract
        let dest = self.cache.path_for(uri);
        fs::create_dir_all(&dest).await?;
        self.extract_zip(&bytes, &dest)?;

        Ok(dest)
    }

    async fn download_with_retry(&self, url: &str, max_retries: u32) -> Result<Vec<u8>> {
        for attempt in 0..max_retries {
            match self.client.get(url).send().await {
                Ok(resp) if resp.status().is_success() => {
                    return Ok(resp.bytes().await?.to_vec());
                }
                Ok(resp) => {
                    if attempt < max_retries - 1 {
                        tokio::time::sleep(Duration::from_secs(2u64.pow(attempt))).await;
                    }
                }
                Err(e) if attempt < max_retries - 1 => {
                    tokio::time::sleep(Duration::from_secs(2u64.pow(attempt))).await;
                }
                Err(e) => return Err(e.into()),
            }
        }
        Err(anyhow!("Failed to download after {} attempts", max_retries))
    }
}
```

**Key improvement:** Use `tokio::spawn` for parallel multi-county downloads:

```rust
pub async fn fetch_state_counties(&self, state: &str, layer: &str) -> Result<GeoDataFrame> {
    let county_fips = get_county_fips(state)?;

    // Parallel downloads!
    let handles: Vec<_> = county_fips.iter()
        .map(|fips| {
            let uri = format!("census:tiger/2023/{}/{}", fips, layer);
            let fetcher = self.clone();
            tokio::spawn(async move { fetcher.fetch(&uri).await })
        })
        .collect();

    let paths: Vec<PathBuf> = futures::future::try_join_all(handles).await?
        .into_iter()
        .collect::<Result<Vec<_>>>()?;

    // Merge all GeoDataFrames
    merge_geodataframes(paths)
}
```

**Effort:** Medium

### Phase 3: Geometry Operations (Weeks 9-14)

#### 3.1 Core Operations (`humboldt/ops.rs`)

```rust
use geo::{BooleanOps, Simplify, ConvexHull, Centroid};
use geo::algorithm::bounding_rect::BoundingRect;
use rayon::prelude::*;

/// Subtract one GeoDataFrame's geometries from another
pub fn subtract(gdf: &GeoDataFrame, subtract_gdf: &GeoDataFrame) -> Result<GeoDataFrame> {
    // Union all geometries to subtract
    let subtract_union = subtract_gdf.geometries.iter()
        .fold(None, |acc, geom| {
            match (acc, geom) {
                (None, g) => Some(g.clone()),
                (Some(a), g) => Some(a.union(g)),
            }
        })
        .ok_or_else(|| anyhow!("No geometries to subtract"))?;

    // Apply difference in parallel
    let new_geometries: Vec<Geometry> = gdf.geometries
        .par_iter()
        .map(|g| g.difference(&subtract_union))
        .collect();

    Ok(GeoDataFrame {
        df: gdf.df.clone(),
        geometries: new_geometries,
        crs: gdf.crs.clone(),
    })
}

/// Simplify geometries
pub fn simplify(gdf: &GeoDataFrame, tolerance: f64, preserve_topology: bool) -> GeoDataFrame {
    let new_geometries = if preserve_topology {
        // geo-rs doesn't have preserve_topology - use VW simplification as alternative
        gdf.geometries.par_iter()
            .map(|g| g.simplify_vw(&tolerance))
            .collect()
    } else {
        gdf.geometries.par_iter()
            .map(|g| g.simplify(&tolerance))
            .collect()
    };

    GeoDataFrame {
        df: gdf.df.clone(),
        geometries: new_geometries,
        crs: gdf.crs.clone(),
    }
}

/// Dissolve by attribute (merge geometries with same attribute value)
pub fn dissolve_by(gdf: &GeoDataFrame, column: &str) -> Result<GeoDataFrame> {
    let col = gdf.df.column(column)?;
    let mut groups: HashMap<String, Vec<usize>> = HashMap::new();

    for (i, val) in col.str()?.into_iter().enumerate() {
        if let Some(v) = val {
            groups.entry(v.to_string()).or_default().push(i);
        }
    }

    let mut new_geometries = Vec::new();
    let mut new_rows = Vec::new();

    for (key, indices) in groups {
        let merged = indices.iter()
            .map(|&i| &gdf.geometries[i])
            .fold(None, |acc, g| match acc {
                None => Some(g.clone()),
                Some(a) => Some(a.union(g)),
            })
            .unwrap();

        new_geometries.push(merged);
        // Take first row's attributes
        new_rows.push(gdf.df.get_row(indices[0])?);
    }

    Ok(GeoDataFrame {
        df: DataFrame::from(new_rows)?,
        geometries: new_geometries,
        crs: gdf.crs.clone(),
    })
}
```

**Effort:** High - most complex module

#### 3.2 Spatial Indexing (`humboldt/spatial_index.rs`)

```rust
use rstar::{RTree, RTreeObject, AABB};

struct IndexedGeometry {
    index: usize,
    envelope: AABB<[f64; 2]>,
}

impl RTreeObject for IndexedGeometry {
    type Envelope = AABB<[f64; 2]>;
    fn envelope(&self) -> Self::Envelope { self.envelope }
}

pub fn build_spatial_index(gdf: &GeoDataFrame) -> RTree<IndexedGeometry> {
    let items: Vec<IndexedGeometry> = gdf.geometries.iter()
        .enumerate()
        .map(|(i, g)| {
            let bbox = g.bounding_rect().unwrap();
            IndexedGeometry {
                index: i,
                envelope: AABB::from_corners(
                    [bbox.min().x, bbox.min().y],
                    [bbox.max().x, bbox.max().y],
                ),
            }
        })
        .collect();

    RTree::bulk_load(items)
}
```

**Effort:** Medium

### Phase 4: Output Generation (Weeks 15-18)

#### 4.1 SVG Export (`kelley/svg.rs`)

```rust
pub struct SvgExporter {
    width: f64,
    height: f64,
    bounds: Rect,
}

impl SvgExporter {
    pub fn render(&self, layers: &[(&str, &GeoDataFrame, &StyleConfig)]) -> String {
        let mut svg = format!(
            r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="{} {} {} {}">"#,
            self.bounds.min().x, self.bounds.min().y,
            self.bounds.width(), self.bounds.height()
        );

        for (name, gdf, style) in layers {
            svg.push_str(&format!(r#"<g id="{}">"#, name));

            for geom in &gdf.geometries {
                let path = geometry_to_path(geom);
                svg.push_str(&format!(
                    r#"<path d="{}" stroke="{}" stroke-width="{}" fill="{}"/>"#,
                    path, style.stroke, style.stroke_width,
                    style.fill.as_deref().unwrap_or("none")
                ));
            }

            svg.push_str("</g>");
        }

        svg.push_str("</svg>");
        svg
    }
}

fn geometry_to_path(geom: &Geometry) -> String {
    match geom {
        Geometry::Polygon(p) => polygon_to_path(p),
        Geometry::MultiPolygon(mp) => mp.0.iter().map(polygon_to_path).collect::<Vec<_>>().join(" "),
        Geometry::LineString(ls) => linestring_to_path(ls),
        _ => String::new(),
    }
}

fn polygon_to_path(poly: &Polygon) -> String {
    let mut path = ring_to_path(&poly.exterior(), true);
    for hole in poly.interiors() {
        path.push(' ');
        path.push_str(&ring_to_path(hole, true));
    }
    path
}
```

**Effort:** Medium - straightforward but detail-oriented

### Phase 5: CLI & TUI (Weeks 19-24)

#### 5.1 CLI (`main.rs`)

```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "strata", version, about = "Plotter-ready vector maps from GIS sources")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Launch interactive wizard
    New,
    /// Build outputs from recipe
    Build {
        #[arg(help = "Recipe file path")]
        recipe: PathBuf,
        #[arg(short, long, default_value = "output")]
        output: PathBuf,
    },
    /// Download and cache sources
    Prepare {
        recipe: PathBuf,
    },
    /// Preview features within bounds
    Preview {
        recipe: PathBuf,
        #[arg(long)]
        bounds: Option<String>,
    },
    /// Manage cache
    Cache {
        #[command(subcommand)]
        action: CacheAction,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Build { recipe, output } => {
            let recipe = Recipe::from_file(&recipe)?;
            let mut pipeline = Pipeline::new(recipe);
            pipeline.prepare().await?;
            pipeline.build()?;
            pipeline.export(&output)?;
        }
        // ...
    }

    Ok(())
}
```

**Effort:** Low

#### 5.2 TUI (`tui/app.rs`)

This is the **most labor-intensive** part. The Python Textual TUI is ~2000 LOC across multiple screens. Ratatui equivalent:

```rust
use ratatui::{prelude::*, widgets::*};
use crossterm::event::{self, Event, KeyCode};

pub struct App {
    state: AppState,
    current_screen: Screen,
    recipe_data: RecipeBuilder,
}

enum Screen {
    Welcome,
    SourceBrowser,
    LayerConfig,
    BoundsConfig,
    OutputConfig,
}

impl App {
    pub fn run(&mut self, terminal: &mut Terminal<impl Backend>) -> Result<()> {
        loop {
            terminal.draw(|f| self.render(f))?;

            if let Event::Key(key) = event::read()? {
                match self.handle_key(key.code) {
                    Some(Action::Quit) => break,
                    Some(Action::NextScreen) => self.advance_screen(),
                    Some(Action::PrevScreen) => self.go_back(),
                    _ => {}
                }
            }
        }
        Ok(())
    }

    fn render(&self, frame: &mut Frame) {
        match self.current_screen {
            Screen::Welcome => self.render_welcome(frame),
            Screen::SourceBrowser => self.render_source_browser(frame),
            // ...
        }
    }
}
```

**Effort:** Very High - significant reimplementation

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| geo-rs missing operations | High | Wrap GEOS via FFI for edge cases |
| GeoDataFrame complexity | High | Start simple, iterate on API |
| TUI parity with Textual | Medium | Accept reduced features initially |
| Shapefile edge cases | Medium | Test extensively with real data |
| CRS transformation bugs | Medium | Validate against Python output |

---

## Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Foundation | 4 weeks | Recipe parsing, GeoDataFrame type, cache |
| 2. Data Acquisition | 4 weeks | TIGER, CanVec, Quebec, OpenSkiMap fetchers |
| 3. Geometry Ops | 6 weeks | All humboldt operations |
| 4. Output | 4 weeks | SVG, GeoJSON export |
| 5. CLI/TUI | 6 weeks | Full CLI, basic TUI |
| **Total** | **24 weeks** | Feature parity |

---

# Rat-King Linefill Integration Proposal

## Overview

rat-king is **perfectly suited** for adding linefill patterns to Strata's output. It's already:
- Written in Rust (native integration with strata-rs)
- Designed for pen plotters (same target as Strata)
- Has 28 patterns (lines, crosshatch, honeycomb, spirals, etc.)
- 200x faster than Python equivalents

## Integration Point

Linefill should happen at the **end of the Kelley module**, after all geometry operations but before final SVG output:

```
[Humboldt: subtract, clip, simplify]
            ↓
    GeoDataFrame with clean polygons
            ↓
[Kelley: coordinate transform]
            ↓
    SVG-space polygons
            ↓
[rat-king: generate fill patterns]  ← NEW
            ↓
    Polygons + fill lines
            ↓
[Kelley: render SVG]
            ↓
    Final plotter-ready SVG
```

## Recipe Schema Extension

Add `fill` option to `StyleConfig`:

```yaml
layers:
  - name: towns
    source: vt_towns
    operations:
      - type: subtract
        target: lake_champlain
    style:
      stroke: "#7b1fa2"
      stroke_width: 0.5
      # NEW: linefill options
      fill_pattern: crosshatch    # Pattern name
      fill_spacing: 2.0           # Line spacing in mm
      fill_angle: 45              # Angle in degrees
      fill_inset: 0.5             # Shrink boundary before filling
```

### Supported Patterns

From rat-king's 28 patterns, the most useful for cartography:

| Pattern | Best For | Parameters |
|---------|----------|------------|
| `lines` | Water, simple areas | spacing, angle |
| `crosshatch` | Urban areas, emphasis | spacing, angle, cross_angle |
| `honeycomb` | Parks, forests | spacing |
| `zigzag` | Mountains, terrain | spacing, angle, amplitude |
| `concentric` | Lakes, focal points | spacing, connect_loops |
| `stipple` | Sand, sparse areas | spacing |
| `wave` | Water features | spacing, amplitude, frequency |
| `brick` | Buildings, urban | spacing |

## Implementation

### Option A: Direct Library Integration (Recommended for Rust version)

Add rat-king as a workspace dependency:

```toml
# strata-rs/Cargo.toml
[workspace.dependencies]
rat-king = { path = "../rat-king/crates/rat-king" }
```

New module `kelley/linefill.rs`:

```rust
use rat_king::{Polygon as RkPolygon, Point as RkPoint, Line};
use rat_king::patterns::*;
use geo::Polygon;

/// Convert geo::Polygon to rat-king::Polygon
fn geo_to_ratking(poly: &Polygon) -> RkPolygon {
    let outer: Vec<RkPoint> = poly.exterior().points()
        .map(|p| RkPoint { x: p.x(), y: p.y() })
        .collect();

    let holes: Vec<Vec<RkPoint>> = poly.interiors()
        .iter()
        .map(|ring| ring.points().map(|p| RkPoint { x: p.x(), y: p.y() }).collect())
        .collect();

    RkPolygon { outer, holes, id: None }
}

/// Generate fill lines for a polygon
pub fn generate_fill(
    poly: &Polygon,
    pattern: &str,
    spacing: f64,
    angle: f64,
    options: &FillOptions,
) -> Vec<Line> {
    let rk_poly = geo_to_ratking(poly);

    match pattern {
        "lines" => generate_lines_fill(&rk_poly, spacing, angle),
        "crosshatch" => generate_crosshatch_fill(&rk_poly, spacing, angle),
        "honeycomb" => generate_honeycomb_fill(&rk_poly, spacing, angle),
        "zigzag" => generate_zigzag_fill(&rk_poly, spacing, angle, options.amplitude),
        "wave" => generate_wave_fill(&rk_poly, spacing, angle, options.amplitude, options.frequency),
        "concentric" => generate_concentric_fill(&rk_poly, spacing, options.connect_loops),
        "stipple" => generate_stipple_fill(&rk_poly, spacing),
        "brick" => generate_brick_fill(&rk_poly, spacing, angle),
        "spiral" => generate_spiral_fill(&rk_poly, spacing, options.over_diameter),
        "hilbert" => generate_hilbert_fill(&rk_poly, spacing as usize),
        _ => generate_lines_fill(&rk_poly, spacing, angle), // Default fallback
    }
}

#[derive(Default)]
pub struct FillOptions {
    pub amplitude: f64,
    pub frequency: f64,
    pub connect_loops: bool,
    pub over_diameter: f64,
    pub inset: f64,
}
```

### Option B: Subprocess Call (Python-Compatible)

If keeping Python Strata, call rat-king as subprocess:

```python
# kelley/linefill.py
import subprocess
import tempfile
from pathlib import Path

def apply_linefill(svg_path: Path, pattern: str, spacing: float, angle: float) -> Path:
    """Apply rat-king fill patterns to SVG polygons."""
    output_path = svg_path.with_suffix('.filled.svg')

    cmd = [
        "rat-king", "fill",
        str(svg_path),
        "-p", pattern,
        "-s", str(spacing),
        "-a", str(angle),
        "-o", str(output_path),
    ]

    subprocess.run(cmd, check=True)
    return output_path
```

This approach works but loses tight integration.

## Extended StyleConfig Schema

```rust
#[derive(Debug, Deserialize, Serialize, Default)]
pub struct StyleConfig {
    // Existing
    pub stroke: String,
    pub stroke_width: f64,
    pub fill: Option<String>,           // Solid fill (for screen display)

    // NEW: Linefill patterns
    pub fill_pattern: Option<String>,   // Pattern name
    pub fill_spacing: Option<f64>,      // Line spacing (default 2.0)
    pub fill_angle: Option<f64>,        // Angle in degrees (default 45)
    pub fill_inset: Option<f64>,        // Shrink before filling
    pub fill_stroke: Option<String>,    // Fill line color (defaults to stroke)
    pub fill_stroke_width: Option<f64>, // Fill line width

    // Pattern-specific
    pub fill_amplitude: Option<f64>,    // For zigzag, wave
    pub fill_frequency: Option<f64>,    // For wave
    pub fill_connect_loops: Option<bool>, // For concentric
}
```

## Example Recipe with Linefill

```yaml
name: vermont_filled
description: Vermont map with linefill patterns for pen plotter

sources:
  vt_towns:
    uri: census:tiger/2023/vt/cousub
  vt_water:
    uri: census:tiger/2023/vt/areawater

layers:
  - name: water
    source: vt_water
    style:
      stroke: "#1565c0"
      stroke_width: 0.3
      fill_pattern: wave
      fill_spacing: 1.5
      fill_angle: 0
      fill_amplitude: 0.8
      fill_frequency: 0.3
    order: 1

  - name: towns
    source: vt_towns
    operations:
      - type: subtract
        target: vt_water
    style:
      stroke: "#333333"
      stroke_width: 0.5
      fill_pattern: lines
      fill_spacing: 3.0
      fill_angle: 45
    order: 2

  - name: urban_areas
    source: vt_towns
    filter:
      NAME: ["Burlington", "Montpelier", "Rutland"]
    style:
      stroke: "#7b1fa2"
      stroke_width: 0.5
      fill_pattern: crosshatch
      fill_spacing: 2.0
      fill_angle: 30
    order: 3

output:
  bounds: [-73.5, 42.7, -71.4, 45.1]
  formats:
    - type: svg
      options:
        page_size: [11, 17]
```

## Plotter Optimization

rat-king already includes polygon ordering for minimal pen travel. Integrate this:

```rust
use rat_king::order::{order_nearest_neighbor, calculate_travel_distance};

impl SvgExporter {
    pub fn render_optimized(&self, layers: &[LayerData]) -> String {
        let mut all_polygons = Vec::new();
        let mut polygon_to_layer = Vec::new();

        // Collect all polygons
        for (layer_idx, layer) in layers.iter().enumerate() {
            for geom in &layer.gdf.geometries {
                if let Geometry::Polygon(p) = geom {
                    all_polygons.push(geo_to_ratking(p));
                    polygon_to_layer.push(layer_idx);
                }
            }
        }

        // Optimize order
        let order = order_nearest_neighbor(&all_polygons);
        let travel = calculate_travel_distance(&all_polygons, &order);
        println!("Optimized travel distance: {:.2}mm", travel);

        // Render in optimized order
        let mut svg = self.svg_header();
        for &idx in &order {
            let layer = &layers[polygon_to_layer[idx]];
            svg.push_str(&self.render_polygon(&all_polygons[idx], &layer.style));
        }
        svg.push_str("</svg>");
        svg
    }
}
```

## Performance Expectations

Based on rat-king benchmarks:
- 314 polygons with crosshatch: ~100ms
- Vermont towns (~250 features): ~80ms estimated
- Full state with all layers: <500ms for fill generation

This is negligible compared to data download time.

---

## Summary

### Rust Conversion
- **Feasibility:** High, with caveats around GeoPandas replacement
- **Timeline:** ~24 weeks for full parity
- **Key Challenge:** Building a custom `GeoDataFrame` type on Polars + geo-rs
- **Recommendation:** Phased approach - core library first, TUI last

### Rat-King Integration
- **Fit:** Excellent - purpose-built for this exact use case
- **Integration:** Direct library dependency in Rust, or subprocess in Python
- **Recipe Changes:** Add `fill_pattern`, `fill_spacing`, `fill_angle` to StyleConfig
- **Performance:** Negligible overhead (~100-500ms for typical maps)

### Suggested First Steps
1. Set up Rust workspace with rat-king as submodule/dependency
2. Implement `GeoDataFrame` prototype with shapefile reading
3. Port one simple recipe end-to-end (no TUI)
4. Add linefill integration to Kelley module
5. Iterate from there
