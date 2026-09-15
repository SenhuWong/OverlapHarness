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

## Progress

- Published harness commits `7c0aab7`, `a49b1f0`, and `d009df6`; workstation
  102 is clean at the last revision, with its earlier deployment preserved in
  `stash@{0}`.
- Built `solver-2d-sst` with system Open MPI and passed both solver CTest cases.
- Preprocessed levels 0--4 for 32 partitions. Every level has valid donors and
  mesh receptors; the generated partition file is 4.1 MiB.
- Slurm preflight job `593` completed one coarse step to time 0.016 on 32 ranks,
  produced finite force samples, and wrote matching step-1 AMR and unstructured
  checkpoints. Its only stderr output was a repeated non-fatal display
  authorization warning.
- Prepared the full runtime at
  `artifacts/runtime/naca0012-pitching-2d/sst-ws102-t120-20260915T150008Z` and
  verified its Slurm request with `sbatch --test-only`.
- Installed Postfix and GNU Mailutils. Gmail rejected the direct-delivery test
  with SMTP status `550 5.7.26` because the workstation sender has neither SPF
  nor DKIM. The full run remains unsubmitted until a working authenticated SMTP
  relay is configured and tested.
