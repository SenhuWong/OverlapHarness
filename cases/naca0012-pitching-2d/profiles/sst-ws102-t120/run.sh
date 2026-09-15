#!/usr/bin/env bash
#SBATCH --job-name=naca-sst-t120
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --time=0
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=thenwhowon@gmail.com

set -euo pipefail

run_root=${SLURM_SUBMIT_DIR:?submit this script with sbatch}
cd "$run_root"

harness_root=$(git -C "$run_root" rev-parse --show-toplevel)
solver="$harness_root/artifacts/build/solver/2d-sst/BackgroundSolver"
partition_file=InterMesh/_cell_32_naca0012_sharp.grd.h5

test -x "$solver"
test -r "$partition_file"
mkdir -p logs
trap 'status=$?; printf "%s\n" "$status" > logs/run.exitcode' EXIT

solver_args=(inputs/inputs)
if [[ ${OVERLAP_PREFLIGHT:-0} == 1 ]]; then
  solver_args+=(max_step=1 amr.check_int=1 unstruct.checkpoint_int=1)
fi

echo "Job started on $(hostname) at $(date --iso-8601=seconds)"
echo "Harness revision: $(git -C "$harness_root" rev-parse HEAD)"
echo "Solver revision: $(git -C "$harness_root/solver" rev-parse HEAD)"
echo "MPI ranks: ${SLURM_NTASKS:?}"
echo "Mode: $([[ ${OVERLAP_PREFLIGHT:-0} == 1 ]] && echo preflight || echo full)"

mpirun --bind-to core --map-by core -np "$SLURM_NTASKS" \
  "$solver" "${solver_args[@]}"
