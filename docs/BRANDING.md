# Strata: A Layered Approach to Cartographic Data

## Package Architecture

```
strata/
├── __init__.py           # William Smith - the foundation
├── thoreau/              # Data Acquisition
├── humboldt/             # Processing & Transformation
├── kelley/               # Visualization & Output
└── maury/                # Pipeline Orchestration
```

---

## The Voices

Each module's documentation is written in the voice of its namesake historical figure.

---

## 1. William Smith (1769-1839) — Package Foundation

**Role:** The `strata` package itself — the concept of layers

**Title:** "Father of English Geology"

**His Story:** A self-taught canal surveyor who discovered that rock layers (strata) could be identified by their fossil contents. Created the first geological map of an entire nation (1815). Working-class background, practical approach.

### Voice Characteristics
- Practical, hands-on
- Self-taught confidence
- Layer-focused thinking
- Working-class directness

### Key Quotes

> "The same strata were found always in the same order of superposition and contained the same peculiar fossils."

> "Organized fossils are to the naturalist as coins to the antiquary; they are the antiquities of the earth."

### Sample Documentation Voice

```python
"""
strata: A toolkit for layered cartographic data processing.

Just as the Earth reveals its history through the ordering of its
strata—each layer distinct, identifiable, and positioned in proper
relation to those above and below—so too must our maps be constructed.

The order matters. Place your regional backgrounds at the bottom,
your water bodies above, your boundaries with their cutouts next,
and your roads at the very top. Each stratum serves its purpose;
none can be omitted without loss.

I learned this truth not in university halls but in the canal cuts
of Somerset, where the exposed rock faces taught me what no book
could: that nature organizes itself in layers, and we would do well
to follow her example.
"""
```

---

## 2. Henry David Thoreau (1817-1862) — Data Acquisition

**Role:** `strata.thoreau` — fetching and collecting source data

**Title:** Surveyor, Naturalist, Author of *Walden*

**His Story:** Professional land surveyor who supported himself surveying while writing. Created 200 surveys including three of Walden Pond. Combined precise measurement with careful observation.

### Voice Characteristics
- Precise but poetic
- First-person narrative
- Simple tools described plainly
- Finds meaning in measurement
- Gentle skepticism of received wisdom

### Key Quotes

> "I fathomed it easily with a cod-line and a stone weighing about a pound and a half, and could tell accurately when the stone left the bottom, by having to pull so much harder before the water got underneath to help me."

> "It is remarkable how long men will believe in the bottomlessness of a pond without taking the trouble to sound it."

> "I surveyed it carefully, before the ice broke up, early in '46, with compass and chain and sounding line."

> "When I had mapped the pond by the scale of ten rods to an inch, and put down the soundings, more than a hundred in all, I observed this remarkable coincidence."

### Sample Documentation Voice

```python
"""
strata.thoreau: Data acquisition from authoritative sources.

I have walked to the Census Bureau, so to speak, and returned with
their TIGER files—those careful delineations of every county, town,
and water body in the nation. It is remarkable how many will speculate
about boundaries without taking the trouble to fetch the authoritative
source.

The work of acquisition is simple but requires patience. One must
know where to look—the Census for American boundaries, CanVec for
Canadian waters, Quebec's open data for their municipalities. Each
source has its own character, its own way of organizing what it knows.

I find that when I have been fetching data—downloading shapefiles,
converting projections, validating geometries—these were the true
paths to understanding. My processing seems to have put forth new
roots, to be more strongly planted.

Functions:
    fetch_census_tiger() - Acquire US boundaries and water features
    fetch_canvec() - Acquire Canadian vector data
    fetch_quebec_open() - Acquire Quebec municipal boundaries
    validate_source() - Verify the integrity of acquired data
"""
```

---

## 3. Alexander von Humboldt (1769-1859) — Processing & Transformation

**Role:** `strata.humboldt` — geometry operations, transformations, analysis

**Title:** "Father of Ecology," Scientific Explorer

**His Story:** Invented isothermal lines and thematic mapping. Saw nature as an interconnected system. His method: collect observations → compare and combine → reveal hidden connections.

### Voice Characteristics
- Systems thinking
- Unity in diversity
- Transformation of raw data into understanding
- Scientific yet poetic
- Everything is interconnected

### Key Quotes

> "Nature considered rationally, that is to say, submitted to the process of thought, is a unity in diversity of phenomena; a harmony, blending together all created things."

> "The most important aim of all physical science is this: to recognize unity in diversity."

> "It is far more difficult to observe correctly than most men imagine; to behold is not necessarily to observe, and the power of comparing and combining is only to be obtained by education."

> "If instead of geographic maps, we only possessed tables covering latitude, longitude, and altitude, a great number of curious connections that continents manifest in their forms would have stayed forever lost."

### Sample Documentation Voice

```python
"""
strata.humboldt: Geometric transformation and spatial analysis.

The most important aim of all cartographic processing is this: to
recognize unity in diversity—to comprehend all the single features
as revealed by our data sources, to judge single geometries separately
without surrendering their bulk, and to grasp the landscape's essence
under the cover of outer appearances.

When we subtract water from land, we do not merely perform a geometric
operation. We reveal the true relationship between these phenomena—
the way the lake carves its space from the surrounding towns, the way
the island asserts its separation from the mainland. These are not
merely shapes but connections made visible.

I have ever desired to discern spatial phenomena in their widest
mutual connection, and to comprehend Geography as a whole, animated
and moved by inward forces.

Functions:
    cut_water_from_land() - Subtract water bodies from boundaries
    identify_islands() - Find land masses within water features
    merge_features() - Combine geometries into unified wholes
    transform_crs() - Project between coordinate systems
    simplify_topology() - Reduce complexity while preserving form
"""
```

---

## 4. Florence Kelley (1859-1932) — Visualization & Output

**Role:** `strata.kelley` — SVG generation, web maps, color schemes

**Title:** Social Reformer, Pioneer of Social Mapping

**Her Story:** Directed the Hull House Maps and Papers (1895)—first systematic spatial investigation of an American neighborhood. Used maps to reveal patterns invisible in raw data.

### Voice Characteristics
- Direct and purposeful
- Evidence-based
- Pattern-revealing
- Accessible to "the plain man"
- Data serves social purpose

### Key Quotes

> "So that the plain man who pays for the census gets what he pays for, statistical data in a form in which they are ready for him to understand."

> "By looking at just eight pages, the reader could easily see the clustering of nationalities and the distribution of families' weekly wages."

> "Investigate, educate, legislate, enforce."

> "The particularity of the facts breathe life into a time, a place, persons, and tell a tale."

### Sample Documentation Voice

```python
"""
strata.kelley: Visualization that reveals what raw data cannot.

A map is not decoration. A map is evidence.

When we render these geometries to SVG or display them on the web,
we do so with purpose: so that the reader can easily see the patterns
that would remain hidden in tables of coordinates. The clustering of
towns, the threading of rivers, the way Lake Champlain carves through
the landscape—these relationships become visible only when properly
presented.

I have no patience for visualizations that obscure rather than reveal.
Every color choice, every line weight, every layer ordering must serve
the goal of comprehension. Statistical projections which speak to the
senses without fatiguing the mind possess the advantage of fixing
attention on a great number of important facts.

The plain citizen who uses these maps deserves data in a form ready
to understand.

Functions:
    render_svg() - Generate scalable vector graphics
    render_web() - Create interactive Leaflet maps
    apply_colors() - Assign meaningful color schemes
    export_json() - Prepare data for web consumption
"""
```

---

## 5. Matthew Fontaine Maury (1806-1873) — Pipeline Orchestration

**Role:** `strata.maury` — build system, layer composition, coordination

**Title:** "Pathfinder of the Seas," "Father of Oceanography"

**His Story:** Collected ship logs from captains worldwide, aggregated thousands of observations, produced charts that revealed patterns invisible to individual sailors. Established international data standards.

### Voice Characteristics
- Coordination of many sources
- Pattern recognition across data
- Poetic about natural systems
- Confident, eloquent
- Data aggregation pioneer

### Key Quotes

> "There is a river in the ocean. In the severest droughts it never fails, and in the mightiest floods it never overflows."

> "I have been consulting the records of the winds and currents... the results are startling."

> "The sea has its rivers and its currents."

### Sample Documentation Voice

```python
"""
strata.maury: Pipeline orchestration and layer composition.

I have been consulting the records of many sources—the Census Bureau's
careful delineations, the Canadian government's water features, Quebec's
municipal boundaries—and the results, when properly combined, are
remarkable.

No single source tells the complete story. The Census knows American
waters but not Canadian. Quebec knows its municipalities but not the
lake that spans the border. Only by aggregating these observations,
by establishing a uniform system of processing, can we produce charts
worthy of the landscape they represent.

There is a river in the data. It flows from acquisition through
transformation to visualization. In the severest complexity it never
fails, and in the mightiest datasets it never overflows—provided we
respect the proper order of operations.

The layer sandwich is our chart of charts: backgrounds at bottom,
major water bodies above, towns with their cutouts next, small water
to show through, and highways at the very top.

Functions:
    build_all() - Execute the complete pipeline
    compose_layers() - Stack layers in proper order
    validate_pipeline() - Verify all sources and transformations
    LayerStack - The fundamental ordering of cartographic elements
"""
```

---

## Summary: The Cartographic Ensemble

| Module | Person | Era | Role | Voice |
|--------|--------|-----|------|-------|
| `strata` | William Smith | 1810s | Foundation | Practical, layer-focused |
| `strata.thoreau` | Henry David Thoreau | 1850s | Acquisition | Precise, observational |
| `strata.humboldt` | Alexander von Humboldt | 1800s | Processing | Systems thinking, unity |
| `strata.kelley` | Florence Kelley | 1890s | Visualization | Direct, purposeful |
| `strata.maury` | Matthew Fontaine Maury | 1850s | Orchestration | Coordinating, eloquent |

---

## Design Principles (Derived from the Voices)

1. **Layer order matters** (Smith) — The sequence of strata determines what shows through
2. **Go to the source** (Thoreau) — Don't speculate; fetch authoritative data
3. **Seek connections** (Humboldt) — Processing reveals relationships hidden in raw data
4. **Serve the reader** (Kelley) — Visualization must be accessible and purposeful
5. **Coordinate many sources** (Maury) — No single dataset tells the complete story
