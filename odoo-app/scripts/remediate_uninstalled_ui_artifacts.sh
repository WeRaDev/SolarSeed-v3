#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$APP_DIR/docker-compose.yml"
ENV_FILE="$APP_DIR/.env"
SQL_FILE="$SCRIPT_DIR/remediate_uninstalled_ui_artifacts.sql"

DB_NAME="${1:-wera}"
DB_USER="${ODOO_DB_USER:-odoo}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Missing compose file: $COMPOSE_FILE" >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

if [[ ! -f "$SQL_FILE" ]]; then
  echo "Missing SQL file: $SQL_FILE" >&2
  exit 1
fi

read_counts() {
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T odoo-db \
    psql -U "$DB_USER" -d "$DB_NAME" -At -c "select
      (select count(*) from ir_ui_view v
       join ir_model_data d on d.model='ir.ui.view' and d.res_id=v.id
       join ir_module_module m on m.name=d.module
       where v.active and m.state!='installed') as active_views_from_uninstalled,
      (select count(*) from ir_ui_menu u
       join ir_model_data d on d.model='ir.ui.menu' and d.res_id=u.id
       join ir_module_module m on m.name=d.module
       where u.active and m.state!='installed') as active_menus_from_uninstalled;"
}

echo "Pre-remediation drift counts (views|menus):"
read_counts

echo "Applying remediation SQL: $SQL_FILE"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T odoo-db \
  psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" -f - < "$SQL_FILE"

echo "Post-remediation drift counts (views|menus):"
read_counts

echo "Done. Recommended service reload:"
echo "docker compose -f \"$COMPOSE_FILE\" --env-file \"$ENV_FILE\" restart odoo"
