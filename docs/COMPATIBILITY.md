# Compatibility Strategy

## Philosophy

Geo Processing Toolkit is designed to sit between raw geospatial inputs and downstream systems.

It should help answer:
- Is this data structurally usable?
- What needs review before processing?
- What should be repaired or standardized first?
- What evidence do we have that a QA step was performed?

## Ecosystem position

This project complements, rather than replaces:

- Python geospatial libraries such as GeoPandas, Rasterio, Shapely, and GDAL-based tooling
- desktop GIS platforms such as QGIS and ArcGIS
- cloud-native and interoperable workflows built around COG, GeoParquet, and STAC-like structures
- automation and CI/CD workflows that need machine-readable validation output

## Current compatibility posture

Current focus is strongest in:
- CLI-based validation workflows
- raster stack pre-flight checks
- vector validation and geometry repair
- JSON reporting for QA review and automation

## Near-term compatibility priorities

- GeoParquet validation support
- COG-aware raster validation guidance
- STAC-oriented metadata checks
- broader report consistency across commands
- more real-world QA examples

## Important note

Compatibility does not mean hidden transformation.

The toolkit should stay explicit:
- detect problems clearly
- report them clearly
- support repeatable QA
- avoid pretending to "fix everything automatically"
