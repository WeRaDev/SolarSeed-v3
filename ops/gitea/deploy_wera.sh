#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-wera@192.168.1.71}"
REMOTE_DIR="${2:-/home/wera/gitea-stack}"
ADMIN_EMAIL="${3:-cloud@wera.global}"

echo "Preparing remote directories on ${HOST}..."
ssh "${HOST}" "mkdir -p '${REMOTE_DIR}' /home/wera/.secrets"

echo "Uploading compose artifact..."
scp "/Users/mikhailananyin/Documents/SolarSeed-v3/ops/gitea/docker-compose.host.yml" "${HOST}:${REMOTE_DIR}/docker-compose.host.yml"

echo "Generating secrets, configuring environment, and starting stack..."
ssh "${HOST}" "TS_BIN=\$(command -v tailscale || true); \
[ -z \"\${TS_BIN}\" ] && [ -x /usr/sbin/tailscale ] && TS_BIN=/usr/sbin/tailscale; \
[ -z \"\${TS_BIN}\" ] && [ -x /usr/bin/tailscale ] && TS_BIN=/usr/bin/tailscale; \
[ -z \"\${TS_BIN}\" ] && { echo 'tailscale binary not found on host PATH'; exit 1; }; \
TS_IP=\$(\${TS_BIN} ip -4 | head -n1); \
TS_DNS=\$(\${TS_BIN} status --self --json | jq -r '.Self.DNSName' | sed 's/\\.\$//'); \
if [ -f '${REMOTE_DIR}/.env' ]; then set -a; source '${REMOTE_DIR}/.env'; set +a; fi; \
if [ -f /home/wera/.secrets/gitea-admin.env ]; then set -a; source /home/wera/.secrets/gitea-admin.env; set +a; fi; \
[ -z \"\${GITEA_DB_PASSWORD:-}\" ] && GITEA_DB_PASSWORD=\$(openssl rand -base64 32 | tr -d '\\n'); \
[ -z \"\${GITEA_ADMIN_PASSWORD:-}\" ] && GITEA_ADMIN_PASSWORD=\$(openssl rand -base64 32 | tr -d '\\n'); \
[ -z \"\${GITEA_ADMIN_USERNAME:-}\" ] && GITEA_ADMIN_USERNAME=admin; \
[ -z \"\${GITEA_ADMIN_EMAIL:-}\" ] && GITEA_ADMIN_EMAIL='${ADMIN_EMAIL}'; \
cat > '${REMOTE_DIR}/.env' <<EOF
TAILSCALE_IP=\${TS_IP}
GITEA_DOMAIN=\${TS_DNS}
GITEA_DB_PASSWORD=\${GITEA_DB_PASSWORD}
GITEA_ADMIN_USERNAME=\${GITEA_ADMIN_USERNAME}
GITEA_ADMIN_EMAIL=\${GITEA_ADMIN_EMAIL}
GITEA_ADMIN_PASSWORD=\${GITEA_ADMIN_PASSWORD}
EOF
cat > /home/wera/.secrets/gitea-admin.env <<EOF
GITEA_URL=http://\${TS_DNS}:3000
GITEA_SSH=\${TS_DNS}:2222
GITEA_ADMIN_USERNAME=\${GITEA_ADMIN_USERNAME}
GITEA_ADMIN_EMAIL=\${GITEA_ADMIN_EMAIL}
GITEA_ADMIN_PASSWORD=\${GITEA_ADMIN_PASSWORD}
EOF
chmod 600 '${REMOTE_DIR}/.env' /home/wera/.secrets/gitea-admin.env; \
docker compose -f '${REMOTE_DIR}/docker-compose.host.yml' --env-file '${REMOTE_DIR}/.env' up -d"

echo "Waiting for Gitea health endpoint..."
ssh "${HOST}" "set -a; source '${REMOTE_DIR}/.env'; set +a; for i in \$(seq 1 60); do curl -fsS http://\${TAILSCALE_IP}:3000/api/healthz >/dev/null && exit 0; sleep 2; done; exit 1"

echo "Creating admin user (idempotent)..."
ssh "${HOST}" "set -a; source /home/wera/.secrets/gitea-admin.env; set +a; \
docker exec -u git col-gitea gitea admin user create \
  --username \"\${GITEA_ADMIN_USERNAME}\" \
  --password \"\${GITEA_ADMIN_PASSWORD}\" \
  --email \"\${GITEA_ADMIN_EMAIL}\" \
  --admin \
  --must-change-password=true || true"

echo "Validating deployment..."
ssh "${HOST}" "set -a; source '${REMOTE_DIR}/.env'; set +a; \
docker ps --format '{{.Names}}|{{.Status}}' | grep -E '^col-gitea(\\||-postgres\\|)'; \
curl -fsS http://\${TAILSCALE_IP}:3000/api/healthz >/dev/null; \
echo \"Gitea is reachable at http://\${GITEA_DOMAIN}:3000\"; \
echo \"Admin credentials are stored in /home/wera/.secrets/gitea-admin.env\""

echo "Done."
