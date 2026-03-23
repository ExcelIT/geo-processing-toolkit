from __future__ import annotations

import json

import click

from .clip import clip_raster
from .folder_search import search_folders
from .geometry_fix import fix_geometries
from .temporal_composite import build_temporal_composites
from .validate import validate_vector_file


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
