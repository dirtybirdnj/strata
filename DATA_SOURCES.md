# Strata Data Sources - North America & Global Coverage

This document catalogs authoritative GIS data sources for building a comprehensive global mapping system.

---

## Current Implementation Status

| Source | Status | Module |
|--------|--------|--------|
| US Census TIGER | ✅ Implemented | `thoreau/census.py` |
| Quebec Open Data | ✅ Implemented | `thoreau/quebec.py` |
| Canada CanVec/NRN | ✅ Implemented | `thoreau/canada.py` |
| OpenSkiMap | ✅ Implemented | `thoreau/openskimap.py` |

---

## North America

### United States

#### Census TIGER (Implemented)
- **URI Pattern**: `census:tiger/2023/{state}/{layer}`
- **Layers**: cousub, areawater, linearwater, prisecroads, county, state, place, tract
- **Coverage**: All 50 states + DC + PR
- **Source**: https://www2.census.gov/geo/tiger/

#### USGS National Hydrography Dataset (NHD)
- **Status**: 🔲 Not implemented
- **URI Pattern**: `usgs:nhd/{region}` or `usgs:nhd/{state}`
- **Data**: Rivers, streams, canals, lakes, ponds, coastline, dams, streamgages
- **Resolution**: 1:24,000 (high) and 1:100,000 (medium)
- **Note**: NHD retired Oct 2023, replaced by 3D Hydrography Program (3DHP)
- **Download**: https://www.usgs.gov/national-hydrography/access-national-hydrography-products
- **Formats**: Shapefile, File Geodatabase

#### USGS National Map - Elevation
- **Status**: 🔲 Not implemented
- **URI Pattern**: `usgs:elevation/{resolution}/{region}`
- **Data**: DEMs at 1/3 arc-second (~10m), 1 arc-second (~30m)
- **Download**: https://apps.nationalmap.gov/downloader/

---

### Canada (Partially Implemented)

#### CanVec Hydro (Implemented)
- **URI Pattern**: `canada:canvec/hydro`
- **Data**: National hydrology at 1:1M scale

#### National Road Network (Implemented)
- **URI Pattern**: `canada:nrn/{province}`
- **Coverage**: All 13 provinces/territories

#### CanVec Topographic (Not Implemented)
- **Status**: 🔲 Not implemented
- **URI Pattern**: `canada:canvec/{theme}`
- **Themes**: transport, buildings, landcover, relief
- **Source**: https://open.canada.ca/data/en/dataset/8ba2aa2a-7bb9-4448-b4d7-f164409fe056

#### Canadian Digital Elevation Model (CDEM)
- **Status**: 🔲 Not implemented
- **URI Pattern**: `canada:cdem/{tile}`
- **Resolution**: ~20m
- **Source**: https://open.canada.ca/data/en/dataset/7f245e4d-76c2-4caa-951a-45d1d2051333

---

### Mexico

#### INEGI (Instituto Nacional de Estadística y Geografía)
- **Status**: 🔲 Not implemented
- **Official Source**: https://www.inegi.org.mx/app/descarga/default.html
- **Interactive Map**: https://www.inegi.org.mx/app/mapa/espacioydatos/default.aspx

**Available Datasets:**

| Dataset | URI Pattern | Description |
|---------|-------------|-------------|
| Marco Geoestadístico | `mexico:mgn/{level}` | Administrative boundaries (state, municipality, locality) |
| Red Nacional de Caminos | `mexico:rnc` | National road network |
| DENUE | `mexico:denue` | National directory of economic units (POIs) |
| Hidrografía | `mexico:hydro` | Rivers, lakes, watersheds |
| Uso de Suelo | `mexico:landuse` | Land use/land cover |

**Alternative Sources:**
- **HDX Administrative Boundaries**: https://data.humdata.org/dataset/cod-ab-mex
  - Admin levels 0-2, updated December 2024
  - Sourced from INEGI, provided via ITOS/USAID
- **IGISMAP**: https://www.igismap.com/download-mexico-shapefile-free-boundary-line-polygon/

---

## Global Sources

### Natural Earth
- **Status**: 🔲 Not implemented (high priority for world base maps)
- **URI Pattern**: `naturalearth:{scale}/{category}/{layer}`
- **Scales**: 10m, 50m, 110m
- **Source**: https://www.naturalearthdata.com/downloads/

**Key Layers:**

| Layer | Scale | Description |
|-------|-------|-------------|
| `ne:10m/cultural/admin_0_countries` | 1:10M | 258 countries |
| `ne:10m/cultural/admin_1_states_provinces` | 1:10M | States/provinces |
| `ne:10m/cultural/populated_places` | 1:10M | Cities/towns |
| `ne:10m/physical/rivers_lake_centerlines` | 1:10M | Major rivers |
| `ne:10m/physical/lakes` | 1:10M | Major lakes |
| `ne:10m/physical/coastline` | 1:10M | Global coastline |
| `ne:10m/physical/land` | 1:10M | Land polygons |
| `ne:10m/physical/ocean` | 1:10M | Ocean polygon |

**Download Options:**
- All vector themes: SHP (576 MB), SQLite (423 MB), GeoPackage (436 MB)
- Individual layers available
- Public domain, free for any use

---

### OpenStreetMap via Geofabrik
- **Status**: 🔲 Not implemented
- **URI Pattern**: `osm:{region}` or `osm:{country}/{subregion}`
- **Source**: https://download.geofabrik.de/
- **Updates**: Daily

**Available Regions:**
- Continents: africa, antarctica, asia, australia-oceania, central-america, europe, north-america, south-america
- Countries and subregions within each continent
- US states available individually

**Formats:**
- `.osm.pbf` - Raw OSM data (compact)
- `.shp.zip` - Shapefiles (roads, railways, waterways, POIs, buildings, landuse, natural, places)

**Free Shapefile Layers:**
- Roads (all classes)
- Railways
- Waterways
- Points of interest
- Buildings
- Land use
- Natural features
- Places (cities, towns)

---

### EuroGeographics (Europe)
- **Status**: 🔲 Not implemented
- **URI Pattern**: `eurogeo:{product}`
- **Source**: https://eurogeographics.org/maps-for-europe/

**Open Data Products:**

| Product | Scale | Description |
|---------|-------|-------------|
| EuroGlobalMap | 1:1M | Admin boundaries, transport, settlements, water |
| EuroDEM | - | European DEM |
| Open Gazetteer | - | European place names |

- Coverage: 45 countries and territories
- INSPIRE compliant
- NUTS/LAU codes for EU member states

---

## Topographic / Elevation Data

### SRTM (Shuttle Radar Topography Mission)
- **Status**: 🔲 Not implemented
- **URI Pattern**: `srtm:{resolution}/{tile}` or `srtm:30m/{lat}/{lon}`
- **Resolutions**: 30m (1 arc-second), 90m (3 arc-second)
- **Coverage**: 56°S to 60°N (80% of Earth's land)
- **Format**: HGT files (height grid)

**Download Sources:**
- [OpenTopography](https://portal.opentopography.org/datasetMetadata?otCollectionID=OT.042013.4326.1)
- [Derek Watkins SRTM Downloader](https://dwtkns.com/srtm30m/) - Interactive tile selector
- [CGIAR-CSI](https://csidotinfo.wordpress.com/data/srtm-90m-digital-elevation-database-v4-1/) - Void-filled, 5°x5° tiles
- [USGS Earth Explorer](https://earthexplorer.usgs.gov/)

### ASTER GDEM
- **Status**: 🔲 Not implemented
- **URI Pattern**: `aster:{tile}`
- **Resolution**: 30m
- **Coverage**: 83°N to 83°S (near-global)
- **Source**: https://asterweb.jpl.nasa.gov/gdem.asp
- **Note**: Better than SRTM in rugged mountainous terrain

### Viewfinder Panoramas (Void-Filled DEMs)
- **Status**: 🔲 Not implemented
- **URI Pattern**: `vfp:{region}`
- **Source**: https://viewfinderpanoramas.org/dem3.html
- **Note**: SRTM/GDEM with voids filled using accurate topographic mapping
- **Canada**: Uses 0.75" Geobase data resampled to 3"

---

## Bathymetric Data

### GEBCO (General Bathymetric Chart of the Oceans)
- **Status**: 🔲 Not implemented
- **URI Pattern**: `gebco:grid` or `gebco:contours`
- **Resolution**: 15 arc-second (~450m)
- **Coverage**: Global ocean and land
- **Source**: https://download.gebco.net/
- **License**: Public domain

**Products:**
| Product | Format | Description |
|---------|--------|-------------|
| GEBCO_2025 Grid | NetCDF, GeoTIFF | Global terrain model |
| GEBCO TID Grid | NetCDF | Source identification grid |

**Pre-processed Contours (OpenDEM):**
- **Source**: https://www.opendem.info/download_bathymetry.html
- **License**: ODbL
- Contour intervals: -25m to -12000m
- Clipped by OSM water polygons

### ETOPO (Global Relief Model)
- **Status**: 🔲 Not implemented
- **URI Pattern**: `etopo:{version}/{resolution}`
- **Current Version**: ETOPO 2022
- **Resolutions**: 15 arc-second, 30 arc-second, 1 arc-minute
- **Source**: https://www.ncei.noaa.gov/products/etopo-global-relief-model

**Features:**
- Combines topography + bathymetry seamlessly
- Ice Surface and Bedrock versions
- Includes ICESat-2 validation
- Public domain (NOAA)

**Use Cases:**
- Tsunami forecasting
- Ocean circulation modeling
- Earth visualization

---

## Thematic Global Datasets

### World Database on Protected Areas (WDPA)
- **Status**: 🔲 Not implemented
- **URI Pattern**: `wdpa:polygons` or `wdpa:points`
- **Source**: https://www.protectedplanet.net/
- **Coverage**: 260,000+ protected areas in 245 countries
- **Updates**: Monthly
- **License**: Free for non-commercial use

**Data Includes:**
- National parks
- Nature reserves
- Marine protected areas
- World Heritage sites
- IUCN categories

### Global Administrative Areas (GADM)
- **Status**: 🔲 Not implemented
- **URI Pattern**: `gadm:{country}/{level}`
- **Source**: https://gadm.org/
- **Coverage**: All countries, multiple admin levels
- **License**: Free for non-commercial use

---

## Implementation Priority

### Phase 1: North America Complete
1. **Mexico INEGI** - Administrative boundaries + roads
2. **USGS NHD** - US hydrography (higher detail than TIGER areawater)

### Phase 2: Global Base Maps
3. **Natural Earth** - World countries, coastlines, major features
4. **OpenStreetMap/Geofabrik** - Detailed roads, buildings, POIs

### Phase 3: Elevation & Depth
5. **SRTM/ASTER** - Global elevation (raster → contour conversion)
6. **GEBCO** - Ocean bathymetry
7. **ETOPO** - Combined topo/bathy

### Phase 4: Thematic Layers
8. **WDPA** - Protected areas
9. **EuroGeographics** - European admin boundaries

---

## Technical Considerations

### Raster vs Vector
Elevation data (SRTM, ASTER, ETOPO, GEBCO grids) is raster format. For pen plotter output, need:
1. Contour generation (GDAL `gdal_contour`)
2. Simplification
3. SVG path conversion

### Large File Handling
| Source | Typical Size | Strategy |
|--------|--------------|----------|
| INEGI MGN | ~500MB | State-by-state download |
| Natural Earth 10m | ~600MB | One-time download, local cache |
| OSM Geofabrik | 1-50GB per country | Region extracts, streaming |
| SRTM tiles | ~25MB per tile | Tile-based lazy loading |
| GEBCO | ~8GB global | Regional extracts via API |

### Coordinate Systems
All sources use WGS84 (EPSG:4326) as base. Strata already handles CRS transformation for area calculations.

### Rate Limits & Terms
| Source | Limits | Terms |
|--------|--------|-------|
| INEGI | None stated | Open data |
| OpenSkiMap | 1 download/day | ODbL |
| WDPA | None | Non-commercial free |
| Geofabrik | Fair use | ODbL |
| SRTM/ASTER | None | Public domain |

---

## Global Coverage Matrix

### Coverage Status Legend
- ✅ **Full** - Official open data, high quality, regularly updated
- 🟡 **Partial** - Some data available, may have gaps or restrictions
- 🟠 **Limited** - Only global datasets (Natural Earth, OSM), no official sources
- 🔴 **Restricted** - Legal barriers to data collection/export
- ⬛ **Unavailable** - No feasible access

---

### North America

| Country/Territory | Admin Bounds | Roads | Hydro | Elevation | Status | Notes |
|-------------------|--------------|-------|-------|-----------|--------|-------|
| 🇺🇸 United States | ✅ TIGER | ✅ TIGER | ✅ NHD | ✅ USGS | ✅ Full | Excellent coverage |
| 🇨🇦 Canada | ✅ StatCan | ✅ NRN | ✅ CanVec | ✅ CDEM | ✅ Full | All open data |
| 🇲🇽 Mexico | ✅ INEGI | ✅ RNC | ✅ INEGI | 🟡 | ✅ Full | Implement next |
| 🇬🇹 Guatemala | 🟡 IGN | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇧🇿 Belize | 🟠 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | |
| 🇭🇳 Honduras | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇸🇻 El Salvador | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇳🇮 Nicaragua | 🟡 INETER | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇨🇷 Costa Rica | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇵🇦 Panama | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇨🇺 Cuba | 🟠 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | US sanctions complicate |
| 🇯🇲 Jamaica | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇭🇹 Haiti | 🟡 HDX | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | Humanitarian focus |
| 🇩🇴 Dominican Rep. | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇵🇷 Puerto Rico | ✅ TIGER | ✅ TIGER | ✅ NHD | ✅ USGS | ✅ Full | US territory |
| Caribbean Islands | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | Variable by island |

### South America

| Country | Admin Bounds | Roads | Hydro | Elevation | Status | Notes |
|---------|--------------|-------|-------|-----------|--------|-------|
| 🇧🇷 Brazil | ✅ IBGE | 🟡 | ✅ ANA | 🟡 SRTM | ✅ Full | Excellent open data |
| 🇦🇷 Argentina | ✅ IGN | 🟡 | 🟡 | 🟡 SRTM | 🟡 Partial | |
| 🇨🇱 Chile | ✅ IDE Chile | 🟡 | 🟡 | 🟡 SRTM | 🟡 Partial | |
| 🇨🇴 Colombia | ✅ IGAC | 🟡 | 🟡 | 🟡 SRTM | 🟡 Partial | |
| 🇵🇪 Peru | 🟡 IGN | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇻🇪 Venezuela | 🟠 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | Political instability |
| 🇪🇨 Ecuador | 🟡 IGM | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇧🇴 Bolivia | 🟡 IGM | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇵🇾 Paraguay | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇺🇾 Uruguay | ✅ IDE | 🟡 | 🟡 | 🟡 SRTM | 🟡 Partial | Good open data |
| 🇬🇾 Guyana | 🟠 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | |
| 🇸🇷 Suriname | 🟠 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | |
| 🇬🇫 French Guiana | 🟡 IGN FR | 🟡 | 🟡 | 🟡 SRTM | 🟡 Partial | French territory |

### Europe

| Country | Admin Bounds | Roads | Hydro | Elevation | Status | Notes |
|---------|--------------|-------|-------|-----------|--------|-------|
| 🇬🇧 United Kingdom | ✅ OS OpenData | ✅ | ✅ | ✅ | ✅ Full | Excellent open data |
| 🇫🇷 France | ✅ IGN | ✅ | ✅ | ✅ | ✅ Full | Via Géoportail |
| 🇩🇪 Germany | ✅ BKG | ✅ | ✅ | ✅ | ✅ Full | Via Geoportal.de |
| 🇮🇹 Italy | ✅ ISTAT | 🟡 | 🟡 | 🟡 | 🟡 Partial | |
| 🇪🇸 Spain | ✅ IGN | ✅ | ✅ | ✅ | ✅ Full | Via CNIG |
| 🇵🇹 Portugal | ✅ DGT | 🟡 | 🟡 | 🟡 | 🟡 Partial | |
| 🇳🇱 Netherlands | ✅ PDOK | ✅ | ✅ | ✅ | ✅ Full | Excellent |
| 🇧🇪 Belgium | ✅ NGI | ✅ | ✅ | ✅ | ✅ Full | |
| 🇨🇭 Switzerland | ✅ SwissTopo | ✅ | ✅ | ✅ | ✅ Full | High quality |
| 🇦🇹 Austria | ✅ BEV | ✅ | ✅ | ✅ | ✅ Full | Via data.gv.at |
| 🇵🇱 Poland | ✅ GUGiK | 🟡 | 🟡 | 🟡 | 🟡 Partial | |
| 🇨🇿 Czechia | ✅ ČÚZK | ✅ | ✅ | ✅ | ✅ Full | |
| 🇸🇪 Sweden | ✅ Lantmäteriet | ✅ | ✅ | ✅ | ✅ Full | |
| 🇳🇴 Norway | ✅ Kartverket | ✅ | ✅ | ✅ | ✅ Full | Excellent |
| 🇫🇮 Finland | ✅ NLS | ✅ | ✅ | ✅ | ✅ Full | |
| 🇩🇰 Denmark | ✅ SDFE | ✅ | ✅ | ✅ | ✅ Full | |
| 🇮🇪 Ireland | ✅ OSi | 🟡 | 🟡 | 🟡 | 🟡 Partial | |
| 🇬🇷 Greece | 🟡 NCMA | 🟠 OSM | 🟠 | 🟡 | 🟡 Partial | |
| 🇷🇺 Russia | 🟡 Rosreestr | 🟠 | 🟠 | 🟡 SRTM | 🟠 Limited | Data localization laws |
| 🇺🇦 Ukraine | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | Conflict zone caveats |
| 🇧🇾 Belarus | 🟠 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | |
| Baltics (EE/LV/LT) | ✅ | ✅ | ✅ | ✅ | ✅ Full | EU open data |
| Balkans | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | Variable |

### Asia

| Country | Admin Bounds | Roads | Hydro | Elevation | Status | Notes |
|---------|--------------|-------|-------|-----------|--------|-------|
| 🇨🇳 China | 🔴 | 🔴 | 🔴 | 🟡 SRTM | 🔴 Restricted | **GCJ-02 required** |
| 🇯🇵 Japan | ✅ GSI | ✅ | ✅ | ✅ | ✅ Full | Excellent |
| 🇰🇷 South Korea | 🔴 | 🔴 | 🔴 | 🟡 | 🔴 Restricted | **Export banned** |
| 🇰🇵 North Korea | ⬛ | ⬛ | ⬛ | 🟡 SRTM | ⬛ Unavailable | No official data |
| 🇹🇼 Taiwan | ✅ NLSC | ✅ | ✅ | ✅ | ✅ Full | |
| 🇮🇳 India | 🔴 | 🟡 | 🟡 | 🟡 SRTM | 🔴 Restricted | **SOI restrictions** |
| 🇵🇰 Pakistan | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇧🇩 Bangladesh | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇹🇭 Thailand | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇻🇳 Vietnam | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇵🇭 Philippines | 🟡 PSA | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇮🇩 Indonesia | 🟡 BIG | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇲🇾 Malaysia | 🟡 JUPEM | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇸🇬 Singapore | ✅ data.gov.sg | ✅ | ✅ | ✅ | ✅ Full | Excellent open data |
| 🇦🇪 UAE | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇸🇦 Saudi Arabia | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇮🇱 Israel | 🟡 SOI | 🟡 | 🟡 | 🟡 | 🟡 Partial | Military zone restrictions |
| 🇹🇷 Turkey | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇮🇷 Iran | 🟠 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | Sanctions complicate |
| 🇦🇫 Afghanistan | 🟠 HDX | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | Conflict zone |
| 🇮🇶 Iraq | 🟡 HDX | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇸🇾 Syria | 🟠 HDX | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | Conflict zone |

### Africa

| Country | Admin Bounds | Roads | Hydro | Elevation | Status | Notes |
|---------|--------------|-------|-------|-----------|--------|-------|
| 🇿🇦 South Africa | ✅ StatsSA | 🟡 | 🟡 | 🟡 SRTM | 🟡 Partial | |
| 🇪🇬 Egypt | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇲🇦 Morocco | 🟡 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇰🇪 Kenya | 🟡 HDX | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇳🇬 Nigeria | 🟡 HDX | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇪🇹 Ethiopia | 🟡 HDX | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| 🇹🇿 Tanzania | 🟡 HDX | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | |
| Most African nations | 🟡 HDX | 🟠 OSM | 🟠 | 🟡 SRTM | 🟡 Partial | Via Humanitarian Data Exchange |

### Oceania

| Country | Admin Bounds | Roads | Hydro | Elevation | Status | Notes |
|---------|--------------|-------|-------|-----------|--------|-------|
| 🇦🇺 Australia | ✅ ABS/GA | ✅ | ✅ | ✅ | ✅ Full | Excellent |
| 🇳🇿 New Zealand | ✅ LINZ | ✅ | ✅ | ✅ | ✅ Full | Excellent open data |
| 🇵🇬 Papua New Guinea | 🟠 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | |
| Pacific Islands | 🟠 | 🟠 OSM | 🟠 | 🟡 SRTM | 🟠 Limited | Variable coverage |

---

## Restricted Regions - Detailed Analysis

### 🔴 CHINA - Coordinate Obfuscation Required

**Legal Framework:**
- Surveying and Mapping Law treats geographic data as national security matter
- "Certain Provisions on the Display of Public Map Content" (2003, updated 2009)
- Personal Information Protection Law (PIPL) restricts cross-border data transfer

**Restrictions:**
- All maps must use **GCJ-02** coordinate system (intentional offset from WGS84)
- Precision finer than 50 meters prohibited
- Elevation grids finer than 100 meters prohibited
- Military bases, airports (except listed), sensitive infrastructure locations banned
- Foreign entities cannot conduct mapping activities without approval

**Practical Impact:**
- Cannot legally obtain or redistribute accurate Chinese map data
- All coordinates have random 100-500m offset
- SRTM elevation data is available (collected from space, not subject to Chinese law)
- Natural Earth and OSM provide coarse coverage

**Strata Approach:**
- Mark China as restricted in UI
- Provide Natural Earth boundaries only
- SRTM elevation available
- Display warning about GCJ-02 offset if users attempt detailed work

---

### 🔴 SOUTH KOREA - Export Ban

**Legal Framework:**
- Geospatial Information Management Act, Article 16
- Act on the Establishment and Management of Spatial Data (2014)
- Map Export Review Committee (requires unanimous approval - never granted)

**Restrictions:**
- Export of map data finer than 1:25,000 scale prohibited
- All export requests have been denied (Google 2011, 2016, 2023; Apple 2023)
- Data cannot leave Korean servers
- National security justification (technical state of war with North Korea)

**Practical Impact:**
- Google Maps, Apple Maps have degraded functionality in South Korea
- Cannot obtain official Korean mapping data
- SRTM elevation available
- OpenStreetMap coverage exists but may have legal gray areas

**Strata Approach:**
- Mark South Korea as restricted
- Provide Natural Earth boundaries
- SRTM elevation available
- Note: OSM data exists but export legality unclear

---

### 🔴 INDIA - Survey of India Restrictions

**Legal Framework:**
- National Map Policy 2005
- Geospatial Information Regulation Bill (proposed, controversial)
- Survey of India controls all official mapping

**Restrictions:**
- High-resolution topographic data restricted
- Defense and sensitive areas cannot be mapped
- Foreign mapping activities require approval
- Data export requires licensing

**Recent Changes (2021):**
- Some liberalization for Indian companies
- Still restrictive for foreign entities
- Ongoing regulatory uncertainty

**Strata Approach:**
- Natural Earth and OSM boundaries available
- SRTM elevation available
- Mark as partially restricted
- Cannot guarantee official data access

---

### ⬛ NORTH KOREA - No Data Available

**Situation:**
- No official mapping agency provides public data
- Closed society with no open data infrastructure
- International sanctions limit engagement

**Available Data:**
- Natural Earth country boundary
- SRTM elevation (satellite-derived)
- OSM has some coverage (from satellite imagery interpretation)
- No official roads, admin boundaries, or hydrology

**Strata Approach:**
- Country outline only from Natural Earth
- SRTM elevation available
- Note extreme data limitations

---

### 🟠 CONFLICT ZONES

**Syria, Yemen, Libya, Sudan, Somalia, etc.**
- Official data sources disrupted or destroyed
- Humanitarian Data Exchange (HDX) provides emergency datasets
- Data may be outdated or incomplete
- Security considerations for mappers

**Strata Approach:**
- Use HDX humanitarian boundaries where available
- SRTM elevation
- Mark as limited/conflict zone
- Note data currency issues

---

### 🟠 SANCTIONED COUNTRIES

**Cuba, Iran, Venezuela, etc.**
- US and international sanctions may restrict data transactions
- Official data sources may exist but access complicated
- OSM coverage variable

**Strata Approach:**
- Natural Earth boundaries
- SRTM elevation
- Note potential legal complications for US users

---

## National Mapping Agencies by Region

### North America
| Country | Agency | Open Data Portal |
|---------|--------|------------------|
| 🇺🇸 USA | USGS, Census Bureau | data.gov, census.gov |
| 🇨🇦 Canada | NRCan, StatCan | open.canada.ca |
| 🇲🇽 Mexico | INEGI | inegi.org.mx |

### Europe (Selected)
| Country | Agency | Open Data Portal |
|---------|--------|------------------|
| 🇬🇧 UK | Ordnance Survey | ordnancesurvey.co.uk/opendata |
| 🇫🇷 France | IGN | geoservices.ign.fr |
| 🇩🇪 Germany | BKG | gdz.bkg.bund.de |
| 🇨🇭 Switzerland | SwissTopo | swisstopo.admin.ch |
| 🇳🇱 Netherlands | Kadaster | pdok.nl |
| 🇳🇴 Norway | Kartverket | kartverket.no |
| 🇸🇪 Sweden | Lantmäteriet | lantmateriet.se |
| 🇫🇮 Finland | NLS | maanmittauslaitos.fi |

### Asia-Pacific
| Country | Agency | Open Data Portal |
|---------|--------|------------------|
| 🇯🇵 Japan | GSI | gsi.go.jp |
| 🇦🇺 Australia | Geoscience Australia | data.gov.au |
| 🇳🇿 New Zealand | LINZ | data.linz.govt.nz |
| 🇸🇬 Singapore | SLA | data.gov.sg |
| 🇹🇼 Taiwan | NLSC | data.gov.tw |

### South America
| Country | Agency | Open Data Portal |
|---------|--------|------------------|
| 🇧🇷 Brazil | IBGE | ibge.gov.br |
| 🇦🇷 Argentina | IGN | ign.gob.ar |
| 🇨🇱 Chile | IGM | ide.cl |
| 🇨🇴 Colombia | IGAC | igac.gov.co |
| 🇺🇾 Uruguay | IDE | ide.uy |

---

## Fallback Data Strategy

For regions without official open data, use this hierarchy:

1. **Humanitarian Data Exchange (HDX)** - https://data.humdata.org/
   - Admin boundaries for 200+ countries
   - Emergency/humanitarian focus
   - Regular updates

2. **GADM (Global Administrative Areas)** - https://gadm.org/
   - All countries, multiple admin levels
   - Free for non-commercial use
   - Academic-maintained

3. **Natural Earth** - https://naturalearthdata.com/
   - Public domain
   - 1:10M, 1:50M, 1:110M scales
   - Countries, states/provinces, major features

4. **OpenStreetMap via Geofabrik** - https://download.geofabrik.de/
   - Crowd-sourced, variable quality
   - ODbL license
   - Daily updates

5. **SRTM/ASTER Elevation** - Always available
   - Satellite-derived, not subject to national laws
   - 30m resolution global coverage

---

## Proposed URI Scheme

```
{provider}:{product}/{params}

Examples:
  mexico:mgn/state              # Mexico states
  mexico:mgn/municipality       # Mexico municipalities
  mexico:rnc                    # Mexico road network

  naturalearth:10m/cultural/admin_0_countries
  naturalearth:50m/physical/rivers

  osm:north-america/us/vermont
  osm:europe/germany

  srtm:30m/N44W073              # Single tile by lat/lon
  srtm:30m/vermont              # State extent (multiple tiles)

  gebco:contours                # Pre-generated contours
  gebco:grid/N40W080            # Grid extract by tile

  etopo:2022/15s                # 15 arc-second resolution

  wdpa:polygons                 # All protected area polygons
  wdpa:points                   # Point-only records
```

---

## Next Steps

1. Implement `thoreau/mexico.py` for INEGI data
2. Implement `thoreau/naturalearth.py` for global base maps
3. Add contour generation utility for raster elevation data
4. Create `thoreau/osm.py` for Geofabrik extracts
5. Update TUI catalog with new sources
