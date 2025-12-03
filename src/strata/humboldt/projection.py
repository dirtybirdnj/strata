"""
Coordinate reference system transformations.
"""

import geopandas as gpd


def transform_crs(
    gdf: gpd.GeoDataFrame,
    target_crs: str,
) -> gpd.GeoDataFrame:
    """
    Transform GeoDataFrame to a different coordinate reference system.

    Args:
        gdf: GeoDataFrame to transform
        target_crs: Target CRS (e.g., "epsg:32145" for Vermont State Plane)

    Returns:
        Transformed GeoDataFrame
    """
    if gdf.crs is None:
        # Assume WGS84 if no CRS set
        gdf = gdf.set_crs("epsg:4326")

    if gdf.crs.to_string().lower() == target_crs.lower():
        return gdf

    return gdf.to_crs(target_crs)


def get_bounds_in_crs(
    bounds: tuple | list,
    source_crs: str = "epsg:4326",
    target_crs: str = "epsg:4326",
) -> tuple:
    """
    Transform bounding box coordinates between CRS.

    Args:
        bounds: (minx, miny, maxx, maxy) in source CRS
        source_crs: Source CRS
        target_crs: Target CRS

    Returns:
        Transformed bounds tuple
    """
    from shapely.geometry import box

    if source_crs.lower() == target_crs.lower():
        return tuple(bounds)

    # Create a box and transform it
    bbox = box(*bounds)
    gdf = gpd.GeoDataFrame({"geometry": [bbox]}, crs=source_crs)
    transformed = gdf.to_crs(target_crs)

    return tuple(transformed.total_bounds)
