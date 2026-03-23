from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd

from .utils import utc_now_iso, write_json


def _field_summary(gdf: gpd.GeoDataFrame) -> list[dict[str, Any]]:
    fields = []
    non_geom_columns = [c for c in gdf.columns if c != gdf.geometry.name]
    for col in non_geom_columns:
        series = gdf[col]
        fields.append(
            {
                "name": col,
                "dtype": str(series.dtype),
                "null_count": int(series.isna().sum()),
                "non_null_count": int(series.notna().sum()),
                "unique_non_null": int(series.dropna().nunique()),
            }
        )
    return fields


def validate_vector_file(input_path: str | Path, report_path: str | Path | None = None) -> dict[str, Any]:
    gdf = gpd.read_file(input_path)

    invalid_count = int((~gdf.geometry.is_valid).fillna(False).sum())
    empty_count = int(gdf.geometry.is_empty.fillna(False).sum())
    null_geom_count = int(gdf.geometry.isna().sum())
    total_count = len(gdf)

    bbox = None
    if total_count > 0:
        minx, miny, maxx, maxy = gdf.total_bounds.tolist()
        bbox = {"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy}

    findings = []
    if gdf.crs is None:
        findings.append("Dataset has no CRS defined.")
    if invalid_count > 0:
        findings.append(f"Dataset contains {invalid_count} invalid geometries.")
    if empty_count > 0:
        findings.append(f"Dataset contains {empty_count} empty geometries.")
    if null_geom_count > 0:
        findings.append(f"Dataset contains {null_geom_count} null geometries.")
    if total_count == 0:
        findings.append("Dataset contains zero features.")

    report = {
        "timestamp_utc": utc_now_iso(),
        "operation": "validate_vector_file",
        "input_path": str(input_path),
        "summary": {
            "feature_count": total_count,
            "invalid_geometries": invalid_count,
            "empty_geometries": empty_count,
            "null_geometries": null_geom_count,
            "crs": str(gdf.crs) if gdf.crs else None,
            "geometry_types": sorted(gdf.geometry.geom_type.dropna().unique().tolist()) if total_count else [],
            "bbox": bbox,
        },
        "fields": _field_summary(gdf),
        "findings": findings,
    }

    if report_path:
        write_json(report, report_path)

    return report
