# TRL4 Branch Working Notes
Use branch `trl4` for laboratory machine updates and validation.
Typical change set:
- machine configuration updates in `compose/`, `ops/`, `prometheus/`, `alertmanager/`, `rundeck/`
- TRL4-specific runbook procedures in `ops/RUNBOOK.md`
Before push:
1. `docker compose -f compose/docker-compose.yml config --quiet`
2. run TRL4 machine smoke checks from `ops/RUNBOOK.md`
3. record rollback command or previous tag in branch notes
