---
name: odoo-trl4-restore-operations
description: Operate and restore the SolarSeed TRL4 Odoo 19 stack from backup archives. Use this whenever the user asks to deploy Odoo, restore database+filestore, validate service health, or expose Odoo through Tailscale while keeping loopback-only binding.
---

# Odoo TRL4 restore operations

## Scope
Use this skill for:
- Bringing the TRL4 Odoo stack up/down
- Restoring `dump.sql` + `filestore/` backups (ZIP format)
- Post-restore validation
- Tailnet exposure with `tailscale serve`

## Safety rules
- Treat `down -v`, volume deletion, and DB overwrite as destructive.
- Require explicit `CONFIRM DESTRUCTIVE` before destructive actions.
- Keep Odoo ports loopback-bound (`127.0.0.1`) unless explicitly approved otherwise.

## Canonical paths and defaults
- Local repo compose: `odoo-app/docker-compose.yml`
- Local env file: `odoo-app/.env`
- TRL4 host workspace: `~/odoo-app`
- DB name: `wera`
- Odoo login URL: `http://127.0.0.1:8069/web/login?db=wera`

## Procedure
1. Validate compose config before changing runtime:
   - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env config --quiet`
2. Start stack:
   - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env up -d`
3. Restore archive (SQL then filestore):
   - Unpack zip to temp directory
   - Pipe `dump.sql` into `psql` in `odoo-db`
   - Ensure filestore directory exists in `odoo` container
   - Copy filestore content into `/var/lib/odoo/filestore/wera`
   - Fix ownership to `odoo:odoo` (container root may be required)
4. Validate runtime:
   - `docker compose ... ps`
   - `curl -I http://127.0.0.1:8069/web/login?db=wera`
   - `docker compose ... logs --tail=120 odoo`
5. Validate module baseline quickly from DB:
   - Query `ir_module_module` for core apps (`base`, `web`, `website`, `sale`, `account`)
6. Expose on tailnet only (if requested):
   - `tailscale serve --bg 8069`
   - `tailscale serve status`

## Known restore caveats
- Warnings like `functions in index expression must be marked IMMUTABLE` can appear during SQL import from older/custom dumps.
- Missing `...gist_idx` relations may appear during replay but can still result in a usable runtime.
- Treat final success as health + login + core module checks, not warning-free SQL output.

## Response template
When done, report:
- Stack status (`up/down`, healthy containers)
- Restore result (SQL + filestore)
- Login endpoint HTTP status
- Tailnet URL status (if configured)
- Any warnings and whether they are blocking
