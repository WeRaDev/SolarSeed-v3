# SolarSeed v3.1 — CONFIG (fill once)

IMPORTANT:
- Do not put secrets in Git.
- If you need to store secrets, put them in `compose/.env` (gitignored) and/or a password manager.

## 1) Host identity
- Hostname: wera-ss-pt-sn-1
- LAN IP (static or DHCP reservation): DHCP reservation → 192.168.1.71
- Preferred NIC: Wi‑Fi (Windows MAC: C0-4A-00-28-B3-FB)

## 2) Domain / TLS mode
Choose one:
- [x] (A) LAN-only (no public DNS)
- [ ] (B) Public domain + Let’s Encrypt

If (B):
- Domain name:
- Public DNS provider (optional):

## 3) Admin accounts (no passwords here)
- Nextcloud admin username: admin
- Nextcloud admin email: cloud@wera.global
- Rundeck admin username: admin
- Rundeck admin email: cloud@wera.global

## 4) Storage plan
- Data disk / device (e.g. /dev/sdb1): single physical disk (likely /dev/sda on Debian); dedicated /data partition TBD
- Data mountpoint (e.g. /data): /data
- Docker volumes strategy:
  - [ ] Docker managed volumes under /var/lib/docker
  - [ ] Bind mounts rooted at <mountpoint>/docker/
- Data partition encrypted?
  - [x] yes
  - [ ] no

## 5) Alert notification channel
Choose one (or more):
- [ ] Signal
- [x] Telegram
- [ ] Email (SMTP)
- [ ] Webhook

Details (IDs/addresses/endpoints; no API tokens here):
- Telegram: https://t.me/c/2208627521/4

## 6) Service ports (City of Light v3.1 baseline)
- Fortress (Nextcloud): 8080
- Nextcloud AIO admin: 8443
- Library (Prometheus): 9090
- Library (Alertmanager): 9093
- Factory (Rundeck): 4440
- Spirit: 9105
- OpenFang API/WebChat: 4200
- University (llama.cpp, optional): 8081
- House (PostgreSQL): 5432

