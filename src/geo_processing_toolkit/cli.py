from __future__ import annotations

import json

import click

from .clip import clip_raster
from .folder_search import search_folders
from .geometry_fix import fix_geometries
from .temporal_composite import build_temporal_composites
from .validate import validate_vector_file
from .validate_raster_stack import validate_raster_stack
from .utils import write_json


@click.group()
def cli() -> None:
    """Geo Processing Toolkit CLI."""


@cli.command("clip-raster")
@click.option("--raster", "raster_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--vector", "vector_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "output_path", required=True, type=click.Path(dir_okay=False))
@click.option("--crop", is_flag=True, help="Crop output to vector extent.")
@click.option("--force-bounds", is_flag=True, help="Force output extent to vector bounds using source resolution.")
@click.option("--report", "report_path", type=click.Path(dir_okay=False), help="Optional JSON report path.")
def clip_raster_cmd(raster_path: str, vector_path: str, output_path: str, crop: bool, force_bounds: bool, report_path: str | None) -> None:
    report = clip_raster(
        raster_path=raster_path,
        vector_path=vector_path,
        output_path=output_path,
        crop=crop,
        force_bounds=force_bounds,
        report_path=report_path,
    )
    click.echo(json.dumps(report, indent=2))


def _report_messages(report: dict, level: str) -> list[tuple[str, str, str]]:
    items: list[tuple[str, str, str]] = []
    for file_item in report.get("files", []):
        path = file_item.get("path") or "<unknown>"
        for message in file_item.get("messages", []):
            if message.get("level") == level:
                items.append((path, message.get("code", ""), message.get("message", "")))
    return items


@cli.command("validate-raster-stack")
@click.argument("paths", nargs=-1, required=True, type=click.Path(path_type=str))
@click.option("--pattern", default="*.tif", show_default=True, type=str)
@click.option("--recursive", is_flag=True, help="Search directories recursively.")
@click.option("--reference", type=click.Choice(["first", "file"], case_sensitive=False), default="first", show_default=True)
@click.option("--reference-file", type=click.Path(path_type=str, dir_okay=False), default=None)
@click.option("--json-out", type=click.Path(path_type=str, dir_okay=False), default=None)
@click.option("--quiet", is_flag=True, help="Only print summary/errors to console.")
@click.option("--verbose", is_flag=True, help="Print per-file details.")
@click.option("--fail-on", type=click.Choice(["error", "warning", "never"], case_sensitive=False), default="error", show_default=True)
@click.option("--check-nodata/--no-check-nodata", default=True, show_default=True)
@click.option("--check-dtype/--no-check-dtype", default=True, show_default=True)
@click.option("--check-driver/--no-check-driver", default=True, show_default=True)
@click.option("--tolerance-resolution", type=float, default=0.0, show_default=True)
@click.option("--tolerance-bounds", type=float, default=0.0, show_default=True)
@click.option("--tolerance-transform", type=float, default=0.0, show_default=True)
def validate_raster_stack_cmd(
    paths: tuple[str, ...],
    pattern: str,
    recursive: bool,
    reference: str,
    reference_file: str | None,
    json_out: str | None,
    quiet: bool,
    verbose: bool,
    fail_on: str,
    check_nodata: bool,
    check_dtype: bool,
    check_driver: bool,
    tolerance_resolution: float,
    tolerance_bounds: float,
    tolerance_transform: float,
) -> None:
    if quiet and verbose:
        raise click.UsageError("Use either --quiet or --verbose, not both.")

    if reference.lower() == "file" and not reference_file:
        raise click.UsageError("--reference-file is required when --reference file is used.")

    try:
        report = validate_raster_stack(
            paths=list(paths),
            pattern=pattern,
            recursive=recursive,
            reference=reference.lower(),
            reference_file=reference_file,
            check_nodata=check_nodata,
            check_dtype=check_dtype,
            check_driver=check_driver,
            tolerance_resolution=tolerance_resolution,
            tolerance_bounds=tolerance_bounds,
            tolerance_transform=tolerance_transform,
        )
        report["fail_on"] = fail_on.lower()

        if json_out:
            write_json(report, json_out)

        errors = _report_messages(report, "error")
        warnings = _report_messages(report, "warning")

        if not quiet:
            if report["status"] == "FAIL":
                click.echo("Raster stack validation failed")
            else:
                click.echo("Raster stack validation passed")

            click.echo("")
            click.echo(f"Files checked: {len(report.get('resolved_inputs', []))}")
            ref_value = report.get("reference_raster") or "<none>"
            click.echo(f"Reference raster: {ref_value}")
            click.echo("")
            click.echo("Checks:")
            labels = [
                ("crs", "CRS"),
                ("bounds", "Bounds"),
                ("resolution", "Resolution"),
                ("transform", "Transform"),
                ("dimensions", "Width/height"),
                ("band_count", "Band count"),
                ("nodata", "Nodata"),
                ("dtype", "Dtype"),
                ("driver", "Driver"),
            ]
            for key, label in labels:
                state = report.get("checks", {}).get(key, "pass")
                rendered = "OK" if state == "pass" else state.upper()
                click.echo(f"- {label}: {rendered}")

            if errors:
                click.echo("")
                click.echo("Errors:")
                for path, _, message in errors:
                    click.echo(f"- {path}: {message}")

            if warnings:
                click.echo("")
                click.echo("Warnings:")
                for path, _, message in warnings:
                    click.echo(f"- {path}: {message}")

            if verbose:
                click.echo("")
                click.echo("Per-file status:")
                for file_item in report.get("files", []):
                    click.echo(f"- {file_item.get('path', '<unknown>')}: {str(file_item.get('status', 'pass')).upper()}")
        else:
            if errors:
                click.echo("Errors:")
                for path, _, message in errors:
                    click.echo(f"- {path}: {message}")

        click.echo("")
        click.echo("Summary:")
        click.echo(f"- Errors: {report['summary']['errors']}")
        click.echo(f"- Warnings: {report['summary']['warnings']}")
        click.echo(f"- Status: {report['status']}")

        fail_policy = fail_on.lower()
        should_fail = False
        if fail_policy == "error":
            should_fail = report["summary"]["errors"] > 0
        elif fail_policy == "warning":
            should_fail = report["summary"]["errors"] > 0 or report["summary"]["warnings"] > 0
        elif fail_policy == "never":
            should_fail = False

        raise SystemExit(1 if should_fail else 0)
    except click.ClickException:
        raise
    except Exception as exc:
        click.echo(f"Unexpected runtime error: {exc}", err=True)
        raise SystemExit(3)


@cli.command("fix-geometry")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "output_path", required=True, type=click.Path(dir_okay=False))
@click.option("--keep-only-valid", is_flag=True, help="Drop invalid/empty/null geometries after attempted repair.")
@click.option("--report", "report_path", type=click.Path(dir_okay=False), help="Optional JSON report path.")
def fix_geometry_cmd(input_path: str, output_path: str, keep_only_valid: bool, report_path: str | None) -> None:
    report = fix_geometries(
        input_path=input_path,
        output_path=output_path,
        keep_only_valid=keep_only_valid,
        report_path=report_path,
    )
    click.echo(json.dumps(report, indent=2))


@cli.command("validate-vector")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--report", "report_path", required=True, type=click.Path(dir_okay=False))
def validate_vector_cmd(input_path: str, report_path: str) -> None:
    report = validate_vector_file(input_path=input_path, report_path=report_path)
    click.echo(json.dumps(report, indent=2))


@cli.command("temporal-composite")
@click.option("--input-root", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--output-dir", required=True, type=click.Path(file_okay=False))
@click.option(
    "--method",
    type=click.Choice(["median", "mean", "max", "min"], case_sensitive=False),
    default="median",
    show_default=True,
)
@click.option("--report", "report_path", type=click.Path(dir_okay=False), help="Optional JSON report path.")
def temporal_composite_cmd(input_root: str, output_dir: str, method: str, report_path: str | None) -> None:
    report = build_temporal_composites(
        input_root=input_root,
        output_dir=output_dir,
        method=method.lower(),
        report_path=report_path,
    )
    click.echo(json.dumps(report, indent=2))


@cli.command("search-folder")
@click.option("--root", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--query", required=True, type=str)
@click.option("--case-sensitive", is_flag=True, help="Use case-sensitive matching.")
@click.option("--non-recursive", is_flag=True, help="Only search direct children of root.")
@click.option("--max-results", type=click.IntRange(min=1), help="Maximum matches to return.")
@click.option("--report", "report_path", type=click.Path(dir_okay=False), help="Optional JSON report path.")
def search_folder_cmd(
    root: str,
    query: str,
    case_sensitive: bool,
    non_recursive: bool,
    max_results: int | None,
    report_path: str | None,
) -> None:
    report = search_folders(
        root=root,
        query=query,
        case_sensitive=case_sensitive,
        recursive=not non_recursive,
        max_results=max_results,
        report_path=report_path,
    )
    click.echo(json.dumps(report, indent=2))


if __name__ == "__main__":
    cli()
