# Artifacts

Artifacts make experiments reviewable and reproducible. Follow the contract in
`ARCHITECTURE.md` and copy the examples in `_template/` into each new run.

Commit lightweight evidence when useful. Keep large output outside Git and
describe it in `external.json` with its location, size, file hash or directory
inventory hash, and retention state. Never overwrite a completed run; create a
new run ID.

`build/` and `install/` are ignored, reproducible infrastructure artifacts.
They hold CMake build trees and installed dependencies and may be regenerated
from the root CMake presets. Case/run directories hold execution evidence and
remain subject to the append-only artifact contract.
