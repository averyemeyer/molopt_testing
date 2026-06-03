# Table Guide

## Main 10K Tables

- `metrics_full_qed_logp_sascore.csv` - one row per seed run with final top1,
  top10, top100, best score, max oracle call, and AUC-top10.
- `metrics_full_qed_logp_sascore.md` - markdown version of the same metrics.
- `full_qed_logp_sascore_top1_thresholds.csv` - oracle calls needed for the
  mean top1 curve to reach target values.
- `full_qed_logp_sascore_top10_thresholds.csv` - oracle calls needed for the
  mean top10 curve to reach target values.
- `full_qed_logp_sascore_top100_thresholds.csv` - oracle calls needed for the
  mean top100 curve to reach target values.

## Medium Matrix Tables

- `coverage_medium.csv` / `coverage_medium.md` - completion coverage for the
  medium cheap-oracle matrix.
- `validation_medium.csv` - result file sanity checks.
- `audit_medium_scores.csv` - recomputed oracle-score audit.
- `metrics_medium.csv` / `metrics_medium.md` - final top-k and AUC metrics for
  medium runs. This includes the completed cheap-oracle matrix plus the partial
  medium hERG slice.
