from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import rasterio
from rasterio import features
from rasterio.mask import mask
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling, transform_geom

from .utils import utc_now_iso, write_json


def _vector_geoms_in_raster_crs(gdf: gpd.GeoDataFrame, raster_crs) -> list[dict[str, Any]]:
    if gdf.crs is None:
        raise ValueError("Vector input has no CRS defined.")
    geoms = gdf.geometry.dropna().tolist()
    if not geoms:
        raise ValueError("Vector input contains no usable geometries.")
    if gdf.crs == raster_crs:
        return [geom.__geo_interface__ for geom in geoms]
    return [transform_geom(gdf.crs, raster_crs, geom.__geo_interface__) for geom in geoms]


def _forced_bounds_clip(src, gdf: gpd.GeoDataFrame, output_path: str | Path) -> dict[str, Any]:
    geoms = _vector_geoms_in_raster_crs(gdf, src.crs)
    bounds_geom = [features.geometry_window(src, geoms, north_up=True, pixel_precision=3)]
    del bounds_geom  # explicitly unused; retained to highlight geometry-window concept

    vector_in_src = gdf.to_crs(src.crs)
    minx, miny, maxx, maxy = vector_in_src.total_bounds.tolist()
    res_x, res_y = src.res
    width = max(1, int(np.ceil((maxx - minx) / res_x)))
    height = max(1, int(np.ceil((maxy - miny) / abs(res_y))))
    transform = from_origin(minx, maxy, res_x, abs(res_y))

    destination = np.full((src.count, height, width), src.nodata if src.nodata is not None else 0, dtype=src.dtypes[0])

    for band_idx in range(1, src.count + 1):
        reproject(
            source=rasterio.band(src, band_idx),
            destination=destination[band_idx - 1],
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=src.crs,
            resampling=Resampling.nearest,
            src_nodata=src.nodata,
            dst_nodata=src.nodata if src.nodata is not None else 0,
        )

    mask_arr = features.geometry_mask(
        geoms=geoms,
        out_shape=(height, width),
        transform=transform,
        invert=True,
        all_touched=False,
    )

    nodata = src.nodata if src.nodata is not None else 0
    for idx in range(destination.shape[0]):
        band = destination[idx]
        band[~mask_arr] = nodata

    meta = src.meta.copy()
    meta.update(
        {
            "height": height,
            "width": width,
            "transform": transform,
            "nodata": nodata,
        }
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(output_path, "w", **meta) as dst:
        dst.write(destination)

    return {
        "mode": "force_bounds",
        "width": width,
        "height": height,
        "nodata": nodata,
        "bounds": {"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy},
    }


def clip_raster(
    raster_path: str | Path,
    vector_path: str | Path,
    output_path: str | Path,
    crop: bool = False,
    force_bounds: bool = False,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    gdf = gpd.read_file(vector_path)
    if len(gdf) == 0:
        raise ValueError("Vector input contains zero features.")

    with rasterio.open(raster_path) as src:
        if force_bounds:
            details = _forced_bounds_clip(src, gdf, output_path)
        else:
            geoms = _vector_geoms_in_raster_crs(gdf, src.crs)
            out_image, out_transform = mask(src, geoms, crop=crop)
            out_meta = src.meta.copy()
            out_meta.update(
                {
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                }
            )
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with rasterio.open(output_path, "w", **out_meta) as dst:
                dst.write(out_image)
            details = {
                "mode": "mask",
                "width": out_image.shape[2],
                "height": out_image.shape[1],
                "nodata": src.nodata,
            }

        report = {
            "timestamp_utc": utc_now_iso(),
            "operation": "clip_raster",
            "input_raster": str(raster_path),
            "input_vector": str(vector_path),
            "output_raster": str(output_path),
            "summary": {
                "raster_crs": str(src.crs),
                "vector_crs": str(gdf.crs) if gdf.crs else None,
                "band_count": src.count,
                "dtype": src.dtypes[0],
                **details,
            },
        }

    if report_path:
        write_json(report, report_path)

    return report
