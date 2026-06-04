# ADMET Replicate Curve Shape Notes

The 3-seed ADMET replicate scout smooths the selected-algorithm curves relative
to the original one-seed scout, especially for `top1` and `top10`.

`top100` can still show U-shaped behavior in a 100-call run. This is expected:
until 100 molecules have been scored, the `top100` average is effectively the
average of all molecules seen so far, not a stable best-100 pool. Early
high-scoring molecules can be diluted by lower-scoring molecules before the pool
is fully populated.

Mean curve check across all selected algorithms and seeds:

| Oracle | Top-k | Start | Minimum | Final | Final - minimum |
| --- | --- | ---: | ---: | ---: | ---: |
| hERG | top1 | 0.5632 | 0.5632 | 0.9882 | 0.4251 |
| hERG | top10 | 0.5632 | 0.5623 | 0.9526 | 0.3903 |
| hERG | top100 | 0.5632 | 0.5504 | 0.5885 | 0.0381 |
| DILI | top1 | 0.5998 | 0.5998 | 0.9980 | 0.3982 |
| DILI | top10 | 0.5998 | 0.4837 | 0.9833 | 0.4996 |
| DILI | top100 | 0.5998 | 0.4837 | 0.5056 | 0.0219 |
| ClinTox | top1 | 0.9329 | 0.9329 | 0.9995 | 0.0667 |
| ClinTox | top10 | 0.9329 | 0.8281 | 0.9980 | 0.1699 |
| ClinTox | top100 | 0.9329 | 0.8281 | 0.8817 | 0.0536 |
| Mutagenicity | top1 | 0.7204 | 0.7204 | 0.9911 | 0.2707 |
| Mutagenicity | top10 | 0.7204 | 0.7148 | 0.9737 | 0.2589 |
| Mutagenicity | top100 | 0.7204 | 0.6754 | 0.6868 | 0.0114 |
| Carcinogenicity | top1 | 0.7684 | 0.7684 | 0.9891 | 0.2207 |
| Carcinogenicity | top10 | 0.7684 | 0.7062 | 0.9753 | 0.2691 |
| Carcinogenicity | top100 | 0.7684 | 0.7062 | 0.7820 | 0.0758 |

Practical interpretation: use `top10` as the primary ADMET scout view, `top1`
for best-hit behavior, and `top100` only as a pool-level diagnostic at this
small budget.
