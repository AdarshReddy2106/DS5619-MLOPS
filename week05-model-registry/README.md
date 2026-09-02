# Lab 5 — Model Registry Governance

**Track A (tabular fraud-detection) · Week 5 · DS5619 Machine Learning Systems Operations**

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python generate_for_student.py --student-id <your roll number or institute email>
```

The generator creates personalized files in `data/candidate_a/` and
`data/candidate_b/`. Candidate A is deliberately below the F1 requirement;
candidate B is deliberately above it. Record the same student ID in
`NOTES.md`; the grader uses it to regenerate and verify your data.

## Learning Objective

This lab builds a small local model registry using JSON files instead of an
MLflow or W&B server. The registry demonstrates three practical ideas:

1. **Artifact identity:** each registered model gets its own immutable version.
2. **Governance evidence:** each model can have a model card describing its
   intended use, data, limitations, and ethical considerations.
3. **Promotion gates:** Production requires both a complete model card and an
   F1 score of at least `0.70`.

The registry answers “what is currently in Production?” from saved manifests,
not from memory or a chat message.

## Files

- `src/mini_model_registry.py` — implement the four registry functions.
- `src/run_pipeline.py` — complete driver script. Do not edit it.
- `model_card_fields.json` — replace every `TODO` with specific model-card content.
- `data/candidate_a/` and `data/candidate_b/` — generated model artifacts and metrics. Do not hand-edit these files.
- `.model_registry/` — generated version folders, manifests, and model cards.
- `registry_summary.json` — generated summary of the Production model.
- `NOTES.md` 

## Functions

All four functions are in `src/mini_model_registry.py`.

### `register_model(name, model_path, metrics, registry_dir)`

- Creates the next version under `registry_dir/models/{name}/`.
- Copies the JSON artifact to `model.json`.
- Writes `manifest.json` with the version, metrics, initial stage `"None"`, and creation time.
- Returns the new version ID.

### `generate_model_card(name, version_id, card_fields, registry_dir)`

- Requires every field listed in `REQUIRED_CARD_FIELDS`.
- Rejects missing, empty, or `TODO`-containing values.
- Writes the completed card and the registered metrics to `model_card.json`.

### `promote_model(name, version_id, target_stage, registry_dir)`

- Allows promotion to `Staging` without the Production gate.
- Allows promotion to `Production` only when a card exists and `metrics["f1"] >= PRODUCTION_F1_THRESHOLD`.
- Archives any other version currently in Production.
- Appends each successful stage change to the manifest history.

### `get_production_model(name, registry_dir)`

- Scans saved manifests for the version whose stage is `"Production"`.
- Returns that manifest, or `None` when no version is in Production.

## Complete the Model Card

Edit `model_card_fields.json` and replace all `TODO` placeholders 

`src/run_pipeline.py` checks for `TODO` before doing any registry work, so the
card must be completed first.

## Run the Pipeline

```bash
python src/run_pipeline.py
```

The script performs this sequence:

1. Registers candidate A and candidate B as separate model versions.
2. Attempts to promote candidate A without a card. The registry blocks it.
3. Creates candidate A's card and tries again. Its low F1 blocks it again.
4. Creates candidate B's card and promotes it to Production.
5. Writes `registry_summary.json` with the current Production version and
   metrics.

The two blocked promotions are expected output, not pipeline failures.

Inspect these outputs after the run:

- `.model_registry/models/fraud-detector/v*/manifest.json` — version, metrics,
  stage, and promotion history.
- `.model_registry/models/fraud-detector/v*/model_card.json` — governance
  evidence for each completed card.
- `registry_summary.json` — the current Production answer.

## Self-Check

```bash
pytest tests/ -q
```

The smoke tests check registration, model-card validation, both Production
gates, archival of the previous Production version, lookup, and the complete
pipeline.

## Deliverables

- Completed `src/mini_model_registry.py`.
- Completed `model_card_fields.json` with no `TODO` text.
- Personalized `data/candidate_a/` and `data/candidate_b/` files.
- Generated `.model_registry/` and `registry_summary.json`.
- `NOTES.md` containing:
  - your student ID;
  - which candidate reached Production and why;
  - how to add a stale-feature-data check for data older than 30 days;
  - whether the design can gate 40 candidates from an AutoML search.

## Submission

```bash
git add -A
git commit -m "Week 5: model registry governance"
git tag week05-submit
git push origin main --tags
```
