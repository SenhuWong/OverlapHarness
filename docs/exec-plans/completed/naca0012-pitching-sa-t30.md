# NACA0012 pitching 2D SA run to time 30

## Objective

Run the recovered NACA0012 pitching case locally with the two-dimensional
Spalart--Allmaras solver on 10 MPI ranks through nondimensional physical time
30, while preserving enough evidence and synchronized restart state to audit
or resume the calculation.

## Frozen numerical configuration

- solver variant: `AMReX_SPACEDIM=2`, `TURB_MODEL=SA`, Release;
- MPI allocation: 10 ranks bound to hardware threads; the WSL allocation
  exposed seven physical cores and thirteen hardware threads;
- mesh partition count: 10;
- free stream and motion: Mach 0.4, Reynolds number 3.4e6, mean angle 6.25
  degrees, amplitude 8.5 degrees, reduced frequency 0.075;
- unstructured physical step: 0.01;
- terminal condition: step 3000 at time 30;
- AMR: maximum level 2, no subcycling, CFL 1.0;
- SA far-field ratio: `nu_tilde / nu = 3.0`;
- stored-Jacobian SUNDIALS GMRES: four pseudo steps per physical step;
- plot and bulk unstructured snapshots disabled; coupled AMReX and
  unstructured restart checkpoints written every 500 steps.

These settings extend the solver's previously recorded 10-rank SA validation
configuration from time 5.2 to time 30. They do not change the pitching case's
physical definition.

## Acceptance criteria

1. The mesh preprocessor succeeds and produces a 10-partition HDF5 mesh.
2. The MPI process exits with status zero at step 3000 and time 30.
3. The force history has 3000 strictly increasing finite rows from time 0
   through 29.99.
4. Solver logs contain no explicit non-finite or bad-state diagnostic.
5. Every scheduled AMReX/unstructured checkpoint pair is present, and the
   final pair records step 3000.

The recovered short SST history is advisory only and is not an SA acceptance
baseline.

## Execution

1. Rebuild `solver-2d-sa` and run its two MPI-aware CTest checks.
2. Create a unique directory under `artifacts/naca0012-pitching-2d/`, capture
   source status, and freeze the case inputs with the SA/time overrides.
3. Preprocess the grid for 10 partitions and record hashes and logs.
4. Run on 10 MPI ranks, retaining stdout, stderr, force history, and restart
   checkpoints. Monitor physical-step progress and resource use without
   editing either source worktree.
5. Validate the terminal state and write the manifest, metrics, external
   inventory, and outcome.
6. Record the supported SA command in `docs/operations.md`, then move this plan
   to `docs/exec-plans/completed/` with the measured outcome.

## Status

- 2026-09-11: 2D SA rebuild succeeded; both solver-native CTest checks passed.
- 2026-09-11: two-step preflight passed with the intended SA/GMRES and AMR
  configuration.
- 2026-09-11: the formal 3000-step run completed in 2508.37 seconds with exit
  code zero. All case criteria passed.

## Outcome

The run reached step 3000 and time 30 with 3000 finite force rows spanning
time 0 through 29.99 and no explicit non-finite or bad-state diagnostic. The
force ranges were `Cl=[0.589711, 1.58039]` and
`Cd=[0.0597362, 0.900858]`. Six paired checkpoints were recorded at steps 500
through 3000, and each unstructured checkpoint contains ten rank files.

The run record is
`artifacts/naca0012-pitching-2d/run-20260911T091449Z-9238956-sa10-t30`.
Case outcome is `PASS`; artifact qualification is `INCOMPLETE` because the
source snapshot captured the user's pre-existing `.gitignore` modification.
This run establishes stable completion and finite force history through time
30. No experimental SA accuracy criterion was evaluated.
