# Odoo App Stack (TRL4 restore profile)
This directory contains an isolated Odoo + PostgreSQL stack prepared for restoring `odoo-app/wera.dump.zip` on the TRL4 machine.

## 1) Runtime profile
- Odoo image: `odoo:19.0`
- DB image: `pgvector/pgvector:pg16`
- DB extensions expected by dump: `pg_trgm`, `unaccent`, `vector`
- Default restored DB name: `wera`
- Default bind mode: loopback only (`127.0.0.1`) for TRL4-safe exposure

## 2) Prepare `.env`
From repository root:
1. `cp odoo-app/.env.example odoo-app/.env`
2. Set strong values:
   - `ODOO_DB_PASSWORD=<strong-random-password>`
   - (recommended) change `admin_passwd` in `odoo-app/config/odoo.conf`
3. Validate:
   - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env config --quiet`

## 3) Start stack
- `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env up -d`
- Verify:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env ps`

## 4) Restore `wera.dump.zip`
The archive is an Odoo backup (`dump.sql` + `filestore/`), not an addon.

Example restore flow:
1. Unpack:
   - `unzip -o odoo-app/wera.dump.zip -d /tmp/wera-odoo-restore`
2. Restore SQL:
   - `cat /tmp/wera-odoo-restore/dump.sql | docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env exec -T odoo-db psql -U ${ODOO_DB_USER:-odoo} -d ${ODOO_DB_NAME:-wera}`
3. Restore filestore:
   - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env exec -T odoo sh -lc 'mkdir -p /var/lib/odoo/filestore/${ODOO_DB_NAME:-wera}'`
   - `docker cp /tmp/wera-odoo-restore/filestore/. solarseed-odoo:/var/lib/odoo/filestore/${ODOO_DB_NAME:-wera}/`
   - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env exec -T odoo sh -lc 'chown -R odoo:odoo /var/lib/odoo/filestore/${ODOO_DB_NAME:-wera}'`

## 5) Access model (local + Tailscale)
- Local machine access:
  - `http://127.0.0.1:8069`
- Tailnet access without exposing Odoo on `0.0.0.0`:
  - `tailscale serve --bg 8069`
  - Check endpoint:
    - `tailscale serve status`

## 6) Post-restore checks
- Odoo HTTP health:
  - `curl -I http://127.0.0.1:8069/web/login?db=wera`
- Odoo logs:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env logs --tail=200 odoo`
- DB module state sanity:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env exec -T odoo-db psql -U ${ODOO_DB_USER:-odoo} -d ${ODOO_DB_NAME:-wera} -c \"select name, latest_version, state from ir_module_module where name in ('base','website') order by name;\"`

## 7) Useful operations
- Status:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env ps`
- Stop:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env down`
- Destructive reset (DB + filestore volumes):
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env down -v`
