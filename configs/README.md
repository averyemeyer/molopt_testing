# Benchmark Config Guide

Configs are copied to `mol-opt/benchmark_configs/` by
`scripts/install_into_molopt.sh`.

## Main Protocols

- `medium_cheap.yaml`: broad 1,000-call, 3-seed matrix across cheap evaluator
  objectives and the default algorithm set.
- `full_cheap_pilot_qed_logp.yaml`: 10,000-call QED/LogP pilot.
- `full_cheap_pilot_sascore.yaml`: 10,000-call synthesis-desirability pilot.
- `small_admet/`: 100-call one-seed toxicity scouts.
- `admet_replicates/`: 100-call three-seed toxicity follow-up using the
  selected five-algorithm subset.
- `generation_overhead_probe.yaml`: 500-call deterministic timing probe with
  no real property evaluator.

## Common Fields

- `tier`: selects call budget, seeds, logging frequency, and patience.
- `oracles`: explicit evaluator-backed objective names.
- `algorithms`: explicit MolOpt methods, `available`, or `all`.
- `smi_file`: starter SMILES path relative to the MolOpt clone.
- `output_root`: root folder for raw result trees.
- `skip_existing`: avoids rerunning completed result directories.
- `continue_on_error`: records a failed method and continues the matrix.

All MolOpt objectives are maximized. Direction transforms are implemented in
`scripts/liddia_oracles.py`, not in the YAML files.
