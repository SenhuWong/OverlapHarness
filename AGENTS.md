# Agent Entry Point

## Purpose

OverlapHarness is an iterative engineering and research harness for developing
and validating a compressible Navier--Stokes solver for flows around moving
bodies with overset grids. The moving-boundary coupled solver is the project
goal; this statement does not imply that every coupled path is already
production-ready.

The harness preserves the solver's architectural boundaries while coordinating
changes in the `solver/` submodule, including maintenance, refactoring, feature
development, and numerical-method research. Work should follow an auditable
loop: inspect the current evidence, state a hypothesis or task, implement the
smallest justified change, build the affected configurations, run frozen cases
when a numerical claim is involved, evaluate explicit metrics, and record the
outcome. Agents may carry out that loop autonomously within the requested scope,
but must not redefine the physical objective, weaken acceptance criteria, or
present unvalidated results as established conclusions.

## Start Here

- Read `ARCHITECTURE.md` before code-affecting or file-structure changes.
- Use `docs/index.md` to locate the current design and operating documents.
- Follow `docs/operations.md` for supported dependency, build, run, cleanup,
  and validation commands.
- Use applicable project-local skills under `.agents/skills/`.
- For multi-step or risky work, maintain an execution plan under
  `docs/exec-plans/active/`.

## Repository Rules

- Keep changes scoped to the requested task and preserve unrelated user work.
- Treat the harness and `solver/` as separate Git repositories. Commit solver
  changes in the submodule before updating the parent gitlink.
- Do not use global skills unless the user's prompt explicitly names the skill;
  task matching alone is not authorization. Project-local `.agents/skills/`
  remain available when applicable.
- Never commit passwords, tokens, private keys, or machine-specific secrets.
- Runs, checkpoints, generated files, verification attempts, and disposable
  scratch files belong only in `artifacts/`.
- A project-local skill must keep every required CLI and deterministic helper
  below its own `.agents/skills/<skill>/` directory. Local skills must be
  self-contained.
- Do not edit either Git worktree while a build or validation command is
  running against it.
- Do not expand allowed changes or weaken checks, pass/stop conditions, tests,
  or tolerances without explicit user approval.
- Report conflicts among code, tests, architecture, and design documents; do
  not silently choose one and discard contrary evidence.
- Treat successful configuration or compilation as build evidence only.
  Numerical claims require a recorded case run and explicit acceptance metrics.

## Validation

- Run the relevant checks in `docs/operations.md`.
- Rebuild every solver variant affected by a configuration, generated-index,
  shared-source, or dependency change.
- Report exact commands, results, skipped checks, and what remains unverified.
- Preserve warnings and failed attempts as evidence; do not omit them from the
  final report when they affect confidence or supported behavior.

## Documentation

- Update architecture documents only when a stable boundary or contract changes.
- Update `docs/operations.md` when a supported command or workflow changes,
  and add new documents to `docs/index.md`.
- Keep task progress and discoveries in the active execution plan.
- Move completed plans to `docs/exec-plans/completed/` with their outcome.
