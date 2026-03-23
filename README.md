# Geo Processing Toolkit

Open-source Python toolkit for validating, repairing, and standardizing geospatial datasets before they enter production GIS, remote-sensing, climate-risk, and disaster-response workflows.

Project website: `https://sscar.biz`  
General information: `data@sscar.biz`  
Code and infrastructure: `info@excelit.biz` 

## Why this project exists

A lot of geospatial work still depends on brittle scripts, inconsistent source data, and manual corrections that break pipelines or reduce trust in outputs. Geo Processing Toolkit focuses on the boring but critical layer between raw data and operational use:

- validate inputs before processing
- repair common geometry problems
- normalize raster and vector workflows
- detect compatibility issues early
- produce machine-readable reports for audit, automation, and downstream use

This project is intentionally focused on repeatability, validation, and standards readiness instead of trying to become a full GIS framework.

## What it does

Geo Processing Toolkit currently focuses on practical preprocessing and QA tasks such as:

- raster clipping to polygon extent
- geometry repair for invalid vector inputs
- vector validation and reporting
- temporal composite generation
- JSON processing reports
- folder and input discovery helpers

## Where it fits in the stack

This toolkit is designed to sit between raw geospatial data and downstream analytics, mapping, or decision-support systems.

Typical use cases include:

- validating government or operational base layers before use
- standardizing vector inputs before dashboarding or analysis
- checking raster compatibility before time-series processing
- preparing reproducible preprocessing steps for remote-sensing workflows
- generating QA evidence for project, compliance, or delivery records

## Target users

This project is intended for:

- GIS analysts
- remote-sensing practitioners
- geospatial developers
- environmental and monitoring teams
- crisis and resilience data teams
- consultants building repeatable geospatial workflows

## Design goals

The project is being built around these principles:

- clear command-line workflows
- predictable and testable behavior
- lightweight, practical utilities
- machine-readable reporting
- format-aware validation and repair
- compatibility with modern geospatial standards

## Planned direction

The near-term direction of the project is to strengthen support for operational geospatial QA and cloud-native workflows, including:

- raster stack alignment checks
- GeoParquet support
- Cloud Optimized GeoTIFF (COG) awareness
- nodata harmonization checks
- STAC-oriented validation helpers
- richer JSON report schemas

## Non-goals

This project is not trying to:

- replace GeoPandas, Rasterio, GDAL, or other core geospatial libraries
- become a desktop GIS
- duplicate large-scale analysis frameworks
- hide underlying geospatial complexity behind vague abstractions

Instead, it focuses on the validation, repair, and standardization layer that many production workflows still handle inconsistently.

## Current commands and modules

Core modules and commands are organized around practical workflow steps such as clipping, validation, geometry repair, reporting, and temporal composites.

Continue reading below for installation, usage, examples, testing, and project roadmap.

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
