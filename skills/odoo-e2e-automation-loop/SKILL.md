---
name: odoo-e2e-automation-loop
description: Run the full seven-step Odoo automation loop from repository sync to manual-test handoff. Use this whenever the user asks to automate Odoo install/restore/configuration, reduce manual steps, improve reliability, or replay validated changes from local to TRL.
---

# Odoo end-to-end automation loop

## Objective
Execute Odoo changes with the smallest reliable action list while preserving UX quality and rollback safety. This skill is the default orchestrator for install/restore/configuration work.

## Trigger conditions
Use this skill immediately when the user asks for any of:
- Process simplification or automation of Odoo operations.
- Installation, restoration from backup, environment setup, or configuration hardening.
- Local-first validation followed by TRL deployment replay.
- Better UX outcomes with fewer manual operations.

## Seven-step loop (mandatory order)
1. **Synchronize repositories**
   - Sync target app and documentation repositories from Gitea.
   - Create/refresh a feature branch and capture the branch + commit hash for replay.
2. **Audit and upgrade skill set**
   - Cross-check existing skills against app docs (`odoo-app/README.md`, `odoo-app/ODOO.AGENT.md`, `ops/RUNBOOK.md`, `WARP.md`).
   - Create or update skills when gaps are found before runtime mutation.
3. **Setup and configure local containerized app**
   - Validate compose/env.
   - Start local stack and apply required app configuration.
   - Enable monitoring hooks (logs, route probes, module-state checks).
4. **Restore DB and verify functionality**
   - Restore SQL + filestore and sync subscription metadata.
   - Execute verification suite: auth checks, route checks, asset checks, module/queue checks, and critical business-path tests.
5. **Learn, document, and publish branch**
   - Analyze failures and fixes.
   - Update app documentation and operational notes.
   - Commit and push the remote branch.
6. **Replay on TRL machine**
   - Verify TRL workspace is up-to-date with the same remote branch commit.
   - Repeat local steps 3 and 4 on TRL in one batched SSH session.
   - Ensure app availability through Tailscale when required.
7. **Report and wait for manual tests**
   - Provide concise evidence and explicit manual test instructions.
   - Wait for manual-test feedback, then restart loop from step 2 for failures.

## Built-in reliability constraints
- Never skip verification between apply stages.
- Never close a run without evidence for login, target routes, and module state.
- Always run `env.cr.commit()` after Odoo shell writes that must persist.
- Prefer idempotent scripts over ad-hoc one-off shell edits.
- Treat destructive actions as confirmation-gated.
- For website rollouts, probe website-specific debug bundle paths (`/web/assets/<website_id>/debug/web.assets_frontend.css`) before and after changes.
- If CSS fallback markers appear (`css_error_message`, `A css error occured`), run stale `ir.asset` cleanup and force `/web/assets/%` regeneration before handoff.

## UX quality gates
Before handoff, confirm:
- Intended host resolves to intended website.
- Core pages load with expected branding and assets.
- Primary CTA path works end-to-end.
- No new runtime errors appear in post-change logs.
- No style-compilation toast is visible in browser verification captures.

## Output contract
Return:
- Branch/commit and environments touched (local + TRL).
- Steps completed with pass/fail status.
- Evidence pointers for each quality gate.
- Remaining blockers with the next minimal action list.
