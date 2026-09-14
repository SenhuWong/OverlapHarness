# Operations

Run the commands below from the `OverlapHarness` repository root. They are the
supported local build and validation interface after the machine-specific
dependency choices have been confirmed with the user.

## Initialize source dependencies

```sh
git submodule update --init --recursive
```

This initializes `solver/` and its six vendor source submodules: AMReX, EnTT,
GLM, HDF5, SUNDIALS, and yaml-cpp. METIS is also solver-owned under
`solver/Depend/`; the harness does not select a separate METIS installation.
Do not build inside a vendor source directory.

## Confirm machine-provided dependencies

Before any configure, build, or run on a new machine, inspect the available
choices read-only and ask the user to confirm:

- the C, C++, and Fortran compiler toolchain;
- the MPI implementation, compiler wrappers, installation prefix if any, and
  launcher;
- any machine-provided library path not supplied by the recursive checkout;
- for a numerical run, the rank count and launcher/binding options.

Do not choose Open MPI, MPICH, a module, or a local installation merely because
it appears first on `PATH`. Never use a compiler, MPI launcher, or library below
`artifacts/`: that directory contains numerical evidence, not dependencies.
The following commands only inventory candidates; they do not authorize a
choice:

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

The confirmed C, C++, and Fortran wrappers, MPI implementation, and build type
form one build identity. Do not reuse a build tree after changing any of them.
If the user chooses an MPI candidate, qualify it with a minimal program that
calls `MPI_Init` and `MPI_Finalize` both directly and under the confirmed
launcher. A probe performed for a numerical topic belongs in that topic's
experiment record; a general machine-qualification probe belongs under
`build/diagnostics/` and is disposable.

## Configure the superbuild

After the user confirms an MPI installation prefix, pass its absolute path:

```sh
cmake --preset superbuild \
  -DOVERLAP_MPI_ROOT="/confirmed/absolute/mpi-prefix"
```

If the user instead confirms the wrappers and launcher currently resolved from
`PATH`, omit `OVERLAP_MPI_ROOT`:

```sh
cmake --preset superbuild
```

The setting selects one coherent set of MPI compiler wrappers and launcher for
HDF5, SUNDIALS, and every solver variant. Configuration currently creates the
orchestration cache at the legacy path `artifacts/build/superbuild`. This is
disposable local build state, not a numerical experiment and not a dependency
source to reuse after cloning on another machine.

## Build shared dependencies

```sh
cmake --build --preset hdf5-parallel --parallel 8
cmake --build --preset sundials-parallel --parallel 8
```

HDF5 is built with `HDF5_ENABLE_PARALLEL=ON` and currently installed at the
legacy path `artifacts/install/hdf5`. SUNDIALS builds its MPI-enabled ARKODE
libraries and is installed at `artifacts/install/sundials`. Their build trees
are `artifacts/build/dependencies/hdf5` and
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

Each target incrementally configures and builds its own directory under the
legacy `artifacts/build/solver/` path. The six directories isolate the two
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
mpi_exec="/confirmed/absolute/path/to/mpiexec"
run_id="run-$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short=8 HEAD)"
run_dir="$harness_root/artifacts/naca0012-pitching-2d/$run_id"
mkdir -p "$run_dir/inputs" "$run_dir/logs"
cp -a cases/naca0012-pitching-2d/. "$run_dir/inputs/"
```

Generate the 16-partition HDF5 mesh from the run directory:

```sh
cd "$run_dir"
"$mpi_exec" -n 1 \
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

Run exactly 100 physical steps with the 2D SST executable. Add launcher- and
binding-specific options only after the user confirms them for this machine:

```sh
"$mpi_exec" -n 16 \
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

## Reproduce the rejected 10-rank 2D SA run through time 30

This workflow reproduces a completed diagnostic attempt. It is preserved for
audit and restart inspection, but its force history is not accepted as
dynamic-stall validation. The profile README records the numerical reasons.

Build and check the SA variant:

```sh
cmake --build --preset solver-2d-sa --parallel 10
ctest --test-dir artifacts/build/solver/2d-sa --output-on-failure
```

Create a new artifact, freeze the shared case, and overlay the recorded SA
profile before preprocessing:

```sh
harness_root=$PWD
mpi_exec="/confirmed/absolute/path/to/mpiexec"
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
"$mpi_exec" -n 1 \
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

The WSL allocation used on 2026-09-11 exposed seven physical cores and thirteen
hardware threads. That historical attempt ran ten ranks bound to hardware
threads, but a new run must use launcher/binding options confirmed for its MPI
implementation and machine:

```sh
/usr/bin/time -v -o logs/resource.log \
  "$mpi_exec" -n 10 \
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

The validator checks completion and finite force history. It does not validate
force accuracy, temporal convergence, pseudo-time convergence, dynamic stall,
or partition independence. Also verify all six AMReX/unstructured checkpoint
pairs listed in the profile README before finalizing the artifact.

## Run the candidate workstation-102 SA profile locally

This profile preserves the conservative workstation-102 nonlinear controls and
8-rank preprocessing contract. It uses the current solver's required
`amr.blocking_factor=4`; the original workstation input with value 16 remains
beside the profile for audit.

Build the current 2D SA variant, create a unique artifact, and freeze only the
authoritative source inputs:

```sh
cmake --build --preset solver-2d-sa --parallel 8
ctest --test-dir artifacts/build/solver/2d-sa --output-on-failure

harness_root=$PWD
mpi_exec="/confirmed/absolute/path/to/mpiexec"
profile=cases/naca0012-pitching-2d/profiles/sa-102-settings-t30
run_id="run-$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short=8 HEAD)-sa8-102-t30"
run_dir="$harness_root/artifacts/naca0012-pitching-2d/$run_id"
mkdir -p "$run_dir/inputs" "$run_dir/logs" \
  "$run_dir/raw/amrex" "$run_dir/raw/unstruct"
cp "$profile/inputs" "$run_dir/inputs/inputs"
cp "$profile/Ranswzm.sne" "$run_dir/inputs/Ranswzm.sne"
cp "$profile/profile.json" "$run_dir/inputs/profile.json"
cp "$profile/README.md" "$run_dir/inputs/README.md"
cp cases/naca0012-pitching-2d/naca0012_sharp.grd "$run_dir/inputs/"
cp cases/naca0012-pitching-2d/validate.py "$run_dir/inputs/"
ln -s raw/amrex "$run_dir/amrex_output"
ln -s raw/unstruct "$run_dir/unstruct_output"
cd "$run_dir"
```

Generate the 8-partition input. The 24 mask levels and unit reference length
are part of the frozen profile even though this run uses AMR levels 0 through
2:

```sh
"$mpi_exec" -n 1 \
  "$harness_root/artifacts/build/solver/2d-sa/tests/mesh_preprocessor_2d" \
  inputs/naca0012_sharp.grd \
  --dim 2 \
  --nparts 8 \
  --levels 24 \
  --reference-length 1.0 \
  --skip-tecplot \
  >logs/preprocess.stdout.log 2>logs/preprocess.stderr.log
printf '%s\n' "$?" >logs/preprocess.exitcode
```

Run on eight allocated ranks. Add binding options only after they are confirmed
for the selected launcher and allocation:

```sh
/usr/bin/time -v -o logs/resource.log \
  "$mpi_exec" -n 8 \
  "$harness_root/artifacts/build/solver/2d-sa/BackgroundSolver" \
  inputs/inputs \
  >logs/stdout.log 2>logs/stderr.log </dev/null
printf '%s\n' "$?" >logs/run.exitcode
```

Validate its two output cadences after it reaches time 30:

```sh
python3 inputs/validate.py --run-dir . \
  --expected-steps 7500 \
  --expected-final-time 30 \
  --expected-dt 0.004 \
  --expected-force-samples 30000 \
  --expected-force-dt 0.001 \
  >logs/validate.stdout.log 2>logs/validate.stderr.log
printf '%s\n' "$?" >logs/validate.exitcode
cd "$harness_root"
```

These criteria establish execution and finite output only. The profile retains
the workstation's conflicting Cartesian and scene free-stream values, so a
passing run is not yet physical validation.

## Clean generated build state

Remove one solver cache when changing configuration outside its named axes:

```sh
cmake -E remove_directory artifacts/build/solver/2d-sst
cmake -E remove_directory \
  artifacts/build/superbuild/external/solver-2d-sst
cmake --preset superbuild \
  -DOVERLAP_MPI_ROOT="/confirmed/absolute/mpi-prefix"
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

These commands do not touch the externally selected MPI toolchain or numerical
experiment records elsewhere under `artifacts/`.

## Direct solver configuration

The superbuild is the supported path. For focused CMake debugging, an
equivalent direct 2D SST configuration is:

```sh
mpi_prefix="/confirmed/absolute/mpi-prefix"
cmake -S solver -B artifacts/build/solver/2d-sst \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER="$mpi_prefix/bin/mpicc" \
  -DCMAKE_CXX_COMPILER="$mpi_prefix/bin/mpicxx" \
  -DCMAKE_Fortran_COMPILER="$mpi_prefix/bin/mpifort" \
  -DMPIEXEC_EXECUTABLE="$mpi_prefix/bin/mpiexec" \
  -DAMReX_SPACEDIM=2 \
  -DTURB_MODEL=SST \
  -DHDF5_DIR="$PWD/artifacts/install/hdf5/cmake" \
  -DSUNDIALS_DIR="$PWD/artifacts/install/sundials/lib/cmake/sundials"
cmake --build artifacts/build/solver/2d-sst --parallel 8
```

The solver retains `solver/vendor/HDF5/install/cmake` and the analogous vendor
SUNDIALS install path as compatibility defaults. Do not populate those paths
for harness builds because generated installations would dirty submodules.
