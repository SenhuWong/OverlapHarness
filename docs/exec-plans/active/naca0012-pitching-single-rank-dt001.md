# NACA0012 pitching single-rank dt=0.001 control

## Objective

Measure the effect of reducing the physical time step in the rejected 2D SA
profile by rerunning it on one MPI rank through time 30 with `dt=0.001`.
Compare its force history with the completed one-rank `dt=0.01` run.

## Controlled changes

- Change `dt_unstruct` from 0.01 to 0.001.
- Change `max_step` from 3000 to 30000 so the terminal time remains 30.
- Change the AMReX and unstructured checkpoint intervals from 500 to 5000
  steps so checkpoints retain the same five-time-unit physical cadence.

Keep the mesh, one-partition decomposition, one-rank core binding, AMR levels,
CFL, SA parameters, motion law, and four fixed inner pseudo steps unchanged.
This isolates physical-step sensitivity within the existing under-converged
fixed-point profile; it does not test pseudo-time convergence or qualify the
case against experiment.

## Execution and checks

1. Freeze the modified inputs in a new artifact directory and preprocess the
   grid into one partition.
2. Run the unchanged 2D SA executable for 30000 steps through time 30.
3. Require normal exit, 30000 finite force rows, terminal time 30, and paired
   checkpoints at physical times 5 through 30.
4. Compare `Cl`, `Cd`, and `Cm` with the one-rank `dt=0.01` history on matching
   physical times, including the maximum-angle and first-downstroke interval.
5. Store plots, pointwise data, metrics, logs, and the final assessment in the
   run artifact, then record the outcome here.
