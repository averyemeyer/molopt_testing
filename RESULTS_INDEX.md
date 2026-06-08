# MolOpt Benchmark Results Index

This repository keeps a curated benchmark record rather than the full raw
MolOpt result tree. The most useful entry points are below.

## Agent-Facing Summary

- `agent_knowledge/molopt_benchmark_knowledge.yaml` - reviewed, human-editable
  benchmark facts and routing guidance
- `agent_knowledge/molopt_benchmark_knowledge.json` - generated machine-readable
  mirror for lead-optimizer code or retrieval
- `agent_knowledge/PROMPT_CONTEXT.md` - concise prompt-ready context
- `agent_knowledge/schema.json` - validation contract for the structured files

## Narrative

- `summary_2026-06-02.md` - meeting-oriented summary and takeaways
- `RUNNING.md` - clean-clone installation, local/Slurm execution, outputs, and
  post-processing commands
- `LOCAL_MOLOPT_CHANGES.md` - upstream commit and explanations for every
  reusable tracked-code change
- `oracle_time_run_analysis_2026-06-02.md` - explicit oracle-call, time, and
  resource analysis for planning future lead-optimizer runs
- `tool_runtime_comparison.md` - short comparison of MolOpt candidate
  generation, ADMET evaluation, and GeLLMO-C targeted generation

## Plots

- `plots/full/` - evaluator-backed 10K pilot plots for `qed`, `logp`, and `sascore`
  - Each oracle has `top1`, `top10`, and `top100` views.
  - `top1` asks whether the optimizer can find one standout molecule.
  - `top10` asks whether it can produce a robust shortlist.
  - `top100` asks whether it moves the broader candidate pool.
- `plots/medium/` - evaluator-backed 1K cheap-oracle matrix plots for the wider algorithm set.
  - Each oracle has `top1`, `top10`, and `top100` views.
- `plots/small_admet/` - completed 100-call ADMET/toxicity scout plots for
  hERG, DILI, ClinTox, mutagenicity, and carcinogenicity.
- `plots/admet_replicates/` - 3-seed, 100-call ADMET/toxicity follow-up plots
  for the selected algorithm subset.

## Tables

- `tables/metrics_full_qed_logp_sascore.csv` - final top1/top10/top100 and
  AUC-top10 values for every completed 10K pilot seed.
- `tables/full_qed_logp_sascore_top1_thresholds.csv` - first oracle call where
  the mean top1 curve reaches each target threshold.
- `tables/full_qed_logp_sascore_top10_thresholds.csv` - same for top10.
- `tables/full_qed_logp_sascore_top100_thresholds.csv` - same for top100.
- `tables/oracle_wall_time_estimates.csv` - estimated wall time per oracle for
  the completed 10K QED/LogP/SAScore pilot.
- `tables/part2_evaluator/` - evaluator-backed rescoring audit metrics and
  original-vs-part2 comparison tables.
- `tables/metrics_medium.csv` - medium 1K metrics: the completed cheap-oracle
  matrix plus the partial hERG slice.
- `tables/small_admet/` - tox-only metrics and threshold tables for the
  completed 55-run small ADMET scout.
- `tables/admet_replicates/` - metrics and runtime tables for the completed
  75-run ADMET replicate scout.
- `tables/molopt_generation_probe.csv` - generation/optimizer overhead from a
  near-zero-cost deterministic oracle.
- `tables/tool_runtime_comparison.csv` - compact cross-tool timing summary.
- `tables/coverage_medium.*`, `tables/validation_medium.csv`, and
  `tables/audit_medium_scores.csv` - coverage and correctness checks for the
  medium cheap matrix.

## Scripts

- `scripts/install_into_molopt.sh` - apply the compatibility patch and copy the
  curated harness/configs/starter set into a clean upstream clone.
- `scripts/run_molopt_oracle_tests.py` - benchmark runner. New future runs write
  `benchmark_run_metadata.json` sidecars with elapsed seconds and resource data.
- `scripts/time_direct_vs_oracle_admet.py` and
  `scripts/run_direct_vs_oracle_timing.sh` - same-resource direct evaluator
  versus wrapper timing.
- `scripts/run_generation_overhead_probe.slurm` - near-zero-cost MolOpt
  generation/optimizer timing launcher.
- `scripts/summarize_molopt_metrics.py` - per-run final top-k and AUC tables.
- `scripts/summarize_molopt_thresholds.py` - call-to-threshold summaries.
- `scripts/plot_molopt_benchmark_tier.py` - multi-algorithm comparison plots.
- `scripts/liddia_oracles.py` - evaluator-backed LIDDIA oracle wrappers used
  in this benchmark. Raw physchem/toxicity values come from `evaluator.tools`;
  wrappers only adapt direction where MolOpt needs higher-is-better objectives.
- `scripts/rescore_molopt_results.py` - recompute saved MolOpt result scores
  with the current oracle wrappers while preserving original call numbers.

## Reproducibility

- `environment/molopt-liddia.yml` - curated environment definition.
- `environment/molopt-liddia-pip-freeze.txt` - full June 8, 2026 working
  environment snapshot for provenance.
- `patches/mol-opt-compatibility.patch` - changes to `molopt/base.py`, MIMOSA,
  and SelfiesGA against upstream commit `63382d7`.
- `inputs/zinc_sanity_1k.smi` - matched starter set copied into
  `benchmark_inputs/` by the installer.

## Follow-Up Configs

- `configs/admet_replicates/` - separate 3-seed, 100-call ADMET replicate
  scout configs. These write to `oracle_benchmark_results_admet_replicates`
  and should be plotted separately from the existing one-seed ADMET scout.

## Logs

- `logs/molopt-cfg-5455029.*` - completed full 10K QED/LogP pilot.
- `logs/molopt-cfg-5458061.*` - completed full 10K SAScore pilot.
- `logs/molopt-cfg-5454909.*` - medium hERG ADMET slice that timed out.
- `logs/molopt-cfg-5461356.*` - small ADMET scout log snapshot.
