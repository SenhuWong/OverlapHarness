# Artifacts

Artifacts make experiments reviewable and reproducible. Follow the contract in
`ARCHITECTURE.md` and start each run from `_template/`.

Commit lightweight evidence when useful. Keep large output outside Git and
describe it in `external.json` with its location, size, SHA-256, and retention
state. Never overwrite a completed run; create a new run ID.

