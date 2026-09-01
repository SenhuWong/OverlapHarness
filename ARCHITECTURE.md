# Architecture

## Current State

`solver/` is connected over SSH as a Git submodule and initially pinned to
`71244518cdf74cda4591e312aab2e64f351ef4f1` on upstream `master`. The source map
below is verified at that revision. It must be reviewed when the gitlink moves.

The checkout is source-complete for tracked files but is not build-qualified:
its dependency closure is incomplete and this host lacks the required build
toolchain. No solver test or numerical claim is established by this document.

## Repository Layout

```text
Amrex_Overlap_autodev/
|-- AGENTS.md                 agent entry point and roadmap
|-- ARCHITECTURE.md           stable boundaries and provenance contract
|-- .gitignore                generated and large-payload exclusions
|-- solver/                   Amrex_Overlap Git submodule
|   |-- CMakeLists.txt        top-level build and executable selection
|   |-- source/               AMReX levels and coupled orchestration
|   |-- UnstructSolver/       unstructured discretization/time integration
|   |-- UniTioga/             overset connectivity and exchange
|   |-- MathTools/            mesh/search geometry utilities
|   |-- Exec/                 executable-specific sources and AMReX inputs
|   `-- bg_inputs/            coupled scene, grid, and background inputs
|-- cases/
|   `-- <case>/
|       |-- README.md         purpose, parameters, and acceptance criteria
|       `-- ...               authoritative editable inputs
|-- artifacts/
|   |-- README.md
|   |-- _template/            tracked run-record templates
|   `-- <case>/<run-id>/      one append-only execution record
`-- tools/                    future thin build/run/record wrappers
```

The parent repository does not vendor solver history. Its gitlink selects the
solver revision used by cases, tools, and recorded experiments.

## Verified Solver Map

| Path | Observed responsibility |
| --- | --- |
| `solver/CMakeLists.txt` | Configures AMReX, HDF5, MPI-facing libraries, turbulence policy, and executable targets. |
| `solver/source/main.cpp` | Contains the active AMReX entry point and the currently dormant coupled orchestration function. |
| `solver/source/AmrLevelRans/` | AMReX state, RK4 advance, blank-aware Cartesian RHS, AMR patch exposure, and coupling callbacks. |
| `solver/source/MeshLoader.*` | Partitions/loads unstructured grids, builds solver mesh data, and registers TIOGA blocks. |
| `solver/UnstructSolver/source/` | Unstructured mesh ownership, MPI halo exchange, flux/turbulence strategies, and LUSGS/Dual-LUSGS advance. |
| `solver/UniTioga/source/` | Mesh and Cartesian block registration, hole cutting, donor search, interpolation, blanking, and data exchange. |
| `solver/MathTools/source/` | ADT, bounding-box, geometry, and low-level numerical utilities. |
| `solver/Exec/*` | Problem-specific Fortran/C++ sources and AMReX input files selected by CMake. |
| `solver/bg_inputs/` | Coupled NACA scene/grid examples referenced by the dormant coupled path. |

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
blanking fields. TIOGA performs mesh/mesh and mesh/AMR connectivity plus the
two-way field exchange. The unstructured physical-time path uses Dual-LUSGS
inner iterations; the Cartesian path uses RK4 and blank-aware RHS kernels.

## Current Execution and Build Boundary

The default `main()` does **not** enter the coupled flow: its call to
`loader_test_samrai()` is commented. It initializes AMReX, writes a plotfile,
and advances AMR time steps. The coupled function contains mesh loading, TIOGA
connectivity, callback registration, and Dual-LUSGS exchange, but it and the
active AMReX setup contain interactive `std::cin.get()` pauses. `CartWrapper`
is fully commented and is not an active abstraction.

Build qualification is blocked by two independent facts:

- `solver/CMakeLists.txt` requires `vendor/glm`, `vendor/yaml-cpp`,
  `vendor/HDF5`, `vendor/entt`, and `vendor/amrex-25.06`; `vendor/` is absent
  and ignored, while the declared AMReX nested submodule has no gitlink at the
  pinned revision;
- this host currently has no `cmake`, C/C++/Fortran compiler, or MPI wrapper.

No CTest/test target is registered. A prebuilt x86-64 METIS shared library is
tracked under `solver/Depend/`, so portable builds must replace or explicitly
qualify it. AMReX restart and checkpoint overrides currently throw “not
implemented”. These are roadmap facts, not changes made by the harness.

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

`tools/` will remain a thin orchestration layer around solver-native commands.
Its first stable interface should cover environment inspection, configure/build,
case freeze, run, artifact finalization, and validation. Numerical algorithms
remain in `solver/`; case-specific parameters remain in `cases/`; tools must not
silently change either.
