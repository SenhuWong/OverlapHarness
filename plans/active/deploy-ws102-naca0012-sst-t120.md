# Deploy workstation-102 NACA0012 SST run

## Goal

Publish the approved harness changes, deploy a reproducible 32-rank SST
pitching case to workstation 102, and submit the physical-time-120 run only
after preprocessing and a one-step Slurm preflight succeed.

## Steps

1. Fast-forward to the fetched remote branch and commit the approved harness
   maintenance changes without disturbing the solver repository.
2. Add the workstation-102 SST run profile and `run.sh`, then verify its model,
   mesh, timestep, checkpoint, and Slurm settings against current solver code.
3. Push the commits and update the canonical checkout under
   `~/harness-auto/OverlapHarness`, preserving the existing deployment.
4. Build the `solver-2d-sst` variant on workstation 102.
5. Freeze a runtime directory, preprocess its 32-way mesh through levels 0--4,
   and inspect the donor and mask summaries.
6. Submit and inspect a one-coarse-step 32-rank Slurm preflight.
7. Configure tested email notification and hourly monitoring, then submit the
   unchanged full run to physical time 120.
8. Record exact commands, job identifiers, evidence, limitations, and recovery
   state; move this plan to `plans/completed/` only when the requested setup and
   submission are complete.

## Guardrails

- Do not force-push, weaken checks, or change physical parameters to conceal a
  failure.
- Do not submit the full run if preprocessing or the Slurm preflight exposes an
  unresolved donor, model, output, or restart problem.
- Treat automated status as operational evidence only; final physical
  acceptance remains a human decision.
