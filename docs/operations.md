# Build and Checks

Run these commands from the OverlapHarness root. Case-specific preprocessing,
launch, and result inspection belong in the applicable case README.

## Prerequisites

- Git with submodule support
- CMake and a supported build tool
- C, C++, and Fortran compilers
- An MPI implementation with compiler wrappers
- Python 3 for harness helpers and case checks

The superbuild obtains HDF5 and SUNDIALS from the configured source trees; do
not assume system installations are ABI-compatible.

## Initialize and Configure

Confirm the MPI installation, build type, and artifact root with the user.
The HDF5 and SUNDIALS sources are the solver vendor submodules. Configure once;
the CMake cache records the resulting non-secret machine choices:

```bash
git submodule update --init --recursive
cmake --preset superbuild \
  -DOVERLAP_MPI_ROOT=/path/to/mpi \
  -DOVERLAP_ARTIFACTS_DIR=/path/to/artifacts \
  -DCMAKE_BUILD_TYPE=Release
```

Omit `OVERLAP_MPI_ROOT` to use MPI wrappers from `PATH`, and omit
`OVERLAP_ARTIFACTS_DIR` to use the repository's ignored `artifacts/`
directory. Do not commit passwords, tokens, private keys, or machine-specific
secrets.

On later reconfiguration, rerun the same command with the confirmed values.
Do not edit solver sources to change MPI discovery.

## Build

Build all six variants:

```bash
cmake --build --preset solver-matrix
```

Build one variant:

```bash
cmake --build --preset solver-2d-sa
```

Replace `2d-sa` in the preset name with a variant from
`docs/build-layout.md`. Rebuild every variant affected by changes to
configuration, generated indices, shared source, or dependencies.

## Solver-Native Checks

Run CTest from the relevant solver build directory, for example:

```bash
ctest --test-dir artifacts/build/solver/2d-sa --output-on-failure
```

A successful configure, build, or CTest run is build evidence only. Numerical
claims require the applicable case workflow and explicit metrics.

## Invalidate External Dependencies

When an ExternalProject dependency changes identity, remove both its build and
install trees before rebuilding:

```bash
cmake -E remove_directory artifacts/build/dependencies/hdf5
cmake -E remove_directory artifacts/install/hdf5
cmake -E remove_directory artifacts/build/dependencies/sundials
cmake -E remove_directory artifacts/install/sundials
```

This paired invalidation is required after changes to the compiler, MPI,
dependency options, ABI, or build type. Adjust the paths only if the selected
artifact root differs.

## Case Runbooks

`cases/README.md` is the case registry. Each case README owns its preprocessing,
launch, validation, and inspection instructions. A completed Slurm case should
expose `sbatch run.sh` as its standard launch command. Do not fabricate that
entry point for an unfinished case or an unverified machine configuration.
