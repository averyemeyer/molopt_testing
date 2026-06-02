"""Run a MolOpt benchmark from a YAML protocol config."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def load_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        raise ValueError(f"Config must be a mapping: {path}")
    return config


def build_command(config):
    command = [
        sys.executable,
        "run_molopt_oracle_tests.py",
        "--tier",
        config["tier"],
        "--smi-file",
        config.get("smi_file", "molecule.smi"),
        "--output-root",
        config.get("output_root", "oracle_benchmark_results"),
        "--n-jobs",
        str(config.get("n_jobs", 1)),
    ]

    oracles = as_list(config.get("oracles"))
    oracle_set = config.get("oracle_set")
    if oracle_set in {"all", "cheap", "admet"} and not oracles:
        oracles = [oracle_set]
    if not oracles:
        raise ValueError("Config must specify oracles or oracle_set")
    command.extend(["--oracles", *oracles])

    algorithms = as_list(config.get("algorithms"))
    algorithm_set = config.get("algorithm_set")
    if algorithm_set == "all" and not algorithms:
        algorithms = ["all"]
    elif algorithm_set == "default" and not algorithms:
        algorithms = ["available"]
    if not algorithms:
        raise ValueError("Config must specify algorithms or algorithm_set")
    command.extend(["--algorithms", *algorithms])

    if config.get("skip_existing", False):
        command.append("--skip-existing")
    if config.get("continue_on_error", False):
        command.append("--continue-on-error")
    if config.get("debug", False):
        command.append("--debug")

    return command


def merged_env(config):
    env = os.environ.copy()
    for key, value in (config.get("env") or {}).items():
        if key == "PYTHONPATH" and env.get("PYTHONPATH"):
            env[key] = f"{value}:{env[key]}"
        else:
            env[key] = str(value)
    return env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Benchmark YAML config path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_config(config_path)
    command = build_command(config)

    print(f"Benchmark config: {config_path}")
    print("Command:")
    print(" ".join(command))

    if args.dry_run:
        return

    subprocess.run(command, check=True, env=merged_env(config))


if __name__ == "__main__":
    main()
