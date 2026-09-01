# Architecture

## Current State

The harness repository was initialized before solver access was available.
`solver/` is therefore a planned submodule boundary until GitHub authentication
is completed. Solver-internal paths below remain intentionally unspecified and
must be replaced with observed paths after checkout.

## Repository Layout

```text
Amrex_Overlap_autodev/
|-- AGENTS.md                 agent entry point and roadmap
|-- ARCHITECTURE.md           stable boundaries and provenance contract
|-- .gitignore                generated and large-payload exclusions
|-- solver/                   Amrex_Overlap Git submodule (pending access)
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

## Solver Model

The intended numerical data flow, based on the project contract, is:

```text
case + geometry
  -> near-wall unstructured mesh
  -> far-field AMReX Cartesian mesh
  -> TIOGA overset connectivity and field exchange
  -> compressible Navier--Stokes advance
  -> solution, diagnostics, and validation metrics
```

This is a logical model, not yet a verified source map. After submodule
checkout, record the actual directories and call boundaries for:

- build and dependency configuration;
- AMReX Cartesian-grid ownership;
- unstructured near-wall discretization;
- TIOGA registration, connectivity, interpolation, and blanking;
- conservative state exchange and boundary treatment;
- compressible fluxes, time integration, and restart/I/O;
- unit, regression, and example cases.

Do not infer file ownership from names alone; confirm it from code and tests.

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
- harness SHA/dirty state and solver SHA/dirty state/nested revisions;
- input paths, sizes, and SHA-256 values;
- compiler, MPI, dependencies, configuration, build command, and executable
  SHA-256;
- host/resource summary, exact execution command, and exit status;
- paths to metrics, verdict, logs, and externally stored payloads.

`verdict.json` evaluates named criteria with value, unit, comparison, threshold,
status, and evidence path. Allowed terminal outcomes are `PASS`, `FAIL`, and
`INCOMPLETE`; `PASS` requires every required criterion to pass. An execution
that merely completed is `RUN_COMPLETE`, not automatically `PASS`.

Large payloads are not committed. `external.json` records each payload's
logical role, path or URI, byte size, SHA-256, and retention status. The artifact
is incomplete if required external evidence cannot be located or its hash no
longer matches.

## Planned Harness Boundary

`tools/` will remain a thin orchestration layer around solver-native commands.
Its first stable interface should cover environment inspection, configure/build,
case freeze, run, artifact finalization, and validation. Numerical algorithms
remain in `solver/`; case-specific parameters remain in `cases/`; tools must not
silently change either.

