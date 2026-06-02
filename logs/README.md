# Log Notes

This directory contains selected Slurm stdout/stderr logs for benchmark
provenance.

Included logs:

- `molopt-cfg-5455029.*` - completed full 10K QED/LogP pilot.
- `molopt-cfg-5458061.*` - completed full 10K SAScore pilot.
- `molopt-cfg-5454909.out` - medium hERG ADMET job stdout; job timed out.
- `molopt-cfg-5461356.out` - small ADMET scout stdout snapshot.
- Repair/fill logs for medium cheap benchmark gaps.

The ADMET stderr logs from jobs `5454909` and `5461356` are intentionally not
committed because they contain large model-progress output. The important
runtime outcomes are recorded in `oracle_time_run_analysis_2026-06-02.md`.

The full raw logs remain in the source working tree:

```text
/users/PCON0041/mey200/testing/mol-opt/molopt-cfg-5454909.error
/users/PCON0041/mey200/testing/mol-opt/molopt-cfg-5461356.error
```
