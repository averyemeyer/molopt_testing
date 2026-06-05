# MolOpt, Evaluator, And GeLLMO-C Runtime Comparison

## What Was Measured

All comparison jobs requested one GPU and four CPU cores. The GeLLMO-C timing
job ran on an NVIDIA A100 40 GB GPU.

| Operation | Wall time | Meaning |
| --- | ---: | --- |
| MolOpt generation probe | 0.002-0.09 s/molecule | Candidate generation or selection plus optimizer bookkeeping; no property model |
| GeLLMO-C warm generation | 4.7 s/5 candidates | One instruction-guided batch of molecular modifications |
| GeLLMO-C warm generation | 4.8 s/20 candidates | Candidates generated together; not 20 independent calls |
| GeLLMO-C model load | 121.5 s | One-time startup cost when the model is kept resident |
| MolOpt ADMET oracle | 11-13 s/molecule | One evaluator-backed toxicity endpoint score |
| Direct `predict_toxicity` | 13.2 s/molecule warm | Returns all five toxicity endpoint predictions together |

## Plain-Language Interpretation

- MolOpt algorithms generate or select candidates quickly relative to ADMET
  scoring. The tested range was about 0.002-0.09 seconds per molecule.
- GeLLMO-C takes several seconds to create a targeted batch, but it uses the
  starting molecule and natural-language objective to guide the edit.
- Neither generation timing proves that a candidate improved. Candidates still
  need evaluator scoring.
- Evaluator-backed ADMET prediction is the dominant runtime cost.
- If several toxicity endpoints are needed for the same molecule, call
  `predict_toxicity` once and reuse all endpoint values rather than invoking
  separate endpoint wrappers.

## Appropriate Comparison

MolOpt and GeLLMO-C perform different jobs:

| MolOpt | GeLLMO-C |
| --- | --- |
| Search algorithm proposes/selects molecules and repeatedly calls an oracle | Language model proposes targeted modifications |
| Supports broad optimization curves over many calls | Supports scaffold-aware, instruction-guided edits |
| Generation overhead varies by algorithm | Has a large one-time model-load cost |
| Runtime is dominated by expensive evaluator oracles | Generated candidates still require external evaluation |

For the LIDDIA lead optimizer, a practical architecture is to keep generation
tools resident, score candidates selectively, and cache multi-endpoint
evaluator results per molecule.

## Measurement Caveats

- The MolOpt generation probe used 500 unique scored molecules and one seed.
- The probe score was deterministic but chemically meaningless; it isolates
  runtime mechanics, not optimization quality.
- GeLLMO-C generation time depends on prompt length, generated token count,
  beam count, hardware, and model checkpoint.
- GeLLMO-C five-candidate batches produced 60-80% RDKit-valid strings in the
  short trajectory test; the measured 20-candidate batch produced 20/20 valid
  strings.
- These numbers are planning estimates, not universal throughput guarantees.
