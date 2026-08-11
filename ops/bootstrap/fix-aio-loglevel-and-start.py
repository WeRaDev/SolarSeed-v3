#!/usr/bin/env python3
import json, re, subprocess, time, pathlib, urllib.parse, shlex

def run(cmd, check=True):
    print("+", " ".join(cmd) if isinstance(cmd, list) else cmd)
    return subprocess.run(cmd, check=check, text=True, capture_output=True)

def sh(cmd):
    r = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    print(r.stdout)
    if r.stderr:
        print(r.stderr)
    return r

print("=== Patch postgresql.conf ===")
sh("docker stop nextcloud-aio-database nextcloud-aio-redis 2>/dev/null || true")
sh("""docker run --rm -v nextcloud_aio_database:/data alpine sh -c '
sed -n "520,540p" /data/postgresql.conf || true
python3 - <<EOF
from pathlib import Path
p=Path("/data/postgresql.conf")
t=p.read_text(errors="ignore")
t2=re.sub(r"(?m)^(log_min_messages)\\s*=\\s*$", r"\\1 = warning", t)
import re
t2=re.sub(r"(?m)^(log_min_messages)\\s*=\\s*[\"\\']?[\"\\']?\\s*$", r"\\1 = warning", t)
if t2!=t:
    p.write_text(t2)
    print("patched log_min_messages")
else:
    # force line if missing or empty variants
    lines=[]
    found=False
    for line in t.splitlines(True):
        if line.startswith("log_min_messages"):
            lines.append("log_min_messages = warning\\n")
            found=True
        else:
            lines.append(line)
    if not found:
        lines.append("\\nlog_min_messages = warning\\n")
    p.write_text("".join(lines))
    print("forced log_min_messages")
print("tail:")
print("".join(Path("/data/postgresql.conf").read_text().splitlines(True)[520:540]))
EOF
'""")

# alpine may not have python3 - use sed only
sh("""docker run --rm -v nextcloud_aio_database:/data alpine sh -c '
if grep -n "^log_min_messages" /data/postgresql.conf; then
  sed -i -E "s/^log_min_messages[[:space:]]*=.*/log_min_messages = warning/" /data/postgresql.conf
else
  echo "log_min_messages = warning" >> /data/postgresql.conf
fi
grep -n "^log_min_messages" /data/postgresql.conf
sed -n "525,540p" /data/postgresql.conf
'""")

print("=== Recreate db/redis with AIO_LOG_LEVEL=warn ===")

def inspect(name):
    return json.loads(subprocess.check_output(["docker","inspect",name], text=True))[0]

for name in ["nextcloud-aio-database","nextcloud-aio-redis"]:
    try:
        c=inspect(name)
    except Exception as e:
        print(name, "not present", e)
        continue
    env=c["Config"]["Env"] or []
    env=[e for e in env if not e.startswith("AIO_LOG_LEVEL=")] + ["AIO_LOG_LEVEL=warn"]
    image=c["Config"]["Image"]
    mounts=c["Mounts"]
    hostconfig=c["HostConfig"]
    nets=list((c.get("NetworkSettings") or {}).get("Networks") or {})
    print("recreating", name)
    subprocess.check_call(["docker","rm","-f",name])
    cmd=["docker","run","-d","--name",name]
    restart=(hostconfig.get("RestartPolicy") or {}).get("Name") or "unless-stopped"
    if restart and restart != "no":
        cmd += ["--restart", restart]
    for e in env:
        cmd += ["-e", e]
    for m in mounts:
        mode = "rw" if m.get("RW", True) else "ro"
        if m["Type"]=="volume":
            cmd += ["-v", f"{m['Name']}:{m['Destination']}:{mode}"]
        elif m["Type"]=="bind":
            cmd += ["-v", f"{m['Source']}:{m['Destination']}:{mode}"]
    if nets:
        cmd += ["--network", nets[0]]
    for cap in (hostconfig.get("CapAdd") or []):
        cmd += ["--cap-add", cap]
    for s in (hostconfig.get("SecurityOpt") or []):
        cmd += ["--security-opt", s]
    if hostconfig.get("Init"):
        cmd += ["--init"]
    # healthcheck leave default from image
    cmd.append(image)
    print(" ".join(shlex.quote(x) for x in cmd)[:700])
    subprocess.check_call(cmd)
    for n in nets[1:]:
        subprocess.call(["docker","network","connect", n, name])

time.sleep(6)
print(subprocess.check_output(["docker","ps","-a","--filter","name=nextcloud-aio-database","--filter","name=nextcloud-aio-redis","--format","table {{.Names}}\t{{.Status}}"], text=True))
print("DB logs:")
print(subprocess.check_output(["docker","logs","nextcloud-aio-database","--tail","40"], text=True, stderr=subprocess.STDOUT))
print("REDIS logs:")
print(subprocess.check_output(["docker","logs","nextcloud-aio-redis","--tail","30"], text=True, stderr=subprocess.STDOUT))
print("AIO_LOG env:")
for name in ["nextcloud-aio-database","nextcloud-aio-redis"]:
    env=subprocess.check_output(["docker","inspect","--format","{{range .Config.Env}}{{println .}}{{end}}",name], text=True)
    print(name, [e for e in env.splitlines() if "AIO_LOG" in e])

# Start remaining via AIO API
cookie="/tmp/aio_fix_final.jar"
password=subprocess.check_output([
  "docker","exec","nextcloud-aio-mastercontainer","python3","-c",
  "import json; print(json.load(open('/mnt/docker-aio-config/data/configuration.json'))['password'])"
], text=True).strip()

def curl(args, out=None):
    cmd=["curl","-sk","-c",cookie,"-b",cookie,"--max-time","60"]+args
    if out: cmd += ["-o", out, "-w", "%{http_code}"]
    return subprocess.run(cmd, capture_output=True, text=True)

curl(["https://127.0.0.1:8080/login"], out="/tmp/fll.html")
html=pathlib.Path("/tmp/fll.html").read_text(errors="ignore")
csrf_name=re.search(r'name="csrf_name"\s+value="([^"]+)"', html).group(1)
csrf_value=re.search(r'name="csrf_value"\s+value="([^"]+)"', html).group(1)
data=urllib.parse.urlencode({"password":password,"csrf_name":csrf_name,"csrf_value":csrf_value})
print("login", curl(["-X","POST","https://127.0.0.1:8080/api/auth/login","-H","Content-Type: application/x-www-form-urlencoded","--data",data], out="/tmp/fllr").stdout)
curl(["https://127.0.0.1:8080/containers"], out="/tmp/flc.html")
html=pathlib.Path("/tmp/flc.html").read_text(errors="ignore")
names=re.findall(r'name="csrf_name"\s+value="([^"]+)"', html)
vals=re.findall(r'name="csrf_value"\s+value="([^"]+)"', html)
csrf_name, csrf_value = names[0], vals[0]
data=urllib.parse.urlencode({"csrf_name":csrf_name,"csrf_value":csrf_value})
print("start", curl(["-X","POST","https://127.0.0.1:8080/api/docker/start","-H","Content-Type: application/x-www-form-urlencoded","--data",data], out="/tmp/fls").stdout)

for i in range(60):
    def health(name):
        try:
            return subprocess.check_output(["docker","inspect","-f","{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}",name], text=True).strip()
        except Exception:
            return "missing"
    nc, ap, db, rd = map(health, ["nextcloud-aio-nextcloud","nextcloud-aio-apache","nextcloud-aio-database","nextcloud-aio-redis"])
    print(f"t={i*5}s nc={nc} ap={ap} db={db} rd={rd}")
    if nc=="healthy" and ap=="healthy" and db=="healthy":
        break
    time.sleep(5)

print(subprocess.check_output(["docker","ps","-a","--filter","name=nextcloud-aio","--format","table {{.Names}}\t{{.Status}}"], text=True))
try:
    src=subprocess.check_output(["docker","inspect","-f","{{range .Mounts}}{{if eq .Destination \"/mnt/ncdata\"}}{{.Source}}{{end}}{{end}}","nextcloud-aio-nextcloud"], text=True).strip()
except Exception as e:
    src=f"ERR {e}"
print("ncdata_source", src)
if src.startswith("/mnt/nextcloud-data"):
    for cmd in [
        ["docker","exec","--user","www-data","nextcloud-aio-nextcloud","php","occ","config:system:get","datadirectory"],
        ["docker","exec","--user","www-data","nextcloud-aio-nextcloud","php","occ","status"],
        ["docker","exec","--user","www-data","nextcloud-aio-nextcloud","php","occ","files:scan-app-data"],
        ["docker","exec","--user","www-data","nextcloud-aio-nextcloud","php","occ","files:scan","--all"],
    ]:
        r=subprocess.run(cmd, text=True, capture_output=True)
        print(r.stdout or r.stderr)
    for url in ["http://127.0.0.1:11000/status.php","https://wera-ss-pt-sn-1.tailfb390c.ts.net:8443/status.php"]:
        r=subprocess.run(["curl","-sk","--max-time","15",url], text=True, capture_output=True)
        print(url, r.stdout[:400])
    print("SUCCESS")
else:
    print("DB logs final:")
    print(subprocess.check_output(["docker","logs","nextcloud-aio-database","--tail","30"], text=True, stderr=subprocess.STDOUT))
    print("REDIS logs final:")
    print(subprocess.check_output(["docker","logs","nextcloud-aio-redis","--tail","20"], text=True, stderr=subprocess.STDOUT))
    raise SystemExit(5)
