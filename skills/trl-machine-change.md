# name
trl-machine-change

# intent
Provide a safe, branch-aware process for TRL machine configuration and operations updates.

# trigger_conditions
- A change touches `compose/`, `ops/`, `prometheus/`, `alertmanager/`, or branch-specific TRL docs.
- A task may impact running services, data safety, or deployment behavior.

# required_inputs
- Target branch context (`trl4` or `trl5`).
- Requested operational outcome.
- Relevant runbook/config files.

# procedure
1. Confirm target branch and machine context.
2. Inspect current config and runbook state before editing.
3. Define rollback path for the exact change.
4. Implement minimal reversible diff.
5. Validate compose and impacted service checks.
6. Document branch-specific operational notes.

# validation
- Compose syntax validates for touched compose files.
- Branch-specific checks in `ops/RUNBOOK.md` were run or explicitly noted as pending.
- Rollback procedure is documented when impact is non-trivial.

# expected_outputs
- Safe operational diff.
- Validation evidence.
- Rollback-ready notes for deployment.

# failure_modes
- Branch mismatch (`trl4` vs `trl5`) causing wrong environment assumptions.
- Missing rollback notes for high-impact changes.
- Operational edits merged without runbook updates.

# handoff_notes
- If uncertainty remains, stop before deployment-impacting changes and request explicit confirmation.
