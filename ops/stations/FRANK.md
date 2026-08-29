# SolarSeed Station "Frank" (TRL4 Lab)

Station callsign: **Frank**
Role: City of Light TRL4 lab host (grid power, full stack validation)
Hostname: `wera-ss-pt-sn-1`
Tailscale FQDN: `wera-ss-pt-sn-1.tailfb390c.ts.net`
Document status: live snapshot **2026-08-29** (post containerd migration recovery)

Related:
- `ops/RUNBOOK.md` — day-2 ops including containerd migration section
- SolarCity `docs/Research/CITY_OF_LIGHT_TRL4_RESEARCH_REPORT.md` — TRL4 research + Appendix A
- `WARP.md` — agent operational guide

---

## Identity and access

| Field | Value |
|-------|--------|
| Station name | Frank |
| Stage | TRL4 (lab) |
| Hostname | `wera-ss-pt-sn-1` |
| Operator account | `wera` |
| LAN | `192.168.1.71` |
| Tailscale IPv4 | `100.82.194.96` |
| SSH (LAN) | `ssh wera@192.168.1.71` |
| SSH (tailnet) | `ssh wera@wera-ss-pt-sn-1.tailfb390c.ts.net` |

---

## Storage architecture (current)

| Mount | Role |
|-------|------|
| `/` (`/dev/sdb7` ext4 ~93G) | OS, packages, logs only |
| `/data` (`data_crypt`) | City configs, secrets, light binds |
| `/data-bulk` (`data_bulk`) | Docker data-root **and** containerd root |
| `/mnt/nextcloud-data` (`nextcloud_data`) | Nextcloud AIO datadir |

### Container runtime paths (mandatory pair)

| Runtime | Config file | Path |
|---------|-------------|------|
| Docker Engine | `/etc/docker/daemon.json` | `"data-root": "/data-bulk/docker"` |
| containerd | `/etc/containerd/config.toml` | `root = "/data-bulk/containerd"` |

### systemd mount guard for containerd

File: `/etc/systemd/system/containerd.service.d/20-data-bulk-mount-guard.conf`

```ini
[Unit]
ConditionPathIsMountPoint=/data-bulk
RequiresMountsFor=/data-bulk
```

**Never** use `Requires=data-bulk.mount`. systemd unit for `/data-bulk` is `data\x2dbulk.mount`.

### Incident history (2026-08-26 → 2026-08-29)

1. Root filled; investigation found ~50 GiB still in `/var/lib/containerd` after Docker data-root move.
2. Data copied to `/data-bulk/containerd` and config updated.
3. Incorrect drop-in `Requires=data-bulk.mount` prevented containerd start; Docker remained `activating`.
4. Drop-in corrected to `RequiresMountsFor=/data-bulk` on 2026-08-29; containerd + Docker recovered; City/Nextcloud containers healthy.
5. Old `/var/lib/containerd` tree cleaned after healthy validation to reclaim root space.

### Validation commands

```bash
systemctl is-active containerd docker
docker info --format 'Root={{.DockerRootDir}}'
grep -E '^root' /etc/containerd/config.toml
docker ps
df -h / /data-bulk
sudo du -sh /data-bulk/containerd /var/lib/containerd
```

Expected:
- both services `active`
- Docker RootDir `/data-bulk/docker`
- containerd root `/data-bulk/containerd`
- `/var/lib/containerd` empty or near-empty after cleanup
- `/` well under 80% with ≥20 GiB free for TRL4 preflight
