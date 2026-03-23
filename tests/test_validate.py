import geopandas as gpd
from shapely.geometry import Point

from geo_processing_toolkit.validate import validate_vector_file


def test_validate_vector_file(tmp_path):
    gdf = gpd.GeoDataFrame(
        {"name": ["a", "b"]},
        geometry=[Point(0, 0), Point(1, 1)],
        crs="EPSG:4326",
    )
    path = tmp_path / "points.gpkg"
    gdf.to_file(path, driver="GPKG")

    report = validate_vector_file(path)
    assert report["summary"]["feature_count"] == 2
    assert report["summary"]["invalid_geometries"] == 0
    assert report["summary"]["crs"] == "EPSG:4326"
