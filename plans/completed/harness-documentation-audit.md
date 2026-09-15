# Harness documentation audit

## Goal

Compare the current harness instructions and documentation with official OpenAI
and Anthropic guidance, identify redundant or low-value content, and add the
user-requested concision rule to `AGENTS.md`.

## Steps

1. Read official guidance on persistent project instructions.
2. Inventory and review harness-owned files outside the solver submodule.
3. Compare an independent subagent review with the main review.
4. Make only the authorized `AGENTS.md` change and verify the diff.
5. Record findings and remaining recommendations, then archive this plan.

## Outcome

- Reviewed official OpenAI and Anthropic guidance on persistent project
  instructions.
- Added the authorized concision rule to `AGENTS.md`.
- Independently audited the harness and identified redundancy, stale facts, and
  contract conflicts without changing other protected files.
- Reserved all recommended documentation and implementation changes for
  explicit user approval.
