# Odoo App Stack (TRL4 restore profile)
This directory contains an isolated Odoo + PostgreSQL stack prepared for restoring `odoo-app/wera.dump.zip` on the TRL4 machine.

## 0) Odoo agent bootstrap
- Canonical agent instruction file for this app: `odoo-app/AGENTS.md`
- Source of truth authored for this project: `odoo-app/ODOO.AGENT.md`
- Initialization command (idempotent):
  - `ln -sfn ODOO.AGENT.md odoo-app/AGENTS.md`
- Verification:
  - `test -L odoo-app/AGENTS.md && ls -l odoo-app/AGENTS.md`

## 1) Runtime profile
- **Edition**: Odoo 19.0 Enterprise (custom subscription)
- **Subscription reference**: `M240830172487565` (stored in `ir_config_parameter` as `database.enterprise_code`)
- Odoo image: `odoo:19.0`
- DB image: `pgvector/pgvector:pg16`
- DB extensions expected by dump: `pg_trgm`, `unaccent`, `vector`
- Default restored DB name: `wera`
- Default bind mode: loopback only (`127.0.0.1`) for TRL4-safe exposure

### Enterprise addons status (TRL4)
The `wera` database was restored from an Enterprise backup and contains Enterprise module metadata (e.g. `web_enterprise`, `account_accountant`). However, the Docker image `odoo:19.0` ships only Community addons. Enterprise addon code must be mounted at `/mnt/enterprise` (mapped from `odoo-app/enterprise`) and included in `addons_path` before Enterprise modules can be installed or upgraded. See `ODOO.AGENT.md` for the target repository layout.

### Documented blocker findings (Odoo docs)
Based on Odoo documentation research, the remaining blockers are structural and expected:
- Enterprise source install requires cloning both repositories:
  - Community server: `odoo/odoo`
  - Enterprise addons: `odoo/enterprise`
  - Source: https://www.odoo.com/documentation/19.0/administration/on_premise/source.html
- The Enterprise repository contains addons only; it does not replace Community server code.
- Odoo loads modules only from configured `addons_path` directories. If Enterprise addons are absent from the mounted path, Enterprise modules remain unresolved and cannot be installed.
  - Source: https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101/01_architecture.html
- A module must contain `__manifest__.py` (and module package structure) to be recognized by Odoo.
  - Source: https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101/02_newapp.html
- Therefore `database.enterprise_code` alone is insufficient: it tracks subscription metadata, but does not provide addon files.

Operational implication for this stack:
- Until licensed Enterprise addon source is present in `odoo-app/enterprise` and mounted to `/mnt/enterprise`, marker modules such as `web_enterprise`, `account_accountant`, and `web_studio` will stay unresolved/uninstalled in runtime even if `database.enterprise_code` is correctly set.

## 2) Prepare `.env`
From repository root:
1. `cp odoo-app/.env.example odoo-app/.env`
2. Set strong values:
   - `ODOO_DB_PASSWORD=<strong-random-password>`
   - `ODOO_ENTERPRISE_CODE=M240830172487565`
   - (recommended) change `admin_passwd` in `odoo-app/config/odoo.conf`
3. Validate:
   - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env config --quiet`

## 3) Start services
From repository root:
```bash
docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env up -d
```

## 4) Restore database + filestore
Example restore flow:
- Unpack backup archive to `/tmp/wera-odoo-restore/`
- Check for file structure: `ls /tmp/wera-odoo-restore/` (should show `dump.sql`, `filestore/`)
- Pipe SQL into db container:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env exec -T odoo-db psql -U ${ODOO_DB_USER:-odoo} < /tmp/wera-odoo-restore/dump.sql`
- Create filestore directory:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env exec -T odoo sh -lc 'mkdir -p /var/lib/odoo/filestore/${ODOO_DB_NAME:-wera}'`
- Copy filestore:
  - `docker cp /tmp/wera-odoo-restore/filestore/. solarseed-odoo:/var/lib/odoo/filestore/${ODOO_DB_NAME:-wera}/`
- Fix ownership:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env exec -T odoo sh -lc 'chown -R odoo:odoo /var/lib/odoo/filestore/${ODOO_DB_NAME:-wera}'`
4. Sync Enterprise subscription code into DB (idempotent):
   - `source odoo-app/.env && docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env exec -T odoo odoo shell -d ${ODOO_DB_NAME:-wera} --db_host=odoo-db -r ${ODOO_DB_USER:-odoo} -w "$ODOO_DB_PASSWORD" < odoo-app/scripts/ensure_enterprise_subscription.py`

## 5) Access model (local + Tailscale)
- Local machine access:
  - URL: `http://127.0.0.1:8069/web/login?db=wera`
  - Port binding: loopback-only (localhost) for safety
- Tailscale access:
  - Exposed by: `tailscale serve --bg 8069` (when running on TRL4)
  - Tailnet URL: `https://<tailscale-hostname>.tail<tailnet-id>.ts.net/web/login?db=wera`

## 6) Verify after restore
- Container health:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env ps`
- HTTP login page:
  - `curl -I http://127.0.0.1:8069/web/login?db=wera`
- Odoo logs:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env logs --tail=200 odoo`
- DB module state sanity:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env exec -T odoo-db psql -U ${ODOO_DB_USER:-odoo} -d ${ODOO_DB_NAME:-wera} -c "select name, latest_version, state from ir_module_module where name in ('base','website') order by name;"`
- Enterprise code sanity:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env exec -T odoo-db psql -U ${ODOO_DB_USER:-odoo} -d ${ODOO_DB_NAME:-wera} -c "select key, value from ir_config_parameter where key='database.enterprise_code';"`

## 7) Useful operations
- Status:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env ps`
- Logs:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env logs --tail=50 odoo`
- Stop:
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env down`
- Destructive reset (DB + filestore volumes):
  - `docker compose -f odoo-app/docker-compose.yml --env-file odoo-app/.env down -v`

## 8) Mandatory automation loop (local -> TRL)
Use this loop for every install/restore/configuration task to reduce manual errors and improve UX outcomes.

1. Synchronize app and documentation repositories from Gitea, then work on a dedicated branch.
2. Cross-validate active skills against this README, `ODOO.AGENT.md`, `ops/RUNBOOK.md`, and `WARP.md`; update skills before runtime mutation.
3. Prepare and validate local container runtime (`docker compose ... config --quiet`, then `up -d`).
4. Restore backup and run verification suite (login, module states/queues, route probes, website asset probes, CTA flow).
5. Record lessons, update docs/skills/scripts, then commit and push the branch.
6. Replay the same validated process on TRL from the same branch commit and confirm Tailscale availability when required.
7. Publish evidence and await manual test feedback; if manual tests fail, restart from step 2.

Operational note:
- If Odoo shell changes are used for data writes, execute `env.cr.commit()` before post-checks/evidence capture.
## 9) Fonseca rollout handoff (Phase 8 manual callback baseline)
- Addon delivery unit:
  - `odoo-app/addons/wera_fonseca_site`
  - Current module version: `19.0.1.1.0`
- Intake + consultation flow contract:
  - Public intake endpoint: `POST /fonseca/intake`
  - CRM tagging: `fonseca-gardens` and `intent:<quote|consultation|remote-owner>`
  - Consultation intent handling: manual callback scheduling from CRM (`manual-callback-queue` activity)
  - Consultation CTA target (no self-booking dependency): `/contactus?partner=fonseca-gardens&intent=consultation`
  - Redirect contract after submit: `/contactus?partner=fonseca-gardens&intent=<intent>&submitted=1`
- Content production artifacts:
  - Source of truth: `odoo-app/content/fonseca_gardens_source_of_truth.json`
  - Visual request pack: `odoo-app/content/fonseca_gardens_visual_request_pack.json`
- Rollout script mode contract:
  - `odoo-app/scripts/fonseca_trl4_rollout.py` defaults to `FONSECA_APPOINTMENT_MODE=manual_callback`
  - Unsupported appointment-family modules in queue states are normalized to `uninstalled` during rollout.
- Phase evidence baseline:
  - `ops/evidence/fonseca_phase5_20260607T121444Z`
  - `ops/evidence/fonseca_phase6_r2_20260608T113906Z`
  - `ops/evidence/fonseca_phase8_manual_callback_20260608T170919Z`
- Current QA position before TRL replay:
  - Automated route/CRM checks passed in R2 evidence.
  - Manual browser gate (final callback UX/content/responsive pass) remains required after replay.
