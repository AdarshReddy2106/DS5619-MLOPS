# NOTES.md — Week 2: Config-Driven Data Pipelines

**Student ID used with `generate_for_student.py`:**
student_id: 102301018
<!-- seed: 1319725832 -->

## What was hardcoded, and what would switching it have required?

- The original script hardcoded the input path as data/v1/transactions.csv, the high-value threshold as 5000, and the output path as data/v1/report_hardcoded.json.
- The input format was also hardcoded because the pipeline used a load_csv() function directly.
- To change the high-value threshold, the HIGH_VALUE_THRESHOLD value in the Python source had to be modified.
- To switch from CSV to JSON, the data-loading implementation had to be changed because only CSV loading was supported.
- The refactored pipeline moves the input path, format, threshold, and output path into YAML configuration.
- This allows the same pipeline code to run with different formats, thresholds, and output locations without modifying src/pipeline.py.