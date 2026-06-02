# MolOpt Testing Benchmarks

Curated benchmark record for the LIDDIA/MolOpt optimizer tests prepared on
2026-06-02.

This repository is intentionally small: it keeps the scripts, configs, plots,
tables, and meeting summary needed to explain the benchmarking process and
takeaways without committing the full raw MolOpt result tree.

## What Is Included

- `pi_meeting_summary_2026-06-02.md` - main narrative summary and takeaways
- `plots/medium/` - medium 1K cheap-oracle top10 comparison plots
- `plots/full/` - full 10K QED/LogP pilot plots
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
  - Oracles: QED and LogP
  - Algorithms: screening, Graph GA, SMILES GA, STONED, GPBO
  - 5 seeds
  - 10,000 oracle calls

In-progress at initial commit:

- Full 10K SA-score pilot, Slurm job `5458061`

## Key Takeaway

The optimizer stack can follow the supplied oracle signal, but raw physchem
oracles are often exploitable. For lead-optimizer integration, raw descriptors
such as molecular weight, LogP, TPSA, HBA/HBD, and rotatable bonds should usually
be wrapped as desirability or constrained objectives rather than naively
maximized.

