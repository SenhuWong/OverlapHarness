# Build Matrix

The superbuild provides six configurations from the solver's two explicit
compile-time axes:

| Variant | `AMReX_SPACEDIM` | `TURB_MODEL` |
| --- | ---: | --- |
| `2d-euler` | 2 | `EULER` |
| `2d-sst` | 2 | `SST` |
| `2d-sa` | 2 | `SA` |
| `3d-euler` | 3 | `EULER` |
| `3d-sst` | 3 | `SST` |
| `3d-sa` | 3 | `SA` |

`AMReX_SPACEDIM` changes dimension-dependent compiled code.
`TURB_MODEL` changes definitions, sources, and generated Fortran indices.
Each combination therefore needs an isolated CMake cache and generated-module
directory. The current executable set is defined by `solver/CMakeLists.txt`
and is not duplicated here.

HDF5 and SUNDIALS may share an artifact root only when the compiler, MPI
implementation, dependency options, ABI, and build type are compatible. Use a
different `OVERLAP_ARTIFACTS_DIR` when that identity changes.

Use `docs/operations.md` for configuration, full-matrix or single-variant
builds, checks, and paired cache invalidation.
