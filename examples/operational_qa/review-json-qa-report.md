# Example: Review a JSON QA Report

## Scenario

A command has produced a machine-readable JSON report. That report should be usable for:

- QA review
- delivery evidence
- audit trail storage
- automation and CI/CD decisions

This example explains how to review the report structure and what to focus on.

## Example report file

```text
reports/raster_stack_validation.json
```

## Key fields to review

### command

Shows which workflow produced the report.

### status

Overall outcome of the command.

Allowed values:

- `PASS`
- `PASS_WITH_WARNINGS`
- `FAIL`

### summary

Shows counts of:

- errors
- warnings
- infos

This is usually the fastest way to understand whether deeper review is required.

### files

Contains per-file results, including:

- file path
- file-level status
- metadata
- messages

### messages

Look for:

- message level
- stable message code
- human-readable explanation

Examples:

- `CRS_MISMATCH`
- `NODATA_MISSING`
- `DTYPE_MISMATCH`
- `FILE_OPEN_ERROR`

## Review approach

### When status is PASS

- no blocking problems found
- no warnings found
- workflow is in a clean state

### When status is PASS_WITH_WARNINGS

- review warnings before downstream use
- determine whether the warnings are acceptable for the use case
- document the decision where needed

### When status is FAIL

- do not continue blindly
- inspect which files failed
- identify whether the cause is data quality, metadata, or workflow compatibility
- correct the problem before re-running

## Why JSON reporting matters

Machine-readable reports make it easier to:

- keep evidence of QA checks
- standardize workflow review
- build future automation
- support repeatable delivery processes
- separate subjective review from objective checks

## Recommended practice

For any important workflow:

- keep the JSON report
- keep the command used to generate it
- keep the original input files unchanged
- re-run validation after repairs or normalization
