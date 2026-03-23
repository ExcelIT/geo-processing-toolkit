# JSON Report Schema (v1)

Geo Processing Toolkit commands emit machine-readable JSON reports that share a common envelope for automation, auditing, and downstream tooling.

## Standard envelope

All command reports should include:

- `command`: command identifier (for example, `clip-raster`)
- `status`: `PASS`, `PASS_WITH_WARNINGS`, or `FAIL`
- `summary`: compact command-level metrics
- `files`: per-file records with `path`, `status`, `role`, and `messages`
- `generated_at`: UTC timestamp in ISO format

Commands can add extra fields (for example, `input`, `output`, `findings`, `checks`, or `tolerances`) while keeping this envelope stable.

## Canonical example

```json
{
  "command": "validate-raster-stack",
  "status": "PASS_WITH_WARNINGS",
  "summary": {
    "errors": 0,
    "warnings": 1,
    "infos": 5
  },
  "files": [
    {
      "path": "data/2025_01_01.tif",
      "status": "pass",
      "role": "input_raster",
      "messages": []
    },
    {
      "path": "data/2025_01_11.tif",
      "status": "warning",
      "role": "input_raster",
      "messages": [
        {
          "level": "warning",
          "code": "NODATA_MISSING",
          "message": "Raster is missing nodata metadata."
        }
      ]
    }
  ],
  "generated_at": "2026-03-23T13:30:00+00:00",
  "checks": {
    "readable": "pass",
    "crs": "pass",
    "bounds": "pass",
    "resolution": "pass",
    "transform": "pass",
    "dimensions": "pass",
    "band_count": "pass",
    "dtype": "pass",
    "nodata": "warning",
    "driver": "pass"
  }
}
```

## Notes

- `files[].status` is lowercase (`pass`, `warning`, `error`) for per-file consistency.
- Top-level `status` is uppercase (`PASS`, `PASS_WITH_WARNINGS`, `FAIL`) for workflow-level decisions.
- Message objects should use stable `code` values to keep integrations robust.
