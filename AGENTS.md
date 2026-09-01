# Agent Guide

## Mission

This repository is the development harness for `Amrex_Overlap`, a compressible
Navier--Stokes overset-grid solver using near-wall unstructured meshes,
far-field AMReX Cartesian meshes, and TIOGA assembly.

The parent repository owns reproducible work. `solver/` owns solver source and
history as a Git submodule.

## Start Here

1. Read `ARCHITECTURE.md` and the active `cases/<case>/README.md`.
2. Inspect both repositories with `git status` and record both revisions.
3. Establish the smallest relevant baseline before editing.
4. Make one scoped change; build and test at the nearest useful level.
5. Run only from a frozen case snapshot under a new artifact directory.
6. Report commands, evidence, failures, and anything not verified.

Do not invent build, run, or validation commands. Until stable wrappers exist,
discover them from the pinned solver revision and record the exact commands
used.

## Repository Contract

- Keep harness code, cases, experiment metadata, and lightweight evidence in
  this repository.
- Keep solver code changes in `solver/`. Commit there first, then update the
  parent gitlink in a separate parent-repository commit.
- Solver edits are allowed when the task requests solver development,
  optimization, or architecture work. Do not move solver source into the
  parent repository.
- Preserve unrelated and pre-existing user changes in both repositories.
- Never commit credentials, private keys, machine secrets, or licensed data.
- Do not treat process exit code `0` as numerical or physical validation.
- Do not weaken an acceptance criterion after seeing a result. Create a new
  criterion revision and a new run.

Use subagents for independent source mapping, review, or result analysis when
that keeps the main context clean. Avoid concurrent edits to the same files.

## Experiment Contract

`cases/<case>/` is the editable source of truth. Every execution uses an input
snapshot at `artifacts/<case>/<run-id>/inputs/`.

A run must bind:

- harness revision and dirty state;
- solver revision, nested submodule revisions, and dirty state;
- input file SHA-256 values;
- build configuration and executable SHA-256;
- exact command, environment summary, resources, timestamps, and exit status;
- criterion-level validation results and evidence paths.

Inputs are immutable once execution begins. A terminal run directory is
append-only; retry with a new run ID. Small manifests, logs, metrics, and
verdicts may be committed. Large plotfiles, checkpoints, binaries, and archives
stay outside Git and are indexed by path or URI, size, SHA-256, and retention.

Accepted results require clean harness and solver revisions. Dirty exploratory
runs are allowed only when marked non-accepting and their diffs are preserved.

## Initial Roadmap

- [x] Define repository and artifact contracts.
- [ ] Authenticate and add `Amrex_Overlap` at `solver/` as a submodule.
- [ ] Map the checked-out solver build, mesh, TIOGA, time-integration, and I/O
  paths in `ARCHITECTURE.md`.
- [ ] Add one portable entry point for environment checks, build, run, record,
  and validate operations.
- [ ] Add a minimal smoke case and a deterministic baseline artifact.
- [ ] Add focused regression cases before architecture or performance work.

