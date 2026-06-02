# Log Notes

This directory contains selected Slurm stdout/stderr logs for benchmark
provenance.

The hERG ADMET stderr log from job `5454909` is intentionally not committed
because it contains hundreds of thousands of model-progress lines. The important
runtime outcome is recorded in `pi_meeting_summary_2026-06-02.md`: the job hit
the 12-hour walltime after completing `herg/graph_ga` and `herg/screening`.

The full raw log remains in the source working tree:

```text
/users/PCON0041/mey200/testing/mol-opt/molopt-cfg-5454909.error
```
