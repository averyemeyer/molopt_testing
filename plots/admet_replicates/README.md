# ADMET Replicate Plots

Three-seed follow-up ADMET/toxicity scout.

- Source output root: `oracle_benchmark_results_admet_replicates`
- Tier: `small_replicate`
- Budget: 100 oracle calls
- Seeds: `0, 1, 2`
- Algorithms: `screening`, `graph_ga`, `graph_mcts`, `smiles_ga`, `stoned`
- Oracles: hERG, DILI, ClinTox, mutagenicity, carcinogenicity

These plots are separate from `plots/small_admet/`, which contains the original
one-seed all-algorithm scout.

Use `top10` as the main shortlist-quality view. `top100` is still useful as a
pool-level diagnostic, but it can show early U-shaped behavior because a
100-call run has not filled a true 100-molecule top-k pool until the end.
