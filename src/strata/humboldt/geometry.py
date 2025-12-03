"""
Core geometry operations using Shapely/GeoPandas.
"""

import geopandas as gpd
from shapely.geometry import box
from shapely.ops import unary_union


def subtract(
    gdf: gpd.GeoDataFrame,
    subtract_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Subtract geometry of one GeoDataFrame from another.

    This is used for water cutouts - removing lake geometry from town boundaries.

    Args:
        gdf: Base GeoDataFrame to subtract from
        subtract_gdf: GeoDataFrame containing geometry to subtract

    Returns:
        GeoDataFrame with subtracted geometry
    """
    # Ensure same CRS
    if gdf.crs != subtract_gdf.crs:
        subtract_gdf = subtract_gdf.to_crs(gdf.crs)

    # Union all subtract geometries into one
    subtract_union = subtract_gdf.geometry.union_all()

    # Subtract from each feature
    result = gdf.copy()
    result["geometry"] = result.geometry.difference(subtract_union)

    # Remove empty geometries
    result = result[~result.geometry.is_empty]

    return result


def clip(
    gdf: gpd.GeoDataFrame,
    bounds: tuple | list,
) -> gpd.GeoDataFrame:
    """
    Clip GeoDataFrame to bounding box.

    Args:
        gdf: GeoDataFrame to clip
        bounds: (minx, miny, maxx, maxy) bounding box

    Returns:
        Clipped GeoDataFrame
    """
    clip_box = box(*bounds)
    return gdf.clip(clip_box)


def clip_to_gdf(
    gdf: gpd.GeoDataFrame,
    clip_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Clip GeoDataFrame to another GeoDataFrame's geometry.

    Args:
        gdf: GeoDataFrame to clip
        clip_gdf: GeoDataFrame defining clip boundary

    Returns:
        Clipped GeoDataFrame
    """
    # Ensure same CRS
    if gdf.crs != clip_gdf.crs:
        clip_gdf = clip_gdf.to_crs(gdf.crs)

    clip_union = clip_gdf.geometry.union_all()
    return gdf.clip(clip_union)


def merge(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Merge all features in a GeoDataFrame into a single geometry.

    Args:
        gdf: GeoDataFrame to merge

    Returns:
        GeoDataFrame with single merged geometry
    """
    merged_geom = gdf.geometry.union_all()
    return gpd.GeoDataFrame(
        {"geometry": [merged_geom]},
        crs=gdf.crs,
    )


def simplify(
    gdf: gpd.GeoDataFrame,
    tolerance: float,
    preserve_topology: bool = True,
) -> gpd.GeoDataFrame:
    """
    Simplify geometries to reduce complexity.

    Args:
        gdf: GeoDataFrame to simplify
        tolerance: Simplification tolerance (higher = more simplified)
        preserve_topology: If True, prevent self-intersections

    Returns:
        Simplified GeoDataFrame
    """
    result = gdf.copy()
    result["geometry"] = result.geometry.simplify(
        tolerance,
        preserve_topology=preserve_topology,
    )
    return result


def buffer(
    gdf: gpd.GeoDataFrame,
    distance: float,
) -> gpd.GeoDataFrame:
    """
    Buffer (expand or contract) geometries.

    Args:
        gdf: GeoDataFrame to buffer
        distance: Buffer distance (positive = expand, negative = contract)

    Returns:
        Buffered GeoDataFrame
    """
    result = gdf.copy()
    result["geometry"] = result.geometry.buffer(distance)
    # Remove empty geometries (from negative buffer)
    result = result[~result.geometry.is_empty]
    return result
