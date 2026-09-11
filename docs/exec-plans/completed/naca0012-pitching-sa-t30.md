# Rejected NACA0012 pitching 2D SA diagnostic run to time 30

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
- four inner pseudo steps per physical step; runtime fixed-point mode 2 used
  Anderson acceleration around the legacy partitioned Dual-LUSGS map, not the
  global SPGMR solve;
- stored-Jacobian reuse disabled and no residual stopping threshold active;
- plot and bulk unstructured snapshots disabled; coupled AMReX and
  unstructured restart checkpoints written every 500 steps.

These settings were adapted from the solver's earlier short 10-rank SA run,
which ended at time 5.2, well before the maximum pitch angle. The extension
also used a 100 by 100 base background grid rather than the 200 by 200 grid
recorded in that report. Completion of the extension does not qualify its
physical result.

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
  code zero. Its original completion and finite-value checks passed.
- 2026-09-11: review of the lift curve and runtime-selected solver path rejected
  the run as physical validation. `dt` and CFL were each relaxed by a factor of
  ten relative to the original smoke profile, only four fixed pseudo steps were
  performed without residual stopping, fixed-point mode 2 bypassed SPGMR for
  an Anderson-accelerated partitioned Dual-LUSGS map, stored-Jacobian reuse was
  off, and the mesh-motion speed estimate stayed zero. Time 30 covers only
  0.339 of the approximately 88.50-unit pitching period and stops on the first
  downstroke, so the run cannot establish a closed hysteresis loop or periodic
  response.

## Outcome

The run reached step 3000 and time 30 with 3000 finite force rows spanning
time 0 through 29.99 and no explicit non-finite or bad-state diagnostic. The
force ranges were `Cl=[0.589711, 1.58039]` and
`Cd=[0.0597362, 0.900858]`. Six paired checkpoints were recorded at steps 500
through 3000, and each unstructured checkpoint contains ten rank files.

The run record is
`artifacts/naca0012-pitching-2d/run-20260911T091449Z-9238956-sa10-t30`.
The original machine-readable case outcome is `PASS` because the validator
only checked completion, finite force values, explicit bad-state diagnostics,
and checkpoint presence. That verdict is insufficient for numerical or
physical acceptance and is withdrawn as a validation claim. The artifact
qualification remains `INCOMPLETE` because the source snapshot captured the
user's pre-existing `.gitignore` modification. The retained run establishes
execution and restart integrity through time 30 only.
