# SolarSeed v3.1 — RESTORE

## Prerequisites
- Matching `compose/docker-compose.yml` and `.env`
- Backup archives available under `/data/backups`
- Sufficient free space on target host

## Restore order
1. Stop stack:
   - `docker compose -f compose/docker-compose.yml down`
2. Restore PostgreSQL data (logical dump preferred for compatibility)
3. Restore Prometheus data
4. Restore Spirit memory/logs
5. Restore Nextcloud data
6. Start stack and validate health

## Commands

### PostgreSQL restore (from SQL dump)
1. Start only postgres:
   - `docker compose -f compose/docker-compose.yml up -d postgres`
2. Wait until healthy, then restore:
   - `gunzip -c /data/backups/postgres_YYYYMMDD.sql.gz | docker compose -f compose/docker-compose.yml exec -T postgres psql -U ${POSTGRES_USER:-citydb} ${POSTGRES_DB:-cityoflight}`

### Prometheus volume restore
`docker run --rm -v solarseed-v3_prometheus_data:/data -v /data/backups:/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/prometheus_YYYYMMDD.tar.gz -C /"`

### Spirit restore
`docker run --rm -v solarseed-v3_spirit_memory:/memory -v solarseed-v3_spirit_logs:/logs -v /data/backups:/backup alpine sh -c "rm -rf /memory/* /logs/* && tar xzf /backup/spirit_YYYYMMDD.tar.gz -C /"`

### Nextcloud restore
`docker run --rm -v solarseed-v3_nextcloud_data:/nc -v /data/backups:/backup alpine sh -c "rm -rf /nc/* && tar xzf /backup/nextcloud_YYYYMMDD.tar.gz -C /"`

## Post-restore validation
- Start services:
  - `docker compose -f compose/docker-compose.yml up -d`
- Check health:
  - `docker compose -f compose/docker-compose.yml ps`
  - `curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'`
  - `curl -s http://localhost:9105/health | jq .`
- Verify Fortress UI:
  - `http://localhost:8080`
