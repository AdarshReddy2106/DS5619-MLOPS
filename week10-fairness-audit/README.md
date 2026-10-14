# Lab 10 — Fairness and Robustness Audit

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python generate_for_student.py --student-id 102301018
```

This overwrites `data/fixtures/` with personalized synthetic CCTV images — 60 images across two camera profiles (`camera_A_daylight` and `camera_B_lowlight`) along with `_annotations.coco.json`, generated deterministically from the student ID `102301018` (seed: `1406615973`).

The generator checks candidate datasets using the mock detector to ensure a clear recall disparity signal survives reseeding: small-vehicle classes (`Bicycle` and `Two-wheeler`) consistently fall below the 90% threshold while large-vehicle classes do not.

## Architecture & Background

Production machine learning systems must monitor performance parity across groups to detect systematic disparities before and during deployment. In this lab, we operationalize group-level fairness metrics and adversarial robustness auditing on the BMD-45 vehicle detection benchmark:

```
                      ┌──▶ Clean Fairness Audit (Per-Class Recall) ──▶ Underperforming Classes
Image Fixtures + COCO ┤
                      └──▶ FGSM Attack (Channel Perturbations)   ──▶ Robustness Degradation
```

- **Fairness Metric (Equal Opportunity / Per-Class Recall)**: Measures the true positive rate independently for each vehicle category:
  $$\text{Recall} = \frac{\text{Detected Ground-Truth Boxes}}{\text{Total Ground-Truth Boxes}}$$
  Boxes are matched using Intersection-over-Union ($\text{IoU} \ge 0.3$) against detector proposals regardless of class label accuracy.
- **A Note on Framing**: While vehicle class disparities indicate operational safety risks in traffic monitoring, the same statistical auditing methodology applies to protected demographic attributes (e.g., race, gender, age) where performance gaps represent systemic discrimination and legal civil rights liabilities.
- **Adversarial Robustness (White-Box L-$\infty$ Perturbation)**: The detector classifies pixels as reddish blobs using the decision boundary $r > 120$, $r - g > 40$, and $r - b > 40$. Because the rule is known, a white-box Fast Gradient Sign Method (FGSM) style attack shifts pixel values in the most damaging direction (lowering red by $\epsilon$, raising green and blue by $\epsilon$) across budgets $\epsilon \in [0, 10, 20, 30, 40]$ to assess how quickly each class degrades.

## Task Implementation

### 1. Fairness Audit Core (`src/fairness_audit.py`)

- **Intersection-over-Union (`compute_iou`)**:
  - Converts bounding boxes from `[x, y, w, h]` to `(x1, y1, x2, y2)` corner coordinates.
  - Clamps overlap dimensions to $\ge 0$ to prevent negative values on disjoint boxes.
  - Computes $\text{IoU} = \frac{\text{Area of Overlap}}{\text{Area of Union}}$, safely returning `0.0` when the union area is zero.

- **Ground-Truth Matching (`match_ground_truth`)**:
  - Evaluates whether each ground-truth box overlaps at least one detection with $\text{IoU} \ge \text{iou\_threshold}$ ($0.3$).
  - Returns a list of booleans of matching length and order, supporting multiple ground-truth associations.

- **Category-Level Audit (`audit_by_category`)**:
  - Loads COCO annotations, mapping images to ground-truth bounding boxes and categories.
  - Evaluates each image through the detector (applying an optional image transform when provided).
  - Accumulates total and detected box counts per category, rounding recall to 4 decimal places and skipping categories with zero instances.

- **Underperforming Category Identification (`find_underperforming_categories`)**:
  - Filters categories with recall strictly below `recall_threshold` ($0.90$).
  - Returns a list of `(category_name, recall)` tuples sorted worst-first (ascending recall).

### 2. Adversarial Robustness Check (`src/adversarial.py`)

- **FGSM-Style White-Box Perturbation (`perturb_image`)**:
  - Shifts channels using PIL's lookup-table point transforms: red is decreased by $\epsilon$, green and blue are increased by $\epsilon$.
  - Clamps all channel values strictly to $[0, 255]$ without mutating the input image.
  - Returns an identical copy when $\epsilon = 0$.

- **Audit Under Attack (`audit_under_attack`)**:
  - Iterates over perturbation budgets $\epsilon \in [0, 10, 20, 30, 40]$.
  - Leverages the `transform` parameter of `audit_by_category` to re-audit perturbed images, returning clean stats at $\epsilon = 0$.

- **Fragility Ranking (`find_most_fragile`)**:
  - Computes the recall drop for each category ($\text{recall}_0 - \text{recall}_\epsilon$) at a specified budget ($\epsilon = 20$).
  - Ranks categories by largest drop descending, applying an alphabetical tie-breaker on category names.

## Verification

### Unit Testing

The implementation was validated using the test suite:

```bash
pytest tests/ -q
```

All 13 tests passed successfully:

```
.............                                                            [100%]
13 passed in 11.17s
```

### Pipeline Execution

The complete pipeline driver was executed:

```bash
python src/run_pipeline.py
```

Which produced the following output:

```
Per-category recall:
  Bicycle             13/ 20 = 65.0% <-- below threshold
  Two-wheeler         13/ 16 = 81.2% <-- below threshold
  Other               14/ 16 = 87.5% <-- below threshold
  Sedan               15/ 16 = 93.8%
  Mini-bus            15/ 16 = 93.8%
  MUV                 16/ 17 = 94.1%
  Truck               16/ 17 = 94.1%
  Van                 17/ 18 = 94.4%
  Hatchback           11/ 11 = 100.0%
  SUV                 15/ 15 = 100.0%
  Bus                 18/ 18 = 100.0%
  Three-wheeler       13/ 13 = 100.0%
  LCV                 22/ 22 = 100.0%
  Tempo-traveller     19/ 19 = 100.0%

3 categories below 90% recall threshold.

Recall under attack (rows = classes, columns = eps [0, 10, 20, 30, 40]):
  Bicycle            0.65  0.50  0.35  0.20  0.10
  Two-wheeler        0.81  0.69  0.62  0.38  0.25
  Other              0.88  0.88  0.88  0.50  0.38
  Sedan              0.94  0.75  0.56  0.25  0.19
  Mini-bus           0.94  0.81  0.62  0.50  0.38
  MUV                0.94  0.82  0.82  0.76  0.47
  Truck              0.94  0.88  0.71  0.65  0.47
  Van                0.94  0.89  0.89  0.78  0.61
  Hatchback          1.00  1.00  0.73  0.64  0.55
  SUV                1.00  0.93  0.87  0.80  0.60
  Bus                1.00  0.94  0.89  0.56  0.44
  Three-wheeler      1.00  0.69  0.54  0.31  0.23
  LCV                1.00  0.86  0.77  0.55  0.45
  Tempo-traveller    1.00  0.95  0.79  0.68  0.53

Most fragile at eps=20: Three-wheeler (-46%), Sedan (-38%), Mini-bus (-31%)
Lowest recall at that budget: Bicycle (35%), Three-wheeler (54%), Sedan (56%)
Wrote fairness_report.json
```

### Artifacts Produced

1. **`fairness_report.json`**:
   - Clean audit results across all 14 categories.
   - Identified underperforming categories: `Bicycle` (65.0%), `Two-wheeler` (81.25%), and `Other` (87.5%).
   - Matrix of per-class recall under adversarial attack across $\epsilon \in [0, 10, 20, 30, 40]$.
   - Most fragile classes at $\epsilon = 20$: `Three-wheeler` (-46.15%), `Sedan` (-37.50%), `Mini-bus` (-31.25%).
   - Lowest recall under attack at $\epsilon = 20$: `Bicycle` (35.0%), `Three-wheeler` (53.85%), `Sedan` (56.25%).

2. **`NOTES.md`**:
   - **Student ID**: `102301018` (Seed: `1406615973`).
   - **Flagged Class Analysis**: Distinguishes structural small-object disparity (`Bicycle`, `Two-wheeler`) from sample-size noise (`Other`).
   - **Protected Demographic Framing**: Contrasts technical failure stakes with civil rights liability and mandatory pre-deployment gates.
   - **Lifecycle Attack & Control**: Formulates an evaluation-set data poisoning attack and its cryptographic checksum / immutable versioning control.
   - **SHAP/LIME Analysis**: Investigates missed Bicycle annotation 83 in image 21 (19 reddish pixels vs. 20-pixel threshold) and explains why SHAP/LIME fail on false negatives.
   - **Robustness Trade-offs**: Details why absolute recall under attack is a better harm metric than recall drop, outlines mitigation strategies (input validation, adversarial training), and compares rule-based sensitivity to CNN feature representations.
