# TUI Golden Path - Screen Mockups

Detailed ASCII mockups for every screen in the Strata TUI redesign.

---

## Table of Contents

1. [Launch & Home](#1-launch--home)
2. [Phase 1: Foundation](#phase-1-foundation)
3. [Phase 2: Drill-Down Navigation](#phase-2-drill-down-navigation)
4. [Phase 3: Visual Crop](#phase-3-visual-crop)
5. [Phase 4: Cache Management](#phase-4-cache-management)
6. [Phase 5: Layer Configuration](#phase-5-layer-configuration)
7. [Phase 6: Output Generation](#phase-6-output-generation)
8. [Phase 7: Batch Mode](#phase-7-batch-mode)
9. [Complete Flow Diagram](#complete-flow-diagram)

---

## 1. Launch & Home

### 1.1 Splash / Home Screen

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                                                                             │
│               ███████╗████████╗██████╗  █████╗ ████████╗ █████╗            │
│               ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗           │
│               ███████╗   ██║   ██████╔╝███████║   ██║   ███████║           │
│               ╚════██║   ██║   ██╔══██╗██╔══██║   ██║   ██╔══██║           │
│               ███████║   ██║   ██║  ██║██║  ██║   ██║   ██║  ██║           │
│               ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝           │
│                                                                             │
│                    Plotter-ready maps from GIS data                         │
│                              v0.1.0                                         │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   [N]  New Map          Create a new map from scratch               │   │
│  │                                                                     │   │
│  │   [B]  Batch Maps       Generate multiple maps at once              │   │
│  │                                                                     │   │
│  │   [O]  Open Recipe      Load an existing .strata.yaml file          │   │
│  │                                                                     │   │
│  │   [C]  Cache Manager    View and manage downloaded data             │   │
│  │                                                                     │   │
│  │   [S]  Settings         Configure preferences                       │   │
│  │                                                                     │   │
│  │   [Q]  Quit                                                         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Recent Maps:                                                               │
│    • vermont_towns.strata.yaml (2 hours ago)                               │
│    • lake_champlain_12x18.strata.yaml (yesterday)                          │
│    • jay_peak_ski.strata.yaml (3 days ago)                                 │
│                                                                             │
│  Cache: 847 MB used │ Terminal: Kitty (graphics supported)                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Terminal Capability Detection (shown briefly on startup)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Detecting terminal capabilities...                                         │
│                                                                             │
│    [✓] Terminal: Kitty 0.32.1                                              │
│    [✓] Graphics: Kitty protocol supported                                  │
│    [✓] Colors: True color (24-bit)                                         │
│    [✓] Unicode: Full support                                               │
│    [✓] Size: 120 × 40 (adequate)                                           │
│                                                                             │
│  Graphics mode: HIGH RESOLUTION                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Terminal Fallback Notice

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Detecting terminal capabilities...                                         │
│                                                                             │
│    [✓] Terminal: xterm-256color                                            │
│    [✗] Graphics: No image protocol detected                                │
│    [✓] Colors: 256 colors                                                  │
│    [✓] Unicode: Full support                                               │
│    [!] Size: 80 × 24 (minimum)                                             │
│                                                                             │
│  Graphics mode: BRAILLE (text-based rendering)                             │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  TIP: For best experience, use Kitty, WezTerm, or iTerm2 terminal     │ │
│  │  which support inline image rendering.                                 │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [Enter] Continue with braille mode    [Q] Quit                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation

### 1.1 Graphics Abstraction Demo (Braille Mode)

```
┌─ Preview: Vermont ──────────────────────────────────────────────────────────┐
│                                                                             │
│  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿   │
│  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⠛⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿   │
│  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿   │
│  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿   │
│  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⠀⣴⣶⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿   │
│  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⣿⣿⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿  VERMONT  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿   │
│  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠙⠋⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿   │
│  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿   │
│  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣀⣀⣀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿   │
│  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿   │
│                                                                             │
│  Rendering: Braille (160×80 effective resolution)                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Graphics Abstraction Demo (High-Res Mode)

```
┌─ Preview: Vermont ──────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │                      [Inline PNG/Image Here]                        │   │
│  │                                                                     │   │
│  │              Kitty graphics protocol renders actual                 │   │
│  │              raster image inline in terminal                        │   │
│  │                                                                     │   │
│  │              Resolution: 800×600 pixels                             │   │
│  │              Colors: Full 24-bit                                    │   │
│  │                                                                     │   │
│  │                     ┌────────────┐                                  │   │
│  │                    ╱              ╲                                 │   │
│  │                   │    VERMONT    │                                 │   │
│  │                   │   ▪ Burlington│                                 │   │
│  │                    ╲   Lake      ╱                                  │   │
│  │                     ╲ Champlain ╱                                   │   │
│  │                      └─────────┘                                    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Rendering: Kitty graphics (800×600 pixels)                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 2: Drill-Down Navigation

### 2.1 World View (Top Level)

```
┌─ Select Region ─────────────────────────────────────────────────────────────┐
│  Step 1 of 5: Choose Location                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ Regions ──────────────────┐  ┌─ Preview ─────────────────────────────┐ │
│  │                            │  │                                       │ │
│  │  ▸ North America        ◀──┼──│      ⣀⣀⣀⡀                           │ │
│  │    South America           │  │    ⣰⣿⣿⣿⣿⣷⡀    ⣀⣤⣤⣀              │ │
│  │    Europe                  │  │   ⣼⣿⣿⣿⣿⣿⣿⣆  ⣴⣿⣿⣿⣿⣷            │ │
│  │    Asia                    │  │   ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿           │ │
│  │    Africa                  │  │   ⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿            │ │
│  │    Oceania                 │  │    ⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟             │ │
│  │    Antarctica              │  │      ⠈⠻⣿⣿⣿⣿⣿⠿⠋               │ │
│  │                            │  │         NORTH AMERICA               │ │
│  │                            │  │                                       │ │
│  │                            │  │  Countries: 23                        │ │
│  │                            │  │  Area: 24.71 million km²              │ │
│  │                            │  │  Data: Natural Earth + Census         │ │
│  │                            │  │                                       │ │
│  └────────────────────────────┘  └───────────────────────────────────────┘ │
│                                                                             │
│  [↑↓] Navigate    [Enter] Drill down    [/] Search    [Esc] Back           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Continent Level (North America)

```
┌─ Select Region ─────────────────────────────────────────────────────────────┐
│  Step 1 of 5: Choose Location    ◂ World › North America                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ Countries ────────────────┐  ┌─ Preview ─────────────────────────────┐ │
│  │                            │  │       ⣀⣀⣤⣤⣤⣤⣀⣀                     │ │
│  │    Canada               ●  │  │    ⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄                 │ │
│  │  ▸ United States        ◀──┼──│  ⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄               │ │
│  │    Mexico               ○  │  │  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿  ← USA      │ │
│  │    ─────────────────────   │  │  ⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇               │ │
│  │    Caribbean               │  │   ⠙⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠋                │ │
│  │    Central America         │  │      ⠈⠉⠛⠛⠛⠛⠉⠁                   │ │
│  │                            │  │                                       │ │
│  │                            │  │  UNITED STATES                        │ │
│  │                            │  │  States: 50 + DC + territories        │ │
│  │                            │  │  Area: 9.83 million km²               │ │
│  │                            │  │  Data: Census TIGER/Line              │ │
│  │                            │  │  Cache: ● 12 states cached (1.2 GB)   │ │
│  │                            │  │                                       │ │
│  └────────────────────────────┘  └───────────────────────────────────────┘ │
│                                                                             │
│  Legend: ● Fully cached  ◐ Partial  ○ Not cached                           │
│                                                                             │
│  [↑↓] Navigate    [Enter] Drill down    [/] Search    [Esc] Back           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Country Level (United States - Regions)

```
┌─ Select Region ─────────────────────────────────────────────────────────────┐
│  Step 1 of 5: Choose Location    ◂ World › North America › United States   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ US Regions ───────────────┐  ┌─ Preview ─────────────────────────────┐ │
│  │                            │  │                                       │ │
│  │  ▸ Northeast (9 states) ◀──┼──│     ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿         │ │
│  │    Southeast (12 states)   │  │    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿        │ │
│  │    Midwest (12 states)     │  │   ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿       │ │
│  │    Southwest (4 states)    │  │   ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿███⣿⣿⣿⣿       │ │
│  │    West (11 states)        │  │    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿███⣿⣿⣿        │ │
│  │    ─────────────────────   │  │     ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿███⣿⣿         │ │
│  │    All 50 states           │  │              ⣿⣿⣿⣿⣿⣿⣿              │ │
│  │    US Territories          │  │                                       │ │
│  │                            │  │  NORTHEAST                            │ │
│  │                            │  │  ME, NH, VT, MA, RI, CT, NY, NJ, PA   │ │
│  │                            │  │  Area: 181,324 mi²                    │ │
│  │                            │  │  Cache: ● VT, NH  ◐ NY  ○ 6 others   │ │
│  │                            │  │                                       │ │
│  └────────────────────────────┘  └───────────────────────────────────────┘ │
│                                                                             │
│  [↑↓] Navigate    [Enter] Drill down    [/] Search    [Esc] Back           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Region Level (Northeast States)

```
┌─ Select Region ─────────────────────────────────────────────────────────────┐
│  Step 1 of 5: Choose Location    ◂ ... › United States › Northeast         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ States ───────────────────┐  ┌─ Preview ─────────────────────────────┐ │
│  │                            │  │          ⢀⣤⣶⣿⣿⣶⣤⡀                  │ │
│  │    Connecticut          ○  │  │        ⣴⣿⣿⣿⣿⣿⣿⣿⣿⣦                │ │
│  │    Maine                ○  │  │       ⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧               │ │
│  │    Massachusetts        ○  │  │      ⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧              │ │
│  │    New Hampshire        ●  │  │     ⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧             │ │
│  │    New Jersey           ○  │  │    ⢸███⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇  VERMONT  │ │
│  │    New York             ◐  │  │    ⠘███⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃            │ │
│  │    Pennsylvania         ○  │  │     ⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋             │ │
│  │    Rhode Island         ○  │  │      ⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋              │ │
│  │  ▸ Vermont              ● ◀┼──│       ⠙⠿⣿⣿⣿⣿⣿⣿⠿⠋               │ │
│  │                            │  │                                       │ │
│  │                            │  │  VERMONT                              │ │
│  │                            │  │  Counties: 14 │ Towns: 251            │ │
│  │                            │  │  Area: 9,616 mi² (24,906 km²)         │ │
│  │                            │  │  Cache: ● Fully cached (156 MB)       │ │
│  │                            │  │                                       │ │
│  └────────────────────────────┘  └───────────────────────────────────────┘ │
│                                                                             │
│  [↑↓] Navigate   [Enter] Drill down   [Space] Select for map   [Esc] Back  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.5 State Level (Vermont Counties)

```
┌─ Select Region ─────────────────────────────────────────────────────────────┐
│  Step 1 of 5: Choose Location    ◂ ... › Northeast › Vermont               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ Counties ─────────────────┐  ┌─ Preview ─────────────────────────────┐ │
│  │                            │  │        ╭──────╮                       │ │
│  │    Addison County       ●  │  │       ╱ Grand  ╲                      │ │
│  │    Bennington County    ●  │  │      │  Isle   │                      │ │
│  │    Caledonia County     ●  │  │      ╰────┬────╯                      │ │
│  │  ▸ Chittenden County    ● ◀┼──│   ╭──────┤├──────╮                    │ │
│  │    Essex County         ●  │  │   │Franklin││Orleans│                  │ │
│  │    Franklin County      ●  │  │   ╰──┬────┤├──┬───╯                   │ │
│  │    Grand Isle County    ●  │  │╭─────┤████├├──┤Caledonia              │ │
│  │    Lamoille County      ●  │  ││Chitt│████├├Lamoille                  │ │
│  │    Orange County        ●  │  │╰─────┤Wash├├──┤                       │ │
│  │    Orleans County       ●  │  │      │ington├──┤Orange                │ │
│  │    Rutland County       ●  │  │Addison├────┤   │                      │ │
│  │    Washington County    ●  │  │      │Wind-│   │                      │ │
│  │    Windham County       ●  │  │Rutland│sor │   ╯                      │ │
│  │    Windsor County       ●  │  │      ├────┤Windham                    │ │
│  │                            │  │Benning│    │                          │ │
│  │                            │  │ton    ╰────╯                          │ │
│  │                            │  │                                       │ │
│  │                            │  │  CHITTENDEN COUNTY                    │ │
│  │                            │  │  Towns: 18 │ Pop: 168,323             │ │
│  │                            │  │  Area: 620 mi² (1,606 km²)            │ │
│  │                            │  │  Largest: Burlington, Essex           │ │
│  │                            │  │                                       │ │
│  └────────────────────────────┘  └───────────────────────────────────────┘ │
│                                                                             │
│  [↑↓] Navigate   [Enter] Drill down   [Space] Select for map   [Esc] Back  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.6 County Level (Chittenden County Towns)

```
┌─ Select Region ─────────────────────────────────────────────────────────────┐
│  Step 1 of 5: Choose Location    ◂ ... › Vermont › Chittenden County       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ Towns (18) ───────────────┐  ┌─ Preview ─────────────────────────────┐ │
│  │                            │  │                                       │ │
│  │  [✓] Bolton             ●  │  │    ╭─────────╮                        │ │
│  │  [✓] Burlington         ●  │  │   ╱ Milton    ╲                       │ │
│  │  [✓] Charlotte          ●  │  │  │  ╭───────╮  │                      │ │
│  │  [✓] Colchester         ●  │  │  │  │Colches│  │Georgia               │ │
│  │  [ ] Essex              ●  │  │  │  │ter    ├──┤                      │ │
│  │  [ ] Essex Junction     ●  │  │  │  ├───┬───┤  │                      │ │
│  │  [ ] Hinesburg          ●  │  │  │  │Bur│Wino│  │Essex                │ │
│  │  [ ] Huntington         ●  │  │  │  │ling│oski├─┤                      │ │
│  │  [ ] Jericho            ●  │  │  │  │ton├───┤  │                      │ │
│  │  [ ] Milton             ●  │  │  │  │   │S.B│  │                      │ │
│  │  [ ] Richmond           ●  │  │  │Shelb├───┴──┤  │Jericho             │ │
│  │  [ ] Shelburne          ●  │  │  │urne │Willis│  │                    │ │
│  │  [✓] South Burlington   ●  │  │  ├─────┤ton  ├──┤                      │ │
│  │  [ ] St. George         ●  │  │  │Charl│     │  │Richmond             │ │
│  │  [ ] Underhill          ●  │  │  │otte ├─────┤  │                      │ │
│  │  [ ] Westford           ●  │  │  ╰─────┤Hines├──╯                      │ │
│  │  [ ] Williston          ●  │  │        │burg │                        │ │
│  │  [✓] Winooski           ●  │  │        ╰─────╯                        │ │
│  │                            │  │                                       │ │
│  └────────────────────────────┘  └───────────────────────────────────────┘ │
│                                                                             │
│  Selected: 5 towns │ Combined area: 48 mi²                                 │
│                                                                             │
│  [Space] Toggle  [a] All  [n] None  [Enter] Continue to crop  [Esc] Back   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.7 Search Mode

```
┌─ Search Location ───────────────────────────────────────────────────────────┐
│                                                                             │
│  Search: burlington_                                                        │
│                                                                             │
│  ┌─ Results ──────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  ▸ Burlington, Chittenden County, Vermont, USA                         │ │
│  │    └─ Town │ Pop: 44,743 │ Area: 15.5 mi² │ Cache: ●                   │ │
│  │                                                                        │ │
│  │    Burlington, Coffey County, Kansas, USA                              │ │
│  │    └─ City │ Pop: 2,674 │ Area: 2.1 mi² │ Cache: ○                     │ │
│  │                                                                        │ │
│  │    Burlington, Des Moines County, Iowa, USA                            │ │
│  │    └─ City │ Pop: 24,028 │ Area: 15.2 mi² │ Cache: ○                   │ │
│  │                                                                        │ │
│  │    Burlington, Halton Region, Ontario, Canada                          │ │
│  │    └─ City │ Pop: 183,314 │ Area: 73.5 mi² │ Cache: ○                  │ │
│  │                                                                        │ │
│  │    Burlington County, New Jersey, USA                                  │ │
│  │    └─ County │ Pop: 461,860 │ Area: 819 mi² │ Cache: ○                 │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [↑↓] Navigate    [Enter] Select    [Esc] Cancel search                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 3: Visual Crop

### 3.1 Initial Crop View (Fit to Selection)

```
┌─ Adjust Crop Area ──────────────────────────────────────────────────────────┐
│  Step 2 of 5: Define Bounds                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ Map View ─────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │         · · · · · · · · · · · · · · · · · · · · · · · · · · · ·       │ │
│  │       · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·     │ │
│  │     · · · · · · · · · · · ┌─────────────────────┐ · · · · · · · · ·   │ │
│  │    · · · · · · · · · · · ·│▲                    │· · · · · · · · · ·  │ │
│  │   · · · · · · · · · · · · │                     │ · · · · · · · · · · │ │
│  │  · · · · · · · · · ·Lake· │   ╭─────╮           │ · · · · · · · · · ·│ │
│  │  · · · · · · · · Champlain│   │ BTV │  Winooski │ · · · · · · · · · ·│ │
│  │  · · · · · · · · · · · · ·│◄──│     ├───────────│──►· · · · · · · · ·│ │
│  │  · · · · · · · · · · · · ·│   │ S.B │           │ · · · · · · · · · ·│ │
│  │   · · · · · · · · · · · · │   ╰─────╯           │ · · · · · · · · · · │ │
│  │    · · · · · · · · · · · ·│                     │· · · · · · · · · ·  │ │
│  │     · · · · · · · · · · · │▼                    │ · · · · · · · · ·   │ │
│  │       · · · · · · · · · · └─────────────────────┘ · · · · · · · · ·   │ │
│  │         · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·     │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Bounds ─────────────────────┐  ┌─ Dimensions ──────────────────────┐   │
│  │ West:  -73.2791              │  │ Width:  8.2 miles (13.2 km)       │   │
│  │ East:  -73.1012              │  │ Height: 6.1 miles (9.8 km)        │   │
│  │ South:  44.4234              │  │ Aspect: 1.34:1                    │   │
│  │ North:  44.5123              │  │ Area:   50.0 mi² (129.5 km²)      │   │
│  └──────────────────────────────┘  └────────────────────────────────────┘   │
│                                                                             │
│  [←→↑↓] Pan   [Shift+Arrow] Resize   [+/-] Zoom   [[] []] Aspect preset    │
│  [f] Fit to features   [c] Center   [Enter] Continue   [Esc] Back          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Crop Adjusted (Wider View with Context)

```
┌─ Adjust Crop Area ──────────────────────────────────────────────────────────┐
│  Step 2 of 5: Define Bounds                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ Map View ─────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · │ │
│  │  · · ┌─────────────────────────────────────────────────────────┐ · · · │ │
│  │  · · │▲                                                        │ · · · │ │
│  │  · · │         Milton          Georgia                         │ · · · │ │
│  │  · · │     ╭─────────────────────────────╮                     │ · · · │ │
│  │  · · │    ╱    Colchester                 ╲                    │ · · · │ │
│  │Lake  │   │  ┌───────────────────────────┐  │                   │ · · · │ │
│  │Champ-│◄──│  │ BURLINGTON │   Winooski   │  │  Essex            │──►· · │ │
│  │plain │   │  │            │              │  │                   │ · · · │ │
│  │  · · │   │  │  S. Burl.  │              │  │  Jericho          │ · · · │ │
│  │  · · │    ╲ └───────────────────────────┘ ╱                    │ · · · │ │
│  │  · · │     ╰─────────────────────────────╯                     │ · · · │ │
│  │  · · │         Shelburne        Williston                      │ · · · │ │
│  │  · · │▼                                                        │ · · · │ │
│  │  · · └─────────────────────────────────────────────────────────┘ · · · │ │
│  │  · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Bounds ─────────────────────┐  ┌─ Dimensions ──────────────────────┐   │
│  │ West:  -73.3500              │  │ Width:  15.4 miles (24.8 km)      │   │
│  │ East:  -72.9800              │  │ Height: 12.8 miles (20.6 km)      │   │
│  │ South:  44.3800              │  │ Aspect: 1.20:1 (fits tabloid)     │   │
│  │ North:  44.5650              │  │ Area:   197.1 mi² (510.5 km²)     │   │
│  └──────────────────────────────┘  └────────────────────────────────────┘   │
│                                                                             │
│  [←→↑↓] Pan   [Shift+Arrow] Resize   [+/-] Zoom   [[] []] Aspect preset    │
│  [f] Fit to features   [c] Center   [Enter] Continue   [Esc] Back          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Aspect Ratio Presets

```
┌─ Aspect Ratio ──────────────────────────────────────────────────────────────┐
│                                                                             │
│  Select page aspect ratio:                                                  │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │   ┌─────┐      ┌───────┐      ┌─────────┐      ┌───┐                  │ │
│  │   │     │      │       │      │         │      │   │                  │ │
│  │   │     │      │       │      │         │      │   │                  │ │
│  │   │     │      │       │      │         │      │   │                  │ │
│  │   │     │      │       │      └─────────┘      │   │                  │ │
│  │   │     │      │       │                       │   │                  │ │
│  │   │     │      └───────┘       Landscape       │   │                  │ │
│  │   └─────┘                       3:2            │   │                  │ │
│  │                                                └───┘                  │ │
│  │  ▸ Letter      Tabloid                        24×36                  │ │
│  │    8.5×11       11×17                         2:3                    │ │
│  │    Portrait    Portrait                       Portrait               │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  (•) Letter 8.5×11 (Portrait)                                              │
│  ( ) Letter 8.5×11 (Landscape)                                             │
│  ( ) Tabloid 11×17 (Portrait)                                              │
│  ( ) Tabloid 11×17 (Landscape)                                             │
│  ( ) Poster 18×24                                                          │
│  ( ) Large 24×36                                                           │
│  ( ) Square 1:1                                                            │
│  ( ) Custom...                                                              │
│                                                                             │
│  [↑↓] Select    [Enter] Apply    [Esc] Cancel                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 4: Cache Management

### 4.1 Cache Dashboard

```
┌─ Data Cache ────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Cache Location: ~/Library/Caches/strata/                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Used: 1.2 GB of 10 GB limit    [████████████░░░░░░░░░░░░░░░░░░░░] 12%     │
│                                                                             │
│  ┌─ Cached Data ──────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  SOURCE                                SIZE        LAST USED           │ │
│  │  ──────────────────────────────────────────────────────────────────── │ │
│  │  [✓] census/tiger/2023/vt              156 MB      2 hours ago        │ │
│  │      └─ cousub, areawater, linearwater, prisecroads, county           │ │
│  │                                                                        │ │
│  │  [✓] census/tiger/2023/nh               98 MB      3 days ago         │ │
│  │      └─ cousub, areawater, linearwater, prisecroads                   │ │
│  │                                                                        │ │
│  │  [ ] census/tiger/2023/ny              312 MB      1 week ago         │ │
│  │      └─ cousub, areawater, county                                     │ │
│  │                                                                        │ │
│  │  [✓] quebec/municipalities              47 MB      2 weeks ago        │ │
│  │      └─ SDA_MUN_100k                                                  │ │
│  │                                                                        │ │
│  │  [ ] canada/canvec/hydro               148 MB      1 month ago        │ │
│  │      └─ waterbody_2, watercourse_1                                    │ │
│  │                                                                        │ │
│  │  [ ] naturalearth/10m                   89 MB      2 months ago       │ │
│  │      └─ admin_0, admin_1, coastline, lakes, rivers                    │ │
│  │                                                                        │ │
│  │  ──────────────────────────────────────────────────────────────────── │ │
│  │  6 sources │ 850 MB total │ 2 selected (254 MB)                       │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [Space] Toggle    [d] Delete selected    [D] Delete ALL (850 MB)          │
│  [p] Pre-cache region    [r] Refresh    [q] Back to menu                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Pre-Cache Region Selection

```
┌─ Pre-Cache Region ──────────────────────────────────────────────────────────┐
│                                                                             │
│  Download data for offline use                                              │
│                                                                             │
│  ┌─ Select Region ────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  (•) Single State                                                      │ │
│  │      └─ State: [Vermont                    ▼]                          │ │
│  │                                                                        │ │
│  │  ( ) Multi-State Region                                                │ │
│  │      └─ Region: [Northeast (9 states)      ▼]                          │ │
│  │                                                                        │ │
│  │  ( ) Custom Selection                                                  │ │
│  │      └─ [Select states...]                                             │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Data Layers ──────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  Census TIGER/Line:                        Est. Size                   │ │
│  │    [✓] County subdivisions (towns)         ~45 MB                      │ │
│  │    [✓] Area water (lakes, ponds)           ~32 MB                      │ │
│  │    [✓] Linear water (rivers, streams)      ~28 MB                      │ │
│  │    [✓] Roads (primary & secondary)         ~41 MB                      │ │
│  │    [ ] Counties                            ~2 MB                       │ │
│  │    [ ] Census tracts                       ~8 MB                       │ │
│  │    [ ] Places (cities, villages)           ~3 MB                       │ │
│  │                                                                        │ │
│  │  Already cached: 156 MB (will skip)                                    │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Summary ──────────────────────────────────────────────────────────────┐ │
│  │  Region: Vermont (all layers)                                          │ │
│  │  New data to download: 0 MB (already cached)                           │ │
│  │  Estimated time: Instant                                               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [Enter] Start download    [Escape] Cancel                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Download Progress

```
┌─ Downloading ───────────────────────────────────────────────────────────────┐
│                                                                             │
│  Pre-caching: New Hampshire (all layers)                                    │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  Overall Progress                                                      │ │
│  │  [████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 42%     │ │
│  │                                                                        │ │
│  │  41 MB of 98 MB │ 2:34 elapsed │ ~3:30 remaining                      │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Files ────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  [✓] tl_2023_33_cousub.zip                     23 MB     Complete     │ │
│  │  [▶] tl_2023_33_areawater.zip                  18 MB     42% ████░░░░ │ │
│  │  [ ] tl_2023_33_linearwater.zip                15 MB     Pending      │ │
│  │  [ ] tl_2023_33_prisecroads.zip                42 MB     Pending      │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Speed: 1.2 MB/s │ Source: Census Bureau TIGER/Line                        │
│                                                                             │
│  [Space] Pause    [Escape] Cancel (keeps completed files)                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 5: Layer Configuration

### 5.1 Layer Selection (Auto-Suggested)

```
┌─ Configure Layers ──────────────────────────────────────────────────────────┐
│  Step 3 of 5: Map Layers                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Scale detected: LOCAL (50 mi² area)                                        │
│  Suggested layers for Burlington area:                                      │
│                                                                             │
│  ┌─ Layers (draw order: bottom → top) ────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  #   LAYER                  TYPE     FILL        STROKE      SOURCE    │ │
│  │  ─────────────────────────────────────────────────────────────────────│ │
│  │  1   [✓] Context towns      Polygon  ░░░░░░░░░   ─────────   cousub   │ │
│  │          (neighboring)               #f5f5f5     #e0e0e0              │ │
│  │                                                                        │ │
│  │  2   [✓] Water bodies       Polygon  ░░░░░░░░░   ─────────   areawater│ │
│  │                                      #b3e5fc     #1565c0              │ │
│  │                                                                        │ │
│  │  3   [✓] Rivers & streams   Line     ░░░░░░░░░   ─────────   linear   │ │
│  │                                      (none)      #1976d2     water    │ │
│  │                                                                        │ │
│  │  4   [✓] Selected towns     Polygon  ░░░░░░░░░   ━━━━━━━━━   cousub   │ │
│  │      ▸ (Burlington, etc)             #ffffff     #424242    (filtered)│ │
│  │                                                                        │ │
│  │  5   [✓] Roads              Line     ░░░░░░░░░   ─────────   prisec   │ │
│  │                                      (none)      #757575     roads    │ │
│  │                                                                        │ │
│  │  6   [ ] Town labels        Text     ░░░░░░░░░   ─────────   (gen)    │ │
│  │                                      (none)      #212121              │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [↑↓] Select    [Space] Toggle    [e] Edit style    [+] Add layer          │
│  [Page Up/Dn] Reorder    [Enter] Continue    [Esc] Back                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Layer Style Editor

```
┌─ Edit Layer Style ──────────────────────────────────────────────────────────┐
│                                                                             │
│  Layer: Selected towns (Polygon)                                            │
│                                                                             │
│  ┌─ Preview ──────────────────┐  ┌─ Settings ─────────────────────────────┐ │
│  │                            │  │                                        │ │
│  │    ┌────────────────┐      │  │  Fill                                  │ │
│  │    │                │      │  │  ├─ Color:    [#ffffff] ████████████   │ │
│  │    │   Sample       │      │  │  ├─ Opacity:  [100] %                  │ │
│  │    │   Polygon      │      │  │  └─ Vary by feature: [ ]               │ │
│  │    │                │      │  │                                        │ │
│  │    └────────────────┘      │  │  Stroke                                │ │
│  │                            │  │  ├─ Color:    [#424242] ████████████   │ │
│  │                            │  │  ├─ Width:    [1.5] px                 │ │
│  │                            │  │  ├─ Opacity:  [100] %                  │ │
│  │                            │  │  └─ Style:    [Solid          ▼]      │ │
│  │                            │  │                                        │ │
│  └────────────────────────────┘  │  Operations                            │ │
│                                  │  ├─ [✓] Simplify (tolerance: 0.0003)   │ │
│                                  │  ├─ [ ] Subtract water bodies          │ │
│                                  │  └─ [ ] Remove holes                   │ │
│                                  │                                        │ │
│                                  │  Data Filter                           │ │
│                                  │  └─ [Edit filter expression...]        │ │
│                                  │                                        │ │
│                                  └────────────────────────────────────────┘ │
│                                                                             │
│  Presets: [Default] [Muted] [Bold] [Outline Only] [Water Style]            │
│                                                                             │
│  [Tab] Next field    [Enter] Save    [Esc] Cancel                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Add Layer Dialog

```
┌─ Add Layer ─────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌─ Available Sources ────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  Currently loaded:                                                     │ │
│  │    ● census:tiger/2023/vt/cousub        (in use)                      │ │
│  │    ● census:tiger/2023/vt/areawater     (in use)                      │ │
│  │    ● census:tiger/2023/vt/linearwater   (in use)                      │ │
│  │    ● census:tiger/2023/vt/prisecroads   (in use)                      │ │
│  │                                                                        │ │
│  │  Additional (cached):                                                  │ │
│  │  ▸ ○ census:tiger/2023/vt/county        Counties                      │ │
│  │    ○ census:tiger/2023/vt/place         Cities & villages             │ │
│  │    ○ census:tiger/2023/vt/tract         Census tracts                 │ │
│  │                                                                        │ │
│  │  Additional (requires download):                                       │ │
│  │    ◌ canada:nhn/02OJ000/rivers          Richelieu River (~12 MB)      │ │
│  │    ◌ openskimap:runs                    Ski trails (~200 MB)          │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Legend: ● In use  ○ Cached  ◌ Not cached                                  │
│                                                                             │
│  [↑↓] Select    [Enter] Add layer    [d] Download & add    [Esc] Cancel   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 6: Output Generation

### 6.1 Output Configuration

```
┌─ Output Settings ───────────────────────────────────────────────────────────┐
│  Step 4 of 5: Configure Output                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ Format ───────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  Primary output:                                                       │ │
│  │    (•) PDF  - Print-ready, vector graphics                            │ │
│  │    ( ) PNG  - Raster image for web/preview                            │ │
│  │    ( ) SVG  - Vector, editable, plotter-ready                         │ │
│  │                                                                        │ │
│  │  Additional formats:                                                   │ │
│  │    [ ] Also export SVG (for editing)                                  │ │
│  │    [ ] Also export GeoJSON (for web maps)                             │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Page Size ──────────────────┐  ┌─ Quality ─────────────────────────┐   │
│  │                              │  │                                   │   │
│  │  Preset: [Tabloid 11×17  ▼]  │  │  (•) Print (300 DPI)             │   │
│  │                              │  │  ( ) Web (150 DPI)               │   │
│  │  Width:  [11.0] inches       │  │  ( ) Draft (72 DPI)              │   │
│  │  Height: [17.0] inches       │  │                                   │   │
│  │  Margin: [0.5 ] inches       │  │  Simplification: [Medium     ▼]  │   │
│  │                              │  │                                   │   │
│  │  Orientation:                │  └───────────────────────────────────┘   │
│  │  (•) Portrait  ( ) Landscape │                                          │
│  │                              │                                          │
│  └──────────────────────────────┘                                          │
│                                                                             │
│  ┌─ Output Path ──────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  Directory: ~/Maps/                                                    │ │
│  │  Filename:  burlington_area_2024                                       │ │
│  │                                                                        │ │
│  │  Will create: ~/Maps/burlington_area_2024.pdf                         │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [Tab] Next field    [Enter] Continue to preview    [Esc] Back             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Pre-Build Preview

```
┌─ Preview & Build ───────────────────────────────────────────────────────────┐
│  Step 5 of 5: Review & Generate                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ Map Preview ──────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │           ╭───────────────────────────────────────────╮               │ │
│  │          ╱            Milton         Georgia           ╲              │ │
│  │         │    ╭─────────────────────────────────╮        │             │ │
│  │         │   ╱       Colchester                  ╲       │             │ │
│  │         │  │  ┌─────────────────────────────┐    │      │             │ │
│  │    ~~~~ │  │  │ BURLINGTON │    Winooski    │    │      │             │ │
│  │   ~Lake~│  │  │            │                │    │Essex │             │ │
│  │  ~Champ~│  │  │  S. Burl.  │                │    │      │             │ │
│  │   ~~~~~│  │   └─────────────────────────────┘   │      │             │ │
│  │         │  │   Shelburne         Williston      │      │             │ │
│  │         │   ╲____________________________________╱      │             │ │
│  │          ╲           Charlotte        Hinesburg        ╱              │ │
│  │           ╰───────────────────────────────────────────╯               │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Summary ──────────────────────────────────────────────────────────────┐ │
│  │  Features: 18 towns, 47 water bodies, 312 road segments               │ │
│  │  Output:   ~/Maps/burlington_area_2024.pdf (est. 2.4 MB)              │ │
│  │  Time:     ~15 seconds                                                 │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [p] Full preview (opens in viewer)    [Enter] BUILD    [Esc] Back         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Build Progress

```
┌─ Building Map ──────────────────────────────────────────────────────────────┐
│                                                                             │
│  burlington_area_2024.pdf                                                   │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  [████████████████████████████████████████░░░░░░░░░░░░░░░░░░] 68%     │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Progress ─────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  [✓] Loading sources                                    0.8s          │ │
│  │  [✓] Clipping to bounds                                 1.2s          │ │
│  │  [✓] Processing layer: Context towns                    0.4s          │ │
│  │  [✓] Processing layer: Water bodies                     0.6s          │ │
│  │  [✓] Processing layer: Rivers & streams                 0.3s          │ │
│  │  [▶] Processing layer: Selected towns                   0.2s...       │ │
│  │  [ ] Processing layer: Roads                            pending       │ │
│  │  [ ] Rendering SVG                                      pending       │ │
│  │  [ ] Converting to PDF                                  pending       │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Elapsed: 3.5s │ Remaining: ~1.7s                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.4 Build Complete

```
┌─ Complete ──────────────────────────────────────────────────────────────────┐
│                                                                             │
│                              ✓ Map Generated!                               │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │                         [Thumbnail Preview]                            │ │
│  │                                                                        │ │
│  │                    ┌───────────────────────┐                          │ │
│  │                    │                       │                          │ │
│  │                    │    Burlington Area    │                          │ │
│  │                    │        Map            │                          │ │
│  │                    │                       │                          │ │
│  │                    └───────────────────────┘                          │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Output: ~/Maps/burlington_area_2024.pdf                                   │
│  Size:   2.3 MB                                                            │
│  Time:   5.2 seconds                                                       │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  [o] Open file         [f] Show in Finder        [r] Open recipe      │ │
│  │                                                                        │ │
│  │  [n] New map           [b] Batch from this       [q] Quit             │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 7: Batch Mode

### 7.1 Batch Mode Entry

```
┌─ Batch Mode ────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Generate multiple maps with consistent styling                             │
│                                                                             │
│  ┌─ Batch Type ───────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  (•) One map per feature                                              │ │
│  │      Generate a separate map for each town, county, etc.              │ │
│  │                                                                        │ │
│  │  ( ) Grid/Atlas pages                                                 │ │
│  │      Divide a large area into consistent page tiles                   │ │
│  │                                                                        │ │
│  │  ( ) Multiple regions                                                 │ │
│  │      Same style applied to different selected areas                   │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [Enter] Continue    [Esc] Back to menu                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Batch Parent Selection

```
┌─ Select Parent Region ──────────────────────────────────────────────────────┐
│  Batch Step 1 of 4: Choose container region                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  What region contains the features you want to map?                         │
│                                                                             │
│  ┌─ Region ───────────────────┐  ┌─ Preview ─────────────────────────────┐ │
│  │                            │  │        ╭──────────────────╮           │ │
│  │  Recent:                   │  │       ╱                    ╲          │ │
│  │    Vermont                 │  │      │      VERMONT        │          │ │
│  │    Chittenden County       │  │      │                     │          │ │
│  │                            │  │      │    14 counties      │          │ │
│  │  Browse:                   │  │      │    251 towns        │          │ │
│  │  ▸ Vermont              ◀──┼──│      │                     │          │ │
│  │    New Hampshire           │  │      │                     │          │ │
│  │    New York                │  │       ╲                   ╱           │ │
│  │    Quebec                  │  │        ╰──────────────────╯           │ │
│  │    [Browse more...]        │  │                                       │ │
│  │                            │  │  Batch options:                       │ │
│  │                            │  │    • 14 counties                      │ │
│  │                            │  │    • 251 towns (county subdivisions)  │ │
│  │                            │  │                                       │ │
│  └────────────────────────────┘  └───────────────────────────────────────┘ │
│                                                                             │
│  [↑↓] Navigate    [Enter] Select    [/] Search    [Esc] Back               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Batch Feature Selection

```
┌─ Select Features ───────────────────────────────────────────────────────────┐
│  Batch Step 2 of 4: Choose which features to map                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Parent: Vermont │ Batch by: Towns (county subdivisions)                    │
│  Found 251 towns                                                            │
│                                                                             │
│  ┌─ Filter ───────────────────────────────────────────────────────────────┐ │
│  │  ( ) All 251 towns                                                     │ │
│  │  (•) By county                                                         │ │
│  │  ( ) By name pattern                                                   │ │
│  │  ( ) Manual selection                                                  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Select Counties ──────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  [✓] Addison (23 towns)         [ ] Lamoille (10 towns)               │ │
│  │  [ ] Bennington (17 towns)      [ ] Orange (17 towns)                 │ │
│  │  [ ] Caledonia (17 towns)       [ ] Orleans (19 towns)                │ │
│  │  [✓] Chittenden (18 towns)      [ ] Rutland (27 towns)                │ │
│  │  [ ] Essex (9 towns)            [✓] Washington (20 towns)             │ │
│  │  [ ] Franklin (15 towns)        [ ] Windham (23 towns)                │ │
│  │  [ ] Grand Isle (5 towns)       [ ] Windsor (24 towns)                │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Selected: 61 towns in 3 counties                                          │
│                                                                             │
│  [Space] Toggle county    [a] All    [n] None    [Enter] Continue          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.4 Batch Layer Configuration

```
┌─ Batch Layer Settings ──────────────────────────────────────────────────────┐
│  Batch Step 3 of 4: Configure layers (applied to all maps)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  These settings will be used for all 61 town maps:                          │
│                                                                             │
│  ┌─ Layers ───────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  1  [✓] Neighboring towns (context)     ░░░#fafafa  ───#e0e0e0        │ │
│  │         Shown ghosted in background                                    │ │
│  │                                                                        │ │
│  │  2  [✓] Water bodies                    ░░░#b3e5fc  ───#1565c0        │ │
│  │         Lakes and ponds within/near town                               │ │
│  │                                                                        │ │
│  │  3  [✓] Rivers & streams                (none)      ───#1976d2        │ │
│  │         Waterways within/near town                                     │ │
│  │                                                                        │ │
│  │  4  [✓] Focus town (highlighted)        ░░░#ffffff  ━━━#424242        │ │
│  │         The town being mapped (bold outline)                           │ │
│  │                                                                        │ │
│  │  5  [ ] Roads                           (none)      ───#757575        │ │
│  │                                                                        │ │
│  │  6  [✓] Town label                      (text)      ───#212121        │ │
│  │         Centered name label                                            │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [↑↓] Select    [Space] Toggle    [e] Edit style    [Enter] Continue       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.5 Batch Output Configuration

```
┌─ Batch Output Settings ─────────────────────────────────────────────────────┐
│  Batch Step 4 of 4: Configure output                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Generating 61 town maps...                                                 │
│                                                                             │
│  ┌─ Bounds Mode ──────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  (•) Fit to each feature                                              │ │
│  │      Auto-crop to town bounds + padding                                │ │
│  │                                                                        │ │
│  │  ( ) Fixed size, centered                                             │ │
│  │      Same dimensions for all, centered on town centroid                │ │
│  │                                                                        │ │
│  │  Padding: [15] % around each feature                                   │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Output ───────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  Format:    [PDF              ▼]     Quality: [Print 300 DPI    ▼]    │ │
│  │  Page size: [Letter 8.5×11   ▼]     Orientation: (•) Auto ( ) Fixed  │ │
│  │                                                                        │ │
│  │  Directory: ~/Maps/vermont_towns/                                      │ │
│  │  Pattern:   {county}/{name}.pdf                                        │ │
│  │                                                                        │ │
│  │  Examples:                                                             │ │
│  │    addison/addison.pdf                                                │ │
│  │    addison/bridport.pdf                                               │ │
│  │    chittenden/burlington.pdf                                          │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Estimated: 61 files │ ~85 MB total │ ~4 minutes                           │
│                                                                             │
│  [p] Preview 3 samples    [Enter] START BATCH    [Esc] Back                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.6 Batch Processing

```
┌─ Batch Processing ──────────────────────────────────────────────────────────┐
│                                                                             │
│  Processing 61 town maps...                                                 │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  [████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░] 56%      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Current: chittenden/hinesburg.pdf (34 of 61)                              │
│                                                                             │
│  ┌─ Statistics ───────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  Elapsed:    2:14              Remaining:   ~1:45                      │ │
│  │  Completed:  33                Pending:     28                         │ │
│  │  Warnings:   0                 Errors:      0                          │ │
│  │  Total size: 47.2 MB           Avg size:    1.4 MB                     │ │
│  │  Avg time:   4.1s per map                                              │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Recent ───────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  ✓ chittenden/essex.pdf                  1.8 MB    4.2s               │ │
│  │  ✓ chittenden/essex_junction.pdf         0.9 MB    2.8s               │ │
│  │  ✓ chittenden/georgia.pdf                1.2 MB    3.4s               │ │
│  │  → chittenden/hinesburg.pdf              processing...                │ │
│  │    chittenden/huntington.pdf             pending                       │ │
│  │    chittenden/jericho.pdf                pending                       │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [Space] Pause    [Escape] Cancel (keeps completed)    [v] View completed  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.7 Batch Complete

```
┌─ Batch Complete ────────────────────────────────────────────────────────────┐
│                                                                             │
│                         ✓ Batch Processing Complete!                        │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │   ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐    │ │
│  │   │ Add │ │ Bri │ │ Bur │ │ Cha │ │ Col │ │ Ess │ │ Fer │ │ ... │    │ │
│  │   │ison │ │ dpo │ │ lin │ │ rlo │ │ che │ │ ex  │ │ ris │ │     │    │ │
│  │   │     │ │ rt  │ │ gto │ │ tte │ │ ste │ │     │ │ bur │ │ +54 │    │ │
│  │   │     │ │     │ │ n   │ │     │ │ r   │ │     │ │ gh  │ │     │    │ │
│  │   └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘    │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ Summary ──────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  Maps generated:  61                                                   │ │
│  │  Total size:      84.7 MB                                              │ │
│  │  Total time:      3:58                                                 │ │
│  │  Output:          ~/Maps/vermont_towns/                                │ │
│  │                                                                        │ │
│  │  Breakdown:                                                            │ │
│  │    addison/       23 files    28.4 MB                                 │ │
│  │    chittenden/    18 files    24.1 MB                                 │ │
│  │    washington/    20 files    32.2 MB                                 │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [o] Open folder    [r] Save recipe    [n] New batch    [q] Quit           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Complete Flow Diagram

```
                                    ┌──────────────┐
                                    │    START     │
                                    │  (strata)    │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │    HOME      │
                                    │    MENU      │
                                    └──────┬───────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
             ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
             │   NEW MAP    │       │    BATCH     │       │    CACHE     │
             │   (Single)   │       │    MODE      │       │   MANAGER    │
             └──────┬───────┘       └──────┬───────┘       └──────────────┘
                    │                      │
                    ▼                      ▼
             ┌──────────────┐       ┌──────────────┐
             │  DRILL-DOWN  │       │   SELECT     │
             │  NAVIGATION  │       │   PARENT     │
             │              │       │   REGION     │
             │ World        │       └──────┬───────┘
             │  └─Continent │              │
             │    └─Country │              ▼
             │      └─State │       ┌──────────────┐
             │        └─... │       │   SELECT     │
             └──────┬───────┘       │   FEATURES   │
                    │               │  (children)  │
                    ▼               └──────┬───────┘
             ┌──────────────┐              │
             │   VISUAL     │              │
             │   CROP       │◄─────────────┘
             │              │
             │ [Pan/Resize] │
             └──────┬───────┘
                    │
                    ▼
             ┌──────────────┐
             │   LAYER      │
             │   CONFIG     │
             │              │
             │ [Add/Style]  │
             └──────┬───────┘
                    │
                    ▼
             ┌──────────────┐
             │   OUTPUT     │
             │   SETTINGS   │
             │              │
             │ [Format/Size]│
             └──────┬───────┘
                    │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
   ┌──────────────┐  ┌──────────────┐
   │   PREVIEW    │  │    BATCH     │
   │   & BUILD    │  │   PROGRESS   │
   │   (single)   │  │  (multiple)  │
   └──────┬───────┘  └──────┬───────┘
          │                 │
          ▼                 ▼
   ┌──────────────┐  ┌──────────────┐
   │   COMPLETE   │  │    BATCH     │
   │   (1 file)   │  │   COMPLETE   │
   │              │  │  (N files)   │
   └──────────────┘  └──────────────┘
```

---

## Keyboard Shortcuts Reference

### Global

| Key | Action |
|-----|--------|
| `q` / `Esc` | Back / Quit |
| `?` | Show help |
| `/` | Search |
| `Tab` | Next field |
| `Shift+Tab` | Previous field |

### Navigation

| Key | Action |
|-----|--------|
| `↑` / `↓` | Move selection |
| `Enter` | Drill down / Confirm |
| `Backspace` | Go up level |
| `Space` | Toggle select |
| `a` | Select all |
| `n` | Select none |

### Crop View

| Key | Action |
|-----|--------|
| `←` `→` `↑` `↓` | Pan view |
| `Shift` + Arrow | Resize crop |
| `+` / `-` | Zoom in/out |
| `[` / `]` | Cycle aspect ratios |
| `f` | Fit to features |
| `c` | Center on selection |

### Batch Mode

| Key | Action |
|-----|--------|
| `Space` | Pause/Resume |
| `v` | View completed |
| `Esc` | Cancel (keeps done) |

---

*TUI Mockups v1.0 - December 2024*
