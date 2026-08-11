# buildings.md -- City of Light Building Registry

All apps and services available to agents on wera-ss-pt-sn-1.
Updated: 2026-03-28

---

## Docker Buildings (Container Services)

### Fortress -- Nextcloud AIO
- **Container**: nextcloud-aio-mastercontainer
- **Image**: nextcloud/all-in-one:latest
- **Port**: 8080 (admin), 443 (HTTPS when configured)
- **Memory**: ~2 GB
- **Status**: Healthy
- **Access**: http://100.82.194.96:8080
- **Purpose**: Central platform for users, files, communication, and AI integration
- **Nextcloud Apps** (standard organisational package):
  - **Files** -- file storage, sharing, versioning, WebDAV access
  - **Talk** -- chat, video calls, agent-to-human communication
  - **Calendar** -- scheduling, event management
  - **Contacts** -- address book, agent identity registry
  - **Mail** -- email client (when SMTP configured)
  - **Deck** -- kanban boards, task management
  - **Notes** -- markdown notes
  - **Office** -- document editing (Collabora/OnlyOffice when enabled)
  - **Forms** -- surveys, data collection
  - **Groupware** -- organisation management
  - **AI Assistant** -- LLM-powered text generation, summarization (connects to local LLM)
  - **Context Agent** -- MCP-based agent tool access
  - **Full Text Search** -- search across all content
  - **External Storage** -- mount S3, FTP, WebDAV, SFTP sources
  - **Two-Factor Auth** -- TOTP, WebAuthn security

### Library -- Prometheus + Alertmanager
- **Container**: col-prometheus
- **Image**: prom/prometheus:v3.3.0
- **Port**: 9090
- **Memory**: 512 MB
- **Status**: Healthy (4 scrape targets UP)
- **Access**: http://100.82.194.96:9090
- **Purpose**: Metrics collection, time-series database, alerting engine
- **Scrape targets**: prometheus, node-exporter, cadvisor, spirit
- **Sub-building -- Alertmanager**:
  - Container: col-alertmanager
  - Image: prom/alertmanager:v0.28.1
  - Port: 9093 (localhost only)
  - Memory: 64 MB

### University -- llama.cpp LLM Server
- **Container**: col-llama-cpp
- **Image**: ghcr.io/ggml-org/llama.cpp:server
- **Port**: 8081
- **Memory**: 3 GB (limit)
- **Status**: Healthy
- **Access**: http://100.82.194.96:8081
- **Purpose**: Local LLM inference for Spirit reflection and agent reasoning
- **Model**: Qwen 3.4B Q4_K_M (2 GB GGUF v3)
- **API**: OpenAI-compatible `/v1/chat/completions`
- **Config**: 4 threads, ctx 2048, parallel 1
- **Throughput**: ~8-12 tok/s on i5-4430 DDR3

### House -- PostgreSQL
- **Container**: col-postgres
- **Image**: postgres:16-bookworm
- **Port**: 5432 (internal only)
- **Memory**: 512 MB
- **Status**: Healthy
- **Access**: Internal Docker network only (no web UI)
- **Purpose**: Relational database for Spirit memory, resource ledger, agent data
- **Database**: cityoflight
- **Auth**: Docker secrets (pg_password file)

### Agency -- OpenFang Agent OS
- **Container**: col-openfang
- **Image**: city-openfang:v1 (OpenFang v0.5.2, built from Rust source)
- **Port**: 4200
- **Memory**: 512 MB
- **Status**: Healthy
- **Access**: http://100.82.194.96:4200
- **Purpose**: Agent Operating System managing AI agent lifecycle, scheduling, and tool access
- **LLM Provider**: vllm (OpenAI-compatible) pointing to llama-cpp:8081
- **Features**:
  - Agent creation and management via TOML manifests
  - 16-layer security model (WASM sandbox, audit trail, taint tracking)
  - Shell execution (`shell_exec`), file operations, web fetch
  - Memory: SQLite + vector embeddings
  - WebChat UI for agent interaction
  - Scheduled agent tasks (cron-style)
- **Current agents**: spirit-observer, spirit-orchestrator, spirit-reflector (manifests in `openfang/agents/`)

### Forge -- Gitea
- **Container**: col-gitea
- **Image**: gitea/gitea:1.25.5
- **Port**: 3000 (HTTP), 2222 (SSH Git)
- **Memory**: 256 MB
- **Status**: Planned (TRL4.1 rollout)
- **Access**: `http://<tailscale-host>:3000`
- **Purpose**: Sovereign source control forge for SolarSeed repositories, issues, and pull requests
- **Database**: PostgreSQL `gitea` DB/user on the internal Docker network
- **Security baseline**:
  - Registration disabled
  - Sign-in required to view repositories
  - Access scoped by Tailscale network policy

### Event Bus -- Redis
- **Container**: col-redis
- **Image**: redis:7-alpine
- **Port**: 6379 (internal only)
- **Memory**: 256 MB
- **Status**: Healthy
- **Access**: Internal Docker network only
- **Purpose**: Agent-to-agent communication backbone via Redis Streams
- **Config**: AOF persistence, password auth, FLUSHDB/FLUSHALL disabled
- **Channels** (planned):
  - `city/heartbeat/{agent_id}` -- per-agent liveness
  - `city/security/alert` -- security events
  - `city/spirit/state` -- Spirit beliefs summary
  - `city/agent/register` -- agent registration events
  - `city/tikkun/request` -- self-repair requests

---

## Sensorium (Hardware Monitoring)

### Node Exporter
- **Container**: col-node-exporter
- **Image**: prom/node-exporter:v1.9.0
- **Port**: 9100 (internal)
- **Memory**: 64 MB
- **Purpose**: Hardware proprioception (CPU temp, memory, disk, network, load)

### cAdvisor
- **Container**: col-cadvisor
- **Image**: gcr.io/cadvisor/cadvisor:v0.52.1
- **Port**: 8080 (internal, shared with Nextcloud)
- **Memory**: 128 MB
- **Purpose**: Container resource metrics (CPU, RAM, network per container)

---

## Spirit (Observation Process)

### Spirit Heartbeat
- **Container**: col-spirit
- **Image**: city-spirit:latest (Python/FastAPI)
- **Port**: 9105
- **Memory**: 256 MB
- **Access**: http://100.82.194.96:9105
- **Purpose**: Self-aware heartbeat of the City; observes, reflects, proposes
- **Endpoints**:
  - `GET /health` -- liveness
  - `GET /api/v1/status` -- buildings, approvals, and approval policy tiers
  - `GET /api/v1/reflection` -- latest LLM reflection
  - `GET /metrics` -- Prometheus metrics
  - `GET /approvals` -- pending approval queue and supported tiers
  - `POST /approve` -- tier-aware approval by `id` (or legacy `index`) + `actor_tier`
  - `POST /reject` -- tier-aware rejection by `id` (or legacy `index`) + `actor_tier`
- **Approval item fields**: `id`, `action`, `severity`, `requester_tier`, `required_approver_tier`, `reason`, `timestamp`

---

## OS-Level Services (Psycho -- Admin only)

| Service | Version | Purpose |
|---------|---------|---------|
| Debian 13 (Trixie) | 13 | Operating system |
| Docker CE | 29.3.0 | Container runtime |
| Tailscale | 1.96.2 | VPN mesh (secure remote access) |
| chrony | 4.6.1 | NTP time synchronization |
| OpenSSH | 10.0p1 | Secure shell access |
| UFW | 0.36.2 | Firewall (deny-all + allowlist) |

---

## Soul (Constitution)

| File | Location | Purpose |
|------|----------|---------|
| soul.md | `/data/city-of-light/soul.md` | Computable constitution with Four Invariants |
| .soul-hash | `/data/city-of-light/.soul-hash` | HMAC-SHA256 integrity hash |
| soul-key | `/data/.secrets/soul-key` | HMAC key (root-only) |
| christ-soul.md | `/data/city-of-light/christ-soul.md` | 12 operational principles |

---

## Not Yet Deployed (TRL4 Roadmap)

| Building | Service | Purpose | Priority |
|----------|---------|---------|----------|
| Dashboard | Grafana 11 | Visualization + alerting UI | MEDIUM |
| Factory | Rundeck 5.7 | Workflow automation, RBAC jobs | MEDIUM |
| Gateway | Caddy 2 | Reverse proxy + auto HTTPS | LOW |
| Lighthouse | RxInferServer.jl | Spirit Bayesian inference engine | FUTURE |
| Pushgateway | prom/pushgateway | Agent heartbeat metrics receiver | PLANNED |
