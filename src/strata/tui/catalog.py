"""
Data source catalog for the Strata TUI.

Provides a browsable catalog of available data sources including:
- US Census TIGER/Line data (all 50 states + DC + territories)
- Quebec administrative boundaries
- Custom file/URL sources
"""

from dataclasses import dataclass

# US State metadata
US_STATES = {
    "al": {"name": "Alabama", "fips": "01"},
    "ak": {"name": "Alaska", "fips": "02"},
    "az": {"name": "Arizona", "fips": "04"},
    "ar": {"name": "Arkansas", "fips": "05"},
    "ca": {"name": "California", "fips": "06"},
    "co": {"name": "Colorado", "fips": "08"},
    "ct": {"name": "Connecticut", "fips": "09"},
    "de": {"name": "Delaware", "fips": "10"},
    "dc": {"name": "District of Columbia", "fips": "11"},
    "fl": {"name": "Florida", "fips": "12"},
    "ga": {"name": "Georgia", "fips": "13"},
    "hi": {"name": "Hawaii", "fips": "15"},
    "id": {"name": "Idaho", "fips": "16"},
    "il": {"name": "Illinois", "fips": "17"},
    "in": {"name": "Indiana", "fips": "18"},
    "ia": {"name": "Iowa", "fips": "19"},
    "ks": {"name": "Kansas", "fips": "20"},
    "ky": {"name": "Kentucky", "fips": "21"},
    "la": {"name": "Louisiana", "fips": "22"},
    "me": {"name": "Maine", "fips": "23"},
    "md": {"name": "Maryland", "fips": "24"},
    "ma": {"name": "Massachusetts", "fips": "25"},
    "mi": {"name": "Michigan", "fips": "26"},
    "mn": {"name": "Minnesota", "fips": "27"},
    "ms": {"name": "Mississippi", "fips": "28"},
    "mo": {"name": "Missouri", "fips": "29"},
    "mt": {"name": "Montana", "fips": "30"},
    "ne": {"name": "Nebraska", "fips": "31"},
    "nv": {"name": "Nevada", "fips": "32"},
    "nh": {"name": "New Hampshire", "fips": "33"},
    "nj": {"name": "New Jersey", "fips": "34"},
    "nm": {"name": "New Mexico", "fips": "35"},
    "ny": {"name": "New York", "fips": "36"},
    "nc": {"name": "North Carolina", "fips": "37"},
    "nd": {"name": "North Dakota", "fips": "38"},
    "oh": {"name": "Ohio", "fips": "39"},
    "ok": {"name": "Oklahoma", "fips": "40"},
    "or": {"name": "Oregon", "fips": "41"},
    "pa": {"name": "Pennsylvania", "fips": "42"},
    "ri": {"name": "Rhode Island", "fips": "44"},
    "sc": {"name": "South Carolina", "fips": "45"},
    "sd": {"name": "South Dakota", "fips": "46"},
    "tn": {"name": "Tennessee", "fips": "47"},
    "tx": {"name": "Texas", "fips": "48"},
    "ut": {"name": "Utah", "fips": "49"},
    "vt": {"name": "Vermont", "fips": "50"},
    "va": {"name": "Virginia", "fips": "51"},
    "wa": {"name": "Washington", "fips": "53"},
    "wv": {"name": "West Virginia", "fips": "54"},
    "wi": {"name": "Wisconsin", "fips": "55"},
    "wy": {"name": "Wyoming", "fips": "56"},
    "pr": {"name": "Puerto Rico", "fips": "72"},
}

# TIGER layer types with descriptions
TIGER_LAYERS = {
    "cousub": {
        "name": "County Subdivisions",
        "description": "Towns, townships, and other county subdivisions",
        "geometry": "polygon",
    },
    "areawater": {
        "name": "Area Water",
        "description": "Lakes, ponds, reservoirs, and other water bodies",
        "geometry": "polygon",
    },
    "linearwater": {
        "name": "Linear Water",
        "description": "Rivers, streams, and other linear water features",
        "geometry": "line",
    },
    "prisecroads": {
        "name": "Primary & Secondary Roads",
        "description": "Interstates, US routes, and state highways",
        "geometry": "line",
    },
    "county": {
        "name": "Counties",
        "description": "County boundaries",
        "geometry": "polygon",
    },
    "state": {
        "name": "State Outline",
        "description": "State boundary",
        "geometry": "polygon",
    },
    "place": {
        "name": "Places",
        "description": "Cities, towns, CDPs, and other populated places",
        "geometry": "polygon",
    },
    "tract": {
        "name": "Census Tracts",
        "description": "Census tract boundaries (for demographic data)",
        "geometry": "polygon",
    },
}

# Quebec administrative layers
QUEBEC_LAYERS = {
    "municipalities": {
        "name": "Municipalities",
        "description": "Municipal boundaries (villes, municipalités, paroisses)",
        "geometry": "polygon",
        "features": "~2,263",
    },
    "mrc": {
        "name": "MRCs",
        "description": "Municipalités régionales de comté (regional county municipalities)",
        "geometry": "polygon",
        "features": "138",
    },
    "regions": {
        "name": "Administrative Regions",
        "description": "Quebec's 17 administrative regions",
        "geometry": "polygon",
        "features": "21",
    },
    "metropolitan": {
        "name": "Metropolitan Communities",
        "description": "Communautés métropolitaines (Montreal, Quebec City)",
        "geometry": "polygon",
        "features": "2",
    },
}


@dataclass
class CatalogEntry:
    """A single entry in the data source catalog."""

    uri: str
    name: str
    description: str
    geometry: str  # polygon, line, point
    source_type: str  # census, quebec, file, url
    region: str  # State/province name
    cached: bool = False
    estimated_size_mb: float | None = None


def build_census_catalog(year: str = "2023") -> list[CatalogEntry]:
    """Build catalog entries for all Census TIGER layers."""
    entries = []

    for state_code, state_info in US_STATES.items():
        state_name = state_info["name"]

        for layer_code, layer_info in TIGER_LAYERS.items():
            uri = f"census:tiger/{year}/{state_code}/{layer_code}"
            entries.append(
                CatalogEntry(
                    uri=uri,
                    name=f"{state_name} - {layer_info['name']}",
                    description=layer_info["description"],
                    geometry=layer_info["geometry"],
                    source_type="census",
                    region=state_name,
                )
            )

    return entries


def build_quebec_catalog() -> list[CatalogEntry]:
    """Build catalog entries for Quebec administrative boundaries."""
    entries = []

    for layer_code, layer_info in QUEBEC_LAYERS.items():
        uri = f"quebec:{layer_code}"
        entries.append(
            CatalogEntry(
                uri=uri,
                name=f"Quebec - {layer_info['name']}",
                description=layer_info["description"],
                geometry=layer_info["geometry"],
                source_type="quebec",
                region="Quebec",
            )
        )

    return entries


def get_full_catalog() -> list[CatalogEntry]:
    """Get the complete data source catalog."""
    entries = []
    entries.extend(build_census_catalog())
    entries.extend(build_quebec_catalog())
    return entries


def get_states_list() -> list[tuple[str, str]]:
    """Get list of (code, name) tuples for all states, sorted by name."""
    return sorted(
        [(code, info["name"]) for code, info in US_STATES.items()],
        key=lambda x: x[1],
    )


def get_layers_for_source(source_type: str) -> list[tuple[str, str, str]]:
    """Get available layers for a source type.

    Returns list of (code, name, description) tuples.
    """
    if source_type == "census":
        return [
            (code, info["name"], info["description"])
            for code, info in TIGER_LAYERS.items()
        ]
    elif source_type == "quebec":
        return [
            (code, info["name"], info["description"])
            for code, info in QUEBEC_LAYERS.items()
        ]
    return []
