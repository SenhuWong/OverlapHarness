# 2D SA profile through time 30

This profile changes the shared NACA0012 pitching case to the two-dimensional
Spalart--Allmaras configuration used by the 10-rank time-30 run. Copy the base
case into an artifact run directory, then copy this profile's `inputs` and
`Ranswzm.sne` over the corresponding frozen files before preprocessing.

The profile uses `dt=0.01`, 3000 physical steps, AMR levels 0 through 2 without
time subcycling, CFL 1.0, a free-stream `nu_tilde / nu` ratio of 3.0, and four
stored-Jacobian SUNDIALS GMRES pseudo steps. It writes paired AMReX and
unstructured restart checkpoints every 500 steps and disables plot and bulk
unstructured field output.

Acceptance requires an exit code of zero, step 3000 at time 30, 3000 finite
force rows from time 0 through 29.99, no explicit non-finite/bad-state
diagnostic, and all six scheduled checkpoint pairs. The historical force file
in the base case is an SST trace at another time step and is not an SA accuracy
baseline.
