"""
Basic sanity tests for feature_engineering.py using the committed sample file.
Run with: pytest tests/
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from feature_engineering import load_raw_tab, rename_columns, derive_conductivity


SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "raw", "GeoB130124_sample.tab"
)


def test_load_raw_tab_skips_header():
    df = load_raw_tab(SAMPLE_PATH)
    assert len(df) > 0
    assert "Latitude" in df.columns


def test_rename_columns():
    df = load_raw_tab(SAMPLE_PATH)
    df = rename_columns(df)
    expected = {"latitude", "longitude", "distance_m", "depth_water_m",
                "kappa_raw", "porosity_pct", "salinity", "kappa_matrix",
                "clay_silt_fraction", "seafloor_undulation_m"}
    assert expected.issubset(set(df.columns))


def test_derive_conductivity_positive():
    df = load_raw_tab(SAMPLE_PATH)
    df = rename_columns(df)
    df = derive_conductivity(df)
    assert "apparent_conductivity_Sm" in df.columns
    assert (df["apparent_conductivity_Sm"] > 0).all()
