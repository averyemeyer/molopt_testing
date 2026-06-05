"""Run MolOpt oracle benchmark tests.

Starts with GraphGA and writes one output folder per:
  tier / oracle / algorithm / seed

Example:
  python run_molopt_oracle_tests.py --tier small
  python run_molopt_oracle_tests.py --tier medium --oracles cheap
  python run_molopt_oracle_tests.py --tier full --oracles qed sascore herg
"""

import argparse
import importlib
import json
import resource
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import torch

from liddia_oracles import (
    carcinogens,
    clintox,
    dili,
    generation_probe,
    hba,
    hbd,
    herg,
    logp,
    mol_wt,
    mutagenicity,
    qed,
    rot_bonds,
    sascore,
    tpsa,
)


TIERS = {
    "small": {
        "max_oracle_calls": 100,
        "seeds": [0],
        "freq_log": 10,
        "patience": 5,
    },
    "small_replicate": {
        "max_oracle_calls": 100,
        "seeds": [0, 1, 2],
        "freq_log": 10,
        "patience": 5,
    },
    "medium": {
        "max_oracle_calls": 1000,
        "seeds": [0, 1, 2],
        "freq_log": 50,
        "patience": 10,
    },
    "full": {
        "max_oracle_calls": 10000,
        "seeds": [0, 1, 2, 3, 4],
        "freq_log": 100,
        "patience": 20,
    },
    "generation_probe": {
        "max_oracle_calls": 500,
        "seeds": [0],
        "freq_log": 500,
        "patience": 100,
    },
}


CHEAP_ORACLES = {
    "sascore": sascore,
    "qed": qed,
    "mol_wt": mol_wt,
    "logp": logp,
    "tpsa": tpsa,
    "hbd": hbd,
    "hba": hba,
    "rot_bonds": rot_bonds,
}


ADMET_ORACLES = {
    "herg": herg,
    "dili": dili,
    "clintox": clintox,
    "mutagenicity": mutagenicity,
    "carcinogens": carcinogens,
}

PROBE_ORACLES = {
    "generation_probe": generation_probe,
}


ALL_ORACLES = {
    **CHEAP_ORACLES,
    **ADMET_ORACLES,
    **PROBE_ORACLES,
}


ALGORITHM_CANDIDATES = {
    "graph_ga": [("molopt.graph_ga", "GraphGA")],
    "screening": [("molopt.screening", "Screening")],
    "smiles_ga": [("molopt.smiles_ga", "SmilesGA")],
    "stoned": [("molopt.stoned", "Stoned")],
    "graph_mcts": [("molopt.graph_mcts", "Graph_MCTS")],
    "moldqn": [("molopt.moldqn", "MolDQN")],
    "gpbo": [("molopt.gpbo", "GPBO")],
    "reinvent": [("molopt.reinvent", "REINVENT")],
    "reinvent_selfies": [("molopt.reinvent_selfies", "REINVENT_SELFIES")],
    "mimosa": [("molopt.mimosa", "MIMOSA")],
    "selfies_ga": [("molopt.selfies_ga", "SelfiesGA")],
    "smiles_vae": [("molopt.smiles_vae", "SmilesVAE")],
    "jt_vae": [("molopt.jt_vae", "JTVAE")],
}


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


ALGORITHM_CONFIGS = {
    "smiles_vae": "molopt/smiles_vae/hparams_default.yaml",
    "jt_vae": "molopt/jt_vae/hparams_default.yaml",
}


ALGORITHM_SMI_FILE_OVERRIDES = {
    "jt_vae": None,
}


def load_algorithm(name):
    errors = []
    for module_name, class_name in ALGORITHM_CANDIDATES[name]:
        try:
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        except Exception as exc:
            errors.append(f"{module_name}.{class_name}: {exc}")
    raise ImportError("\n".join(errors))


def available_algorithms():
    found = {}
    missing = {}
    for name in ALGORITHM_CANDIDATES:
        try:
            found[name] = load_algorithm(name)
        except ImportError as exc:
            missing[name] = str(exc)
    return found, missing


def select_algorithms(names):
    found, missing = available_algorithms()

    if names == ["all"]:
        return found
    if names == ["available"]:
        return {
            name: found[name]
            for name in DEFAULT_ALGORITHMS
            if name in found
        }

    selected = {}
    for name in names:
        if name not in ALGORITHM_CANDIDATES:
            known = ", ".join(sorted(ALGORITHM_CANDIDATES))
            raise ValueError(f"Unknown algorithm '{name}'. Known algorithms: {known}")
        if name not in found:
            raise ImportError(f"Could not import algorithm '{name}':\n{missing[name]}")
        selected[name] = found[name]
    return selected


def debug_oracle(name, fn):
    def wrapped(smi):
        score = fn(smi)
        print(name, smi, score)
        return score

    wrapped.__name__ = name
    return wrapped


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def resource_snapshot():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "user_cpu_seconds": usage.ru_utime,
        "system_cpu_seconds": usage.ru_stime,
        "max_rss_kb": usage.ru_maxrss,
    }


def result_max_call(output_dir):
    calls = []
    for path in output_dir.glob("results_*.yaml"):
        try:
            import yaml

            with path.open() as handle:
                data = yaml.safe_load(handle) or {}
            for values in data.values():
                if isinstance(values, list) and len(values) >= 2:
                    calls.append(int(values[1]))
        except Exception:
            continue
    return max(calls) if calls else None


def write_run_metadata(path, metadata):
    path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


def select_oracles(names):
    if names == ["all"]:
        return ALL_ORACLES
    if names == ["cheap"]:
        return CHEAP_ORACLES
    if names == ["admet"]:
        return ADMET_ORACLES

    selected = {}
    for name in names:
        if name not in ALL_ORACLES:
            known = ", ".join(sorted(ALL_ORACLES))
            raise ValueError(f"Unknown oracle '{name}'. Known oracles: {known}")
        selected[name] = ALL_ORACLES[name]
    return selected


def make_optimizer(
    algorithm_name,
    optimizer_cls,
    smi_file,
    n_jobs,
    max_oracle_calls,
    freq_log,
    output_dir,
):
    optimizer_smi_file = ALGORITHM_SMI_FILE_OVERRIDES.get(algorithm_name, smi_file)
    kwargs = {
        "smi_file": optimizer_smi_file,
        "n_jobs": n_jobs,
        "max_oracle_calls": max_oracle_calls,
        "freq_log": freq_log,
        "output_dir": str(output_dir),
        "log_results": True,
    }

    try:
        return optimizer_cls(**kwargs)
    except TypeError:
        # Some MolOpt methods may not accept n_jobs.
        kwargs.pop("n_jobs")
        return optimizer_cls(**kwargs)


def run_optimizer(
    algorithm_name,
    optimizer_cls,
    oracle_name,
    oracle_fn,
    smi_file,
    output_root,
    tier_name,
    config,
    n_jobs,
    debug,
    skip_existing,
    continue_on_error,
):
    for seed in config["seeds"]:
        output_dir = (
            Path(output_root)
            / tier_name
            / oracle_name
            / algorithm_name
            / f"seed_{seed}"
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        if skip_existing and list(output_dir.glob("results_*.yaml")):
            print(
                f"Skipping existing tier={tier_name} oracle={oracle_name} "
                f"algorithm={algorithm_name} seed={seed} output={output_dir}"
            )
            continue

        print(
            f"Running tier={tier_name} oracle={oracle_name} "
            f"algorithm={algorithm_name} seed={seed} output={output_dir}"
        )

        metadata_path = output_dir / "benchmark_run_metadata.json"
        start_time = time.perf_counter()
        start_resources = resource_snapshot()
        metadata = {
            "tier": tier_name,
            "oracle": oracle_name,
            "algorithm": algorithm_name,
            "seed": seed,
            "output_dir": str(output_dir),
            "smi_file": smi_file,
            "n_jobs": n_jobs,
            "max_oracle_calls_configured": config["max_oracle_calls"],
            "freq_log": config["freq_log"],
            "patience": config["patience"],
            "started_at_utc": utc_now_iso(),
            "status": "running",
        }
        write_run_metadata(metadata_path, metadata)

        previous_default_dtype = torch.get_default_dtype()
        if algorithm_name != "gpbo":
            torch.set_default_dtype(torch.float32)

        try:
            optimizer = make_optimizer(
                algorithm_name=algorithm_name,
                optimizer_cls=optimizer_cls,
                smi_file=smi_file,
                n_jobs=n_jobs,
                max_oracle_calls=config["max_oracle_calls"],
                freq_log=config["freq_log"],
                output_dir=output_dir,
            )

            oracle = debug_oracle(oracle_name, oracle_fn) if debug else oracle_fn
            optimize_kwargs = {
                "oracle": oracle,
                "patience": config["patience"],
                "seed": seed,
            }
            if algorithm_name in ALGORITHM_CONFIGS:
                optimize_kwargs["config"] = ALGORITHM_CONFIGS[algorithm_name]

            optimizer.optimize(**optimize_kwargs)
            metadata["status"] = "succeeded"
        except Exception:
            metadata["status"] = "failed"
            metadata["exception"] = traceback.format_exc()
            print(
                f"FAILED tier={tier_name} oracle={oracle_name} "
                f"algorithm={algorithm_name} seed={seed} output={output_dir}"
            )
            traceback.print_exc()
            if not continue_on_error:
                raise
        finally:
            torch.set_default_dtype(previous_default_dtype)
            end_resources = resource_snapshot()
            metadata.update(
                {
                    "finished_at_utc": utc_now_iso(),
                    "elapsed_seconds": time.perf_counter() - start_time,
                    "actual_max_oracle_call": result_max_call(output_dir),
                    "user_cpu_seconds_delta": (
                        end_resources["user_cpu_seconds"]
                        - start_resources["user_cpu_seconds"]
                    ),
                    "system_cpu_seconds_delta": (
                        end_resources["system_cpu_seconds"]
                        - start_resources["system_cpu_seconds"]
                    ),
                    "max_rss_kb": end_resources["max_rss_kb"],
                }
            )
            write_run_metadata(metadata_path, metadata)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", choices=sorted(TIERS), default="small")
    parser.add_argument(
        "--algorithms",
        nargs="+",
        default=["graph_ga"],
        help=(
            "Use all, available, or names like graph_ga smiles_ga stoned. "
            "'available' excludes smiles_vae and jt_vae by default."
        ),
    )
    parser.add_argument(
        "--oracles",
        nargs="+",
        default=["cheap"],
        help="Use all, cheap, admet, or specific names like qed sascore herg.",
    )
    parser.add_argument("--smi-file", default="molecule.smi")
    parser.add_argument("--output-root", default="oracle_benchmark_results")
    parser.add_argument("--n-jobs", type=int, default=1)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip seed output directories that already contain a results_*.yaml file.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Log optimizer failures and continue with the next seed/algorithm/oracle.",
    )
    parser.add_argument("--list-algorithms", action="store_true")
    args = parser.parse_args()

    if args.list_algorithms:
        found, missing = available_algorithms()
        print("Available algorithms:")
        for name in sorted(found):
            print(f"  {name}")
        print("\nMissing algorithms:")
        for name in sorted(missing):
            print(f"  {name}")
        return

    config = TIERS[args.tier]
    oracles = select_oracles(args.oracles)
    algorithms = select_algorithms(args.algorithms)

    print(f"Tier config: {config}")
    print(f"Selected oracles: {', '.join(oracles)}")
    print(f"Selected algorithms: {', '.join(algorithms)}")

    for oracle_name, oracle_fn in oracles.items():
        for algorithm_name, optimizer_cls in algorithms.items():
            run_optimizer(
                algorithm_name=algorithm_name,
                optimizer_cls=optimizer_cls,
                oracle_name=oracle_name,
                oracle_fn=oracle_fn,
                smi_file=args.smi_file,
                output_root=args.output_root,
                tier_name=args.tier,
                config=config,
                n_jobs=args.n_jobs,
                debug=args.debug,
                skip_existing=args.skip_existing,
                continue_on_error=args.continue_on_error,
            )


if __name__ == "__main__":
    main()
