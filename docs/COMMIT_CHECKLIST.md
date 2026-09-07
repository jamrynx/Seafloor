# Commit Checklist

A concrete, phase-by-phase list of what to commit and when. The rule: **do
the work first, commit right after that specific piece is genuinely done.**
Don't pre-write commits and don't batch multiple checklist items from
different phases into one commit — that's what makes history look staged.

Each item below = roughly one commit. Check it off as you go.

---

## Phase 0 — Supervisor sign-off
- [ ] `docs(roadmap): confirm scope after supervisor review` — after your
      meeting, if anything in the roadmap/model choice changed, commit the
      updated ROADMAP.md reflecting what sir approved. If nothing changed,
      skip this commit — don't force one.

## Phase 1 — Data acquisition & understanding
- [ ] `data: add full GeoB130124 field profile (213,645 rows)` — after you
      manually download it (kept out of git via .gitignore if too large;
      commit a note in DATA_SOURCES.md confirming you have it locally,
      or commit it if your repo size allows).
- [ ] `data: add full GeoB130106 field profile` — same, second profile.
- [ ] `notebooks: exploratory data analysis on both profiles` — after you've
      actually plotted/inspected the data (a Jupyter notebook in
      notebooks/, saved with output cells so the EDA is visible).
- [ ] `docs(data-sources): document dataset limitations and scoping notes`
      — after you've actually decided how to handle the single-region /
      research-grade-sensor / "low-cost" framing issues.

## Phase 2 — Feature engineering
- [ ] `feat(features): clean raw sensor fields and handle missing values`
      — once you've actually run cleaning against the FULL dataset (not
      just the sample) and confirmed it works.
- [ ] `feat(features): tune windowing and noise-injection parameters on
      full dataset` — once you've picked real window_m and noise_frac
      values based on looking at the real 213k-row profile, not guesses.
- [ ] `data(processed): commit generated feature table` — the actual
      features CSV produced from the full dataset.
- [ ] `test: expand feature engineering tests for full-dataset edge cases`
      — if you find real edge cases (e.g. long missing-data gaps) once
      working with the complete file.

## Phase 3 — Clustering pipeline
- [ ] `feat(clustering): validate distance metric implementations on real
      feature table` — once HAC/KMeans actually run against your real
      features.csv and you've sanity-checked the output.
- [ ] `feat(clustering): add dendrogram + cluster visualization` — actual
      plotting code, once you've decided how you want to visualize results.
- [ ] `feat(clustering): determine and justify cluster count (k)` — once
      you've run the elbow method / dendrogram cut analysis and picked a
      real k with a documented reason.
- [ ] (optional) `feat(clustering): add DBSCAN comparison` — only if you
      actually build this.

## Phase 4 — Comparison & validation
- [ ] `feat(validation): run internal validation metrics on real clusters`
      — silhouette/Davies-Bouldin computed on your actual results, not stubs.
- [ ] `feat(validation): compute Euclidean-vs-Cosine agreement (ARI)` —
      once you have both real clusterings to compare.
- [ ] `feat(validation): attempt external deposit cross-reference` OR
      `docs(validation): document why external ground truth doesn't apply
      to this survey region` — whichever is actually true once you
      investigate.
- [ ] `results: add generated figures (dendrograms, cluster maps, metric
      comparison charts)` — the real output plots.

## Phase 5 — Write-up
- [ ] `docs: draft methodology section` — as you write it.
- [ ] `docs: draft results and discussion section` — as you write it.
- [ ] `docs: add limitations section` — be honest about scope decisions
      made along the way (sample data during dev, single-region survey,
      simulated low-cost sensor noise, etc.)
- [ ] `docs: finalize report` — final version once reviewed.
- [ ] (optional) `docs: add presentation slides` — if required for viva.

## Phase 6 — Submission
- [ ] `chore: incorporate supervisor feedback` — whatever sir actually
      asks you to change.
- [ ] `chore: final cleanup before submission` — remove dead code, fix
      README, tidy structure.
- [ ] Tag `v1.0-submission` on the final commit.

---

## A note on pacing
If you're ever tempted to do 3 weeks of checklist items in one sitting
right before a deadline — that's the sign to stop and actually spread the
remaining work across the days you have left, even if it means shorter
sessions more often. A history with realistic gaps and reasonable commit
sizes is exactly what "normal progress" looks like; it doesn't need to be
daily, just genuine.
