from geo_processing_toolkit.folder_search import search_folders


def test_search_folders_recursive(tmp_path):
    (tmp_path / "alpha_folder").mkdir()
    nested_parent = tmp_path / "nested"
    nested_parent.mkdir()
    (nested_parent / "alpha_nested").mkdir()

    report = search_folders(root=tmp_path, query="alpha")

    assert report["command"] == "search-folder"
    assert report["status"] == "PASS"
    assert "generated_at" in report
    assert report["summary"]["match_count"] == 2
    assert any(path.endswith("alpha_folder") for path in report["matches"])
    assert any(path.endswith("alpha_nested") for path in report["matches"])


def test_search_folders_non_recursive(tmp_path):
    (tmp_path / "alpha_folder").mkdir()
    nested_parent = tmp_path / "nested"
    nested_parent.mkdir()
    (nested_parent / "alpha_nested").mkdir()

    report = search_folders(root=tmp_path, query="alpha", recursive=False)

    assert report["summary"]["match_count"] == 1
    assert report["matches"][0].endswith("alpha_folder")


def test_search_folders_case_sensitive(tmp_path):
    (tmp_path / "AlphaFolder").mkdir()

    insensitive = search_folders(root=tmp_path, query="alpha", case_sensitive=False)
    sensitive = search_folders(root=tmp_path, query="alpha", case_sensitive=True)

    assert insensitive["summary"]["match_count"] == 1
    assert sensitive["summary"]["match_count"] == 0


def test_search_folders_max_results(tmp_path):
    (tmp_path / "alpha_1").mkdir()
    (tmp_path / "alpha_2").mkdir()

    report = search_folders(root=tmp_path, query="alpha", max_results=1)

    assert report["summary"]["match_count"] == 1


def test_search_folders_writes_report(tmp_path):
    (tmp_path / "alpha_1").mkdir()
    report_path = tmp_path / "folder_search_report.json"

    report = search_folders(root=tmp_path, query="alpha", report_path=report_path)

    assert report_path.exists()
    assert report["summary"]["match_count"] == 1
