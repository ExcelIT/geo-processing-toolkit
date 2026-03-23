# Geo Processing Toolkit

[![CI](https://github.com/ExcelIT/geo-processing-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/ExcelIT/geo-processing-toolkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Release](https://img.shields.io/github/v/release/ExcelIT/geo-processing-toolkit)](https://github.com/ExcelIT/geo-processing-toolkit/releases)

Geo Processing Toolkit is an open-source Python toolkit for common geospatial preprocessing, validation, and conversion workflows.

It is designed for GIS analysts, remote sensing practitioners, developers, and researchers who need reliable utilities for:

- raster clipping to vector polygons
- geometry validation and repair
- vector dataset quality checks
- temporal raster composites from date-based folders
- JSON processing reports for repeatable workflows

This repository is intentionally focused on the boring, repetitive geospatial tasks that often break pipelines.

## Features

- **Clip rasters to polygons** with optional output extent forced to vector bounds
- **Repair invalid geometries** and prepare data for export
- **Validate vector datasets** and generate machine-readable reports
- **Build temporal composites** from multi-date raster folders
- **Emit JSON reports** to support QA, automation, and reproducibility

## Repository structure

```text
geo-processing-toolkit/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── CONTRIBUTING.md
├── CHANGELOG.md
├── src/
│   └── geo_processing_toolkit/
│       ├── __init__.py
│       ├── cli.py
│       ├── clip.py
│       ├── geometry_fix.py
│       ├── temporal_composite.py
│       ├── utils.py
│       └── validate.py
├── tests/
├── examples/
└── docs/
```

## Installation

### Option 1: local editable install

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows PowerShell

pip install --upgrade pip
pip install -e .
```

### Option 2: regular install from source

```bash
git clone https://github.com/ExcelIT/geo-processing-toolkit.git
cd geo-processing-toolkit
pip install .
```

## Dependencies

Main runtime dependencies:

- geopandas
- rasterio
- shapely
- numpy
- click

## Open source status

- License: MIT (`LICENSE`)
- Contribution guide: `CONTRIBUTING.md` 
- Changelog: `CHANGELOG.md` 
- CI: GitHub Actions workflow at `.github/workflows/ci.yml` 
- Repository: `https://github.com/ExcelIT/geo-processing-toolkit` 
- Website: `https://sscar.biz` 

## Project support and contact

For general project information, partnerships, and geospatial solution context:

- General information: `data@sscar.biz` 

For code issues, repository workflows, and infrastructure-related matters:

- Code and infrastructure: `info@excelit.biz` 
- Or open a GitHub issue in this repository for non-sensitive topics

## CLI usage

After installation, the command is:

```bash
gptk --help
```

### 1. Clip raster to vector

```bash
gptk clip-raster \
  --raster data/input.tif \
  --vector data/mask.gpkg \
  --output out/clipped.tif \
  --crop
```

Force the output extent to the vector bounds while keeping source resolution:

```bash
gptk clip-raster \
  --raster data/input.tif \
  --vector data/mask.gpkg \
  --output out/clipped_forced_bounds.tif \
  --force-bounds
```

### 2. Repair invalid geometries

```bash
gptk fix-geometry \
  --input data/broken.gpkg \
  --output out/fixed.gpkg
```

### 3. Validate vector dataset

```bash
gptk validate-vector \
  --input data/parcels.gpkg \
  --report out/parcels_validation.json
```

### 4. Build temporal composite

Assumes folder names end with a date, for example:

- `S2_L2A_2025_20250101`
- `S2_L2A_2025_20250111`
- `S2_L2A_2025_20250121`

Each folder should contain band rasters like `*_B02.tif`, `*_B03.tif`, `*_B04.tif`, etc.

```bash
gptk temporal-composite \
  --input-root data/sentinel_dates \
  --output-dir out/composites \
  --method median
```

### 5. Search folders by name

Search recursively under a root directory and return matching folder paths:

```bash
gptk search-folder \
  --root data \
  --query sentinel \
  --max-results 20
```

Optional behavior:

- `--case-sensitive` for case-sensitive matching
- `--non-recursive` to search only direct children of `--root`
- `--report out/folder_search.json` to save a JSON report

## Python usage

```python
from geo_processing_toolkit.clip import clip_raster
from geo_processing_toolkit.validate import validate_vector_file

clip_raster(
    raster_path="data/input.tif",
    vector_path="data/mask.gpkg",
    output_path="out/clipped.tif",
    crop=True,
)

report = validate_vector_file("data/parcels.gpkg")
print(report["summary"])
```

## Output reports

Where relevant, commands write JSON reports containing:

- input/output paths
- geometry statistics
- band processing summaries
- validation findings
- timestamps

This makes the toolkit easier to use in automated pipelines such as CI, scheduled tasks, n8n, or other orchestration systems.

## Suggested roadmap

- add Cloud Optimized GeoTIFF support
- add GeoParquet support
- add STAC item utilities
- add raster stack alignment checks
- add nodata harmonization tools
- add parallel composite processing

See `docs/roadmap.md`.

## Contributing

See `CONTRIBUTING.md`.

## License

MIT License. See `LICENSE`.

## Contact

Geo Processing Toolkit is maintained as an open-source geospatial Python project.

### General information
For general information, project context, partnerships, or geospatial service inquiries:

- `data@sscar.biz` 

### Code, bugs, and infrastructure
For code-related issues, bug reports, enhancement requests, repository workflow matters, and infrastructure-related questions:

- `info@excelit.biz` 
- Or open an issue in this repository for non-sensitive topics

### Website
- `https://sscar.biz` 
