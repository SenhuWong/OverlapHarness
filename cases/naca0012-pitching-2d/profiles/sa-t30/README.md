# Rejected diagnostic 2D SA profile through time 30

This profile records the two-dimensional Spalart--Allmaras configuration used
by the 10-rank time-30 run. It is retained so that the attempt can be audited
and reproduced. Do not use it as a physically validated dynamic-stall profile.
Copy the base case into an artifact run directory, then copy this profile's
`inputs` and `Ranswzm.sne` over the corresponding frozen files before
preprocessing.

The profile uses `dt=0.01`, 3000 physical steps, AMR levels 0 through 2 without
time subcycling, CFL 1.0, a free-stream `nu_tilde / nu` ratio of 3.0, and four
inner pseudo steps. Runtime settings selected fixed-point mode 2, so these
steps used Anderson acceleration around the legacy partitioned Dual-LUSGS map;
they did not execute the global SPGMR solve. Stored-Jacobian reuse was disabled.
No residual stopping threshold was active. The profile also relaxed the
original smoke case from `dt=0.001` and CFL 0.1 to `dt=0.01` and CFL 1.0 and
used a 100 by 100 base background grid, while the earlier short SA report used
200 by 200. The runtime mesh-motion speed estimate remained zero throughout
the pitching motion. These differences make the calculation unsuitable as
accuracy or stall evidence.

With the implemented motion law, this case has a nondimensional period of
about 88.50. Time 30 covers only 0.339 period: the angle peaks near time 22.13
and the run stops early on the first downstroke. It cannot establish a closed
dynamic-stall hysteresis loop or a periodic response.

The run writes paired AMReX and unstructured restart checkpoints every 500
steps and disables plot and bulk unstructured field output.

The recorded checks require an exit code of zero, step 3000 at time 30, 3000
finite force rows from time 0 through 29.99, no explicit non-finite/bad-state
diagnostic, and all six scheduled checkpoint pairs. They establish execution
and restart integrity only. They do not accept the force history as a
validation result. The historical force file in the base case is an SST trace
at another time step and is not an SA accuracy baseline.
