---
name: odoo-admin-app-governance
description: Verify and govern Odoo 19 admin identity, module state, enterprise addon parity, and multi-website routing. Use this whenever the user asks about admin/login checks, installed app consistency, enterprise activation drift, or wrong-website rendering after restore/config changes.
---

# Odoo admin and app governance

## Scope
Use this skill to:
- Distinguish Odoo master password vs application user credentials.
- Verify admin-capable users and authenticate candidate credentials safely.
- Audit module lifecycle health (`installed`, `to install`, `to upgrade`, `to remove`).
- Detect enterprise-code vs enterprise-addon drift.
- Validate multi-website domain routing and host-based rendering.

## Important concepts
- `admin_passwd` in `odoo.conf` is the database manager password, not necessarily the web admin password.
- Web authentication uses `res_users` credentials.
- `database.enterprise_code` is metadata only; Enterprise addons must still exist in mounted addon paths.
- Odoo shell writes must be followed by `env.cr.commit()` before post-checks and evidence capture.

## Governance procedure
1. Confirm target database and environment profile (local or TRL).
2. Enumerate admin-capable users (`base.group_system`) from DB relations.
3. Validate login by calling `/web/session/authenticate` with explicit DB and candidate credentials.
4. Audit module health:
   - Count states for `installed`, `to install`, `to upgrade`, `to remove`.
   - Flag non-zero queue states as rollout risk.
5. Audit module catalog consistency:
   - For installed modules, verify addon directory/manifest presence in configured addon paths.
6. Audit enterprise parity:
   - Verify `database.enterprise_code` matches expected subscription code.
   - Verify enterprise addon mount is non-empty.
   - Verify marker modules (`web_enterprise`, `account_accountant`, `web_studio`) resolve.
7. Audit website routing parity when website scope is involved:
   - Inspect `website.domain` and key redirect routes.
   - Probe with explicit `Host` headers and verify rendered website identity.
8. If any corrective Odoo shell writes are executed, run `env.cr.commit()` and re-check.
9. If login remains unknown/invalid, separate credential recovery from module governance findings.

## Guardrails
- Never claim login success without successful authentication response.
- Never claim enterprise readiness if marker modules are unresolved.
- Never claim website routing is fixed without host-based probe evidence.
- Do not print plaintext secrets in reports.

## Output contract
Always return:
- Admin identity findings.
- Authentication result with endpoint and DB context.
- Module state summary (including queue states).
- Catalog consistency and enterprise parity findings.
- Website host-routing findings (if applicable).
- Recommended next action split by urgency (`blocking`, `follow-up`, `optional`).
