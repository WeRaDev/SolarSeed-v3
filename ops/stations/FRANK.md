# SolarSeed Station "Frank" (TRL4 Lab)

Station callsign: **Frank**  
Role: City of Light TRL4 lab host (grid power, full stack validation)  
Hostname: `wera-ss-pt-sn-1`  
Tailscale FQDN: `wera-ss-pt-sn-1.tailfb390c.ts.net`  
Document status: live snapshot **2026-08-11T01:57Z** (post storage reorg + NC datadir + Docker root migration)

Related:
- `ops/CONFIG.md` -- compact config snapshot
- `ops/NEXTCLOUD_AIO_TRL4.md` -- Nextcloud AIO operations
- `WARP.md` -- agent operational guide
- Bootstrap scripts under `ops/bootstrap/`

---

## 1) Identity and access

| Field | Value |
|-------|--------|
| Station name | Frank |
| Stage | TRL4 (lab, unlimited grid energy) |
| Hostname | `wera-ss-pt-sn-1` |
| Operator account | `wera` |
| LAN | `192.168.1.71/24` on `enp3s0` |
| Tailscale IPv4 | `100.82.194.96` |
| SSH (LAN) | `ssh wera@192.168.1.71` |
| SSH (tailnet) | `ssh wera@wera-ss-pt-sn-1.tailfb390c.ts.net` or `ssh wera@100.82.194.96` |
| Sudo | interactive password (TTY); use `ssh -t` for privileged work |

### Tailscale serve (tailnet only)

| URL | Backend |
|-----|---------|
| `https://wera-ss-pt-sn-1.tailfb390c.ts.net/` | `http://127.0.0.1:8069` (Odoo -- currently not running) |
| `https://wera-ss-pt-sn-1.tailfb390c.ts.net:8443/` | `http://127.0.0.1:11000` (Nextcloud Apache) |
| `https://wera-ss-pt-sn-1.tailfb390c.ts.net:4200/` | `http://127.0.0.1:4200` (OpenFang) |

---

## 2) Hardware and OS

| Field | Live value |
|-------|------------|
| CPU | Intel Core i5-4440 @ 3.10GHz, 4 cores / 4 threads |
| RAM | ~15.6 GiB (`MemTotal 16341208 kB`) |
| Swap | ~5.1 GiB |
| GPU | NVIDIA GP107 [GeForce GTX 1050 Ti] (`10de:1c82`) |
| OS | Debian GNU/Linux 13 (trixie), `DEBIAN_VERSION_FULL=13.5` |
| Kernel | `6.12.95+deb13-amd64` |
| Docker Engine | 29.6.1 |
| Docker data-root | `/data-bulk/docker` |

Power policy: sleep/suspend targets remain masked (server must not sleep). GDM has been failing (`gdm.service` failed at snapshot); core services do not depend on GUI.

### 2.1 GPU runtime status (2026-08-11)

- Proprietary NVIDIA driver active (`550.163.01`), verified with `nvidia-smi`.
- `nouveau` is no longer the active runtime path for inference workloads.
- NVIDIA Container Toolkit is installed; Docker GPU workloads run with `--gpus all`.
- `col-llama-cpp` is configured with GPU device requests (`Capabilities: [["gpu"]]`).
- VRAM snapshot (`nvidia-smi`): total `4096 MiB`, used `0 MiB`, free `4032 MiB`.

---

## 3) Storage architecture (post 2026-08-11 reorg)

Device names can swap after reboot. Prefer **by-id**:

| by-id | Live node (snapshot) | Role |
|-------|----------------------|------|
| `ata-ST1000DM003-1ER162_Z4Y0CBCQ` | `/dev/sda` (931.5G) | System + City LUKS partitions |
| `ata-SAMSUNG_HD501LJ_S0VVJ1PP402262` | `/dev/sdb` (465.8G) | Nextcloud AIO user data (full disk LUKS) |

### ST1000 layout (`sda`)

```text
sda
├─ sda1   500M  NTFS   (legacy reserved)
├─ sda2   97G   NTFS   (legacy idle)
├─ sda3   391G  LUKS -> data_bulk  -> /data-bulk   (city-bulk, Docker)
├─ sda4   extended
├─ sda5   202G  NTFS   Data2 (legacy idle)
├─ sda6   45G   NTFS   recovery (legacy idle)
├─ sda7   94G   ext4   /                          (OS)
├─ sda8   5.1G  swap
└─ sda9   98G   LUKS -> data_crypt -> /data       (City configs/secrets)
```

### Samsung layout (`sdb`)

```text
sdb
└─ sdb1  466G  LUKS -> nextcloud_data -> /mnt/nextcloud-data
```

### Mount table (live)

| Mount | Mapper / device | Size | Use% (snapshot) | Purpose |
|-------|-----------------|------|-----------------|---------|
| `/` | `/dev/sda7` ext4 | 93G | ~38% | OS, packages, home |
| `/data` | `data_crypt` ext4 label `data` | 96G | ~5% | City compose, secrets, models, prometheus bind data, Borg path parent |
| `/data-bulk` | `data_bulk` ext4 label `city-bulk` | 384G | ~6% | Docker data-root + growth room |
| `/mnt/nextcloud-data` | `nextcloud_data` ext4 label `nextcloud-data` | 458G | ~1% | Nextcloud AIO datadir (`/mnt/ncdata` in container) |

### crypttab / keys (no secret values in git)

| Mapper | Keyfile (host) | Mount |
|--------|----------------|-------|
| `data_crypt` | `/etc/cryptsetup-keys.d/data_crypt.key` | `/data` |
| `data_bulk` | `/data/.secrets/data-bulk.key` | `/data-bulk` |
| `nextcloud_data` | `/data/.secrets/nextcloud-data.key` | `/mnt/nextcloud-data` |

All three LUKS mounts use `nofail` + short device timeout in fstab so a locked volume does not brick boot into emergency mode.

### `/data-bulk` directory stubs

```text
/data-bulk/
  docker/          # Docker Engine data-root
  backups/
  containers/
  models/
  prometheus/
  README-SOLARSEED.txt
```

### Storage design intent

1. **OS root stays small** -- packages and logs only; never Docker layers.
2. **`/data`** -- City configuration, soul, secrets, light service binds, Borg backup directory parent.
3. **`/data-bulk`** -- high-churn Docker images/volumes/layers.
4. **`/mnt/nextcloud-data`** -- user cloud files on dedicated encrypted disk.

Legacy NTFS on `sda1/2/5/6` remains idle reclaim candidates (not wiped).

---

## 4) Runtime topology (City of Light on Frank)

### Compose / networks

| Context | Path / name |
|---------|-------------|
| Host City compose | `/data/city-of-light/docker-compose.yml` |
| City network | `city-of-light` |
| Nextcloud AIO network | `nextcloud-aio` |
| Docker root | `/data-bulk/docker` (`/etc/docker/daemon.json`) |

### Service map (buildings)

| Building | Container(s) | Host bind (snapshot) | Notes |
|----------|--------------|----------------------|-------|
| Fortress | Nextcloud AIO family | Apache `127.0.0.1:11000`; AIO admin `127.0.0.1:8080`; Talk `0.0.0.0:3478` | NC 33.0.7.1; datadir on Samsung LUKS |
| Library | `col-prometheus`, `col-alertmanager`, `col-cadvisor`, `col-node-exporter` | Prom `0.0.0.0:9090`; AM `127.0.0.1:9093` | Scrapes include nextcloud-exporter |
| University | `col-llama-cpp` | `0.0.0.0:8081` | OpenAI-compatible API; production model `Bonsai-4B-Q1_0.gguf`; runtime `--threads 4 --ctx-size 4096 --parallel 1`; GPU enabled |
| House | `col-postgres` | internal | City DB |
| Agency | `col-openfang` | `127.0.0.1:4200` | OpenFang ~0.5.1 |
| Spirit | `col-spirit` | `0.0.0.0:9105` | Python Spirit; observation + approvals |
| Event bus | `col-redis` | internal | |
| Forge | `col-gitea` (+ DB volume) | `127.0.0.1:3000`, `127.0.0.1:2222` | May flap health after restarts |
| Cityview | `cityview-ui`, `cityview-operator-gateway` | `0.0.0.0:5174`, `0.0.0.0:8780` | Operator UI + gateway |
| Soul | files on `/data/city-of-light/` | -- | `soul.md` + HMAC under `/data` |

### Nextcloud AIO specifics

- Domain: `wera-ss-pt-sn-1.tailfb390c.ts.net`
- `NEXTCLOUD_DATADIR=/mnt/nextcloud-data`
- Container path: `/mnt/ncdata` (bind from host)
- `APACHE_IP_BINDING=127.0.0.1`, `APACHE_PORT=11000`
- `AIO_LOG_LEVEL=warn` required on master; children may need recreation with same env after AIO recreate
- Community: fail2ban, nextcloud-exporter (`127.0.0.1:9205`)
- ClamAV disabled
- Borg repo: `/data/backups/borg`
- Latest backup archive: `20260811_013544-nextcloud-aio` (2026-08-11); prior `20260717_000110-nextcloud-aio`

### Not running at snapshot (present historically / images may exist)

- Odoo stack (tailnet `:443` still points at `:8069`)
- Poly-Robot runtime containers

---

## 5) Health snapshot (2026-08-11 ~01:57Z)

Uptime at sample: ~3h10m after recent Docker root move / service restarts.

### HTTP probes (loopback)

| Endpoint | Result |
|----------|--------|
| Spirit `/health` | 200 |
| Prometheus `/-/healthy` | 200 |
| OpenFang `/api/health` | 200 |
| llama.cpp `/health` | 200 |
| Nextcloud `status.php` | 200 (`installed`, not maintenance, 33.0.7.1) |
| Cityview gateway `/health` | 200 |
| Gitea `/api/healthz` | flapping / not ready at sample |

### Container health (summary)

- Core NC: nextcloud, apache, database, redis, mastercontainer **healthy**
- City core: prometheus, openfang, llama-cpp, postgres, redis, cityview **healthy**
- Spirit / alertmanager / node-exporter: running, often **no Docker healthcheck**
- Collabora: intermittently unhealthy/restarting (non-blocking for basic NC)
- Borgbackup: **Exited (0)** after successful backup

### systemd failed (non-blocking for City stack)

- `gdm.service`
- `plymouth-quit.service`
- `user@1000.service`

Spirit reported `pending_approvals: 5` at sample.

---

## 6) Major changes recorded (2026-08-10/11)

1. **Root full incident** -- Collabora RW layer / Docker on tiny root; emergency reclaim.
2. **Samsung wipe** -- full disk LUKS+ext4 for Nextcloud datadir (`CONFIRM DESTRUCTIVE` on Samsung by-id only).
3. **AIO datadir migration** -- rsync from `nextcloud_aio_nextcloud_data` volume to `/mnt/nextcloud-data`; mastercontainer `NEXTCLOUD_DATADIR`.
4. **AIO log-level remediation** -- empty `log_min_messages` / Redis `loglevel ""` / supervisord `ENV_AIO_LOG_LEVEL`; fix with `AIO_LOG_LEVEL=warn` on children.
5. **ST1000 sda3 Data1 wipe** -- LUKS `data_bulk` mounted `/data-bulk` (`CONFIRM DESTRUCTIVE` sda3 only).
6. **Docker data-root move** -- `/var/lib/docker` -> `/data-bulk/docker`; old tree retained as `/var/lib/docker.pre-data-bulk-*`.
7. **Borg backup** -- archive `20260811_013544-nextcloud-aio` after migrations.

### Bootstrap scripts (repo)

| Script | Purpose |
|--------|---------|
| `ops/bootstrap/format-samsung-nextcloud-data.sh` | Samsung LUKS Nextcloud volume |
| `ops/bootstrap/format-sda3-city-bulk.sh` | ST1000 sda3 City bulk |
| `ops/bootstrap/migrate-aio-datadir-to-samsung.sh` | AIO datadir migrate |
| `ops/bootstrap/aio-start-with-new-datadir.sh` | AIO start helper |
| `ops/bootstrap/fix-aio-loglevel-and-start.py` | log-level fix + start |
| `ops/bootstrap/migrate-docker-root-to-data-bulk.sh` | Docker data-root migration |

---

## 7) Operator checklist

### Daily / after reboot

1. Confirm mounts: `df -hT / /data /data-bulk /mnt/nextcloud-data`
2. Confirm Docker root: `docker info --format '{{.DockerRootDir}}'` -> `/data-bulk/docker`
3. `docker ps` + core probes (Spirit, Prom, OpenFang, NC status.php)
4. If `/data` empty: unlock/mount City LUKS (keyfile crypttab should auto-open when disks present)
5. If NC children crash after AIO recreate: ensure `AIO_LOG_LEVEL=warn` on DB/Redis/Nextcloud

### High-impact reminders

- Never wipe disks by unstable `/dev/sdX` name alone -- use **by-id** and confirm root is not on target.
- Do not delete `/var/lib/docker.pre-data-bulk-*` or old `nextcloud_aio_nextcloud_data` volume until multi-day stability is accepted.
- Destructive partition ops require explicit `CONFIRM DESTRUCTIVE` with device identity.

### Useful probes

```bash
ssh wera@wera-ss-pt-sn-1.tailfb390c.ts.net 'df -hT / /data /data-bulk /mnt/nextcloud-data; docker info --format Root={{.DockerRootDir}}; curl -sk http://127.0.0.1:11000/status.php; curl -s http://127.0.0.1:9105/health; curl -s http://127.0.0.1:4200/api/health'
```

---

## 8) Open / next work

- Reclaim remaining idle NTFS (`sda2`, `sda5`, `sda6`) if more City capacity needed
- Decide fate of old Docker backup tree and old NC volume after soak period
- Repair or drop GDM if console GUI required
- Stabilize Gitea health after restarts
- Odoo: restart stack or clear stale tailnet `:443` serve if unused
- Optional: Collabora stability; Grafana; Customs (Authentik/DIDroom)
- Keep Spirit approvals queue triaged (5 pending at snapshot)

---

## 9) Naming

Use **Frank** in human/ops conversation for this TRL4 lab station.  
Technical identifiers remain `wera-ss-pt-sn-1` / tailnet FQDN above.
