from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_parent_dir(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def write_json(data: dict[str, Any], path: str | Path) -> Path:
    output = ensure_parent_dir(path)
    with output.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return output


def build_report_envelope(
    *,
    command: str,
    status: str,
    summary: dict[str, Any],
    files: list[dict[str, Any]],
    **extra: Any,
) -> dict[str, Any]:
    report = {
        "command": command,
        "status": status,
        "summary": summary,
        "files": files,
        "generated_at": utc_now_iso(),
    }
    report.update(extra)
    return report


def infer_driver_from_path(path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    drivers = {
        ".gpkg": "GPKG",
        ".shp": "ESRI Shapefile",
        ".geojson": "GeoJSON",
        ".json": "GeoJSON",
        ".parquet": "Parquet",
    }
    if suffix not in drivers:
        raise ValueError(f"Unsupported vector output extension: {suffix}")
    return drivers[suffix]


def safe_stem(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")
