import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

from geo_processing_toolkit.clip import clip_raster


def test_clip_raster(tmp_path):
    raster_path = tmp_path / "input.tif"
    out_path = tmp_path / "clipped.tif"
    vector_path = tmp_path / "mask.gpkg"

    data = np.arange(100, dtype="float32").reshape((10, 10))
    transform = from_origin(0, 10, 1, 1)

    with rasterio.open(
        raster_path,
        "w",
        driver="GTiff",
        height=10,
        width=10,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        nodata=-9999,
    ) as dst:
        dst.write(data, 1)

    gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[box(2, 2, 8, 8)], crs="EPSG:4326")
    gdf.to_file(vector_path, driver="GPKG")

    report = clip_raster(raster_path, vector_path, out_path, crop=True)
    assert report["command"] == "clip-raster"
    assert report["status"] == "PASS"
    assert "generated_at" in report
    assert report["summary"]["band_count"] == 1

    with rasterio.open(out_path) as src:
        clipped = src.read(1)
        assert clipped.shape[0] > 0
        assert clipped.shape[1] > 0
