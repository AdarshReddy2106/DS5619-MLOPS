# NOTES.md — Week 10: Fairness and Robustness Audit

**Student ID:** 102301018  
**Seed:** 1406615973

## Which classes got flagged?

The 0.90 recall audit flagged **Bicycle (0.650)**, **Two-wheeler (0.8125)**, and **Other (0.875)**. This is expected for Bicycle and Two-wheeler because the generator gives small vehicles the smallest box-size multipliers. `Other` is likely sampling noise because it has only 16 examples.

## If the grouping variable were a protected attribute

A systematic performance gap could create ethical, legal, financial, and safety risks. The audit would require representative data, bias analysis, deployment gates, continuous monitoring, documentation, and human appeal processes.

## Which attack could corrupt this audit?

**Attack:** Evaluation-data poisoning during dataset preparation or testing. An attacker could alter annotations or pixels to lower or inflate recall.  
**Control:** Hash and sign the dataset and annotations, store immutable versions, and verify provenance before running the audit.

## Would SHAP or LIME explain a missed detection?

No, not directly. A missed box has no confidence score or prediction for SHAP/LIME to explain. These tools could explain a surrogate, such as reddish-pixel count, but not why an absent box was never proposed.

Example: Bicycle annotation 83 in image 21 has an $8 \times 6$ box. Only 19 pixels satisfy the reddish rule, below the detector's 20-pixel minimum.

## What did your attack show?

- **Flagged-class trend:** Bicycle fell from 0.65 to 0.10; Two-wheeler from 0.8125 to 0.25; Other stayed at 0.875 through $\epsilon=20$ and fell to 0.375 at $\epsilon=40$.
- **Most fragile at $\epsilon=20$:** Three-wheeler (drop 0.4615), Sedan (0.3750), and Mini-bus (0.3125). None were clean-flagged.
- **Drop vs. absolute recall:** The rankings disagree. Lowest attacked recall was Bicycle (0.35), Three-wheeler (0.5385), and Sedan (0.5625). Absolute recall is the better harm measure because it reflects actual detection performance.
- **Cost:** Low-performing classes bear the greatest operational and safety cost because they start with more missed objects.
- **Mitigation:** Use illumination normalization, denoising, channel checks, stronger thresholds, and morphological cleanup. Learned detectors can also use adversarial training.
- **Rule vs. CNN:** The attack shifts pixel channels across fixed color thresholds. CNNs usually resist this better because they also use shapes, edges, and context.
