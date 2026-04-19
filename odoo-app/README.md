# Odoo App Stack (Learning and Customization)

This directory contains an isolated Odoo + PostgreSQL stack for SolarSeed learning and customization work.

## 1) First-time setup

From repository root:

1. Create local runtime env file:
   - `cp odoo-app/.env.example odoo-app/.env`
2. Set a strong DB password in `odoo-app/.env`:
   - `ODOO_DB_PASSWORD=<strong-random-password>`
3. Validate compose:
   - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env config --quiet`
4. Start stack:
   - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env up -d`
5. Open Odoo:
   - `http://localhost:8069`

## 2) Create the learning database

At first launch Odoo redirects to database selector.

- Master password (`admin_passwd`): currently set in `odoo-app/config/odoo.conf` (`admin` for lab use).
- Database name: `odoo_lab` (matches default `dbfilter`).
- Load demo data: recommended for learning.

## 3) Scaffold your first custom module

Create a module inside `odoo-app/addons`:

- `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env run --rm odoo odoo scaffold solarseed_custom /mnt/extra-addons`

This creates:
- `odoo-app/addons/solarseed_custom/__manifest__.py`
- models, views, security, and basic module structure

## 4) Install custom module in Odoo UI

1. In Odoo, enable developer mode.
2. Go to Apps.
3. Click `Update Apps List`.
4. Search for your module (`solarseed_custom`).
5. Install.

## 5) Iteration workflow (edit -> upgrade -> verify)

1. Edit module files on host under `odoo-app/addons/<module_name>/...`.
2. Upgrade module in DB:
   - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env run --rm odoo -d odoo_lab -u <module_name> --stop-after-init`
3. Check runtime logs:
   - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env logs -f odoo`
4. Refresh browser and re-test behavior.

## 6) Useful operations

- Stack status:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env ps`
- Stop stack:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env down`
- Stop and delete data volumes (destructive reset):
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env down -v`

## 7) Notes for safe customization

- Keep secrets only in `odoo-app/.env` (gitignored).
- Keep custom addons in `odoo-app/addons/`.
- Keep Odoo config in `odoo-app/config/odoo.conf`.
- Prefer small upgrades (`-u <module_name>`) instead of reinstalling full DB.

## 8) Compatibility findings: `gogarden.dump.zip`

The file `odoo-app/gogarden.dump.zip` is a full database backup (`dump.sql` + `filestore/`), not an installable addon module.

### What was tested

- Restore into local `odoo:18.0` stack with PostgreSQL 15.
- Restore into temporary `odoo:19.0` stack with PostgreSQL 16 + pgvector.
- Copy matching filestore to `/var/lib/odoo/filestore/gogardens`.
- Open `/web/login?db=gogardens`.

### Observed result

- Database and filestore restore complete, but login request fails with HTTP 500.
- Backup metadata reports base version `saas~19.2.1.3`, which does not match local standard image versions.
- Representative errors seen during tests:
  - `column res_lang.short_time_format does not exist`
  - `column res_company.layout_background does not exist`
  - `Skipping database gogardens as its base version is not 19.0.1.3`

### Conclusion

This backup is from an Odoo Online/SaaS schema level and is not directly runnable on the local Community Docker images used in this repository.

### Recommended path

- Use a source and module set matching the exact SaaS schema lineage, or
- Perform a formal migration/export path to a supported on-premise version before local restore testing.
