import json
import os
import re
import signal
import ssl
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen
import anyio
import websockets

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel


@dataclass
class ForwardSpec:
    name: str
    local_port: int
    remote_host: str
    remote_port: int
    scheme: str
    insecure_tls: bool


@dataclass
class HealthCheckSpec:
    name: str
    url: str
    timeout_seconds: int
    insecure_tls: bool
    kind: str
    expect_path_prefix: str | None
    forward_name: str | None


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
    proxy_headers: dict[str, dict[str, str]]


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


class ActionResponse(BaseModel):
    ok: bool
    message: str


def _run(cmd: list[str]) -> str:
    res = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or res.stdout.strip() or "command failed")
    return res.stdout.strip()
def _resolve_profile_str(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    if not raw.startswith("env:"):
        return raw or fallback
    spec = raw.split(":", 1)[1]
    if "|" in spec:
        env_name, default_value = spec.split("|", 1)
    else:
        env_name, default_value = spec, fallback
    return str(os.environ.get(env_name, default_value)).strip()


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
            scheme=f.get("scheme", "http"),
            insecure_tls=bool(f.get("insecure_tls", False)),
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
            insecure_tls=bool(c.get("insecure_tls", False)),
            kind=str(c.get("kind", "http")),
            expect_path_prefix=c.get("expect_path_prefix"),
            forward_name=c.get("forward_name"),
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
    proxy_headers = raw.get("proxy_headers", {})
    return Profile(
        name=raw.get("name", "default"),
        ssh_host=_resolve_profile_str(ssh.get("host", ""), ""),
        ssh_user=_resolve_profile_str(ssh.get("user", ""), ""),
        forwards=forwards,
        health_checks=checks,
        building_access=access,
        proxy_headers=proxy_headers,
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


def _urlopen(req: UrlRequest, timeout_seconds: int, insecure_tls: bool = False):
    if insecure_tls:
        return urlopen(req, timeout=timeout_seconds, context=ssl._create_unverified_context())
    return urlopen(req, timeout=timeout_seconds)


def _check_http(url: str, timeout_seconds: int, insecure_tls: bool = False) -> dict[str, Any]:
    req = UrlRequest(url, method="GET")
    try:
        with _urlopen(req, timeout_seconds, insecure_tls=insecure_tls) as resp:
            return {"ok": True, "status": resp.status}
    except URLError as exc:
        return {"ok": False, "error": str(exc.reason)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _extract_root_relative_refs(html: str) -> list[str]:
    refs = []
    for match in re.finditer(r"""(?:href|src|action)\s*=\s*["'](/[^"']*)["']""", html, flags=re.IGNORECASE):
        value = match.group(1)
        if value.startswith("//"):
            continue
        refs.append(value)
    for match in re.finditer(r"""url\((['"]?)(/[^)'"]+)\1\)""", html, flags=re.IGNORECASE):
        value = match.group(2)
        if value.startswith("//"):
            continue
        refs.append(value)
    return refs


def _check_ui(url: str, timeout_seconds: int, insecure_tls: bool = False, expect_path_prefix: str | None = None) -> dict[str, Any]:
    req = UrlRequest(url, method="GET")
    try:
        with _urlopen(req, timeout_seconds, insecure_tls=insecure_tls) as resp:
            body = resp.read()
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type.lower():
                return {"ok": False, "status": resp.status, "error": "ui check expected text/html response"}
            html = body.decode("utf-8", errors="ignore")
            root_refs = _extract_root_relative_refs(html)
            incompatible_root_refs: list[str] = []
            if expect_path_prefix:
                normalized_prefix = f"/{expect_path_prefix.strip('/')}/"
                for ref in root_refs:
                    if ref.startswith(normalized_prefix):
                        continue
                    incompatible_root_refs.append(ref)
            if incompatible_root_refs:
                return {
                    "ok": False,
                    "status": resp.status,
                    "root_relative_refs_count": len(root_refs),
                    "incompatible_root_refs_count": len(incompatible_root_refs),
                    "incompatible_root_refs_sample": incompatible_root_refs[:10],
                    "error": f"response contains root-relative links incompatible with {normalized_prefix}",
                }
            return {"ok": True, "status": resp.status, "root_relative_refs_count": len(root_refs)}
    except URLError as exc:
        return {"ok": False, "error": str(exc.reason)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _run_check(c: HealthCheckSpec) -> dict[str, Any]:
    if c.kind == "proxy_ui":
        return _check_proxy_ui(c)
    if c.kind == "ui":
        return _check_ui(
            c.url,
            c.timeout_seconds,
            insecure_tls=c.insecure_tls,
            expect_path_prefix=c.expect_path_prefix,
        )
    return _check_http(c.url, c.timeout_seconds, insecure_tls=c.insecure_tls)


def _check_proxy_ui(c: HealthCheckSpec) -> dict[str, Any]:
    forward_name = c.forward_name or c.name
    forward = _forward_map().get(forward_name)
    if not forward:
        return {"ok": False, "error": f"proxy_ui check references unknown forward: {forward_name}"}
    if not _listener_pid(forward.local_port):
        return {"ok": False, "error": f"forward {forward_name} is not connected"}

    target_url = f"{forward.scheme}://127.0.0.1:{forward.local_port}/"
    req = UrlRequest(target_url, method="GET")
    try:
        with _urlopen(req, c.timeout_seconds, insecure_tls=forward.insecure_tls) as resp:
            body = resp.read()
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type.lower():
                return {"ok": False, "status": resp.status, "error": "proxy_ui check expected text/html response"}
            html = body.decode("utf-8", errors="ignore")
            rewritten_html = _rewrite_html_for_prefix(html, forward.name)
            root_refs = _extract_root_relative_refs(rewritten_html)
            normalized_prefix = f"/{forward.name.strip('/')}/"
            incompatible_root_refs = [ref for ref in root_refs if not ref.startswith(normalized_prefix)]
            if incompatible_root_refs:
                return {
                    "ok": False,
                    "status": resp.status,
                    "root_relative_refs_count": len(root_refs),
                    "incompatible_root_refs_count": len(incompatible_root_refs),
                    "incompatible_root_refs_sample": incompatible_root_refs[:10],
                    "error": f"proxy_ui rendered output still has root-relative links incompatible with {normalized_prefix}",
                }
            return {
                "ok": True,
                "status": resp.status,
                "root_relative_refs_count": len(root_refs),
                "render_mode": "proxy_rewrite",
            }
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
                "scheme": f.scheme,
                "insecure_tls": f.insecure_tls,
                "listening": listening,
                "pid": pid,
            }
        )
    checks = []
    checks_ok = True
    for c in PROFILE.health_checks:
        result = _run_check(c)
        checks_ok = checks_ok and result["ok"]
        checks.append(
            {
                "name": c.name,
                "url": c.url,
                "timeout_seconds": c.timeout_seconds,
                "insecure_tls": c.insecure_tls,
                "kind": c.kind,
                "expect_path_prefix": c.expect_path_prefix,
                "forward_name": c.forward_name,
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
        check_ok = True
        if b.connection_check and b.connection_check in checks:
            check_ok = bool(checks[b.connection_check].get("ok"))
            health_hint = "up" if check_ok else "down"
        elif b.requires_connection:
            health_hint = "up" if status.get("connected") else "down"
        if b.requires_connection and (not status.get("connected") or not check_ok):
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


def _resolve_header_value(value: str) -> str:
    if value.startswith("env:"):
        env_name = value.split(":", 1)[1]
        return os.environ.get(env_name, "")
    return value


def _start_forward(f: ForwardSpec) -> None:
    if _listener_pid(f.local_port):
        return
    target = _ssh_target()
    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ExitOnForwardFailure=yes",
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
            {
                "name": c.name,
                "url": c.url,
                "timeout_seconds": c.timeout_seconds,
                "insecure_tls": c.insecure_tls,
                "kind": c.kind,
                "expect_path_prefix": c.expect_path_prefix,
                "forward_name": c.forward_name,
            }
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


@app.api_route("/api/v1/access/proxy/{forward_name}", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.api_route(
    "/api/v1/access/proxy/{forward_name}/{path:path}",
    methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def access_proxy(forward_name: str, request: Request, path: str = "") -> Response:
    forward = _forward_map().get(forward_name)
    if not forward:
        raise HTTPException(status_code=404, detail=f"unknown forward: {forward_name}")
    if not _listener_pid(forward.local_port):
        raise HTTPException(status_code=503, detail=f"forward {forward_name} is not connected")

    prefix = f"{forward.scheme}://127.0.0.1:{forward.local_port}"
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
    outgoing_headers["X-Forwarded-Proto"] = request.url.scheme
    outgoing_headers["X-Forwarded-Host"] = request.url.hostname or ""
    outgoing_headers["X-Forwarded-Prefix"] = f"/{forward_name}"
    for hdr_name, hdr_value in PROFILE.proxy_headers.get(forward_name, {}).items():
        resolved_value = _resolve_header_value(hdr_value)
        if resolved_value:
            outgoing_headers[hdr_name] = resolved_value

    body = await request.body()
    proxy_req = UrlRequest(
        target_url,
        data=body if body else None,
        headers=outgoing_headers,
        method=request.method,
    )
    try:
        with _urlopen(proxy_req, 30, insecure_tls=forward.insecure_tls) as resp:
            resp_body = b"" if request.method == "HEAD" else resp.read()
            headers: dict[str, str] = {}
            for h, v in resp.headers.items():
                if h.lower() in HOP_BY_HOP_HEADERS:
                    continue
                headers[h] = v
            location = headers.get("Location")
            if location and location.startswith("/") and not location.startswith(f"/{forward_name}/"):
                headers["Location"] = f"/{forward_name}{location}"
            content_type = headers.get("Content-Type", "")
            if request.method != "HEAD" and "text/html" in content_type.lower() and resp_body:
                html = resp_body.decode("utf-8", errors="ignore")
                rewritten = _rewrite_html_for_prefix(html, forward_name)
                if rewritten != html:
                    resp_body = rewritten.encode("utf-8")
                    headers.pop("Content-Length", None)
            if (
                request.method != "HEAD"
                and forward_name == "openfang"
                and ("javascript" in content_type.lower() or path.endswith(".js"))
                and resp_body
            ):
                js = resp_body.decode("utf-8", errors="ignore")
                rewritten_js = _rewrite_openfang_api_prefix(js, forward_name)
                if rewritten_js != js:
                    resp_body = rewritten_js.encode("utf-8")
                    headers.pop("Content-Length", None)
            return Response(content=resp_body, status_code=resp.status, headers=headers)
    except HTTPError as exc:
        exc_body = exc.read()
        headers: dict[str, str] = {}
        if exc.headers:
            for h, v in exc.headers.items():
                if h.lower() in HOP_BY_HOP_HEADERS:
                    continue
                headers[h] = v
        location = headers.get("Location")
        if location and location.startswith("/") and not location.startswith(f"/{forward_name}/"):
            headers["Location"] = f"/{forward_name}{location}"
        return Response(content=exc_body, status_code=exc.code, headers=headers)
    except URLError as exc:
        raise HTTPException(status_code=502, detail=f"proxy error: {exc.reason}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"proxy error: {exc}") from exc

@app.websocket("/api/v1/access/proxy/{forward_name}/{path:path}")
async def access_proxy_ws(forward_name: str, websocket: WebSocket, path: str) -> None:
    forward = _forward_map().get(forward_name)
    if not forward:
        await websocket.close(code=4404, reason=f"unknown forward: {forward_name}")
        return
    if not _listener_pid(forward.local_port):
        await websocket.close(code=4503, reason=f"forward {forward_name} is not connected")
        return

    ws_scheme = "wss" if forward.scheme == "https" else "ws"
    proxy_path = path.lstrip("/")
    target_url = f"{ws_scheme}://127.0.0.1:{forward.local_port}/{proxy_path}" if proxy_path else f"{ws_scheme}://127.0.0.1:{forward.local_port}/"
    if websocket.url.query:
        target_url = f"{target_url}?{websocket.url.query}"

    outgoing_headers: list[tuple[str, str]] = []
    for k, v in websocket.headers.items():
        lk = k.lower()
        if lk in ("host", "connection", "upgrade", "sec-websocket-key", "sec-websocket-version", "sec-websocket-extensions"):
            continue
        outgoing_headers.append((k, v))
    outgoing_headers.append(("X-Forwarded-Proto", "https" if websocket.url.scheme == "wss" else "http"))
    outgoing_headers.append(("X-Forwarded-Host", websocket.url.hostname or ""))
    outgoing_headers.append(("X-Forwarded-Prefix", f"/{forward_name}"))
    for hdr_name, hdr_value in PROFILE.proxy_headers.get(forward_name, {}).items():
        resolved_value = _resolve_header_value(hdr_value)
        if resolved_value:
            outgoing_headers.append((hdr_name, resolved_value))

    tls_context = ssl._create_unverified_context() if (forward.insecure_tls and ws_scheme == "wss") else None
    await websocket.accept()
    try:
        async with websockets.connect(target_url, additional_headers=outgoing_headers, open_timeout=30, ssl=tls_context) as upstream:
            async def client_to_upstream() -> None:
                while True:
                    message = await websocket.receive()
                    msg_type = message.get("type")
                    if msg_type == "websocket.disconnect":
                        break
                    if msg_type != "websocket.receive":
                        continue
                    text_data = message.get("text")
                    bytes_data = message.get("bytes")
                    if text_data is not None:
                        await upstream.send(text_data)
                    elif bytes_data is not None:
                        await upstream.send(bytes_data)

            async def upstream_to_client() -> None:
                async for data in upstream:
                    if isinstance(data, bytes):
                        await websocket.send_bytes(data)
                    else:
                        await websocket.send_text(data)

            async with anyio.create_task_group() as tg:
                tg.start_soon(client_to_upstream)
                tg.start_soon(upstream_to_client)
    except WebSocketDisconnect:
        return
    except Exception:
        try:
            await websocket.close(code=1011)
        except Exception:
            return


def _rewrite_html_for_prefix(html: str, forward_name: str) -> str:
    prefix = f"/{forward_name.strip('/')}/"

    def rewrite_attr(match: re.Match[str]) -> str:
        attr_prefix = match.group(1)
        quote = match.group(2)
        path_value = match.group(3)
        if path_value.startswith("//"):
            return match.group(0)
        if path_value.startswith(prefix):
            return match.group(0)
        rewritten = f"{prefix}{path_value.lstrip('/')}"
        return f"{attr_prefix}{quote}{rewritten}{quote}"

    rewritten_html = re.sub(
        r"""((?:href|src|action)\s*=\s*)(["'])/([^"']*)\2""",
        rewrite_attr,
        html,
        flags=re.IGNORECASE,
    )

    def rewrite_css_url(match: re.Match[str]) -> str:
        quote = match.group(1)
        path_value = match.group(2)
        if path_value.startswith("//"):
            return match.group(0)
        if path_value.startswith(prefix):
            return match.group(0)
        rewritten = f"{prefix}{path_value.lstrip('/')}"
        return f"url({quote}{rewritten}{quote})"

    rewritten_html = re.sub(
        r"""url\((['"]?)/([^)'"]+)\1\)""",
        rewrite_css_url,
        rewritten_html,
        flags=re.IGNORECASE,
    )
    if forward_name == "openfang":
        rewritten_html = _rewrite_openfang_api_prefix(rewritten_html, forward_name)
    return rewritten_html


def _rewrite_openfang_api_prefix(content: str, forward_name: str) -> str:
    prefix = f"/{forward_name.strip('/')}/"
    rewritten = content
    rewritten = rewritten.replace('"/api/', f'"{prefix}api/')
    rewritten = rewritten.replace("'/api/", f"'{prefix}api/")
    rewritten = rewritten.replace('"/api?', f'"{prefix}api?')
    rewritten = rewritten.replace("'/api?", f"'{prefix}api?")
    return rewritten


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
