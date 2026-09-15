# Track the integrated unstructured solver branch

## Objective

Make the harness reproducibly select the solver line named
`feature/unstruct-sundials-gmres-lusgs`, with all six vendor submodules fixed
at their current verified revisions, so a fresh recursive clone restores the
complete source tree.

## Constraints

- Preserve the running 2D-SA validation by making repository changes only in
  an isolated clone under `artifacts/`.
- Do not rewrite or delete existing remote history.
- Publish the solver branch before publishing the parent harness gitlink.
- Treat recursive clone success and exact seven-gitlink identity as required
  acceptance checks.

## Work

1. [x] Confirm that all six vendor gitlinks selected by solver revision
   `4bf5a2f` are reachable from their configured remotes.
2. [x] Fast-forward `feature/unstruct-sundials-gmres-lusgs` from `456b6c2` to
   the already integrated and build-qualified revision `4bf5a2f`.
3. [x] Record the solver tracking branch in the harness `.gitmodules` while
   retaining the existing solver gitlink at `4bf5a2f`.
4. [x] Commit and push the harness update after the solver branch is public.
5. [x] Clone the published harness branch with `--recursive` into a second
   isolated directory and verify the solver plus all six vendor revisions,
   URLs, cleanliness, and absence of uninitialized submodules.
6. [x] Record exact results and move this plan to `completed/`.

## Acceptance

- The solver branch update is a fast-forward and resolves to `4bf5a2f`.
- `git clone --recursive --branch chore/vendor-submodules` succeeds without
  local repository alternates or unpublished commits.
- The fresh clone is clean and its solver/vendor gitlinks exactly match the
  revisions recorded by the harness and solver commits.
- The pre-existing long-running validation continues undisturbed.

## Outcome

Completed on 2026-09-14.

- The solver branch was fast-forwarded without rewriting history from
  `456b6c2` to `4bf5a2f`. The latter contains the former, the six current
  vendor gitlinks, their build integration, and the 3D-SA executable-selection
  correction required by the qualified solver matrix.
- Harness commit `169fd00` records
  `branch = feature/unstruct-sundials-gmres-lusgs`; its solver gitlink remains
  `4bf5a2f`. Both `chore/vendor-submodules` and the default `main` were advanced
  by fast-forward so an unqualified clone selects this state.
- `git clone --recursive git@github.com:SenhuWong/OverlapHarness.git` completed
  in an isolated directory using only published remotes. It restored the
  solver, all six direct vendor submodules, and all three nested SUNDIALS
  submodules. Exact revision checks and recursive status checks passed.
- All active harness and solver worktrees remained clean. The pre-existing
  eight-rank 2D-SA run continued from time 21.856 to at least 21.915 during the
  operation and was not interrupted or exposed to source edits.
- No build or numerical run was started for this task because the solver
  source identity did not change: the published branch was advanced to the
  already build-qualified `4bf5a2f` commit. Recursive source restoration was
  the requested acceptance boundary.
- One harmless fetch attempt in the isolated single-branch clone did not
  create `origin/main`; it stopped before any push. Fetching with an explicit
  remote-tracking refspec then established that updating `main` from `cf26ccd`
  to `169fd00` was a fast-forward before it was published.
