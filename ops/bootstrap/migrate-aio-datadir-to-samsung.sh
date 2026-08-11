#!/bin/bash
# Migrate Nextcloud AIO datadir from Docker volume nextcloud_aio_nextcloud_data
# to host path /mnt/nextcloud-data (Samsung LUKS). Recreates mastercontainer with
# NEXTCLOUD_DATADIR and starts the stack via AIO API.
set -euo pipefail

TARGET="${NEXTCLOUD_DATADIR_TARGET:-/mnt/nextcloud-data}"
OLD_VOL=nextcloud_aio_nextcloud_data
MASTER=nextcloud-aio-mastercontainer
IMAGE=nextcloud/all-in-one:latest
NETWORK=city-of-light
COOKIE_JAR=/tmp/aio_migrate_cookies.txt

echo "=== Preflight ==="
mountpoint -q "$TARGET" || { echo "FATAL: $TARGET not mounted"; exit 2; }
docker inspect "$MASTER" >/dev/null
df -hT "$TARGET" /

echo "=== Stop AIO children ==="
mapfile -t CHILDREN < <(docker ps -a --format '{{.Names}}' | grep '^nextcloud-aio-' | grep -v "^${MASTER}$" || true)
if [ "${#CHILDREN[@]}" -gt 0 ]; then
  docker stop "${CHILDREN[@]}" || true
fi
docker ps -a --filter name=nextcloud-aio --format 'table {{.Names}}\t{{.Status}}'

echo "=== Rsync volume -> ${TARGET} ==="
docker run --rm \
  -v "${OLD_VOL}:/from:ro" \
  -v "${TARGET}:/to:rw" \
  alpine sh -c 'apk add --no-cache rsync >/dev/null && rsync -aHAX --delete /from/ /to/ && du -sh /to && ls -la /to | head'

echo "=== chown 33:0 / chmod 750 ==="
docker run --rm -v "${TARGET}:/mnt/ncdata:rw" alpine \
  sh -c 'chown -R 33:0 /mnt/ncdata && chmod -R 750 /mnt/ncdata && ls -lan /mnt/ncdata | head'

echo "=== Capture master publish ports ==="
PUBLISH_ARGS=()
while read -r host_ip host_port cont; do
  [ -z "${host_port:-}" ] && continue
  if [ -n "${host_ip:-}" ] && [ "$host_ip" != "0.0.0.0" ] && [ "$host_ip" != "::" ]; then
    PUBLISH_ARGS+=(--publish "${host_ip}:${host_port}:${cont}")
  else
    PUBLISH_ARGS+=(--publish "${host_port}:${cont}")
  fi
done < <(docker inspect "$MASTER" --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if $conf}}{{range $conf}}{{.HostIp}} {{.HostPort}} {{$p}}{{println}}{{end}}{{end}}{{end}}')
if [ "${#PUBLISH_ARGS[@]}" -eq 0 ]; then
  PUBLISH_ARGS=(--publish 127.0.0.1:8080:8080)
fi
echo "Publish: ${PUBLISH_ARGS[*]}"

echo "=== Recreate mastercontainer ==="
docker stop "$MASTER"
docker rm "$MASTER"
docker run \
  --init \
  --sig-proxy=false \
  --name "$MASTER" \
  --restart always \
  "${PUBLISH_ARGS[@]}" \
  --network "$NETWORK" \
  --volume nextcloud_aio_mastercontainer:/mnt/docker-aio-config \
  --volume /var/run/docker.sock:/var/run/docker.sock:ro \
  -e APACHE_PORT=11000 \
  -e APACHE_IP_BINDING=127.0.0.1 \
  -e AIO_LOG_LEVEL=warn \
  -e "NEXTCLOUD_DATADIR=${TARGET}" \
  -d \
  "$IMAGE"

for i in $(seq 1 40); do
  code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 3 https://127.0.0.1:8080/ || true)
  echo "aio_http=$code"
  [ "$code" != "000" ] && break
  sleep 2
done

echo "=== AIO login + start containers ==="
export AIO_PASS
AIO_PASS=$(docker exec "$MASTER" python3 -c "import json; print(json.load(open('/mnt/docker-aio-config/data/configuration.json'))['password'])")
rm -f "$COOKIE_JAR"

curl -sk -c "$COOKIE_JAR" -b "$COOKIE_JAR" --max-time 20 https://127.0.0.1:8080/ > /tmp/aio_root.html
curl -sk -c "$COOKIE_JAR" -b "$COOKIE_JAR" --max-time 20 https://127.0.0.1:8080/login > /tmp/aio_login.html

login_code=$(python3 <<'PY'
import json, os, subprocess
password = os.environ["AIO_PASS"]
cookie = "/tmp/aio_migrate_cookies.txt"
payload = json.dumps({"password": password})
r = subprocess.run([
  "curl","-sk","-c",cookie,"-b",cookie,"--max-time","20",
  "-X","POST","https://127.0.0.1:8080/api/auth/login",
  "-H","Content-Type: application/json",
  "-d",payload,"-o","/tmp/aio_login_api.json","-w","%{http_code}"
], capture_output=True, text=True)
print(r.stdout.strip() or "000")
PY
)
echo "login_http=$login_code"

curl -sk -c "$COOKIE_JAR" -b "$COOKIE_JAR" --max-time 20 \
  https://127.0.0.1:8080/containers > /tmp/aio_containers.html || true

CSRF=$(python3 <<'PY'
import re, pathlib
texts=[]
for p in ['/tmp/aio_containers.html','/tmp/aio_root.html','/tmp/aio_login.html','/tmp/aio_login_api.json']:
  try:
    texts.append(pathlib.Path(p).read_text(errors='ignore'))
  except Exception:
    pass
blob='\n'.join(texts)
patterns=[
  r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']',
  r'["\']csrfToken["\']\s*:\s*["\']([^"\']+)["\']',
  r'["\']csrf_token["\']\s*:\s*["\']([^"\']+)["\']',
  r'X-CSRF-TOKEN["\']?\s*[:=]\s*["\']([^"\']+)["\']',
]
for p in patterns:
  m=re.search(p, blob, re.I)
  if m:
    print(m.group(1))
    raise SystemExit
try:
  jar=pathlib.Path('/tmp/aio_migrate_cookies.txt').read_text(errors='ignore')
  m=re.search(r'csrf[^\t ]*\t([^\n\r]+)', jar, re.I)
  if m:
    print(m.group(1).strip())
except Exception:
  pass
PY
)
echo "csrf_len=${#CSRF}"

start_code=$(curl -sk -c "$COOKIE_JAR" -b "$COOKIE_JAR" --max-time 60 \
  -X POST 'https://127.0.0.1:8080/api/docker/start' \
  -H 'Content-Type: application/json' \
  -H "requesttoken: ${CSRF}" \
  -H "X-CSRF-TOKEN: ${CSRF}" \
  -d '{}' -o /tmp/aio_start.json -w '%{http_code}' || true)
echo "start_http=$start_code"
python3 - <<'PY'
import pathlib
p=pathlib.Path('/tmp/aio_start.json')
if p.exists():
  print(p.read_text(errors='ignore')[:300])
PY

if [ "$start_code" != "200" ] && [ "$start_code" != "201" ] && [ "$start_code" != "204" ] && [ "$start_code" != "302" ]; then
  echo "WARN: primary start endpoint failed; trying form POST"
  curl -sk -c "$COOKIE_JAR" -b "$COOKIE_JAR" --max-time 60 \
    -X POST 'https://127.0.0.1:8080/api/docker/start' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "csrf_token=${CSRF}" \
    -o /tmp/aio_start2.json -w 'start2_http=%{http_code}\n' || true
fi

echo "=== Wait for healthy nextcloud+apache ==="
for i in $(seq 1 60); do
  names=$(docker ps --format '{{.Names}}' | grep '^nextcloud-aio-' | wc -l | tr -d ' ')
  nc=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' nextcloud-aio-nextcloud 2>/dev/null || echo missing)
  ap=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' nextcloud-aio-apache 2>/dev/null || echo missing)
  echo "t=$((i*5))s running_aio=$names nextcloud=$nc apache=$ap"
  if [ "$nc" = "healthy" ] && [ "$ap" = "healthy" ]; then
    break
  fi
  sleep 5
done

echo "=== Verify ==="
docker ps -a --filter name=nextcloud-aio --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
if ! docker inspect nextcloud-aio-nextcloud >/dev/null 2>&1; then
  echo "FATAL: nextcloud container missing; check AIO UI Start containers"
  docker logs "$MASTER" --tail 100 || true
  exit 6
fi

MOUNT_SRC=$(docker inspect nextcloud-aio-nextcloud --format '{{range .Mounts}}{{if eq .Destination "/mnt/ncdata"}}{{.Source}}{{end}}{{end}}')
echo "ncdata_source=$MOUNT_SRC"
docker inspect nextcloud-aio-nextcloud --format '{{json .Mounts}}' | python3 -m json.tool | head -n 80
docker exec --user www-data nextcloud-aio-nextcloud php occ config:system:get datadirectory
docker exec --user www-data nextcloud-aio-nextcloud php occ maintenance:mode --off || true
docker exec --user www-data nextcloud-aio-nextcloud php occ status
docker exec --user www-data nextcloud-aio-nextcloud php occ files:scan-app-data || true
docker exec --user www-data nextcloud-aio-nextcloud php occ files:scan --all || true

echo "=== HTTP status.php ==="
curl -sk --max-time 15 http://127.0.0.1:11000/status.php | python3 -m json.tool || true
curl -sk --max-time 15 https://wera-ss-pt-sn-1.tailfb390c.ts.net:8443/status.php | python3 -m json.tool || true

echo "=== Host target listing ==="
sudo ls -lan "$TARGET" | head -n 25
df -hT "$TARGET"

case "$MOUNT_SRC" in
  ${TARGET}|${TARGET}/) echo "PASS: ncdata bound to $TARGET" ;;
  *)
    echo "FAIL: expected ncdata source $TARGET, got '$MOUNT_SRC'"
    exit 5
    ;;
esac

unset AIO_PASS
echo "=== SUCCESS ==="
