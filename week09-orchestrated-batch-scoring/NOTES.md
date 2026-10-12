# NOTES.md — Week 9: Orchestrated Batch Scoring

**Student ID used with `generate_for_student.py`:**
102301018
seed: 164430207


## notify retry count

`notify` took **3 attempts** (1 initial attempt + 2 retries) to succeed in the run, as recorded in `dag_run_summary.json` (`attempts: 3`). The simulated transient failures occurred on attempts 1 and 2 before succeeding on attempt 3.


## Branch independence

`load` succeeded because `load` and `notify` are **sibling tasks** that both depend only on `score`. Neither depends on the other. Once `score` completed successfully and populated the shared context, both branches became eligible to run. Because `load` ran before `notify` in our topological order, it completed its work (writing `batch_report.json`) before `notify` even began failing.

Even in a concurrent orchestrator where both tasks run in parallel, failures in one branch of a DAG should only block tasks strictly **downstream** of that failure (its transitive dependents). Sibling branches and independent paths should not be blocked or failed. This fault isolation ensures that essential operations (e.g., persisting scored batches to disk or database) succeed regardless of transient issues in auxiliary tasks (e.g., Slack or webhook notifications).


## Retry cost under FinOps

If `notify` were a metered API call billed per request (e.g., third-party SMS/webhook gateway or pay-per-token API), the retry strategy should be modified in several ways:
1. **Reduce Maximum Retries:** Cap attempts to 1 or 2 rather than aggressive retry loops.
2. **Error Classification:** Only retry on transient/recoverable status codes (e.g., HTTP 429 rate limits, 503 service unavailable). Never retry client/deterministic errors (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden) where retries will always fail while burning money.
3. **Exponential Backoff with Jitter:** Prevent wasted requests against overloaded services by backing off exponentially.
4. **Circuit Breakers / Dead-Letter Queues:** Halt retries after consecutive failures to protect the cloud budget.

**Why "retry every failed task the same way" is a risky default once cost enters the picture:**
In classical software, task retries consume local CPU cycles on fixed infrastructure. In cloud-native MLOps and FinOps, tasks frequently invoke external metered services, GPU instances, or serverless functions where each invocation incurs a direct marginal financial cost. A naive, uniform retry policy acts as a cost multiplier during downstream outages, burning budget on requests doomed to fail. Retry strategies must therefore be cost-aware, weighing the business criticality of the task against the financial liability of repeated attempts.
