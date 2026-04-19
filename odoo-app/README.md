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
