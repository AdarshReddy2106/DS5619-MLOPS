# NOTES.md — Week 3: ETL and Data Validation

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
student_id: 102301018
seed: 2941626828
Wrote 600 rows (7 known violations, positions vary per student)

## Quarantine count vs. the 7 known injected problems (mentioned in generate_for_student.py)

<!-- How many rows ended up quarantined, and does that match the 7 known
     injected problems? (It won't match exactly — some rows may trip more
     than one expectation. Explain the discrepancy if there is one.) -->

**Rows quarantined**: 6 distinct rows

**Violations found**: 8 total violations across all expectations
- 2 null amounts (rows 137, 346)
- 1 null card_id (row 95)
- 1 negative amount (row 406)
- 1 bad merchant category (row 214)
- 1 duplicate transaction_id (row 388)

We found 6 quarantined rows but expected 7 injected violations. The reason is that the bad country code violation is NOT being caught because the expectation suite does not include a validation for the `country` column. The suite only validates: `amount`, `card_id`, `merchant_category`, and `transaction_id`. 

The 8 violations reported (vs. 7 expected) occurs because rows 137 and 346 (with null amounts) trigger BOTH the `expect_column_not_null` check AND the `expect_column_positive` check, counting as 2 violations each.
