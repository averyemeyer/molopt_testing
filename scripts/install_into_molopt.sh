#!/bin/bash

set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-}"
EXPECTED_COMMIT="63382d78890e910080ef9a9b3b6d04a4552aff85"
PATCH_PATH="${SOURCE_ROOT}/patches/mol-opt-compatibility.patch"

if [[ -z "$TARGET" ]]; then
    echo "Usage: $0 /path/to/mol-opt" >&2
    exit 2
fi

TARGET="$(cd "$TARGET" && pwd)"

if [[ ! -f "${TARGET}/molopt/base.py" ]] || [[ ! -d "${TARGET}/.git" ]]; then
    echo "Target is not a MolOpt Git clone: ${TARGET}" >&2
    exit 1
fi

CURRENT_COMMIT="$(git -C "$TARGET" rev-parse HEAD)"
if [[ "$CURRENT_COMMIT" != "$EXPECTED_COMMIT" ]]; then
    echo "Warning: patch was prepared against ${EXPECTED_COMMIT}." >&2
    echo "Current target commit: ${CURRENT_COMMIT}" >&2
fi

if git -C "$TARGET" apply --check "$PATCH_PATH" 2>/dev/null; then
    git -C "$TARGET" apply "$PATCH_PATH"
    echo "Applied MolOpt compatibility patch."
elif git -C "$TARGET" apply --reverse --check "$PATCH_PATH" 2>/dev/null; then
    echo "MolOpt compatibility patch is already applied."
else
    echo "Compatibility patch does not apply cleanly." >&2
    exit 1
fi

mkdir -p "${TARGET}/benchmark_configs" "${TARGET}/benchmark_inputs"
cp -R "${SOURCE_ROOT}/configs/." "${TARGET}/benchmark_configs/"
cp "${SOURCE_ROOT}/inputs/zinc_sanity_1k.smi" "${TARGET}/benchmark_inputs/"
cp "${SOURCE_ROOT}"/scripts/*.py "${TARGET}/"
cp "${SOURCE_ROOT}/scripts/run_molopt_from_config.sh" "${TARGET}/"
cp "${SOURCE_ROOT}/scripts/run_direct_vs_oracle_timing.sh" "${TARGET}/"
cp "${SOURCE_ROOT}/scripts/run_generation_overhead_probe.slurm" "${TARGET}/"
chmod +x \
    "${TARGET}/run_molopt_from_config.sh" \
    "${TARGET}/run_direct_vs_oracle_timing.sh" \
    "${TARGET}/run_generation_overhead_probe.slurm"

echo "Installed benchmark harness into ${TARGET}"
echo "Run a dry check with:"
echo "  cd ${TARGET}"
echo "  python run_molopt_benchmark_config.py benchmark_configs/medium_cheap.yaml --dry-run"
