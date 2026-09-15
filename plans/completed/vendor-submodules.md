# Vendor submodules

## Objective

Audit the solver's vendor dependencies against `solver/CMakeLists.txt` and
replace copied dependency trees with reproducible submodules hosted under the
`SenhuWong` GitHub account.

## Scope

- `solver/.gitmodules`
- `solver/.gitignore`
- `solver/CMakeLists.txt`
- `solver/vendor/{glm,yaml-cpp,HDF5,entt,amrex-25.06}` gitlinks
- the parent repository's `solver` gitlink after the solver commit exists

## Dependency evidence

| Path | Evidence | Selected revision |
| --- | --- | --- |
| `vendor/glm` | Local headers declare 1.1.0. No upstream 1.1.0 tag exists; the complete local tree matches upstream commit `8f6213d379a904f5ae910e09a114e066e25faf57`. | That commit on `SenhuWong/glm:vendor-v1.1.0-snapshot`. |
| `vendor/yaml-cpp` | Required by CMake but missing locally. Existing `SenhuWong/yaml-cpp` fork identifies itself as 0.7.0. | Fork's 0.7.0 commit. |
| `vendor/HDF5` | Local partial tree identifies HDF5 2.0.0. Required source and config paths are missing locally. | Complete 2.0.0 tree at `SenhuWong/hdf5:develop`, commit `047b6e04ef951be42c35eb01e3710cc14572590e`. |
| `vendor/entt` | Local amalgamated header exactly matches upstream v3.11.0. | v3.11.0 commit mirrored to `SenhuWong/entt`. |
| `vendor/amrex-25.06` | Local source identifies 25.06. Solver history already established a fork branch with overlap fixes. | `SenhuWong/amrex` commit `28db5162d6be7af0fc36766406d92c517d0509b4`. |

## Plan

1. [x] Compare local dependency contents and required CMake paths with the selected
   upstream revisions.
2. [x] Ensure each selected revision is reachable in the user's GitHub fork.
3. [x] Replace ignored copied trees with submodule gitlinks.
4. [x] Run repository structure checks available on this host.
5. [x] Commit and push the solver change on a task branch, update the parent
   gitlink, and record exact validation results.

## Constraints and open findings

- `PROJECT.md`, `TASK.md`, `docs/index.md`, `docs/operations.md`, and
  `docs/remote-computers.md` are absent, so no project-specific command wrapper
  is available.
- The host currently has no `cmake` or compiler, so a full configure/build may
  remain unverified unless a repository-provided environment is found.
- The local vendor trees contain invalid copied `.git` files and Windows
  `Zone.Identifier` sidecar files; these are discarded when the exact upstream
  submodule revisions replace them.

## Outcome

Completed on branch `chore/vendor-submodules`.

- Solver commit: `6e5d4128698f16e0cf23a5688a4f2d0e3ddcc8e6`.
- Five vendor paths are mode `160000` gitlinks and resolve to commits advertised
  by the corresponding `SenhuWong` forks.
- `git diff HEAD^ HEAD --check` passed.
- Every initialized submodule reported a clean worktree at its locked commit.
- A CMake configure/build was not run because this host has no `cmake` or
  compiler and the repository has no available `docs/operations.md` command.
