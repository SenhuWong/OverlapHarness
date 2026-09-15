# Reproducible dependency and solver build matrix

## Objective

Make the existing HDF5 source submodule part of a reproducible CMake
superbuild, keep all generated build/install state under the harness-level
`artifacts/` directory, and expose the six supported
`AMReX_SPACEDIM`/`TURB_MODEL` solver configurations as named build targets.

## Observed build contract

- `solver/vendor/HDF5` is already a git submodule.
- The solver needs a separately installed parallel HDF5 C library and currently
  looks for `hdf5-config.cmake` below `vendor/HDF5/install/cmake`.
- The manually verified HDF5 configuration uses `HDF5_ENABLE_PARALLEL=ON` and
  installs HDF5 2.0.0.
- `AMReX_SPACEDIM` supports `2` and `3`; `TURB_MODEL` supports `EULER`, `SST`,
  and `SA`, yielding six independent CMake caches.
- In 2D, EULER selects five executables, while SST and SA select
  `BackgroundSolver`. In 3D, all three models select `BackgroundSolver` and
  `TaylorGreenVortex`.

## Planned layout

```text
artifacts/
|-- build/
|   |-- superbuild/
|   |-- dependencies/hdf5/
|   `-- solver/
|       |-- 2d-euler/
|       |-- 2d-sst/
|       |-- 2d-sa/
|       |-- 3d-euler/
|       |-- 3d-sst/
|       `-- 3d-sa/
`-- install/hdf5/
```

Case inputs remain under `cases/`. Runtime outputs, logs, checkpoints, and
validation evidence remain in case/run-specific `artifacts/` records rather
than any build tree.

## Work

1. Add a root CMake superbuild that installs parallel HDF5 once and makes each
   solver configuration depend on that install.
2. Add CMake presets for HDF5, each solver configuration, and the complete
   matrix.
3. Make the solver's HDF5 package path overridable while retaining the existing
   in-submodule install path as a compatibility default.
4. Document exact initialization, configure, dependency, per-configuration,
   matrix, and cleanup commands.
5. Configure the superbuild and validate representative dependency and solver
   targets without modifying the user's existing `solver/build` or
   `solver/vendor/HDF5/{build,install}` trees.

## Constraints

- Preserve the user's dirty `AGENTS.md`, `ARCHITECTURE.md`, existing manual
  build trees, and vendor backup.
- Do not change solver model selection, executable selection, tests, or
  numerical tolerances.

## Outcome

Completed on 2026-09-09.

- Added a root CMake superbuild and presets for parallel HDF5, all six solver
  variants, and the complete matrix.
- Built and installed HDF5 2.0.0 with MPICH and
  `HDF5_ENABLE_PARALLEL=ON` under `artifacts/`.
- Configured all six solver variants successfully against that installation.
- Built and linked the representative `2d-sst` `BackgroundSolver`; its dynamic
  dependencies resolve HDF5 from `artifacts/install/hdf5` and MPICH from the
  system installation.
- Did not compile the other five variants or run numerical cases. Those checks
  remain explicit follow-up validation using the documented presets.
