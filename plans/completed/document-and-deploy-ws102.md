# Document and Deploy Workstation 102

## Goal

Make the workstation workspace rule discoverable from the root agent entry,
then deploy the current project source to the approved remote workspace without
copying machine-local artifacts or credentials.

## Steps

1. Update the protected harness documents with the approved workspace rule.
2. Inspect the remote target and available deployment tools without changing it.
3. Deploy the current harness and solver checkout to the exact approved path.
4. Verify repository state, submodules, and workspace location on workstation
   102.

## Outcome

- Added the remote-resource reference to `AGENTS.md` and documented
  `~/harness-auto/OverlapHarness` as the canonical checkout on workstation
  102.
- Confirmed the target workspace did not previously exist, then deployed the
  current Git worktree and repository metadata.
- Excluded machine-local artifacts, credentials, and the old local
  `solver/build` tree.
- Verified root commit `f1e2a2a`, solver commit `4bf5a2f`, recursive
  submodule state, a clean solver worktree, and `git diff --check` remotely.
- Did not configure, build, or run a numerical case on the workstation.
