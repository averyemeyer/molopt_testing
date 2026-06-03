# Small ADMET Scout Tables

Key files:

- `metrics_small_admet_only.csv` - tox-only per-run metrics for 55 small ADMET
  runs: 5 endpoints x 11 algorithms x 1 seed.
- `metrics_small_admet_only.md` - markdown version of the same table.
- `small_admet_top10_thresholds.csv` - first oracle call where the mean top10
  curve reaches safety-score thresholds.

Interpretation:

- Higher score means safer/lower predicted toxicity because the wrapper uses
  `1 - predicted_toxicity_probability`.
- These are 100-call, one-seed scouts. Use them to decide which endpoint and
  algorithm combinations deserve medium-budget follow-up.
