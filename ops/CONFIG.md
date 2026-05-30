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

