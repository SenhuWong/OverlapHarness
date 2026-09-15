# Architecture

OverlapHarness is an engineering and research harness for a compressible
Navier--Stokes solver around moving bodies. The numerical solver combines AMReX
Cartesian grids, an unstructured near-body solver, and TIOGA overset
connectivity.

## Ownership Boundaries

The harness owns build orchestration, case definitions, runtime isolation,
research records, and qualification policy. Numerical algorithms and solver
executables remain in the `solver/` repository. Third-party source is selected
by the nested gitlinks under `solver/vendor/`.

Harness and solver are separate Git repositories. The parent `solver/` gitlink
identifies the solver revision used by the harness. A solver change is committed
in the submodule before the parent gitlink advances. Generated state must not be
written into either Git worktree.

## Coupled Solver Flow

```text
case and geometry
  -> unstructured near-body mesh and flow solver
  -> AMReX Cartesian background mesh and flow solver
  -> TIOGA connectivity, blanking, interpolation, and exchange
  -> coupled physical-time advance
  -> solution fields and diagnostic metrics
```

`MeshLoader` creates the unstructured solver data and registers TIOGA mesh
blocks. `AmrLevelRans` exposes Cartesian patch geometry, state, and blanking
data. TIOGA connects both mesh systems and performs two-way exchange. The
unstructured and Cartesian solvers retain their own numerical-method
boundaries.

## Build Boundary

The root superbuild owns shared HDF5 and SUNDIALS builds and six isolated solver
configurations. Dimension and turbulence selection affect compiled sources,
definitions, and generated Fortran indices, so each combination has its own
CMake cache and generated-module directory.

Dependencies may share an artifact root only when compiler, MPI, dependency
options, ABI, and build type are compatible. Build commands and cache cleanup
live in `docs/operations.md`; the six combinations and isolation rationale live
in `docs/build-layout.md`.

## Cases and Evidence

`cases/` contains version-controlled definitions of numerical work: essential
inputs, parameters, run instructions, and any current checks or reference data.
Each case owns its case-specific workflow. Generated run state must be written
outside the case directory.

`artifacts/runtime/` contains machine-local run directories, logs, generated
inputs, checkpoints, fields, and other intermediate data. It is ignored by Git
and may remain only on the machine that performed the work.

`artifacts/records/` contains curated, Git-tracked research summaries. A record
groups the experiments needed to answer one research question and normally
contains one Markdown document plus selected figures. It is not a complete
ledger of every run.

An automated `PASS` means only that the checks defined for that case met their
tolerances. It does not by itself establish physical validity or final human
acceptance. Detailed physical acceptance policy remains case-specific and must
not be invented before supporting results exist.

## Instruction Boundary

When work is launched from the OverlapHarness root, root harness documents are
authoritative for orchestration, builds, cases, runs, validation, and plans.
Solver-local agent documents are non-authoritative context for harness work;
consult them only when useful and verify their claims against current code and
tests.
