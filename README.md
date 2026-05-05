# SolarSeed v3 — City of Light (TRL4)
SolarSeed v3 is a TRL4 lab deployment of the City of Light: a sovereign edge-hosted stack that combines observability, automation, local AI inference, and agent orchestration.

The project is designed around a practical operating model:
- **Spirit** (FastAPI) observes system state, reflects with local LLM support, and proposes actions through approvals
- **OpenFang** runs agent personas (observer/orchestrator/reflector + domain agents)
- **Prometheus + Alertmanager + exporters** provide telemetry and health visibility
- **Rundeck + PostgreSQL + Redis + Gitea** provide execution, state, event bus, and sovereign source control
- **CityView** is now an external project repository for the gamified observer/mainframe UI (`wera-global/CityView`)

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
- CityView UI is maintained in the separate `ProductionBase/CityView` repository
- `ops/` — operator config and runbook (`CONFIG.md`, `RUNBOOK.md`) plus host Gitea deployment artifacts in `ops/gitea/`
- `docs/research/` — architecture and research reports
- `docs/reference/` — reference PDFs
- `WARP.md` — TRL4 operational guide (current-state operations)
- `WIZARD.md` — target-state deployment/architecture specification

## Prerequisites
- Docker Engine + Docker Compose v2
- Git
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

## CityView extraction
CityView has been extracted from this repository and is now maintained in `ProductionBase/CityView` (`wera-global/CityView` on Gitea).
For UI development/runtime, use the CityView repository and its `compose/docker-compose.yml`.

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
