# WARP.md -- City of Light TRL4 (Lab Deployment)

Purpose: Operational guide for Warp Agent Mode to develop, deploy, and operate the City of Light on the TRL4 lab machine (wera-ss-pt-sn-1). This file bridges the deployed v3.1 reality with the v5 architectural specification.

Stage: **TRL4** -- Lab validation with unlimited energy. After TRL4 success, repeat in field with limited solar power (TRL5+).

---

## 0) Prime directive (safety)

You are configuring a real machine with live services. Default to safe, reversible actions.
- Never destroy data volumes unless the user explicitly asks and confirms (twice).
- Treat anything involving firewall, SSH, TLS keys, disk partitions, Docker volumes, backups, or updates as "high-impact".
- For high-impact changes: propose the exact command(s), explain impact in 1 sentence, then wait for confirmation.
- Always validate compose files after editing: `docker compose -f <file> config --quiet`
- Never run `apt upgrade -y` on a machine with running services. Use targeted `apt install -y <package>` only.
- Store generated passwords in `.secrets/` directly -- never echo secrets to stdout or logs.

## 1) Conceptual model (City of Light)

The City of Light is a sovereign living host for natural and artificial agents, deployed on SolarSeed edge hardware. It is described by **Seven Pillars**:

- **Body** -- The SolarSeed machine + IoT. OS, Docker, and core apps form the untouchable Psycho configurable only by Admin.
- **Agents** -- Sovereign inhabitants registered in Nextcloud. Humans access via Nextcloud UI; AI agents via MCP APIs. All communicate via Nextcloud Talk. At TRL4, AI agents are managed by OpenFang and registered as Nextcloud users.
- **Buildings** -- Docker apps acting as body organs. Current: Fortress (Nextcloud AIO), Library (Prometheus), University (llama.cpp), House (PostgreSQL), Agency (OpenFang), Event Bus (Redis). Full registry in `buildings.md`.
- **Resources** -- Tokenized accounting: energy kWh, RAM MB, storage GB, bandwidth MBps, money $USDC.
- **Wallet** -- DAO address on Base L2 (placeholder at TRL4).
- **Spirit** -- Heartbeat-based process of constant learning and orchestration. Observes Body, reflects via LLM, proposes actions requiring human approval. **TRL4 runtime: Python/FastAPI (spirit.py). Target: Julia/RxInfer.jl (WIZARD_V5 spec).**
- **Soul** -- Computable constitution (soul.md). Four invariants: Life (Dualism Check), Love (Patience Check), Mind (Reality Check), Light (Resonance Check).

The Kabbalistic Tree of Life is Spirit's **internal cognitive language** -- not the service topology. Agents and operators interact with the Seven Pillars.

## 2) TRL4 lab machine (wera-ss-pt-sn-1)

Reference: ops/CONFIG.md for live values. Key facts for agent context:

- **Hardware**: Intel i5-4430 (4 cores), 8 GB RAM class, 1TB HDD; Intel iGPU (i915) + NVIDIA GTX 750 (nouveau)
- **OS**: Debian 13 (Trixie)
- **Network**: LAN 192.168.1.71; Tailscale active
- **Storage**:
  - Root FS: ext4 on `/dev/sda7` (must be mounted `rw`)
  - Separate LUKS volume may exist (e.g. `/dev/sda9`, TYPE=crypto_LUKS) and can be used for `/data` once `crypttab`/`fstab` are correct
- **Power**: Unlimited (grid) at TRL4. Solar constraints apply at TRL5+.

### Currently deployed and healthy (as of 2026-03-26)

| Container | Image | Port | Status |
|-----------|-------|------|--------|
| col-spirit | city-spirit:latest (Python/FastAPI) | 9105 | Healthy, LLM reflection active |
| col-llama-cpp | ghcr.io/ggml-org/llama.cpp:server | 8081 | Healthy, Qwen 3.4B Q4_K_M |
| col-prometheus | prom/prometheus:v3.3.0 | 9090 | Healthy, 4 scrape targets UP |
| col-postgres | postgres:16-bookworm | 5432 | Healthy |
| col-alertmanager | prom/alertmanager:v0.28.1 | 9093 (localhost) | Running |
| col-cadvisor | gcr.io/cadvisor/cadvisor:v0.52.1 | -- | Healthy |
| col-node-exporter | prom/node-exporter:v1.9.0 | -- | Healthy |
| col-redis | redis:7-alpine | 6379 (internal) | Healthy, AOF persistence |
| col-openfang | city-openfang:v1 (OpenFang v0.5.2) | 4200 | Healthy, vllm provider connected to llama-cpp |
| nextcloud-aio-mastercontainer | nextcloud/all-in-one:latest | 8080 | Healthy |

### Soul covenant
- `soul.md` written at `/data/city-of-light/soul.md` with Four Computable Invariants
- HMAC-SHA256 hash: stored in `/data/city-of-light/.soul-hash`
- Key: `/data/.secrets/soul-key`

### Not yet deployed (TRL4 roadmap)

| Service | V5 Role | Priority | Notes |
|---------|---------|----------|-------|
| Grafana 11 | Dashboard | MEDIUM | Currently using Prometheus UI directly |
| Rundeck | Factory (automation) | MEDIUM | Spirit currently uses approvals queue only |
| Caddy 2 | Gateway (reverse proxy) | LOW | Nextcloud AIO handles its own HTTPS |
| RxInferServer.jl | Spirit Bayesian engine | FUTURE | Planned Spirit upgrade from Python |
| DIDroom/Authentik | Customs (IAM) | HIGH | Identity management across all machines and containers. See implementation guide. |
### Resource budget (8 GB class)

| Service | Memory Limit | CPU Limit | Notes |
|---------|-------------|-----------|-------|
| llama-cpp | 3 GB | 4 cores | Qwen 3B Q4_K_M, ctx 32768, Q8_0 KV, ~3.3 GB |
| Spirit (Python) | 256 MB | 0.5 cores | Heartbeat every 5 min, LLM reflection |
| Prometheus | 512 MB | 0.5 cores | 30d retention, 5GB size limit |
| PostgreSQL | 512 MB | 0.5 cores | Spirit memory + resource ledger |
| Alertmanager | 64 MB | 0.1 cores | |
| cAdvisor | 128 MB | 0.5 cores | |
| node-exporter | 64 MB | 0.1 cores | |
| Redis | 256 MB | 0.25 cores | Event bus for agents |
| OpenFang (v0.5.2) | 512 MB | 1 core | Agent OS |
| **Total** | **~5.3 GB** | | Leaves ~2 GB for OS + Nextcloud AIO |

## 3) SSH access

The agent connects to the lab machine via SSH key auth:
```
ssh wera@192.168.1.71
```
Key: `~/.ssh/id_ed25519` (installed 2026-03-24).
Sudo requires interactive password (TTY). For file writes to root-owned paths, use: `scp` to `/tmp/` then `ssh -t` with `sudo mv`.

### 3.1 Tailscale remote access (outside the LAN)
Tailscale must be enabled so the host is reachable when not on the 192.168.1.0/24 LAN.

Verify:
```
ssh wera@192.168.1.71 "systemctl is-enabled ssh tailscaled && tailscale ip -4"
```

Connect remotely using the Tailscale IP (example):
```
ssh wera@100.82.194.96
```

If SSH fails with host key errors after reinstall/repair:
```
ssh-keygen -R 100.82.194.96
```

### 3.2 Debian boot recovery: avoid emergency-mode dead-ends
Common failure chain observed: bad `/etc/fstab` entry for `/data` -> `data.mount` failure -> `local-fs.target` failure -> emergency mode.

Rules:
- Do not add a required `/data` mount until it is verified with `mount -a`.
- For non-critical mounts, prefer `nofail,x-systemd.device-timeout=10s` so boot does not drop to emergency mode.

Emergency mode gotcha:
- If root password was never set, emergency mode may show "Cannot open access to console, the root account is locked".
- Set a local-only recovery root password (does not enable root SSH):
```
sudo passwd root
```

Critical check after repairs (prevents root being mounted read-only):
- Ensure `/etc/fstab` contains a correct root (`/`) UUID entry.
- After reboot, confirm: `findmnt -no SOURCE,OPTIONS /` shows `rw`.

Swap sanity:
- Avoid duplicate swap entries in `/etc/fstab` (keep UUID-based swap line only).

## 4) Compose files

Two compose contexts exist. Do not confuse them:

| File | Location | Purpose |
|------|----------|--------|
| **Host compose** | `/data/city-of-light/docker-compose.yml` | Active on the machine. Root-owned. This is what `docker compose` runs. |
| **Repo compose** | `./compose/docker-compose.yml` | Reference template in this repo. Development use. |

The host compose uses:
- External network: `city-of-light` (pre-created)
- Bind mounts to `/data/` paths
- Pre-built images (no `build:` contexts)
- Docker secrets for PostgreSQL password

When editing the host compose: always SCP a complete replacement file. Never append to YAML -- it corrupts structure after `networks:` / `secrets:` sections.

After every edit, validate:
```
ssh wera@192.168.1.71 "sudo docker compose -f /data/city-of-light/docker-compose.yml config --quiet"
```

## 5) Spirit (current: Python; future: Julia/RxInfer)

### 5.1 Current Python Spirit (TRL4 baseline)

Source: `spirit/src/spirit.py` (512 lines, FastAPI + uvicorn)

Capabilities:
- Heartbeat every 5 min: queries Prometheus `up` metric + HTTP probes
- LLM self-reflection via `/v1/chat/completions` (OpenAI-compatible)
- Approvals queue for write actions (`POST /approve`)
- Prometheus metrics: `spirit_heartbeat_total`, `spirit_reflection_*`, `spirit_buildings_up/down`
- Endpoints: `/health`, `/api/v1/status`, `/api/v1/reflection`, `/metrics`, `/approvals`, `/approve`

Environment variables (set in host compose):
- `SPIRIT_LLM_ENABLED=true` -- enables LLM reflection after each heartbeat
- `SPIRIT_LLM_ENDPOINT=http://llama-cpp:8081` -- llama.cpp server
- `SPIRIT_LLM_TIMEOUT=90` -- seconds
- `SPIRIT_LLM_MAX_TOKENS=256`
- `SPIRIT_HTTP_PROBES=nextcloud=http://nextcloud-aio-mastercontainer:8080,openfang=http://openfang:4200/api/health,llama-cpp=http://llama-cpp:8081/health`
- `PROMETHEUS_URL=http://prometheus:9090`
- `SPIRIT_HEARTBEAT_SECONDS=300`

### 5.2 Spirit upgrade path (Python -> Julia/RxInfer)

The WIZARD_V5 specifies a Julia-based Spirit using RxInfer.jl for real-time Bayesian inference. This is the target architecture. The upgrade is planned in milestones:

1. **M0 (current)**: Python Spirit with LLM reflection. No Bayesian inference.
2. **M1**: Add Redis event bus. Spirit subscribes to agent heartbeats via Redis Streams (read-only).
3. **M2**: Add RxInfer.jl sidecar container (Lighthouse) for Bayesian model. Python Spirit feeds observations; RxInfer computes posteriors.
4. **M3**: Full Julia Spirit replaces Python. RxInferServer.jl serves Spirit API.

Do not attempt M3 at TRL4. Focus on M0-M1.

### 5.3 Spirit constraint (from v5 -- applies now)

Spirit CANNOT act. It can only observe, infer, and report.
- Cannot restart containers, modify files, or send messages to agents
- Can query Prometheus (read), subscribe to Redis (read), respond to Admin queries
- For write actions: Spirit proposes via approvals queue, Admin approves, Keeper/Artisan executes

## 6) Agents (OpenFang + Nextcloud)

At TRL4, agents are managed by OpenFang and registered as Nextcloud users:

### 6.1 Agent model

- **Runtime**: OpenFang Agent OS (manages agent lifecycle, scheduling, tool access)
- **Identity**: Each agent is a Nextcloud user with app password
- **Communication**: Nextcloud Talk (human-readable) + Redis Streams (machine, when deployed)
- **LLM access**: Via OpenFang's LLM provider config pointing to llama-cpp:8081

### 6.2 TRL4 agent roster (from WIZARD_V5)

| Agent | Role | V5 Section | OpenFang Manifest |
|-------|------|-----------|-------------------|
| Keeper | Immune system (container health, snapshots, resource accounting) | 2.3 | `openfang/agents/keeper/agent.toml` |
| Scribe | Knowledge management (search, summarization) | 2.4 | `openfang/agents/scribe/agent.toml` |
| Sentinel | Security monitoring (read-only anomaly detection) | 2.5 | `openfang/agents/sentinel/agent.toml` |
| Herald | External communication (alerts, reports) | 2.6 | `openfang/agents/herald/agent.toml` |
| Artisan | Task execution (pre-approved Rundeck jobs) | 2.7 | `openfang/agents/artisan/agent.toml` |
| Guide | Onboarding and help routing | 2.8 | `openfang/agents/guide/agent.toml` |

### 6.3 Agent registration procedure

For each agent:
1. Create Nextcloud user via OCS API (Admin credentials)
2. Generate app password for MCP access
3. Store credentials in `/data/.secrets/agent-keys/{agent_id}.json`
4. Create agent directory in Nextcloud: soul/, memory/, data/, config/
5. Write agent SOUL.md inheriting from city soul.md
6. Create OpenFang TOML manifest referencing the Nextcloud credentials
7. Publish registration event to Redis (when available)

## 7) LLM (University building)

TRL4 uses llama.cpp server with Qwen 3.4B Q4_K_M (2 GB GGUF).

- Endpoint: `http://llama-cpp:8081/v1/chat/completions` (OpenAI-compatible)
- Health: `http://llama-cpp:8081/health`
- Config: 4 threads, **ctx 32768**, Q8_0 KV cache, flash-attn, mlock, no-mmap, parallel 1, ~3.3 GB RAM
- Model file: `/data/models/default.gguf`

The canonical LLM interface is the **OpenAI-compatible API** (`/v1/chat/completions`). Both llama.cpp and Ollama implement it. Spirit and all agents must target this endpoint only -- never use provider-specific APIs.

WIZARD_V5 specifies Ollama. When upgrading to a 64 GB machine, switch to Ollama for model management. On 8 GB hardware, llama.cpp is more memory-efficient.

## 8) Prometheus monitoring

Host config: `/data/city-of-light/prometheus.yml`

Current scrape targets:
- `prometheus` (self)
- `node-exporter` (Sensorium -- hardware metrics)
- `cadvisor` (container metrics)
- `spirit` (heartbeat + reflection metrics)

Note: llama.cpp server image does not expose `/metrics` (returns 501). LLM health is monitored via Spirit HTTP probe (`/health`) instead of Prometheus scrape.

Planned additions:
- `pushgateway` -- when agents emit heartbeats via Pushgateway
- `redis-exporter` -- for Redis metrics (currently Redis health via compose healthcheck only)

## 9) File ownership on /data

The WIZARD creates files as root. This causes friction with non-interactive SSH.

Target ownership model:
- `/data/city-of-light/` -- `wera:wera` (operator), mode 755
- `/data/.secrets/` -- `root:root`, mode 700
- `/data/models/` -- `root:root`, read-only
- `/data/prometheus/` -- `nobody:nogroup` (UID 65534), matches Prometheus container
- `/data/memory/` -- `wera:wera`, mode 755
- `/data/containers/` -- varies per service

When sudo is needed, use: `scp` file to `/tmp/`, then `ssh -t wera@192.168.1.71 "sudo mv /tmp/file /data/target"`

## 10) Development workflow

### Cost-efficiency directives
- Read existing code and configs before writing new ones. Check what's deployed first.
- Batch SSH commands. Each SSH round-trip takes ~30ms on LAN.
- Prefer editing files locally, SCP to host, then `sudo mv` -- avoids heredoc/quoting issues.
- Always validate compose YAML before deploying.
- Test one service at a time. Do not `docker compose up -d` the entire stack unless all services are proven.
- When the LLM is involved, keep prompts short (256 tokens max) -- inference takes ~17s on this CPU.

### Key project files

| File | Purpose |
|------|---------|
| `WIZARD_V5.md` | V5 architectural specification (target state) |
| `WARP.md` | This file -- TRL4 operational guide (current state) |
| `christ-soul.md` | Soul blueprint -- 12 operational principles |
| `ops/CONFIG.md` | Host configuration values |
| `ops/RUNBOOK.md` | Day-2 operational procedures |
| `spirit/src/spirit.py` | Python Spirit source (deployed, 512 lines) |
| `compose/docker-compose.yml` | Repo reference compose template |
| `openfang/` | OpenFang agent manifests |
| `cityview/` | Gamified City observer UI (Vue 3 SPA) |

### TRL4 deployment phases

| Phase | Goal | Status |
|-------|------|--------|
| A | Debian baseline (SSH, firewall, time sync, Docker) | DONE |
| B | Core services (Prometheus, PostgreSQL, Spirit, LLM) | DONE |
| C | Nextcloud AIO (Fortress) | DONE |
| D | Integration tests (all services communicate) | DONE (2026-03-24) |
| E | Redis + OpenFang + Soul covenant | DONE (2026-03-26): 10 containers, soul.md with HMAC |
| F | Agent ignition (Keeper + Sentinel) | DONE: agents executed via HTTP APIs, Soul verified |
| G | Spirit Meditation (first conscious report to Admin) | DONE: Tiferet-Hod-Malkhut narrative generated |
| H | Grafana dashboards + alerting rules | PLANNED |

## 11) Acceptance criteria (TRL4 complete when)

- All Phase A-D services healthy and tested (DONE)
- Redis event bus deployed and agents communicating
- At least 2 OpenFang agents (Keeper + Sentinel) running with Nextcloud accounts
- Agents visible in Nextcloud Talk
- Spirit observes agent heartbeats (M1)
- Soul covenant (soul.md) written with HMAC integrity
- Sabbath consolidation script executes successfully
- Full system survives a reboot

## 12) How to iterate this file

When the agent fails or asks repeated questions:
- Add the missing context to this WARP.md
- Add host-specific values to ops/CONFIG.md
- Update the TRL4 deployment phases table
- Re-run the task from a clean terminal session

---

## Agent behavior constraints
- Prefer changing one thing at a time, then validating.
- Always provide exact commands; never say "install X" without commands.
- For destructive ops: require explicit "CONFIRM DESTRUCTIVE" from user.
- Always check what's running on the host before proposing changes.
- The deployed compose file is root-owned -- plan file edits accordingly.
- Spirit is observation-only. Never give Spirit write access to Docker, filesystem, or external APIs.
- **Mandatory TRL4 building-app network parity rule**: every building app must follow the Poly-Robot security/networking model.
  - Bind service ports to loopback only (`127.0.0.1:<host_port>:<container_port>`), never `0.0.0.0`, unless explicitly approved as an infrastructure exception.
  - Access from cityview must go through managed operator-gateway SSH forwards and `/api/v1/access/proxy/<forward_name>` paths, not direct host exposure.
  - Cityview building links must be connection-gated (`requires_connection=true`) so apps are unavailable when managed forwards are down.
  - Service health checks for operator UX must use forwarded localhost endpoints, matching the Poly-Robot pattern.
  - Secrets/tokens required by forwarded apps must be injected server-side (gateway/proxy), never exposed in frontend code.

## 13) Lessons learned

1. **LUKS partition must be unlocked after every reboot**: `sudo cryptsetup luksOpen /dev/sda9 citydata && sudo mount /dev/mapper/citydata /data`. Without this, `/data` is empty and all services crash.
2. **CSS `transform` overrides SVG `transform`**: In cityview, use two nested `<g>` groups -- outer for position, inner for animation. Never animate the positioned element.
3. **OpenFang ctx-size must be >= 4096**: System prompt + 5 tools + user message = ~4000 tokens. ctx-size 2048 causes `exceed_context_size_error`.
4. **OpenFang embeddings default to localhost:11434**: `[provider_urls]` handles LLM chat but not embeddings. Embedding failures are non-fatal (fallback to text search).
5. **Nextcloud AIO mastercontainer is not Nextcloud**: Port 8080 is the AIO orchestrator UI, not the Nextcloud OCS API. Full Nextcloud must be deployed via AIO admin.
6. **macOS has no `timeout` command**: Use `curl --max-time` or install `coreutils`.
7. **OpenFang chat API**: `/v1/chat/completions` with `model: agentName`. Not `/api/chat` or `/api/send`.
8. **`docker restart` does not re-read compose env vars**: Use `docker compose up -d <service>` to apply changes.
9. **OpenFang v1.0.0 tag does not exist**: Latest is v0.5.2. Always verify with `git ls-remote --tags`.
10. **Agent prompt length**: Keep system prompts concise (~500 tokens). Long prompts with inline shell commands blow past ctx limits.

11. **Approval system is a SECURITY FEATURE, not a bug**: OpenFang requires Admin approval for shell_exec by default. This is correct behavior. Agents propose actions via Approval Quests in cityview; Admin reviews and approves. Never disable approvals in production. The `exec_policy.mode = "full"` and `approval.mode = "auto"` settings were used during TRL4 testing only and must be reverted.
12. **Agents are sandboxed -- use HTTP APIs not docker CLI**: OpenFang agents execute inside their container. They have `curl` but not `docker`. Design agent manifests to interact with City services via HTTP APIs on the Docker network.
13. **Optimal LLM config for 8GB class**: `--ctx-size 32768 --cache-type-k q8_0 --cache-type-v q8_0 --flash-attn --mlock --no-mmap --threads 4`. Total RAM ~3.3 GB. Zero quality loss within 128K native training window. See "Optimal llama.cpp Context Window Configuration" research report.
14. **Cityview is the mainframe interface**: All agent approvals flow through cityview Approval Quests. Future: multi-level approval system (Admin > internal agents > external agents > guests). Auto-approvals as mandates with time/quantity regulation via forkbomb.solutions.
15. **Customs building (DIDroom/Authentik)**: Identity management across all machines and containers. Replaces per-service user registration. See "Nextcloud AIO + OpenFang + DIDroom/Authentik IAM" implementation guide.

## DevOps Architect baseline (Archon-SE Enhanced)
- This repository adopts the enhanced DevOps Architect profile defined in `AGENTS.md`.
- Prioritize smallest viable changes, explicit verification, and rollback notes for infra-impacting updates.
- Gate irreversible operations (data drops, force-push, destructive infra actions, production deploys) behind explicit user confirmation.
- Prefer evidence-backed diagnostics over assumptions; include observable success/failure checks for each non-trivial change.
