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

## TRL5 field machine review checklist
- Target host profile:
  - Host: `wera-ss-pt-tv-1.tailfb390c.ts.net`
  - User: `wera-admin`
- Non-destructive baseline review commands:
  - `ssh wera-admin@wera-ss-pt-tv-1.tailfb390c.ts.net "hostname; tailscale ip -4; uname -a; uptime"`
  - `ssh wera-admin@wera-ss-pt-tv-1.tailfb390c.ts.net "id; getent group docker; ls -l /var/run/docker.sock"`
  - `ssh wera-admin@wera-ss-pt-tv-1.tailfb390c.ts.net "docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}'"`
  - `ssh wera-admin@wera-ss-pt-tv-1.tailfb390c.ts.net "docker inspect --format '{{.Name}} {{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' \$(docker ps -q)"`
  - `ssh wera-admin@wera-ss-pt-tv-1.tailfb390c.ts.net "if [ -d /data ]; then df -h / /data; else df -h /; fi"`
- If SSH authentication fails:
  - verify the operator key installed on TRL5 host for user `wera-admin`
  - verify Tailscale ACL allows source machine access to the TRL5 node
  - retry with explicit key: `ssh -i ~/.ssh/id_ed25519 wera-admin@wera-ss-pt-tv-1.tailfb390c.ts.net`

## TRL5 outbound email (Nextcloud + Odoo via Proton Bridge)
Status (2026-08-16, **verified working**):
- Host SMTP proxy + NC/Odoo SMTP wiring deployed and enabled
- NC Admin email test: OK
- Odoo outgoing Test Connection: OK
- Odoo user invitation delivery: OK (after bounce/return-path + alias-domain fixes)
- Bridge account index `0` (`Tomás Crespim` / mailbox `cloud@wera.global`) must stay **connected** (re-login with Proton password + 2FA after some Bridge restarts)

Scope: transactional notifications only (NC password reset / shares, Odoo invitations/chatter). Not bulk marketing.

### Architecture
```
Nextcloud AIO / filantropia-odoo
  -> TCP 172.18.0.1:1025  (also 172.19.0.1:1025)
  -> systemd socat: protonmail-smtp-docker-proxy.service
  -> Proton Mail Bridge 127.0.0.1:1025 (STARTTLS + AUTH PLAIN/LOGIN)
  -> Proton
```
Host units / files:
- `protonmail.service` (oneshot, enabled) — user `protonmail`, `/home/protonmail/protonmail.sh` starts tmux session `protonmail` with `protonmail-bridge --cli`
- `protonmail-smtp-docker-proxy.service` (simple, enabled) — `/usr/local/sbin/protonmail-smtp-docker-proxy.sh`
- Bridge keychain helper: `pass` (`~protonmail/.password-store`); GPG key present for vault
- Do **not** publish SMTP on `0.0.0.0` or Tailscale

### Preflight (on TRL5 as `wera-admin`)
```
systemctl is-active protonmail.service protonmail-smtp-docker-proxy.service
systemctl is-enabled protonmail.service protonmail-smtp-docker-proxy.service
ss -lntp | grep -E '1025|1143'
# Expect bridge: 127.0.0.1:1025 and :1143
# Expect proxy: 172.18.0.1:1025 and 172.19.0.1:1025
docker exec nextcloud-aio-nextcloud nc -zv -w 2 172.18.0.1 1025
```
If Bridge process is missing but proxy is up, restart Bridge then proxy:
```
sudo systemctl restart protonmail.service
sleep 2
sudo systemctl restart protonmail-smtp-docker-proxy.service
```

### Manual Bridge login (required when `list` shows signed out)
1. From your laptop:
```
ssh -t wera-admin@wera-ss-pt-tv-1.tailfb390c.ts.net
```
2. Attach Bridge CLI (needs sudo password):
```
sudo -u protonmail tmux attach -t protonmail
```
If no session:
```
sudo systemctl restart protonmail.service
sudo -u protonmail tmux attach -t protonmail
```
3. In Bridge interactive shell:
```
list
login 0
```
4. Enter **Proton account password** (not the old Bridge SMTP password), then complete **2FA** when prompted.
5. Confirm connected:
```
list
# expect account 0 status connected / logged in (not "signed out")
info 0
```
6. From `info 0`, copy **SMTP** block only:
   - Address: `127.0.0.1` (apps use Docker gw instead)
   - SMTP port: `1025`
   - Username: usually full mailbox address
   - Password: **Bridge mailbox password** (generated; different from Proton login)
   - Security: STARTTLS
7. Detach tmux without killing Bridge: `Ctrl-b` then `d`.

Optional durable secret (root only, never commit):
```
sudo mkdir -p /root/.secrets
sudo install -m 600 /dev/null /root/.secrets/proton-bridge-smtp.env
sudoeditor /root/.secrets/proton-bridge-smtp.env
# SMTP_USER=...
# SMTP_PASS=...
# SMTP_HOST=127.0.0.1
# SMTP_PORT=1025
# FROM=cloud@wera.global
```

### Apply credentials to Nextcloud
Replace placeholders; do not log passwords.
```
docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_smtphost --value=172.18.0.1
docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_smtpport --value=1025
docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_smtpmode --value=smtp
docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_sendmailmode --value=smtp
docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_smtpsecure --value=tls
docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_smtpauth --type=boolean --value=true
docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_smtpname --value='SMTP_USER_FROM_INFO'
docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_smtppassword --value='SMTP_PASS_FROM_INFO'
docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_smtpstreamoptions --type=json \
  --value='{"ssl":{"allow_self_signed":true,"verify_peer":false,"verify_peer_name":false}}'
# keep from-address aligned with Proton send-as
# docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_from_address --value=cloud
# docker exec -u 33 nextcloud-aio-nextcloud php occ config:system:set mail_domain --value=wera.global
```
Test (Admin UI: Basic settings -> Email server -> Send email), or CLI semantics:
- `IMailer::send()` returns **empty array on success**
- non-empty array = failed recipients (do not treat as OK)

### Apply credentials to Odoo
UI path: Settings -> Technical -> Email -> Outgoing Mail Servers -> `Proton Bridge (host via docker gw)`
- SMTP Host: `172.18.0.1`
- SMTP Port: `1025`
- Connection Encryption: **TLS (STARTTLS), encryption only** (`starttls`)
- Authenticate with: Username
- Username / Password: Bridge values from `info 0`
- From Filter: domain `wera.global` (or exact allowed address)
- Test Connection, then send a chatter/test notification

Odoo 19 also needs a **mail alias domain** (not only SMTP server), or invitations fail with:
`You must either provide a sender address explicitly or configure using mail.catchall.domain and mail.default.from`

Required records (already applied on TRL5 2026-08-16):
- `mail.alias.domain`: name `wera.global`, `default_from=cloud`
- **Proton Bridge constraint:** bounce/catchall aliases must also resolve to an address Bridge accepts (use `cloud`, not `bounce`/`catchall`). Bridge logs `invalid return path` and SMTP `554` if envelope MAIL FROM is not the mailbox.
- `res.company` id 1: `email=cloud@wera.global`, `alias_domain_id` -> that domain
- System partners: OdooBot + Administrator email `cloud@wera.global` (not `odoobot@example.com` / empty)
- ICPs: `mail.default.from=cloud`, `mail.catchall.domain=wera.global`, bounce/catchall aliases `cloud`
- Verify: Odoo shell send to `cloud@wera.global` ends `mail.state=sent`; Bridge must be `connected`

### Final verified configuration (2026-08-16, no secrets)
Host:
- Units active+enabled: `protonmail.service`, `protonmail-smtp-docker-proxy.service`
- Listen: `127.0.0.1:1025` / `1143` (Bridge); `172.18.0.1:1025` + `172.19.0.1:1025` (proxy)
- Bridge mailbox / SMTP user: `cloud@wera.global`

| App | Host | Port | Encryption | From / notes |
|-----|------|------|------------|--------------|
| Nextcloud AIO | `172.18.0.1` | 1025 | `tls` + streamoptions (self-signed allow) | `cloud@wera.global`; auth on |
| Odoo `filantropia_public` | `172.18.0.1` | 1025 | `starttls` / `login` | server `Proton Bridge (host via docker gw)`; `from_filter=wera.global` |

Odoo identity (required for invitations):
- Company: `Filantropia Solar` / `cloud@wera.global` / `alias_domain_id` -> `wera.global`
- `mail.alias.domain`: `default_from=bounce=catchall=cloud` (must be mailbox-compatible for Bridge return-path)
- ICPs: `mail.default.from=cloud`, `mail.catchall.domain=wera.global`, bounce/catchall aliases `cloud`
- Partners: OdooBot + Administrator emails `cloud@wera.global`

### Failure symptoms
- Connection refused to `172.18.0.1:1025` -> proxy down or Docker bridge gateway IP changed
- SMTP `454` / auth errors while ports listen -> Bridge password stale **or** `list` shows `signed out`/`locked`
- `554` + Bridge log `invalid return path` -> bounce/catchall alias is not the Bridge mailbox (use `cloud@wera.global`, not `bounce@`)
- `554` account not available / sender invalid with `odoobot@example.com` -> fix OdooBot/admin partner emails
- NC `send()` returns recipient address(es) -> failure (empty array = success)
- After reboot: both units active, but account may still need `login 0` again if session tokens expired
- Bridge CLI warning `dbus-launch` missing is non-fatal when keychain helper is `pass`

### Related docs
- FilantropiaSolar: `docs/ops/TRL5-NC-ACCESS.md` (short pointer)

## TRL5 stabilization notes (2026-07-05)
- Tailscale operator user for TRL5 is `wera-admin`:
  - `sudo tailscale set --operator=wera-admin`
- Nextcloud tailnet exposure is managed via persisted Tailscale serve state:
  - `sudo tailscale serve --bg http://127.0.0.1:11000`
  - check with `tailscale serve status`
- `tailscale-serve-nextcloud.service` is intentionally disabled to avoid boot-time false failures (`unexpected state: NoState`) because serve state already persists in tailscaled:
  - `sudo systemctl disable --now tailscale-serve-nextcloud.service`
- `openipmi.service` is intentionally masked on current TRL5 hardware profile (no usable local BMC device path):
  - `sudo systemctl disable --now openipmi.service`
  - `sudo systemctl mask openipmi.service`
- Post-change verification commands:
  - `systemctl --failed --no-pager --plain`
  - `curl -I --max-time 8 https://wera-ss-pt-tv-1.tailfb390c.ts.net`
  - `docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' $(docker ps -q) | sort | uniq -c`

## TRL5 Nextcloud LocalAI restore (2026-08-16)
Local LLM/STT for Nextcloud Assistant on TRL5 is the AIO community container `nextcloud-aio-local-ai` (not a separate Ollama/llama.cpp University stack).

### Working baseline after restore
- Image: `ghcr.io/docjyj/aio-local-ai-vulkan:v1` (LocalAI ~v3.10)
- Container: `nextcloud-aio-local-ai` on network `nextcloud-aio`
- Listen: `LOCALAI_ADDRESS=:10078`
- Host publish: `127.0.0.1:10078->10078`
- Healthcheck env: `HEALTHCHECK_ENDPOINT=http://localhost:10078/readyz` (must match listen port)
- Volumes (persistent):
  - `nextcloud_aio_localai_models` -> `/models`
  - `nextcloud_aio_localai_backends` -> `/backends`
  - `nextcloud_aio_localai_configuration` -> `/configuration`
- Nextcloud apps: `integration_openai` + `assistant`
  - URL: `http://nextcloud-aio-local-ai:10078`
  - Default chat model: `llama-3.2-1b-instruct:q4_k_m`
  - Default STT model: `whisper-1`
- Required backends installed into the backends volume:
  - `llama-cpp` (+ `vulkan-llama-cpp`)
  - `whisper` (+ `vulkan-whisper`)

### Symptoms that mean backends are missing
- Chat / Assistant: HTTP 500 with `backend not found: llama-cpp`
- Transcribe audio: HTTP path may return 200 with empty failure path in NC UI; LocalAI logs show `Backend not found backend="whisper"` and `Failed to load model modelID="whisper-1"`
- Docker may show `unhealthy` even when API is up if healthcheck still points at `:8080` while app listens on `:10078`

### Repair procedure (non-destructive)
Install missing backends into the running container (writes only the backends volume):
```
ssh wera-admin@wera-ss-pt-tv-1.tailfb390c.ts.net
docker exec nextcloud-aio-local-ai /local-ai backends install llama-cpp
docker exec nextcloud-aio-local-ai /local-ai backends install whisper
docker restart nextcloud-aio-local-ai
```
Wait for readiness:
```
curl -sS -m 5 -o /dev/null -w '%{http_code}\n' http://127.0.0.1:10078/readyz
docker inspect nextcloud-aio-local-ai --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}'
docker exec nextcloud-aio-local-ai ls -la /backends
```

### Healthcheck fix (Phase B)
Image default is `HEALTHCHECK_ENDPOINT=http://localhost:8080/readyz`, but AIO community config sets `LOCALAI_ADDRESS=:10078`. Correct env:
```
HEALTHCHECK_ENDPOINT=http://localhost:10078/readyz
```
Applied on TRL5 by:
1. Patching mastercontainer community def:
   `/var/www/docker-aio/community-containers/local-ai/local-ai.json`
   (add the HEALTHCHECK_ENDPOINT env line)
2. Recreating `nextcloud-aio-local-ai` with the same named volumes/network/port bind and corrected env (do not wipe volumes).

Durability caveat: the `local-ai.json` patch lives in the running mastercontainer filesystem and can be lost when the AIO mastercontainer image is upgraded/recreated. After AIO upgrades, re-check health and re-apply env if LocalAI becomes `unhealthy` again while `:10078/readyz` still returns 200.

### Verification (do not print API keys)
```
# readiness
curl -sS -m 5 -o /dev/null -w '%{http_code}\n' http://127.0.0.1:10078/readyz

# chat smoke (reads key from NC app config; do not echo KEY)
KEY=$(docker exec nextcloud-aio-nextcloud php occ config:app:get integration_openai api_key)
curl -sS -m 120 -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
  http://127.0.0.1:10078/v1/chat/completions \
  -d '{"model":"llama-3.2-1b-instruct:q4_k_m","messages":[{"role":"user","content":"Reply with exactly: OK"}],"max_tokens":8,"temperature":0}'
unset KEY

# from Nextcloud container
docker exec nextcloud-aio-nextcloud curl -sS -m 5 -o /dev/null -w '%{http_code}\n' http://nextcloud-aio-local-ai:10078/readyz
```
STT smoke: any short wav/mp3 via `POST /v1/audio/transcriptions` with `model=whisper-1` and Bearer key must return HTTP 200 without `backend not found` in LocalAI logs. Empty `text` on pure tones is OK; real speech should produce text in Nextcloud UI.

### Operational guardrails
- Prefer small defaults (`llama-3.2-1b-instruct:q4_k_m`, `whisper-1` / base GGML). Large Qwen3-VL 30B-class models can exhaust ~27 GiB RAM.
- Do not delete `/models` or backends volumes during repair.
- Host `:8080` is AIO mastercontainer, not LocalAI.
- No separate Ollama/`llama-server` was required for this Nextcloud Assistant path on TRL5.
