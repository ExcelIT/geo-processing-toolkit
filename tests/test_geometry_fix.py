from shapely.geometry import Polygon

from geo_processing_toolkit.geometry_fix import _fix_geometry


def test_fix_invalid_polygon():
    bowtie = Polygon([(0, 0), (2, 2), (2, 0), (0, 2), (0, 0)])
    assert not bowtie.is_valid
    fixed = _fix_geometry(bowtie)
    assert fixed is not None
    assert fixed.is_valid
