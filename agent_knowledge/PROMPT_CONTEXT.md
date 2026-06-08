# MolOpt Benchmark Context For LIDDIA

- MolOpt maximizes the scalar returned by every oracle. Check the wrapper
  transform before reasoning about direction.
- QED is passed through unchanged: higher is better. In the 10K, 5-seed test,
  STONED had the strongest top-10 trajectory; GPBO and SMILES GA were
  competitive.
- SA score is transformed to `10 - raw SA`, so a higher MolOpt score means
  easier predicted synthesis. Graph GA reached a top-10 desirability of 8.9
  fastest in the tested comparison.
- Toxicity endpoints return `1 - predicted toxicity`, so higher means safer.
  The 100-call, 3-seed ADMET results are preliminary and endpoint-specific.
  Graph MCTS led AUC-top10 for four of five endpoints; SMILES GA led
  carcinogens.
- Do not maximize raw LogP, molecular weight, TPSA, HBA, HBD, or rotatable
  bonds as general lead-quality goals. Use project-specific target ranges,
  constraints, or bounded composite scores.
- Use top-10 average as the default shortlist metric. Top-1 describes the best
  observed hit; top-100 describes broader candidate-library quality.
- Candidate generation cost in the probe was about 0.002-0.09 seconds per
  molecule for the tested methods. Evaluator-backed ADMET scoring cost about
  11.0-12.5 seconds per scored molecule and dominated runtime.
- Seeds change optimizer randomness; they do not select different slices of
  the common 1,000-molecule starter set.
- Report algorithm, transformed objective, raw property interpretation, call
  budget, elapsed time, top-k candidates, evidence strength, and constraints.
- Cache scores by canonical molecule and reuse one toxicity-model output across
  endpoints where the evaluator permits it.

Structured source: `agent_knowledge/molopt_benchmark_knowledge.json`

