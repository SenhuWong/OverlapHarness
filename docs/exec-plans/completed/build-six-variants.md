# Build all six solver variants

## Objective

Build every supported `AMReX_SPACEDIM`/`TURB_MODEL` combination in its
artifact-owned CMake tree, verify the expected executables, and update the
architecture document to reflect the qualified build boundary.

## Work

1. Check that model-specific generated sources are isolated per build tree.
2. Build the `solver-matrix` target with the existing parallel HDF5 install.
3. Verify all expected executables and their HDF5/MPI linkage.
4. Update `ARCHITECTURE.md` without discarding its existing user changes.
5. Record exact validation results and remaining runtime limitations.

## Constraints

- Write generated build state only below `artifacts/`.
- Preserve the manual `solver/vendor/HDF5/install` directory and vendor backup.
- Do not run numerical cases or change solver algorithms and tolerances.

## Outcome

Completed on 2026-09-10.

- Created and built the six independent trees under
  `artifacts/build/solver/`.
- Restored the solver's existing historical SA policy and Fortran kernels,
  added SA problem initialization, and made source collection model-specific.
- Built all 13 executables selected by the six configurations.
- Verified every executable links to the artifact-owned parallel HDF5 2.0.0
  installation and MPICH.
- Updated `ARCHITECTURE.md` with the superbuild, submodule, build-tree, and
  current qualification boundaries.

Validation commands:

```sh
cmake --build --preset solver-2d-sa --parallel 8
cmake --build --preset solver-3d-sa --parallel 8
cmake --build --preset solver-matrix --parallel 8
```

No numerical case was run. The 3D SA configuration is compile-qualified only:
its AMReX SA RHS explicitly stops because the model currently implements a 2D
kernel. Existing compiler warnings remain recorded in `ARCHITECTURE.md`.
