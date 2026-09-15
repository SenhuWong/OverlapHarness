# Compute Resources

This document lists the compute machines currently available to the project.
Secrets remain in the referenced Git-ignored local file.

## 102 Workstation

- Host: `100.89.145.125`
- SSH port: `22`
- User: `ws102`
- Password: stored locally in
  `artifacts/site-config/compute-resources.local.md`

Connect with:

```bash
ssh -p 22 ws102@100.89.145.125
```

### Project Workspace

The project workspace on this machine is `~/harness-auto/`. Keep the project
checkout, builds, runs, and generated artifacts inside this directory. Do not
use or alter unrelated workspaces elsewhere on the machine.

The canonical checkout location is:

```text
~/harness-auto/OverlapHarness
```
