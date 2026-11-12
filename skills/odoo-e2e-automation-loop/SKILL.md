---
name: odoo-e2e-automation-loop
description: Run the full seven-step Odoo automation loop from repository sync to manual-test handoff. Use to automate install/restore/configuration, multi-website dump restore, local-to-TRL replay, or reliability improvements.
---

# Odoo end-to-end automation loop

## Objective
Orchestrate install/restore/configuration with rollback safety—including **multi-website dump restore**.

## Triggers
Odoo install/restore/config automation; local→TRL replay; “match the backup website”; fix double header/footer / brand routing.

## Seven-step loop
1. **Sync repos** — branch + commit pin (Gitea).
2. **Skills audit** — load `odoo-trl4-restore-operations` multi-website playbook; update skills on new failure modes.
3. **Setup stack** — compose/env; loopback bind; logs/probes.
4. **Restore DB + website surfaces**
   - SQL + filestore.
   - Website phases (restore skill): inventory → homepage → menus → header/footer chrome → rewrites → companies/visibility → modules/assets → edge.
   - After any website module `-i/-u`, **re-run homepage/menu/rewrite phases**.
5. **Learn/document/publish** — `SolarCity/ops/evidence/`; commit skills/docs.
6. **TRL replay** — same commit; batched SSH; tunnel restart policy.
7. **Handoff** — manual tests; loop from step 2 on failures.

## Reliability constraints
- No skip of verification between stages.
- Handoff requires per-brand Host probes + chrome/menu/rewrite checks when websites restored.
- `env.cr.commit()` after persistent writes.
- Prefer `SolarCity/ops` scripts on Frank.
- Confirmation-gated destructive ops.
- CSS debug bundles; stale asset cleanup.
- 530 → tunnel first.
- No branding dual-chrome on dump-faithful brands without UX approval.

## UX gates (each brand)
Host identity; dump `/` (or approved stub); one header strategy; one footer strategy; menus/CTAs; assets; edge HTTPS if in scope.

## Output
Branch/commit; step pass/fail; per-brand evidence; blockers + next actions.
