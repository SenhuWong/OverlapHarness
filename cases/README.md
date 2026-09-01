# Cases

Each `cases/<case>/` directory is the editable source of truth for one case.
Its `README.md` must state:

- purpose and fidelity level;
- required inputs and external dependencies;
- physical/numerical parameters and expected behavior;
- build/run assumptions;
- named acceptance criteria with units and provenance.

Do not run a formal experiment from this live directory. Freeze it into a new
artifact `inputs/` snapshot first.

