# Running The MolOpt Benchmark Harness

## 1. Expected Layout

```text
workspace/
  evaluator/
  mol-opt/
  molopt_testing/
```

`evaluator/` is the LIDDIA evaluator source. `mol-opt/` is the upstream clone.
`molopt_testing/` is this curated benchmark and reproducibility repository.

## 2. Prepare A Clean MolOpt Clone

```bash
cd workspace
git clone https://github.com/wenhao-gao/mol-opt.git
git -C mol-opt checkout 63382d78890e910080ef9a9b3b6d04a4552aff85

bash molopt_testing/scripts/install_into_molopt.sh mol-opt
```

The installer applies the compatibility patch and copies:

- benchmark Python scripts into the MolOpt repository root,
- configs into `mol-opt/benchmark_configs/`,
- the starter set into `mol-opt/benchmark_inputs/`.

## 3. Create Or Activate The Environment

```bash
conda env create -f molopt_testing/environment/molopt-liddia.yml
conda activate molopt-liddia
```

On the original system, the environment already exists at:

```text
/users/PCON0041/mey200/.conda/envs/molopt-liddia
```

## 4. Check A Config Without Running It

```bash
cd mol-opt
python run_molopt_benchmark_config.py \
  benchmark_configs/medium_cheap.yaml \
  --dry-run
```

## 5. Submit A Slurm Run

Cheap-oracle example:

```bash
sbatch run_molopt_from_config.sh \
  benchmark_configs/medium_cheap.yaml
```

Three-seed hERG example:

```bash
sbatch run_molopt_from_config.sh \
  benchmark_configs/admet_replicates/admet_replicate_herg.yaml
```

The default request is one node, four CPUs, and one GPU. Override the
environment name if needed:

```bash
MOLOPT_ENV=my_environment sbatch run_molopt_from_config.sh CONFIG.yaml
```

## 6. Output Layout

Each optimizer run writes:

```text
<output_root>/<tier>/<oracle>/<algorithm>/seed_<n>/
```

Important files:

- `results_*.yaml`: molecule, score, and oracle-call index
- `benchmark_run_metadata.json`: elapsed time, status, configured budget,
  actual call count, CPU time, and peak memory
- Slurm `.out`/`.error`: process-level logs

`skip_existing: true` prevents completed result directories from being rerun.

## 7. Summarize And Plot

```bash
python summarize_molopt_metrics.py \
  --root oracle_benchmark_results \
  --tier medium \
  --csv oracle_benchmark_results/metrics_medium.csv \
  --markdown oracle_benchmark_results/metrics_medium.md

python plot_molopt_benchmark_tier.py \
  --root oracle_benchmark_results \
  --tier medium \
  --algorithms all \
  --top-k 10 \
  --output-dir oracle_benchmark_plots
```

Repeat plotting with `--top-k 1` and `--top-k 100` for the other shortlist
views.

## 8. Reproduce The Runtime Probes

Direct evaluator versus MolOpt toxicity wrapper:

```bash
sbatch run_direct_vs_oracle_timing.sh
```

MolOpt generation/optimizer overhead:

```bash
sbatch run_generation_overhead_probe.slurm
```

The direct timing job writes separate cold and warm call tables under
`direct_vs_oracle_timing/`. The generation probe writes normal MolOpt run
metadata under `oracle_benchmark_results_generation_probe/`.

## 9. Oracle Behavior

MolOpt maximizes every supplied scalar score.

- QED is passed through unchanged.
- SA score is converted to synthesis desirability with `10 - SA`.
- Toxicity probabilities are converted to safety with `1 - toxicity`.
- Raw LogP, molecular weight, TPSA, HBA/HBD, and rotatable bonds should not be
  treated as standalone lead-optimization goals without ranges or constraints.

The toxicity wrapper currently invokes `predict_toxicity` for each endpoint
call. Future LIDDIA integration should cache one prediction per molecule and
reuse all endpoint values.

## 10. Recommended Integration Boundary

For the LIDDIA agent:

- keep evaluator-backed oracle definitions in the evaluator/oracle registry,
- expose MolOpt as a budgeted search tool,
- pass explicit objective direction and constraints,
- return top-k molecules plus scores and call counts,
- cache duplicate molecule evaluations,
- use small call budgets for ADMET objectives unless predictions are batched.
