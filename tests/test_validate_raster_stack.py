import json
import math

import numpy as np
import rasterio
from click.testing import CliRunner
from rasterio.transform import from_origin

from geo_processing_toolkit.cli import cli
from geo_processing_toolkit.validate_raster_stack import validate_raster_stack


def _make_raster(
    path,
    *,
    crs="EPSG:32619",
    width=10,
    height=10,
    res=10.0,
    count=1,
    dtype="uint16",
    nodata=0,
    driver="GTiff",
):
    data = np.ones((height, width), dtype=dtype)
    transform = from_origin(0.0, float(height * res), float(res), float(res))
    with rasterio.open(
        path,
        "w",
        driver=driver,
        height=height,
        width=width,
        count=count,
        dtype=dtype,
        crs=crs,
        transform=transform,
        nodata=nodata,
    ) as dst:
        for idx in range(1, count + 1):
            dst.write(data, idx)


def test_validate_raster_stack_passes_for_aligned_rasters(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    _make_raster(a)
    _make_raster(b)

    report = validate_raster_stack([str(a), str(b)])

    assert report["status"] == "PASS"
    assert report["summary"]["errors"] == 0
    assert report["summary"]["warnings"] == 0


def test_validate_raster_stack_fails_on_crs_mismatch(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    _make_raster(a, crs="EPSG:32619")
    _make_raster(b, crs="EPSG:4326")

    report = validate_raster_stack([str(a), str(b)])
    messages = [m for f in report["files"] for m in f["messages"]]

    assert report["status"] == "FAIL"
    assert any(m["code"] == "CRS_MISMATCH" for m in messages)


def test_validate_raster_stack_fails_on_resolution_mismatch(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    _make_raster(a, res=10.0)
    _make_raster(b, res=20.0)

    report = validate_raster_stack([str(a), str(b)])
    messages = [m for f in report["files"] for m in f["messages"]]

    assert report["status"] == "FAIL"
    assert any(m["code"] == "RESOLUTION_MISMATCH" for m in messages)


def test_validate_raster_stack_warns_on_missing_nodata(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    _make_raster(a, nodata=0)
    _make_raster(b, nodata=None)

    report = validate_raster_stack([str(a), str(b)])
    messages = [m for f in report["files"] for m in f["messages"]]

    assert report["status"] == "PASS_WITH_WARNINGS"
    assert any(m["code"] == "NODATA_MISSING" for m in messages)


def test_validate_raster_stack_passes_when_nodata_matches(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    c = tmp_path / "c.tif"
    _make_raster(a, nodata=0)
    _make_raster(b, nodata=0)
    _make_raster(c, nodata=0)

    report = validate_raster_stack([str(a), str(b), str(c)])

    assert report["checks"]["nodata"] == "pass"
    assert report["nodata_summary"]["checked"] is True
    assert report["nodata_summary"]["missing_count"] == 0
    assert report["nodata_summary"]["mismatch_count"] == 0
    assert report["nodata_summary"]["all_missing"] is False


def test_validate_raster_stack_warns_when_nodata_missing(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    c = tmp_path / "c.tif"
    _make_raster(a, nodata=0)
    _make_raster(b, nodata=None)
    _make_raster(c, nodata=0)

    report = validate_raster_stack([str(a), str(b), str(c)])
    messages = [m for f in report["files"] for m in f["messages"]]

    assert report["checks"]["nodata"] == "warning"
    assert report["nodata_summary"]["missing_count"] == 1
    assert report["nodata_summary"]["mismatch_count"] == 0
    assert any(m["code"] == "NODATA_MISSING" for m in messages)


def test_validate_raster_stack_warns_when_nodata_differs(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    c = tmp_path / "c.tif"
    _make_raster(a, nodata=0, dtype="int16")
    _make_raster(b, nodata=-9999, dtype="int16")
    _make_raster(c, nodata=0, dtype="int16")

    report = validate_raster_stack([str(a), str(b), str(c)])
    messages = [m for f in report["files"] for m in f["messages"]]

    assert report["checks"]["nodata"] == "warning"
    assert report["nodata_summary"]["missing_count"] == 0
    assert report["nodata_summary"]["mismatch_count"] == 1
    assert any(m["code"] == "NODATA_MISMATCH" for m in messages)


def test_validate_raster_stack_warns_when_all_nodata_missing(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    _make_raster(a, nodata=None)
    _make_raster(b, nodata=None)

    report = validate_raster_stack([str(a), str(b)])
    messages = [m for f in report["files"] for m in f["messages"]]

    assert report["status"] == "PASS_WITH_WARNINGS"
    assert report["checks"]["nodata"] == "warning"
    assert report["nodata_summary"]["all_missing"] is True
    assert report["nodata_summary"]["missing_count"] == 2
    assert any(m["code"] == "NODATA_MISSING" for m in messages)


def test_validate_raster_stack_reports_nodata_summary(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    _make_raster(a, nodata=0)
    _make_raster(b, nodata=None)

    report = validate_raster_stack([str(a), str(b)])

    assert "nodata_summary" in report
    assert report["nodata_summary"]["checked"] is True
    assert report["nodata_summary"]["reference_value"] == 0.0
    assert report["nodata_summary"]["missing_count"] == 1


def test_validate_raster_stack_skips_nodata_check_when_disabled(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    _make_raster(a, nodata=0)
    _make_raster(b, nodata=None)

    report = validate_raster_stack([str(a), str(b)], check_nodata=False)
    messages = [m for f in report["files"] for m in f["messages"]]

    assert report["checks"]["nodata"] == "pass"
    assert report["status"] == "PASS"
    assert report["nodata_summary"] == {"checked": False}
    assert not any(m["code"] in {"NODATA_MISSING", "NODATA_MISMATCH"} for m in messages)


def test_validate_raster_stack_handles_nan_nodata_consistently(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    _make_raster(a, dtype="float32", nodata=math.nan)
    _make_raster(b, dtype="float32", nodata=math.nan)

    report = validate_raster_stack([str(a), str(b)])
    messages = [m for f in report["files"] for m in f["messages"]]

    assert report["checks"]["nodata"] == "pass"
    assert report["nodata_summary"]["reference_value"] == "NaN"
    assert "NaN" in report["nodata_summary"]["unique_values"]
    assert not any(m["code"] == "NODATA_MISMATCH" for m in messages)


def test_validate_raster_stack_warns_on_dtype_mismatch(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    _make_raster(a, dtype="uint16")
    _make_raster(b, dtype="float32")

    report = validate_raster_stack([str(a), str(b)])
    messages = [m for f in report["files"] for m in f["messages"]]

    assert report["status"] == "PASS_WITH_WARNINGS"
    assert any(m["code"] == "DTYPE_MISMATCH" for m in messages)


def test_validate_raster_stack_writes_json_report(tmp_path):
    a = tmp_path / "a.tif"
    b = tmp_path / "b.tif"
    output_json = tmp_path / "report.json"
    _make_raster(a)
    _make_raster(b)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "validate-raster-stack",
            str(a),
            str(b),
            "--json-out",
            str(output_json),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["command"] == "validate-raster-stack"
    assert payload["status"] == "PASS"


def test_validate_raster_stack_supports_directory_input(tmp_path):
    folder = tmp_path / "rasters"
    folder.mkdir()
    _make_raster(folder / "a.tif")
    _make_raster(folder / "b.tif")

    report = validate_raster_stack([str(folder)], pattern="*.tif", recursive=False)

    assert report["status"] == "PASS"
    assert len(report["resolved_inputs"]) == 2


def test_validate_raster_stack_returns_no_rasters_found_error(tmp_path):
    report = validate_raster_stack([str(tmp_path)], pattern="*.tif", recursive=False)
    messages = [m for f in report["files"] for m in f["messages"]]

    assert report["status"] == "FAIL"
    assert any(m["code"] == "NO_RASTERS_FOUND" for m in messages)
