from __future__ import annotations

from pathlib import Path
from typing import Any

from .utils import utc_now_iso, write_json


def search_folders(
    root: str | Path,
    query: str,
    case_sensitive: bool = False,
    recursive: bool = True,
    max_results: int | None = None,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("Query must not be empty.")

    root_path = Path(root)
    if not root_path.exists() or not root_path.is_dir():
        raise ValueError("Root must be an existing directory.")

    needle = query if case_sensitive else query.lower()
    matches: list[Path] = []
    scanned_dir_count = 0

    candidates = root_path.rglob("*") if recursive else root_path.iterdir()
    for candidate in sorted(candidates, key=lambda p: str(p).lower()):
        if not candidate.is_dir():
            continue
        scanned_dir_count += 1
        haystack = candidate.name if case_sensitive else candidate.name.lower()
        if needle in haystack:
            matches.append(candidate)
            if max_results is not None and len(matches) >= max_results:
                break

    report = {
        "timestamp_utc": utc_now_iso(),
        "operation": "search_folders",
        "input": {
            "root": str(root_path),
            "query": query,
            "case_sensitive": case_sensitive,
            "recursive": recursive,
            "max_results": max_results,
        },
        "summary": {
            "scanned_dir_count": scanned_dir_count,
            "match_count": len(matches),
        },
        "matches": [str(path) for path in matches],
    }

    if report_path:
        write_json(report, report_path)

    return report
