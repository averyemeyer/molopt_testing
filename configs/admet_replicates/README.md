# ADMET Replicate Configs

These configs launch the follow-up ADMET/toxicity replicate scout.

- Output root: `oracle_benchmark_results_admet_replicates`
- Intended plot folder after completion: `plots/admet_replicates/`
- Tier: `small_replicate`
- Budget: 100 oracle calls
- Seeds: `0, 1, 2`
- Algorithms: `screening`, `graph_ga`, `graph_mcts`, `smiles_ga`, `stoned`
- Oracles: one config each for hERG, DILI, ClinTox, mutagenicity, and
  carcinogenicity

These runs are intentionally separate from the existing `plots/small_admet/`
one-seed scout so both versions can be compared side by side.
