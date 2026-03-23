from geo_processing_toolkit.utils import safe_stem


def test_safe_stem():
    assert safe_stem("My Composite Folder 2026") == "my_composite_folder_2026"
