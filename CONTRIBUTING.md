# Contributing to SolarSeed-v3
This repository follows umbrella WeRa standards with local TRL machine constraints.

## Scope
- This repository contains product machine operations for `trl4` and `trl5`.
- Framework runtime and non-product UI layers are out of scope and live in dedicated repositories.

## Required reading before implementation
1. `README.md`
2. `WARP.md`
3. `AGENTS.md`
4. `SOUL.md`
5. `ops/CONFIG.md` and `ops/RUNBOOK.md` for operational changes
6. `skills/registry.yaml`

## Branching
- Baseline branch: `main`.
- Branch-specific machine updates: `trl4` (lab) and `trl5` (field).
- Keep changes focused, reversible, and aligned to one operational objective.

## Pull requests
- Include a concise summary of the change and verification steps.
- Link related issue/task when available.
- Ensure CI passes before merge.

## Quality baseline
- Keep `README.md`, `WARP.md`, `AGENTS.md`, and `SOUL.md` aligned when behavior or operations change.
- Do not commit secrets, credentials, or private keys.
- Prefer reversible changes for infrastructure and runtime operations.

## Skills workflow
- Use `skills/registry.yaml` as the local source of truth for execution profiles.
- For medium/high complexity work, follow:
  1. `repo-orientation`
  2. `task-intake`
  3. `implementation-plan`
  4. `quality-gate`
  5. `release-readiness`
- For PR review, include `revisor-pr-audit`.

## Minimum validation for machine config changes
- Validate compose syntax:
  - `docker compose -f compose/docker-compose.yml config --quiet`
- Run additional service checks documented in `ops/RUNBOOK.md` when impacted.
