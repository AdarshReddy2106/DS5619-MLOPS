# Lab 8 — Drift and Observability Monitoring

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python generate_for_student.py --student-id 102301018
```

This overwrites data/fixtures/ with your own synthetic CCTV images — same file names, same two
camera profiles, always at least one detectable "vehicle" per image, generated deterministically from
your student ID.

## Task Implementation

### Feature Extraction

Implemented `extract_confidence_scores()` to collect all detection confidence scores from a camera directory.
* Finds all `.jpg` images in the directory using `glob.glob()`, sorted for determinism.
* Opens each image using `Image.open(path).convert("RGB")`.
* Runs the mock detector using `det.detect(image)`.
* Collects `d.score` from each detection into a flat list.

This gives us the feature distribution that we monitor for drift.

### Population Stability Index

Implemented `compute_psi()` to quantify drift between a reference and live score distribution.
* Splits the `[0.0, 1.0]` range into `n_bins` (default 10) equal-width bins.
* Computes the proportion of reference and live scores falling in each bin.
* Clamps each proportion to a minimum of `1e-4` to avoid division by zero or `log(0)`.
* Calculates PSI using the formula: `sum((live_pct - ref_pct) * ln(live_pct / ref_pct))`.

A PSI of 0 means the distributions are identical; larger values indicate more drift.

### Drift Classification

Implemented `classify_drift()` to map a PSI value into an actionable label.
* `PSI < 0.10` → `"none"` (No meaningful drift)
* `0.10 <= PSI < 0.25` → `"moderate"` (Drift detected, worth investigating)
* `PSI >= 0.25` → `"significant"` (Major drift, immediate action required)

### Summary Statistics

Implemented `summarize_scores()` to compute descriptive statistics for a score distribution.
* Returns a dict with `count`, `mean`, `std`, `min`, and `max`.
* All values rounded to 4 decimal places (except count).
* Uses `statistics.mean()` and `statistics.stdev()`, with `std = 0.0` when fewer than 2 scores.

## Verification

The implementation was verified by running the test suite:

```bash
pytest tests/ -q
```

All 9 tests passed successfully, validating each function independently.

The full pipeline was then executed:

```bash
python src/run_pipeline.py
```

Which produced the following output:

```
Reference (camera_A_daylight): {'count': 67, 'mean': 0.9763, 'std': 0.0302, 'min': 0.733, 'max': 0.98}
Live (camera_B_lowlight): {'count': 75, 'mean': 0.9739, 'std': 0.0527, 'min': 0.524, 'max': 0.98}
PSI = 0.139 -> drift level: moderate
Wrote drift_report.json
```

The PSI of 0.139 falls in the **moderate** band, confirming that the confidence-score distribution shifted noticeably between the daylight and low-light camera profiles — as expected.
