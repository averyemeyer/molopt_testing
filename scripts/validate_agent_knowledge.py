#!/usr/bin/env python3
"""Validate and export the agent-facing MolOpt benchmark knowledge."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / "agent_knowledge"
YAML_PATH = KNOWLEDGE_DIR / "molopt_benchmark_knowledge.yaml"
JSON_PATH = KNOWLEDGE_DIR / "molopt_benchmark_knowledge.json"
SCHEMA_PATH = KNOWLEDGE_DIR / "schema.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-json",
        action="store_true",
        help="Regenerate the JSON mirror from the canonical YAML file.",
    )
    return parser.parse_args()


def load_yaml() -> dict:
    with YAML_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def validate_source_paths(data: dict) -> list[str]:
    source_paths: set[str] = {
        data["benchmark_context"]["starter_set"]["path"],
        data["benchmark_context"]["score_contract"]["wrapper_source"],
        data["runtime_model"]["generation_probe"]["source_table"],
        data["runtime_model"]["admet_scoring"]["source_table"],
    }
    for profile in data["objective_profiles"]:
        for evidence in profile["evidence"]:
            source_paths.update(evidence["source_tables"])
    return sorted(path for path in source_paths if not (ROOT / path).is_file())


def validate_unique_ids(data: dict) -> None:
    for key in ("objective_profiles", "algorithm_profiles"):
        ids = [item["id"] for item in data[key]]
        duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
        if duplicates:
            raise ValueError(f"Duplicate IDs in {key}: {duplicates}")


def main() -> None:
    args = parse_args()
    data = load_yaml()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(data)
    validate_unique_ids(data)

    missing = validate_source_paths(data)
    if missing:
        raise FileNotFoundError(f"Missing cited source files: {missing}")

    rendered = json.dumps(data, indent=2, sort_keys=False) + "\n"
    if args.write_json:
        JSON_PATH.write_text(rendered, encoding="utf-8")
        print(f"Wrote {JSON_PATH.relative_to(ROOT)}")
    elif not JSON_PATH.is_file():
        raise FileNotFoundError(
            f"{JSON_PATH.relative_to(ROOT)} is missing; run with --write-json"
        )
    elif JSON_PATH.read_text(encoding="utf-8") != rendered:
        raise ValueError(
            "JSON mirror differs from YAML; run with --write-json and commit both"
        )

    print(
        "Validated "
        f"{len(data['objective_profiles'])} objective profiles and "
        f"{len(data['algorithm_profiles'])} algorithm profiles."
    )


if __name__ == "__main__":
    main()
