"""Plot one MolOpt benchmark tier.

This scans benchmark outputs like:

oracle_benchmark_results/
  medium/
    qed/
      graph_ga/
        seed_0/
          *.yaml

and writes one top-k optimization curve per oracle.
"""

import argparse
import glob
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from plot_molopt_curves import load_topk_curve


def find_yaml_patterns(root, tier, oracle, algorithm):
    base = Path(root) / tier / oracle / algorithm / "seed_*"
    return [str(base / "*.yaml"), str(base / "*.yml")]


def load_algorithm_summary(root, tier, oracle, algorithm, top_k):
    patterns = find_yaml_patterns(root, tier, oracle, algorithm)

    paths = []
    for pattern in patterns:
        paths.extend(glob.glob(pattern))
    paths = sorted(paths)

    if not paths:
        return None

    loaded = [load_topk_curve(path, top_k=top_k) for path in paths]
    loaded = [(calls, scores) for calls, scores in loaded if len(calls) > 0]
    if not loaded:
        return None

    max_call = max(int(calls[-1]) for calls, _scores in loaded)
    grid = np.arange(1, max_call + 1)
    curves = [np.interp(grid, calls, scores) for calls, scores in loaded]
    curves = np.array(curves)

    return {
        "grid": grid,
        "mean": curves.mean(axis=0),
        "std": curves.std(axis=0),
        "n": len(curves),
        "pattern": patterns,
    }


def discover_algorithms(root, tier, oracle):
    oracle_dir = Path(root) / tier / oracle
    if not oracle_dir.exists():
        return []
    return sorted(path.name for path in oracle_dir.iterdir() if path.is_dir())


def plot_oracle(root, tier, oracle, algorithms, top_k, output_dir):
    if algorithms == ["all"]:
        algorithms = discover_algorithms(root, tier, oracle)

    summaries = {}
    for algorithm in algorithms:
        summary = load_algorithm_summary(root, tier, oracle, algorithm, top_k)
        if summary is None:
            print(f"Skipping {oracle}/{algorithm}: no YAML files found")
            continue
        summaries[algorithm] = summary

    if not summaries:
        return

    plt.figure(figsize=(7, 4.5))
    for algorithm, summary in summaries.items():
        grid = summary["grid"]
        mean = summary["mean"]
        std = summary["std"]
        plt.plot(grid, mean, label=f"{algorithm} (n={summary['n']})", linewidth=2)
        plt.fill_between(grid, mean - std, mean + std, alpha=0.18)

    plt.xlabel("oracle calls")
    plt.ylabel(f"top{top_k} average")
    plt.title(oracle)
    plt.legend()
    plt.tight_layout()

    output = Path(output_dir) / tier / f"{oracle}_top{top_k}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=300)
    plt.close()
    print(f"Saved {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="oracle_benchmark_results")
    parser.add_argument("--tier", default="medium")
    parser.add_argument(
        "--algorithms",
        nargs="+",
        default=["graph_ga"],
        help="Use all, or names like graph_ga smiles_ga stoned.",
    )
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--output-dir", default="oracle_benchmark_plots")
    parser.add_argument(
        "--oracles",
        nargs="+",
        default=None,
        help="Optional oracle names. If omitted, plot every oracle folder found.",
    )
    args = parser.parse_args()

    tier_dir = Path(args.root) / args.tier
    if args.oracles is None:
        oracles = sorted(path.name for path in tier_dir.iterdir() if path.is_dir())
    else:
        oracles = args.oracles

    output_dir = Path(args.output_dir) / args.tier
    output_dir.mkdir(parents=True, exist_ok=True)

    for oracle in oracles:
        plot_oracle(
            root=args.root,
            tier=args.tier,
            oracle=oracle,
            algorithms=args.algorithms,
            top_k=args.top_k,
            output_dir=output_dir.parent,
        )


if __name__ == "__main__":
    main()
