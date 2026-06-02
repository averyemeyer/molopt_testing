"""Flag MolOpt benchmark result files with impossible score ranges."""

import argparse
import csv
from pathlib import Path

import yaml


BOUNDED_RANGES = {
    "qed": (0.0, 1.0),
    "sascore": (0.0, 10.0),
    "hba": (0.0, None),
    "hbd": (0.0, None),
    "rot_bonds": (0.0, None),
    "logp": (0.0, None),
    "tpsa": (0.0, None),
    "mol_wt": (0.0, None),
    "herg": (0.0, 1.0),
    "dili": (0.0, 1.0),
    "clintox": (0.0, 1.0),
    "mutagenicity": (0.0, 1.0),
    "carcinogens": (0.0, 1.0),
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


def load_scores(path):
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    scores = []
    for values in data.values():
        if isinstance(values, list) and values:
            scores.append(float(values[0]))
    return scores


def validate_path(path):
    meta = parse_result_path(path)
    scores = load_scores(path)
    low, high = BOUNDED_RANGES.get(meta["oracle"], (None, None))

    issues = []
    if not scores:
        issues.append("empty")
    if low is not None and any(score < low for score in scores):
        issues.append(f"score_below_{low}")
    if high is not None and any(score > high for score in scores):
        issues.append(f"score_above_{high}")

    return {
        **meta,
        "path": str(path),
        "n_scores": len(scores),
        "min_score": min(scores) if scores else "",
        "max_score": max(scores) if scores else "",
        "status": "ok" if not issues else "suspect",
        "issues": " ".join(issues) or "-",
    }


def write_csv(rows, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "tier",
        "oracle",
        "algorithm",
        "seed",
        "status",
        "issues",
        "n_scores",
        "min_score",
        "max_score",
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
    parser.add_argument("--csv", default="oracle_benchmark_results/validation_medium.csv")
    args = parser.parse_args()

    root = Path(args.root) / args.tier
    paths = sorted(root.glob("**/results_*.yaml"))
    rows = [validate_path(path) for path in paths]
    rows.sort(key=lambda row: (row["status"], row["oracle"], row["algorithm"], int(row["seed"])))
    write_csv(rows, Path(args.csv))

    suspect = [row for row in rows if row["status"] != "ok"]
    print(f"Checked files: {len(rows)}")
    print(f"Suspect files: {len(suspect)}")
    print(f"Saved {args.csv}")
    for row in suspect[:20]:
        print(
            f"{row['status']} {row['oracle']}/{row['algorithm']}/seed_{row['seed']}: "
            f"{row['issues']} min={row['min_score']} max={row['max_score']}"
        )


if __name__ == "__main__":
    main()
