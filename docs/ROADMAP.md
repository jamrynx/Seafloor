# Roadmap — Distance-Metric Similarity Grouping of Seafloor Sensor Signatures

**Target submission: first week of November 2026**
**Today: Aug 27, 2026 → ~9-10 weeks available**

Status legend: [ ] todo · [~] in progress · [x] done

## Phase 0 — Confirm approach with supervisor (THIS WEEK)
- [ ] Show sir the model shortlist (HAC as primary, K-Means on normalized
      vectors as secondary, DBSCAN optional) and confirm before building
      the clustering code.
- [ ] Confirm real-data approach (Müller et al. PANGAEA field data) vs.
      synthetic is acceptable, and confirm the objective-3 fallback plan
      (internal validation metrics if no external deposit ground truth
      applies to this survey region).
- [ ] Get sign-off on final scope before deeper implementation.

## Phase 1 — Data acquisition & understanding (Week 1)
- [ ] Manually download full GeoB130124 + GeoB130106 .tab files from PANGAEA
      (see docs/DATA_SOURCES.md) and place in data/raw/.
- [ ] Exploratory data analysis: plot profiles, check ranges/units, look for
      missing values, check the two profiles for consistency.
- [ ] Document dataset limitations clearly (single-region, sediment
      characterization survey rather than mineral-deposit exploration,
      "low-cost sensor" framing is a project design choice not a literal
      match to the GEM-3 research-grade sensor used in the study).

## Phase 2 — Feature engineering (Week 2)
- [ ] Clean data: handle categorical <63µm field, missing seafloor
      undulation values, sensor noise smoothing (moving average / outlier
      rejection) to simulate "low-cost sensor" conditions per objective 1.
- [ ] Derive apparent conductivity feature from Porosity + Salinity via
      Archie's Law (documented formula, cited).
- [ ] Window the continuous profile into fixed-length segments (e.g. every
      N meters of distance) and extract per-segment features: mean, std,
      peak anomaly, gradient for magnetic susceptibility and conductivity.
- [ ] Standardize/normalize features (z-score) before distance computation.
- [ ] Output clean feature table to data/processed/features.csv.

## Phase 3 — Distance metric & clustering pipeline (Weeks 3-4)
- [ ] Implement pairwise distance computation: Euclidean and Cosine.
- [ ] Implement Hierarchical Agglomerative Clustering (primary method) with
      both metrics; generate dendrograms.
- [ ] Implement K-Means on L2-normalized vectors as secondary comparison
      (document why this approximates cosine clustering).
- [ ] Optional: DBSCAN as a third comparison for outlier/noise handling.
- [ ] Determine number of clusters (elbow method / dendrogram cut / domain
      reasoning tied to known lithofacies transitions in the source paper).

## Phase 4 — Comparison & validation (Weeks 5-6)
- [ ] Compare Euclidean vs Cosine groupings: visualize cluster assignments
      along the spatial profile (map/plot), quantify agreement (e.g.
      Adjusted Rand Index between the two clusterings).
- [ ] Internal validation: silhouette score, Davies-Bouldin index for each
      metric/method combination.
- [ ] Objective 3 validation: attempt cross-reference against any available
      external deposit-zone reference; if not meaningfully applicable to
      this survey region, state that explicitly and rely on internal
      validation + geological plausibility (do clusters align with known
      lithofacies transitions reported in the original paper, e.g.
      mud/sand boundaries).

## Phase 5 — Write-up & polish (Weeks 7-8)
- [ ] Draft report: intro, methodology, results, discussion, limitations.
- [ ] Generate all figures (dendrograms, cluster maps, metric comparison
      charts).
- [ ] Internal review pass — check every claim is backed by a result file.
- [ ] Optional: slide deck for viva/defense if required.

## Phase 6 — Buffer & submission (Week 9-10)
- [ ] Buffer week for supervisor feedback incorporation.
- [ ] Final proofread, repo cleanup, submission packaging.
- [ ] Submit (first week of November target).

## Git commit discipline
- One logical change per commit (data ingestion, feature engineering,
  clustering, validation, docs — not mixed).
- Commit messages: imperative mood, scoped prefix, e.g.
  `feat(features): add Archie's law conductivity derivation`
  `fix(clustering): correct cosine distance normalization`
  `docs(roadmap): update Phase 2 status`
- Tag milestones: `v0.1-data-ready`, `v0.2-features-ready`,
  `v0.3-clustering-ready`, `v1.0-submission`.
