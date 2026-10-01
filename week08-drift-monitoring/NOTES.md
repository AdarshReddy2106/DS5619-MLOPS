# NOTES.md — Week 8: Drift and Observability Monitoring

**Student ID used with `generate_for_student.py`:**
102301018
seed: 356059401

## Drift level vs. expectation
<!-- What drift level did the report show, and does that match what you'd expect given the two cameras were built with deliberately different visual statistics? -->

The report showed a **moderate** drift level (PSI = 0.139). This matches expectations because the two camera directories represent deliberately different visual conditions (daylight vs. lowlight). This variation in lighting shifts the distribution of the detector's confidence scores, leading to a moderate population stability index.

## What confidence-score-only monitoring misses
<!-- What would you monitor IN ADDITION to confidence score if you had access to ground-truth labels a day later? (Tie this to the kinds of drift from the lecture — which one does confidence-score-only monitoring miss?) -->

If ground-truth labels were available a day later, I would monitor actual model performance metrics (like accuracy, precision, recall) to detect **concept drift**. 

Monitoring only confidence scores captures *feature drift* (or data drift) — shifts in the input distributions. However, it completely misses *concept drift*, which occurs when the relationship between the inputs and the true labels changes (e.g., the model is still highly confident, but its predictions are now wrong). Performance metrics are necessary to catch this.
