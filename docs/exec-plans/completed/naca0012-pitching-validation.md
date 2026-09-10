# NACA0012 pitching validation case

## Objective

Recover the historical NACA0012 pitching inputs and run evidence from the
authorized `102` workstation, compare its leading `AmrexOverlap` source with
the solver revision selected by this harness, and establish the recovered case
as the first repository validation case with a recorded 100-step local run.

## Scope

- read-only discovery below the remote user's `~/dev` and `~/dev_codes` trees;
- a source and Git-history comparison between the remote leading solver and
  the local `solver/` submodule;
- `cases/naca0012-pitching-2d/` for authoritative, reviewable case inputs;
- the smallest solver changes required to run the recovered coupled path
  without interactive input;
- an append-only run record below `artifacts/naca0012-pitching-2d/`;
- documentation updates required by the resulting supported workflow.

## Evidence and decisions

- Record remote repository revisions, status, file paths, sizes, and hashes
  before copying candidate inputs.
- Never store or print the workstation password in repository files, logs, or
  the final report.
- Treat historical output as provenance and regression evidence, not as proof
  of physical correctness.
- Define the first run's criteria before evaluating its output. A successful
  100-step execution establishes smoke and regression evidence only unless the
  recovered history contains an independently justified physical reference.
- Preserve the user's existing root `.gitignore` modification.
- The older checkout is `/home/ws102/dev/Amrex_Overlap` at detached revision
  `2cbf80a`; the leading checkout is
  `/home/ws102/dev-codes/Amrex_Overlap` at observed dirty revision `5091481`.
  The leading committed line continues through `456b6c2`, and its merge base
  with the local pre-task solver line is `1058499`.
- The leading line activates the coupled entry point; adds cell-centered LSQ
  interpolation, preprocessing masks, donor and exchange repairs, runtime
  output routing, restart diagnostics, SUNDIALS GMRES, SA and time-step
  controls, and 2D/3D fixes; and adds solver-native probes and tests. The dirty
  remote worktree is retained only as recovery evidence under
  `artifacts/recovery/ws102-20260910/` and was not copied wholesale.
- The historical case was run with 16 MPI ranks. The recovered mesh has 39,949
  nodes, 79,450 faces, and 39,501 cells. The harness case aligns the AMReX and
  scene free-stream values at Mach 0.4 and Reynolds number 3.4e6; the historical
  AMReX input had conflicting values, so its force series is advisory.

## Work

1. [x] Establish the authorized SSH connection and inventory `~/dev` and
   `~/dev_codes` without modifying the remote workstation.
2. [x] Identify the pitching NACA0012 `.grd`, `.sne`, AMReX input, launch
   command, and relevant historical outputs; record hashes and provenance.
3. [x] Identify the leading remote `AmrexOverlap` repository and compare Git
   ancestry, tracked source, configuration, and coupled execution behavior
   against local `solver/`.
4. [x] Import the minimum authoritative case payload into
   `cases/naca0012-pitching-2d/` and document parameters, provenance, fidelity,
   run assumptions, and initial acceptance criteria.
5. [x] Apply and build any solver changes required for a deterministic,
   non-interactive 2D coupled run.
6. [x] Freeze the case into a new run record, run exactly 100 physical steps,
   extract available metrics, and issue a criterion-level verdict.
7. [x] Update supported operations and architecture documentation, record exact
   checks and limitations, and move this plan to `completed/` only when the
   requested run and evidence are complete.

## Initial acceptance boundary

The first run must execute exactly 100 requested physical steps with exit code
zero, contain no reported NaN or Inf values, retain all required input and
provenance evidence, and produce the solver outputs needed for later numerical
comparison. Additional force, moment, conservation, or pitching-period
criteria will be added only when their definitions and evidence are recovered
from the historical case or established from an independent source.

## Outcome

Completed on 2026-09-10.

- Solver commit `26c0f50` merges the committed leading line through `456b6c2`,
  adds SUNDIALS 6.4.1, removes required startup pauses, corrects the EnTT include
  root, makes wall-distance HDF5 reads independent and path-safe, and wires two
  MPI-aware CTest checks. Solver commit `4bf5a2f` then restricts `Riemann3D` to
  the Euler and SST configurations that provide its initialization symbols.
- `cmake --preset superbuild -DOVERLAP_MPI_ROOT=$PWD/artifacts/install/openmpi`
  succeeded. The system MPICH
  installation hung in a minimal `MPI_Init` probe, so Open MPI 4.1.6 was built
  below `artifacts/` from the official archive with verified SHA-256
  `44da277b8cdc234e71c62473305a09d63f4dcca292ca40335aab7c4bf0e6a566`.
- `cmake --build --preset solver-matrix --parallel 4` completed with exit code
  zero after stale MPICH variant caches and their ExternalProject stamps were
  removed. All six `BackgroundSolver` binaries resolve Open MPI's local
  `libmpi.so.40`. The final selected matrix contains 15 executables.
- The first matrix migration attempt failed when CMake cleared the old
  compiler-bound caches and then could not recover `HDF5_DIR`. The second
  failed because the binary directories were removed without their
  ExternalProject stamps. The clean build then exposed an unsupported
  `Riemann3D`/3D-SA link (`sa_initdata`), which `4bf5a2f` resolves by expressing
  the actual executable/model boundary. Logs are retained under
  `artifacts/logs/solver-matrix-*.log`.
- `ctest --test-dir artifacts/build/solver/2d-sst --output-on-failure` passed
  2/2 tests in 0.41 seconds after the final matrix build.
- Run `run-20260910T180036Z-de29ce85` completed preprocessing and exactly 100
  physical steps on 16 Open MPI ranks in 257 seconds including validation. The
  command exited zero, reached time 0.1, wrote 100 force rows from time 0 to
  0.099, reported no non-finite states, and had empty stderr. Observed ranges
  were `Cl=[1.00078, 1.07047]` and `Cd=[0.278894, 0.617563]`.
- Every case-level criterion passed. The artifact-level verdict is
  `INCOMPLETE`, as required by `ARCHITECTURE.md`, because the pre-run harness
  snapshot contained the user's pre-existing `.gitignore` modification. The
  solver snapshot was clean. All frozen-input and recorded-output hashes were
  reverified after finalization.
- `git diff --check` remains nonzero for inherited whitespace in the recovered
  mesh and leading solver line. The mesh is preserved byte-for-byte with its
  remote SHA-256; broad numerical-source formatting was deliberately excluded.
