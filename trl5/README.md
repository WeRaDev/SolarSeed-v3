# TRL5 Branch Working Notes
Use branch `trl5` for field pilot machine updates and validation.
## Current TRL5 machine profile (validated 2026-05-30)
- Host: `wera-ss-pt-tv-1`
- Tailscale: `wera-ss-pt-tv-1.tailfb390c.ts.net` (`100.82.252.18`)
- Operator user: `wera-admin` (in `docker` group)
- OS: Debian 13 (trixie), kernel `6.12.57+deb13-amd64`
- CPU: AMD Ryzen 7 6800H (16 vCPU)
- RAM: 27 GiB class; swap ~29 GiB
- Root storage: NVMe ext4 (`/dev/nvme0n1p2`, ~910G total, ~15-17% used)
- `/data` mount is not present on this machine baseline
## Current runtime status baseline (2026-05-30)
- Docker engine active and accessible to `wera-admin` without sudo.
- Running containers: 18 total (Nextcloud AIO centered stack).
- Health state: 16 `healthy`, 2 running without Docker healthcheck (`nextcloud-aio-nextcloud-exporter`, `nextcloud-aio-fail2ban`).
- Publicly bound container ports currently include `80`, `8080`, `8443`, and `3478/tcp+udp`.
## Typical TRL5 change set
- machine configuration updates in `compose/`, `ops/`, `prometheus/`, `alertmanager/`, `rundeck/`
- TRL5-specific constraints (solar budget, network availability, fallback behavior) documented in `ops/RUNBOOK.md`
## Before push
1. `docker compose -f compose/docker-compose.yml config --quiet`
2. run TRL5 machine smoke checks and connectivity checks from `ops/RUNBOOK.md`
3. document rollback path and previous stable commit/tag
