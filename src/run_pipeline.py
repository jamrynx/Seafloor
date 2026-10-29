"""
First-pass end-to-end run on both full PANGAEA profiles.

Usage (from repo root):  python src/run_pipeline.py

For each profile: build the 50 m window feature table, run the four
clustering variants at k=3, and compare each against the dominant clay/silt
grain-size class of the window (ARI / NMI). Writes
data/processed/features_<profile>.csv and results/metrics_first_pass.csv.

Notes for the report:
  * HAC-Euclidean uses Ward linkage; HAC-Cosine uses average linkage (Ward is
    only defined for Euclidean), so the two differ in linkage as well as metric.
  * Silhouette for HAC-Cosine is computed in cosine space, so it is not
    directly comparable with the Euclidean-space scores.
  * The grain class is a sediment-type reference from Muller et al. (2012),
    not an independent mineral-deposit survey.
"""
import os
import sys

import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import clustering as cl
import feature_engineering as fe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES = ["GeoB130124", "GeoB130106"]
GRAIN_ORDER = {"<5%": 0, "5-25%": 1, "25-50%": 2, "50-90%": 3, ">90%": 4}
WINDOW_M = 50


def main(k: int = 3) -> None:
    rows = []
    os.makedirs(os.path.join(ROOT, "data", "processed"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    for name in PROFILES:
        raw = os.path.join(ROOT, "data", "raw", f"{name}_full.tab")
        df = fe.rename_columns(fe.load_raw_tab(raw))
        feats = fe.build_feature_table(raw, window_m=WINDOW_M)
        feats.to_csv(os.path.join(ROOT, "data", "processed", f"features_{name}.csv"), index=False)

        df["segment_id"] = (df["distance_m"] // WINDOW_M).astype(int)
        grain = df.groupby("segment_id")["clay_silt_fraction"].agg(lambda s: s.mode().iloc[0])
        feats = feats.merge(grain.rename("grain"), left_on="segment_id", right_index=True)
        ref = feats["grain"].map(GRAIN_ORDER).values

        res = cl.compare_metrics(feats.drop(columns=["grain"]), n_clusters=k)
        print(f"\n== {name}: {len(df)} readings -> {len(feats)} windows")
        for method, v in res.items():
            if method.startswith("agreement"):
                print(f"HAC euclidean vs cosine ARI: {v:.3f}")
                rows.append({"profile": name, "method": method, "k": k, "ari_between_hac": round(v, 4)})
                continue
            m, lab = v["metrics"], v["labels"]
            row = {
                "profile": name, "method": method, "k": k, "n_windows": len(feats),
                "silhouette": m["silhouette"], "davies_bouldin": m["davies_bouldin"],
                "ari_vs_grain": round(adjusted_rand_score(ref, lab), 4),
                "nmi_vs_grain": round(normalized_mutual_info_score(ref, lab), 4),
            }
            rows.append(row)
            print(f"{method:22s} sil={row['silhouette']} DB={row['davies_bouldin']} "
                  f"ARI={row['ari_vs_grain']} NMI={row['nmi_vs_grain']}")
    pd.DataFrame(rows).to_csv(os.path.join(ROOT, "results", "metrics_first_pass.csv"), index=False)
    print("\nWrote results/metrics_first_pass.csv")


if __name__ == "__main__":
    main()
