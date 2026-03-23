from __future__ import annotations

from pathlib import Path
from typing import Iterable

import geopandas as gpd
from shapely.geometry import GeometryCollection
from shapely.geometry.base import BaseGeometry
from shapely.make_valid import make_valid

from .utils import infer_driver_from_path, utc_now_iso, write_json

_ALLOWED_SHP_TYPES = {
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
}


def _fix_geometry(geom: BaseGeometry | None) -> BaseGeometry | None:
    if geom is None or geom.is_empty:
        return geom
    if geom.is_valid:
        return geom
    try:
        fixed = make_valid(geom)
    except Exception:
        fixed = geom.buffer(0)
    return fixed


def _flatten_geometry_collection(geom: BaseGeometry | None) -> list[BaseGeometry | None]:
    if geom is None:
        return [None]
    if geom.is_empty:
        return [geom]
    if isinstance(geom, GeometryCollection):
        parts: list[BaseGeometry] = []
        for sub in geom.geoms:
            parts.extend([g for g in _flatten_geometry_collection(sub) if g is not None])
        return parts or [None]
    return [geom]


def _filter_for_shapefile(geoms: Iterable[BaseGeometry | None]) -> list[BaseGeometry | None]:
    cleaned: list[BaseGeometry | None] = []
    for geom in geoms:
        if geom is None:
            cleaned.append(None)
            continue
        if geom.geom_type in _ALLOWED_SHP_TYPES:
            cleaned.append(geom)
    return cleaned


def fix_geometries(
    input_path: str | Path,
    output_path: str | Path,
    keep_only_valid: bool = False,
    explode_geometry_collections: bool = True,
    report_path: str | Path | None = None,
) -> dict:
    gdf = gpd.read_file(input_path)
    before_invalid = int((~gdf.geometry.is_valid).fillna(False).sum())
    before_empty = int(gdf.geometry.is_empty.fillna(False).sum())
    before_count = len(gdf)

    gdf = gdf.copy()
    gdf["geometry"] = gdf.geometry.apply(_fix_geometry)

    if explode_geometry_collections:
        rows = []
        for _, row in gdf.iterrows():
            parts = _flatten_geometry_collection(row.geometry)
            if Path(output_path).suffix.lower() == ".shp":
                parts = _filter_for_shapefile(parts)
            if not parts:
                continue
            for part in parts:
                new_row = row.copy()
                new_row.geometry = part
                rows.append(new_row)
        gdf = gpd.GeoDataFrame(rows, columns=gdf.columns, crs=gdf.crs)

    if keep_only_valid:
        gdf = gdf[gdf.geometry.notnull()]
        gdf = gdf[~gdf.geometry.is_empty]
        gdf = gdf[gdf.geometry.is_valid]

    after_invalid = int((~gdf.geometry.is_valid).fillna(False).sum()) if len(gdf) else 0
    after_empty = int(gdf.geometry.is_empty.fillna(False).sum()) if len(gdf) else 0

    driver = infer_driver_from_path(output_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver=driver)

    report = {
        "timestamp_utc": utc_now_iso(),
        "operation": "fix_geometries",
        "input_path": str(input_path),
        "output_path": str(output_path),
        "summary": {
            "feature_count_before": before_count,
            "feature_count_after": len(gdf),
            "invalid_geometries_before": before_invalid,
            "invalid_geometries_after": after_invalid,
            "empty_geometries_before": before_empty,
            "empty_geometries_after": after_empty,
            "crs": str(gdf.crs) if gdf.crs else None,
            "geometry_types_after": sorted(gdf.geometry.geom_type.dropna().unique().tolist()) if len(gdf) else [],
        },
    }

    if report_path:
        write_json(report, report_path)

    return report
