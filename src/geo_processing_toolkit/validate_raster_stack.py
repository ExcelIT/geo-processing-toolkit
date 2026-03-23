from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any

import rasterio
from rasterio.errors import RasterioIOError

from .utils import utc_now_iso

PASS = "pass"
WARNING = "warning"
ERROR = "error"


def _resolve_input_paths(paths: list[str], pattern: str, recursive: bool) -> tuple[list[str], list[dict[str, Any]], list[str]]:
    resolved: list[str] = []
    messages: list[dict[str, Any]] = []
    infos: list[str] = []

    for raw in paths:
        path = Path(raw)
        if not path.exists():
            messages.append(
                {
                    "path": str(path),
                    "level": ERROR,
                    "code": "INVALID_INPUT_PATH",
                    "message": "Input path does not exist.",
                }
            )
            continue

        if path.is_dir():
            iterator = path.rglob(pattern) if recursive else path.glob(pattern)
            discovered = sorted([p for p in iterator if p.is_file()], key=lambda p: str(p))
            infos.append(f"Discovered {len(discovered)} files in directory {path}.")
            resolved.extend(str(p) for p in discovered)
        elif path.is_file():
            resolved.append(str(path))
        else:
            messages.append(
                {
                    "path": str(path),
                    "level": ERROR,
                    "code": "INVALID_INPUT_PATH",
                    "message": "Input path is neither a file nor a directory.",
                }
            )

    return resolved, messages, infos


def _compare_float_lists(left: list[float], right: list[float], tolerance: float) -> bool:
    if len(left) != len(right):
        return False
    return all(abs(a - b) <= tolerance for a, b in zip(left, right))


def _normalize_nodata_value(value: Any) -> Any:
    if value is None:
        return None
    try:
        if isinstance(value, float) and math.isnan(value):
            return "NaN"
    except TypeError:
        pass
    return value


def _nodata_equal(left: Any, right: Any) -> bool:
    left_value = _normalize_nodata_value(left)
    right_value = _normalize_nodata_value(right)
    return left_value == right_value


def _default_nodata_summary(checked: bool) -> dict[str, Any]:
    if not checked:
        return {"checked": False}
    return {
        "checked": True,
        "reference_value": None,
        "unique_values": [],
        "missing_count": 0,
        "mismatch_count": 0,
        "all_missing": False,
    }


def _evaluate_nodata_consistency(
    opened: list[dict[str, Any]],
    reference_metadata: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    reference_value = _normalize_nodata_value(reference_metadata.get("nodata"))
    unique_values: list[Any] = []
    seen_values: set[Any] = set()
    missing_count = 0
    mismatch_count = 0
    all_missing = True

    for item in opened:
        metadata = item["metadata"]
        record = item["record"]
        messages = record["messages"]
        nodata_value = _normalize_nodata_value(metadata.get("nodata"))

        if nodata_value not in seen_values:
            seen_values.add(nodata_value)
            unique_values.append(nodata_value)

        if nodata_value is None:
            missing_count += 1
            messages.append(
                {
                    "level": WARNING,
                    "code": "NODATA_MISSING",
                    "message": "Raster is missing nodata metadata.",
                }
            )
            continue

        all_missing = False
        if not _nodata_equal(nodata_value, reference_value):
            mismatch_count += 1
            messages.append(
                {
                    "level": WARNING,
                    "code": "NODATA_MISMATCH",
                    "message": (
                        "Raster nodata value differs from reference "
                        f"({nodata_value} vs {reference_value})."
                    ),
                }
            )

    nodata_status = WARNING if (missing_count > 0 or mismatch_count > 0 or all_missing) else PASS
    summary = {
        "checked": True,
        "reference_value": reference_value,
        "unique_values": unique_values,
        "missing_count": missing_count,
        "mismatch_count": mismatch_count,
        "all_missing": all_missing,
    }
    return nodata_status, summary


def _extract_raster_metadata(path: str) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
    try:
        with rasterio.open(path) as src:
            transform = [float(v) for v in src.transform]
            bounds = [float(src.bounds.left), float(src.bounds.bottom), float(src.bounds.right), float(src.bounds.top)]
            resolution = [float(src.res[0]), float(src.res[1])]

            metadata = {
                "path": str(path),
                "crs": str(src.crs) if src.crs else None,
                "bounds": bounds,
                "resolution": resolution,
                "transform": transform,
                "width": int(src.width),
                "height": int(src.height),
                "count": int(src.count),
                "dtype": str(src.dtypes[0]) if src.count > 0 else None,
                "nodata": src.nodata,
                "driver": src.driver,
            }
            return metadata, None
    except RasterioIOError as exc:
        message = str(exc)
        code = "NOT_A_RASTER" if "supported file format" in message.lower() else "FILE_OPEN_ERROR"
        return None, {"code": code, "message": message}
    except Exception as exc:
        return None, {"code": "FILE_OPEN_ERROR", "message": str(exc)}


def _empty_file_report(path: str, level: str, code: str, message: str) -> dict[str, Any]:
    return {
        "path": path,
        "status": level,
        "metadata": {
            "crs": None,
            "bounds": None,
            "resolution": None,
            "transform": None,
            "width": None,
            "height": None,
            "count": None,
            "dtype": None,
            "nodata": None,
            "driver": None,
        },
        "messages": [{"level": level, "code": code, "message": message}],
    }


def _worst_status(levels: list[str]) -> str:
    if ERROR in levels:
        return ERROR
    if WARNING in levels:
        return WARNING
    return PASS


def validate_raster_stack(
    paths: list[str],
    pattern: str = "*.tif",
    recursive: bool = False,
    reference: str = "first",
    reference_file: str | None = None,
    check_nodata: bool = True,
    check_dtype: bool = True,
    check_driver: bool = True,
    tolerance_resolution: float = 0.0,
    tolerance_bounds: float = 0.0,
    tolerance_transform: float = 0.0,
) -> dict[str, Any]:
    start = time.perf_counter()
    nodata_summary = _default_nodata_summary(check_nodata)

    checks: dict[str, str] = {
        "readable": PASS,
        "crs": PASS,
        "bounds": PASS,
        "resolution": PASS,
        "transform": PASS,
        "dimensions": PASS,
        "band_count": PASS,
        "dtype": PASS,
        "nodata": PASS,
        "driver": PASS,
    }

    resolved_inputs, top_level_messages, info_notes = _resolve_input_paths(paths, pattern=pattern, recursive=recursive)

    duplicates: set[str] = set()
    seen: set[str] = set()
    deduped_inputs: list[str] = []
    for input_path in resolved_inputs:
        if input_path in seen:
            duplicates.add(input_path)
            continue
        seen.add(input_path)
        deduped_inputs.append(input_path)

    files: list[dict[str, Any]] = []
    global_messages: list[dict[str, str]] = []

    for message in top_level_messages:
        files.append(_empty_file_report(message["path"], message["level"], message["code"], message["message"]))
        if message["level"] == ERROR:
            checks["readable"] = ERROR

    for duplicate in sorted(duplicates):
        files.append(
            _empty_file_report(
                duplicate,
                WARNING,
                "DUPLICATE_INPUT",
                "Input path appears more than once and will be validated only once.",
            )
        )

    opened: list[dict[str, Any]] = []
    for input_path in deduped_inputs:
        metadata, open_error = _extract_raster_metadata(input_path)
        if open_error:
            files.append(_empty_file_report(input_path, ERROR, open_error["code"], open_error["message"]))
            checks["readable"] = ERROR
            continue

        file_record = {
            "path": input_path,
            "status": PASS,
            "metadata": {
                "crs": metadata["crs"],
                "bounds": metadata["bounds"],
                "resolution": metadata["resolution"],
                "transform": metadata["transform"],
                "width": metadata["width"],
                "height": metadata["height"],
                "count": metadata["count"],
                "dtype": metadata["dtype"],
                "nodata": metadata["nodata"],
                "driver": metadata["driver"],
            },
            "messages": [],
        }
        files.append(file_record)
        opened.append({"metadata": metadata, "record": file_record})

    if not opened:
        files.append(_empty_file_report("", ERROR, "NO_RASTERS_FOUND", "No raster files were found to validate."))
        checks["readable"] = ERROR
        infos = len(info_notes) + 1
        errors = sum(len([m for m in f["messages"] if m["level"] == ERROR]) for f in files)
        warnings = sum(len([m for m in f["messages"] if m["level"] == WARNING]) for f in files)
        status = "FAIL"
        return {
            "command": "validate-raster-stack",
            "status": status,
            "fail_on": "error",
            "reference_strategy": reference,
            "reference_raster": None,
            "input_count": len(deduped_inputs),
            "resolved_inputs": deduped_inputs,
            "checks": checks,
            "summary": {"errors": errors, "warnings": warnings, "infos": infos},
            "tolerances": {
                "resolution": float(tolerance_resolution),
                "bounds": float(tolerance_bounds),
                "transform": float(tolerance_transform),
            },
            "reference_metadata": None,
            "nodata_summary": nodata_summary,
            "files": files,
            "generated_at": utc_now_iso(),
            "duration_seconds": round(time.perf_counter() - start, 6),
        }

    reference_metadata: dict[str, Any] | None = None
    reference_raster_path: str | None = None

    if reference == "file":
        if not reference_file:
            files.append(
                _empty_file_report("", ERROR, "REFERENCE_FILE_MISSING", "Reference strategy 'file' requires --reference-file.")
            )
            checks["readable"] = ERROR
        elif not Path(reference_file).exists():
            files.append(
                _empty_file_report(reference_file, ERROR, "REFERENCE_FILE_MISSING", "Reference file does not exist.")
            )
            checks["readable"] = ERROR
        else:
            metadata, open_error = _extract_raster_metadata(reference_file)
            if open_error:
                files.append(_empty_file_report(reference_file, ERROR, open_error["code"], open_error["message"]))
                checks["readable"] = ERROR
            else:
                reference_metadata = metadata
                reference_raster_path = reference_file
    else:
        reference_metadata = opened[0]["metadata"]
        reference_raster_path = opened[0]["metadata"]["path"]

    if reference_metadata is not None:
        for item in opened:
            metadata = item["metadata"]
            record = item["record"]
            messages = record["messages"]

            if metadata["crs"] != reference_metadata["crs"]:
                checks["crs"] = ERROR
                messages.append(
                    {
                        "level": ERROR,
                        "code": "CRS_MISMATCH",
                        "message": f"CRS mismatch ({metadata['crs']} vs {reference_metadata['crs']}).",
                    }
                )

            if metadata["width"] != reference_metadata["width"] or metadata["height"] != reference_metadata["height"]:
                checks["dimensions"] = ERROR
                messages.append(
                    {
                        "level": ERROR,
                        "code": "DIMENSIONS_MISMATCH",
                        "message": (
                            "Raster dimensions differ from reference "
                            f"(({metadata['width']}, {metadata['height']}) vs ({reference_metadata['width']}, {reference_metadata['height']}))."
                        ),
                    }
                )

            if metadata["count"] != reference_metadata["count"]:
                checks["band_count"] = ERROR
                messages.append(
                    {
                        "level": ERROR,
                        "code": "BAND_COUNT_MISMATCH",
                        "message": f"Raster band count differs from reference ({metadata['count']} vs {reference_metadata['count']}).",
                    }
                )

            if not _compare_float_lists(metadata["bounds"], reference_metadata["bounds"], tolerance_bounds):
                checks["bounds"] = ERROR
                messages.append(
                    {
                        "level": ERROR,
                        "code": "BOUNDS_MISMATCH",
                        "message": f"Raster bounds differ from reference ({metadata['bounds']} vs {reference_metadata['bounds']}).",
                    }
                )

            if not _compare_float_lists(metadata["resolution"], reference_metadata["resolution"], tolerance_resolution):
                checks["resolution"] = ERROR
                messages.append(
                    {
                        "level": ERROR,
                        "code": "RESOLUTION_MISMATCH",
                        "message": (
                            "Raster resolution differs from reference "
                            f"({tuple(metadata['resolution'])} vs {tuple(reference_metadata['resolution'])})."
                        ),
                    }
                )

            if not _compare_float_lists(metadata["transform"], reference_metadata["transform"], tolerance_transform):
                checks["transform"] = ERROR
                messages.append(
                    {
                        "level": ERROR,
                        "code": "TRANSFORM_MISMATCH",
                        "message": "Raster affine transform differs from reference.",
                    }
                )

            if check_dtype and metadata["dtype"] != reference_metadata["dtype"]:
                checks["dtype"] = WARNING if checks["dtype"] != ERROR else checks["dtype"]
                messages.append(
                    {
                        "level": WARNING,
                        "code": "DTYPE_MISMATCH",
                        "message": f"Raster dtype differs from reference ({metadata['dtype']} vs {reference_metadata['dtype']}).",
                    }
                )

            if check_driver and metadata["driver"] != reference_metadata["driver"]:
                checks["driver"] = WARNING if checks["driver"] != ERROR else checks["driver"]
                messages.append(
                    {
                        "level": WARNING,
                        "code": "DRIVER_MISMATCH",
                        "message": f"Raster driver differs from reference ({metadata['driver']} vs {reference_metadata['driver']}).",
                    }
                )

            del messages

        stems = [Path(item["metadata"]["path"]).stem for item in opened]
        has_digit = [any(ch.isdigit() for ch in stem) for stem in stems]
        if any(has_digit) and not all(has_digit):
            checks["readable"] = ERROR if checks["readable"] == ERROR else checks["readable"]
            global_messages.append(
                {
                    "level": WARNING,
                    "code": "FILENAME_ORDER_AMBIGUOUS",
                    "message": "Filename/date ordering may be ambiguous across input rasters.",
                }
            )

    for message in global_messages:
        if files:
            files[0]["messages"].append(message)
            if files[0]["status"] == PASS:
                files[0]["status"] = message["level"]

    if check_nodata and reference_metadata is not None:
        nodata_status, nodata_summary = _evaluate_nodata_consistency(opened, reference_metadata)
        checks["nodata"] = nodata_status
    elif not check_nodata:
        checks["nodata"] = PASS

    for item in opened:
        record = item["record"]
        record["status"] = _worst_status([m["level"] for m in record["messages"]])

    error_count = 0
    warning_count = 0
    for file_report in files:
        for message in file_report["messages"]:
            if message["level"] == ERROR:
                error_count += 1
            elif message["level"] == WARNING:
                warning_count += 1

    status = "FAIL" if error_count > 0 else "PASS_WITH_WARNINGS" if warning_count > 0 else "PASS"

    unique_crs = len({m["metadata"]["crs"] for m in opened if m["metadata"]["crs"] is not None})
    unique_resolution = len({tuple(m["metadata"]["resolution"]) for m in opened if m["metadata"]["resolution"] is not None})
    unique_dtype = len({m["metadata"]["dtype"] for m in opened if m["metadata"]["dtype"] is not None})
    info_count = 5 + len(info_notes)

    report = {
        "command": "validate-raster-stack",
        "status": status,
        "fail_on": "error",
        "reference_strategy": reference,
        "reference_raster": reference_raster_path,
        "input_count": len(deduped_inputs),
        "resolved_inputs": deduped_inputs,
        "checks": checks,
        "summary": {
            "errors": error_count,
            "warnings": warning_count,
            "infos": info_count,
        },
        "tolerances": {
            "resolution": float(tolerance_resolution),
            "bounds": float(tolerance_bounds),
            "transform": float(tolerance_transform),
        },
        "reference_metadata": (
            {
                "path": reference_metadata["path"],
                "crs": reference_metadata["crs"],
                "bounds": reference_metadata["bounds"],
                "resolution": reference_metadata["resolution"],
                "transform": reference_metadata["transform"],
                "width": reference_metadata["width"],
                "height": reference_metadata["height"],
                "count": reference_metadata["count"],
                "dtype": reference_metadata["dtype"],
                "nodata": _normalize_nodata_value(reference_metadata["nodata"]),
                "driver": reference_metadata["driver"],
            }
            if reference_metadata is not None
            else None
        ),
        "nodata_summary": nodata_summary,
        "files": files,
        "generated_at": utc_now_iso(),
        "duration_seconds": round(time.perf_counter() - start, 6),
    }

    report["info"] = {
        "files_discovered": len(deduped_inputs),
        "selected_reference_raster": reference_raster_path,
        "unique_crs_count": unique_crs,
        "unique_resolution_count": unique_resolution,
        "unique_dtype_count": unique_dtype,
        "scan_notes": info_notes,
        "applied_tolerances": {
            "resolution": float(tolerance_resolution),
            "bounds": float(tolerance_bounds),
            "transform": float(tolerance_transform),
        },
    }

    return report
