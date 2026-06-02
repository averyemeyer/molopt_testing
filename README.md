# MolOpt Testing Benchmarks

Curated benchmark record for the LIDDIA/MolOpt optimizer tests prepared on
2026-06-02.

This repository is intentionally small: it keeps the scripts, configs, plots,
tables, and summary without committing the full raw MolOpt result tree.

## What Is Included

- `summary_2026-06-02.md` - main narrative summary and takeaways
- `RESULTS_INDEX.md` - where to find plots, tables, scripts, logs, and analyses
- `oracle_time_run_analysis_2026-06-02.md` - oracle-call thresholds plus
  time/resource estimates
- `plots/medium/` - medium 1K cheap-oracle top10 comparison plots
- `plots/full/` - full 10K QED/LogP/SAScore pilot plots, including top1,
  top10, and top100 views
- `tables/` - coverage, validation, audit, and metrics tables
- `configs/` - YAML benchmark configs used for the runs
- `scripts/` - runner, oracle, plotting, validation, and audit scripts
- `inputs/zinc_sanity_1k.smi` - 1,000-SMILES starter set
- `logs/` - selected Slurm stdout/stderr logs for provenance

## Benchmark Scope

Main completed runs:

- Medium cheap LIDDIA matrix:
  - 8 cheap oracles
  - 11 available/default algorithms
  - 3 seeds
  - 1,000 oracle calls
- Full 10K pilot:
  - Oracles: QED, LogP, and SAScore
  - Algorithms: screening, Graph GA, SMILES GA, STONED, GPBO
  - 5 seeds
  - 10,000 oracle calls

## Key Takeaway

The optimizer stack can follow the supplied oracle signal, but raw physchem
oracles are often exploitable. For lead-optimizer integration, raw descriptors
such as molecular weight, LogP, TPSA, HBA/HBD, and rotatable bonds should usually
be wrapped as desirability or constrained objectives rather than naively
maximized.

For tool-routing guidance, use `top10` as the main shortlist-quality metric,
`top1` for single-hit discovery, and `top100` for broader pool improvement.
