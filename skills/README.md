# SolarSeed-v3 Skills

This directory contains project-local skills and the project skills registry.

## Inheritance model
- Umbrella skills may be defined at the WeRa Global skills root.
- Local registry `skills/registry.yaml` (when present) references umbrella skills and may add project-specific extensions.
- Local overrides must not weaken umbrella quality or security guardrails.

## Recommended default flow
1. `repo-orientation`
2. `task-intake`
3. `implementation-plan` (for non-trivial changes)
4. `quality-gate`
5. `release-readiness`
6. `retro-capture`

## Project-specific skills
- `trl-machine-change`: safety-first procedure for TRL machine configuration changes (when present).

## Odoo skill set (TRL4)
Reusable Odoo-focused skills for the SolarSeed TRL4 workflow:
- `odoo-trl4-restore-operations`
- `odoo-admin-app-governance`
- `odoo-custom-module-dev`
- `odoo-runtime-troubleshooting`
- `odoo-e2e-automation-loop` (when present)
- `odoo-trl5-setup` (when present)

### Usage note
These skills are tuned for the repository restore profile:
- Odoo image `odoo:19.0`
- Compose path `odoo-app/docker-compose.yml`
- Env file `odoo-app/.env` (or host mirror on TRL)
- Station Frank docs: `ops/stations/FRANK.md`
