# Part 2 Evaluator-Backed Plots

These plots are rescored versions of the existing MolOpt benchmark outputs.

Important interpretation:

- The optimizer trajectories were not rerun.
- The same generated molecules and oracle-call numbers were kept.
- Scores were recomputed with the evaluator-backed `scripts/liddia_oracles.py`.
- This answers: "Did changing the oracle wrapper implementation change the
  plotted scores?"

Result:

- Full 10K QED/LogP/SAScore plots did not change numerically.
- Medium cheap-oracle plots only changed meaningfully for molecular weight,
  because the evaluator-backed wrapper uses exact molecular weight while the
  previous wrapper used average molecular weight.
