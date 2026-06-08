# Agent-Facing Benchmark Knowledge

This directory turns the benchmark record into a compact format that a lead
optimizer agent can consume without reading every CSV, plot, and run log.

## Why These Files Exist

The repository contains two different kinds of information:

1. measured evidence, such as scores, oracle-call counts, and wall time;
2. interpretation, such as whether an objective is safe to maximize and which
   algorithm is a reasonable first choice.

Those should not be mixed into one unstructured prompt. An agent needs a stable
contract that distinguishes evaluator meaning, MolOpt score meaning, measured
results, recommendations, and caveats.

## File Roles

- `molopt_benchmark_knowledge.yaml` is the human-maintained source of truth.
  YAML is readable during scientific review and supports comments.
- `molopt_benchmark_knowledge.json` is the generated machine-readable mirror.
  JSON is easier to load into tool code, retrieval systems, and structured
  prompts. Do not edit it by hand.
- `schema.json` defines required structure and allowed values. It prevents
  silent field-name drift and missing direction or evidence metadata.
- `PROMPT_CONTEXT.md` is a short rendering suitable for a system/developer
  prompt or retrieval result.

The CSV files under `../tables/` remain the evidence archive. This directory
stores compact conclusions plus paths back to those tables instead of copying
all raw rows.

## Design Choices

### Raw Direction And MolOpt Direction Are Separate

MolOpt maximizes the scalar returned by an oracle. That is not always the same
as the evaluator's raw scientific meaning.

- Raw toxicity probability is better when lower.
- The MolOpt wrapper returns `1 - toxicity`, so its score is better when higher.
- Raw SA score is better when lower.
- The MolOpt wrapper returns `10 - SA`, so its score is better when higher.

Keeping both directions prevents an agent from applying a second inversion.

### Evidence And Recommendations Are Separate

An observed ranking belongs under `evidence`. Advice about how an agent should
route a task belongs under `routing`. This matters because a method that wins a
small 100-call scout is not automatically a universal default.

Each evidence block records calls, seeds, compared algorithms, metric, evidence
strength, and source tables.

### Confidence Is Explicit

`strong_internal` means relatively well supported within this study, not
externally validated. `preliminary` marks small scouts or limited replication.
`behavior_only` means the run shows optimizer response but should not define a
drug-design objective.

### Unsafe Objectives Stay Visible

Raw LogP and unbounded descriptors are retained because they teach us about
optimizer behavior. They are marked `avoid_standalone`, so an agent can use
them as target ranges, constraints, or composite terms without interpreting
raw maximization as better drug design.

## Validate Or Regenerate

From the repository root:

```bash
python scripts/validate_agent_knowledge.py --write-json
```

This validates YAML against `schema.json`, writes the JSON mirror, checks cited
local source files, and verifies that YAML and JSON agree.

## Intended Agent Use

Load the JSON when constructing the lead optimizer's tool registry, or retrieve
only the relevant objective profile at planning time. The agent should:

1. identify the requested property and raw scientific goal;
2. select the matching evaluator-backed wrapper;
3. confirm the wrapper's MolOpt score is higher-is-better;
4. reject or reformulate objectives marked `avoid_standalone`;
5. choose algorithms using routing advice at the stated evidence strength;
6. report call budget, runtime assumptions, top-k candidates, and caveats.

This is decision support, not an autonomous medicinal-chemistry rulebook.

