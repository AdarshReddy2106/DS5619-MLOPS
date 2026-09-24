# NOTES.md — Week 7: CI/CD Integration Testing

**Student ID used with `generate_for_student.py`:**
student_id: 102301018
seed: 3284272033

## Why gate integration-test on needs: [lint, unit-test]?

<!-- Why does integration-test need needs: [lint, unit-test] instead of
     just running in parallel with them — what's the actual cost being
     avoided? -->
Running `integration-test` only after `lint` and `unit-test` pass avoids the significant compute cost and time of building a Docker container, pulling base images, and running a heavier test sequence for code that is already known to be broken (e.g. failing a simple unit test or not conforming to linting rules). It acts as a fast-fail mechanism to save CI minutes.
