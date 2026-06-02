"""Rescore existing MolOpt result YAML files with the current oracle wrappers.

This preserves each molecule's original oracle-call number and recomputes only
the score. It is useful for comparing oracle definition changes without
rerunning the stochastic optimizers.
"""

import argparse
import importlib
from pathlib import Path

import yaml
from rdkit import RDLogger


RDLogger.DisableLog("rdApp.warning")


def parse_result_path(path, input_root):
    relative = path.relative_to(input_root)
    parts = relative.parts
    if len(parts) < 5:
        raise ValueError(f"Unexpected result path: {path}")
    tier, oracle, algorithm, seed = parts[:4]
    return tier, oracle, algorithm, seed


def load_oracle(name):
    module = importlib.import_module("liddia_oracles")
    return getattr(module, name)


def rescore_file(path, input_root, output_root, overwrite=False):
    tier, oracle, algorithm, seed = parse_result_path(path, input_root)
    output_dir = output_root / tier / oracle / algorithm / seed
    output_path = output_dir / path.name
    if output_path.exists() and not overwrite:
        return "skipped"

    oracle_fn = load_oracle(oracle)
    with path.open() as handle:
        data = yaml.safe_load(handle) or {}

    rescored = {}
    for smiles, values in data.items():
        if not isinstance(values, list) or len(values) < 2:
            continue
        call = int(values[1])
        rescored[smiles] = [float(oracle_fn(smiles)), call]

    output_dir.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as handle:
        yaml.safe_dump(rescored, handle, sort_keys=False)
    return "rescored"


def discover_paths(input_root, tier, oracles):
    root = input_root / tier if tier else input_root
    paths = []
    for oracle in oracles:
        paths.extend(sorted((root / oracle).glob("*/seed_*/results_*.yaml")))
    return paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", default="oracle_benchmark_results")
    parser.add_argument("--output-root", default="oracle_benchmark_results_part2_evaluator")
    parser.add_argument("--tier", required=True)
    parser.add_argument("--oracles", nargs="+", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    input_root = Path(args.input_root)
    output_root = Path(args.output_root)
    paths = discover_paths(input_root, args.tier, args.oracles)

    counts = {"rescored": 0, "skipped": 0}
    for path in paths:
        status = rescore_file(path, input_root, output_root, overwrite=args.overwrite)
        counts[status] += 1

    print(f"Matched {len(paths)} result files")
    print(f"Rescored {counts['rescored']}")
    print(f"Skipped {counts['skipped']}")
    print(f"Output root: {output_root}")


if __name__ == "__main__":
    main()
