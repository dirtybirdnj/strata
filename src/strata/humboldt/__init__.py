"""
strata.humboldt: Geometric transformation and spatial analysis.

"Nature considered rationally, that is to say, submitted to the process of
thought, is a unity in diversity of phenomena."
    — Alexander von Humboldt, Cosmos
"""

from .geometry import subtract, clip, merge, simplify, buffer
from .projection import transform_crs

__all__ = [
    "subtract",
    "clip",
    "merge",
    "simplify",
    "buffer",
    "transform_crs",
    "process_layer",
]


def process_layer(
    gdf,
    operations: list[dict],
    sources: dict,
) -> "geopandas.GeoDataFrame":
    """
    Apply a sequence of operations to a GeoDataFrame.

    Args:
        gdf: Input GeoDataFrame
        operations: List of operation configs from recipe
        sources: Dict of loaded source GeoDataFrames (for operation targets)

    Returns:
        Processed GeoDataFrame
    """
    import geopandas as gpd

    result = gdf.copy()

    for op in operations:
        op_type = op.get("type")

        if op_type == "subtract":
            targets = op.get("target", [])
            if isinstance(targets, str):
                targets = [targets]
            for target_name in targets:
                if target_name in sources:
                    result = subtract(result, sources[target_name])

        elif op_type == "clip":
            target = op.get("target")
            if target == "bounds":
                # Clip to output bounds - handled at pipeline level
                pass
            elif target in sources:
                bounds_gdf = sources[target]
                result = clip(result, bounds_gdf.total_bounds)

        elif op_type == "simplify":
            tolerance = op.get("tolerance", 0.0001)
            preserve = op.get("preserve_topology", True)
            result = simplify(result, tolerance, preserve_topology=preserve)

        elif op_type == "merge":
            result = merge(result)

        elif op_type == "buffer":
            distance = op.get("distance", 0)
            result = buffer(result, distance)

        elif op_type == "exclude":
            # Remove features that intersect target
            targets = op.get("target", [])
            if isinstance(targets, str):
                targets = [targets]
            for target_name in targets:
                if target_name in sources:
                    target_gdf = sources[target_name]
                    target_union = target_gdf.geometry.union_all()
                    result = result[~result.geometry.intersects(target_union)]

        elif op_type == "identify_islands":
            # TODO: Implement island detection
            pass

    return result
