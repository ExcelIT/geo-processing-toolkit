# Report Schema

## Purpose

Geo Processing Toolkit uses machine-readable JSON reports so validation and preprocessing results can be:

- inspected by humans
- consumed by automation
- stored for audit trails
- compared across runs
- reused by downstream tools

This document defines the common JSON report structure used across commands.

## Design goals

The report schema is designed to be:

- consistent across commands
- easy to parse
- explicit about failures and warnings
- useful in CI/CD and batch workflows
- stable enough for downstream integration

## Core envelope

All report-producing commands should use the same top-level envelope.

```json
{
  "command": "validate-raster-stack",
  "status": "PASS",
  "summary": {
    "errors": 0,
    "warnings": 0,
    "infos": 3
  },
  "files": [],
  "generated_at": "2026-03-23T13:30:00Z"
}
```

## Top-level fields

### command

String.

The command or logical workflow that produced the report.

Examples:

- `validate-raster-stack`
- `validate-vector`
- `clip-raster`
- `search-folder`

### status

String.

Allowed values:

- `PASS`
- `PASS_WITH_WARNINGS`
- `FAIL`

### summary

Object.

Counts of message levels detected during execution.

Required fields:

```json
{
  "errors": 0,
  "warnings": 0,
  "infos": 0
}
```

### files

Array.

Per-file or per-input results. This may be empty for commands that do not operate on file sets, but should be present.

### generated_at

String.

UTC timestamp in ISO 8601 format.

Example:

`2026-03-23T13:30:00Z`

## Recommended top-level fields

Commands may include additional top-level fields when needed.

Recommended fields include:

### fail_on

String.

Used when a command supports configurable exit/failure policy.

Examples:

- `error`
- `warning`
- `never`

### input_count

Integer.

Number of resolved inputs processed.

### resolved_inputs

Array of strings.

Normalized list of files actually processed.

### checks

Object.

Named validation checks and their aggregate result.

Example:

```json
{
  "readable": "pass",
  "crs": "pass",
  "bounds": "pass",
  "resolution": "warning",
  "nodata": "warning"
}
```

Recommended values:

- `pass`
- `warning`
- `fail`

### tolerances

Object.

Numeric tolerances used during comparisons.

Example:

```json
{
  "resolution": 0.0,
  "bounds": 0.0,
  "transform": 0.0
}
```

### reference_strategy

String.

How a comparison reference was chosen.

Examples:

- `first`
- `file`

### reference_raster

String.

Reference file path used in stack validation workflows.

### reference_metadata

Object.

Metadata for the selected reference input.

### duration_seconds

Number.

Elapsed runtime for the command.

### info

Object.

Optional structured metadata that does not belong in the main result body but is still useful for automation or debugging.

## Per-file entry structure

Each entry in `files` should use a consistent shape.

Minimum structure:

```json
{
  "path": "path/to/file.tif",
  "status": "pass",
  "messages": []
}
```

Recommended extended structure:

```json
{
  "path": "path/to/file.tif",
  "status": "warning",
  "metadata": {},
  "messages": []
}
```

### path

String.

Path to the file or logical input being reported.

### status

String.

Allowed values:

- `pass`
- `warning`
- `fail`
- `error`

Use:

- `pass` when no file-level problems were found
- `warning` when non-blocking issues exist
- `fail` when blocking validation issues exist
- `error` when the file could not be processed correctly at all

### metadata

Object.

Optional per-file metadata extracted during processing.

This is especially useful for validation commands.

### messages

Array of message objects.

Each message should use the same structure.

## Message object structure

Use this structure everywhere:

```json
{
  "level": "warning",
  "code": "NODATA_MISSING",
  "message": "Raster is missing nodata metadata."
}
```

### level

Allowed values:

- `info`
- `warning`
- `error`

### code

Stable machine-readable code.

Examples:

- `CRS_MISMATCH`
- `NODATA_MISSING`
- `DTYPE_MISMATCH`
- `FILE_OPEN_ERROR`

### message

Human-readable explanation.

## Report status rules

Use these rules consistently:

### PASS

No errors and no warnings.

### PASS_WITH_WARNINGS

No errors, but one or more warnings.

### FAIL

One or more errors were detected.

## Example: validate-raster-stack

```json
{
  "command": "validate-raster-stack",
  "status": "PASS_WITH_WARNINGS",
  "fail_on": "error",
  "reference_strategy": "first",
  "reference_raster": "data/2025_01_01.tif",
  "input_count": 3,
  "resolved_inputs": [
    "data/2025_01_01.tif",
    "data/2025_02_01.tif",
    "data/2025_03_01.tif"
  ],
  "checks": {
    "readable": "pass",
    "crs": "pass",
    "bounds": "pass",
    "resolution": "pass",
    "transform": "pass",
    "dimensions": "pass",
    "band_count": "pass",
    "dtype": "warning",
    "nodata": "warning",
    "driver": "pass"
  },
  "summary": {
    "errors": 0,
    "warnings": 2,
    "infos": 4
  },
  "tolerances": {
    "resolution": 0.0,
    "bounds": 0.0,
    "transform": 0.0
  },
  "reference_metadata": {
    "path": "data/2025_01_01.tif",
    "crs": "EPSG:32619",
    "bounds": [0.0, 0.0, 100.0, 100.0],
    "resolution": [10.0, 10.0],
    "transform": [10.0, 0.0, 0.0, 0.0, -10.0, 100.0, 0.0, 0.0, 1.0],
    "width": 10,
    "height": 10,
    "count": 1,
    "dtype": "uint16",
    "nodata": 0,
    "driver": "GTiff"
  },
  "files": [
    {
      "path": "data/2025_01_01.tif",
      "status": "pass",
      "metadata": {
        "crs": "EPSG:32619",
        "bounds": [0.0, 0.0, 100.0, 100.0],
        "resolution": [10.0, 10.0],
        "transform": [10.0, 0.0, 0.0, 0.0, -10.0, 100.0, 0.0, 0.0, 1.0],
        "width": 10,
        "height": 10,
        "count": 1,
        "dtype": "uint16",
        "nodata": 0,
        "driver": "GTiff"
      },
      "messages": []
    },
    {
      "path": "data/2025_02_01.tif",
      "status": "warning",
      "metadata": {
        "crs": "EPSG:32619",
        "bounds": [0.0, 0.0, 100.0, 100.0],
        "resolution": [10.0, 10.0],
        "transform": [10.0, 0.0, 0.0, 0.0, -10.0, 100.0, 0.0, 0.0, 1.0],
        "width": 10,
        "height": 10,
        "count": 1,
        "dtype": "float32",
        "nodata": null,
        "driver": "GTiff"
      },
      "messages": [
        {
          "level": "warning",
          "code": "NODATA_MISSING",
          "message": "Raster is missing nodata metadata."
        },
        {
          "level": "warning",
          "code": "DTYPE_MISMATCH",
          "message": "Raster dtype differs from reference (float32 vs uint16)."
        }
      ]
    }
  ],
  "generated_at": "2026-03-23T13:30:00Z",
  "duration_seconds": 0.42
}
```

## Example: validate-vector

```json
{
  "command": "validate-vector",
  "status": "PASS_WITH_WARNINGS",
  "summary": {
    "errors": 0,
    "warnings": 1,
    "infos": 2
  },
  "files": [
    {
      "path": "data/input.gpkg",
      "status": "warning",
      "metadata": {
        "driver": "GPKG",
        "feature_count": 128,
        "geometry_types": ["Polygon", "MultiPolygon"]
      },
      "messages": [
        {
          "level": "warning",
          "code": "INVALID_GEOMETRIES_FOUND",
          "message": "Some geometries are invalid and may require repair."
        }
      ]
    }
  ],
  "generated_at": "2026-03-23T13:35:00Z"
}
```

## Field guidance by command type

### Validation commands

Should generally include:

- `checks`
- `summary`
- `files`
- `messages`
- extracted input metadata

### Processing commands

Should generally include:

- input summary
- output summary
- warnings/errors
- generated outputs
- timing metadata where useful

### Discovery/search commands

Should generally include:

- resolved paths
- counts
- filtering rules used
- result list

## Message code rules

Message codes should be:

- uppercase
- underscore-separated
- stable over time
- specific enough for automation

Good examples:

- `CRS_MISMATCH`
- `NODATA_MISSING`
- `DIMENSIONS_MISMATCH`
- `FILE_OPEN_ERROR`

Bad examples:

- `bad_file`
- `something_wrong`
- `warning1`

## Backward compatibility

Do not silently break report structure once users may depend on it.

When making meaningful schema changes:

- document the change
- keep legacy fields where practical
- prefer additive changes over destructive ones
- note the change in `CHANGELOG.md`

## Implementation guidance

When adding or updating commands:

- start with the common report envelope
- add command-specific fields only where needed
- use stable message codes
- keep summary counts accurate
- make JSON output deterministic enough for tests
- document new fields when they are introduced

## Recommended next step

The project should gradually move all report-producing commands onto this schema so users get a consistent automation surface across validation and preprocessing workflows.
