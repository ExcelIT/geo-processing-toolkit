# Example: Validate Raster Stack Readiness Before Temporal Compositing

## Scenario

A team wants to build a temporal composite from multiple rasters. Before running the composite workflow, the input rasters should be checked for compatibility.

This example shows how to use `validate-raster-stack` as a pre-flight QA step.

## Goals

- verify raster compatibility before compositing
- detect blocking differences early
- separate errors from warnings
- produce a machine-readable validation report

## Example input

Assume a directory such as:

```text
data/rasters/
```

containing multiple GeoTIFF files intended for stack-based processing.

## Step 1: Run raster stack validation

Example command:

```bash
gptk validate-raster-stack ./data/rasters --pattern "*.tif" --recursive --json-out reports/raster_stack_validation.json
```

## What the command checks

The validator is designed to inspect whether the rasters can safely be used together.

Typical checks include:

- readable/openable status
- CRS consistency
- bounds consistency
- resolution consistency
- affine transform consistency
- dimensions
- band count
- dtype differences
- nodata metadata
- driver/format differences

## Step 2: Review the result

Review:

- console output for fast triage
- `reports/raster_stack_validation.json` for a machine-readable QA record

Interpret the result as:

- `PASS` = no warnings or errors
- `PASS_WITH_WARNINGS` = usable, but review warnings
- `FAIL` = blocking compatibility issues were detected

## Example warning cases

Warnings may include:

- missing nodata metadata
- dtype mismatch
- driver mismatch

These do not always block processing, but they should be reviewed.

## Example blocking cases

Errors may include:

- CRS mismatch
- resolution mismatch
- transform mismatch
- dimensions mismatch
- band count mismatch

These should usually be addressed before compositing.

## Step 3: Decide whether to proceed

Use the report to decide whether to:

- proceed with compositing
- isolate bad inputs
- repair or normalize the raster set
- reject the stack until upstream issues are fixed

## Why this matters

Temporal and stack-based raster workflows can fail silently or produce misleading output when rasters are not aligned properly. A pre-flight validation step makes those risks visible before processing begins.

## Notes

- This command is a validation step, not an auto-fix workflow.
- Tolerances should be used carefully and documented when applied.
- Keep the validation report as part of the project QA trail.
