"""Plot MolOpt optimization curves from YAML result files.

Expected YAML format:

CCO:
- 0.40680796565539457
- 1

where each entry is:
  SMILES:
    - score
    - oracle_call_number
"""

import argparse
import glob
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml


def load_topk_curve(path, top_k=10):
    with open(path) as f:
        data = yaml.safe_load(f)

    rows = []
    for _smi, values in data.items():
        if not isinstance(values, list) or len(values) < 2:
            continue
        score = float(values[0])
        call = int(values[1])
        rows.append((call, score))

    rows.sort(key=lambda row: row[0])

    seen = []
    calls = []
    topk_scores = []

    for call, score in rows:
        seen.append(score)
        top_scores = sorted(seen, reverse=True)[:top_k]
        calls.append(call)
        topk_scores.append(float(np.mean(top_scores)))

    return np.array(calls), np.array(topk_scores)


def interpolate_to_grid(calls, scores, grid):
    if len(calls) == 0:
        return None
    return np.interp(grid, calls, scores)


def plot_curves(pattern, output, title, label, top_k):
    paths = sorted(glob.glob(pattern))
    if not paths:
        raise FileNotFoundError(f"No YAML files matched: {pattern}")

    loaded = [load_topk_curve(path, top_k=top_k) for path in paths]
    max_call = max(int(calls[-1]) for calls, _scores in loaded if len(calls) > 0)
    grid = np.arange(1, max_call + 1)

    curves = []
    for calls, scores in loaded:
        curve = interpolate_to_grid(calls, scores, grid)
        if curve is not None:
            curves.append(curve)

    curves = np.array(curves)
    mean = curves.mean(axis=0)
    std = curves.std(axis=0)

    plt.figure(figsize=(7, 4.5))
    plt.plot(grid, mean, label=label, linewidth=2)
    plt.fill_between(grid, mean - std, mean + std, alpha=0.2)
    plt.xlabel("oracle calls")
    plt.ylabel(f"top{top_k} average")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    print(f"Matched {len(paths)} files")
    print(f"Saved {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pattern",
        required=True,
        help="Glob pattern for result YAML files, e.g. 'results/qed/graph_ga/seed_*/results.yaml'",
    )
    parser.add_argument("--output", default="molopt_top10_curve.png")
    parser.add_argument("--title", default="MolOpt optimization curve")
    parser.add_argument("--label", default="Graph GA")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    plot_curves(
        pattern=args.pattern,
        output=args.output,
        title=args.title,
        label=args.label,
        top_k=args.top_k,
    )


if __name__ == "__main__":
    main()
