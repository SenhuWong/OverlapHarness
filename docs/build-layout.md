# Build layout

## Source and generated state

`solver/` and its nested vendor repositories are source checkouts. Builds must
not write generated files into those Git worktrees. The harness-level
`artifacts/` directory is a sibling of `solver/` and owns all generated build
and install state:

```text
OverlapHarness/
|-- solver/
|   `-- vendor/HDF5/              HDF5 source submodule
`-- artifacts/
    |-- build/
    |   |-- superbuild/           CMake orchestration cache and stamps
    |   |-- dependencies/hdf5/    parallel HDF5 build tree
    |   `-- solver/
    |       |-- 2d-euler/
    |       |-- 2d-sst/
    |       |-- 2d-sa/
    |       |-- 3d-euler/
    |       |-- 3d-sst/
    |       `-- 3d-sa/
    `-- install/hdf5/             shared parallel HDF5 installation
```

The HDF5 installation is shared because all six solver variants use the same
compiler, MPI implementation, HDF5 options, and build type. A different
toolchain, MPI implementation, ABI, or build type requires a separate artifact
root, selected with `-DOVERLAP_ARTIFACTS_DIR=/path/to/artifacts` when configuring
the superbuild.

## Why six solver build trees

`AMReX_SPACEDIM` changes AMReX configuration and compiled source behavior.
`TURB_MODEL` changes generated Fortran indices and compile definitions. These
values therefore cannot safely share one CMake cache.

| Variant | `AMReX_SPACEDIM` | `TURB_MODEL` | Executables selected by the current solver CMake |
| --- | ---: | --- | --- |
| `2d-euler` | 2 | `EULER` | `BackgroundSolver`, `RichtmyerMeshkovInstability`, `Riemann2D`, `ShockBubble`, `Sphere` |
| `2d-sst` | 2 | `SST` | `BackgroundSolver` |
| `2d-sa` | 2 | `SA` | `BackgroundSolver` |
| `3d-euler` | 3 | `EULER` | `BackgroundSolver`, `TaylorGreenVortex` |
| `3d-sst` | 3 | `SST` | `BackgroundSolver`, `TaylorGreenVortex` |
| `3d-sa` | 3 | `SA` | `BackgroundSolver`, `TaylorGreenVortex` |

The matrix covers the two explicit solver configuration axes in the current
top-level `solver/CMakeLists.txt`. Future axes such as GPU backend, precision,
or a different compiler/MPI stack should use a distinct artifact root or an
explicit extension of the preset matrix.

## Runtime and test output

Build trees contain compiler and linker output only. Case inputs stay under
`cases/`. Solver runs and validation attempts execute from a case/run-specific
directory under `artifacts/` so plotfiles, checkpoints, logs, metrics, and
verdicts cannot mix with a build tree or source checkout.
