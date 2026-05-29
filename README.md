# SolarSeed v3 Product Repository (TRL4 + TRL5)
SolarSeed now contains only TRL machine product operations scope: host configuration, deployment manifests, observability configuration, and runbooks required to safely update, test, and operate TRL machines before release push.
## Branch model
- `main`: shared product baseline and governance documents.
- `trl4`: lab station release line.
- `trl5`: field pilot release line.
Branch-specific machine changes should be made on `trl4` or `trl5`, validated, and then merged intentionally.
## Repository scope
In scope:
- `compose/`: machine deployment compose templates.
- `ops/`: machine configuration and runbook (`CONFIG.md`, `RUNBOOK.md`).
- `prometheus/`: monitoring scrape and rules.
- `alertmanager/`: alert routing.
- `rundeck/`: automation/job orchestration configuration.
- `docs/`: operational references for TRL work.
Out of scope (moved to dedicated repositories):
- City of Light framework and local operator UI -> `CityLight`.
- Global public/network UI and philanthropy-derived product layer -> `SolarState`.
## Working model for TRL updates
1. Checkout target branch (`trl4` or `trl5`).
2. Edit only machine-relevant configuration/runbook files.
3. Validate compose and monitoring changes before push.
4. Execute branch-specific machine test sequence.
5. Push after successful validation.
## Validation commands
```bash
docker compose -f compose/docker-compose.yml config --quiet
docker compose -f compose/docker-compose.yml ps
```
Add branch-specific smoke checks in `ops/RUNBOOK.md`.
## Safety requirements
- No destructive volume/data operations without explicit confirmation.
- Keep secrets out of Git and out of command output.
- Always document rollback path for changed machine configuration.
## Related repos
- `CityLight`: framework services and CityView-Local.
- `SolarState`: SolarState identity plus CityView-Global.
