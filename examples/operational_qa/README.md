# Operational Geospatial QA Examples

This directory contains lightweight workflow examples that show how Geo Processing Toolkit can be used in real QA-oriented geospatial workflows.

These examples are intentionally documentation-first:

- no large datasets
- no domain-locked assumptions
- no heavy notebooks
- no hidden infrastructure requirements

The goal is to show how validation, repair, reporting, and pre-flight checks fit together before data enters production GIS, remote-sensing, climate-risk, or disaster-response workflows.

## Included workflows

### 1. Validate and repair an incoming vector delivery
See:
- `validate-and-repair-vector-delivery.md`

Focus:
- inspect incoming vector data
- identify validation issues
- repair invalid geometries
- re-check the output
- preserve a QA trail

### 2. Validate raster stack readiness before compositing
See:
- `validate-raster-stack-before-composite.md`

Focus:
- verify that rasters can safely be used together
- detect CRS, resolution, bounds, transform, band, dtype, or nodata problems
- generate a machine-readable validation report before processing

### 3. Review a JSON QA report
See:
- `review-json-qa-report.md`

Focus:
- inspect report status
- identify blocking errors vs warnings
- understand how JSON outputs can support QA review, audit, and automation

## Why these examples exist

Geo Processing Toolkit is not trying to replace core geospatial libraries.

It focuses on the workflow layer that often remains inconsistent in practice:

- validation
- repair
- standardization
- reporting
- operational readiness

These examples show how the toolkit fits into that layer.
