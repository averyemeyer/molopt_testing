# MolOpt Testing Benchmarks

This repository is a curated record of MolOpt benchmark runs used to inform
LIDDIA lead-optimizer agent integration.

The goal is not to declare one optimizer universally best. The goal is to learn
which MolOpt algorithms are useful for different LIDDIA oracle types, how much
they cost to run, and how the agent should describe or route them.

## Main Questions

1. Are the LIDDIA oracle wrappers defined consistently with the evaluator?
2. Which algorithms follow which oracle classes well enough to use as tools?
3. How many oracle calls and how much wall time are needed to reach useful
   scores?
4. Which objectives are safe desirability objectives, and which are raw
   properties that need constraints?
5. What caveats matter before exposing these optimizers to the lead-optimizer
   agent?

## Current Benchmark Scope

- Medium cheap-oracle matrix:
  - 8 cheap oracles
  - 11 algorithms
  - 3 seeds
  - 1,000 oracle calls
- Full cheap-oracle pilot:
  - `qed`, `logp`, `sascore`
  - 5 algorithms
  - 5 seeds
  - 10,000 oracle calls
- Small ADMET/toxicity scout:
  - `herg`, `dili`, `clintox`, `mutagenicity`, `carcinogens`
  - 11 algorithms
  - 1 seed
  - 100 oracle calls

All benchmark runs use the same 1,000-SMILES starter file:

```text
inputs/zinc_sanity_1k.smi
```

## Key Files

- `summary_2026-06-02.md` - plain-language summary and takeaways
- `RESULTS_INDEX.md` - where plots, tables, configs, logs, and scripts live
- `oracle_time_run_analysis_2026-06-02.md` - threshold/time/resource details
- `scripts/liddia_oracles.py` - evaluator-backed MolOpt oracle wrappers
- `plots/` - optimization curves
- `tables/` - metrics, threshold tables, and comparisons
- `configs/` - benchmark YAML configs
- `logs/` - selected Slurm stdout logs for provenance

## Short Takeaway

The algorithms can follow the supplied oracle signal. The larger integration
risk is oracle design: raw properties such as LogP, molecular weight, TPSA,
HBA/HBD, and rotatable bonds can be exploited if the agent asks MolOpt to
maximize them directly.

For lead-optimizer use, bounded desirability objectives and transformed safety
scores are safer defaults. Raw physicochemical properties should usually be
used as constraints, target ranges, or terms in a composite score.
