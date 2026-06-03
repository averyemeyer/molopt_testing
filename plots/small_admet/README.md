# Small ADMET Scout Plots

These plots summarize the completed 100-call ADMET/toxicity scout:

- `herg`
- `dili`
- `clintox`
- `mutagenicity`
- `carcinogens`

Each endpoint has:

- `*_top1.png`
- `*_top10.png`
- `*_top100.png`

Scores are safety/desirability scores from the MolOpt wrapper:

```text
score = 1 - predicted_toxicity_probability
```

So higher values mean lower predicted toxicity liability.

This is a one-seed scout, useful for routing and cost intuition, not a final
statistical benchmark.
