# Example commands

## Clip raster

```bash
gptk clip-raster --raster input.tif --vector mask.gpkg --output clipped.tif --crop
```

## Fix geometry

```bash
gptk fix-geometry --input broken.gpkg --output fixed.gpkg
```

## Validate vector

```bash
gptk validate-vector --input parcels.gpkg --report parcels_validation.json
```

## Temporal composite

```bash
gptk temporal-composite --input-root sentinel_dates --output-dir composites --method median
```

## Search folders by name

```bash
gptk search-folder --root data --query sentinel --max-results 10
```
