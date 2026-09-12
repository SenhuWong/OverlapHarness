# Candidate 2D SA profile using workstation-102 settings

This profile freezes the long-step-control configuration recovered from the
workstation-102 SA run. It is intended to test the current solver with the same
mesh, motion, flow inputs, AMR resolution, time-step hierarchy, and nonlinear
solver controls. Completion and finite forces are execution evidence only; no
experimental acceptance envelope has been defined yet.

The source record used solver commit `228738e` on 32 MPI ranks through a target
time of 200. This profile uses 8 ranks and stops at time 30, as requested for
the local comparison. The original files are retained as
`ws102-wzm_inputs` and `ws102-Ranswzm.sne`.

The runnable `inputs` differs from `ws102-wzm_inputs` in two places:

- `amr.blocking_factor` is 4 instead of 16 because the current solver requires
  the 20-by-20 level-0 domain to be divisible by the blocking factor;
- `input_file` names `inputs/Ranswzm.sne` so a frozen artifact can run from its
  record root.

The runnable scene changes only the mesh path to
`inputs/naca0012_sharp.grd`. The shared mesh is the top-level case file and has
SHA-256 `eba052cd0522890ceb243ca8a3646c7e103c07dd2fc5bcd93e0fe52cc6aca0eb`.

## Frozen numerical definition

- build variant: `AMReX_SPACEDIM=2`, `TURB_MODEL=SA`, Release;
- MPI ranks: 8;
- scene model: SA (`turb: 1`);
- Mach number, Reynolds number, and mean angle: 0.4, 3.4e6, and 6.25 degrees;
- pitch amplitude, reduced frequency, and center: 8.5 degrees, 0.075, and
  `(0.25, 0)`;
- background domain: `[-10.00098, 9.99902]^2` with 20 by 20 level-0 cells;
- AMR: `max_level=2`, refinement ratio 2, normal subcycling, CFL 0.1;
- time steps: 0.004 at level 0 and 0.001 at level 2;
- unstructured solve: 64 pseudo steps, SPGMR, approximate stored-Jacobian
  blocks, LUSGS initial guess and right preconditioning;
- end condition: physical time 30, normally 7,500 level-0 steps;
- force cadence: one row per level-2 time step, normally 30,000 rows from
  time 0 through 29.999.

The recovered AMReX input retains `physics.visc_ma=0.6` and
`physics.visc_re=4.8e6`, while the scene specifies Mach 0.4 and Reynolds number
3.4e6. This conflict is intentionally preserved and must be resolved before
claiming physical validation.

## Generated partition input

Generate the partition-dependent HDF5 file after freezing this profile into a
run record:

```sh
"$HARNESS_ROOT/artifacts/install/openmpi/bin/mpiexec" -n 1 \
  "$HARNESS_ROOT/artifacts/build/solver/2d-sa/tests/mesh_preprocessor_2d" \
  inputs/naca0012_sharp.grd \
  --dim 2 \
  --nparts 8 \
  --levels 24 \
  --reference-length 1.0 \
  --skip-tecplot
```

This writes `InterMesh/_cell_8_naca0012_sharp.grd.h5`. It is generated from
the frozen mesh and command, so it belongs in the run artifact and is not
committed.

## Execution checks

After a completed run, check its terminal cadence with:

```sh
python3 inputs/validate.py --run-dir . \
  --expected-steps 7500 \
  --expected-final-time 30 \
  --expected-dt 0.004 \
  --expected-force-samples 30000 \
  --expected-force-dt 0.001
```

Passing these checks establishes completion and finite output. It does not
establish dynamic-stall accuracy, convergence, or agreement with experiment.
