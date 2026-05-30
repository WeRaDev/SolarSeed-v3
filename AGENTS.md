# AGENTS.md
Provider-agnostic coding-agent instructions for `SolarSeed-v3`.
This is the canonical local agent behavior file for this project.

## Scope and precedence
- Applies to all paths in this repository unless a closer subdirectory `AGENTS.md` exists.
- Inheritance source: umbrella `/Users/mikhailananyin/Documents/WeRa Global/AGENTS.md`.
- Governance source: local `WARP.md`, with umbrella `WARP.md` as parent policy.
- Constitutional source: local `SOUL.md`, inheriting umbrella `SOUL.md`.
- If guidance conflicts, use the most specific file in this order:
  1. Closest subdirectory `AGENTS.md`
  2. Root `AGENTS.md` (this file)
  3. Project `WARP.md`
  4. Umbrella `AGENTS.md` and umbrella `WARP.md`

## Operational mission
Operate and evolve TRL machine product configuration safely:
- `trl4`: lab release line
- `trl5`: field pilot release line

Treat all machine-impacting edits as safety-sensitive and reversible.

## Local execution invariants
- Read before write: inspect existing config/runbook state before changing files.
- Change only requested scope; avoid unrelated refactors.
- One reversible increment at a time.
- For high-impact operational changes, define rollback path in the same change.
- Keep secrets out of git, output, and plaintext logs.

## Branch discipline
- `main` is shared baseline and governance.
- Machine-specific updates go to `trl4` or `trl5`.
- Do not merge branch-specific changes across lines without explicit intent.

## Validation requirements
Run repository-native checks for changed scope. Minimum for compose-affecting changes:
- `docker compose -f compose/docker-compose.yml config --quiet`

If additional checks are defined in runbooks or workflows, run the relevant subset and report results.

## Required reading before non-trivial changes
1. `README.md`
2. `WARP.md`
3. `SOUL.md`
4. `CONTRIBUTING.md`
5. `ops/CONFIG.md` and `ops/RUNBOOK.md` for operational edits
6. `skills/registry.yaml`

## Skills integration
- Local skills entrypoint: `skills/registry.yaml`.
- Use local execution profile first; inherit umbrella skills where local skills do not override.
- For PR/code-review tasks, apply the `revisor-pr-audit` protocol.

## Compatibility
- `CLAUDE.md` is a compatibility shim and must not diverge from this file.
