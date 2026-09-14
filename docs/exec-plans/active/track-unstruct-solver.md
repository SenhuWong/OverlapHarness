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
2. [ ] Fast-forward `feature/unstruct-sundials-gmres-lusgs` from `456b6c2` to
   the already integrated and build-qualified revision `4bf5a2f`.
3. [ ] Record the solver tracking branch in the harness `.gitmodules` while
   retaining the existing solver gitlink at `4bf5a2f`.
4. [ ] Commit and push the harness update after the solver branch is public.
5. [ ] Clone the published harness branch with `--recursive` into a second
   isolated directory and verify the solver plus all six vendor revisions,
   URLs, cleanliness, and absence of uninitialized submodules.
6. [ ] Record exact results and move this plan to `completed/`.

## Acceptance

- The solver branch update is a fast-forward and resolves to `4bf5a2f`.
- `git clone --recursive --branch chore/vendor-submodules` succeeds without
  local repository alternates or unpublished commits.
- The fresh clone is clean and its solver/vendor gitlinks exactly match the
  revisions recorded by the harness and solver commits.
- The pre-existing long-running validation continues undisturbed.

