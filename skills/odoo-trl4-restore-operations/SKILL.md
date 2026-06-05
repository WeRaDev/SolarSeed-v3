---
name: odoo-trl4-restore-operations
description: Execute the SolarSeed Odoo restore protocol from local dry-run through TRL replay. Use this whenever the user asks to install/configure Odoo, restore a backup, run verification tests, and publish the app safely via Tailscale on TRL.
---

# Odoo TRL4 restore operations (local -> TRL)

## Scope
Use this skill for:
- Local Odoo stack setup and validation before touching TRL.
- Restoring `dump.sql` + `filestore/` backups.
- Functional checks after restore (modules, website, login, assets).
- Replaying the same procedure on TRL from a synchronized branch.
- Tailnet exposure using loopback-only Odoo binding.

## Safety rules
- Treat `down -v`, volume deletion, and DB overwrite as destructive.
- Require explicit `CONFIRM DESTRUCTIVE` before destructive actions.
- Keep Odoo ports loopback-bound (`127.0.0.1`) unless explicitly approved otherwise.
- Use batched SSH sessions for TRL execution; avoid one-command-per-connection loops.

## Canonical paths and defaults
- Local repo compose: `odoo-app/docker-compose.yml`
- Local env file: `odoo-app/.env`
- TRL4 host workspace: `~/odoo-app`
- DB name: `wera`
- Odoo login URL: `http://127.0.0.1:8069/web/login?db=wera`

## Mandatory execution order
1. **Repository sync gate (local)**
   - Sync app + documentation repositories from Gitea.
   - Work from a feature branch; record the exact commit to replay on TRL.
2. **Local preflight gate**
   - Validate compose configuration.
   - Validate required env vars and backup artifact presence.
3. **Local apply gate**
   - Start local stack.
   - Restore SQL then filestore.
   - Sync enterprise subscription metadata.
4. **Local verification gate**
   - Probe login and target routes.
   - Check module state and queue state.
   - Verify website routing and asset bundle responses for the target website.
   - Commit Odoo shell writes with `env.cr.commit()` before final checks.
5. **Learning gate**
   - Capture failures, update scripts/docs/skills, and push the branch.
6. **TRL replay gate**
   - Verify TRL workspace is updated to the same branch commit.
   - Repeat local apply + verification steps in one batched SSH session.
   - Enable and validate Tailscale exposure (if requested).
7. **Handoff gate**
   - Publish evidence and await manual test results.

## Consistency gate fail criteria
- Any restore step completed without a corresponding post-check.
- `runtime_offender_views > 0` for active inherited `res.config.settings` views.
- Installed modules expected by DB are missing from addon paths.
- Target host renders the wrong website for intended domain.
- Required route/assets probe fails for the target website.
- Tailscale endpoint missing or non-functional when tailnet exposure is in scope.

## Known restore caveats
- Warnings like `functions in index expression must be marked IMMUTABLE` can appear during SQL import from older/custom dumps.
- Missing `...gist_idx` relations may appear during replay but can still result in a usable runtime.
- Treat final success as user-path health (login + target routes + asset load + module sanity), not warning-free SQL output.

## Response template
When done, report:
- Branch/commit used for local and TRL replay.
- Stack status and restore status (SQL + filestore).
- Verification evidence (login, routes, assets, module state, queue state).
- Tailnet URL status (when configured).
- Remaining blockers and the exact next manual test request.
