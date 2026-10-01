# Lab 7 — CI/CD Integration Testing

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python generate_for_student.py --student-id 102301018
```

This overwrites `data/fixtures/` with personalized synthetic CCTV images — same file names, same two camera profiles, generated deterministically from the student ID. 

## Task Implementation

The goal of this lab was to write a Continuous Integration (CI) pipeline that gates merges by ensuring linting, unit tests, and integration tests all pass. This implements the "shift-left" philosophy, catching issues like a broken Dockerfile or a regression in the `/detect` endpoint before the code is deployed.

### CI Pipeline Configuration (`ci.yml`)

Implemented a GitHub Actions workflow `.github/workflows/ci.yml` that runs on pushes and pull requests:
* **Linting Job (`lint`)**: Runs `flake8` to enforce code style guidelines and catch syntax errors.
* **Unit Test Job (`unit-test`)**: Runs `pytest` to execute all isolated tests.
* **Integration Test Job (`integration-test`)**: Tests the actual built container. 
  * It includes a `needs: [lint, unit-test]` dependency. This ensures that the time-consuming and computationally expensive process of building a Docker image and running it is completely skipped if the faster, simpler `lint` or `unit-test` jobs fail.

### Integration Test Script (`integration_test.sh`)

Implemented the bash script `scripts/integration_test.sh` to handle the lifecycle of testing the containerized application:
* **Builds** the Docker container locally using the Dockerfile.
* **Runs** the container in detached mode (`docker run -d`), mapping port 8080.
* **Polls** the `/health` endpoint in a loop, waiting for the Flask API to start successfully.
* **Tests** the `/detect` endpoint using `curl` by sending a sample fixture image and checking if the JSON response contains `"detections"`.
* **Tears down** the container (`docker rm -f`) at the end of the script to clean up resources, regardless of whether the test passed or failed.

## Verification

The pipeline and script were verified both locally and on GitHub Actions:

### Local Self-check
The structural configuration of the CI pipeline and the integrity of the API was validated using `pytest`:
```bash
pytest tests/ -q
```

The integration script was also tested locally to ensure the container builds and responds:
```bash
chmod +x scripts/integration_test.sh
./scripts/integration_test.sh
```

### GitHub Actions Pipeline
Once verified locally, the code was pushed to GitHub. The Actions tab confirmed that all three jobs (`lint`, `unit-test`, `integration-test`) ran successfully, with the integration test waiting correctly for the first two jobs to complete. The URL for this green CI run was documented in `CI_VERIFICATION.md`.
