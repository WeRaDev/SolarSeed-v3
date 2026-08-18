# TRL4 Nextcloud AIO Operations
## Scope
This runbook records Nextcloud All-in-One (AIO) configuration on TRL4 station **Frank** (`wera-ss-pt-sn-1`) after the TRL5-aligned hardening, datadir migration to Samsung LUKS, Docker data-root move, and backup validation (through 2026-08-11).
TRL5 reference host: `wera-ss-pt-tv-1.tailfb390c.ts.net`.
TRL4 target host: `wera-ss-pt-sn-1.tailfb390c.ts.net` (station Frank).
Station document: `ops/stations/FRANK.md`.
## Current access profile
- Nextcloud tailnet URL: `https://wera-ss-pt-sn-1.tailfb390c.ts.net:8443`
- Nextcloud local backend: `http://127.0.0.1:11000`
- AIO admin panel: `https://127.0.0.1:8080`
- OpenFang tailnet webhook/API: `https://wera-ss-pt-sn-1.tailfb390c.ts.net:4200`
- Existing Odoo tailnet URL remains on default HTTPS port 443: `https://wera-ss-pt-sn-1.tailfb390c.ts.net`
## Tailscale serve rules
Expected `tailscale serve status` entries:
- `https://wera-ss-pt-sn-1.tailfb390c.ts.net/` -> `http://127.0.0.1:8069` (Odoo)
- `https://wera-ss-pt-sn-1.tailfb390c.ts.net:8443/` -> `http://127.0.0.1:11000` (Nextcloud)
- `https://wera-ss-pt-sn-1.tailfb390c.ts.net:4200/` -> `http://127.0.0.1:4200` (OpenFang)
## Security binding
`nextcloud-aio-apache` must bind only to loopback:
- Expected port binding: `127.0.0.1:11000->11000/tcp`
- LAN check: `curl --connect-timeout 3 http://192.168.1.71:11000/` should fail or return HTTP code `000`.
Do not expose `11000` on `0.0.0.0`.
## Nextcloud datadir (Samsung LUKS, 2026-08-11)
User files live on the encrypted Samsung disk, not the default Docker volume.
- Host disk: `ata-SAMSUNG_HD501LJ_S0VVJ1PP402262` (`/dev/sdb`)
- LUKS mapper: `nextcloud_data`
- Filesystem label: `nextcloud-data` (ext4)
- Mountpoint: `/mnt/nextcloud-data` (~458G)
- Keyfile: `/data/.secrets/nextcloud-data.key`
- crypttab: `nextcloud_data UUID=<sdb1-uuid> /data/.secrets/nextcloud-data.key luks,nofail`
- fstab: `/dev/mapper/nextcloud_data /mnt/nextcloud-data ext4 defaults,nofail,x-systemd.device-timeout=10s 0 2`
- Mastercontainer env: `NEXTCLOUD_DATADIR=/mnt/nextcloud-data` and `AIO_LOG_LEVEL=warn`
- AIO config key: `nextcloud_datadir=/mnt/nextcloud-data`
- Nextcloud bind: host `/mnt/nextcloud-data` -> container `/mnt/ncdata`
- `occ config:system:get datadirectory` must return `/mnt/ncdata`
Bootstrap scripts:
- `ops/bootstrap/format-samsung-nextcloud-data.sh`
- `ops/bootstrap/migrate-aio-datadir-to-samsung.sh`
- `ops/bootstrap/aio-start-with-new-datadir.sh`
- `ops/bootstrap/fix-aio-loglevel-and-start.py`
After mastercontainer recreate, child containers may omit `AIO_LOG_LEVEL`. If Postgres/Redis/Nextcloud crash with empty `log_min_messages` / `loglevel ""` / missing `ENV_AIO_LOG_LEVEL` in supervisord, recreate those children with `-e AIO_LOG_LEVEL=warn` and/or patch `/supervisord.conf` `loglevel=warn` (see Known AIO log-level caveat).
Old volume `nextcloud_aio_nextcloud_data` can remain as cold backup until a successful Borg backup after migration; do not delete until verified.
## Docker data-root (City bulk, 2026-08-11)
Docker Engine data-root was moved off `/` onto City bulk LUKS:
- `data-root`: `/data-bulk/docker`
- daemon config: `/etc/docker/daemon.json` (`{"data-root": "/data-bulk/docker"}`)
- bulk volume: LUKS `data_bulk` on ST1000 `sda3`, mounted at `/data-bulk`
- bootstrap script: `ops/bootstrap/migrate-docker-root-to-data-bulk.sh`
- pre-move backup tree on root (delete only after multi-day stability): `/var/lib/docker.pre-data-bulk-*`
After this move, image/layer growth consumes `/data-bulk`, not the 93G root filesystem.
## AIO configuration subset
AIO config file inside the mastercontainer volume:
- Host path: `/var/lib/docker/volumes/nextcloud_aio_mastercontainer/_data/data/configuration.json`
- Container path: `/mnt/docker-aio-config/data/configuration.json`
Expected values:
- `domain`: `wera-ss-pt-sn-1.tailfb390c.ts.net`
- `apache_ip_binding`: `127.0.0.1`
- `borg_backup_host_location`: `/data/backups`
- `backup-mode`: `backup`
- `isClamavEnabled`: `1` (enabled 2026-08-18)
- `isDockerSocketProxyEnabled`: `1`
- `aio_community_containers`: `fail2ban nextcloud-exporter`

**ClamAV note (2026-08-18):** AIO sets `isClamavEnabled=1` in config but does not pass `MAX_SIZE` to the container, leaving `StreamMaxLength` empty and breaking `clamd`. Fix: manually recreate the container with the missing env var:
```bash
docker stop nextcloud-aio-clamav && docker rm nextcloud-aio-clamav
docker run -d --name nextcloud-aio-clamav --network nextcloud-aio \
  --restart unless-stopped \
  -e AIO_LOG_LEVEL=warn -e TZ=Europe/Lisbon -e MAX_SIZE=16G \
  -v nextcloud_aio_clamav:/var/lib/clamav \
  nextcloud/aio-clamav:latest
```
The volume `nextcloud_aio_clamav` preserves downloaded virus databases across recreations.
## Expected container status
Core containers:
- `nextcloud-aio-mastercontainer`: healthy
- `nextcloud-aio-apache`: healthy, loopback-bound on `127.0.0.1:11000`
- `nextcloud-aio-nextcloud`: healthy
- `nextcloud-aio-database`: healthy
- `nextcloud-aio-redis`: healthy
Enabled services:
- `nextcloud-aio-docker-socket-proxy`: healthy
- `nextcloud-aio-imaginary`: healthy
- `nextcloud-aio-whiteboard`: healthy
- `nextcloud-aio-notify-push`: healthy
- `nextcloud-aio-talk`: healthy, exposes TURN/STUN on `3478/tcp+udp`
- `nextcloud-aio-collabora`: healthy
- `nextcloud-aio-nextcloud-exporter`: running on `127.0.0.1:9205`
- `nextcloud-aio-fail2ban`: running
- `nextcloud-aio-clamav`: healthy (enabled 2026-08-18; `MAX_SIZE=16G`)
Backup container:
- `nextcloud-aio-borgbackup`: exits after backup; expected success state is `Exited (0)`.
## Health checks
Run:
```bash
curl -sk http://127.0.0.1:11000/status.php | python3 -m json.tool
curl -sk https://wera-ss-pt-sn-1.tailfb390c.ts.net:8443/status.php | python3 -m json.tool
```
Expected fields:
- `installed: true`
- `maintenance: false`
- `needsDbUpgrade: false`
Last verified version after the update/backup run:
- `version`: `33.0.6.2`
- `versionstring`: `33.0.6`
Post datadir migration verification (2026-08-11):
- `version`: `33.0.7.1`
- `versionstring`: `33.0.7`
- `installed: true`, `maintenance: false`, `needsDbUpgrade: false`
- ncdata bind source: `/mnt/nextcloud-data`
- local + tailnet `:8443` `status.php` HTTP 200
## Manual backup procedure
AIO blocks direct admin login while `nextcloud-aio-apache` is running. For CLI-triggered backup operations, stop Apache first to unblock the local AIO panel login.
1. Stop Apache temporarily:
```bash
docker stop nextcloud-aio-apache
```
2. Authenticate to AIO and trigger a manual backup through the AIO route `POST /api/docker/backup`.
Operational notes:
- Read the AIO password through the mastercontainer, not via host `sudo`:
```bash
AIO_PASS=$(docker exec nextcloud-aio-mastercontainer python3 -c "import json; print(json.load(open('/mnt/docker-aio-config/data/configuration.json'))['password'])")
```
- Use the CSRF values from the AIO login/admin pages.
- The manual backup endpoint is `https://127.0.0.1:8080/api/docker/backup`.
- AIO stops the core stack while the BorgBackup container runs.
3. Monitor backup completion:
```bash
docker ps -a --format 'table {{.Names}}\t{{.Status}}' | grep nextcloud-aio-borgbackup
docker logs nextcloud-aio-borgbackup --tail=120
```
Success criteria:
- `nextcloud-aio-borgbackup` exits with code `0`.
- Logs include `Backup finished successfully`.
- `/data/backups/borg` exists and contains Borg repository files.
## Last successful backup evidence
Manual backup after datadir + Docker root migration completed successfully.
- Archive name: `20260811_013544-nextcloud-aio`
- Completion time: `11.08.2026 - 01:36:36`
- Duration: `00 hours 00 minutes 52 seconds`
- Borg summary after prune/compact: all archives original `3.27 GB`, compressed `1.13 GB`, deduplicated `751.73 MB`
- AIO list entries:
  - `20260717_000110-nextcloud-aio,2026-07-17 00:01:10`
  - `20260811_013544-nextcloud-aio,2026-08-11 01:35:45`
Prior baseline backup (pre-migration):
- Archive name: `20260717_000110-nextcloud-aio`
- Archive fingerprint: `5a953c068dba1b01417abe3a9376a7d7e75285e5e5cf0d0ad5e50c4c12b2834a`
- Original size: `1.63 GB`
- Compressed size: `574.12 MB`
- Deduplicated size: `490.21 MB`
- Completion time: `17.07.2026 - 00:02:27`
- Duration: `00 hours 01 minutes 17 seconds`
Repository path:
```bash
/data/backups/borg
```
## Backup test mode caveat
The AIO `POST /api/docker/backup-test` route expects an existing Borg repository at `/data/backups/borg`.
On a brand-new empty backup directory, `backup-test` can fail with:
```text
No 'borg' directory in the given backup directory found!
```
For first-time setup, run the full manual backup first. After `/data/backups/borg` exists, use AIO's check/test operations.
## Service recovery after backup
After backup completion, restart the AIO stack from the AIO interface or API. If manual recovery is needed:
```bash
docker start nextcloud-aio-database nextcloud-aio-redis
docker start nextcloud-aio-nextcloud
docker start nextcloud-aio-apache
```
Then verify:
```bash
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep nextcloud-aio
curl -sk http://127.0.0.1:11000/status.php | python3 -m json.tool
curl -sk https://wera-ss-pt-sn-1.tailfb390c.ts.net:8443/status.php | python3 -m json.tool
```
## Known AIO log-level caveat
During the 2026-07-17 backup/update run, current AIO child images expected `ENV_AIO_LOG_LEVEL` in their supervisor/PostgreSQL configs, but AIO did not pass that variable into all child containers.
Observed symptoms:
- PostgreSQL generated `log_min_messages =` with an empty value and failed to start.
- Nextcloud's `/supervisord.conf` referenced `%(ENV_AIO_LOG_LEVEL)s` and failed when the env var was missing.
Applied recovery:
- Recreated `nextcloud-aio-mastercontainer` with supported `AIO_LOG_LEVEL=warn`.
- Recreated/started PostgreSQL with `AIO_LOG_LEVEL=warn`; resulting config line is `log_min_messages = warning`.
- Patched `nextcloud-aio-nextcloud:/supervisord.conf` to use `loglevel=warn`.
Important: this in-container supervisor patch may be lost if AIO recreates the Nextcloud child container. If Nextcloud fails with a missing `ENV_AIO_LOG_LEVEL` error after a future AIO update, reapply the patch or wait for an upstream AIO image fix.
## TRL5 Talk integration
TRL4 OpenFang is registered in the Talk app on TRL5.
- TRL5 Nextcloud: `wera-ss-pt-tv-1.tailfb390c.ts.net`
- Bot name: `TRL4 City Agent`
- Bot ID: `1`
- Room: `City of Light Ops`
- Room token: `rkc9y36g`
- Webhook URL: `https://wera-ss-pt-sn-1.tailfb390c.ts.net:4200/nextcloud-talk-webhook`
## Gitea wiki publication
The same runbook was published to the local Gitea wiki repository:
- Repository: `wera-global/solarseed-v3.wiki.git`
- Page: `Nextcloud-AIO-Operations.md`
- Commit: `87801b6cac5ceb53730de522783a2013af8e1daf`
- Author: `WARP <warp@wera.global>`
## Recovery event: 2026-07-25
- All AIO child containers had stopped ~6 days prior while the mastercontainer remained running.
- Recovery action: started containers in dependency order via `docker start` (mastercontainer API not used because containers and config were already intact).
- Verified state after recovery:
  - All core AIO containers `Up` and `healthy`.
  - `status.php` returns `installed: true`, `maintenance: false`, `needsDbUpgrade: false` on both `http://127.0.0.1:11000` and `https://wera-ss-pt-sn-1.tailfb390c.ts.net:8443`.
  - Apache binding remains `127.0.0.1:11000` only; LAN check to `192.168.1.71:11000` returns `000`.
- Prometheus now scrapes `nextcloud-aio-nextcloud-exporter:9205`:
  - Added job to `/data/city-of-light/prometheus.yml`.
  - Attached `col-prometheus` to the `nextcloud-aio` Docker network in `/data/city-of-light/docker-compose.yml` so DNS resolves.
  - Verified target `up` in Prometheus.
- Evidence saved to `ops/evidence/nextcloud_aio_refresh_20260725T000829Z/`.

## Nextcloud app layer (2026-08-18)
The following NC apps are installed and configured:
- `filantropia_solar` 3.2.31 -- from FilantropiaSolar repo `custom_apps/`; configured with Prometheus + Spirit endpoints.
- `integration_openai` 4.5.2 -- API URL `http://col-llama-cpp:8081` (Bonsai-4B-Q1_0 model via GPU).
- `assistant` 3.5.0 -- enabled, backed by integration_openai.
- `files_antivirus` 6.4.0 -- daemon mode, host `nextcloud-aio-clamav:3310`, delete on infection.
- `external` 8.0.1 -- sidebar links: Spirit, Prometheus, Cityview.
- LLM bridge: `col-llama-cpp` connected to `nextcloud-aio` network (persisted in host compose `nextcloud-aio:` entry on llama-cpp service).

Users provisioned: `admin`, `Chris`, `FilantropiaSolar`, `mr.mike`, `nash`, `eric@viso.space`.
Groups: `FilantropiaSolarAdmin`, `admin`.
Passwords at `/data/.secrets/nc-user-passwords/` on TRL4 host.

## Verification results (2026-08-18)
Full functional check passed. Evidence:

| Check | Result |
|-------|--------|
| `status.php` (loopback) | `installed: true`, `maintenance: false`, `needsDbUpgrade: false`, v33.0.7.1 |
| `status.php` (tailnet `:8443`) | same |
| All AIO containers | healthy (13/13) incl. ClamAV |
| `filantropia_solar` 3.2.31 | enabled |
| `integration_openai` 4.5.2 | enabled; url=`http://col-llama-cpp:8081`; model=`Bonsai-4B-Q1_0` |
| `assistant` 3.5.0 | enabled |
| `files_antivirus` 6.4.0 | enabled; daemon mode; host=`nextcloud-aio-clamav`; port=3310 |
| `external` 8.0.1 | enabled |
| LLM reachable from NC container | `{"status":"ok"}` |
| ClamAV PING from NC container | `PONG` (clamd responding on port 3310) |
| Prometheus targets | cadvisor, nextcloud-exporter, node-exporter, prometheus, spirit — all `up` |
| Users | admin, Chris, FilantropiaSolar, eric@viso.space, mr.mike, nash |
| Groups | FilantropiaSolarAdmin (FilantropiaSolar), admin (admin, mr.mike, nash) |
| `filantropia_solar` endpoints | prometheus=`http://col-prometheus:9090`, spirit=`http://col-spirit:9105` |

## Manual steps required
Two items require browser access or a working TTY — they cannot be triggered reliably via CLI.

### Step 1: Borg backup (REQUIRED before user data grows)
`occ talk:room:create` hangs in NC 33 / spreed 23; use the web UI.

1. SSH to Frank: `ssh wera@100.82.194.96`
2. Stop Apache (required to unblock AIO admin panel):
```bash
docker stop nextcloud-aio-apache
```
3. Open the AIO admin panel in a browser on the **local network or via Tailscale**: `https://wera-ss-pt-sn-1.tailfb390c.ts.net:8080` (or `https://192.168.1.71:8080` on LAN). Accept the self-signed cert.
4. Log in with the AIO password:
```bash
# Read password (do not echo it; paste directly into browser)
docker exec nextcloud-aio-mastercontainer python3 -c "import json; print(json.load(open('/mnt/docker-aio-config/data/configuration.json'))['password'])"
```
5. In the AIO panel: click **Create backup** / **Backup** button.
6. Monitor progress — the `nextcloud-aio-borgbackup` container will appear and exit 0 on success. Check:
```bash
docker logs nextcloud-aio-borgbackup --tail=30
```
7. Restart Apache after backup completes:
```bash
docker start nextcloud-aio-apache
```
8. Verify NC is back:
```bash
curl -sk http://127.0.0.1:11000/status.php | python3 -m json.tool
```
9. Record the new archive name (shown in AIO panel or borgbackup logs) in `ops/NEXTCLOUD_AIO_TRL4.md` under "Last successful backup evidence".

### Step 2: Create "City of Light Ops" Talk room
1. Log in to NC as admin at `https://wera-ss-pt-sn-1.tailfb390c.ts.net:8443`
2. Open the **Talk** app (left sidebar).
3. Click **+** > **New group conversation** > name it `City of Light Ops`.
4. Add members: `admin`, `mr.mike`, `nash`, `FilantropiaSolar`.
5. After creation, note the room token (visible in the URL: `.../call/<token>`) and record it here.
6. Optionally: promote `mr.mike` and `nash` to moderators.

### Step 3: Optional — full-text search
Requires ~2 GB additional RAM (Elasticsearch/OpenSearch). Current headroom: ~12 GB free.
- Enable via AIO admin panel: toggle **Fulltextsearch** under "Optional containers".
- Then install NC apps: `occ app:install fulltextsearch files_fulltextsearch fulltextsearch_elasticsearch`
- Run initial index: `occ fulltextsearch:index`

## Remaining follow-ups (post-verification)
- Create Talk room (Step 2 above).
- Optional: full-text search (Step 3 above).

## filantropia_solar deployment note
When packaging from macOS with `tar`, resource fork files (`._*`) are included by default. These are silently extracted on Linux and NC tries to autoload them as PHP controller classes, causing a 500 on every page.

**Symptom**: `ReflectionException: Class "OCA\FilantropiaSolar\Controller\._EnergyApiController" does not exist` in `nextcloud.log`; `/login` returns HTTP 500.

**Fix (applied 2026-08-18)**:
```bash
# Remove existing dotfiles without full reinstall:
docker exec nextcloud-aio-nextcloud find /var/www/html/custom_apps/filantropia_solar -name '._*' -delete
docker exec -u www-data nextcloud-aio-nextcloud php occ maintenance:repair --include-expensive
```
**Prevention** — always set `COPYFILE_DISABLE=1` when creating the tarball on macOS:
```bash
COPYFILE_DISABLE=1 tar --exclude='node_modules' --exclude='.git' \
  --exclude='._*' --exclude='.DS_Store' \
  -czf filantropia_solar.tar.gz nextcloud-app
```

## Final status snapshot (2026-08-18 ~13:20 UTC)
- **Borg backup**: completed successfully at `13:18:37 UTC`.
  - Archive: `20260818_131837-nextcloud-aio` (estimated name from timestamp; AIO log confirmed `Backup finished successfully`).
  - Duration: 23 seconds. Repo at `/data/backups/borg`.
  - Previous archives retained per prune policy (`--keep-within=7d --keep-weekly=4 --keep-monthly=6`).
- **Office suite**: AIO panel session switched from Collabora to **EuroOffice** (`nextcloud-aio-eurooffice`, healthy). Collabora exited (70).
- **All containers**: 14 running and healthy.
- **NC**: `installed: true`, `maintenance: false`, `needsDbUpgrade: false`, v33.0.7.1.
- **Apache**: loopback-only `127.0.0.1:11000`; tailnet `:8443` reachable.
- **Tailnet serve**: `/` → Odoo :8069, `:8443` → NC :11000, `:4200` → OpenFang.
- **Outstanding**: Talk room creation (web UI) and optional full-text search.
