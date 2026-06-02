"""Prepare reproducible ZINC starter SMILES files from mol_opt/data.

Use this with the data files from:
https://github.com/wenhao-gao/mol_opt/tree/main/data

Examples:
  python prepare_zinc_starters.py --input data/zinc.txt.gz
  python prepare_zinc_starters.py --input data/zinc.csv.gz --seed 0
  python prepare_zinc_starters.py --input data/zinc.tab --out-dir benchmark_inputs
"""

import argparse
import csv
import gzip
import random
from pathlib import Path


DEFAULT_SIZES = {
    "zinc_debug_50.smi": 50,
    "zinc_sanity_1k.smi": 1000,
    "zinc_medium_10k.smi": 10000,
}


def open_text(path):
    path = Path(path)
    if path.suffix == ".gz":
        return gzip.open(path, "rt")
    return open(path)


def looks_like_smiles(text):
    if not text:
        return False
    lowered = text.lower()
    if lowered in {"smiles", "smile", "smi", "zinc_id", "zincid"}:
        return False
    return any(char.isalpha() for char in text)


def first_smiles_field(fields):
    for field in fields:
        field = field.strip()
        if looks_like_smiles(field):
            return field
    return None


def iter_smiles(path):
    with open_text(path) as f:
        sample = f.readline()
        f.seek(0)

        if "," in sample:
            reader = csv.reader(f)
            header = next(reader, None)
            smiles_index = None
            if header:
                lowered = [h.strip().lower() for h in header]
                for key in ("smiles", "smile", "smi"):
                    if key in lowered:
                        smiles_index = lowered.index(key)
                        break
                if smiles_index is None:
                    smi = first_smiles_field(header)
                    if smi:
                        yield smi

            for row in reader:
                if smiles_index is not None and smiles_index < len(row):
                    smi = row[smiles_index].strip()
                else:
                    smi = first_smiles_field(row)
                if smi:
                    yield smi
            return

        for line in f:
            fields = line.strip().split()
            smi = first_smiles_field(fields)
            if smi:
                yield smi


def reservoir_sample(items, size, rng):
    sample = []
    for index, item in enumerate(items, start=1):
        if len(sample) < size:
            sample.append(item)
            continue
        replacement = rng.randrange(index)
        if replacement < size:
            sample[replacement] = item
    return sample


def write_smiles(path, smiles):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for smi in smiles:
            f.write(f"{smi}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/zinc.txt.gz",
        help="Path to zinc.txt.gz, zinc.csv.gz, or zinc.tab from mol_opt/data.",
    )
    parser.add_argument("--out-dir", default="benchmark_inputs")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--sizes",
        nargs="*",
        type=int,
        default=None,
        help="Optional custom sample sizes, e.g. --sizes 50 1000 10000.",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    out_dir = Path(args.out_dir)

    if args.sizes:
        sizes = {f"zinc_{size}.smi": size for size in args.sizes}
    else:
        sizes = DEFAULT_SIZES

    max_size = max(sizes.values())
    sampled = reservoir_sample(iter_smiles(args.input), max_size, rng)
    print(f"Sampled {len(sampled)} molecules from {args.input}")

    for filename, size in sizes.items():
        output = out_dir / filename
        write_smiles(output, sampled[:size])
        print(f"Wrote {output} ({min(size, len(sampled))} SMILES)")


if __name__ == "__main__":
    main()
