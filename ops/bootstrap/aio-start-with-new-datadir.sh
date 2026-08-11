#!/bin/bash
set -euo pipefail
MASTER=nextcloud-aio-mastercontainer
TARGET=/mnt/nextcloud-data
COOKIE=/tmp/aio_fix_cookies.txt
rm -f "$COOKIE"

echo "=== Confirm master env ==="
docker inspect "$MASTER" --format '{{range .Config.Env}}{{println .}}{{end}}' | grep NEXTCLOUD_DATADIR

echo "=== Remove old children so AIO recreates binds ==="
mapfile -t CHILDREN < <(docker ps -a --format '{{.Names}}' | grep '^nextcloud-aio-' | grep -v "^${MASTER}$" || true)
if [ "${#CHILDREN[@]}" -gt 0 ]; then
  docker rm -f "${CHILDREN[@]}" || true
fi
docker ps -a --filter name=nextcloud-aio --format 'table {{.Names}}\t{{.Status}}'

export AIO_PASS
AIO_PASS=$(docker exec "$MASTER" python3 -c 'import json; print(json.load(open("/mnt/docker-aio-config/data/configuration.json"))["password"])')

python3 <<'PY'
import os, re, subprocess, pathlib, urllib.parse
cookie = "/tmp/aio_fix_cookies.txt"
password = os.environ["AIO_PASS"]

def curl(args, out=None):
    cmd = ["curl","-sk","-c",cookie,"-b",cookie,"--max-time","30"] + args
    if out:
        cmd += ["-o", out, "-w", "%{http_code}"]
    return subprocess.run(cmd, capture_output=True, text=True)

r = curl(["https://127.0.0.1:8080/login"], out="/tmp/aio_login2.html")
print("login_page_http=", r.stdout.strip())
html = pathlib.Path("/tmp/aio_login2.html").read_text(errors="ignore")
name = re.search(r'name="csrf_name"\s+value="([^"]+)"', html)
val = re.search(r'name="csrf_value"\s+value="([^"]+)"', html)
if not name or not val:
    raise SystemExit("CSRF fields missing on login page")
csrf_name, csrf_value = name.group(1), val.group(1)
print("csrf_name=", csrf_name)
print("csrf_value_len=", len(csrf_value))

data = urllib.parse.urlencode({
    "password": password,
    "csrf_name": csrf_name,
    "csrf_value": csrf_value,
})
r = curl([
    "-X","POST","https://127.0.0.1:8080/api/auth/login",
    "-H","Content-Type: application/x-www-form-urlencoded",
    "-H","Accept: application/json",
    "--data", data,
], out="/tmp/aio_login_resp.json")
print("login_http=", r.stdout.strip())
print("login_body=", pathlib.Path("/tmp/aio_login_resp.json").read_text(errors="ignore")[:300])

r = curl(["https://127.0.0.1:8080/containers"], out="/tmp/aio_containers2.html")
print("containers_http=", r.stdout.strip())
html = pathlib.Path("/tmp/aio_containers2.html").read_text(errors="ignore")
names = re.findall(r'name="csrf_name"\s+value="([^"]+)"', html)
vals = re.findall(r'name="csrf_value"\s+value="([^"]+)"', html)
print("csrf_pairs", len(names), len(vals))
if names and vals:
    csrf_name, csrf_value = names[0], vals[0]
else:
    m = re.search(r'"csrf_name"\s*:\s*"([^"]+)".*?"csrf_value"\s*:\s*"([^"]+)"', html, re.S)
    if not m:
        # dump snippet for debug
        print(html[:1000])
        raise SystemExit("No CSRF on containers page")
    csrf_name, csrf_value = m.group(1), m.group(2)

for endpoint in [
    "https://127.0.0.1:8080/api/docker/start",
    "https://127.0.0.1:8080/api/docker/containers/start",
]:
    data = urllib.parse.urlencode({"csrf_name": csrf_name, "csrf_value": csrf_value})
    r = curl([
        "-X","POST", endpoint,
        "-H","Content-Type: application/x-www-form-urlencoded",
        "-H","Accept: application/json",
        "--data", data,
    ], out="/tmp/aio_start_resp.json")
    body = pathlib.Path("/tmp/aio_start_resp.json").read_text(errors="ignore")[:500]
    print("start", endpoint, "http=", r.stdout.strip(), "body=", body)
    if r.stdout.strip() in {"200","201","204"}:
        break
    # if HTML returned with new csrf, refresh
    names = re.findall(r'name="csrf_name"\s+value="([^"]+)"', body)
    vals = re.findall(r'name="csrf_value"\s+value="([^"]+)"', body)
    if names and vals:
        csrf_name, csrf_value = names[0], vals[0]
PY

echo "=== Wait for healthy stack ==="
for i in $(seq 1 72); do
  n=$(docker ps --format '{{.Names}}' | grep -c '^nextcloud-aio-' || true)
  nc=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' nextcloud-aio-nextcloud 2>/dev/null || echo missing)
  ap=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' nextcloud-aio-apache 2>/dev/null || echo missing)
  db=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' nextcloud-aio-database 2>/dev/null || echo missing)
  echo "t=$((i*5))s n=$n nc=$nc ap=$ap db=$db"
  if [ "$nc" = "healthy" ] && [ "$ap" = "healthy" ] && [ "$db" = "healthy" ]; then
    break
  fi
  sleep 5
done

echo "=== Inventory ==="
docker ps -a --filter name=nextcloud-aio --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

if ! docker inspect nextcloud-aio-nextcloud >/dev/null 2>&1; then
  echo "FATAL: nextcloud missing"
  docker logs "$MASTER" --tail 120 || true
  exit 6
fi

MOUNT_SRC=$(docker inspect nextcloud-aio-nextcloud --format '{{range .Mounts}}{{if eq .Destination "/mnt/ncdata"}}{{.Source}}{{end}}{{end}}')
echo "ncdata_source=$MOUNT_SRC"
docker inspect nextcloud-aio-nextcloud --format '{{json .Mounts}}' | python3 -m json.tool | head -n 80

docker exec --user www-data nextcloud-aio-nextcloud php occ config:system:get datadirectory || true
docker exec --user www-data nextcloud-aio-nextcloud php occ maintenance:mode --off || true
docker exec --user www-data nextcloud-aio-nextcloud php occ status || true
docker exec --user www-data nextcloud-aio-nextcloud php occ files:scan-app-data || true
docker exec --user www-data nextcloud-aio-nextcloud php occ files:scan --all || true

curl -sk --max-time 15 http://127.0.0.1:11000/status.php | python3 -m json.tool || true
curl -sk --max-time 15 https://wera-ss-pt-sn-1.tailfb390c.ts.net:8443/status.php | python3 -m json.tool || true

docker run --rm -v /mnt/nextcloud-data:/d:ro alpine ls -lan /d | head -n 25
df -hT /mnt/nextcloud-data

case "$MOUNT_SRC" in
  "$TARGET"|"$TARGET"/) echo "PASS: ncdata on $TARGET" ;;
  *)
    echo "FAIL: ncdata source is $MOUNT_SRC"
    docker logs "$MASTER" --tail 100 || true
    exit 5
    ;;
esac

unset AIO_PASS
echo "=== SUCCESS ==="
