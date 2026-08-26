# NOTES.md — Week 4: Versioning, Feature Store & Lineage

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
student_id: 102301018
seed: 1267684190
Wrote 500 v1 records -> /home2/mlops/DS5619-MLOPS/week04-versioning-feature-store/data/v1/transactions.csv
Wrote 125 v2 records -> /home2/mlops/DS5619-MLOPS/week04-versioning-feature-store/data/v2/transactions.csv

## v1 vs. v2 manifest comparison

- v1 and v2 have different feature-group version IDs.
- They also have different source raw version IDs.
- Both use transform version `v1` and the same feature schema.
- v1 has 388 feature rows, while v2 has 119 feature rows.
- The difference is because the input files contain different numbers of distinct cards.
- The raw manifests have different content hashes and schemas.
- v2 uses `country_code`, `amount_minor_units`, and `device_fingerprint`.


## Why treat amount_minor_units differently from amount?

- v1 `amount` is already expressed in normal currency units.
- v2 `amount_minor_units` is expressed in cents.
- `build_features` divides v2 values by 100.
- This conversion happens before calculating averages and maximums.
- Without conversion, v2 features would be 100 times larger than v1 features.
- Therefore, conversion is necessary for fair comparison between versions.
