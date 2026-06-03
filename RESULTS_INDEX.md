# MolOpt Benchmark Results Index

This repository keeps a curated benchmark record rather than the full raw
MolOpt result tree. The most useful entry points are below.

## Narrative

- `summary_2026-06-02.md` - meeting-oriented summary and takeaways
- `oracle_time_run_analysis_2026-06-02.md` - explicit oracle-call, time, and
  resource analysis for planning future lead-optimizer runs

## Plots

- `plots/full/` - evaluator-backed 10K pilot plots for `qed`, `logp`, and `sascore`
  - Each oracle has `top1`, `top10`, and `top100` views.
  - `top1` asks whether the optimizer can find one standout molecule.
  - `top10` asks whether it can produce a robust shortlist.
  - `top100` asks whether it moves the broader candidate pool.
- `plots/medium/` - evaluator-backed 1K cheap-oracle matrix plots for the wider algorithm set.
- `plots/small_admet/` - completed 100-call ADMET/toxicity scout plots for
  hERG, DILI, ClinTox, mutagenicity, and carcinogenicity.

## Tables

- `tables/metrics_full_qed_logp_sascore.csv` - final top1/top10/top100 and
  AUC-top10 values for every completed 10K pilot seed.
- `tables/full_qed_logp_sascore_top1_thresholds.csv` - first oracle call where
  the mean top1 curve reaches each target threshold.
- `tables/full_qed_logp_sascore_top10_thresholds.csv` - same for top10.
- `tables/full_qed_logp_sascore_top100_thresholds.csv` - same for top100.
- `tables/part2_evaluator/` - evaluator-backed rescoring audit metrics and
  original-vs-part2 comparison tables.
- `tables/metrics_medium.csv` - medium 1K metrics: the completed cheap-oracle
  matrix plus the partial hERG slice.
- `tables/small_admet/` - tox-only metrics and threshold tables for the
  completed 55-run small ADMET scout.
- `tables/coverage_medium.*`, `tables/validation_medium.csv`, and
  `tables/audit_medium_scores.csv` - coverage and correctness checks for the
  medium cheap matrix.

## Scripts

- `scripts/run_molopt_oracle_tests.py` - benchmark runner. New future runs write
  `benchmark_run_metadata.json` sidecars with elapsed seconds and resource data.
- `scripts/summarize_molopt_metrics.py` - per-run final top-k and AUC tables.
- `scripts/summarize_molopt_thresholds.py` - call-to-threshold summaries.
- `scripts/plot_molopt_benchmark_tier.py` - multi-algorithm comparison plots.
- `scripts/liddia_oracles.py` - evaluator-backed LIDDIA oracle wrappers used
  in this benchmark. Raw physchem/toxicity values come from `evaluator.tools`;
  wrappers only adapt direction where MolOpt needs higher-is-better objectives.
- `scripts/rescore_molopt_results.py` - recompute saved MolOpt result scores
  with the current oracle wrappers while preserving original call numbers.

## Logs

- `logs/molopt-cfg-5455029.*` - completed full 10K QED/LogP pilot.
- `logs/molopt-cfg-5458061.*` - completed full 10K SAScore pilot.
- `logs/molopt-cfg-5454909.*` - medium hERG ADMET slice that timed out.
- `logs/molopt-cfg-5461356.*` - small ADMET scout log snapshot.
