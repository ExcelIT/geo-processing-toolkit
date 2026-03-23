# Roadmap

## Positioning

Geo Processing Toolkit is being developed as a focused open-source toolkit for geospatial QA, validation, repair, and standardization.

The project is aimed at workflows where data quality, consistency, and repeatability matter before data is used in production GIS, remote-sensing, climate-risk, or disaster-response contexts.

## Near-term priorities

### 1. Validation first
Strengthen pre-flight checks so workflows fail early and clearly when datasets are incompatible.

Planned work:
- raster stack alignment checks
- CRS, extent, resolution, and transform validation
- nodata consistency checks
- clearer error messaging
- structured JSON validation reports

### 2. Modern format support
Expand compatibility with modern geospatial formats used in reproducible and cloud-native workflows.

Planned work:
- GeoParquet read and validation support
- Cloud Optimized GeoTIFF (COG) support guidance
- format-specific caveat reporting
- comparison notes for shapefile, GeoPackage, and GeoParquet behavior

### 3. Standards readiness
Make the toolkit more useful for interoperable pipeline design and operational data exchange.

Planned work:
- STAC-oriented validation helpers
- richer metadata checks
- machine-readable report schemas
- better documentation around format assumptions

### 4. Reproducible examples
Improve adoption by making supported workflows easier to understand and test.

Planned work:
- raster clipping example
- geometry repair example
- temporal composite example
- expected output and logging examples
- lightweight sample workflow documentation

## Medium-term priorities

### 5. Reporting and auditability
Improve traceability for professional and operational use cases.

Planned work:
- expanded JSON report schema
- document and stabilize a shared JSON report schema across commands
- run summaries
- validation status categories
- warnings vs blocking failures
- output summaries for automated workflows

### 6. Packaging and distribution
Make the project easier to adopt and maintain.

Planned work:
- PyPI publication
- docs improvements
- versioned examples
- release discipline
- compatibility notes by environment

## Future directions

These are candidate future directions, not immediate commitments:

- optional harmonization helpers for raster stacks
- optional reprojection and normalization workflows
- batch validation pipelines for folders and datasets
- profile-based validation for specific delivery types
- domain packs for crisis mapping, environmental monitoring, and planning workflows

## Contribution direction

The best contributions in the current phase are:

- tests for edge cases
- format support improvements
- validation/reporting improvements
- clearer examples
- documentation updates
- bug fixes with reproducible inputs

## What the project will stay focused on

The project will stay narrow on purpose.

It will continue focusing on:
- validation
- repair
- standardization
- reporting
- workflow readiness

It will not try to become a general-purpose GIS platform.
