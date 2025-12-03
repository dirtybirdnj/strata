"""Tests for recipe parsing and validation."""

import pytest

from strata.maury.recipe import Recipe


MINIMAL_RECIPE = """
name: test_map
sources:
  towns:
    uri: census:tiger/2023/vt/cousub
layers:
  - name: towns
    source: towns
    order: 1
output:
  formats:
    - type: geojson
"""


def test_parse_minimal_recipe():
    """Test parsing a minimal valid recipe."""
    recipe = Recipe.from_yaml(MINIMAL_RECIPE)
    assert recipe.name == "test_map"
    assert "towns" in recipe.sources
    assert len(recipe.layers) == 1
    assert recipe.layers[0].name == "towns"


def test_validate_source_references():
    """Test that undefined source references are caught."""
    bad_recipe = """
name: bad_map
sources:
  towns:
    uri: census:tiger/2023/vt/cousub
layers:
  - name: towns
    source: undefined_source
    order: 1
output:
  formats:
    - type: geojson
"""
    recipe = Recipe.from_yaml(bad_recipe)
    errors = recipe.validate_references()
    assert len(errors) == 1
    assert "undefined_source" in errors[0]


def test_validate_bounds():
    """Test that invalid bounds are caught."""
    bad_bounds = """
name: bad_bounds
sources:
  towns:
    uri: census:tiger/2023/vt/cousub
layers:
  - name: towns
    source: towns
    order: 1
output:
  bounds: [-73.5, 45.2, -71.5, 43.0]  # south > north
  formats:
    - type: geojson
"""
    with pytest.raises(ValueError, match="south.*north"):
        Recipe.from_yaml(bad_bounds)


def test_to_yaml():
    """Test YAML export."""
    recipe = Recipe.from_yaml(MINIMAL_RECIPE)
    yaml_output = recipe.to_yaml()
    assert "name: test_map" in yaml_output
    assert "census:tiger/2023/vt/cousub" in yaml_output
