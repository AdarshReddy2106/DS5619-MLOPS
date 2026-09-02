# NOTES.md — Week 5: Model Registry Governance

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
student_id: 102301018
seed: 991074289
candidate_a: f1=0.477 (below 0.70 bar)
candidate_b: f1=0.816 (clears 0.70 bar)

## Which candidate reached Production, and why?

Candidate B reached Production because its F1 score was 0.816, above the
0.70 threshold, and it had a completed model card. Candidate A was blocked:
its F1 score was 0.477, even after its model card was created.


## Gating stale feature data

I would record the feature-data creation time or age in the model manifest and
check it in promote_model. Production promotion should raise GovernanceError
when the recorded data age is greater than 30 days, or when the metadata is
missing or cannot be verified.


## Scaling the gate to 40 candidates

The design already supports 40 candidates because register_model assigns each
candidate a separate version and promote_model evaluates one version at a
time. The pipeline would need to register all 40 candidates and apply the
same card and metric gates to each; no special two-candidate logic is needed.
