"""Time direct evaluator ADMET calls versus MolOpt oracle wrappers.

This is intended to run inside the same Slurm resource shape as benchmark jobs.
It writes CSV rows for cold and warm calls so we can separate model load time
from per-molecule prediction time.
"""

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_SMILES = [
    "CCO",
    "CC(=O)Oc1ccccc1C(=O)O",
    "CN1CCC[C@H]1c2cccnc2",
]

ENDPOINTS = ["herg", "dili", "clintox", "mutagenicity", "carcinogens"]


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "mode",
        "label",
        "endpoint",
        "smiles_index",
        "smiles",
        "seconds",
        "value",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def timed_row(mode, label, endpoint, smiles_index, smiles, fn):
    start = time.perf_counter()
    value = fn(smiles)
    seconds = time.perf_counter() - start
    return {
        "mode": mode,
        "label": label,
        "endpoint": endpoint,
        "smiles_index": smiles_index,
        "smiles": smiles,
        "seconds": f"{seconds:.6f}",
        "value": json.dumps(value, sort_keys=True),
    }


def run_direct(smiles_list, output):
    from evaluator.tools import predict_toxicity

    rows = []
    for idx, smiles in enumerate(smiles_list):
        label = "cold" if idx == 0 else "warm"
        rows.append(
            timed_row(
                mode="direct_predict_toxicity",
                label=label,
                endpoint="all_toxicity",
                smiles_index=idx,
                smiles=smiles,
                fn=predict_toxicity,
            )
        )
    write_csv(output, rows)


def run_oracle(smiles_list, output):
    import liddia_oracles

    rows = []
    first = True
    for idx, smiles in enumerate(smiles_list):
        for endpoint in ENDPOINTS:
            label = "cold" if first else "warm"
            first = False
            rows.append(
                timed_row(
                    mode="molopt_oracle_wrapper",
                    label=label,
                    endpoint=endpoint,
                    smiles_index=idx,
                    smiles=smiles,
                    fn=getattr(liddia_oracles, endpoint),
                )
            )
    write_csv(output, rows)


def read_rows(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))


def summarize(rows):
    groups = {}
    for row in rows:
        key = (row["mode"], row["label"], row["endpoint"])
        groups.setdefault(key, []).append(float(row["seconds"]))

    summary = []
    for (mode, label, endpoint), values in sorted(groups.items()):
        summary.append(
            {
                "mode": mode,
                "label": label,
                "endpoint": endpoint,
                "n": len(values),
                "mean_seconds": sum(values) / len(values),
                "min_seconds": min(values),
                "max_seconds": max(values),
            }
        )
    return summary


def orchestrate(args):
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    direct_csv = output_dir / "direct_predict_toxicity_timing.csv"
    oracle_csv = output_dir / "molopt_oracle_timing.csv"
    combined_csv = output_dir / "direct_vs_oracle_admet_timing.csv"
    summary_json = output_dir / "direct_vs_oracle_admet_timing_summary.json"

    base_cmd = [sys.executable, str(Path(__file__).resolve())]
    common = [
        "--smiles",
        *args.smiles,
    ]
    subprocess.run(
        [*base_cmd, "--mode", "direct", "--output-csv", str(direct_csv), *common],
        check=True,
    )
    subprocess.run(
        [*base_cmd, "--mode", "oracle", "--output-csv", str(oracle_csv), *common],
        check=True,
    )

    rows = read_rows(direct_csv) + read_rows(oracle_csv)
    write_csv(combined_csv, rows)
    summary_json.write_text(json.dumps(summarize(rows), indent=2, sort_keys=True) + "\n")
    print(f"Saved {combined_csv}")
    print(f"Saved {summary_json}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["orchestrate", "direct", "oracle"],
        default="orchestrate",
    )
    parser.add_argument("--output-dir", default="direct_vs_oracle_timing")
    parser.add_argument("--output-csv", default=None)
    parser.add_argument("--smiles", nargs="+", default=DEFAULT_SMILES)
    args = parser.parse_args()

    if args.mode == "direct":
        run_direct(args.smiles, Path(args.output_csv))
    elif args.mode == "oracle":
        run_oracle(args.smiles, Path(args.output_csv))
    else:
        orchestrate(args)


if __name__ == "__main__":
    main()
