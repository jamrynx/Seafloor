"""
Feature engineering for seafloor EM profiler data (Muller et al. 2012, PANGAEA).

Raw columns (as published):
    Latitude, Longitude, Distance [m], Depth water [m],
    kappa [10**-6 SI] (raw sensor), Poros [% vol], Sal,
    kappa [10**-6 SI] (matrix-corrected), <63 um (categorical), Seafloor und [m]

This module:
    1. Loads and cleans the raw .tab file (PANGAEA tab-delimited format
       with a '/* ... */' metadata header block to skip).
    2. Derives an apparent conductivity feature from Porosity + Salinity
       via Archie's Law (documented below), since the raw file does not
       give bulk conductivity directly.
    3. Simulates "low-cost sensor" noise degradation (this is a project
       design choice -- the source sensor is research-grade; objective 1
       calls for low-cost sensor characteristics, so we inject realistic
       noise/dropout to study robustness).
    4. Windows the continuous profile into fixed-length segments and
       extracts per-segment statistical features suitable for clustering.

Archie's Law reference:
    Formation factor F = a * porosity^(-m)
    Bulk conductivity sigma_bulk = sigma_water / F = sigma_water * porosity^m / a
    Water conductivity sigma_water is estimated from salinity via a
    standard seawater conductivity approximation.
    Constants (a=1, m=1.6) match those stated in the dataset's own comment
    field, ensuring consistency with the source paper's methodology.
"""

import numpy as np
import pandas as pd

# --- Archie's Law constants (as stated in the dataset's own metadata comment) ---
ARCHIE_A = 1.0
ARCHIE_M = 1.6


def load_raw_tab(filepath: str) -> pd.DataFrame:
    """
    Load a PANGAEA-format .tab file, skipping the /* ... */ metadata header.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the end of the metadata comment block
    data_start = 0
    in_comment = False
    for i, line in enumerate(lines):
        if line.strip().startswith("/*"):
            in_comment = True
        if in_comment and line.strip().endswith("*/"):
            data_start = i + 1
            in_comment = False
            break

    from io import StringIO
    data_str = "".join(lines[data_start:])
    df = pd.read_csv(StringIO(data_str), sep="\t")
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename the raw PANGAEA columns to clean, code-friendly names.
    Handles the fact that 'kappa' appears twice (raw sensor + matrix-corrected).
    """
    cols = list(df.columns)
    rename_map = {}
    kappa_seen = 0
    for c in cols:
        if c.startswith("Latitude"):
            rename_map[c] = "latitude"
        elif c.startswith("Longitude"):
            rename_map[c] = "longitude"
        elif c.startswith("Distance"):
            rename_map[c] = "distance_m"
        elif c.startswith("Depth"):
            rename_map[c] = "depth_water_m"
        elif c.startswith("kappa"):
            kappa_seen += 1
            rename_map[c] = "kappa_raw" if kappa_seen == 1 else "kappa_matrix"
        elif c.startswith("Poros"):
            rename_map[c] = "porosity_pct"
        elif c.startswith("Sal"):
            rename_map[c] = "salinity"
        elif c.startswith("<63"):
            rename_map[c] = "clay_silt_fraction"
        elif c.startswith("Seafloor"):
            rename_map[c] = "seafloor_undulation_m"
    return df.rename(columns=rename_map)


def derive_conductivity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive apparent bulk conductivity from porosity + salinity via Archie's Law.
    Uses a standard linear approximation of seawater conductivity from salinity
    (valid near-surface, ~constant temperature assumption -- document this
    simplification explicitly in the report).
    """
    df = df.copy()
    # Approximate seawater conductivity (S/m) from salinity (PSU),
    # simple linear approximation around typical seafloor temperatures.
    # sigma_water (S/m) ~= 0.18 * salinity  (rough field approximation;
    # replace with a proper UNESCO/PSS-78 formula if higher fidelity needed)
    sigma_water = 0.18 * df["salinity"]

    porosity_frac = df["porosity_pct"] / 100.0
    formation_factor = ARCHIE_A * porosity_frac ** (-ARCHIE_M)
    df["apparent_conductivity_Sm"] = sigma_water / formation_factor
    return df


def inject_lowcost_sensor_noise(df: pd.DataFrame, noise_frac: float = 0.05,
                                  dropout_frac: float = 0.02,
                                  random_state: int = 42) -> pd.DataFrame:
    """
    Simulate low-cost sensor degradation relative to the research-grade
    GEM-3 sensor used in the source study:
      - Gaussian noise proportional to signal magnitude (noise_frac)
      - Random dropout (missing readings) at dropout_frac rate

    This is a documented, explicit project design choice (see docstring at
    top of file) -- NOT a claim that the original data itself is noisy.
    """
    rng = np.random.default_rng(random_state)
    df = df.copy()

    for col in ["kappa_matrix", "apparent_conductivity_Sm"]:
        signal = df[col].values
        noise = rng.normal(0, noise_frac * np.nanstd(signal), size=len(signal))
        df[col] = signal + noise

        dropout_mask = rng.random(len(signal)) < dropout_frac
        df.loc[dropout_mask, col] = np.nan

    # Forward-fill dropped readings (simple low-cost-sensor gap handling)
    df[["kappa_matrix", "apparent_conductivity_Sm"]] = (
        df[["kappa_matrix", "apparent_conductivity_Sm"]].ffill().bfill()
    )
    return df


def window_features(df: pd.DataFrame, window_m: float = 50.0) -> pd.DataFrame:
    """
    Segment the continuous profile into fixed-length windows (by distance)
    and extract per-window statistical features for clustering.
    """
    df = df.copy()
    df["segment_id"] = (df["distance_m"] // window_m).astype(int)

    agg = df.groupby("segment_id").agg(
        latitude=("latitude", "mean"),
        longitude=("longitude", "mean"),
        distance_start_m=("distance_m", "min"),
        distance_end_m=("distance_m", "max"),
        kappa_mean=("kappa_matrix", "mean"),
        kappa_std=("kappa_matrix", "std"),
        kappa_max=("kappa_matrix", "max"),
        conductivity_mean=("apparent_conductivity_Sm", "mean"),
        conductivity_std=("apparent_conductivity_Sm", "std"),
        conductivity_max=("apparent_conductivity_Sm", "max"),
        depth_mean=("depth_water_m", "mean"),
    ).reset_index()

    agg = agg.dropna()
    return agg


def build_feature_table(raw_filepath: str, window_m: float = 50.0,
                         simulate_lowcost_sensor: bool = True) -> pd.DataFrame:
    """
    Full pipeline: load -> clean -> derive conductivity -> (optional) noise
    injection -> window -> feature table ready for clustering.
    """
    df = load_raw_tab(raw_filepath)
    df = rename_columns(df)
    df = derive_conductivity(df)
    if simulate_lowcost_sensor:
        df = inject_lowcost_sensor_noise(df)
    features = window_features(df, window_m=window_m)
    return features


if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else "data/raw/GeoB130124_sample.tab"
    features = build_feature_table(filepath)
    print(features.head())
    print(f"\n{len(features)} segments extracted.")
    features.to_csv("data/processed/features_GeoB130124.csv", index=False)
    print("Saved to data/processed/features_GeoB130124.csv")
