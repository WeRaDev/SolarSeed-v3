# SolarSeed v3 — City of Light (TRL4)
SolarSeed v3 is a TRL4 lab deployment of the City of Light: a sovereign edge-hosted stack that combines observability, automation, local AI inference, and agent orchestration.

The project is designed around a practical operating model:
- **Spirit** (FastAPI) observes system state, reflects with local LLM support, and proposes actions through approvals
- **OpenFang** runs agent personas (observer/orchestrator/reflector + domain agents)
- **Prometheus + Alertmanager + exporters** provide telemetry and health visibility
- **Rundeck + PostgreSQL + Redis + Gitea** provide execution, state, event bus, and sovereign source control
- **cityview** provides a Vue-based gamified observer/mainframe UI

## Current architecture (repository runtime)
Primary compose stack is defined in `compose/docker-compose.yml`.

Core services:
- `spirit` (`9105`) — heartbeat, reflection, meditation, approval API
- `openfang` (`4200`) — Agent OS API/WebChat
- `prometheus` (`9090`) — metrics and query API
- `alertmanager` (`9093`) — alert routing
- `postgres` (`5432`, internal) — relational data backend
- `rundeck` (`4440`) — automation/job execution
- `gitea` (`3000` HTTP, `2222` SSH) — self-hosted Git forge
- `node-exporter` + `cadvisor` — host/container metrics

Optional service profile:
- `llama-cpp` (`8081`) — local OpenAI-compatible inference endpoint for Spirit/OpenFang (`--profile university`)

External integration:
- Nextcloud/Fortress is currently managed outside this compose file; notes are embedded in `compose/docker-compose.yml`.

## Repository layout
- `compose/` — main Docker Compose stack and environment file location
- `spirit/` — Python FastAPI service and heartbeat/reflection logic
- `openfang/` — OpenFang config and agent manifests
- `prometheus/` — scrape configuration and rule files
- `alertmanager/` — alert routing config
- `rundeck/` — Rundeck configuration
- `cityview/` — Vue 3 + Pinia + Vite UI
- `ops/` — operator config and runbook (`CONFIG.md`, `RUNBOOK.md`) plus host Gitea deployment artifacts in `ops/gitea/`
- `docs/research/` — architecture and research reports
- `docs/reference/` — reference PDFs
- `WARP.md` — TRL4 operational guide (current-state operations)
- `WIZARD.md` — target-state deployment/architecture specification

## Prerequisites
- Docker Engine + Docker Compose v2
- Git
- For `cityview` development: Node.js 18+ and npm
- For direct Spirit development: Python 3.12+

## Quick start (local compose stack)
1. Create `compose/.env` (required variables):
   - `POSTGRES_PASSWORD=<strong-password>`
   - `RUNDECK_ADMIN_PASSWORD=<strong-password>`
   - `GITEA_DB_PASSWORD=<strong-password>`

2. Create Gitea PostgreSQL role/database once (idempotent example):
   ```bash
   docker compose -f compose/docker-compose.yml exec -T postgres \
     psql -U ${POSTGRES_USER:-citydb} -d ${POSTGRES_DB:-cityoflight} \
     -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='gitea') THEN CREATE ROLE gitea LOGIN PASSWORD '${GITEA_DB_PASSWORD}'; END IF; END \$\$;"
   docker compose -f compose/docker-compose.yml exec -T postgres \
     psql -U ${POSTGRES_USER:-citydb} -d ${POSTGRES_DB:-cityoflight} \
     -c "SELECT 'CREATE DATABASE gitea OWNER gitea' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='gitea')\\gexec"
   ```

3. (Optional) Add LLM/Spirit tuning values in the same file, e.g.:
   - `SPIRIT_LLM_ENABLED=true`
   - `SPIRIT_LLM_ENDPOINT=http://llama-cpp:8081`
   - `SPIRIT_LLM_TIMEOUT=90`
   - `SPIRIT_LLM_MAX_TOKENS=256`
   - `LLAMA_MODEL=/models/<model>.gguf`

4. Start core stack:
   ```bash
   docker compose -f compose/docker-compose.yml up -d
   ```

5. Start optional LLM service:
   ```bash
   docker compose -f compose/docker-compose.yml --profile university up -d llama-cpp
   ```

6. Verify health:
   ```bash
   docker compose -f compose/docker-compose.yml ps
   curl -s http://localhost:9105/health | jq .
   curl -s http://localhost:4200/api/health | jq .
   curl -s http://localhost:3000/api/healthz
   curl -s http://localhost:9090/-/healthy
   ```

## cityview UI (local development)
`cityview` proxies API calls to Spirit/OpenFang/Prometheus via Vite.

```bash
cd cityview
npm install
CITY_HOST=<target-host-or-ip> npm run dev
```

Default dev server:
- `http://localhost:5173`

## cityview UI (local Docker runtime)
`cityview` can now run as a dedicated Docker service in `compose/docker-compose.yml`.

Start UI only (assumes backend endpoints are reachable from configured host values):
```bash
docker compose -f compose/docker-compose.yml up -d --no-deps cityview
```

Start UI with core backend services:
```bash
docker compose -f compose/docker-compose.yml up -d postgres prometheus spirit openfang cityview
```

Runtime host controls:
- `CITYVIEW_CITY_HOST` controls `CITY_HOST` used by Vite proxy targets.
- `POLY_ROBOT_HOST` controls the Poly-Robot proxy target (`:8765`).
- If unset, both default to `host.docker.internal` in the dockerized UI service.

## Reconciliation plan (Docker-based)
The current reconciliation baseline keeps Poly-Robot and Odoo additions while stabilizing runtime through Dockerized `cityview`.

1. Standardize local UI startup through Compose (`cityview` service) instead of ad-hoc host Node runs.
2. Keep Poly-Robot integration enabled in `cityview` (`golden-mine`, `/poly-robot` proxy, health polling) and validate it via host-configurable envs.
3. Preserve `odoo-app/` as an intentional local addition; decide separately whether it should be tracked in this repository or ignored.
4. Use two operational modes:
   - UI-only: `up -d --no-deps cityview`
   - Full local stack: `up -d postgres prometheus spirit openfang cityview`
5. Gate future behavior changes behind explicit env flags, while keeping the Docker runtime path stable.

## Spirit API surface
Main endpoints exposed by `spirit/src/spirit.py`:
- `GET /health`
- `GET /api/v1/status`
- `GET /api/v1/reflection`
- `GET /api/v1/meditation`
- `GET /metrics`
- `GET /approvals`
- `POST /approve`
- `POST /reject`
- `POST /webhook/prometheus` (and severity variants)

Approval model supports tiered approvers:
- `guest`, `external_agent`, `internal_agent`, `admin`

## OpenFang agents in this repo
Agent manifests are stored under `openfang/agents/`:
- `spirit-observer`
- `spirit-orchestrator`
- `spirit-reflector`
- `keeper`
- `sentinel`

OpenFang base config is in `openfang/config.toml`.

## Operations and runbook
Primary day-2 commands and procedures are documented in:
- `ops/RUNBOOK.md`
- `ops/CONFIG.md`

These include:
- routine health checks
- approval quest handling
- safe restart/update patterns
- optional LLM lifecycle controls

## Important notes
- Keep secrets out of Git (`compose/.env` is gitignored).
- `models/` and runtime state paths are intentionally ignored.
- The repository compose file is a **reference/runtime template**; deployed host compose may differ in production.
- Use Gitea as the canonical Git host for this project.

## Related project documents
- `WARP.md` — current TRL4 machine operations guide
- `WIZARD.md` — canonical architecture/deployment specification
- `WIZARD_V5.md` — v5 source specification
- `WIZARD-changelog.md` — historical archive
