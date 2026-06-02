# Part 2 Evaluator-Backed Tables

These tables compare the original saved benchmark scores against scores
recomputed with evaluator-backed oracle wrappers.

Key files:

- `compare_full_part2_evaluator_topk.csv` - original vs evaluator-backed final
  top-k/AUC means for the full 10K QED/LogP/SAScore pilot.
- `compare_medium_part2_evaluator_topk.csv` - same comparison for the medium
  cheap-oracle matrix.
- `metrics_*_part2_evaluator.*` - standalone metrics for the rescored outputs.
- `full_qed_logp_sascore_top10_thresholds_part2_evaluator.csv` - top10
  threshold calls for the rescored full pilot.

Summary:

- Full 10K QED, LogP, and SAScore top-k metrics were unchanged.
- Medium molecular-weight metrics shifted slightly because evaluator-backed
  molecular weight uses exact molecular weight rather than average molecular
  weight.
