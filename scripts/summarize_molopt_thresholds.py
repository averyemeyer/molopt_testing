"""Summarize oracle-call budgets needed to reach score thresholds."""

import argparse
import csv
from pathlib import Path

import numpy as np

from plot_molopt_benchmark_tier import discover_algorithms, load_algorithm_summary


def threshold_call(grid, mean, threshold):
    hits = np.where(mean >= threshold)[0]
    if len(hits) == 0:
        return None
    return int(grid[int(hits[0])])


def default_thresholds(oracle):
    if oracle == "qed":
        return [0.90, 0.93, 0.94, 0.945]
    if oracle == "sascore":
        return [8.0, 8.5, 8.9]
    if oracle in {"herg", "dili", "clintox", "mutagenicity", "carcinogens"}:
        return [0.8, 0.9, 0.95, 0.99]
    if oracle == "logp":
        return [5, 10, 15, 20]
    return []


def parse_thresholds(values):
    thresholds = {}
    for value in values or []:
        oracle, raw = value.split(":", 1)
        thresholds[oracle] = [float(item) for item in raw.split(",") if item]
    return thresholds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="oracle_benchmark_results")
    parser.add_argument("--tier", default="full")
    parser.add_argument("--oracles", nargs="+", required=True)
    parser.add_argument("--algorithms", nargs="+", default=["all"])
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--threshold", action="append", default=[])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    explicit_thresholds = parse_thresholds(args.threshold)
    rows = []
    for oracle in args.oracles:
        algorithms = (
            discover_algorithms(args.root, args.tier, oracle)
            if args.algorithms == ["all"]
            else args.algorithms
        )
        thresholds = explicit_thresholds.get(oracle, default_thresholds(oracle))
        for algorithm in algorithms:
            summary = load_algorithm_summary(
                args.root, args.tier, oracle, algorithm, args.top_k
            )
            if summary is None:
                continue
            grid = summary["grid"]
            mean = summary["mean"]
            final_score = float(mean[-1])
            for threshold in thresholds:
                call = threshold_call(grid, mean, threshold)
                rows.append(
                    {
                        "tier": args.tier,
                        "oracle": oracle,
                        "algorithm": algorithm,
                        "top_k": args.top_k,
                        "n_seeds": summary["n"],
                        "threshold": threshold,
                        "call_to_threshold": "" if call is None else call,
                        "final_score": final_score,
                        "reached": call is not None,
                    }
                )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "tier",
        "oracle",
        "algorithm",
        "top_k",
        "n_seeds",
        "threshold",
        "call_to_threshold",
        "final_score",
        "reached",
    ]
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {output} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
