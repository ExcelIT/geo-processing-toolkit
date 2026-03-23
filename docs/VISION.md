# Vision

## What this project is trying to become

Geo Processing Toolkit is being built as a practical trust layer for geospatial workflows.

The goal is not to replace GeoPandas, Rasterio, GDAL, desktop GIS platforms, or cloud catalogs. The goal is to make geospatial data easier to trust before it enters those systems.

In practice, that means helping teams:

- validate incoming datasets before use
- repair common structural problems
- standardize workflow behavior
- generate machine-readable QA evidence
- detect incompatibilities before they become downstream failures

## Why this matters

A lot of geospatial work still breaks in the same boring places:

- inconsistent CRS information
- geometry validity problems
- mixed raster stack assumptions
- nodata confusion
- silent format differences
- undocumented manual fixes

These problems are usually not the "main project," but they still decide whether downstream analysis is trustworthy.

## What this project is not trying to be

Geo Processing Toolkit is not trying to become:

- a full GIS framework
- a desktop GIS
- a replacement for GDAL, Rasterio, GeoPandas, or Shapely
- a black box that hides geospatial complexity

Instead, it is being built as a narrow, explicit layer focused on validation, repair, reporting, and readiness.

## Long-term direction

The long-term direction is to support cross-platform geospatial readiness through:

- stronger validation and reporting
- better compatibility checks
- cloud-native format awareness
- standards-aware metadata checks
- reproducible QA workflows

## Co-existing with the rest of the ecosystem

This project should work with the ecosystem, not against it.

That means:
- complementing core Python geospatial libraries
- preparing data for desktop GIS and cloud workflows
- aligning with formats such as GeoParquet and COG
- improving readiness for STAC-like data exchange patterns

## Maintainer principle

The project will grow in small, practical increments.

Feature breadth is less important than:
- trust
- repeatability
- clear failure behavior
- honest limitations
- useful reports
