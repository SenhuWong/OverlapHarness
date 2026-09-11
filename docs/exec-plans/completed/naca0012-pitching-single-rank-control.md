# NACA0012 pitching single-rank control

## Objective

Measure whether the partitioned Dual-LUSGS path materially changes the lift
and drag history by rerunning the rejected 2D SA time-30 profile on one MPI
rank. Keep every numerical and physical input fixed except the mesh partition
count and MPI rank count.

## Method and checks

1. Freeze the recorded `profiles/sa-t30` inputs in a new artifact directory.
2. Preprocess the same grid into one partition and run the unchanged 2D SA
   executable on one rank.
3. Require normal completion, 3000 finite force rows, and the terminal time 30
   before comparing results.
4. Plot the one-rank and ten-rank force histories against angle and report
   differences near maximum angle and on the first downstroke.
5. Record the commands, logs, metrics, and comparison under `artifacts/`.

This is a partition-sensitivity diagnostic. It does not qualify temporal,
pseudo-time, spatial, turbulence-model, or dynamic-stall accuracy.

## Status

- 2026-09-11: the one-partition mesh preprocessor completed successfully.
- 2026-09-11: the one-rank solver run completed 3000 steps through time 30 in
  1:54:51 with exit status zero and 3000 finite force rows.
- 2026-09-11: the completion validator passed. No rebuild or CTest repetition
  was performed because the control reused the exact previously checked 2D SA
  executable; this run changed runtime partitioning only.
- 2026-09-11: all 3000 force rows were compared with the ten-rank run and the
  overlay and difference plots were generated.

## Outcome

Reducing the unstructured mesh and MPI execution from ten partitions to one
did not materially change the force history. Over the complete series, the
one-rank-minus-ten-rank `Cl` RMSE is `1.45e-4`. For `t >= 18`, spanning the
maximum angle and first downstroke, the `Cl` RMSE is `3.74e-5` and the maximum
absolute difference is `6.0e-5`.

The one-rank and ten-rank peak `Cl` values are 1.58042 and 1.58039. At maximum
angle they are 1.57106 and 1.57103, and at the final sample they are 1.39574
and 1.39579. The corresponding maximum-angle-to-final drops are 0.17532 and
0.17524. The curves are effectively coincident in the interval where a rapid
stall-associated drop was expected, so rank partitioning is not the dominant
cause of the missing response for this profile.

The run record is
`artifacts/naca0012-pitching-2d/run-20260911T135853Z-e86b75a3-sa1-t30-control`.
Its machine validator PASS establishes execution and finite values only. The
physical-validation status remains rejected for the numerical reasons recorded
in `cases/naca0012-pitching-2d/profiles/sa-t30/README.md`.
