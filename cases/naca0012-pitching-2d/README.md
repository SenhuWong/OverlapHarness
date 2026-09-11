# Two-dimensional pitching NACA0012

## Purpose and fidelity

This is the harness's first coupled moving-body validation case. It exercises
the 2D SST unstructured near-body solver, sinusoidal rigid-body pitch, TIOGA
connectivity, and the AMReX Cartesian background for exactly 100 physical
steps. Its current qualification level is a runtime and finite-force smoke
test. It does not yet establish agreement with experimental dynamic-stall
data.

The case was recovered from the `102` workstation on 2026-09-10. The principal
historical run was:

```text
/home/ws102/dev-codes/Amrex_Overlap/build-2d-sst/big_naca.wzm
```

The source repository was at commit `509148149e02388a1c53abd2c9f12009b2ef9c6f`
with uncommitted changes. The later committed solver line used by this harness
ends at `456b6c2` before harness-specific dependency integration. Exact source
and file hashes are recorded in `provenance.json`.

## Physical definition

- airfoil: sharp trailing-edge NACA0012 unstructured grid;
- dimension: 2;
- turbulence model: SST k-omega (`TURB_MODEL=SST`, scene `turb: 0`);
- free-stream Mach number: 0.4;
- Reynolds number: 3.4e6;
- mean angle of attack: 6.25 degrees;
- pitch amplitude: 8.5 degrees;
- reduced frequency: 0.075;
- pitch center: `(0.25, 0)` chord;
- unstructured physical step: 0.001 nondimensional time;
- background domain: `[-10.00098, 9.99902]^2` with `100 x 100` level-0 cells;
- AMR maximum level: 0 for this first smoke test;
- dual-time pseudo-step limit: 200 per physical step.

The recovered historical AMReX input specified Mach 0.6 and Reynolds number
4.8e6 while its scene specified Mach 0.4 and Reynolds number 3.4e6. This case
uses 0.4 and 3.4e6 consistently on both sides of the coupled interface. The
historical coefficient series is therefore advisory and is not a required
acceptance baseline.

## Required files

- `inputs`: AMReX and coupled-runtime parameters;
- `Ranswzm.sne`: scene, flow, and prescribed pitching motion;
- `naca0012_sharp.grd`: Cobalt-style unstructured mesh;
- `reference/historical-clcd-first-100.tsv`: first 101 historical force rows,
  including the initial row at time zero;
- `validate.py`: deterministic run-record validator.

The preprocessed partition file is generated per MPI size and must not be
committed. For the canonical 16-rank run, generate it from the run-record root:

```sh
"$HARNESS_ROOT/artifacts/install/openmpi/bin/mpiexec" -n 1 \
  "$HARNESS_ROOT/artifacts/build/solver/2d-sst/tests/mesh_preprocessor_2d" \
  inputs/naca0012_sharp.grd \
  --dim 2 \
  --nparts 16 \
  --levels 1 \
  --reference-length 0.2 \
  --skip-tecplot
```

This writes `InterMesh/_cell_16_naca0012_sharp.grd.h5`. The rank count passed
to the preprocessor and `mpiexec` must match.

## Build and run assumptions

Build configuration: `AMReX_SPACEDIM=2`, `TURB_MODEL=SST`, Release. Freeze the
contents of this directory into `<run>/inputs/`, generate `InterMesh/` in the
run root, and run from that root:

```sh
"$HARNESS_ROOT/artifacts/install/openmpi/bin/mpiexec" \
  --use-hwthread-cpus --bind-to hwthread -n 16 \
  "$HARNESS_ROOT/artifacts/build/solver/2d-sst/BackgroundSolver" \
  inputs/inputs
```

`HARNESS_ROOT` is the absolute path to the harness checkout. The two Open MPI
placement options are required on the current ten-core/twenty-thread local
host because the recovered partition count is 16. A host with at least 16
allocated cores may use its scheduler's normal placement policy instead.

Write the process exit status as an integer followed by a newline to
`logs/run.exitcode`, then validate with:

```sh
python3 inputs/validate.py --run-dir .
```

## Acceptance criteria

All criteria below are required and are evaluated by `validate.py`:

1. `execution-exit-zero`: the MPI command exits with status 0.
2. `accepted-physical-steps`: the solver completion log reaches step 100.
3. `solver-final-time`: the step-100 completion time is 0.1 within an absolute
   tolerance of `1e-10` nondimensional time.
4. `force-history-sample-count`: the force history contains 100 rows. The
   coupled driver records coefficients at the beginning of each physical step.
5. `force-history-time-range`: force times are strictly increasing from 0 to
   0.099 within an absolute tolerance of `1e-10` nondimensional time.
6. `force-history-finite`: every reported time, lift, drag, and optional moment
   coefficient is finite.
7. `no-reported-nonfinite-state`: stdout and stderr contain none of the solver's
   explicit bad-state or non-finite diagnostics.

The validator reports differences from the recovered force series as advisory
metrics. Those differences do not affect the verdict because the recovered
binary cannot be bound to a clean source revision and the historical AMReX and
unstructured free-stream parameters disagreed.

The tested 10-rank 2D SA configuration through time 30 is stored separately in
`profiles/sa-t30/`. Its README defines the SA acceptance criteria; the
top-level `inputs` and `Ranswzm.sne` remain the original 100-step SST smoke
profile.
