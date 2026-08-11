# SolarSeed v3 Product Repository (TRL4 + TRL5)

SolarSeed contains TRL machine product operations: host configuration, deployment manifests, observability, automation, and runbooks required to safely update, test, and operate TRL machines.

## Branch model
- `main`: shared product baseline and governance documents.
- `trl4`: lab station release line (station callsign **Frank**, host `wera-ss-pt-sn-1`).
- `trl5`: field pilot release line.

Branch-specific machine changes should be made on `trl4` or `trl5`, validated, and then merged intentionally.

## Station Frank (TRL4)
Live lab host documentation:
- `ops/stations/FRANK.md` — full station state (hardware, storage, services, health)
- `ops/CONFIG.md` — compact config snapshot
- `ops/NEXTCLOUD_AIO_TRL4.md` — Nextcloud AIO operations
- `WARP.md` — agent operational guide for TRL4

## Repository scope
In scope on `trl4`:
- `compose/` — machine deployment compose templates
- `ops/` — machine configuration, runbooks, station docs, bootstrap scripts
- `prometheus/`, `alertmanager/` — monitoring
- `rundeck/` — automation/job orchestration
- `spirit/`, `openfang/` — Spirit and agent manifests (TRL4 runtime)
- `odoo-app/` — Odoo TRL4 restore/ops profile
- `skills/` — project-local skills (including Odoo TRL workflows)
- `docs/` — operational references

Related external repos may host split products (`CityLight`, `CityView`, `SolarState`).

## Working model for TRL updates
1. Checkout target branch (`trl4` or `trl5`).
2. Edit machine-relevant configuration/runbook files.
3. Validate compose and monitoring changes before push.
4. Execute branch-specific machine test sequence.
5. Push after successful validation.

## Validation commands
```bash
docker compose -f compose/docker-compose.yml config --quiet
docker compose -f compose/docker-compose.yml ps
```
Add branch-specific smoke checks in `ops/RUNBOOK.md` and station docs.

## Safety requirements
- No destructive volume/data operations without explicit confirmation.
- Keep secrets out of Git and out of command output.
- Always document rollback path for changed machine configuration.
- Prefer disk **by-id** paths for partition work on Frank (sdX names can swap).
