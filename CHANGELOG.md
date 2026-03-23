# Changelog

## v0.2.0

### Added

- `validate-raster-stack` command for pre-flight raster compatibility checks
- shared JSON report envelope for core command outputs
- documented report schema in `docs/report-schema.md`
- expanded roadmap around geospatial QA, validation, repair, and standards readiness

### Improved

- README positioning and project scope clarity
- command documentation and examples
- contact, contribution, and security guidance

### Notes

This release strengthens Geo Processing Toolkit as a focused open-source toolkit for validating, repairing, and standardizing geospatial datasets before production GIS and remote-sensing workflows.

## 0.1.2 - 2026-03-23

### Added

- README badges for CI, MIT license, and latest release
- GitHub issue templates for bug reports and feature requests
- pull request template with validation checklist
- contributor `Makefile` targets: `lint`, `test`, `build`

### Changed

- release notes for `v0.1.1` updated with post-release improvements

## 0.1.1 - 2026-03-23

### Added

- `search-folder` CLI command for finding matching directories
- `search_folders` Python utility with optional JSON reporting
- tests for folder search utility and CLI command
- GitHub Actions CI workflow (`ruff` + `pytest`)
- `CODE_OF_CONDUCT.md` for open-source governance

### Changed

- README updated with open-source release checklist and command docs
- examples updated with `search-folder` usage

## 0.1.0 - 2026-03-23

Initial public starter release.

### Added

- raster clipping command
- geometry repair command
- vector validation command
- temporal composite command
- JSON reporting helpers
- test suite starter
