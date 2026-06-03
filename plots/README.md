# Plot Guide

## Full 10K Pilot

Folder: `plots/full/`

These are the evaluator-backed plots used for the current benchmark summary.

Oracles:

- `qed`
- `logp`
- `sascore`

Each oracle has:

- `*_top1.png` - best single molecule found so far
- `*_top10.png` - best shortlist quality; default view for tool guidance
- `*_top100.png` - broader pool improvement

## Medium 1K Matrix

Folder: `plots/medium/`

These evaluator-backed plots cover the wider cheap-oracle benchmark matrix. Use
them to compare algorithm behavior across more oracle classes, but treat the
10K full plots as the stronger paper-style comparison for the selected oracles.

Each medium oracle has the same top-k views:

- `*_top1.png`
- `*_top10.png`
- `*_top100.png`
