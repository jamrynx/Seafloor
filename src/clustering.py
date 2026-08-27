"""
Clustering pipeline: compares Euclidean vs Cosine similarity for grouping
seafloor magnetic/conductivity signatures (Objective 2).

Primary method: Hierarchical Agglomerative Clustering (HAC)
    - Accepts any distance metric via a precomputed distance matrix.
    - Produces dendrograms for visual interpretation.

Secondary method: K-Means
    - Native Euclidean only. For a "cosine-equivalent" comparison, we
      L2-normalize feature vectors first, which makes Euclidean distance
      on normalized vectors monotonically equivalent to cosine distance
      (this equivalence is documented, not just asserted -- see README).
"""

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, adjusted_rand_score

FEATURE_COLUMNS = [
    "kappa_mean", "kappa_std", "kappa_max",
    "conductivity_mean", "conductivity_std", "conductivity_max",
]


def prepare_matrix(features: pd.DataFrame) -> np.ndarray:
    """Standardize feature columns before any distance computation."""
    X = features[FEATURE_COLUMNS].values
    scaler = StandardScaler()
    return scaler.fit_transform(X)


def run_hac(X: np.ndarray, metric: str = "euclidean", n_clusters: int = 3,
            method: str = "average"):
    """
    Run Hierarchical Agglomerative Clustering with a given distance metric.
    metric: 'euclidean' or 'cosine' (anything scipy.pdist supports).
    method: linkage method -- 'average' works for both metrics;
            'ward' only valid for euclidean.
    """
    dist_condensed = pdist(X, metric=metric)
    Z = linkage(dist_condensed, method=method)
    labels = fcluster(Z, t=n_clusters, criterion="maxclust")
    return labels, Z


def run_kmeans_cosine_equivalent(X: np.ndarray, n_clusters: int = 3,
                                   random_state: int = 42):
    """
    K-Means approximating cosine clustering via L2-normalized vectors.
    Euclidean distance between unit vectors u, v relates to cosine similarity as:
        ||u - v||^2 = 2 - 2*cos(u, v)
    so minimizing Euclidean distance on normalized vectors is equivalent
    to maximizing cosine similarity.
    """
    X_norm = normalize(X, norm="l2")
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = km.fit_predict(X_norm)
    return labels, km


def run_kmeans_euclidean(X: np.ndarray, n_clusters: int = 3,
                           random_state: int = 42):
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = km.fit_predict(X)
    return labels, km


def evaluate_clustering(X: np.ndarray, labels: np.ndarray, metric: str = "euclidean") -> dict:
    """Internal validation metrics (used for Objective 3 fallback)."""
    if len(set(labels)) < 2:
        return {"silhouette": None, "davies_bouldin": None}
    return {
        "silhouette": silhouette_score(X, labels, metric=metric),
        "davies_bouldin": davies_bouldin_score(X, labels),
    }


def compare_metrics(features: pd.DataFrame, n_clusters: int = 3) -> dict:
    """
    Full comparison: HAC-Euclidean vs HAC-Cosine vs KMeans-Euclidean vs
    KMeans-CosineEquivalent. Returns labels + internal validation scores +
    agreement (Adjusted Rand Index) between the two HAC variants.
    """
    X = prepare_matrix(features)

    hac_euc_labels, _ = run_hac(X, metric="euclidean", n_clusters=n_clusters, method="ward")
    hac_cos_labels, _ = run_hac(X, metric="cosine", n_clusters=n_clusters, method="average")
    km_euc_labels, _ = run_kmeans_euclidean(X, n_clusters=n_clusters)
    km_cos_labels, _ = run_kmeans_cosine_equivalent(X, n_clusters=n_clusters)

    results = {
        "hac_euclidean": {
            "labels": hac_euc_labels,
            "metrics": evaluate_clustering(X, hac_euc_labels, "euclidean"),
        },
        "hac_cosine": {
            "labels": hac_cos_labels,
            "metrics": evaluate_clustering(X, hac_cos_labels, "cosine"),
        },
        "kmeans_euclidean": {
            "labels": km_euc_labels,
            "metrics": evaluate_clustering(X, km_euc_labels, "euclidean"),
        },
        "kmeans_cosine_equiv": {
            "labels": km_cos_labels,
            "metrics": evaluate_clustering(X, km_cos_labels, "euclidean"),
        },
        "agreement_hac_euc_vs_cos_ARI": adjusted_rand_score(hac_euc_labels, hac_cos_labels),
    }
    return results


if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else "data/processed/features_GeoB130124.csv"
    features = pd.read_csv(filepath)
    results = compare_metrics(features, n_clusters=3)

    for name, res in results.items():
        if name == "agreement_hac_euc_vs_cos_ARI":
            print(f"\nAgreement (ARI) between HAC-Euclidean and HAC-Cosine: {res:.3f}")
            continue
        print(f"\n{name}:")
        print(f"  silhouette: {res['metrics']['silhouette']}")
        print(f"  davies_bouldin: {res['metrics']['davies_bouldin']}")
