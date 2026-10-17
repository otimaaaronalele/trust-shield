## Model and evaluation (DS1)

**Data:** PaySim synthetic mobile money dataset (Kaggle). License: see the dataset's Kaggle page [LINK AND LICENSE TO BE ADDED BY TEAM].
**Rows used:** CASH_OUT and TRANSFER only: 2,770,409 rows, 8,213 fraud (0.2965%).

**Split (by time step, not random):**
  train: steps 1-482, 2,636,285 rows, 5,379 fraud
  validation: steps 483-594, 82,838 rows, 1,180 fraud
  test: steps 595-743, 51,286 rows, 1,654 fraud

**Model:** LightGBM, 1 boosting rounds (early stopping on validation).
**Features (all available before approval):** is_transfer, amount, oldbalanceOrg, oldbalanceDest, amount_to_old_balance, amount_exceeds_balance.
**Excluded:** newbalanceOrig, newbalanceDest and ledger discrepancy, because they exist only after the transaction.
**Threshold:** 0.00446, chosen on validation to meet a target false-positive rate of 0.50%.

**Test results (scored once):**

| TP | FP | FN | TN | Recall | Precision | FPR | F1 |
|----|----|----|----|--------|-----------|-----|----|
| 1654 | 215 | 0 | 49417 | 1.0 | 0.885 | 0.00433 | 0.939 |

**Limitations:** PaySim is synthetic and its fraud patterns are simple, so these figures do not represent real-world performance. The test set has 1654 fraud cases, so rates carry sampling uncertainty. Results are from a replay of completed records.

Commit: not in a git repo yet: commit, then rerun this cell    Run date: 2026-10-17

**Two-tier decision (test set):** Tier 1 rule (hold when the amount equals the origin balance): 1,596 holds, 1,596 fraud, 0 honest held. Tier 2 (model score at the chosen threshold, rule did not fire): 273 flagged for human review, 58 fraud, 215 honest (precision 0.2125). Combined: 1,654 of 1,654 fraud found, 215 honest held. The rule's perfect precision reflects how PaySim generates fraud and should not be expected on real data. Counts are at the test set's fraud rate of 3.23%.
