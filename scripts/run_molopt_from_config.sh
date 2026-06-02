#!/bin/bash
#SBATCH --account=pcon0041
#SBATCH --job-name=molopt-cfg
#SBATCH --time=12:00:00
#SBATCH --nodes=1 --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus-per-node=1
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.error

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")}"
source /fs/ess/PCON0041/rezaaverly/miniconda3/etc/profile.d/conda.sh
conda activate molopt-liddia

CONFIG_PATH="${1:-benchmark_configs/medium_cheap.yaml}"

export MPLCONFIGDIR="${TMPDIR:-/tmp}/molopt-mpl-${SLURM_JOB_ID:-$$}"
export XDG_CACHE_HOME="${TMPDIR:-/tmp}/molopt-cache-${SLURM_JOB_ID:-$$}"
mkdir -p "$MPLCONFIGDIR" "$XDG_CACHE_HOME"

python run_molopt_benchmark_config.py "$CONFIG_PATH"
