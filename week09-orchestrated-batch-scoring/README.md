# Lab 9 — Orchestrated Batch Scoring

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python generate_for_student.py --student-id 102301018
```

This overwrites `data/fixtures/` with personalized synthetic CCTV images — 40 images across two camera profiles (`camera_A_daylight` and `camera_B_lowlight`) along with `_annotations.coco.json`, generated deterministically from the student ID (seed: `164430207`).

## Architecture & Background

Batch scoring pipelines in production are structured as Directed Acyclic Graphs (DAGs) rather than sequential scripts. Upstream stages (data extraction and inference) must produce intermediate state before downstream consumers (storage loaders and notification hooks) can operate.

The batch-scoring pipeline implements the following DAG:

```
extract ──▶ score ──┬──▶ load
                    └──▶ notify
```

- **`extract`**: Discovers and lists all input images in `data/fixtures/`.
- **`score`**: Runs the mock object detector across each image and accumulates vehicle detection counts into a shared context dictionary.
- **`load`**: Writes the final `batch_report.json` summarizing images scored and per-image detection counts (depends on `score`).
- **`notify`**: Simulates an external webhook/Slack notification (depends on `score`). It intentionally encounters transient failures on its first two attempts and succeeds on the third to exercise retry logic in a live run.

## Task Implementation

All orchestrator logic was implemented in `src/mini_orchestrator.py`:

### 1. Topological Sorting (`topological_order`)

Implemented dependency resolution using **Kahn's Algorithm**:
* **Dependency Validation**: Checks all task definitions in `tasks`; raises a `ValueError` if a task specifies an unknown or missing dependency.
* **In-degree Tracking**: Computes the number of incoming edges (dependencies) for each task.
* **Frontier Processing**: Iteratively extracts tasks with `in_degree == 0`, appends them to the execution order, and decrements the in-degree of all downstream dependent tasks.
* **Cycle Detection**: If the queue empties before all tasks are placed, raises a `ValueError` indicating a cyclic dependency.
* **Branching DAG Support**: Correctly orders branched graphs, ensuring parents always precede their dependent children.

### 2. Task Execution with Retries (`run_task_with_retry`)

Implemented a resilient task execution loop for handling transient failures:
* Allows up to `task.max_retries` additional attempts (`1 + max_retries` total attempts).
* Introduces a pause of `task.retry_delay_seconds` using `time.sleep()` between failed attempts.
* Returns the total attempt count upon eventual success (e.g., `1` on first attempt, `3` if succeeded on the 2nd retry).
* Re-raises the last caught exception if all retry attempts are exhausted without swallowing the traceback.

### 3. DAG Orchestration Engine (`run_dag`)

Implemented end-to-end execution of the dependency graph:
* Determines execution order via `topological_order(tasks)`.
* Instantiates and propagates a shared `context` dictionary across tasks, allowing downstream tasks (like `load`) to access artifacts produced upstream (like `score`).
* Executes each scheduled task via `run_task_with_retry()`, recording metadata (`status`, `attempts`, and `error` if failed).
* Implements **fail-fast gating**: if an unrecoverable failure occurs, execution immediately stops, preventing downstream tasks from running on invalid or missing state.

## Verification

### Unit Testing

The implementation was validated using the test suite:

```bash
pytest tests/ -q
```

All 10 tests passed successfully

### Pipeline Execution

The complete pipeline driver was executed:

```bash
python src/run_pipeline.py
```

Which produced the following output:

```
Execution order: ['extract', 'score', 'load', 'notify']
  extract: {'status': 'success', 'attempts': 1}
  score: {'status': 'success', 'attempts': 1}
  load: {'status': 'success', 'attempts': 1}
  notify: {'status': 'success', 'attempts': 3}
Wrote D:\ACADEMICS\SEM 7\DS5619-MLOPS\week09-orchestrated-batch-scoring\dag_run_summary.json
```

### Artifacts Produced

1. **`batch_report.json`**:
   - `images_scored`: 40
   - `total_detections`: 173
   - Complete breakdown of detected vehicle counts across all images.

2. **`dag_run_summary.json`**:
   - Records the topological execution order `['extract', 'score', 'load', 'notify']`.
   - Confirms `extract`, `score`, and `load` succeeded on attempt 1.
   - Confirms `notify` recovered on attempt 3 after 2 simulated transient failures.
