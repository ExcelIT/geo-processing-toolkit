from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Literal

import numpy as np
import rasterio

from .utils import safe_stem, utc_now_iso, write_json

CompositeMethod = Literal["median", "mean", "max", "min"]


_DATE_PATTERN = re.compile(r"(\d{8})$")
_BAND_PATTERN = re.compile(r"_((B\d{2,3}|B8A))\.tif$", re.IGNORECASE)


def extract_date_from_folder(folder: Path) -> datetime | None:
    match = _DATE_PATTERN.search(folder.name)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y%m%d")


def find_date_folders(input_root: str | Path) -> list[Path]:
    root = Path(input_root)
    folders = [p for p in root.iterdir() if p.is_dir() and extract_date_from_folder(p) is not None]
    return sorted(folders, key=lambda p: extract_date_from_folder(p) or datetime.min)


def get_band_list_from_first_folder(first_folder: Path) -> list[str]:
    bands: set[str] = set()
    for tif in first_folder.glob("*.tif"):
        match = _BAND_PATTERN.search(tif.name)
        if match:
            bands.add(match.group(1).upper())
    return sorted(bands)


def _find_band_file(folder: Path, band: str) -> Path | None:
    for tif in folder.glob("*.tif"):
        match = _BAND_PATTERN.search(tif.name)
        if match and match.group(1).upper() == band.upper():
            return tif
    return None


def _aggregate(stack: np.ndarray, method: CompositeMethod) -> np.ndarray:
    if method == "median":
        return np.nanmedian(stack, axis=0)
    if method == "mean":
        return np.nanmean(stack, axis=0)
    if method == "max":
        return np.nanmax(stack, axis=0)
    if method == "min":
        return np.nanmin(stack, axis=0)
    raise ValueError(f"Unsupported method: {method}")


def build_temporal_composites(
    input_root: str | Path,
    output_dir: str | Path,
    method: CompositeMethod = "median",
    report_path: str | Path | None = None,
) -> dict:
    folders = find_date_folders(input_root)
    if not folders:
        raise ValueError("No date-named subfolders were found in input_root.")

    first_folder = folders[0]
    bands = get_band_list_from_first_folder(first_folder)
    if not bands:
        raise ValueError("No supported band rasters were found in the first date folder.")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs: list[dict] = []

    for band in bands:
        band_arrays = []
        meta = None
        used_files = []

        for folder in folders:
            tif_path = _find_band_file(folder, band)
            if tif_path is None:
                continue
            with rasterio.open(tif_path) as src:
                arr = src.read(1).astype("float32")
                nodata = src.nodata
                if nodata is not None:
                    arr = np.where(arr == nodata, np.nan, arr)
                band_arrays.append(arr)
                used_files.append(str(tif_path))
                if meta is None:
                    meta = src.meta.copy()

        if not band_arrays or meta is None:
            continue

        stack = np.stack(band_arrays, axis=0)
        composite = _aggregate(stack, method)
        output_nodata = meta.get("nodata", -9999)
        output_array = np.where(np.isnan(composite), output_nodata, composite).astype("float32")

        meta.update(dtype="float32", count=1, nodata=output_nodata)
        output_name = f"{safe_stem(Path(input_root).name)}_{band}_{method}.tif"
        output_path = output_dir / output_name

        with rasterio.open(output_path, "w", **meta) as dst:
            dst.write(output_array, 1)

        outputs.append(
            {
                "band": band,
                "method": method,
                "input_file_count": len(used_files),
                "input_files": used_files,
                "output_file": str(output_path),
            }
        )

    report = {
        "timestamp_utc": utc_now_iso(),
        "operation": "build_temporal_composites",
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "summary": {
            "date_folder_count": len(folders),
            "bands_detected": bands,
            "method": method,
            "outputs_created": len(outputs),
        },
        "outputs": outputs,
    }

    if report_path:
        write_json(report, report_path)

    return report
