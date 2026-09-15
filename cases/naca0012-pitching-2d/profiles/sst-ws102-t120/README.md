# Workstation-102 SST run to time 120

This profile is the long-running, human-reviewed target case for workstation
102. It uses 32 MPI ranks, SST k-omega, Mach 0.4, Reynolds number 3.4e6, and the
large pitching motion recorded by the parent case. The finest-level timestep is
0.001; with `max_level=4`, the nominal coarse timestep is 0.016.

The `20 x 20` level-0 grid and `max_level=4` are candidate settings until the
five-level preprocessing summary and one-step Slurm preflight succeed. The full
run stops at physical time 120, about 1.36 pitching periods, so completion does
not establish periodic convergence or final acceptance.

## Prepare

From the harness root on workstation 102, create a machine-local run directory
and freeze this profile:

```bash
harness_root=$(pwd)
run_id=sst-ws102-t120-$(date -u +%Y%m%dT%H%M%SZ)
run_root="$harness_root/artifacts/runtime/naca0012-pitching-2d/$run_id"
mkdir -p "$run_root/inputs" "$run_root/logs"
cp cases/naca0012-pitching-2d/profiles/sst-ws102-t120/inputs \
  cases/naca0012-pitching-2d/profiles/sst-ws102-t120/Ranswzm.sne \
  cases/naca0012-pitching-2d/naca0012_sharp.grd "$run_root/inputs/"
cp cases/naca0012-pitching-2d/profiles/sst-ws102-t120/run.sh \
  cases/naca0012-pitching-2d/profiles/sst-ws102-t120/monitor.sh "$run_root/"
```

Generate the 32-way partition and all masks needed for levels 0 through 4:

```bash
cd "$run_root"
"$harness_root/artifacts/build/solver/2d-sst/tests/mesh_preprocessor_2d" \
  inputs/naca0012_sharp.grd --dim 2 --nparts 32 --levels 5 \
  --reference-length 0.2 --skip-tecplot
```

Inspect the reported per-level donor and mask counts before proceeding.

## Launch

Exercise the actual Slurm, MPI, TIOGA, SST, and output path for one coarse step:

```bash
sbatch --export=ALL,OVERLAP_PREFLIGHT=1 run.sh
```

Prepare a fresh runtime directory after the preflight. The standard full launch
from that directory is:

```bash
sbatch run.sh
```

Start hourly machine-local monitoring with the returned job ID:

```bash
nohup ./monitor.sh JOB_ID >/dev/null 2>&1 &
```

AMReX and unstructured checkpoints are written as a pair every 50 coarse steps,
nominally every 0.8 physical-time units. A restart must select matching step and
time directories from both output trees. Slurm sends `END` and `FAIL` mail to
the configured project address; `monitor.sh` records hourly scheduler state and
checkpoint progress and sends an additional message for terminal failures.
