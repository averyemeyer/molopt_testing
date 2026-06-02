"""Create benchmark metric tables from MolOpt YAML result files."""

import argparse
import csv
from pathlib import Path

import numpy as np
import yaml

from plot_molopt_curves import load_topk_curve


TOP_KS = [1, 10, 100]


def parse_result_path(path):
    parts = path.parts
    try:
        idx = parts.index("oracle_benchmark_results")
    except ValueError:
        raise ValueError(f"Path is not under oracle_benchmark_results: {path}")

    tier = parts[idx + 1]
    oracle = parts[idx + 2]
    algorithm = parts[idx + 3]
    seed = parts[idx + 4].replace("seed_", "")
    return tier, oracle, algorithm, seed


def load_scores(path):
    with open(path) as f:
        data = yaml.safe_load(f) or {}

    rows = []
    for smi, values in data.items():
        if not isinstance(values, list) or len(values) < 2:
            continue
        rows.append((smi, float(values[0]), int(values[1])))
    rows.sort(key=lambda row: row[2])
    return rows


def topk_mean(scores, top_k):
    if not scores:
        return ""
    return float(np.mean(sorted(scores, reverse=True)[:top_k]))


def auc_topk(path, top_k):
    calls, values = load_topk_curve(path, top_k=top_k)
    if len(calls) < 2:
        return ""
    return float(np.trapz(values, calls) / calls[-1])


def summarize_file(path):
    rows = load_scores(path)
    scores = [score for _smi, score, _call in rows]
    calls = [call for _smi, _score, call in rows]
    tier, oracle, algorithm, seed = parse_result_path(path)

    out = {
        "tier": tier,
        "oracle": oracle,
        "algorithm": algorithm,
        "seed": seed,
        "path": str(path),
        "n_molecules": len(rows),
        "max_call": max(calls) if calls else "",
        "best_score": max(scores) if scores else "",
    }
    for top_k in TOP_KS:
        out[f"final_top{top_k}"] = topk_mean(scores, top_k)
    out["auc_top10"] = auc_topk(path, 10)
    return out


def discover_paths(root, tier):
    root_path = Path(root)
    if tier:
        root_path = root_path / tier
    return sorted(root_path.glob("**/results_*.yaml"))


def write_csv(rows, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "tier",
        "oracle",
        "algorithm",
        "seed",
        "n_molecules",
        "max_call",
        "best_score",
        "final_top1",
        "final_top10",
        "final_top100",
        "auc_top10",
        "path",
    ]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| tier | oracle | algorithm | seed | max call | top1 | top10 | top100 | auc top10 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {tier} | {oracle} | {algorithm} | {seed} | {max_call} | {final_top1:.4g} | {final_top10:.4g} | {final_top100:.4g} | {auc_top10:.4g} |".format(
                **row
            )
        )
    output.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="oracle_benchmark_results")
    parser.add_argument("--tier", default="medium")
    parser.add_argument("--csv", default="oracle_benchmark_results/metrics_medium.csv")
    parser.add_argument("--markdown", default="oracle_benchmark_results/metrics_medium.md")
    args = parser.parse_args()

    paths = discover_paths(args.root, args.tier)
    rows = [summarize_file(path) for path in paths]
    rows.sort(key=lambda row: (row["tier"], row["oracle"], row["algorithm"], int(row["seed"])))

    write_csv(rows, Path(args.csv))
    write_markdown(rows, Path(args.markdown))

    print(f"Result files: {len(rows)}")
    print(f"Saved {args.csv}")
    print(f"Saved {args.markdown}")


if __name__ == "__main__":
    main()
