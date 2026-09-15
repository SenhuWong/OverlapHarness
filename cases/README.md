# Cases

Each `cases/<case>/` directory is the version-controlled source for one
numerical case. Its README owns the case purpose, essential inputs and
parameters, preprocessing, launch, checks, and result inspection.

## Registry

- [`naca0012-pitching-2d/`](naca0012-pitching-2d/): long-running,
  human-reviewed moving-body case. Its README indexes the retained SA profiles.

## Run Ownership

Generated inputs, logs, checkpoints, fields, and other run state belong under
`artifacts/runtime/<case>/<run-id>/`, not in the case directory. Curated
research conclusions belong under `artifacts/records/<study-id>/`.

A completed case for the supported Slurm machine should expose
`sbatch run.sh` as its standard launch command, with `run.sh` wrapping the
case-specific workflow. Do not add an untested launcher to an unfinished case.

An automated `PASS` means only that the case's listed checks met their
tolerances. It does not establish physical validity or final acceptance.
