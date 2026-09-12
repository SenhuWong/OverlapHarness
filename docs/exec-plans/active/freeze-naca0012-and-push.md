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
4. [ ] Commit and push the solver branch, then commit and push the harness
   branch.
5. [ ] Record the pushed revisions and move this plan to `completed/`.
