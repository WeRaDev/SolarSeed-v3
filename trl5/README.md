# TRL5 Branch Working Notes
Use branch `trl5` for field pilot machine updates and validation.
Typical change set:
- machine configuration updates in `compose/`, `ops/`, `prometheus/`, `alertmanager/`, `rundeck/`
- TRL5-specific constraints (solar budget, network availability, fallback behavior) documented in `ops/RUNBOOK.md`
Before push:
1. `docker compose -f compose/docker-compose.yml config --quiet`
2. run TRL5 machine smoke checks and connectivity checks from `ops/RUNBOOK.md`
3. document rollback path and previous stable commit/tag
