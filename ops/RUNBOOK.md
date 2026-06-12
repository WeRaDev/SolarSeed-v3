# SolarSeed v3.1 — RUNBOOK

## Routine health checks
- Container status:
  - `docker compose -f compose/docker-compose.yml ps`
- Resource usage:
  - `docker stats --no-stream`
- Prometheus target health:
  - `curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'`
- Spirit health + approvals queue:
  - `curl -s http://localhost:9105/health | jq .`
  - `curl -s http://localhost:9105/approvals | jq .`
  - `curl -s http://localhost:9105/api/v1/status | jq '.approval_policy'`
- Spirit self-reflection (when LLM enabled):
  - `curl -s http://localhost:9105/api/v1/reflection | jq .`
- OpenFang daemon health:
  - `curl -s http://localhost:4200/api/health | jq .`
- Gitea forge health:
  - `curl -s http://localhost:3000/api/healthz | jq .`

## Incident triage
1. Check which building is down:
   - `curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health!="up")'`
2. Review Spirit decisions:
   - `docker compose -f compose/docker-compose.yml logs spirit | grep -E '(heartbeat_complete|alert_received|action_proposed|action_approved)'`
3. Validate Alertmanager routing:
   - `curl -s http://localhost:9093/api/v2/status | jq .`
4. Validate OpenFang API:
   - `curl -s http://localhost:4200/api/agents | jq .`
5. Validate Gitea API:
   - `curl -s http://localhost:3000/api/v1/version | jq .`

## Approval quest handling
- List pending approvals with tier requirements:
  - `curl -s http://localhost:9105/approvals | jq '.pending_approvals[] | {id, action, severity, requester_tier, required_approver_tier, reason}'`
- Approve by id as Admin tier:
  - `curl -s -X POST http://localhost:9105/approve -H "Content-Type: application/json" -d '{"id":"<approval-id>","actor_tier":"admin"}' | jq .`
- Reject by id with reason:
  - `curl -s -X POST http://localhost:9105/reject -H "Content-Type: application/json" -d '{"id":"<approval-id>","actor_tier":"admin","reason":"denied by operator"}' | jq .`
- Legacy index-based approval remains available for compatibility:
  - `curl -s -X POST http://localhost:9105/approve -H "Content-Type: application/json" -d '{"index":0,"actor_tier":"admin"}' | jq .`

## Safe restart patterns
- Restart one service:
  - `docker compose -f compose/docker-compose.yml restart <service>`
- Restart monitoring stack:
  - `docker compose -f compose/docker-compose.yml restart prometheus alertmanager node-exporter cadvisor spirit`
- Restart agency layer:
  - `docker compose -f compose/docker-compose.yml restart openfang`

## Updates
1. Pull upstream images:
   - `docker compose -f compose/docker-compose.yml pull`
2. Rebuild Spirit if code changed:
   - `docker compose -f compose/docker-compose.yml build spirit`
3. Rebuild OpenFang runtime if version pin changed:
   - `docker compose -f compose/docker-compose.yml build openfang`
4. Apply update:
   - `docker compose -f compose/docker-compose.yml up -d`
5. Validate:
   - `docker compose -f compose/docker-compose.yml ps`
   - `curl -s http://localhost:9105/health | jq .`
   - `curl -s http://localhost:4200/api/health | jq .`
   - `curl -s http://localhost:3000/api/healthz | jq .`

## OpenFang Personas bootstrap
The API expects `manifest_toml` (inline TOML content) in the JSON body. Helper to spawn from a manifest file:
```
MANIFEST=$(cat <path-to-agent.toml>)
curl -s -X POST http://localhost:4200/api/agents \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "import json,sys; print(json.dumps({'manifest_toml': sys.stdin.read()}))" <<< "$MANIFEST")"
```
- Spawn all Spirit personas from project manifests:
  - `for a in spirit-orchestrator spirit-observer spirit-reflector; do M=$(cat openfang/agents/$a/agent.toml); curl -s -X POST http://localhost:4200/api/agents -H "Content-Type: application/json" -d "$(python3 -c "import json,sys; print(json.dumps({'manifest_toml': sys.stdin.read()}))" <<< "$M")"; echo; done`
- List running personas:
  - `curl -s http://localhost:4200/api/agents | jq '.[].name'`

## Optional University building
- Start llama.cpp only when needed:
  - `docker compose -f compose/docker-compose.yml --profile university up -d llama-cpp`
- Stop optional LLM service:
  - `docker compose -f compose/docker-compose.yml --profile university stop llama-cpp`

## Forge deployment (Gitea on host via Tailscale)
- Artifacts:
  - `ops/gitea/docker-compose.host.yml`
  - `ops/gitea/.env.example`
  - `ops/gitea/deploy_wera.sh`
- Deploy to lab host:
  - `./ops/gitea/deploy_wera.sh`
- After deploy:
  - access URL and admin credentials are stored on host in `/home/wera/.secrets/gitea-admin.env`

## Fortress integration checklist
- Nextcloud reachable: `http://localhost:8080`
- Nextcloud AIO admin UI reachable: `https://localhost:8443`
- FilantropiaSolar app enabled in Nextcloud and configured with:
  - Prometheus endpoint: `http://prometheus:9090`
  - Spirit endpoint: `http://spirit:9105`
  - Rundeck endpoint: `http://rundeck:4440`

## Odoo stack on TRL4 (restore profile)
- Host workspace:
  - `~/odoo-app`
- Bring stack up:
  - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env config --quiet`
  - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env up -d`
- Restore `wera.dump.zip`:
  - `rm -rf /tmp/wera-odoo-restore && mkdir -p /tmp/wera-odoo-restore`
  - `unzip -o ~/odoo-app/wera.dump.zip -d /tmp/wera-odoo-restore`
  - `cat /tmp/wera-odoo-restore/dump.sql | docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo-db psql -U odoo -d wera`
  - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo sh -lc 'mkdir -p /var/lib/odoo/filestore/wera'`
  - `docker cp /tmp/wera-odoo-restore/filestore/. solarseed-odoo:/var/lib/odoo/filestore/wera/`
  - `docker exec -u 0 solarseed-odoo chown -R odoo:odoo /var/lib/odoo/filestore/wera`
  - `source ~/odoo-app/.env && docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo odoo shell -d ${ODOO_DB_NAME:-wera} --db_host=odoo-db -r ${ODOO_DB_USER:-odoo} -w "$ODOO_DB_PASSWORD" < ~/odoo-app/scripts/ensure_enterprise_subscription.py`
  - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo-db psql -U ${ODOO_DB_USER:-odoo} -d ${ODOO_DB_NAME:-wera} -c "select key, value from ir_config_parameter where key='database.enterprise_code';"`
- Validate:
  - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env ps`
  - `curl -I http://127.0.0.1:8069/web/login?db=wera`
  - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env logs --tail=120 odoo`
- Tailnet exposure (TRL4 host only):
  - `sudo tailscale set --operator=wera` (one-time optional)
  - `sudo tailscale serve --bg 8069`
  - `tailscale serve status`
  - Current expected output:
    - `https://wera-ss-pt-sn-1.tailfb390c.ts.net (tailnet only)`
    - `|-- / proxy http://127.0.0.1:8069`
  - Validate from operator workstation:
    - `curl -I 'https://wera-ss-pt-sn-1.tailfb390c.ts.net/web/login?db=wera'`
  - Disable exposure:
    - `tailscale serve --https=443 off`
  - Re-enable exposure:
    - `sudo tailscale serve --bg 8069`
## Fonseca rollout replay on TRL4 (P8 manual callback mode)
Use this when shipping the current `wera_fonseca_site` rollout to TRL4 while appointment enterprise addons are unavailable.
- Scope:
  - apply addon/script delta from local validated branch state
  - run module upgrade for `wera_fonseca_site`
  - enforce manual consultation callback mode and normalize unsupported appointment queue states
  - verify route + CTA + CRM lead/activity contracts without destructive DB actions
- Batched SSH execution sequence:
  1. Preflight and sync:
     - `cd ~/odoo-app`
     - `git --no-pager status --short`
     - `git --no-pager rev-parse --abbrev-ref HEAD`
     - `git --no-pager pull --ff-only`
     - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env config --quiet`
  2. Apply rollout:
     - `source ~/odoo-app/.env && docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo odoo -d ${ODOO_DB_NAME:-wera} --db_host=odoo-db -r ${ODOO_DB_USER:-odoo} -w "$ODOO_DB_PASSWORD" -u wera_fonseca_site --stop-after-init`
     - `source ~/odoo-app/.env && docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo odoo shell -d ${ODOO_DB_NAME:-wera} --db_host=odoo-db -r ${ODOO_DB_USER:-odoo} -w "$ODOO_DB_PASSWORD" < ~/odoo-app/scripts/fonseca_trl4_rollout.py`
     - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env up -d odoo`
  3. Post-checks:
     - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env ps`
     - `curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:8069/' -H 'Host: fonseca-gardens.wera-ss-pt-sn-1.tailfb390c.ts.net'`
     - `curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:8069/contactus?intent=quote&partner=fonseca-gardens' -H 'Host: fonseca-gardens.wera-ss-pt-sn-1.tailfb390c.ts.net'`
     - `curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:8069/contactus?intent=consultation&partner=fonseca-gardens' -H 'Host: fonseca-gardens.wera-ss-pt-sn-1.tailfb390c.ts.net'`
     - `curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:8069/appointment' -H 'Host: fonseca-gardens.wera-ss-pt-sn-1.tailfb390c.ts.net'`
     - `source ~/odoo-app/.env && docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo-db psql -U ${ODOO_DB_USER:-odoo} -d ${ODOO_DB_NAME:-wera} -c "select name, latest_version, state from ir_module_module where name in ('wera_fonseca_site','website','crm','appointment','appointment_crm','appointment_hr','appointment_sms','website_appointment_crm','web_gantt','hr_gantt') order by name;"`
     - `source ~/odoo-app/.env && docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo-db psql -U ${ODOO_DB_USER:-odoo} -d ${ODOO_DB_NAME:-wera} -c "select name, state from ir_module_module where name in ('appointment','appointment_crm','appointment_hr','appointment_sms','website_appointment_crm','web_gantt','hr_gantt') and state in ('to install','to upgrade','to remove') order by name;"`
     - `curl -s -i -X POST 'http://127.0.0.1:8069/fonseca/intake' -H 'Host: fonseca-gardens.wera-ss-pt-sn-1.tailfb390c.ts.net' -H 'Content-Type: application/x-www-form-urlencoded' --data 'name=TRL4+Callback+Probe&phone=%2B351900000000&email=callback.probe%40example.com&intent=consultation&property_address=Sintra&message=Manual+callback+validation'`
     - `source ~/odoo-app/.env && docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo-db psql -U ${ODOO_DB_USER:-odoo} -d ${ODOO_DB_NAME:-wera} -c "select l.id, l.name, l.email_from, l.phone, l.create_date, a.summary, a.date_deadline from crm_lead l left join mail_activity a on a.res_model = 'crm.lead' and a.res_id = l.id where l.name ilike '%TRL4 Callback Probe%' order by l.id desc limit 3;"`
- Non-destructive policy:
  - do not run `down -v`, `drop database`, or restore commands in this replay path
  - if rollback is needed, reset code to prior commit and rerun `-u wera_fonseca_site`
- Evidence:
  - Save replay outputs under `ops/evidence/fonseca_phase8_manual_callback_<timestamp>/`
  - Include module state, queue-normalization query output, route codes, and CRM lead/activity verification output.
  - Include content artifacts copied from:
    - `odoo-app/content/fonseca_gardens_source_of_truth.json`
    - `odoo-app/content/fonseca_gardens_visual_request_pack.json`

## Odoo Settings registry mismatch (TRL4)
Use this when Settings UI fails with Owl/undefined-field errors after restore or module drift.

1. Detect runtime offenders (active inherited views referencing runtime-missing `res.config.settings` fields):
   - `source ~/odoo-app/.env && docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo odoo shell -d wera --db_host=odoo-db -r "${ODOO_DB_USER:-odoo}" -w "$ODOO_DB_PASSWORD"`
   - In shell, compare active inherited view field names to `env['res.config.settings']._fields` and list offending view IDs/XMLIDs.
2. Quarantine offending inherited views:
   - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env exec -T odoo-db psql -U odoo -d wera -c "update ir_ui_view set active=false where id in (<offending_ids>);"`
3. Restart Odoo only:
   - `docker compose -f ~/odoo-app/docker-compose.yml --env-file ~/odoo-app/.env restart odoo`
4. Validate Settings endpoints (authenticated):
   - `/web/action/load` with `res.config.settings` action ID
   - `/web/dataset/call_kw/res.config.settings/get_view`
   - `/web/dataset/call_kw/res.config.settings/get_views`
5. Capture audit artifact:
   - Save quarantined view IDs/XMLIDs/missing fields to `/home/wera/.secrets/odoo-settings-view-quarantine-<timestamp>.json`
6. Verify clean state:
   - runtime detector reports `runtime_offender_views=0`
   - recent logs contain no new Settings-specific `ValidationError`/undefined-field failures

## Odoo remediation log (2026-06-05)
Resolution summary for repeated cron failures and PostgreSQL collation warnings observed on the local TRL4 Odoo profile.

- Symptoms observed:
  - Repeated cron failures for IDs `48`, `81`, `82` (`Marketing Automation`, `AI Fields`, `AI Documents`)
  - Recurrent PostgreSQL warning: collation version mismatch for `postgres`/`template1`
  - Repeated Odoo warning scanning obsolete DB `gogardens`

- Actions applied:
  1. Disabled failing cron jobs:
     - `update ir_cron set active=false where id in (48,81,82);`
  2. Refreshed collation metadata:
     - `ALTER DATABASE postgres REFRESH COLLATION VERSION;`
     - `ALTER DATABASE template1 REFRESH COLLATION VERSION;`
  3. Removed obsolete database:
     - `DROP DATABASE IF EXISTS gogardens WITH (FORCE);`

- Verification checks:
  - `select datname from pg_database where datname='gogardens';` -> no rows
  - `select datname, datcollversion, pg_database_collation_actual_version(oid) ...` mismatch query -> no rows
  - `select id, cron_name, active from ir_cron where id in (48,81,82);` -> all inactive
  - `curl -I http://127.0.0.1:8069/web/login?db=wera` -> `200 OK`
  - module queue states (`to install`, `to upgrade`, `to remove`) -> empty

- Current status:
  - Odoo service healthy (`odoo` up, `odoo-db` healthy)
  - Cron failure loop from IDs `48/81/82` stopped
  - PostgreSQL collation mismatch warning resolved for active DBs
  - `gogardens` no longer exists

## TRL4 lab machine review checklist
- Target host profile:
  - Host: `wera-ss-pt-sn-1` (`100.82.194.96`)
  - User: `wera`
- Non-destructive baseline review commands:
  - `ssh wera@100.82.194.96 "hostname; tailscale ip -4; uname -a; uptime"`
  - `ssh wera@100.82.194.96 "if [ -d /data ]; then df -h / /data; else df -h /; fi; grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree' /proc/meminfo"`
  - `ssh wera@100.82.194.96 "docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}'"`
  - `ssh wera@100.82.194.96 "docker inspect --format '{{.Name}} {{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' \$(docker ps -q)"`
  - `ssh wera@100.82.194.96 "sudo docker compose -f /data/city-of-light/docker-compose.yml config --quiet"`
- If SSH authentication fails:
  - verify the operator key installed on TRL4 host for user `wera`
  - verify Tailscale ACL allows source machine access to the TRL4 node
  - retry with explicit key: `ssh -i ~/.ssh/id_ed25519 wera@100.82.194.96`
