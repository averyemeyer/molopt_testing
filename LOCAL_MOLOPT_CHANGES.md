# Local Changes To The MolOpt Clone

## Upstream Base

The benchmark clone came from:

```text
https://github.com/wenhao-gao/mol-opt
commit 63382d78890e910080ef9a9b3b6d04a4552aff85
```

The reusable tracked-code changes are stored in:

```text
patches/mol-opt-compatibility.patch
```

## Compatibility Changes

### `molopt/base.py`

- Replaced the mutable default `mol_buffer={}` with `mol_buffer=None`.
  This prevents separate oracle instances from accidentally sharing state.
- Re-enabled `joblib` and `load_smiles_from_file`.
  This is required to run every algorithm against the curated 1,000-SMILES
  starter file instead of downloading/loading the default ZINC data.

### `molopt/mimosa/online_train.py`

- Changed `from utils import Molecule_Dataset` to the package-relative
  `from .utils import Molecule_Dataset`.
- This allows MIMOSA to import correctly when MolOpt is used as a package.

### `molopt/selfies_ga/discriminator.py`

- Creates the discriminator as float explicitly.
- Removes an extra positional argument passed to `create_discriminator`.
- These changes resolve dtype/signature errors encountered during SelfiesGA
  runs.

## Benchmark Harness Additions

The original clone also contains untracked benchmark files generated during
this study. The reusable versions are curated in this repository:

- `scripts/liddia_oracles.py`
- `scripts/run_molopt_oracle_tests.py`
- `scripts/run_molopt_benchmark_config.py`
- `scripts/run_molopt_from_config.sh`
- plotting, validation, rescoring, and summary scripts under `scripts/`
- benchmark protocols under `configs/`
- the matched starter set under `inputs/`

Large raw result trees, checkpoints, and repetitive Slurm logs remain outside
this repository.

## Changes Not Included In The Patch

The local clone's `demo.py` contains commented experiment paths and notes.
Those edits are not required for the benchmark or future LIDDIA integration,
so they are intentionally excluded from the compatibility patch.

## Apply Or Inspect The Patch

```bash
git -C /path/to/mol-opt apply --check \
  /path/to/molopt_testing/patches/mol-opt-compatibility.patch

git -C /path/to/mol-opt apply \
  /path/to/molopt_testing/patches/mol-opt-compatibility.patch
```

Use `scripts/install_into_molopt.sh` to apply the patch and install the full
benchmark harness in one step.
