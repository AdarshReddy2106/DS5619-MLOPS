"""
A minimal, from-scratch expectations framework in the spirit of Great
Expectations / data contracts (this week's lecture). You are implementing
the checking logic yourself rather than importing a library — the goal is
to understand what these tools actually do under the hood.

Fill in the four functions marked # TODO. Do not change the Violation
dataclass or any function signature.
"""
from dataclasses import dataclass


@dataclass
class Violation:
    expectation: str      # name of the check, e.g. "expect_column_not_null"
    column: str            # which column it was checking
    row_index: int          # index into the rows list where it failed
    detail: str              # short human-readable reason


def _is_null(value):
    return value is None or (isinstance(value, str) and value.strip() == "")


def expect_column_not_null(rows, column):
    violations = []

    """Return a Violation for every row where rows[i][column] is null/empty."""
    for index, row in enumerate(rows):
        if _is_null(row[column]):
            violations.append(
                Violation(
                    "expect_column_not_null",
                    column,
                    index,
                    "Value is Null/Empty"
                )
            )

    return violations



def expect_column_positive(rows, column):
    violations = []
    """Return a Violation for every row where rows[i][column], cast to float,
    is not strictly greater than 0. If the value can't be cast to float at
    all, that also counts as a violation (detail should say so).
    """
    for idx, row in enumerate(rows):
        try:
            curr = float(row[column])
            if curr<=0:
                violations.append(
                    Violation(
                        "expect_column_positive",
                        column,
                        idx,
                        "Value can't cast to float"
                    )
                )
            
        except ValueError or TypeError:
            violations.append(
                Violation(
                    "expect_column_positive",
                    column,
                    idx,
                    "Value is less than or equal to zero"
                )
            )

    return violations

def expect_column_in_set(rows, column, allowed_values):
    """Return a Violation for every row where rows[i][column] is not a member
    of allowed_values (a set or list you're given).
    """
    violations = []

    for idx , row in enumerate(rows):
        if row[column] not in allowed_values:
            violations.append(
                Violation(
                    "expect_column_in_set",
                    column,
                    idx,
                    "Value is not a member of allowed values"
                )
            )

    return violations


def expect_column_unique(rows, column):
    """Return a Violation for every row AFTER THE FIRST that repeats a value
    already seen in `column`. (i.e. if three rows share a value, rows 2 and 3
    are violations; row 1 is not.)
    """
    violations = []
    values = set()

    for idx, row in enumerate(rows):
        if row[column] not in values:
            values.add(row[column])

        else:
            violations.append(
                Violation(
                    "expect_column_unique",
                    column,
                    idx,
                    "Value is already seen."
                    )
            )

    return violations
