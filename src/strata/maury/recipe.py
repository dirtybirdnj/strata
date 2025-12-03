"""
Recipe parser and validator for .strata.yaml files.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class SourceConfig(BaseModel):
    """Configuration for a data source."""

    uri: str
    description: str | None = None
    filter: dict[str, Any] | None = None
    clip_to: str | None = None


class OperationConfig(BaseModel):
    """Configuration for a layer operation."""

    type: str
    target: str | list[str] | None = None
    tolerance: float | None = None
    preserve_topology: bool = True
    min_area_km2: float | None = None
    output: str | None = None
    distance: float | None = None


class StyleConfig(BaseModel):
    """Configuration for layer styling."""

    stroke: str = "#333333"
    stroke_width: float = 1.0
    fill: str | None = None
    opacity: float = 1.0
    dash_array: list[float] | None = None


class LayerConfig(BaseModel):
    """Configuration for a map layer."""

    name: str
    source: str | list[str]
    operations: list[OperationConfig] = Field(default_factory=list)
    style: StyleConfig = Field(default_factory=StyleConfig)
    order: int


class QualityConfig(BaseModel):
    """Configuration for a quality level."""

    name: str
    simplify: float


class SVGOptions(BaseModel):
    """Options for SVG output."""

    per_layer: bool = True
    combined: bool = True
    optimize_for: str = "plotter"
    stroke_units: str = "mm"
    page_size: list[float] = Field(default_factory=lambda: [11, 17])
    margin: float = 0.5


class GeoJSONOptions(BaseModel):
    """Options for GeoJSON output."""

    per_layer: bool = True
    precision: int = 6


class PMTilesOptions(BaseModel):
    """Options for PMTiles output."""

    minzoom: int = 4
    maxzoom: int = 14
    attribution: str = ""


class FormatConfig(BaseModel):
    """Configuration for an output format."""

    type: str
    quality: list[QualityConfig] | None = None
    options: SVGOptions | GeoJSONOptions | PMTilesOptions | None = None


class OutputConfig(BaseModel):
    """Configuration for recipe output."""

    bounds: list[float] | str = "auto"
    projection: str = "epsg:4326"
    formats: list[FormatConfig]

    @field_validator("bounds")
    @classmethod
    def validate_bounds(cls, v: list[float] | str) -> list[float] | str:
        if isinstance(v, list):
            if len(v) != 4:
                raise ValueError("Bounds must have 4 values: [west, south, east, north]")
            west, south, east, north = v
            if south > north:
                raise ValueError(f"Invalid bounds: south ({south}) > north ({north})")
            if west > east:
                # Could be crossing antimeridian, allow it
                pass
        return v


class Recipe(BaseModel):
    """A complete Strata recipe."""

    name: str
    description: str = ""
    version: int = 1
    sources: dict[str, SourceConfig]
    layers: list[LayerConfig]
    output: OutputConfig

    @classmethod
    def from_file(cls, path: str | Path) -> "Recipe":
        """Load a recipe from a YAML file."""
        path = Path(path)
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    @classmethod
    def from_yaml(cls, yaml_string: str) -> "Recipe":
        """Load a recipe from a YAML string."""
        data = yaml.safe_load(yaml_string)
        return cls.model_validate(data)

    def to_yaml(self) -> str:
        """Export recipe as YAML."""
        return yaml.dump(
            self.model_dump(exclude_none=True),
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

    def validate_references(self) -> list[str]:
        """Check that all source references in layers are valid."""
        errors = []
        source_names = set(self.sources.keys())

        for layer in self.layers:
            # Check source references
            layer_sources = (
                [layer.source] if isinstance(layer.source, str) else layer.source
            )
            for src in layer_sources:
                if src not in source_names:
                    errors.append(
                        f"Layer '{layer.name}' references undefined source '{src}'"
                    )

            # Check operation target references
            for op in layer.operations:
                if op.target:
                    targets = (
                        [op.target] if isinstance(op.target, str) else op.target
                    )
                    for target in targets:
                        if target not in source_names and target != "bounds":
                            errors.append(
                                f"Layer '{layer.name}' operation references "
                                f"undefined source '{target}'"
                            )

        return errors
