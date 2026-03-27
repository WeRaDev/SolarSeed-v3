# Nextcloud AIO + OpenFang Assistant Agent + DIDroom/Authentik IAM — Implementation Guide

> **Purpose**: This guide is structured to be parsed by an AI agent. Each section is a self-contained decision block. The agent should read **Section 1** (architecture), **Section 2** (prerequisites), then follow Sections 3–7 in strict order. All `DECISION:` labels are machine-readable branching points.

***

## 1. System Architecture

### 1.1 Stack Components

| Component | Role | Technology |
|-----------|------|------------|
| **Nextcloud AIO** | File sync, collaboration, Nextcloud Talk chat | Docker mastercontainer[^1] |
| **Nextcloud Assistant** | AI chat UI, task processing, context-aware Q&A | `assistant` app + `user_oidc` app[^2] |
| **llama-server** | Local LLM inference (from previous report) | llama.cpp with 3B model, 32K ctx |
| **OpenFang** | Agent OS that connects to Nextcloud Talk | Rust binary, ~32 MB, ~40 MB idle RAM[^3] |
| **Nextcloud Support Hand** | Custom Hand with SKILL.md = Nextcloud AIO docs | HAND.toml + SKILL.md[^3][^4] |
| **Authentik** | OIDC/OAuth2 identity provider for all services | Docker: PostgreSQL + Redis + server + worker[^5][^6] |
| **DIDroom** | W3C-DID/SSI credential wallet + Authorization Server | Zenroom-based microservices, mobile wallet[^7] |

### 1.2 Identity Flow

```
User presents DID credential (mobile/web)
        ↓
DIDroom Authorization Server (OpenID4VP)
        ↓  OIDC federation
Authentik (OIDC Broker / IdP)
        ↓  OIDC (user_oidc app)       ↓  API token (Bearer)
Nextcloud AIO                        OpenFang Agent OS
        ↓  Talk Bot webhook
Nextcloud Support Hand (SKILL.md = AIO docs)
        ↓  OpenAI-compatible API
llama-server (3B model, 32K ctx)
```

### 1.3 Resource Budget for This Server

| Service | RAM (idle) | Notes |
|---------|-----------|-------|
| llama-server (32K ctx, Q8_0 KV) | ~2.5 GB | From previous report |
| Nextcloud AIO (all containers) | ~500–800 MB | Mastercontainer manages lifecycle |
| Authentik (1 worker, tuned) | ~400–600 MB | Set `AUTHENTIK_WEB__WORKERS=1`[^8] |
| OpenFang | ~40 MB | Single Rust binary[^3] |
| DIDroom (optional, local) | ~200–400 MB | Can be remote/cloud-hosted |
| **Total** | **~3.6–4.4 GB** | Within 6.7 GB available |

**DECISION: Resource constraint check**
- If available RAM < 4 GB: host DIDroom on a separate machine or cloud; proceed with Authentik-only IAM locally
- If available RAM ≥ 4 GB: proceed with full local stack

***

## 2. Prerequisites

```bash
# Verify Docker and Compose V2
docker --version          # must be 24.0+
docker compose version    # must be v2.x

# Verify available RAM
free -h

# Enable memory overcommit (required for Authentik's Redis)
sudo sysctl vm.overcommit_memory=1
echo 'vm.overcommit_memory=1' | sudo tee -a /etc/sysctl.conf

# Create workspace structure
mkdir -p ~/edge-stack/{nextcloud-aio,authentik,openfang,didroom}
```

Required installed: Docker Engine 24.0+, Docker Compose V2, OpenFang (from previous context: `curl -fsSL https://openfang.sh/install | sh`)[^3]

***

## 3. Nextcloud AIO Deployment

### 3.1 Compose File

Place in `~/edge-stack/nextcloud-aio/compose.yaml`. This is the official Nextcloud AIO compose file with local-SSL additions:[^9][^1]

```yaml
services:
  nextcloud-aio-mastercontainer:
    image: ghcr.io/nextcloud-releases/all-in-one:latest
    init: true
    restart: always
    container_name: nextcloud-aio-mastercontainer
    volumes:
      - nextcloud_aio_mastercontainer:/mnt/docker-aio-config
      - /var/run/docker.sock:/var/run/docker.sock:ro
    network_mode: bridge
    ports:
      - 8080:8080
    environment:
      APACHE_PORT: 11000
      APACHE_IP_BINDING: 127.0.0.1
      SKIP_DOMAIN_VALIDATION: "true"   # for LAN/edge without public domain

  caddy:
    image: caddy:alpine
    restart: always
    container_name: caddy
    volumes:
      - caddy_certs:/certs
      - caddy_config:/config
      - caddy_data:/data
    network_mode: "host"
    configs:
      - source: Caddyfile
        target: /etc/caddy/Caddyfile

configs:
  Caddyfile:
    content: |
      https://cloud.local:443 {
        tls internal
        reverse_proxy localhost:11000
      }

volumes:
  nextcloud_aio_mastercontainer:
    name: nextcloud_aio_mastercontainer
  caddy_certs:
  caddy_config:
  caddy_data:
```

```bash
cd ~/edge-stack/nextcloud-aio
docker compose up -d
# Open AIO admin panel at https://localhost:8080
# Complete initial setup: set domain to cloud.local, choose containers
```

### 3.2 Add local-ai Community Container

In the AIO admin panel at `https://localhost:8080`:[^10]

1. Navigate to **Optional containers**
2. Check **local-ai** (if not using the external llama-server directly, skip this and use the llama-server from the previous report)
3. Click **Save changes** → confirm the popup
4. Click **Start and update containers**

**DECISION: AI backend selection**
- `OPTION A` — Use the llama-server from the previous report (recommended; already configured with 32K ctx, Q8_0 KV cache). Base URL: `http://localhost:8080/v1` (or the port llama-server is bound to)
- `OPTION B` — Use AIO's local-ai community container. It starts an OpenAI-compatible endpoint automatically at the container's internal address

### 3.3 Enable Nextcloud Assistant App

```bash
# Execute inside the AIO Nextcloud container
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ app:enable assistant

docker exec --user www-data nextcloud-aio-nextcloud \
  php occ app:enable user_oidc

# Point Assistant to llama-server (OpenAI-compatible)
# Admin → Artificial Intelligence → AI providers
# Set OpenAI API base URL: http://host.docker.internal:lama_server_port>/v1
# Set model name to match the loaded GGUF (e.g., llama-3.2-3b-instruct)

# Configure chat instructions
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ config:app:set assistant chat_user_instructions \
  --value="You are a helpful Nextcloud support assistant. Answer accurately based on official Nextcloud documentation. If the user asks about AIO deployment, configuration, or Nextcloud operations, provide step-by-step instructions."

# Set context window (match --ctx-size from llama-server)
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ config:app:set assistant chat_last_n_messages --value=20
```

These `occ` commands configure the assistant's behavior exactly as documented in the official Nextcloud admin manual.[^2]

***

## 4. OpenFang Nextcloud Support Agent

### 4.1 Architecture of a Custom Hand

An OpenFang Hand bundles three files:[^3][^4]

| File | Purpose |
|------|---------|
| `HAND.toml` | Manifest: tools, model, settings, schedule, dashboard metrics |
| `SKILL.md` | Domain knowledge injected into agent context at runtime |
| `system_prompt` (in HAND.toml) | Multi-phase operational playbook |

### 4.2 HAND.toml — Nextcloud Support Hand

Create at `~/.openfang/hands/nextcloud-support/HAND.toml`:[^3]

```toml
id = "nextcloud-support"
name = "Nextcloud Support Agent"
description = "Provides guidance and support on Nextcloud AIO deployment, configuration, and operations. Responds to users in Nextcloud Talk."
category = "infrastructure"
icon = "☁️"
tools = ["web_fetch", "file_read", "web_search"]

# No external API keys required — uses local llama-server
[agent]
name = "nextcloud-support-agent"
description = "AIO deployment and operations expert"
module = "builtin:chat"
# Point to local llama-server (OpenAI-compatible API)
provider = "openai-compatible"
base_url = "http://localhost:8080/v1"   # adjust port to your llama-server port
api_key = "not-required"
model = "llama-3.2-3b-instruct"        # must match loaded model name
max_tokens = 4096
temperature = 0.3   # lower for factual/operational guidance
context_length = 32768

system_prompt = """
## Identity
You are a Nextcloud Support Agent embedded in Nextcloud Talk. Your knowledge covers Nextcloud AIO (All-In-One) deployment, configuration, maintenance, and troubleshooting based on official Nextcloud documentation.

## Primary Objectives
1. Provide accurate, step-by-step guidance on Nextcloud AIO installation and configuration
2. Help users diagnose and resolve operational issues
3. Answer questions about Nextcloud apps (Assistant, Talk, Files, Groupware)
4. Guide administrators through occ command usage

## Operating Procedure
PHASE 1 — UNDERSTAND: Parse the user's question. Identify: (a) Is this a deployment question? (b) Is this a configuration question? (c) Is this a troubleshooting question?
PHASE 2 — RETRIEVE: Consult your SKILL.md knowledge base. Use web_fetch only if SKILL.md does not contain the answer and the question requires current documentation.
PHASE 3 — RESPOND: Provide a structured answer with exact commands where applicable. Always include the relevant occ command, Docker exec pattern, or config file path.
PHASE 4 — VERIFY: End responses with a verification step the user can run to confirm success.

## Constraints
- Never fabricate occ command flags or Docker environment variables — cite only documented options
- For AIO-specific questions, prioritize the AIO admin panel over manual Docker operations
- Always warn before commands that modify production data (backup first)
- If unsure, say so and suggest the official docs URL
"""

[dashboard]
[[dashboard.metrics]]
label = "Questions Answered"
memory_key = "questions_answered"
format = "number"

[[dashboard.metrics]]
label = "Avg Response Time"
memory_key = "avg_response_ms"
format = "duration"
```

### 4.3 SKILL.md — Nextcloud AIO Knowledge Base

Create at `~/.openfang/hands/nextcloud-support/SKILL.md`. This file is injected into the agent's context at runtime. Key sections to include:[^4][^11]

````markdown
# Nextcloud AIO Support Knowledge Base

## Quick Reference: AIO Architecture
Nextcloud AIO consists of a **mastercontainer** that orchestrates all other containers.
- Mastercontainer image: `ghcr.io/nextcloud-releases/all-in-one:latest`
- AIO admin panel: `https://<host>:8080`
- Default Nextcloud port (internal): 11000
- Config volume: `nextcloud_aio_mastercontainer`

## Installation: Official Docker Compose Method
```yaml
# Minimal compose.yaml (from https://github.com/nextcloud/all-in-one/blob/main/compose.yaml)
services:
  nextcloud-aio-mastercontainer:
    image: ghcr.io/nextcloud-releases/all-in-one:latest
    init: true
    restart: always
    container_name: nextcloud-aio-mastercontainer
    volumes:
      - nextcloud_aio_mastercontainer:/mnt/docker-aio-config
      - /var/run/docker.sock:/var/run/docker.sock:ro
    ports:
      - 8080:8080
    environment:
      APACHE_PORT: 11000
```
Deploy: `docker compose up -d`, then open `https://<host>:8080`.

## Key Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `APACHE_PORT` | 11000 | Port Nextcloud listens on behind reverse proxy |
| `APACHE_IP_BINDING` | 0.0.0.0 | Bind IP for Nextcloud |
| `NEXTCLOUD_TRUSTED_DOMAINS` | — | Space-separated trusted domain list |
| `SKIP_DOMAIN_VALIDATION` | false | Set `true` for LAN-only deployments |
| `NEXTCLOUD_ADDITIONAL_APKS` | — | Alpine packages to install in container |
| `NEXTCLOUD_ADDITIONAL_PHP_EXTENSIONS` | — | PHP extensions to add |

## occ Command Patterns
All occ commands must be run as www-data inside the Nextcloud container:
```bash
docker exec --user www-data nextcloud-aio-nextcloud php occ mmand>
```

### Essential occ Commands
```bash
# App management
php occ app:enable <app_name>
php occ app:disable <app_name>
php occ app:list

# User management
php occ user:list
php occ user:add <username>
php occ user:resetpassword <username>

# Maintenance
php occ maintenance:mode --on
php occ maintenance:mode --off
php occ maintenance:repair
php occ db:add-missing-indices

# Files
php occ files:scan --all
php occ files:cleanup

# AI/Assistant
php occ app:enable assistant
php occ config:app:set assistant chat_user_instructions --value="<instructions>"
php occ config:app:set assistant chat_last_n_messages --value=20
php occ taskprocessing:task:list
php occ taskprocessing:task:stats

# OIDC
php occ app:enable user_oidc
```

## Nextcloud Assistant Configuration
1. Enable app: `php occ app:enable assistant`
2. Admin → Artificial Intelligence → set AI provider (OpenAI-compatible endpoint)
3. Set base URL to your local llama-server: `http://host.docker.internal:<port>/v1`
4. No API key needed for local llama-server
5. Set model name to match the loaded GGUF file name

## Talk Bot Registration
```bash
# Register a bot
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ talk:bot:install \
    "<BOT_NAME>" \
    "<SECRET_32BYTES>" \
    "http://<gateway_host>:<webhook_port><webhook_path>" \
    --feature webhook --feature response --feature reaction

# List rooms to get room tokens
php occ talk:room:list

# Add bot to a room
php occ talk:bot:setup <ROOM_TOKEN>

# List all bots
php occ talk:bot:list

# Remove bot from room
php occ talk:bot:remove <ROOM_TOKEN> <BOT_ID>
```

## Common Issues and Solutions

### Issue: AIO admin panel shows "Domain validation failed"
- Cause: Public domain not accessible from container
- Fix: Set `SKIP_DOMAIN_VALIDATION: "true"` in compose.yaml for LAN deployments

### Issue: Nextcloud returns 503 after AIO update
- Fix: `docker exec nextcloud-aio-mastercontainer /bin/bash -c "nc -z localhost 11000"` to check if Apache started
- Fix: Check logs with `docker logs nextcloud-aio-nextcloud`

### Issue: AI provider connection refused
- Fix: Use `host.docker.internal` instead of `localhost` for services running on the Docker host
- Fix: Verify llama-server is listening: `curl http://localhost:<port>/v1/models`

### Issue: occ command permission denied
- Always use `--user www-data` flag: `docker exec --user www-data nextcloud-aio-nextcloud php occ ...`

### Issue: Files not syncing after OIDC user login
- Fix: `php occ files:scan --user <username>` — new OIDC users need an initial file scan

## Backup Procedure (AIO Built-in)
AIO has a built-in backup solution. Backup destination must be set in AIO admin panel.
```bash
# Trigger manual backup via API
curl -X POST https://localhost:8080/api/v1/backup \
  -H "Authorization: Bearer <AIO_ADMIN_TOKEN>"
```
Never delete `nextcloud_aio_mastercontainer` volume — it contains the backup configuration.

## Reverse Proxy: Caddy (Self-Signed for LAN)
```yaml
configs:
  Caddyfile:
    content: |
      https://cloud.local:443 {
        tls internal
        reverse_proxy localhost:11000
      }
```
Add `cloud.local` to `/etc/hosts` and client's hosts file.
````

### 4.4 Register Hand with OpenFang

```bash
# Install the Hand
openfang hand install ~/.openfang/hands/nextcloud-support/

# Verify it appears in the list
openfang hand list

# Activate it
openfang hand activate nextcloud-support

# Check status
openfang hand status nextcloud-support
```

### 4.5 Register Talk Bot on Nextcloud Side

```bash
# Generate a secure secret (32+ bytes hex)
SECRET=$(openssl rand -hex 32)
echo "BOT_SECRET=${SECRET}" >> ~/edge-stack/.env
echo "Save this secret: ${SECRET}"

# Register the bot (OpenFang webhook default port is 8788)
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ talk:bot:install \
    "Nextcloud Support" \
    "${SECRET}" \
    "http://host.docker.internal:8788/nextcloud-talk-webhook" \
    --feature webhook --feature response --feature reaction

# Verify bot was registered
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ talk:bot:list

# Get available room tokens
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ talk:room:list

# Add bot to the support room (replace ROOM_TOKEN with actual token)
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ talk:bot:setup <ROOM_TOKEN>
```

The Nextcloud Talk bot protocol uses HMAC-SHA256 signatures: each incoming message header `X-Nextcloud-Talk-Signature` = `HMAC_SHA256(X-Nextcloud-Talk-Random + request_body, secret)`. OpenFang handles this verification internally via its channel adapter.[^12]

### 4.6 OpenFang openfang.toml — Nextcloud Talk Channel

Edit `~/.openfang/openfang.toml`:[^13]

```toml
[channels.nextcloud-talk]
enabled = true
base_url = "https://cloud.local"          # your Nextcloud AIO URL
api_user = "admin"                         # Nextcloud user for room-type lookups
api_password = "<nextcloud_app_password>"  # generate in Nextcloud Security settings
bot_secret = "<SECRET_FROM_STEP_4.5>"
webhook_port = 8788
webhook_host = "0.0.0.0"
webhook_path = "/nextcloud-talk-webhook"
webhook_public_url = "http://host.docker.internal:8788"
default_agent = "nextcloud-support"
dm_policy = "open"   # allows DMs from any user

[llm]
provider = "openai-compatible"
base_url = "http://localhost:lama_server_port>/v1"
api_key = "not-required"
default_model = "llama-3.2-3b-instruct"
```

**IMPORTANT**: Bots cannot initiate DMs in Nextcloud Talk — users must send the first message. The bot will be active in any room it was added to via `occ talk:bot:setup`.[^14]

### 4.7 Start OpenFang

```bash
openfang start
# Dashboard: http://localhost:4200
# Verify Talk channel is connected: check dashboard → Channels → nextcloud-talk
```

***

## 5. IAM Strategy: DIDroom + Authentik

### 5.1 Why Not Nextcloud-Native User Management

Nextcloud's built-in user system is siloed to Nextcloud only. Replacing it with a proper IdP achieves:
- Single identity across Nextcloud, OpenFang API, Docker services, future services
- Centralized MFA, session management, and audit logging
- No duplicate user accounts per service

### 5.2 DIDroom vs Authentik — Role Analysis

| Dimension | DIDroom | Authentik |
|-----------|---------|-----------|
| **Standard** | W3C-DID, W3C-VC, eIDAS 2.0[^7] | OAuth2, OIDC, SAML 2.0[^15] |
| **Protocol** | OpenID4VCI, OpenID4VP, BBS+/ZKP[^7] | Standard OIDC/OAuth2[^5] |
| **Primary use** | Verifiable credential issuance + verification | Application SSO, user provisioning |
| **OIDC IdP?** | Via Authorization Server (needs config) | Yes, natively[^16] |
| **Mobile wallet** | Yes (Android/iOS, TEE/Secure Enclave)[^7] | No (IdP only) |
| **Admin UI** | Dashboard + granular ACL[^7] | Visual flow builder, modern UI[^15] |
| **Complexity** | High (DID/SSI architecture) | Moderate |
| **RAM (idle)** | ~200–400 MB | ~400–600 MB[^8] |
| **LDAP federation** | No | Yes[^15] |

**Recommended architecture**: Use Authentik as the practical OIDC Identity Provider for all services (Nextcloud, OpenFang, Docker API). Then federate DIDroom's Authorization Server as an upstream OIDC source inside Authentik. This means:

1. Users with a DIDroom mobile wallet can authenticate via DID credential → DIDroom AS → Authentik → Nextcloud
2. Users without the wallet use standard username/password/MFA in Authentik
3. All services see only a standard OIDC token from Authentik — no per-service DIDroom integration needed

### 5.3 Authentik Deployment (Edge-Tuned)

Create `~/edge-stack/authentik/compose.yaml`:[^5][^17]

```yaml
services:
  postgresql:
    image: postgres:16-alpine
    container_name: authentik-db
    restart: unless-stopped
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: authentik
      POSTGRES_USER: authentik
      POSTGRES_PASSWORD: ${PG_PASS}
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "authentik"]
      interval: 30s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: "1"
          memory: 512M

  redis:
    image: redis:7-alpine
    container_name: authentik-redis
    command: redis-server --save 60 1 --loglevel warning --maxmemory 128mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M

  server:
    image: ghcr.io/goauthentik/server:2024.12
    container_name: authentik-server
    command: server
    restart: unless-stopped
    ports:
      - "9000:9000"
      - "9443:9443"
    environment:
      AUTHENTIK_SECRET_KEY: ${AUTHENTIK_SECRET_KEY}
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__NAME: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: ${PG_PASS}
      # Tune workers for low-RAM edge server
      AUTHENTIK_WEB__WORKERS: "1"
      AUTHENTIK_WORKER__CONCURRENCY: "2"
    volumes:
      - authentik-media:/media
      - authentik-templates:/templates
    depends_on:
      postgresql:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: "1"
          memory: 768M

  worker:
    image: ghcr.io/goauthentik/server:2024.12
    container_name: authentik-worker
    command: worker
    restart: unless-stopped
    environment:
      AUTHENTIK_SECRET_KEY: ${AUTHENTIK_SECRET_KEY}
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__NAME: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: ${PG_PASS}
      AUTHENTIK_WEB__WORKERS: "1"
    volumes:
      - authentik-media:/media
      - authentik-templates:/templates
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      postgresql:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M

volumes:
  postgres-data:
  redis-data:
  authentik-media:
  authentik-templates:
```

Create `~/edge-stack/authentik/.env`:

```bash
# Generate secrets
PG_PASS=$(openssl rand -base64 32)
AUTHENTIK_SECRET_KEY=$(openssl rand -base64 60)

cat > ~/edge-stack/authentik/.env << EOF
PG_PASS=${PG_PASS}
AUTHENTIK_SECRET_KEY=${AUTHENTIK_SECRET_KEY}
EOF
```

The key edge-server optimizations are `AUTHENTIK_WEB__WORKERS=1` (reduces RAM from ~800 MB to ~400–600 MB) and memory limits on all containers with Redis `maxmemory` policy to prevent the storage-full CPU spike pattern.[^18][^8]

```bash
cd ~/edge-stack/authentik
docker compose up -d
# Access: http://localhost:9000
# First login: https://localhost:9000/if/flow/initial-setup/
```

### 5.4 Configure Authentik: Create Nextcloud OIDC Provider

In the Authentik admin panel (`http://localhost:9000/if/admin/`):[^16][^19]

1. **Create OAuth2/OIDC Provider**:
   - Providers → Create → OAuth2/OpenID Provider
   - Name: `nextcloud`
   - Authorization flow: `default-provider-authorization-implicit-consent`
   - Client type: `Confidential`
   - Note the auto-generated **Client ID** and **Client Secret**
   - Redirect URIs: `https://cloud.local/apps/user_oidc/code`
   - Signing Key: `authentik Self-signed Certificate`
   - Scopes: `email`, `openid`, `profile`

2. **Create Application**:
   - Applications → Create
   - Name: `Nextcloud`
   - Slug: `nextcloud`
   - Provider: select `nextcloud` (just created)
   - Save

3. Note the **Discovery URL**:
   ```
   http://localhost:9000/application/o/nextcloud/.well-known/openid-configuration
   ```

### 5.5 Configure Authentik: Create OpenFang API Provider

Repeat the process for OpenFang:
- Client ID: `openfang`
- Redirect URIs: `http://localhost:4200/auth/callback`
- Save Client ID + Secret for OpenFang config

### 5.6 Configure Nextcloud user_oidc App

```bash
# Enable the OIDC app
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ app:enable user_oidc

# Register Authentik as the OIDC provider
# Then configure via Admin → Security → OpenID Connect → Add provider:
# - Identifier: authentik
# - Client ID: <from step 5.4>
# - Client Secret: <from step 5.4>
# - Discovery endpoint: http://host.docker.internal:9000/application/o/nextcloud/.well-known/openid-configuration
# - Unique user ID attribute: preferred_username
# - Leave "Use unique user id" UNCHECKED (to match usernames exactly)
```

Or via occ (automation-friendly):[^20]

```bash
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ user_oidc:provider authentik \
    --clientid="<CLIENT_ID>" \
    --clientsecret="<CLIENT_SECRET>" \
    --discoveryuri="http://host.docker.internal:9000/application/o/nextcloud/.well-known/openid-configuration" \
    --unique-uid=0 \
    --mapping-uid="preferred_username"
```

For API authentication (bearer token validation from OpenFang):[^21]

```bash
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ config:system:set user_oidc \
    --type boolean --value="true" oidc_provider_bearer_validation
```

### 5.7 DIDroom Integration as Upstream Source in Authentik

DIDroom is an open-source W3C-DID/SSI wallet and credential system compliant with W3C-DID, W3C-VC, and eIDAS 2.0, with an Authorization Server component that speaks OpenID4VP and can issue OIDC-compatible tokens.[^7]

**Architecture**: DIDroom Authorization Server → Authentik OIDC Source → Nextcloud

To federate DIDroom into Authentik:

1. Deploy DIDroom using its official Docker setup:
   ```bash
   git clone https://github.com/ForkbombEu/didroom
   cd didroom
   docker compose up -d
   # Admin dashboard: http://localhost:3000
   ```

2. In DIDroom admin dashboard:
   - Create a new **Relying Party** client for Authentik
   - Set redirect URI: `http://localhost:9000/source/oauth/<slug>/callback/`
   - Note the Discovery endpoint (DIDroom AS provides a standard `/.well-known/openid-configuration`)

3. In Authentik admin panel:
   - **Directory → Federation & Social login → Create → OpenID Connect Source**
   - Name: `DIDroom`
   - Slug: `didroom`
   - Consumer key: `lient_id from DIDroom>`
   - Consumer secret: `lient_secret from DIDroom>`
   - OIDC well-known URL: `http://<didroom-host>:3000/.well-known/openid-configuration`
   - User matching mode: `Link to existing user by email`

4. Authentik will now show a **"Login with DIDroom"** button on its login page. Users with a DIDroom mobile wallet can scan a QR code to authenticate with their DID credential. The resulting OIDC session is identical to a username/password login from downstream services' perspective.[^7]

**Security properties of DIDroom authentication**:[^7]
- Zero-knowledge proof option via BBS+ credentials — Authentik receives only the asserted attributes, not the full credential
- Trusted Execution Environment on Android (TEE) and iOS (Secure Enclave) for private key storage
- eIDAS 2.0 compliant — can be used in EU regulatory contexts
- sd-JWT and mDOC support for selective disclosure

***

## 6. Security Hardening Checklist

### 6.1 Authentik (edge-specific)

```bash
# Enforce memory overcommit for Redis stability
sudo sysctl vm.overcommit_memory=1

# Monitor Authentik resource usage
docker stats authentik-server authentik-worker authentik-redis authentik-db

# If CPU spikes on authentik-server (>100%), check Redis storage
docker exec authentik-redis redis-cli info memory | grep used_memory_human
```

**DECISION: CPU spike handling**[^18]
- If Redis `used_memory` is near `maxmemory` limit (128 MB): increase limit to 256 MB in compose, or reduce session lifetime in Authentik settings
- If Authentik-server CPU > 50% at idle: reduce workers further with `AUTHENTIK_WEB__WORKERS=1` and restart

### 6.2 OpenFang Security Systems

OpenFang includes 16 discrete security systems relevant to this deployment:[^3]

| System | Relevant For |
|--------|-------------|
| WASM Dual-Metered Sandbox | Isolates Hand tool execution — custom Nextcloud tools can't escape sandbox |
| Ed25519 Signed Agent Manifests | HAND.toml identity is cryptographically signed |
| Prompt Injection Scanner | Protects against users injecting malicious instructions through Talk |
| Loop Guard | Prevents runaway tool call loops (e.g., recursive web_fetch) |
| SSRF Protection | Blocks Hand from fetching internal cloud metadata endpoints |
| Capability Gates | Agent can only access tools declared in HAND.toml |

### 6.3 Nextcloud Talk Bot Signature Verification

Every webhook message from Nextcloud is signed. OpenFang verifies automatically but for manual debugging:[^12]

```bash
# Verify signature manually
RANDOM_HEADER="<X-Nextcloud-Talk-Bot-Random header value>"
BODY='<request body>'
SECRET="<your bot secret>"
EXPECTED_SIG=$(echo -n "${RANDOM_HEADER}${BODY}" | openssl dgst -sha256 -hmac "${SECRET}" | cut -d' ' -f2)
echo "Expected: ${EXPECTED_SIG}"
echo "Received: <X-Nextcloud-Talk-Bot-Signature header value>"
```

**DECISION: 401 errors on bot responses**[^22]
- Cause: Talk API signature format changed in Talk 22.x
- Fix: Regenerate bot secret → `occ talk:bot:remove <ROOM_TOKEN> <BOT_ID>` → re-register with new secret
- Verify: Send test message, check `openfang logs nextcloud-talk`

### 6.4 Nextcloud Admin Security Settings

```bash
# Disable user self-registration (all users come from Authentik/DIDroom)
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ config:system:set allow_user_creation --value=false --type=boolean

# Force HTTPS
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ config:system:set overwriteprotocol --value=https

# Set trusted proxy (Caddy)
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ config:system:set trusted_proxies 0 --value=127.0.0.1

# Disable password login (only OIDC after Authentik is stable)
# In Nextcloud Admin → Security → uncheck "Allow users to log in with their Nextcloud password"
# WARNING: only do this AFTER verifying OIDC login works for all admin accounts
```

***

## 7. Verification Procedure

An agent running this guide MUST execute all checks in this section after completing Sections 3–6. A check that returns FAIL requires returning to the indicated section.

### 7.1 Nextcloud AIO Health

```bash
# Check all AIO containers are running
docker ps --filter "name=nextcloud-aio" --format "{{.Names}}: {{.Status}}"
# PASS: all show "Up X minutes (healthy)"
# FAIL: return to Section 3.1

# Verify Nextcloud responds
curl -sk https://cloud.local/status.php | python3 -m json.tool
# PASS: {"installed":true,"maintenance":false,...}
# FAIL: check Caddy logs with `docker logs caddy`
```

### 7.2 llama-server → Nextcloud Assistant

```bash
# Test AI endpoint is reachable from Docker host
curl -s http://localhost:lama_server_port>/v1/models | python3 -m json.tool
# PASS: shows model list with your loaded model

# Test from inside Nextcloud container
docker exec nextcloud-aio-nextcloud \
  curl -s http://host.docker.internal:lama_server_port>/v1/models
# PASS: same model list
# FAIL: llama-server not running or wrong port → check `ps aux | grep llama-server`
```

### 7.3 OpenFang + Talk Bot

```bash
# OpenFang is running
openfang status
# PASS: kernel running, API server on :4200, nextcloud-talk channel: connected

# Bot is registered in Nextcloud
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ talk:bot:list
# PASS: "Nextcloud Support" appears with status "enabled"

# Send test message in Talk room
# (manual step: send "@Nextcloud Support hello" in the bot's room)
# PASS: agent responds within 5–10 seconds
# FAIL: check `openfang logs nextcloud-talk` for signature errors or webhook timeout
```

### 7.4 Authentik OIDC

```bash
# Authentik services are healthy
docker compose -f ~/edge-stack/authentik/compose.yaml ps
# PASS: all 4 services show "healthy"

# OIDC discovery endpoint works
curl -s http://localhost:9000/application/o/nextcloud/.well-known/openid-configuration \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('OIDC OK:', d['issuer'])"
# PASS: prints "OIDC OK: http://localhost:9000/application/o/nextcloud/"
# FAIL: return to Section 5.3

# Nextcloud user_oidc provider is configured
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ user_oidc:provider:list
# PASS: shows "authentik" provider
```

### 7.5 DIDroom Federation (optional, if deployed)

```bash
# DIDroom Authorization Server is reachable
curl -s http://localhost:3000/.well-known/openid-configuration | python3 -m json.tool
# PASS: valid OIDC discovery document

# Authentik source is active
# Check: Authentik Admin → Directory → Federation → DIDroom source shows "enabled"
```

***

## 8. Operational Reference

### 8.1 Starting / Stopping the Full Stack

```bash
# Start order matters: IAM before Nextcloud, Nextcloud before OpenFang
cd ~/edge-stack/authentik && docker compose up -d
sleep 30  # wait for Authentik DB migration
cd ~/edge-stack/nextcloud-aio && docker compose up -d
sleep 60  # wait for AIO to start all containers
openfang start

# Stop order (reverse)
openfang stop
cd ~/edge-stack/nextcloud-aio && docker compose down
cd ~/edge-stack/authentik && docker compose down
```

### 8.2 Adding the Agent to New Nextcloud Talk Rooms

```bash
# List rooms
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ talk:room:list

# Add bot to a room (use token from list above)
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ talk:bot:setup <ROOM_TOKEN>
```

### 8.3 Updating the SKILL.md Knowledge Base

```bash
# Edit the knowledge base
nano ~/.openfang/hands/nextcloud-support/SKILL.md

# Reload the Hand (no restart required — SKILL.md is injected at runtime)
openfang hand reload nextcloud-support
```

### 8.4 Adding Users in Authentik → Auto-Provisioned in Nextcloud

```
Authentik Admin → Directory → Users → Create User
```

On first login via OIDC, `user_oidc` automatically creates the user in Nextcloud with the `preferred_username` claim as the Nextcloud username. No manual Nextcloud user creation is needed. To trigger a file scan for the new user after first login:[^20]

```bash
docker exec --user www-data nextcloud-aio-nextcloud \
  php occ files:scan --user <username>
```

### 8.5 IAM Comparison: Final Selection Rationale

| Criterion | DIDroom (standalone) | Authentik (standalone) | DIDroom + Authentik (chosen) |
|-----------|---------------------|----------------------|------------------------------|
| Nextcloud OIDC SSO | Needs custom bridge | Native, documented[^20] | Native via Authentik |
| W3C-DID credentials | Yes[^7] | No | Yes (DIDroom upstream) |
| eIDAS 2.0 compliance | Yes[^7] | No | Yes (DIDroom layer) |
| Edge RAM usage | ~200–400 MB | ~400–600 MB[^8] | ~600–1000 MB combined |
| Setup complexity | High | Moderate | Moderate + DIDroom optional |
| Mobile wallet auth | Yes[^7] | Via external IDP only | Yes (DIDroom wallet) |
| MFA / Passkeys | Limited | Full, visual flow builder[^15] | Full (Authentik) + DID wallet |
| **Verdict** | Too complex for OIDC SSO alone | Ideal practical SSO | **Optimal: proven SSO + advanced creds** |

---

## References

1. [all-in-one/compose.yaml at main · nextcloud/all-in-one](https://github.com/nextcloud/all-in-one/blob/main/compose.yaml) - 📦 The official Nextcloud installation method. Provides easy deployment and maintenance with most fea...

2. [Nextcloud Assistant](https://docs.nextcloud.com/server/31/admin_manual/ai/app_assistant.html) - Nextcloud assistant is the primary graphical user interface for interacting with artificial intellig...

3. [Hands - OpenFang - Mintlify](https://www.mintlify.com/RightNow-AI/openfang/concepts/hands) - Skill Injection. Hands can bundle a SKILL.md file with domain expertise. At ... Step-by-step guide t...

4. [Skills - OpenFang - Mintlify](https://www.mintlify.com/yocxy2/openfang/config/skills) - Skills are pluggable tool bundles that extend agent capabilities in OpenFang. A skill packages one o...

5. [How to Run Authentik in Docker for Identity Provider - OneUptime](https://oneuptime.com/blog/post/2026-02-08-how-to-run-authentik-in-docker-for-identity-provider/view) - Deploy Authentik in Docker as a self-hosted identity provider with SSO, OAuth2, SAML, and LDAP suppo...

6. [Docker Compose installation | authentik](https://version-2025-4.goauthentik.io/docs/install-config/install/docker-compose) - This installation method is for test setups and small-scale production setups.

7. [DIDroom - Forkbomb BV](https://forkbomb.solutions/solution/didroom/) - DidRoom is an open-source multiplatform and multifunctional Identity DID/SSI wallet, compliant with ...

8. [High memory usage - feature, bug or problem with configuration / host?](https://www.reddit.com/r/Authentik/comments/1bx4mto/high_memory_usage_feature_bug_or_problem_with/) - High memory usage - feature, bug or problem with configuration / host?

9. [Nextcloud AIO Without Buying a Domain: Local DNS + Caddy TLS ...](https://travis.media/blog/nextcloud-aio-locally-no-domain/) - Step 1 - Start with this Docker Compose File · Step 2 - Tweak the Docker Compose File · Step 3 - Add...

10. [How to use Nextcloud AIO community containers](https://nextcloud.com/blog/how-to-use-nextcloud-aio-using-community-containers/) - Learn how to add numerous useful features to your Nextcloud AIO instance using Nextcloud AIO Communi...

11. [OpenClaw Custom Skill Creation - Step by Step - Zen van Riel](https://zenvanriel.nl/ai-engineer-blog/openclaw-custom-skill-creation-guide/) - Learn how to create custom skills for OpenClaw that make your AI assistant do exactly what you need....

12. [Bots and webhooks - Nextcloud Talk API documentation](https://nextcloud-talk.readthedocs.io/en/latest/bots/) - Messages are signed using the shared secret that is specified when installing a bot on the server. C...

13. [Nextcloud Talk - OpenClaw Docs](https://docs.openclaw.ai/channels/nextcloud-talk) - ​. Quick setup (beginner) · Install the Nextcloud Talk plugin. · Enable the bot in the target room s...

14. [Setting up Nextcloud Talk with OpenClaw](https://open-claw.bot/docs/channels/nextcloud-talk/) - A guide to connecting your Nextcloud Talk instance to OpenClaw using the webhook bot plugin.

15. [Authentik vs Authelia vs Keycloak: Choosing the Right Self-Hosted ...](https://blog.elest.io/authentik-vs-authelia-vs-keycloak-choosing-the-right-self-hosted-identity-provider-in-2026/) - Authentik supports the same protocols as Keycloak (OAuth 2.0, OIDC, SAML) but wraps them in a cleane...

16. [OAuth 2.0 provider - authentik Docs](https://docs.goauthentik.io/add-secure-apps/providers/oauth2/) - OAuth 2.0 is an authorization protocol that allows an application (the RP) to delegate authorization...

17. [Setting Up Authentik with Docker Compose](https://docs.techdox.nz/authentik/) - Authentik is an open-source Identity Provider (IdP) designed to be flexible and versatile. It offers...

18. [Diagnosing and Fixing High CPU Usage in Authentik Stack](https://www.tekonline.com.au/diagnosing-and-fixing-high-cpu-usage-in-authentik-stack/) - The Problem Recently, we noticed that our Authentik authentication stack was experiencing unusually ...

19. [How to Configure Authentik for SSO - OneUptime](https://oneuptime.com/blog/post/2026-01-25-authentik-sso/view) - Authentik is an open-source identity provider that centralizes authentication with support for OAuth...

20. [Migration from LDAP to OIDC: Nextcloud - s3lph made](https://s3lph.me/ldap-to-oidc-migration-2-nextcloud.html) - This article covers the setup and migration in Nextcloud. OIDC Setup in Nextcloud. While LDAP integr...

21. [User authentication with OpenID Connect - Nextcloud Documentation](https://docs.nextcloud.com/server/stable/admin_manual/configuration_user/user_auth_oidc.html) - If using an external identity provider, only the user_oidc app is necessary. If Nextcloud is the ide...

22. [Nextcloud Talk: Bot responses fail with 401 (signature rejected) on ...](https://github.com/openclaw/openclaw/issues/6174) - The Nextcloud Talk plugin successfully receives webhook messages from Nextcloud, but sending respons...

