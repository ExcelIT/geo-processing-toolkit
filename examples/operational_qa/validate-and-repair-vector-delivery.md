# Example: Validate and Repair an Incoming Vector Delivery

## Scenario

A project team receives a new vector delivery from an external source. Before using it in analysis, publishing it to a dashboard, or handing it to another workflow, the data should be checked for validity and repaired where appropriate.

This example shows a lightweight QA sequence for an incoming vector file.

## Goals

- validate the input
- identify geometry or structure problems
- repair invalid geometries where possible
- preserve a machine-readable QA trail
- confirm that the repaired output is ready for downstream use

## Example input

Assume an incoming file such as:

```text
data/incoming_delivery.gpkg
```

## Step 1: Validate the incoming file

Run the vector validation workflow first.

Example command:

```bash
gptk validate-vector data/incoming_delivery.gpkg --json-out reports/incoming_delivery_validation.json
```

## What to look for

Typical findings may include:

- invalid geometries
- mixed geometry types
- missing or unexpected CRS information
- feature-level issues that should be reviewed before use

## Step 2: Review the validation result

Review:

- console output
- the JSON report at `reports/incoming_delivery_validation.json`

This gives you a QA record of the condition of the delivery before any repair is attempted.

## Step 3: Repair invalid geometries

If the validation result indicates geometry problems that are safe to repair, run the geometry repair workflow.

Example command:

```bash
gptk repair-geometry data/incoming_delivery.gpkg outputs/incoming_delivery_repaired.gpkg
```

## Step 4: Re-run validation on the repaired output

Always validate the repaired file again.

Example command:

```bash
gptk validate-vector outputs/incoming_delivery_repaired.gpkg --json-out reports/incoming_delivery_repaired_validation.json
```

## Expected QA outcome

At the end of this flow, you should have:

- the original incoming file
- a repaired output file where appropriate
- an initial validation report
- a post-repair validation report
- a documented decision trail for QA review

## Why this matters

Vector deliveries often arrive with issues that are small enough to be ignored temporarily but large enough to cause downstream failures, geometry errors, dashboard problems, or inconsistent results later.

This workflow makes that risk visible earlier.

## Notes

- Repair should not be treated as a substitute for understanding data-quality issues.
- Keep the original source file unchanged.
- Prefer reproducible QA records over undocumented manual edits.
