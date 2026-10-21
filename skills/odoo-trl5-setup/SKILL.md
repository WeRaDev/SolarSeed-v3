---
name: odoo-trl5-setup
description: Set up and validate Odoo on the TRL5 field machine using local-first preparation, batched SSH execution, and controlled public-exposure gating. Use this when preparing or executing Odoo installation/restore/configuration on TRL5.
---

# Odoo TRL5 setup

## Objective
Establish a stable TRL5 Odoo runtime with repeatable verification and rollback, while preserving loopback-first service exposure and explicit approval gates for high-impact changes.

## Trigger conditions
Use this skill when the user asks to:
- Set up Odoo on TRL5 for the first time.
- Replay a validated Odoo branch onto TRL5.
- Restore Odoo DB + filestore on TRL5.
- Prepare TRL5 for public domain publication.

## Preconditions
- One pinned branch+commit is selected for replay.
- `odoo-app` artifacts (compose, env template, scripts, addons, backup) are ready locally.
- TRL5 host is reachable over SSH/Tailscale.

## Execution gates
### 1) TRL5 preflight gate (read-only)
- Verify host identity, Docker health, free storage, and current listeners.
- Verify Odoo stack is not already running in a conflicting profile.
- Verify no conflicting public ingress change is in progress.

### 2) Artifact parity gate (local)
- Confirm `odoo-app` directory content matches pinned commit.
- Validate compose/env syntax locally before transfer.
- Prepare one transfer bundle (avoid ad-hoc piecemeal writes on host).

### 3) Apply gate (batched SSH session)
- Sync `odoo-app` to TRL5 workspace.
- Validate compose on host (`docker compose ... config --quiet`).
- Start DB and Odoo services.
- Restore SQL and filestore when restore is in scope.
- Run subscription sync script and module upgrade scripts as required.

### 4) Runtime hardening gate
- Keep Odoo loopback-bound unless explicitly approved otherwise.
- Enforce strict DB filter.
- For internet-facing mode, set `proxy_mode=True` and `list_db=False`.
- If website styling regresses, run stale-asset cleanup flow:
  - deactivate stale `ir.asset` rows tied to uninstalled modules
  - clear `/web/assets/%` attachments
  - restart/reload Odoo and re-probe debug CSS bundle

### 5) Validation gate
- Login endpoint returns expected status.
- Core website routes return expected host-specific content.
- CTA/intake path succeeds end-to-end.
- Module queue states (`to install`, `to upgrade`, `to remove`) are empty.
- No style fallback markers remain in website debug CSS bundle.

### 6) Handoff gate
- Record evidence paths and exact probe outputs.
- Report branch/commit and final container status.
- Provide explicit manual test request.

## Public exposure decision gate (TRL5)
Choose one and document:
- Cloudflare Tunnel (outbound-only; no inbound origin ports).
- Public edge gateway (e.g., Linode) over Tailscale backhaul.

Do not execute domain cutover or firewall/listener changes without explicit approval.

## Rollback profile
- Rollback code to prior pinned commit and re-run scoped module upgrade.
- Restore previous DNS/edge route if cutover has started.
- Re-verify login + routes + assets with the previous known-good host mapping.

## Output contract
Return:
- Applied commit hash and TRL5 workspace path.
- Preflight, apply, and validation outcomes.
- Remaining blockers and next minimal action.
