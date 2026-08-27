# Data Sources

## Primary dataset (real field survey data)

**Müller, H. et al. (2012)** — Magnetic susceptibility and electric conductivity of
marine surficial sediments by benthic electromagnetic profiling.
Published in: *Geophysics*, 77(1), E43-E56. https://doi.org/10.1190/GEO2010-0129.1
Data series (PANGAEA): https://doi.org/10.1594/PANGAEA.776056
License: CC-BY-3.0 — https://creativecommons.org/licenses/by/3.0/

Two real field profiles from the NW Iberian shelf, collected by the benthic EM
profiler "Neridis II" during cruise POS366/3 (2008):

| Profile    | DOI                                    | Rows    | File to download |
|------------|-----------------------------------------|---------|-------------------|
| GeoB130124 | https://doi.org/10.1594/PANGAEA.776054 | 213,645 | `data/raw/GeoB130124_full.tab` |
| GeoB130106 | https://doi.org/10.1594/PANGAEA.776055 | (check page) | `data/raw/GeoB130106_full.tab` |

### How to download the COMPLETE files (must be done manually)

The Claude sandbox used to scaffold this repo does not have network access to
pangaea.de, so only a partial sample (~1900 rows) was pulled automatically for
pipeline development. **Before running the real analysis, download the full
files yourself:**

1. Go to https://doi.pangaea.de/10.1594/PANGAEA.776054?format=textfile
2. Save the page as `data/raw/GeoB130124_full.tab` (plain text, tab-delimited)
3. Go to https://doi.pangaea.de/10.1594/PANGAEA.776055?format=textfile
4. Save the page as `data/raw/GeoB130106_full.tab`
5. Or use the "Download ZIP" button on https://doi.pangaea.de/10.1594/PANGAEA.776056
   which bundles all 15 related datasets (includes calibration/figure data too).

### Columns (real, as published)

| Column | Meaning | Unit |
|---|---|---|
| Latitude, Longitude | Position along profile | decimal degrees |
| Distance | Distance along profile track | m |
| Depth water | Water depth | m |
| kappa (col 5) | Raw magnetic susceptibility (sensor output) | 10⁻⁶ SI |
| Poros | Porosity (derived via Archie's law) | % vol |
| Sal | Salinity | (unitless practical salinity) |
| kappa (col 8) | Magnetic susceptibility of sediment matrix (corrected) | 10⁻⁶ SI |
| <63 µm | Clay + silt content (grain size fraction) | category (e.g. "<5%") |
| Seafloor und. | Seafloor undulation (high-pass filtered bathymetry) | m |

**Important:** this dataset gives magnetic susceptibility directly, but does
NOT give a direct bulk electrical conductivity column — conductivity is
implied through porosity + salinity (via Archie's Law, noted in the dataset
comment: m=1.6, a=1, +14.4% offset). Our feature engineering step
(`src/feature_engineering.py`) derives an apparent conductivity feature from
Poros + Sal using Archie's Law, documented inline with the formula and
citation, since this is standard practice in marine geophysics and is
explicitly signposted by the original authors.

## Secondary / validation reference (objective 3)

For cross-referencing whether unsupervised clusters land near real known
mineral-rich zones, candidate sources (to evaluate once clustering is done):

- NOAA/NGDC Marine Minerals (MMS) geochemical database — ferromanganese
  nodule/crust analyses compiled from Scripps, CNEXO, USGS.
- Published SMS/nodule site coordinates from literature (e.g. TAG hydrothermal
  mound, Clarion-Clipperton Zone nodule fields) — NOT from the same survey
  region as our primary dataset (NW Iberian shelf), so this is a
  supplementary/illustrative cross-check only, not a strict ground truth for
  this specific survey.

**Honest limitation to state in the report:** the NW Iberian shelf profile is
a sediment-characterization survey, not a known mineral-deposit exploration
site. If no legitimate external deposit-ground-truth exists for these exact
coordinates, objective 3 will be validated using internal clustering metrics
(silhouette score, Davies-Bouldin index) instead of forcing an external match
that doesn't really apply. This should be stated plainly in the final report
as a scoping decision, not hidden.

## Citation requirement

CC-BY-3.0 requires attribution. Always cite:

> Müller, H., von Dobeneck, T., Hilgenfeldt, C., SanFelipo, B., Rey, D.,
> Rubio, B. (2012): Mapping the magnetic susceptibility and electric
> conductivity of marine surficial sediments by benthic EM profiling.
> Geophysics, 77(1), E43-E56. https://doi.org/10.1190/GEO2010-0129.1
