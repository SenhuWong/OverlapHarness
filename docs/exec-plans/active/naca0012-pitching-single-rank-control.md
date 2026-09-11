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
