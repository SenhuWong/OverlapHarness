# Operations

Run the commands below from the `OverlapHarness` repository root. They are the
supported local build interface for the current CPU/MPI configuration.

## Initialize source dependencies

```sh
git submodule update --init --recursive
```

This initializes `solver/` and the five nested vendor submodules. Do not build
inside a vendor source directory.

## Check the local toolchain

```sh
cmake --version
cc --version
c++ --version
gfortran --version
mpicc --version
mpicxx --version
mpif90 --version
```

The configured compiler and MPI implementation form part of the build identity.
Do not reuse an existing artifact build tree after changing either one.

## Configure the superbuild

```sh
cmake --preset superbuild
```

This creates only the orchestration cache at `artifacts/build/superbuild`.
Dependency and solver builds start with the build commands below.

## Build the shared parallel HDF5 dependency

```sh
cmake --build --preset hdf5-parallel --parallel 8
```

The target configures HDF5 with `HDF5_ENABLE_PARALLEL=ON`, disables its tests,
examples, language bindings, high-level library, and command-line tools, then
installs the C library to `artifacts/install/hdf5`. Its build tree is
`artifacts/build/dependencies/hdf5`.

The solver targets depend on this target, so running it separately is optional.
It is useful when validating a compiler/MPI environment before configuring any
solver variant.

## Build one solver variant

Choose exactly one preset:

```sh
cmake --build --preset solver-2d-euler --parallel 8
cmake --build --preset solver-2d-sst --parallel 8
cmake --build --preset solver-2d-sa --parallel 8
cmake --build --preset solver-3d-euler --parallel 8
cmake --build --preset solver-3d-sst --parallel 8
cmake --build --preset solver-3d-sa --parallel 8
```

Each target first brings the shared parallel HDF5 installation up to date,
then incrementally configures and builds its own directory under
`artifacts/build/solver/`.

## Build the complete matrix

```sh
cmake --build --preset solver-matrix --parallel 8
```

This builds all six independent solver configurations. Increase or reduce the
parallel count to match the machine. Re-run `cmake --preset superbuild` after
changing the root superbuild or presets; ordinary solver source changes are
picked up by the next variant build.

## Clean generated build state

Remove one solver cache when changing a configuration outside its named axes:

```sh
cmake -E remove_directory artifacts/build/solver/2d-sst
```

Remove all reproducible build and dependency install state for a clean rebuild:

```sh
cmake -E remove_directory artifacts/build
cmake -E remove_directory artifacts/install/hdf5
```

These commands do not remove case/run records elsewhere under `artifacts/`.

## Legacy manual HDF5 install

The solver retains `solver/vendor/HDF5/install/cmake` as a compatibility
default for direct builds. A direct solver configuration may select another
parallel HDF5 installation explicitly:

```sh
cmake -S solver -B artifacts/build/solver/2d-sst \
  -DCMAKE_BUILD_TYPE=Release \
  -DAMReX_SPACEDIM=2 \
  -DTURB_MODEL=SST \
  -DHDF5_DIR="$PWD/artifacts/install/hdf5/cmake"
cmake --build artifacts/build/solver/2d-sst --parallel 8
```

The superbuild is preferred because it records the dependency relationship and
does not dirty the HDF5 submodule.

## Run and validation output

Do not run an executable from its build directory or from a live case source
directory. Freeze the selected case inputs into a new
`artifacts/<case>/<run-id>/inputs/` directory and execute from that run record.
Keep stdout, stderr, plotfiles, checkpoints, metrics, and the final verdict in
the corresponding artifact paths defined by `ARCHITECTURE.md`.
