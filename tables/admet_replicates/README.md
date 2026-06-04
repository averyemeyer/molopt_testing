# ADMET Replicate Tables

Tables for the three-seed ADMET/toxicity follow-up scout.

- `metrics_admet_replicates.csv` / `.md`: final top1/top10/top100 and AUC-top10
  for each oracle, algorithm, and seed.
- `runtime_admet_replicates_by_oracle.csv`: elapsed time and estimated seconds
  per oracle call aggregated by endpoint.
- `curve_shape_notes.md`: short explanation of top1/top10/top100 behavior and
  why top100 can still show U-shaped curves at a 100-call budget.

All 75 expected runs succeeded: 5 endpoints x 5 algorithms x 3 seeds.
