import json

from click.testing import CliRunner

from geo_processing_toolkit.cli import cli


def test_search_folder_command(tmp_path):
    (tmp_path / "sentinel_a").mkdir()
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "sentinel_b").mkdir()

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "search-folder",
            "--root",
            str(tmp_path),
            "--query",
            "sentinel",
            "--max-results",
            "2",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["command"] == "search-folder"
    assert payload["status"] == "PASS"
    assert "generated_at" in payload
    assert payload["summary"]["match_count"] == 2
