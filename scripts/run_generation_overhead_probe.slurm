#!/bin/bash
#SBATCH --account=pcon0041
#SBATCH --job-name=molopt-gen-probe
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus-per-node=1
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.error

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")}"

if command -v conda >/dev/null 2>&1; then
    eval "$(conda shell.bash hook)"
elif [[ -f /fs/ess/PCON0041/rezaaverly/miniconda3/etc/profile.d/conda.sh ]]; then
    source /fs/ess/PCON0041/rezaaverly/miniconda3/etc/profile.d/conda.sh
else
    echo "Conda initialization was not found." >&2
    exit 1
fi

conda activate "${MOLOPT_ENV:-molopt-liddia}"

WORKSPACE_ROOT="$(cd .. && pwd)"
export PYTHONPATH="${WORKSPACE_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

/usr/bin/time -v python run_molopt_benchmark_config.py \
  benchmark_configs/generation_overhead_probe.yaml
