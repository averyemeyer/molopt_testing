"""Summarize MolOpt benchmark result coverage.

Writes a CSV and Markdown table showing which tier/oracle/algorithm/seed
combinations have a saved results_*.yaml file.
"""

import argparse
import csv
from pathlib import Path


TIERS = {
    "small": [0],
    "medium": [0, 1, 2],
    "full": [0, 1, 2, 3, 4],
}

CHEAP_ORACLES = [
    "sascore",
    "qed",
    "mol_wt",
    "logp",
    "tpsa",
    "hbd",
    "hba",
    "rot_bonds",
]

ADMET_ORACLES = [
    "herg",
    "dili",
    "clintox",
    "mutagenicity",
    "carcinogens",
]

ALL_ORACLES = CHEAP_ORACLES + ADMET_ORACLES

DEFAULT_ALGORITHMS = [
    "graph_ga",
    "screening",
    "smiles_ga",
    "stoned",
    "graph_mcts",
    "moldqn",
    "gpbo",
    "reinvent",
    "reinvent_selfies",
    "mimosa",
    "selfies_ga",
]

ALL_ALGORITHMS = DEFAULT_ALGORITHMS + ["smiles_vae", "jt_vae"]


def discover_oracles(root, tier):
    tier_dir = Path(root) / tier
    if not tier_dir.exists():
        return []
    return sorted(path.name for path in tier_dir.iterdir() if path.is_dir())


def oracle_group(oracle):
    if oracle in CHEAP_ORACLES:
        return "cheap"
    if oracle in ADMET_ORACLES:
        return "admet"
    return "other"


def has_result(root, tier, oracle, algorithm, seed):
    seed_dir = Path(root) / tier / oracle / algorithm / f"seed_{seed}"
    return any(seed_dir.glob("results_*.yaml"))


def select_oracles(root, tiers, oracle_set, explicit_oracles):
    if explicit_oracles:
        return explicit_oracles
    if oracle_set == "all":
        return ALL_ORACLES
    if oracle_set == "cheap":
        return CHEAP_ORACLES
    if oracle_set == "admet":
        return ADMET_ORACLES

    discovered = set()
    for tier in tiers:
        discovered.update(discover_oracles(root, tier))
    return sorted(discovered)


def summarize(root, tiers, oracles, algorithms):
    rows = []
    for tier in tiers:
        seeds = TIERS[tier]
        for oracle in oracles:
            for algorithm in algorithms:
                present = [
                    seed
                    for seed in seeds
                    if has_result(root, tier, oracle, algorithm, seed)
                ]
                missing = [seed for seed in seeds if seed not in present]
                rows.append(
                    {
                        "tier": tier,
                        "oracle_group": oracle_group(oracle),
                        "oracle": oracle,
                        "algorithm": algorithm,
                        "complete": len(missing) == 0,
                        "present": " ".join(map(str, present)) or "-",
                        "missing": " ".join(map(str, missing)) or "-",
                        "n_present": len(present),
                        "n_expected": len(seeds),
                    }
                )
    return rows


def write_csv(rows, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "tier",
                "oracle_group",
                "oracle",
                "algorithm",
                "complete",
                "present",
                "missing",
                "n_present",
                "n_expected",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| tier | group | oracle | algorithm | status | present seeds | missing seeds |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        status = "complete" if row["complete"] else "missing"
        lines.append(
            "| {tier} | {oracle_group} | {oracle} | {algorithm} | {status} | {present} | {missing} |".format(
                status=status,
                **row,
            )
        )
    output.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="oracle_benchmark_results")
    parser.add_argument("--tiers", nargs="+", choices=sorted(TIERS), default=["medium"])
    parser.add_argument(
        "--oracle-set",
        choices=["all", "cheap", "admet", "discovered"],
        default="all",
        help="Expected oracle set to report. Default is all LIDDIA oracles.",
    )
    parser.add_argument(
        "--oracles",
        nargs="+",
        default=None,
        help="Explicit oracle names. Overrides --oracle-set.",
    )
    parser.add_argument(
        "--algorithm-set",
        choices=["default", "all"],
        default="default",
        help="Default excludes optional VAE algorithms, matching run_molopt_oracle_tests.py available runs.",
    )
    parser.add_argument("--algorithms", nargs="+", default=None)
    parser.add_argument("--csv", default="oracle_benchmark_results/coverage_medium.csv")
    parser.add_argument("--markdown", default="oracle_benchmark_results/coverage_medium.md")
    args = parser.parse_args()

    algorithms = args.algorithms
    if algorithms is None:
        algorithms = ALL_ALGORITHMS if args.algorithm_set == "all" else DEFAULT_ALGORITHMS
    oracles = select_oracles(args.root, args.tiers, args.oracle_set, args.oracles)

    rows = summarize(args.root, args.tiers, oracles, algorithms)
    rows.sort(
        key=lambda row: (
            row["tier"],
            row["oracle_group"],
            row["oracle"],
            row["algorithm"],
        )
    )

    write_csv(rows, Path(args.csv))
    write_markdown(rows, Path(args.markdown))

    complete = sum(1 for row in rows if row["complete"])
    missing = len(rows) - complete
    expected_seed_runs = sum(row["n_expected"] for row in rows)
    present_seed_runs = sum(row["n_present"] for row in rows)
    print(f"Rows: {len(rows)}")
    print(f"Complete rows: {complete}")
    print(f"Rows with missing seeds: {missing}")
    print(f"Seed runs present: {present_seed_runs}/{expected_seed_runs}")
    print(f"Saved {args.csv}")
    print(f"Saved {args.markdown}")


if __name__ == "__main__":
    main()
