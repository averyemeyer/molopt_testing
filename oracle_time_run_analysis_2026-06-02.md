# Oracle, Time, and Run Analysis

Prepared on 2026-06-02 for internal LIDDIA/MolOpt benchmark planning.

## What The Top-k Metrics Mean

For each seed run, MolOpt records every molecule scored by the oracle. The
top-k curve at oracle call `n` is the average score of the best `k` molecules
seen so far in that run. Curves are then averaged across seeds.

- `top1`: best single molecule found so far. Useful for "can this method hit a
  standout?" but sensitive to lucky outliers.
- `top10`: average of the best 10 molecules found so far. Best default for
  lead-optimizer tool guidance because it reflects a practical shortlist.
- `top100`: average of the best 100 molecules found so far. Useful for asking
  whether an optimizer improves the broader candidate pool, not just a few hits.

The seeds are replicate stochastic runs over the same 1,000-SMILES starter file,
not different predefined slices of the starter set.

## Completed 10K Cheap-Oracle Pilot

Scope:

- Oracles: `qed`, `logp`, `sascore`
- Algorithms: `screening`, `graph_ga`, `smiles_ga`, `stoned`, `gpbo`
- Seeds: `0, 1, 2, 3, 4`
- Input file: `inputs/zinc_sanity_1k.smi`

Final mean metrics are in `tables/metrics_full_qed_logp_sascore.csv`.
Threshold summaries are in:

- `tables/full_qed_logp_sascore_top1_thresholds.csv`
- `tables/full_qed_logp_sascore_top10_thresholds.csv`
- `tables/full_qed_logp_sascore_top100_thresholds.csv`

## Selected Calls-To-Target

These are mean curve thresholds, measured in oracle calls. Empty values in the
CSV mean the threshold was not reached by the end of the run.

### Top10 Shortlist Targets

| Oracle | Target | Fastest methods in this pilot |
| --- | ---: | --- |
| QED | 0.94 | STONED: 567 calls; SMILES GA: 823; GPBO: 2818; Graph GA: 4311 |
| QED | 0.945 | STONED: 962 calls; GPBO: 5256 |
| LogP | 10 | GPBO: 357 calls; SMILES GA: 750; Graph GA: 1036; STONED: 1455 |
| LogP | 20 | SMILES GA: 3388 calls; STONED: 5887; GPBO: 8604 |
| SAScore | 8.5 | Graph GA: 215 calls; GPBO: 350; STONED: 780; SMILES GA: 1760 |
| SAScore | 8.9 | Graph GA: 532 calls; GPBO: 2734 |

### Top100 Pool Targets

Top100 is stricter because the method must generate many high-scoring molecules.

| Oracle | Target | Methods that reached it |
| --- | ---: | --- |
| QED | 0.94 | SMILES GA: 1340 calls; STONED: 2559; GPBO: 7672 |
| LogP | 20 | SMILES GA: 3708 calls; STONED: 6196 |
| SAScore | 8.9 | Graph GA: 2792 calls; GPBO: 9789 |

## Observed Slurm Resource Use

All listed jobs used the same batch shape:

- 1 node
- 4 CPU cores
- 1 A100 GPU requested
- 16 GB requested memory
- 12-hour walltime limit

| Job | Purpose | State | Elapsed | Peak RSS | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `5455029` | Full 10K QED/LogP pilot | Completed | 09:37:28 | 8.46 GB | 50 seed runs |
| `5458061` | Full 10K SAScore pilot | Completed | 03:57:18 | 8.64 GB | 25 seed runs |
| `5452346` | Medium cheap repair slice | Completed | 02:05:01 | 4.60 GB | flagged row repair |
| `5452692` | Medium LogP/SelfiesGA fill | Completed | 00:07:24 | 2.81 GB | final gap fill |
| `5454909` | Medium hERG ADMET slice | Timeout | 12:00:26 | 1.75 GB | completed only 6 medium seed runs |
| `5461356` | Small ADMET scout | Running at check | 00:43:23 | n/a | 100-call ADMET all-algorithm scout |

## Approximate Cheap-Oracle Timing

The completed QED/LogP/SAScore 10K pilot produced 445,060 actual scored calls
across all completed seed runs. The two completed full jobs took 48,886 seconds
of wall-clock time in total.

Approximate selected-pilot rate:

- 0.11 wall-clock seconds per actual cheap-oracle call
- about 9 cheap-oracle calls per wall-clock second for this sequential job mix

This is an estimate for planning, not a universal property of the algorithms.
It includes optimizer overhead, I/O, early stopping behavior, and the selected
mix of methods. It is most useful for rough triage:

- 1K cheap-oracle run: usually minutes per seed
- 10K cheap-oracle run: roughly 10 to 15 minutes per seed in this pilot mix
- 10K x 5 algorithms x 5 seeds x 1 cheap oracle: a few hours as a single Slurm
  batch, depending on early stopping and algorithm mix

### Estimated Wall Time By Oracle

Exact per-oracle wall times were not recorded for these first completed jobs
because the benchmark logs did not yet write per-seed timing sidecars. The
estimates below use job-level elapsed time and actual scored-call counts from
`tables/metrics_full_qed_logp_sascore.csv`.

| Run set | Oracle | Actual scored calls | Estimated sec/call | Estimated calls/sec | Estimated wall time |
| --- | --- | ---: | ---: | ---: | ---: |
| Full 10K QED/LogP | QED | 133,515 | 0.1026 | 9.75 | 3.80 h |
| Full 10K QED/LogP | LogP | 204,257 | 0.1026 | 9.75 | 5.82 h |
| Full 10K SAScore | SAScore | 107,288 | 0.1327 | 7.54 | 3.96 h |

QED and LogP were run in the same Slurm job, so their wall time is allocated
proportionally by scored-call count. SAScore ran as its own job, so its estimate
is closer to a true oracle-level job average. These are still wall-clock
estimates, not pure oracle-function latency measurements.

The CSV version is `tables/oracle_wall_time_estimates.csv`.

## Approximate Time-To-Target

Using the cheap-oracle pilot rate above, a threshold reached in 1,000 oracle
calls corresponds to roughly 2 minutes of wall-clock time in this selected
sequential batch context. Examples:

| Objective | Top-k target | Method | Calls | Rough wall-clock equivalent |
| --- | --- | --- | ---: | ---: |
| QED | top10 >= 0.94 | STONED | 567 | about 1 minute |
| QED | top10 >= 0.94 | SMILES GA | 823 | about 1.5 minutes |
| LogP | top10 >= 20 | SMILES GA | 3388 | about 6 minutes |
| LogP | top10 >= 20 | STONED | 5887 | about 11 minutes |
| SAScore | top10 >= 8.9 | Graph GA | 532 | about 1 minute |
| SAScore | top10 >= 8.9 | GPBO | 2734 | about 5 minutes |

These estimates are useful for tool-routing intuition, but future runs should
use the new `benchmark_run_metadata.json` sidecars for exact elapsed time and
resource use per seed.

## ADMET/Toxicity Timing

ADMET endpoints are much slower than cheap RDKit-style descriptors. The hERG
medium slice completed only 6 medium seed runs before the 12-hour walltime limit.
The small ADMET scout log shows single-molecule ensemble inference repeated for
novel SMILES, which makes broad all-algorithm ADMET sweeps expensive.

Current practical guidance:

- Use cheap oracles for broad algorithm comparisons.
- Use ADMET/toxicity oracles as targeted follow-up runs.
- Prefer smaller ADMET budgets first, then scale promising algorithm/oracle
  combinations.
- Add batching/caching around model-based scoring before treating ADMET as an
  interactive optimization target.

## Lead-Optimizer Integration Takeaways

- Use top10 as the default tool-performance signal for routing because it
  reflects shortlist quality.
- Use top1 only when the agent is explicitly searching for one extreme hit.
- Use top100 when the agent needs a broader candidate pool or diversity for
  downstream filtering.
- For raw physchem objectives such as LogP, molecular weight, HBA/HBD, TPSA, and
  rotatable bonds, high optimization scores can reflect oracle exploitation.
- For toxicity/safety oracles, benchmark scores should be transformed so higher
  means safer or more desirable before comparing curves.
