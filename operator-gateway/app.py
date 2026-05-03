import json
import os
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel


@dataclass
class ForwardSpec:
    name: str
    local_port: int
    remote_host: str
    remote_port: int


@dataclass
class HealthCheckSpec:
    name: str
    url: str
    timeout_seconds: int


@dataclass
class BuildingAccessSpec:
    id: str
    app_url: str | None
    app_label: str
    requires_connection: bool
    connection_check: str | None
    forward_name: str | None


@dataclass
class Profile:
    name: str
    ssh_host: str
    ssh_user: str
    forwards: list[ForwardSpec]
    health_checks: list[HealthCheckSpec]
    building_access: list[BuildingAccessSpec]


class ActionResponse(BaseModel):
    ok: bool
    message: str


def _run(cmd: list[str]) -> str:
    res = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or res.stdout.strip() or "command failed")
    return res.stdout.strip()


def _load_profile() -> Profile:
    path = Path(os.environ.get("OPERATOR_PROFILE_PATH", "/app/config/session_profile.json"))
    if not path.exists():
        raise RuntimeError(f"profile file missing: {path}")
    raw: dict[str, Any] = json.loads(path.read_text())
    ssh = raw.get("ssh") or {}
    forwards = [
        ForwardSpec(
            name=f.get("name", f"forward-{i+1}"),
            local_port=int(f["local_port"]),
            remote_host=f["remote_host"],
            remote_port=int(f["remote_port"]),
        )
        for i, f in enumerate(raw.get("forwards", []))
    ]
    if not forwards:
        raise RuntimeError("profile requires at least one forward")
    checks = [
        HealthCheckSpec(
            name=c.get("name", f"check-{i+1}"),
            url=c["url"],
            timeout_seconds=int(c.get("timeout_seconds", 5)),
        )
        for i, c in enumerate(raw.get("health_checks", []))
    ]
    access = [
        BuildingAccessSpec(
            id=b["id"],
            app_url=b.get("app_url"),
            app_label=b.get("app_label", "Open App →"),
            requires_connection=bool(b.get("requires_connection", False)),
            connection_check=b.get("connection_check"),
            forward_name=b.get("forward_name"),
        )
        for b in raw.get("building_access", [])
    ]
    return Profile(
        name=raw.get("name", "default"),
        ssh_host=str(ssh.get("host", "")).strip(),
        ssh_user=str(ssh.get("user", "")).strip(),
        forwards=forwards,
        health_checks=checks,
        building_access=access,
    )


PROFILE = _load_profile()
app = FastAPI(title="Cityview Operator Gateway", version="0.1.0")


def _listener_pid(port: int) -> int | None:
    res = subprocess.run(
        ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-Fpct"],
        check=False,
        capture_output=True,
        text=True,
    )
    if res.returncode not in (0, 1):
        return None
    lines = [ln.strip() for ln in res.stdout.splitlines() if ln.strip()]
    pid = None
    cmd = None
    for line in lines:
        if line.startswith("p"):
            pid = int(line[1:])
        elif line.startswith("c"):
            cmd = line[1:]
    if pid and cmd == "ssh":
        return pid
    return None


def _check_http(url: str, timeout_seconds: int) -> dict[str, Any]:
    req = UrlRequest(url, method="GET")
    try:
        with urlopen(req, timeout=timeout_seconds) as resp:
            return {"ok": True, "status": resp.status}
    except URLError as exc:
        return {"ok": False, "error": str(exc.reason)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _status() -> dict[str, Any]:
    forwards = []
    all_listening = True
    for f in PROFILE.forwards:
        pid = _listener_pid(f.local_port)
        listening = pid is not None
        all_listening = all_listening and listening
        forwards.append(
            {
                "name": f.name,
                "local_port": f.local_port,
                "remote_host": f.remote_host,
                "remote_port": f.remote_port,
                "listening": listening,
                "pid": pid,
            }
        )
    checks = []
    checks_ok = True
    for c in PROFILE.health_checks:
        result = _check_http(c.url, c.timeout_seconds)
        checks_ok = checks_ok and result["ok"]
        checks.append(
            {
                "name": c.name,
                "url": c.url,
                "timeout_seconds": c.timeout_seconds,
                **result,
            }
        )
    return {
        "profile": {
            "name": PROFILE.name,
            "ssh_host": PROFILE.ssh_host,
            "ssh_user": PROFILE.ssh_user,
        },
        "forwards": forwards,
        "health_checks": checks,
        "connected": all_listening,
        "healthy": checks_ok,
        "state": "CONNECTED" if all_listening and checks_ok else ("DEGRADED" if all_listening else "DISCONNECTED"),
    }


def _ssh_target() -> str:
    if not PROFILE.ssh_host or not PROFILE.ssh_user:
        raise RuntimeError("profile ssh user/host are required")
    return f"{PROFILE.ssh_user}@{PROFILE.ssh_host}"


def _forward_map() -> dict[str, ForwardSpec]:
    return {f.name: f for f in PROFILE.forwards}


def _resolve_building_access(status: dict[str, Any]) -> list[dict[str, Any]]:
    checks = {c["name"]: c for c in status.get("health_checks", [])}
    resolved = []
    for b in PROFILE.building_access:
        app_url = b.app_url
        health_hint = "unknown"
        if b.connection_check and b.connection_check in checks:
            health_hint = "up" if checks[b.connection_check].get("ok") else "down"
        elif b.requires_connection:
            health_hint = "up" if status.get("connected") else "down"
        if b.requires_connection and not status.get("connected"):
            app_url = None
        resolved.append(
            {
                "id": b.id,
                "app_url": app_url,
                "app_label": b.app_label,
                "requires_connection": b.requires_connection,
                "connection_check": b.connection_check,
                "forward_name": b.forward_name,
                "health_hint": health_hint,
            }
        )
    return resolved


def _start_forward(f: ForwardSpec) -> None:
    if _listener_pid(f.local_port):
        return
    target = _ssh_target()
    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ServerAliveInterval=30",
        "-fNT",
        "-L",
        f"{f.local_port}:{f.remote_host}:{f.remote_port}",
        target,
    ]
    _run(cmd)


def _stop_forward(f: ForwardSpec) -> None:
    pid = _listener_pid(f.local_port)
    if not pid:
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/connection/profile")
def profile() -> dict[str, Any]:
    return {
        "name": PROFILE.name,
        "ssh_host": PROFILE.ssh_host,
        "ssh_user": PROFILE.ssh_user,
        "forwards": [
            {
                "name": f.name,
                "local_port": f.local_port,
                "remote_host": f.remote_host,
                "remote_port": f.remote_port,
            }
            for f in PROFILE.forwards
        ],
        "health_checks": [
            {"name": c.name, "url": c.url, "timeout_seconds": c.timeout_seconds}
            for c in PROFILE.health_checks
        ],
    }


@app.get("/api/v1/connection/status")
def connection_status() -> dict[str, Any]:
    return _status()


@app.get("/api/v1/access/buildings")
def access_buildings() -> dict[str, Any]:
    status = _status()
    return {
        "profile": {"name": PROFILE.name},
        "connection_state": status.get("state", "UNKNOWN"),
        "connected": bool(status.get("connected")),
        "buildings": _resolve_building_access(status),
    }


@app.api_route("/api/v1/access/proxy/{forward_name}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.api_route("/api/v1/access/proxy/{forward_name}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def access_proxy(forward_name: str, request: Request, path: str = "") -> Response:
    forward = _forward_map().get(forward_name)
    if not forward:
        raise HTTPException(status_code=404, detail=f"unknown forward: {forward_name}")
    if not _listener_pid(forward.local_port):
        raise HTTPException(status_code=503, detail=f"forward {forward_name} is not connected")

    prefix = f"http://127.0.0.1:{forward.local_port}"
    proxy_path = path.lstrip("/")
    target_url = f"{prefix}/{proxy_path}" if proxy_path else f"{prefix}/"
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    outgoing_headers: dict[str, str] = {}
    for k, v in request.headers.items():
        lk = k.lower()
        if lk in ("host", "content-length", "connection", "accept-encoding"):
            continue
        outgoing_headers[k] = v

    body = await request.body()
    proxy_req = UrlRequest(
        target_url,
        data=body if body else None,
        headers=outgoing_headers,
        method=request.method,
    )
    try:
        with urlopen(proxy_req, timeout=30) as resp:
            resp_body = resp.read()
            headers = {}
            content_type = resp.headers.get("Content-Type")
            if content_type:
                headers["Content-Type"] = content_type
            return Response(content=resp_body, status_code=resp.status, headers=headers)
    except HTTPError as exc:
        exc_body = exc.read()
        headers = {}
        content_type = exc.headers.get("Content-Type") if exc.headers else None
        if content_type:
            headers["Content-Type"] = content_type
        return Response(content=exc_body, status_code=exc.code, headers=headers)
    except URLError as exc:
        raise HTTPException(status_code=502, detail=f"proxy error: {exc.reason}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"proxy error: {exc}") from exc


@app.post("/api/v1/connection/start", response_model=ActionResponse)
def connection_start() -> ActionResponse:
    try:
        for f in PROFILE.forwards:
            _start_forward(f)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"failed to start connection: {exc}") from exc
    return ActionResponse(ok=True, message="connection started")


@app.post("/api/v1/connection/stop", response_model=ActionResponse)
def connection_stop() -> ActionResponse:
    for f in PROFILE.forwards:
        _stop_forward(f)
    return ActionResponse(ok=True, message="connection stopped")
