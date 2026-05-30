# SolarSeed v3.1 — TRL5 CONFIG Snapshot (2026-05-30)
IMPORTANT:
- Do not put secrets in Git.
- Keep credentials only in `.secrets/` on host and/or password manager.
## 1) Host identity (TRL5 field machine)
- Hostname: `wera-ss-pt-tv-1`
- Tailscale FQDN: `wera-ss-pt-tv-1.tailfb390c.ts.net`
- Tailscale IPv4: `100.82.252.18`
- Primary operator account: `wera-admin`
- `wera-admin` Docker access: confirmed (`docker` group member, gid 989)
## 2) OS and hardware profile
- OS: Debian GNU/Linux 13 (trixie), `VERSION_ID=13`, `DEBIAN_VERSION_FULL=13.2`
- Kernel: `6.12.57+deb13-amd64`
- CPU: AMD Ryzen 7 6800H with Radeon Graphics
  - 16 vCPU (`Thread(s) per core: 2`, `Socket(s): 1`)
- Memory:
  - MemTotal: `28477788 kB` (~27 GiB)
  - MemAvailable at review: `~22 GiB`
  - SwapTotal: `29094908 kB` (~29 GiB), idle at review
## 3) Storage layout (observed)
- Root filesystem: `/dev/nvme0n1p2` (ext4)
  - Size: ~910G
  - Used at review: ~15-17%
- EFI partition: `/dev/nvme0n1p1` (vfat) mounted at `/boot/efi`
- `/data` mountpoint: not present on current TRL5 baseline
## 4) Runtime/software stack baseline
- Docker Engine: active
- Container platform focus: Nextcloud AIO stack
- Running containers: 18
  - Healthy: 16
  - Running without Docker healthcheck: 2 (`nextcloud-aio-nextcloud-exporter`, `nextcloud-aio-fail2ban`)
## 5) Network and exposed service ports (observed)
- Host listeners include: `22`, `80`, `443`, `8080`, `8443`, `9105`, `10000`
- Docker published ports include:
  - `0.0.0.0:80->80/tcp` (AIO mastercontainer)
  - `0.0.0.0:8080->8080/tcp` (AIO mastercontainer)
  - `0.0.0.0:8443->8443/tcp` (AIO mastercontainer)
  - `0.0.0.0:3478->3478/tcp+udp` (nextcloud-aio-talk)
  - `127.0.0.1:11000->11000/tcp` (nextcloud-aio-apache)
  - `127.0.0.1:9205->9205/tcp` (nextcloud-exporter)
## 6) Validation timestamp
- Last verified from operator workstation over Tailscale SSH: `2026-05-30`

