"""
Core geometry operations using Shapely/GeoPandas.
"""

import geopandas as gpd
from shapely.geometry import box, Polygon, MultiPolygon
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


def extract_islands(
    gdf: gpd.GeoDataFrame,
    min_area: float = 0.0,
) -> gpd.GeoDataFrame:
    """
    Extract islands (interior rings/holes) from polygon geometries.

    Water bodies like Lake Champlain are represented as polygons with
    interior rings (holes) where islands exist. This function extracts
    those holes as separate polygon features.

    Args:
        gdf: GeoDataFrame with polygon geometries (e.g., lake polygons)
        min_area: Minimum area in CRS units to include (filters tiny islands)

    Returns:
        GeoDataFrame containing island polygons
    """
    islands = []

    for idx, row in gdf.iterrows():
        geom = row.geometry

        if geom is None or geom.is_empty:
            continue

        # Handle both Polygon and MultiPolygon
        polygons = []
        if isinstance(geom, Polygon):
            polygons = [geom]
        elif isinstance(geom, MultiPolygon):
            polygons = list(geom.geoms)

        for poly in polygons:
            # Extract interior rings (holes = islands in water)
            for interior in poly.interiors:
                island_poly = Polygon(interior)

                # Filter by area
                if island_poly.area >= min_area:
                    # Create a new row with island geometry
                    island_data = {"geometry": island_poly}

                    # Copy relevant attributes from parent
                    for col in gdf.columns:
                        if col != "geometry":
                            island_data[col] = row[col]

                    # Add source info
                    island_data["_source_idx"] = idx
                    island_data["_island_area"] = island_poly.area

                    islands.append(island_data)

    if not islands:
        # Return empty GeoDataFrame with same structure
        return gpd.GeoDataFrame(columns=list(gdf.columns) + ["_source_idx", "_island_area"], crs=gdf.crs)

    return gpd.GeoDataFrame(islands, crs=gdf.crs)


def remove_holes(
    gdf: gpd.GeoDataFrame,
    min_hole_area: float = 0.0,
) -> gpd.GeoDataFrame:
    """
    Remove interior rings (holes) from polygon geometries.

    This creates "filled" polygons without islands, useful when you want
    to show the water body outline without island cutouts.

    Args:
        gdf: GeoDataFrame with polygon geometries
        min_hole_area: Only remove holes larger than this (0 = remove all)

    Returns:
        GeoDataFrame with holes removed
    """
    result = gdf.copy()

    def remove_holes_from_geom(geom):
        if geom is None or geom.is_empty:
            return geom

        if isinstance(geom, Polygon):
            if min_hole_area <= 0:
                # Remove all holes
                return Polygon(geom.exterior)
            else:
                # Keep small holes, remove large ones
                kept_holes = [
                    interior for interior in geom.interiors
                    if Polygon(interior).area < min_hole_area
                ]
                return Polygon(geom.exterior, kept_holes)

        elif isinstance(geom, MultiPolygon):
            new_polys = [remove_holes_from_geom(p) for p in geom.geoms]
            return MultiPolygon(new_polys)

        return geom

    result["geometry"] = result.geometry.apply(remove_holes_from_geom)
    return result
