---
name: odoo-runtime-troubleshooting
description: Diagnose and recover Odoo 19 runtime failures in SolarSeed with evidence-first playbooks. Use this whenever Internal Server Error appears, connection pools saturate, wrong website/branding renders, Settings crashes, module registry drift, or post-restore behavior is unstable.
---

# Odoo runtime troubleshooting

## Scope
Use this skill when symptoms include:
- `Access Denied` on login
- Odoo container running but web/login failing
- Module states inconsistent after restore
- Missing filestore assets/attachments
- SQL restore warnings with uncertain impact
- Settings Owl lifecycle errors due undefined `res.config.settings` fields/actions
- `psycopg2.pool.PoolError: The Connection Pool Is Full`
- Wrong website rendered for a host (domain/routing drift)
- Styling/assets missing for one website while others render correctly

## Baseline triage sequence
1. Check runtime state and recent logs.
2. Verify DB connectivity and active DB filter.
3. Probe login endpoint and one known public route.
4. Query module lifecycle states (`installed`, `to install`, `to upgrade`, `to remove`).
5. Verify filestore path/ownership.
6. Run targeted branch playbooks below based on the dominant symptom.

## Branch playbooks
### A) Connection pool saturation / Internal Server Error
1. Confirm `PoolError` traces and request failures in logs.
2. Measure DB session pressure (`pg_stat_activity`) to detect idle/leaked connection buildup.
3. Stabilize quickly:
   - Recycle only Odoo runtime container/service.
4. Remove queue pressure:
   - Clear or remediate modules stuck in `to install` / `to upgrade`.
5. Re-validate:
   - burst probes on key routes; ensure no fresh `PoolError` traces.

### B) Wrong website renders for host / UX mismatch
1. Inspect `website.domain` values and website IDs.
2. Probe with explicit `Host` header and identify effective `website_id`.
3. Validate redirect behavior (`Location` headers) and menu/page ownership.
4. Check website-specific asset bundle responses (`/web/assets/<website_id>/...`).
5. Fix domain mapping or page ownership, then re-probe until host routes to the intended website.

### C) Settings crash / registry mismatch
1. Compare active inherited `res.config.settings` fields against runtime registry fields.
2. Quarantine offending inherited views (`active=false`) and restart only Odoo.
3. Re-test authenticated Settings endpoints (`get_view`, `get_views`).
4. Save quarantine evidence artifact and track removed view IDs/XMLIDs.

### D) Restore drift or attachment failures
1. Re-apply filestore copy and ownership.
2. Verify key modules and marker routes.
3. If SQL warnings occurred but runtime checks pass, classify warnings as non-blocking with explicit note.

## Persistence and rollout guardrails
- Always run `env.cr.commit()` after Odoo shell writes that should survive subsequent checks.
- Do not rely on `docker restart` when env/config changes are expected; use compose apply (`up -d <service>`).
- Avoid direct production-wide module upgrades during incident response; use scoped fixes first.

## Reporting contract
Summarize:
- Primary root cause and secondary contributing factors.
- Evidence from logs, DB checks, route probes, and module state checks.
- Actions taken in order (stabilize -> remediate -> verify).
- Before/after status for user-facing behavior and residual risk list.
