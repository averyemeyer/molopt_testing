"""Recompute saved MolOpt scores and flag mismatches.

This is stronger than range validation: it catches benchmark contamination where
scores are plausible but belong to a previous oracle run.
"""

import argparse
import csv
from pathlib import Path

import yaml

from liddia_oracles import hba, hbd, logp, mol_wt, qed, rot_bonds, sascore, tpsa


ORACLES = {
    "hba": hba,
    "hbd": hbd,
    "logp": logp,
    "mol_wt": mol_wt,
    "qed": qed,
    "rot_bonds": rot_bonds,
    "sascore": sascore,
    "tpsa": tpsa,
}


def parse_result_path(path):
    parts = path.parts
    idx = parts.index("oracle_benchmark_results")
    return {
        "tier": parts[idx + 1],
        "oracle": parts[idx + 2],
        "algorithm": parts[idx + 3],
        "seed": parts[idx + 4].replace("seed_", ""),
    }


def load_rows(path):
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    for smi, values in data.items():
        if isinstance(values, list) and len(values) >= 2:
            yield smi, float(values[0]), int(values[1])


def audit_file(path, tolerance, max_mismatches):
    meta = parse_result_path(path)
    oracle_fn = ORACLES.get(meta["oracle"])
    if oracle_fn is None:
        return None

    checked = 0
    mismatches = []
    max_abs_error = 0.0
    for smi, saved_score, call in load_rows(path):
        checked += 1
        recomputed = float(oracle_fn(smi))
        abs_error = abs(saved_score - recomputed)
        max_abs_error = max(max_abs_error, abs_error)
        if abs_error > tolerance and len(mismatches) < max_mismatches:
            mismatches.append((smi, call, saved_score, recomputed, abs_error))

    return {
        **meta,
        "path": str(path),
        "checked": checked,
        "status": "ok" if not mismatches else "mismatch",
        "n_mismatches_sampled": len(mismatches),
        "max_abs_error": max_abs_error,
        "examples": "; ".join(
            f"call={call} saved={saved:.6g} expected={expected:.6g} smi={smi}"
            for smi, call, saved, expected, _error in mismatches
        )
        or "-",
    }


def write_csv(rows, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "tier",
        "oracle",
        "algorithm",
        "seed",
        "status",
        "checked",
        "n_mismatches_sampled",
        "max_abs_error",
        "examples",
        "path",
    ]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="oracle_benchmark_results")
    parser.add_argument("--tier", default="medium")
    parser.add_argument("--csv", default="oracle_benchmark_results/audit_medium_scores.csv")
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--max-mismatches", type=int, default=5)
    args = parser.parse_args()

    paths = sorted((Path(args.root) / args.tier).glob("**/results_*.yaml"))
    rows = [
        row
        for path in paths
        for row in [audit_file(path, args.tolerance, args.max_mismatches)]
        if row is not None
    ]
    rows.sort(key=lambda row: (row["status"], row["oracle"], row["algorithm"], int(row["seed"])))
    write_csv(rows, Path(args.csv))

    bad = [row for row in rows if row["status"] != "ok"]
    print(f"Audited files: {len(rows)}")
    print(f"Files with mismatches: {len(bad)}")
    print(f"Saved {args.csv}")
    for row in bad[:20]:
        print(
            f"{row['oracle']}/{row['algorithm']}/seed_{row['seed']} "
            f"max_abs_error={row['max_abs_error']:.6g} {row['examples']}"
        )


if __name__ == "__main__":
    main()
