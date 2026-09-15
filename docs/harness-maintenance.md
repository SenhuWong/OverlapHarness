# Harness Maintenance

This document records approved decisions about the harness itself so later
maintenance does not reopen the same design questions. It captures policy, not
the question-by-question discussion. Update it when the user explicitly
approves a different harness decision.

## Information Ownership

| Information | Authoritative location |
| --- | --- |
| Agent entry rules | `AGENTS.md` |
| Stable system and ownership boundaries | `ARCHITECTURE.md` |
| Documentation navigation | `docs/index.md` |
| Supported build and check commands | `docs/operations.md` |
| Compile-time build variants | `docs/build-layout.md` |
| Compute-resource inventory and login methods | `docs/compute-resources.md` |
| Case registry | `cases/README.md` |
| Case-specific inputs, launch, and checks | Each case README |
| Mutable task plans | `plans/` |
| Machine-local run data | `artifacts/runtime/` |
| Curated research conclusions | `artifacts/records/` |

`AGENTS.md` points to the indexes and owners above; it must not grow one link
for every document or case. Plans are a sibling of `docs/` because they are
mutable agent work, while `docs/` is long-lived project guidance.

## Agent and Documentation Policy

- Keep persistent instructions concise, specific, and non-duplicative.
- Retain actionable rules, stable contracts, necessary rationale, and useful
  evidence. Remove dated status, exhaustive inventories, and repeated workflow
  prose from long-lived documents.
- Root `AGENTS.md`, `ARCHITECTURE.md`, and `docs/**` are change-controlled;
  agents need explicit user approval to change them.
- Root harness instructions govern work started here. Do not preload
  `solver/AGENTS.md` or `solver/docs/ai/**`; they are optional,
  non-authoritative context and may describe an older workflow. Do not modify
  or remove them as part of harness cleanup.
- `CLAUDE.md` contains only `@AGENTS.md` so Claude Code reads the same root
  contract.
- No extra guard is required to prevent agents from starting in the wrong
  directory.
- Existing solver Git history is out of scope for credential cleanup or history
  rewriting. Never copy a credential from history into current files.
- Keep compute-resource addresses, usernames, and login commands in
  `docs/compute-resources.md`. Store passwords only in its referenced,
  Git-ignored local credential file.
- Each compute resource has one documented project workspace. Remote project
  checkouts, builds, runs, and generated artifacts stay inside that boundary.

## Architecture and Builds

- `ARCHITECTURE.md` describes stable ownership, coupling, build, case, and
  evidence boundaries. It may state the intended moving-body solver goal while
  clearly distinguishing that goal from implemented capability.
- `docs/build-layout.md` owns only the six combinations
  `2D/3D x EULER/SST/SA` and the cache, generated-index, ABI, and artifact-root
  isolation they require. Executable inventories and dated build results do not
  belong there.
- `docs/operations.md` lists required tools, asks for machine-dependent choices
  on first setup, and records the supported commands. It includes both the
  whole-matrix build and a single-variant build.
- ExternalProject cache invalidation removes the affected dependency's build
  and install trees together.
- Build success is not numerical validation. Preserve exact reporting of
  commands, results, skipped checks, and material uncertainty.

## Cases and Runs

- `cases/README.md` is the only global case registry. Profiles are indexed by
  their parent case README, not by the documentation index.
- Each case owns concise preprocessing, launch, checking, and inspection
  instructions. For a completed case on the supported remote Slurm machine, the
  standard launch is `sbatch run.sh`; `run.sh` wraps the case workflow.
- The harness currently assumes one remote supercomputer. Do not introduce a
  multi-cluster abstraction. Non-secret site settings may live in a case script.
- Keep the current NACA0012 pitching case and both SA profiles. Do not add
  draft/active/qualified lifecycle labels merely because the case is unfinished.
- NACA0012 pitching is a long-running moving-body case that may take three days
  or more and requires human review. Do not add `run.sh` until the target Slurm
  configuration is available and the user can run it manually once.

An automated `PASS` means only that the checks listed by the case met their
tolerances. It is not final acceptance or proof of physical validity. Do not
invent baseline binding, universal thresholds, or a more elaborate acceptance
schema before results justify them. Fast steady cases may later support
automatic regression checks, but a moving-body case remains necessary before a
solver revision is accepted.

## Runtime Artifacts and Research Records

- Raw outputs, generated inputs, logs, checkpoints, failed attempts, and other
  machine-local intermediates live under
  `artifacts/runtime/<case>/<run-id>/` and stay on the machine that ran them.
- Git synchronizes conclusions, not every runtime file.
- A research record lives under `artifacts/records/<study-id>/` and groups the
  experiments used to answer one research question. It is not one record per
  run.
- A record normally needs only a Markdown document and selected figures. State
  the purpose, relevant revisions and setup, important results, interpretation,
  conclusion, and limitations. Put important numeric values in Markdown even
  when they also appear in a figure.
- Do not require manifests, verdict JSON, external-file ledgers, or an
  append-only run schema as a universal artifact contract. A case may still
  produce structured files when its own validator uses them.

## Before Changing the Harness

Confirm that the user explicitly approved changes to protected harness
documents, place each fact in its owner above, avoid duplicating details, and
record any newly resolved harness decision here. Acceptance-policy work remains
deferred until numerical results make it concrete.
