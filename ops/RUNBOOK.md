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
