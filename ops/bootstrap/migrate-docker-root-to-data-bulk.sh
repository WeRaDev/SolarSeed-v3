#!/bin/bash
# Migrate Docker data-root from /var/lib/docker (on /) to /data-bulk/docker (LUKS city bulk).
set -euo pipefail

NEW_ROOT=/data-bulk/docker
OLD_ROOT=/var/lib/docker
DAEMON_JSON=/etc/docker/daemon.json
BACKUP_SUFFIX=$(date -u +%Y%m%dT%H%M%SZ)

echo "=== Preflight ==="
mountpoint -q /data-bulk || { echo "FATAL: /data-bulk not mounted"; exit 2; }
df -hT / /data-bulk
docker info --format 'Root={{.DockerRootDir}} Driver={{.Driver}}' || true
ROOT_NOW=$(docker info --format '{{.DockerRootDir}}' 2>/dev/null || echo unknown)
if [ "$ROOT_NOW" = "$NEW_ROOT" ]; then
  echo "Already using $NEW_ROOT"
  docker info --format 'Root={{.DockerRootDir}}'
  df -hT / /data-bulk
  exit 0
fi

mkdir -p "$NEW_ROOT"
# Ensure empty-ish target (allow only empty or previous incomplete sync)
if [ -d "$NEW_ROOT" ] && [ "$(ls -A "$NEW_ROOT" 2>/dev/null | wc -l | tr -d ' ')" -gt 0 ]; then
  if [ -f "$NEW_ROOT/.solarseed-docker-root-ready" ]; then
    echo "Target already marked ready; will reconfigure daemon only if needed"
  else
    echo "WARN: $NEW_ROOT not empty; will rsync --delete into it after docker stop"
  fi
fi

echo "=== Record container inventory ==="
docker ps -a --format '{{.Names}} {{.Status}}' | tee /root/docker-ps-before-migrate-$BACKUP_SUFFIX.txt >/dev/null || true
docker info > /root/docker-info-before-migrate-$BACKUP_SUFFIX.txt 2>&1 || true

echo "=== Stop Docker (containers will stop) ==="
systemctl stop docker.socket docker.service || systemctl stop docker
# containerd often needed stopped for clean root move on debian
systemctl stop containerd || true
sleep 2
if pgrep -x dockerd >/dev/null; then
  echo "FATAL: dockerd still running"; pgrep -a docker; exit 3
fi

echo "=== Rsync $OLD_ROOT -> $NEW_ROOT ==="
# Preserve ACLs/xattrs where available
if command -v rsync >/dev/null; then
  rsync -aHAX --numeric-ids --info=progress2 "$OLD_ROOT"/ "$NEW_ROOT"/
else
  tar -C "$OLD_ROOT" -cf - . | tar -C "$NEW_ROOT" -xf -
fi
touch "$NEW_ROOT/.solarseed-docker-root-ready"
echo "sync complete"
du -sh "$OLD_ROOT" "$NEW_ROOT" || true
df -hT /data-bulk /

echo "=== Write daemon.json data-root ==="
mkdir -p /etc/docker
if [ -f "$DAEMON_JSON" ]; then
  cp -a "$DAEMON_JSON" "${DAEMON_JSON}.bak.$BACKUP_SUFFIX"
  # merge data-root with python
  python3 - <<PY
import json, pathlib
p=pathlib.Path("$DAEMON_JSON")
try:
    data=json.loads(p.read_text() or "{}")
except Exception:
    data={}
if not isinstance(data, dict):
    data={}
data["data-root"]="$NEW_ROOT"
p.write_text(json.dumps(data, indent=2) + "\n")
print(p.read_text())
PY
else
  cat > "$DAEMON_JSON" <<JSON
{
  "data-root": "$NEW_ROOT"
}
JSON
  cat "$DAEMON_JSON"
fi

echo "=== Move aside old root (keep backup) ==="
if [ -d "${OLD_ROOT}.pre-data-bulk-$BACKUP_SUFFIX" ]; then
  echo "backup path exists already"
else
  mv "$OLD_ROOT" "${OLD_ROOT}.pre-data-bulk-$BACKUP_SUFFIX"
fi
# leave a placeholder so nothing accidental writes there before start
mkdir -p "$OLD_ROOT"
# optional stub readme
echo "Docker data-root moved to $NEW_ROOT on $BACKUP_SUFFIX. Old tree: ${OLD_ROOT}.pre-data-bulk-$BACKUP_SUFFIX" > "$OLD_ROOT/README-MOVED.txt"

echo "=== Start containerd + docker ==="
systemctl start containerd || true
systemctl start docker
sleep 3
systemctl is-active docker
docker info --format 'Root={{.DockerRootDir}} Driver={{.Driver}} Containers={{.ContainersRunning}}/{{.Containers}}'

NEW_CHECK=$(docker info --format '{{.DockerRootDir}}')
if [ "$NEW_CHECK" != "$NEW_ROOT" ]; then
  echo "FATAL: Docker root is $NEW_CHECK expected $NEW_ROOT"
  exit 4
fi

echo "=== Wait for containers to come back (restart policies) ==="
for i in $(seq 1 36); do
  running=$(docker ps -q | wc -l | tr -d ' ')
  total=$(docker ps -aq | wc -l | tr -d ' ')
  echo "t=$((i*5))s running=$running total=$total"
  # Nextcloud + city core sample
  nc=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' nextcloud-aio-nextcloud 2>/dev/null || echo missing)
  ap=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' nextcloud-aio-apache 2>/dev/null || echo missing)
  pr=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' col-prometheus 2>/dev/null || echo missing)
  echo "  nc=$nc ap=$ap prom=$pr"
  if [ "$running" -ge 15 ] && [ "$nc" = "healthy" ] && [ "$ap" = "healthy" ]; then
    break
  fi
  sleep 5
done

echo "=== Post status ==="
docker ps -a --format 'table {{.Names}}\t{{.Status}}' | head -n 50
df -hT / /data-bulk
docker system df || true

# quick HTTP probes
for url in http://127.0.0.1:11000/status.php http://127.0.0.1:9105/health http://127.0.0.1:9090/-/healthy http://127.0.0.1:4200/api/health; do
  code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 8 "$url" || echo err)
  echo "$code $url"
done
curl -sk --max-time 10 http://127.0.0.1:11000/status.php | head -c 250; echo

echo "=== SUCCESS: Docker data-root is $NEW_CHECK ==="
echo "Old tree kept at ${OLD_ROOT}.pre-data-bulk-$BACKUP_SUFFIX — delete only after multi-day stability"
