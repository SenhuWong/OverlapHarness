# Freeze NACA0012 inputs and publish the harness

## Objective

Make the current NACA0012 pitching work reproducible from another checkout by
committing every authoritative source input and the deterministic preprocessing
contract, excluding generated run artifacts, then publish both repositories in
dependency order.

## Scope

- add a runnable 8-rank SA profile derived from the workstation-102 reference;
- retain the exact workstation-102 AMReX input beside the current-solver
  compatibility input;
- extend the existing validator only enough to represent different AMR-step
  and force-sampling cadences;
- update the supported run documentation and documentation index;
- publish the clean solver revision before the parent harness gitlink.

## Work

1. [x] Freeze and hash the profile inputs, shared grid, validator, and
   preprocessing arguments under `cases/naca0012-pitching-2d/`.
2. [x] Verify that no generated HDF5 or artifact payload is staged.
3. [x] Exercise the validator's existing and new cadence options against
   recorded evidence.
4. [x] Commit and push the solver branch, then commit and push the harness
   branch.
5. [x] Record the pushed revisions and move this plan to `completed/`.

## Outcome

Completed on 2026-09-12.

- Solver branch `feature/naca0012-pitching-validation` was published at
  `4bf5a2fb44556fa4593e6182c34a61e343c76159`.
- Harness branch `chore/vendor-submodules` was published through profile commit
  `28385c4` before this closeout.
- The case now carries the runnable `sa-102-settings-t30` profile, byte-preserved
  workstation reference inputs, deterministic preprocessing arguments, and
  hashes for every solver input. Generated HDF5 and all run records remain
  ignored below `artifacts/`.
- The default 100-step validator, the existing 30,000-step SA invocation, and a
  split-cadence fixture all passed. The split-cadence path distinguishes 7,500
  level-0 steps from 30,000 force samples.
- `git diff --check` reports only the two original trailing-space lines retained
  intentionally in byte-preserved `ws102-wzm_inputs`; the runnable `inputs`
  file is whitespace-clean.
