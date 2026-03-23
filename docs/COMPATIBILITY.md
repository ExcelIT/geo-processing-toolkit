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

## Tested vs planned compatibility matrix

### Python versions

| Version | Status | Notes |
|---------|--------|-------|
| 3.11 | ✅ Tested | Primary CI target |
| 3.12 | ⚠️ Expected to work | Not yet in CI |
| 3.10 | ⚠️ Expected to work | Not yet in CI |
| 3.9 | ❌ Not supported | Below minimum version |

### Raster formats

| Format | Status | Notes |
|--------|--------|-------|
| GeoTIFF | ✅ Tested | Primary validation target |
| COG | 🔄 Planned | Validation guidance in roadmap |
| NetCDF | ⚠️ Expected to work via Rasterio | Not explicitly tested |
| HDF5 | ⚠️ Expected to work via Rasterio | Not explicitly tested |

### Vector formats

| Format | Status | Notes |
|--------|--------|-------|
| GeoPackage | ✅ Tested | Primary validation target |
| Shapefile | ✅ Tested | Validation and repair tested |
| GeoJSON | ⚠️ Expected to work | Not yet in test suite |
| GeoParquet | 🔄 Planned | Validation support in roadmap |
| FlatGeobuf | ❌ Out of scope for now | Not prioritized |

### Core library dependencies

| Library | Tested version range | Notes |
|---------|---------------------|-------|
| GeoPandas | 0.14+ | Primary vector processing |
| Rasterio | 1.3+ | Primary raster I/O |
| Shapely | 2.0+ | Geometry operations |
| NumPy | 1.24+ | Array operations |
| Click | 8.1+ | CLI framework |

### Downstream platform expectations

| Platform | Status | Notes |
|----------|--------|-------|
| QGIS | ⚠️ Expected compatible | Output formats QGIS-readable, not explicitly tested |
| ArcGIS | ⚠️ Expected compatible | Standard formats, not explicitly tested |
| Python workflows | ✅ Tested | GeoPandas/Rasterio interop tested |
| Cloud catalogs | 🔄 Planned | STAC/COG alignment in roadmap |
| CI/CD automation | ✅ Tested | JSON reporting designed for automation |

### Legend

- ✅ **Tested**: Actively tested in CI or local workflows
- ⚠️ **Expected to work**: Should work based on dependencies, not explicitly tested
- 🔄 **Planned**: On roadmap, not yet implemented
- ❌ **Not supported / Out of scope**: Not currently prioritized

## Important note

Compatibility does not mean hidden transformation.

The toolkit should stay explicit:
- detect problems clearly
- report them clearly
- support repeatable QA
- avoid pretending to "fix everything automatically"
