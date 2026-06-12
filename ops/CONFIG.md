# SolarSeed v3.1 — TRL4 CONFIG Snapshot (2026-05-30)
IMPORTANT:
- Do not put secrets in Git.
- Keep credentials only in `.secrets/` on host and/or password manager.

## 1) Host identity (TRL4 lab machine)
- Hostname: `wera-ss-pt-sn-1`
- LAN IP (DHCP reservation): `192.168.1.71`
- Tailscale IPv4: `100.82.194.96`
- Primary operator account: `wera`

## 2) OS and hardware profile
- OS: Debian GNU/Linux 13 (trixie), `DEBIAN_VERSION_FULL=13.4`
- Kernel: `6.12.85+deb13-amd64`
- CPU: Intel(R) Core(TM) i5-4430 @ 3.00GHz
  - 4 vCPU (`Thread(s) per core: 1`, `Core(s) per socket: 4`, `Socket(s): 1`)
- Memory:
  - MemTotal: `8004552 kB` (~8.0 GB)
  - MemAvailable at review: `2971392 kB` (~2.97 GB)
  - SwapTotal: `5330940 kB` (~5.3 GB)
  - SwapFree at review: `4343080 kB` (~4.34 GB)

## 3) Storage layout (observed)
- Root filesystem: `/dev/sda7` (ext4)
  - Size: 93G
  - Used at review: 29%
- Data filesystem: `/dev/mapper/data_crypt`
  - Mountpoint: `/data`
  - Size: 96G
  - Used at review: 3%

## 4) Runtime/software stack baseline
- Docker Engine: active
- Running containers: 23
  - Healthy: 18
  - Running without Docker healthcheck: 5 (`poly-robot-runtime-supervisor-1`, `poly-robot-runtime-gui`, `col-spirit`, `col-alertmanager`, `col-node-exporter`)
- Key City services currently healthy: `col-openfang`, `col-prometheus`, `col-llama-cpp`, `col-gitea`, `nextcloud-aio-mastercontainer`
- Odoo stack profile:
  - **Odoo**: 19.0 Enterprise (custom subscription `M240830172487565`)
  - Image: `odoo:19.0` (Community base; Enterprise addon code must be mounted separately)
  - DB: `pgvector/pgvector:pg15` (`wera` database with Enterprise module metadata)
  - Enterprise code registered in DB as `database.enterprise_code`
  - Port bind profile: loopback default (`127.0.0.1:8069`) with tailnet exposure through `tailscale serve`
  - DB routing profile: `--db-filter=${ODOO_DB_FILTER:-^wera$}`

## 5) Network and exposed service ports (observed)
- Public binds include:
  - `0.0.0.0:11000->11000/tcp` (nextcloud-aio-apache)
  - `0.0.0.0:3478->3478/tcp+udp` (nextcloud-aio-talk)
  - `0.0.0.0:8765->8765/tcp` (poly-robot-runtime-gui)
- Loopback-only binds include:
  - `127.0.0.1:8080->8080/tcp` (nextcloud-aio-mastercontainer)
  - `127.0.0.1:4200->4200/tcp` (col-openfang)
  - `127.0.0.1:9105->9105/tcp` (col-spirit)
  - `127.0.0.1:9090->9090/tcp` (col-prometheus)
  - `127.0.0.1:9093->9093/tcp` (col-alertmanager)
  - `127.0.0.1:3000->3000/tcp` and `127.0.0.1:2222->2222/tcp` (col-gitea)
  - `127.0.0.1:8081->8081/tcp` (col-llama-cpp)

## 6) Validation timestamp
- Last verified from operator workstation over Tailscale SSH: `2026-05-30`

## 7) Latest remediation status (2026-06-05)
- Disabled failing Odoo cron jobs:
  - `48` Marketing Automation: execute activities
  - `81` AI Fields: Compute AI fields
  - `82` AI Documents: Sort documents with AI
- Refreshed PostgreSQL collation metadata for `postgres` and `template1`; mismatch query now returns zero rows.
- Removed obsolete `gogardens` database from the local Odoo PostgreSQL instance.
- Odoo health baseline after remediation:
  - Login endpoint `/web/login?db=wera` returns `200`
  - Module queue states (`to install`, `to upgrade`, `to remove`) are empty
## 8) Fonseca rollout readiness snapshot (2026-06-08, local pre-TRL replay)
- Rollout addon: `wera_fonseca_site` version `19.0.1.1.0`
- Manual callback mode baseline applied:
  - consultation/quote forms post to `/fonseca/intake`
  - CRM lead creation with `fonseca-gardens` + `intent:*` tags
  - consultation intent creates CRM callback-scheduling activity (`manual-callback-queue`)
  - stale `/appointment` CTA links removed from rendered Fonseca routes and header CTA patches
  - rollout script defaults to `FONSECA_APPOINTMENT_MODE=manual_callback`
  - unsupported appointment-family queue states normalized to `uninstalled`
- Content production artifacts prepared:
  - `odoo-app/content/fonseca_gardens_source_of_truth.json`
  - `odoo-app/content/fonseca_gardens_visual_request_pack.json`
- Evidence packs:
  - `ops/evidence/fonseca_phase6_r1_20260607T201434Z`
  - `ops/evidence/fonseca_phase6_r2_20260608T113906Z`
  - `ops/evidence/fonseca_phase8_manual_callback_20260608T170919Z`
- Remaining closure gate:
  - final manual browser QA pass after TRL replay (callback UX, content polish, responsive behavior)

