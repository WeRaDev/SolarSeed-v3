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

## 7) Post-remediation operational state (2026-07-05)
- `openipmi.service` is intentionally `masked` and `inactive` on this host (no `/dev/ipmi*` BMC device path present).
- Tailscale operator user is set to `wera-admin`.
- Tailnet HTTPS endpoint `https://wera-ss-pt-tv-1.tailfb390c.ts.net` is served via persisted Tailscale serve state:
  - `/` -> `http://127.0.0.1:11000` (Nextcloud Apache)
- `tailscale-serve-nextcloud.service` is intentionally `disabled` to avoid boot-time false failures while preserving working tailnet serve state.
- Post-reboot verification result (2026-07-05):
  - `systemctl --failed` returned no failed units.
  - Docker health remained `16 healthy`, `2 no-healthcheck`.

## 8) Nextcloud LocalAI (restored 2026-08-16)
- Role: local OpenAI-compatible backend for Nextcloud `integration_openai` + `assistant` (chat + STT)
- Container: `nextcloud-aio-local-ai`
- Image: `ghcr.io/docjyj/aio-local-ai-vulkan:v1`
- Network: `nextcloud-aio`
- Address: container `:10078`; host bind `127.0.0.1:10078`
- Health: `HEALTHCHECK_ENDPOINT=http://localhost:10078/readyz` (aligned with listen port)
- NC endpoint: `http://nextcloud-aio-local-ai:10078`
- Default models in NC app config:
  - completion: `llama-3.2-1b-instruct:q4_k_m`
  - STT/speech: `whisper-1`
- Backend volume contents required for function:
  - `llama-cpp`, `vulkan-llama-cpp`
  - `whisper`, `vulkan-whisper`
- Volumes: `nextcloud_aio_localai_models`, `nextcloud_aio_localai_backends`, `nextcloud_aio_localai_configuration`
- Operator notes: see `ops/RUNBOOK.md` section "TRL5 Nextcloud LocalAI restore (2026-08-16)"
- Related notes outside LocalAI path:
  - Outbound mail uses Proton Bridge + docker-gateway SMTP proxy; see RUNBOOK section "TRL5 outbound email"
  - `nextcloud-aio-vaultwarden` previously observed stopped long-term (not part of LocalAI path)
  - AIO mastercontainer upgrade can drop the in-container `local-ai.json` HEALTHCHECK patch; re-check after upgrades

## 9) Outbound email / Proton Bridge (verified 2026-08-16)
- Purpose: transactional SMTP for Nextcloud AIO + Odoo (`filantropia-odoo`)
- Verified: NC email test OK; Odoo Test Connection OK; Odoo user invitation OK
- Bridge: host user `protonmail`, systemd `protonmail.service` -> tmux session `protonmail`
- Bridge mailbox / SMTP auth user: `cloud@wera.global`
- Bridge listen: `127.0.0.1:1025` (SMTP STARTTLS), `127.0.0.1:1143` (IMAP)
- Docker proxy: `protonmail-smtp-docker-proxy.service` (`/usr/local/sbin/protonmail-smtp-docker-proxy.sh`)
  - Binds `172.18.0.1:1025` and `172.19.0.1:1025` only (not public / Tailscale)
- App SMTP target: `172.18.0.1:1025`
  - Nextcloud: `mail_smtpsecure=tls` + self-signed streamoptions; from `cloud@wera.global`
  - Odoo outgoing server: `Proton Bridge (host via docker gw)` (`starttls` / `login`, `from_filter=wera.global`)
- Odoo identity: company + OdooBot + Administrator use `cloud@wera.global`; alias domain `wera.global` with bounce/catchall/default_from all `cloud` (Bridge rejects non-mailbox return-paths)
- Secrets: never in Git; optional host file `/root/.secrets/proton-bridge-smtp.env` (mode 600) after Bridge `info 0`
- Operator dependency: Bridge account index `0` (`Tomás Crespim`) must be **connected** (`login 0` + 2FA). Signed-out/locked Bridge rejects AUTH (`454`) or send
- Runbook: `ops/RUNBOOK.md` "TRL5 outbound email (Nextcloud + Odoo via Proton Bridge)"
- Filantropia pointer: FilantropiaSolar `docs/ops/TRL5-NC-ACCESS.md`

