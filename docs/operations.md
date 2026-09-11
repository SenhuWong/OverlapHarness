# Operations

Run the commands below from the `OverlapHarness` repository root. They are the
supported local build and validation interface for the current CPU/MPI setup.

## Initialize source dependencies

```sh
git submodule update --init --recursive
```

This initializes `solver/` and its six vendor submodules: AMReX, EnTT, GLM,
HDF5, SUNDIALS, and yaml-cpp. Do not build inside a vendor source directory.

## Check the local toolchain

```sh
cmake --version
cc --version
c++ --version
gfortran --version
mpicc --version
mpicxx --version
mpifort --version
mpiexec --version
```

The C, C++, and Fortran wrappers, MPI implementation, and build type form one
build identity. Do not reuse an artifact build tree after changing any of them.

The system MPICH installation on the current WSL host hangs in `MPI_Init`.
Open MPI 4.1.6 was therefore built locally under `artifacts/` with Fortran
bindings, using the official release archive whose SHA-256 is
`44da277b8cdc234e71c62473305a09d63f4dcca292ca40335aab7c4bf0e6a566`:

```sh
cmake -E make_directory artifacts/downloads artifacts/src \
  artifacts/build/dependencies/openmpi
curl --fail --location \
  --output artifacts/downloads/openmpi-4.1.6.tar.gz \
  https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.6.tar.gz
printf '%s  %s\n' \
  44da277b8cdc234e71c62473305a09d63f4dcca292ca40335aab7c4bf0e6a566 \
  artifacts/downloads/openmpi-4.1.6.tar.gz | sha256sum --check
tar -xzf artifacts/downloads/openmpi-4.1.6.tar.gz -C artifacts/src
cd artifacts/build/dependencies/openmpi
../../../src/openmpi-4.1.6/configure \
  --prefix="$OLDPWD/artifacts/install/openmpi" \
  --enable-mpi-fortran=usempi \
  --disable-oshmem \
  --without-verbs \
  --without-ucx
make --jobs 8
make install
cd "$OLDPWD"
```

An existing MPI installation is suitable only after a minimal program that
calls `MPI_Init` and `MPI_Finalize` succeeds both directly and under the chosen
launcher. Keep that probe and its output under `artifacts/`.

## Configure the superbuild

Use the harness-local Open MPI installation on the current host:

```sh
cmake --preset superbuild \
  -DOVERLAP_MPI_ROOT="$PWD/artifacts/install/openmpi"
```

On a machine with a working MPI implementation already on `PATH`, omit
`OVERLAP_MPI_ROOT`:

```sh
cmake --preset superbuild
```

The setting selects one coherent set of MPI compiler wrappers and launcher for
HDF5, SUNDIALS, and every solver variant. Configuration creates only the
orchestration cache at `artifacts/build/superbuild`.

## Build shared dependencies

```sh
cmake --build --preset hdf5-parallel --parallel 8
cmake --build --preset sundials-parallel --parallel 8
```

HDF5 is built with `HDF5_ENABLE_PARALLEL=ON` and installed at
`artifacts/install/hdf5`. SUNDIALS builds its MPI-enabled ARKODE libraries and
is installed at `artifacts/install/sundials`. Their build trees are
`artifacts/build/dependencies/hdf5` and
`artifacts/build/dependencies/sundials`. Tests, examples, unused SUNDIALS
solver packages, HDF5 language bindings, and HDF5 tools are disabled.

Solver targets depend on both dependencies, so building them separately is
optional. Separate builds are useful when qualifying a compiler/MPI setup.

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

Each target incrementally configures and builds its own directory under
`artifacts/build/solver/`. The six directories isolate the two
`AMReX_SPACEDIM` values and three `TURB_MODEL` values, including their generated
Fortran modules and CMake caches.

## Build the complete matrix

```sh
cmake --build --preset solver-matrix --parallel 8
```

Increase or reduce the parallel count to match the machine. Re-run the
configure preset after changing the root superbuild or presets. Rebuild every
affected variant after changing shared or generated solver sources.

## Run solver-native checks

For the current `2d-sst` build:

```sh
ctest --test-dir artifacts/build/solver/2d-sst --output-on-failure
```

The checks generate a one-partition preprocessed mesh fixture and then exercise
the cell-centered LSQ MeshLoader path with that fixture.

## Run the NACA0012 pitching validation case

Create a unique record and freeze the case inputs before execution:

```sh
harness_root=$PWD
run_id="run-$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short=8 HEAD)"
run_dir="$harness_root/artifacts/naca0012-pitching-2d/$run_id"
mkdir -p "$run_dir/inputs" "$run_dir/logs"
cp -a cases/naca0012-pitching-2d/. "$run_dir/inputs/"
```

Generate the 16-partition HDF5 mesh from the run directory:

```sh
cd "$run_dir"
"$harness_root/artifacts/install/openmpi/bin/mpiexec" -n 1 \
  "$harness_root/artifacts/build/solver/2d-sst/tests/mesh_preprocessor_2d" \
  inputs/naca0012_sharp.grd \
  --dim 2 \
  --nparts 16 \
  --levels 1 \
  --reference-length 0.2 \
  --skip-tecplot \
  >logs/preprocess.stdout.log 2>logs/preprocess.stderr.log
printf '%s\n' "$?" >logs/preprocess.exitcode
```

Run exactly 100 physical steps with the 2D SST executable. Use hardware-thread
slots when the local MPI allocation exposes fewer than 16 physical-core slots:

```sh
"$harness_root/artifacts/install/openmpi/bin/mpiexec" \
  --use-hwthread-cpus --bind-to hwthread -n 16 \
  "$harness_root/artifacts/build/solver/2d-sst/BackgroundSolver" \
  inputs/inputs \
  >logs/stdout.log 2>logs/stderr.log </dev/null
printf '%s\n' "$?" >logs/run.exitcode
```

Validate the completed record:

```sh
python3 inputs/validate.py --run-dir . \
  >logs/validate.stdout.log 2>logs/validate.stderr.log
printf '%s\n' "$?" >logs/validate.exitcode
cd "$harness_root"
```

The case definition and criterion meanings are in
`cases/naca0012-pitching-2d/README.md`. Runs must not execute from the live case
directory or a build directory. Retain failed attempts as evidence.

## Run the 10-rank 2D SA profile through time 30

Build and check the SA variant:

```sh
cmake --build --preset solver-2d-sa --parallel 10
ctest --test-dir artifacts/build/solver/2d-sa --output-on-failure
```

Create a new artifact, freeze the shared case, and overlay the tested SA
profile before preprocessing:

```sh
harness_root=$PWD
run_id="run-$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short=8 HEAD)-sa10-t30"
run_dir="$harness_root/artifacts/naca0012-pitching-2d/$run_id"
mkdir -p "$run_dir/inputs" "$run_dir/logs"
cp -a cases/naca0012-pitching-2d/. "$run_dir/inputs/"
cp cases/naca0012-pitching-2d/profiles/sa-t30/inputs \
  "$run_dir/inputs/inputs"
cp cases/naca0012-pitching-2d/profiles/sa-t30/Ranswzm.sne \
  "$run_dir/inputs/Ranswzm.sne"
cd "$run_dir"
```

Generate all three overset-mask resolutions required by AMR levels 0 through
2. The partition count must match the MPI rank count:

```sh
"$harness_root/artifacts/install/openmpi/bin/mpiexec" -n 1 \
  "$harness_root/artifacts/build/solver/2d-sa/tests/mesh_preprocessor_2d" \
  inputs/naca0012_sharp.grd \
  --dim 2 \
  --nparts 10 \
  --levels 3 \
  --reference-length 0.2 \
  --skip-tecplot \
  >logs/preprocess.stdout.log 2>logs/preprocess.stderr.log
printf '%s\n' "$?" >logs/preprocess.exitcode
```

The WSL allocation qualified on 2026-09-11 exposed seven physical cores and
thirteen hardware threads. It therefore ran ten MPI ranks bound to hardware
threads:

```sh
/usr/bin/time -v -o logs/resource.log \
  "$harness_root/artifacts/install/openmpi/bin/mpiexec" \
  --use-hwthread-cpus --bind-to hwthread -n 10 \
  "$harness_root/artifacts/build/solver/2d-sa/BackgroundSolver" \
  inputs/inputs \
  >logs/stdout.log 2>logs/stderr.log </dev/null
printf '%s\n' "$?" >logs/run.exitcode
```

This advances 3000 physical steps with `dt=0.01`. Paired restart records are
written every 500 steps below `raw/amrex/` and `raw/unstruct/`. Validate the
terminal state with:

```sh
python3 inputs/validate.py --run-dir . \
  --expected-steps 3000 \
  --expected-final-time 30 \
  --expected-dt 0.01 \
  >logs/validate.stdout.log 2>logs/validate.stderr.log
printf '%s\n' "$?" >logs/validate.exitcode
cd "$harness_root"
```

The validator checks completion and finite force history. Also verify all six
AMReX/unstructured checkpoint pairs listed in the profile README before
finalizing the artifact.

## Clean generated build state

Remove one solver cache when changing configuration outside its named axes:

```sh
cmake -E remove_directory artifacts/build/solver/2d-sst
cmake -E remove_directory \
  artifacts/build/superbuild/external/solver-2d-sst
cmake --preset superbuild \
  -DOVERLAP_MPI_ROOT="$PWD/artifacts/install/openmpi"
```

The second directory contains the ExternalProject stamps. Removing only the
variant cache leaves a stale “create directories” stamp and causes the next
superbuild invocation to enter a directory that no longer exists.

Remove all reproducible solver and shared-dependency state for a clean rebuild:

```sh
cmake -E remove_directory artifacts/build/superbuild
cmake -E remove_directory artifacts/build/solver
cmake -E remove_directory artifacts/build/dependencies/hdf5
cmake -E remove_directory artifacts/build/dependencies/sundials
cmake -E remove_directory artifacts/install/hdf5
cmake -E remove_directory artifacts/install/sundials
```

These commands retain the independently installed MPI toolchain and case run
records elsewhere under `artifacts/`.

## Direct solver configuration

The superbuild is the supported path. For focused CMake debugging, an
equivalent direct 2D SST configuration is:

```sh
cmake -S solver -B artifacts/build/solver/2d-sst \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER="$PWD/artifacts/install/openmpi/bin/mpicc" \
  -DCMAKE_CXX_COMPILER="$PWD/artifacts/install/openmpi/bin/mpicxx" \
  -DCMAKE_Fortran_COMPILER="$PWD/artifacts/install/openmpi/bin/mpifort" \
  -DMPIEXEC_EXECUTABLE="$PWD/artifacts/install/openmpi/bin/mpiexec" \
  -DAMReX_SPACEDIM=2 \
  -DTURB_MODEL=SST \
  -DHDF5_DIR="$PWD/artifacts/install/hdf5/cmake" \
  -DSUNDIALS_DIR="$PWD/artifacts/install/sundials/lib/cmake/sundials"
cmake --build artifacts/build/solver/2d-sst --parallel 8
```

The solver retains `solver/vendor/HDF5/install/cmake` and the analogous vendor
SUNDIALS install path as compatibility defaults. Do not populate those paths
for harness builds because generated installations would dirty submodules.
