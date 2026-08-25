# SolarSeed v3.1 — TRL4 CONFIG Snapshot (Frank)

IMPORTANT:
- Do not put secrets in Git.
- Keep credentials only in `.secrets/` on host and/or password manager.
- Station callsign: **Frank** (hostname remains `wera-ss-pt-sn-1`).
- Full station document: `ops/stations/FRANK.md`.

## 1) Host identity (TRL4 lab machine / Frank)
- Station name: `Frank`
- Hostname: `wera-ss-pt-sn-1`
- Tailscale FQDN: `wera-ss-pt-sn-1.tailfb390c.ts.net`
- LAN IP (DHCP reservation): `192.168.1.71`
- Tailscale IPv4: `100.82.194.96`
- Primary operator account: `wera`
- SSH: `ssh wera@wera-ss-pt-sn-1.tailfb390c.ts.net` (or LAN / Tailscale IP)

## 2) OS and hardware profile
- OS: Debian GNU/Linux 13 (trixie), `DEBIAN_VERSION_FULL=13.5`
- Kernel: `6.12.95+deb13-amd64`
- CPU: Intel(R) Core(TM) i5-4440 CPU @ 3.10GHz
  - 4 vCPU (`Thread(s) per core: 1`, `Core(s) per socket: 4`, `Socket(s): 1`)
- GPU:
  - NVIDIA GeForce GTX 1050 Ti (`10de:1c82`)
  - Active driver: NVIDIA proprietary `550.163.01` (`nvidia-smi` working)
  - VRAM: total `4096 MiB`; with GPU llama loaded ~`3000 MiB` used by `/app/llama-server`
- Memory:
  - MemTotal: `16341208 kB` (~15.6 GiB)
  - Typical available with cache: ~10 GiB class when stack healthy
- Swap: ~5.1 GiB
- Docker Engine: `29.6.1`
- Docker data-root: `/data-bulk/docker`
- Docker accelerator runtime: NVIDIA Container Toolkit configured; GPU containers available with `--gpus all`.

## 3) Storage layout (live 2026-08-11)
Prefer disk **by-id** (sdX letters can swap):
- System disk: `ata-ST1000DM003-1ER162_Z4Y0CBCQ` (often `/dev/sda`, 931.5G)
- Nextcloud disk: `ata-SAMSUNG_HD501LJ_S0VVJ1PP402262` (often `/dev/sdb`, 465.8G)

| Mount | Source | Size | Role |
|-------|--------|------|------|
| `/` | ST1000 `sda7` ext4 | 93G | OS only |
| `[SWAP]` | ST1000 `sda8` | 5.1G | swap |
| `/data` | LUKS `data_crypt` on ST1000 `sda9` | 96G | City configs, secrets, light binds, Borg parent |
| `/data-bulk` | LUKS `data_bulk` on ST1000 `sda3` | 384G | Docker data-root + growth |
| `/mnt/nextcloud-data` | LUKS `nextcloud_data` on Samsung `sdb1` | 458G | Nextcloud AIO user datadir |

Keyfiles:
- `data_crypt`: `/etc/cryptsetup-keys.d/data_crypt.key`
- `data_bulk`: `/data/.secrets/data-bulk.key`
- `nextcloud_data`: `/data/.secrets/nextcloud-data.key`

Idle legacy NTFS still present on ST1000: `sda1`, `sda2`, `sda5` (Data2), `sda6` (recovery).

Snapshot free space (2026-08-11): `/` ~38% used; `/data` ~5%; `/data-bulk` ~6%; `/mnt/nextcloud-data` ~1%.

## 4) Runtime/software stack baseline
- Running containers: ~25–26 (City compose + Nextcloud AIO)
- Docker root on City bulk (not on `/`)
- Core healthy at last verification:
  - Nextcloud AIO: mastercontainer, apache (`127.0.0.1:11000`), nextcloud, database, redis
  - City: `col-openfang`, `col-prometheus`, `col-llama-cpp`, `col-postgres`, `col-redis`, `col-spirit`, cityview UI + operator-gateway
- Nextcloud version: `33.0.7.1` (`33.0.7`)
- Nextcloud datadir bind: host `/mnt/nextcloud-data` -> container `/mnt/ncdata`
- Mastercontainer env includes: `NEXTCLOUD_DATADIR=/mnt/nextcloud-data`, `APACHE_IP_BINDING=127.0.0.1`, `APACHE_PORT=11000`, `AIO_LOG_LEVEL=warn`
- OpenFang API: healthy (~0.5.1)
- llama.cpp production profile (verified GPU 2026-08-19):
  - Image: **`local/llama.cpp:server-cuda-12.4.1-sm61`** (built on Frank; do **not** use rolling `ghcr.io/...:server-cuda` — requires CUDA>=12.8 / breaks driver 550)
  - Model: `/models/Bonsai-4B-Q1_0.gguf`
  - Args: `--threads 4 --ctx-size 16384 --parallel 1 -ngl 999`
  - `gpus: all`; VRAM in use ~3.0 GiB on GTX 1050 Ti when healthy
  - NC `integration_openai` URL: `http://col-llama-cpp:8081`, model id `/models/Bonsai-4B-Q1_0.gguf`
  - Rebuild recipe: `/data-bulk/build/llama.cpp` + `.devops/cuda.Dockerfile` with `CUDA_VERSION=12.4.1`, `UBUNTU_VERSION=22.04`, `CUDA_DOCKER_ARCH=61`, `GCC_VERSION=11`, target `server`
- Gitea: present on loopback; health may flap after restarts
- Odoo: **not running** at snapshot; tailnet `:443` re-routed to NC on 2026-08-18
- Poly-Robot: **not running** at snapshot
- Collabora: intermittent unhealthy/restart loops possible; non-blocking for basic NC file access

## 5) Network and ports (observed)
### Tailscale serve (as of 2026-08-18)
- `/` (`:443`) -> `http://localhost:11000` (Nextcloud — canonical URL, must stay on NC)
- `:8443` -> `http://127.0.0.1:11000` (Nextcloud alias)
- `:4200` -> `http://127.0.0.1:4200` (OpenFang)

### Loopback-preferred / loopback
- `127.0.0.1:11000` Nextcloud Apache
- `127.0.0.1:8080` AIO mastercontainer admin
- `127.0.0.1:4200` OpenFang
- `127.0.0.1:3000` / `127.0.0.1:2222` Gitea
- `127.0.0.1:9093` Alertmanager
- `127.0.0.1:9205` nextcloud-exporter

### Currently also published on 0.0.0.0 (policy drift vs strict loopback-only)
- `9090` Prometheus
- `9105` Spirit
- `8081` llama.cpp
- `5174` cityview-ui
- `8780` cityview-operator-gateway
- `3478` Nextcloud Talk TURN/STUN

## 6) Backups
- Borg path: `/data/backups/borg`
- Archives:
  - `20260717_000110-nextcloud-aio`
  - `20260811_013544-nextcloud-aio` (post datadir + Docker root migration)
  - `20260818_131837-nextcloud-aio` (post NC TRL5-alignment + user provisioning; 23s, Exited 0)
- Runbook: `ops/NEXTCLOUD_AIO_TRL4.md`

## 7) Retention / cleanup pending operator soak
- Keep until multi-day stability accepted:
  - `/var/lib/docker.pre-data-bulk-*` (pre-move Docker tree on root)
  - Docker volume `nextcloud_aio_nextcloud_data` (pre-migration ncdata copy)

## 8) Validation timestamp
- Last verified from operator workstation over Tailscale SSH: `2026-08-18`
- Authoritative narrative: `ops/stations/FRANK.md`

## 11) NC performance baseline (2026-08-18)
- Response: `/login` 83ms, `/status.php` 30ms
- PHP 8.3.33; OPcache enabled (256 MB) + JIT (1255, 128 MB buffer)
- APCu + Redis caching configured; Redis hit rate ~70% on fresh install
- DB: 20 MB (fresh), 1 active connection
- ClamAV: ~980 MB RAM (virus DB in memory, expected)
- All required NC 33 PHP modules present; no missing DB indexes
- `maintenance_window_start` = `1` (1am UTC)
- NC 33.0.8 update available; 3 app updates (calendar, contacts, notes)

## 9) Outbound email / Proton Bridge (installed 2026-08-19)
- Purpose: transactional SMTP for Nextcloud AIO on Frank (same pattern as TRL5)
- Host install: **done** (`protonmail` + docker-gateway socat proxy)
- Bridge package: `protonmail-bridge` `3.21.2-1`
- Units: `protonmail.service`, `protonmail-smtp-docker-proxy.service` (active+enabled)
- Bridge listen: `127.0.0.1:1025` SMTP STARTTLS, `127.0.0.1:1143` IMAP
- Proxy binds Docker gateways including `172.18.0.1:1025` (nextcloud-aio gw)
- UFW: `allow from 172.16.0.0/12 to any port 1025 proto tcp` (required; without it NC timed out to gateway)
- NC SMTP (non-secret): host `172.18.0.1`, port `1025`, `tls`, auth true, from `cloud@wera.global`
- NC SMTP credentials: **pending** Bridge `login` + `info 0` password into `mail_smtpname` / `mail_smtppassword`
- Odoo: not running at install; when restored apply TRL5 alias-domain return-path rules
- Runbook: `ops/RUNBOOK.md` "TRL4 outbound email"

## 10) Historical notes still relevant
- Console GUI / no-sleep work (2026-06-27): sleep targets masked; GDM may currently be failed -- does not block City services.
- AIO child containers require `AIO_LOG_LEVEL=warn` propagation; empty log settings break Postgres/Redis/Nextcloud supervisord after recreate.
- Odoo Enterprise subscription metadata and Fonseca rollout notes from mid-2026 remain in git history / older sections of ops evidence; stack not active on Frank at this snapshot.
