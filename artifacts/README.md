# Artifacts

Artifacts make experiments reviewable and reproducible. Follow the contract in
`ARCHITECTURE.md` and copy the examples in `_template/` into each new run.

Commit lightweight evidence when useful. Keep large output outside Git and
describe it in `external.json` with its location, size, file hash or directory
inventory hash, and retention state. Never overwrite a completed run; create a
new run ID.
