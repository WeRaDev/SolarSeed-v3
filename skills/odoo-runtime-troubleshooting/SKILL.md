---
name: odoo-runtime-troubleshooting
description: Diagnose and recover Odoo 19 runtime issues in the SolarSeed restore profile. Use this whenever Odoo login fails, AccessDenied appears, modules do not load, restore warnings occur, or filestore/database drift is suspected.
---

# Odoo runtime troubleshooting

## Scope
Use this skill when symptoms include:
- `Access Denied` on login
- Odoo container running but web/login failing
- Module states inconsistent after restore
- Missing filestore assets/attachments
- SQL restore warnings with uncertain impact

## Fast triage sequence
1. Runtime status:
   - `docker compose ... ps`
2. Odoo logs:
   - `docker compose ... logs --tail=200 odoo`
3. DB connectivity and target DB name:
   - check `odoo.conf` + compose env (`HOST`, `USER`, `PASSWORD`, db filter)
4. HTTP probe:
   - `curl -I http://127.0.0.1:8069/web/login?db=wera`
5. Module integrity:
   - query `ir_module_module` for key modules and `state`
6. Filestore integrity:
   - verify path `/var/lib/odoo/filestore/<db>`
   - verify ownership `odoo:odoo`

## Decision patterns
- Login URL `200` + auth `Access Denied`:
  - runtime is healthy; credential mismatch is likely.
- Repeated missing-file/attachment errors:
  - filestore restore mismatch or ownership issue.
- Module load/registry errors in logs:
  - run targeted module update, inspect XML IDs and dependency order.
- Only SQL import warnings but healthy login/modules:
  - record warnings and continue; treat as non-blocking unless user-facing failures appear.

## Recovery actions
- Re-run filestore copy and ownership fix when attachments break.
- Re-run targeted module update with `--stop-after-init` for broken custom modules.
- If credentials unknown, propose explicit password reset workflow.

## Reporting contract
Summarize:
- Root cause hypothesis (ranked if uncertain)
- Evidence (logs + DB checks + HTTP checks)
- Actions taken
- Current service state and residual risks
