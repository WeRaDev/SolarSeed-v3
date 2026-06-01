# Odoo skill set
This directory contains reusable Odoo-focused skills for the SolarSeed TRL4 workflow.

## Skills
- `odoo-trl4-restore-operations`: Deploy, restore, validate, and safely expose Odoo 19 on the TRL4 host.
- `odoo-admin-app-governance`: Handle admin authentication checks, user/admin role verification, and module-state audits.
- `odoo-custom-module-dev`: Build and update Odoo 19 modules with manifest, security, and upgrade/test workflow.
- `odoo-runtime-troubleshooting`: Triage Odoo runtime failures (restore drift, access denied, module load errors, filestore issues).

## Usage note
These skills are tuned for the repository's current restore profile:
- Odoo image `odoo:19.0`
- PostgreSQL `pgvector/pgvector:pg16`
- DB `wera`
- Compose path `odoo-app/docker-compose.yml`
- Env file `odoo-app/.env` (or host mirror `~/odoo-app/.env` on TRL4)
