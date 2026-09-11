# Architecture

OverlapHarness is an engineering harness for developing and qualifying a
compressible Navier--Stokes solver for flows around moving bodies. The solver
combines AMReX Cartesian grids, a near-wall unstructured solver, and TIOGA
overset connectivity. The harness owns reproducible builds, cases, run records,
and validation evidence; numerical implementation remains in the solver
repository.

## Repository Layout

```text
OverlapHarness/
|-- AGENTS.md                 agent entry point and repository rules
|-- ARCHITECTURE.md           stable boundaries and provenance contract
|-- CMakeLists.txt            dependency and six-variant superbuild
|-- CMakePresets.json         supported configure/build entry points
|-- .gitignore                generated and large-payload exclusions
|-- .agents/skills/           project-local agent workflows and helpers
|-- docs/                     design, operations, and execution plans
|-- solver/                   Amrex_Overlap Git submodule
|   |-- CMakeLists.txt        solver configuration and executable selection
|   |-- source/               AMReX levels and coupled orchestration
|   |-- UnstructSolver/       unstructured discretization/time integration
|   |-- UniTioga/             overset connectivity and exchange
|   |-- MathTools/            mesh/search geometry utilities
|   |-- Exec/                 executable-specific sources and AMReX inputs
|   |-- bg_inputs/            coupled scene, grid, and background inputs
|   `-- vendor/               six nested source submodules
|-- cases/
|   `-- <case>/
|       |-- README.md         purpose, parameters, and acceptance criteria
|       `-- ...               authoritative editable inputs
|-- artifacts/
|   |-- README.md
|   |-- _template/            tracked run-record templates
|   |-- build/                generated dependency and solver build trees
|   |-- install/              generated dependency installations
|   `-- <case>/<run-id>/      one append-only execution record
`-- tools/                    future debugging and visualization utilities
```

## Source and Submodule Contract

The harness repository does not copy solver or dependency history. Its
`solver/` gitlink selects the solver revision used by cases, tools, and recorded
experiments. The solver repository owns six nested vendor gitlinks under
`solver/vendor/`: HDF5, AMReX, EnTT, GLM, yaml-cpp, and SUNDIALS. A recursive
submodule initialization must reproduce all seven source identities, including
the solver gitlink, without generated files.

Builds and installs never write into either Git worktree. They belong under the
harness-level `artifacts/` tree. A solver change is committed in `solver/`
before the parent gitlink is advanced, so a parent commit never depends on an
uncommitted submodule state.

## Verified Solver Map

| Path | Observed responsibility |
| --- | --- |
| `solver/CMakeLists.txt` | Configures AMReX, parallel HDF5, MPI-facing libraries, turbulence policy, and executable targets. |
| `solver/source/main.cpp` | Contains the active AMReX entry point and coupled mesh loading, connectivity, exchange, and advance orchestration. |
| `solver/source/AmrLevelRans/` | AMReX state, RK4 advance, model policies, blank-aware Cartesian RHS, AMR patch exposure, and coupling callbacks. |
| `solver/source/MeshLoader.*` | Partitions and loads unstructured grids, builds solver mesh data, and registers TIOGA blocks. |
| `solver/UnstructSolver/source/` | Owns unstructured meshes, MPI halo exchange, flux and turbulence strategies, and LUSGS/Dual-LUSGS advance. |
| `solver/UniTioga/source/` | Registers mesh and Cartesian blocks and performs hole cutting, donor search, interpolation, blanking, and data exchange. |
| `solver/MathTools/source/` | Provides ADT, bounding-box, geometry, and low-level numerical utilities. |
| `solver/Exec/*` | Provides problem-specific Fortran/C++ sources and AMReX input files selected by CMake. |
| `solver/bg_inputs/` | Holds coupled scene, grid, and background-input examples. Harness validation inputs live under `cases/`. |

The implemented coupled data flow is:

```text
case + geometry
  -> near-wall unstructured mesh
  -> far-field AMReX Cartesian mesh
  -> TIOGA overset connectivity and field exchange
  -> compressible Navier--Stokes advance
  -> solution, diagnostics, and validation metrics
```

`MeshLoader` creates both unstructured solver data and TIOGA `MeshBlock` data.
`AmrLevelRans` exposes AMReX `MultiFab` patch geometry, solution pointers, and
blanking fields. TIOGA performs mesh-to-mesh and mesh-to-AMR connectivity plus
two-way field exchange. The unstructured physical-time path uses Dual-LUSGS
inner iterations; the Cartesian path uses RK4 and blank-aware RHS kernels.

## Build Boundary

The root superbuild owns shared parallel HDF5 and SUNDIALS builds plus six
independent solver configurations:

```text
artifacts/
|-- build/
|   |-- superbuild/           CMake orchestration cache and stamps
|   |-- dependencies/hdf5/    parallel HDF5 build tree
|   |-- dependencies/sundials/ SUNDIALS build tree
|   `-- solver/
|       |-- 2d-euler/
|       |-- 2d-sst/
|       |-- 2d-sa/
|       |-- 3d-euler/
|       |-- 3d-sst/
|       `-- 3d-sa/
|-- install/hdf5/             shared parallel HDF5 installation
`-- install/sundials/         shared SUNDIALS installation
```

`AMReX_SPACEDIM` changes AMReX configuration and compiled behavior.
`TURB_MODEL` changes compile definitions, model-specific Fortran sources, and
the generated `turb_indices.f90`. Each combination therefore owns a separate
CMake cache and generated-module directory. HDF5 and SUNDIALS may be shared
only while the compiler, MPI implementation, dependency options, and build
type remain identical. `OVERLAP_MPI_ROOT` binds the MPI C, C++, and Fortran
wrappers and launcher across both dependencies and all solver variants; when
it is empty, the superbuild selects wrappers from `PATH`.

| Variant | Dimension | Model | Selected executables |
| --- | ---: | --- | --- |
| `2d-euler` | 2 | `EULER` | `BackgroundSolver`, `RichtmyerMeshkovInstability`, `Riemann2D`, `ShockBubble`, `Sphere` |
| `2d-sst` | 2 | `SST` | `BackgroundSolver` |
| `2d-sa` | 2 | `SA` | `BackgroundSolver` |
| `3d-euler` | 3 | `EULER` | `BackgroundSolver`, `TaylorGreenVortex`, `Riemann3D` |
| `3d-sst` | 3 | `SST` | `BackgroundSolver`, `TaylorGreenVortex`, `Riemann3D` |
| `3d-sa` | 3 | `SA` | `BackgroundSolver`, `TaylorGreenVortex` |

On 2026-09-10 all six Release configurations and all 15 selected executables
built successfully with GNU 13.3, a harness-local Open MPI 4.1.6, parallel
HDF5 2.0.0, and SUNDIALS 6.4.1. All six `BackgroundSolver` binaries resolve
`libmpi.so.40` from that Open MPI installation. This is build qualification;
the 3D SA binaries remain compile-qualified only because their AMReX SA RHS
kernels explicitly stop at runtime when the unsupported path is selected.

The active `main()` calls `loader_test_samrai()` and enters the coupled path.
It loads preprocessed unstructured partitions, registers TIOGA connectivity,
constructs the AMReX hierarchy, and advances the coupled solvers. Required
startup paths are non-interactive; diagnostic pauses remain only on exceptional
failure paths. `CartWrapper` is fully commented and is not an active
abstraction.

The solver registers two CTest checks: generation of a one-partition
preprocessed mesh fixture and a cell-centered LSQ MeshLoader test consuming
that fixture. Current builds still report warnings including an AMReX
boundary-condition copy over-read diagnostic, HDF5 size-type narrowing,
`#pragma once` in implementation files, and `MPICH_SKIP_MPICXX` redefinition.
A prebuilt x86-64 METIS shared library is tracked under `solver/Depend/`, so
portable builds must replace or explicitly qualify it.

The first harness numerical case is `cases/naca0012-pitching-2d`. Its initial
16-rank local run completed 100 coupled 2D SST physical steps and passed the
case-level execution and finite-force criteria. The run record remains
artifact-qualified as `INCOMPLETE` because the harness source snapshot included
a pre-existing `.gitignore` modification; this does not change its numerical
criterion results.

The same case now carries a tested `profiles/sa-t30` configuration. On
2026-09-11, the 2D SA solver ran 3000 steps on 10 MPI ranks through physical
time 30 with AMR levels 0 through 2 and four SUNDIALS GMRES pseudo steps. It
produced 3000 finite force samples and six synchronized AMReX/unstructured
checkpoint pairs, including the terminal step. All case criteria passed. Its
artifact qualification is also `INCOMPLETE` solely because the captured
harness snapshot retained the same pre-existing `.gitignore` modification;
the solver snapshot was clean.

Supported configure, build, cleanup, and run-record commands are defined in
`docs/operations.md`; the rationale and extension rules for the matrix are in
`docs/build-layout.md`.

## Two-Repository Development Model

Harness and solver revisions are independent identities:

1. Reproduce or create a baseline and record both revisions.
2. Develop solver changes on a branch inside `solver/`.
3. Build and validate the solver change against a frozen case snapshot.
4. Commit the solver change in its repository.
5. Update the parent gitlink and any matching case or validation metadata.

This order preserves a reviewable solver commit and a reviewable harness commit.
A parent commit must never imply that a dirty submodule result is reproducible.

## Execution Data Flow

```text
cases/<case>/
  -- freeze + hash --> artifacts/<case>/<run-id>/inputs/
  -- build/run -----> logs + small metrics + large external payloads
  -- validate ------> criterion results + final verdict
  -- record --------> manifest binding both Git revisions and all evidence
```

Runs must not execute directly from the live case directory. Failed runs are
evidence and are retained; an input or source change creates a new run.

## Artifact Contract

Use a UTC-based unique ID such as `run-20260901T153012Z-a1b2c3d4`. A run begins
mutable, but its `inputs/` is frozen before execution. After a terminal verdict,
the directory is append-only.

```text
artifacts/<case>/<run-id>/
|-- ATTEMPT.md       purpose, decisions, limitations, and concise handoff
|-- manifest.json    machine-readable identity and provenance
|-- inputs/          immutable snapshot with per-file SHA-256
|-- logs/            stdout, stderr, build, and validator logs
|-- metrics.json     compact physical and numerical measurements
|-- verdict.json     criterion-level PASS/FAIL/INCOMPLETE result
`-- external.json    index of untracked large payloads
```

The manifest schema starts at version `1` and records:

- run ID, case ID, purpose, parent run, and UTC start/end;
- harness SHA/dirty evidence and solver SHA/dirty evidence/nested revisions;
- input paths, sizes, and SHA-256 values;
- compiler, MPI, dependencies, configuration, build command, and executable
  SHA-256;
- host/resource summary, exact execution command, and exit status;
- paths to metrics, verdict, logs, and externally stored payloads.

Each nested-submodule record carries path, revision, dirty state, and hashed
status evidence. Commands are stored as `argv`, working directory, and launcher,
not as an ambiguous shell transcript.

Execution state and validation outcome are separate. Execution moves through
`CREATED`, `RUNNING`, then `COMPLETED` or `FAILED`. `verdict.json` uses
`NOT_RUN`, `PASS`, `FAIL`, or `INCOMPLETE` and binds the frozen criterion
definition by path and SHA-256. `PASS` requires completed execution, clean
source snapshots, all required evidence, and every required criterion passing.

Large payloads are not committed. `external.json` records each payload's
logical role, file/directory kind, path or URI, byte size, and retention status.
Files use SHA-256 directly. Directories use a sorted per-file inventory of
relative path, size, and SHA-256 plus the inventory file's SHA-256. The artifact
is incomplete if required external evidence cannot be located or verified.

Harness cleanliness is sampled immediately before the run directory is
created; files added while recording that artifact do not retroactively dirty
the source snapshot. Environment capture is allowlist-only and redacted.

## Planned Harness Boundary

`tools/` remains a thin orchestration layer around solver-native commands. Its
first stable interface should cover environment inspection, configure/build,
case freeze, run, artifact finalization, and validation. Numerical algorithms
remain in `solver/`; case-specific parameters remain in `cases/`; tools must not
silently change either.
