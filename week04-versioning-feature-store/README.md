# Lab 4 — Versioning, Feature Store & Lineage

**Track A (tabular fraud-detection) · Week 4 · DS5619 Machine Learning Systems Operations**

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python generate_for_student.py --student-id <your roll number or institute email>
```

This overwrites `data/v1/transactions.csv` and `data/v2/transactions.csv` with
records generated deterministically from your student ID 

Do not manually edit these CSV files.

## Functions
All four functions are in `src/mini_feature_store.py`.

### `snapshot_raw_version(input_path, registry_dir)`

- Calculates a SHA-256 hash of the input file.
- Reuses the existing version ID when the same file content was registered.
- Creates a new version for new file content.
- Writes a raw-data manifest containing the path, hash, columns, row count, and creation time.

### `build_features(rows)`

- Accepts either the v1 or v2 transaction schema.
- Detects v2 using `country_code` and `amount_minor_units`.
- Converts v2 cents to normal currency units by dividing by 100.
- Groups transactions by `card_id`.
- Calculates transaction count, average amount, maximum amount, card-present, percentage, and latest event time.

### `register_feature_group(name, feature_rows, source_version_id, registry_dir, transform_version)`

- Creates a new feature-group version for every registration.
- Saves the feature rows in `features.json`.
- Saves a manifest containing the schema, row count, transform version, and source raw version.
- Never overwrites an earlier feature-group version.

### `get_lineage(name, fg_version_id, registry_dir)`

- Reads the selected feature-group manifest.
- Finds the raw version recorded in `source_raw_version_id`.
- Reads that raw manifest.
- Returns both manifests as one lineage dictionary.


Run the complete pipeline from this directory:
```bash
python src/run_pipeline.py
```

This runs your four functions against v1, then v2, checks that re-snapshotting
v1 is idempotent, and writes `lineage_report.json` at the repo root
(`src/run_pipeline.py` is complete, don't edit it).

## Self-check

```bash
pytest tests/ -q
```

