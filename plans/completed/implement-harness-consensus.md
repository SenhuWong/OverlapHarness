# Implement harness-maintenance consensus

## Goal

Apply the approved documentation and artifact-boundary decisions from the
grill-me review without changing solver code or inventing unverified case
workflows.

## Steps

1. Simplify the root agent and architecture documents.
2. Clarify documentation, build, case, and artifact ownership.
3. Add the harness-maintenance and Claude entry documents.
4. Replace run-record templates with a research-note template.
5. Verify links, ignore behavior, diffs, and repository boundaries.

## Outcome

- Reduced the root agent entry and architecture document to stable,
  non-duplicated rules and boundaries.
- Moved plan ownership to `plans/`, centralized documentation navigation, and
  recorded the approved maintenance decisions.
- Kept the NACA0012 case and both SA profiles, marked the case as long-running
  and human-reviewed, and deliberately did not add an unverified `run.sh`.
- Replaced the universal run-record schema with ignored machine-local runtime
  data and Git-tracked Markdown research records.
- Added the shared Claude entry and scoped project-local skill-maintenance
  rules.
- Verified the documented CMake preset names, Markdown targets, ignore
  behavior, whitespace, and the untouched solver worktree. No build or
  numerical run was needed for documentation-only changes.
