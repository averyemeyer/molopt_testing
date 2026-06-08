# MolOpt-LIDDIA Environment

The benchmark environment on this system is named `molopt-liddia`.

The name `liddia_molopt` was used informally in discussion, but it is not the
actual Conda environment name.

## Recreate The Environment

From the `molopt_testing` repository:

```bash
conda env create -f environment/molopt-liddia.yml
conda activate molopt-liddia
```

The curated environment file contains the packages required by the tested
MolOpt algorithms, plotting scripts, and evaluator-backed toxicity functions.

`molopt-liddia-pip-freeze.txt` is a snapshot of the complete working
environment as of June 8, 2026. It is included for provenance and debugging,
not as the preferred installation file: several Conda packages appear as local
build paths and are not portable.

## Evaluator Source

The benchmark does not install the LIDDIA `evaluator` package from PyPI. The
expected workspace layout is:

```text
workspace/
  evaluator/
  mol-opt/
  molopt_testing/
```

The Slurm runner adds `workspace/` to `PYTHONPATH`. The oracle wrapper also
walks upward from its own location to find a sibling `evaluator/` directory.

Verify the important imports with:

```bash
python -c "import torch, tdc, rdkit, admet_ai; print(torch.__version__)"
python -c "from evaluator.tools import calculate_qed, predict_toxicity; print(calculate_qed('CCO'))"
```

## Tested Versions

- Python 3.10
- PyTorch 2.5.0
- PyTDC 0.4.1
- RDKit 2025.09.6 in the final working environment
- ADMET-AI 1.4.0
- NumPy 1.24.4
- SciPy 1.10.1
- pandas 2.1.4
