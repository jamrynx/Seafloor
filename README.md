# Distance-Metric Similarity Grouping of Seafloor Sensor Signatures for Ocean Mineral Resource Exploration

Unsupervised learning project (B.Tech CSE, LPU) — target submission: first
week of November 2026.

## Objectives
1. Extract magnetic and conductivity signature features from low-cost
   seafloor metal-detection sensors.
2. Compare Euclidean and Cosine similarity for grouping seafloor readings
   by mineral-signature similarity.
3. Validate groupings against known mineral-deposit survey samples.

## Status
Early scaffold stage. See `docs/ROADMAP.md` for the full week-by-week plan
and `docs/DATA_SOURCES.md` for exactly where the data comes from and how to
get the complete files (a full download step is required — see below).

## Data
Real field survey data: benthic electromagnetic profiler measurements
(magnetic susceptibility + porosity/salinity, used to derive conductivity)
from the NW Iberian shelf, published by Müller et al. (2012) via PANGAEA,
CC-BY-3.0 licensed. Full citation and download instructions in
`docs/DATA_SOURCES.md`.

**Action required before running the real pipeline:** only a partial sample
(~1900 of 213,645 rows) is committed in `data/raw/` for pipeline development.
Download the complete files manually per the instructions in
`docs/DATA_SOURCES.md` and place them in `data/raw/` before final analysis.

## Project structure
```
data/
  raw/            # original / minimally-touched data files
  processed/      # feature tables ready for clustering
  external/       # any external validation reference data (Objective 3)
src/
  feature_engineering.py   # load, clean, derive conductivity, window, extract features
  clustering.py             # HAC + KMeans, Euclidean vs Cosine comparison
  validation.py             # Objective 3 validation (external + internal fallback)
notebooks/         # exploratory analysis
docs/
  ROADMAP.md        # week-by-week plan to Nov submission
  DATA_SOURCES.md    # data provenance, citation, download steps
tests/              # unit tests
results/figures/    # generated plots (dendrograms, cluster maps, etc.)
```

## Setup
```bash
pip install -r requirements.txt
```

## Running the pipeline (once full data is downloaded)
```bash
python src/feature_engineering.py data/raw/GeoB130124_full.tab
python src/clustering.py data/processed/features_GeoB130124.csv
```

## Methodology notes
- **Why HAC as primary method:** Hierarchical Agglomerative Clustering
  accepts any precomputed distance metric, making it the cleanest way to
  directly compare Euclidean vs Cosine groupings on the same algorithm
  (Objective 2's core ask).
- **Why KMeans is included as secondary:** KMeans is natively Euclidean-only;
  we additionally run it on L2-normalized vectors, which is mathematically
  equivalent to cosine-based clustering (documented in `src/clustering.py`).
- **"Low-cost sensor" framing:** the source dataset uses a research-grade
  EM profiler (GEM-3). Since Objective 1 specifies low-cost sensors, we
  explicitly inject realistic noise/dropout to simulate low-cost sensor
  degradation — this is a stated, documented design decision, not a claim
  about the original data's quality.
- **Objective 3 validation:** the source survey is a sediment
  characterization study, not a mineral-deposit exploration site. External
  ground-truth deposit coordinates for this exact region may not exist; if
  so, this is stated explicitly and internal validation metrics (silhouette,
  Davies-Bouldin) are used instead. See `docs/DATA_SOURCES.md`.

## Citation
Müller, H., von Dobeneck, T., Hilgenfeldt, C., SanFelipo, B., Rey, D.,
Rubio, B. (2012): Mapping the magnetic susceptibility and electric
conductivity of marine surficial sediments by benthic EM profiling.
Geophysics, 77(1), E43-E56. https://doi.org/10.1190/GEO2010-0129.1
(CC-BY-3.0)
