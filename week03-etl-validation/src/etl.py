"""
Extract -> Validate -> Transform -> Load pipeline for the fraud transaction
data. Run with:

    python src/etl.py --config config.yaml

(a default config.yaml pointing at data/raw_transactions.csv is provided)
"""
import argparse
import csv
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import expectations as exp

KNOWN_CATEGORIES = {
    "grocery", "electronics", "fuel", "travel", "restaurant",
    "online_retail", "utilities", "pharmacy", "entertainment", "atm_withdrawal",
}


def build_expectation_suite():
    """The data contract for this dataset. Each entry says which expectation
    function to run, and with what arguments. This is provided — read it to
    know exactly what your expectation functions in expectations.py need to
    handle correctly.
    """
    return [
        (exp.expect_column_not_null, {"column": "amount"}),
        (exp.expect_column_not_null, {"column": "card_id"}),
        (exp.expect_column_positive, {"column": "amount"}),
        (exp.expect_column_in_set, {"column": "merchant_category", "allowed_values": KNOWN_CATEGORIES}),
        (exp.expect_column_unique, {"column": "transaction_id"}),
    ]


def extract(input_path):
    with open(input_path, newline="") as f:
        return list(csv.DictReader(f))


def run_etl(config):
    """Implement the four ETL steps described in ASSIGNMENT.md:
    extract, validate (run every expectation in build_expectation_suite()
    and collect ALL violations, not just the first), transform (split into
    clean vs quarantined rows — a row with ANY violation is quarantined),
    load (write clean_output_path, quarantine_output_path, and
    report_output_path as described in the assignment).

    Return the validation_report dict as well as writing it to disk.
    """

    # Extraction
    rows = extract(config["input_path"])

    # Validate

    suite = build_expectation_suite()
    all_violations  = []
    for expectation_function, argument in suite:
        violations  = expectation_function(rows,**argument) 
        # **arguments unpacks the dictionary and pass its contents as arguments. 
        # ex: expectation_function(rows, column="amount")
        all_violations.extend(violations) 
        # collecting all violations in to a single list

    bad_row_indices = set()

    for violation in all_violations:
        bad_row_indices.add(violation.row_index)

    clean_rows = []
    quarantined_rows = []

    for index, row in enumerate(rows):
        if index in bad_row_indices:
            quarantined_rows.append(row)

        else:
            clean_rows.append(row)

    
    # writing to csv files

    with open(config["clean_output_path"], "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(clean_rows)


    with open(config["quarantine_output_path"], "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(quarantined_rows)

    # summary
    expectation_results = {}

    for violation in all_violations:
        expectation = violation.expectation
        column = violation.column
        key = f"{expectation}_{column}"

        if key not in expectation_results:
            expectation_results[key] = {
                "expectation": expectation,
                "column": column,
                "n_violations": 0,
                "row_indices": []
            }

        expectation_results[key]["n_violations"] += 1
        expectation_results[key]["row_indices"].append(violation.row_index)

    validation_report = {
        "expectations": list(expectation_results.values())
    }

    with open(config["report_output_path"], "w") as f:
        json.dump(validation_report, f, indent=2)
    
    return validation_report



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    report = run_etl(config)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
