# SolarSeed v3.1 — BACKUP

## Scope
- PostgreSQL data (`postgres_data` volume)
- Prometheus TSDB (`prometheus_data` volume)
- Spirit memory/logs (`spirit_memory`, `spirit_logs` volumes)
- Nextcloud data (`nextcloud_data` volume or external datadir)
- Compose and config files (`compose/`, `prometheus/`, `alertmanager/`, `spirit/`, `ops/`)

## Recommended cadence
- Daily: PostgreSQL logical dump + Spirit memory archive
- Daily: Prometheus volume snapshot
- Weekly: Nextcloud data backup
- Monthly: full restore drill to a staging host

## Commands

### PostgreSQL logical backup
`docker compose -f compose/docker-compose.yml exec postgres pg_dump -U ${POSTGRES_USER:-citydb} ${POSTGRES_DB:-cityoflight} | gzip > /data/backups/postgres_$(date +%Y%m%d).sql.gz`

### Prometheus volume backup
`docker run --rm -v solarseed-v3_prometheus_data:/data -v /data/backups:/backup alpine sh -c "tar czf /backup/prometheus_$(date +%Y%m%d).tar.gz -C / data"`

### Spirit backup
`docker run --rm -v solarseed-v3_spirit_memory:/memory -v solarseed-v3_spirit_logs:/logs -v /data/backups:/backup alpine sh -c "tar czf /backup/spirit_$(date +%Y%m%d).tar.gz -C / memory logs"`

### Nextcloud data backup
`docker run --rm -v solarseed-v3_nextcloud_data:/nc -v /data/backups:/backup alpine sh -c "tar czf /backup/nextcloud_$(date +%Y%m%d).tar.gz -C / nc"`

## Verification
- Verify archive integrity after each backup:
  - `gzip -t /data/backups/<file>.gz`
  - `tar tzf /data/backups/<file>.tar.gz | head`
- Keep at least one off-host encrypted copy.
