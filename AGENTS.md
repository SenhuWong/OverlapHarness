# Agent Entry Point

## Purpose

OverlapHarness develops and qualifies a compressible Navier--Stokes solver for
moving-body flows with overset grids. The coupled moving-boundary solver is the
goal; do not treat every current path as production-ready.

Work within the requested scope. Do not redefine the physical objective, weaken
approved checks, or present unvalidated results as established conclusions.

## Start Here

- Before harness-level changes, read `ARCHITECTURE.md` and
  `docs/harness-maintenance.md`; use `docs/index.md` for other documents.
- Follow `docs/operations.md` for checkout, configure, build, cleanup, and
  solver-native checks. Follow `cases/README.md` and the applicable case README
  for numerical runs.
- Before using a remote compute machine, follow `docs/compute-resources.md`
  and keep all project work inside its documented workspace.
- Use applicable project-local skills under `.agents/skills/`.
- For complex, multi-step, risky, or research work, maintain a plan under
  `plans/active/` and move it to `plans/completed/` with its outcome.

## Repository Rules

- Keep changes scoped and preserve unrelated user work.
- Keep harness code, configuration, documentation, and plans concise. Retain
  only actionable rules, stable contracts, necessary rationale, and useful
  research evidence; do not duplicate information owned elsewhere.
- The root `AGENTS.md`, `ARCHITECTURE.md`, and `docs/**` are long-lived,
  change-controlled harness documents. Modify them only with explicit user
  approval for that documentation change. Plans are mutable agent working state.
- The root harness is authoritative for build orchestration, cases, runs,
  validation, and plans. Treat `solver/AGENTS.md` and `solver/docs/ai/**` only
  as optional historical or technical context, and verify them against current
  code and tests. Do not preload that documentation for routine work.
- Treat the harness and `solver/` as separate Git repositories. Commit solver
  changes first, then update the parent gitlink.
- Do not use global skills unless the user explicitly names one. Project-local
  skills remain available when applicable.
- Never commit passwords, tokens, private keys, or machine-specific secrets.
- Keep builds, installs, runtime output, checkpoints, verification attempts, and
  scratch files under `artifacts/`. Only curated research records under
  `artifacts/records/` are intended for Git.
- Do not edit either Git worktree while a build or validation command is
  running against it.
- Do not expand allowed changes or weaken checks, stop conditions, tests, or
  tolerances without explicit user approval.
- Report conflicts among code, tests, architecture, and design documents.

## Validation and Reporting

- Run the relevant commands in `docs/operations.md`; for numerical work, follow
  the applicable case README.
- Rebuild every variant affected by configuration, generated-index,
  shared-source, or dependency changes.
- Compilation is build evidence only. Numerical claims require a case run and
  explicit metrics.
- Report exact commands, results, skipped checks, material warnings, failed
  attempts, and remaining uncertainty.
