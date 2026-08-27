"""
Objective 3: validate groupings against known mineral-deposit survey samples.

STATUS: stub -- to be completed once Phase 4 (see docs/ROADMAP.md) begins,
and once it's confirmed with the supervisor whether external ground-truth
deposit coordinates are meaningfully available for the NW Iberian shelf
survey region used in this project (see docs/DATA_SOURCES.md for the
honest scoping note on this).

Two validation paths are supported here:

1. EXTERNAL validation (if usable ground truth is found):
   compare_to_known_deposits() takes a set of (lat, lon, is_known_deposit)
   reference points and checks whether unsupervised cluster labels
   correspond to real deposit/non-deposit zones (e.g. via purity or a
   simple precision/recall against a distance threshold).

2. INTERNAL validation (fallback, always available):
   already implemented in src/clustering.py via silhouette score and
   Davies-Bouldin index. Use those if no external ground truth applies.
"""

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist


def compare_to_known_deposits(features: pd.DataFrame, labels: np.ndarray,
                                known_deposits: pd.DataFrame,
                                distance_threshold_deg: float = 0.01) -> dict:
    """
    features: must contain 'latitude', 'longitude' columns (segment centroids)
    labels: cluster assignment per segment (same order as features)
    known_deposits: DataFrame with 'latitude', 'longitude' of known
                     mineral-rich reference points
    distance_threshold_deg: how close (in degrees) counts as "near a
                             known deposit" -- convert to meters as needed
                             for your region's latitude.

    Returns per-cluster deposit-proximity purity.
    """
    coords = features[["latitude", "longitude"]].values
    deposit_coords = known_deposits[["latitude", "longitude"]].values

    dists = cdist(coords, deposit_coords)
    near_deposit = (dists.min(axis=1) < distance_threshold_deg)

    df = pd.DataFrame({"cluster": labels, "near_deposit": near_deposit})
    purity_by_cluster = df.groupby("cluster")["near_deposit"].mean().to_dict()
    return {
        "purity_by_cluster": purity_by_cluster,
        "overall_near_deposit_fraction": near_deposit.mean(),
    }


if __name__ == "__main__":
    print("This module is a stub. See docstring for usage once Phase 4 begins.")
