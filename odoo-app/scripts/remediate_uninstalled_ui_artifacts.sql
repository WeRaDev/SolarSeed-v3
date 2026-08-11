-- Remediate runtime drift where UI artifacts from uninstalled modules remain active.
-- The script is reversible because it snapshots affected rows before deactivation.

BEGIN;

CREATE TABLE IF NOT EXISTS oz_backup_uninstalled_ui_view (
    id integer NOT NULL,
    active boolean NOT NULL,
    module varchar,
    xmlid_name varchar,
    captured_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS oz_backup_uninstalled_ui_menu (
    id integer NOT NULL,
    active boolean NOT NULL,
    module varchar,
    xmlid_name varchar,
    captured_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO oz_backup_uninstalled_ui_view (id, active, module, xmlid_name, captured_at)
SELECT v.id, v.active, d.module, d.name, now()
FROM ir_ui_view v
JOIN ir_model_data d ON d.model = 'ir.ui.view' AND d.res_id = v.id
JOIN ir_module_module m ON m.name = d.module
WHERE v.active
  AND m.state != 'installed';

INSERT INTO oz_backup_uninstalled_ui_menu (id, active, module, xmlid_name, captured_at)
SELECT u.id, u.active, d.module, d.name, now()
FROM ir_ui_menu u
JOIN ir_model_data d ON d.model = 'ir.ui.menu' AND d.res_id = u.id
JOIN ir_module_module m ON m.name = d.module
WHERE u.active
  AND m.state != 'installed';

UPDATE ir_ui_view v
SET active = false,
    write_date = now()
FROM ir_model_data d
JOIN ir_module_module m ON m.name = d.module
WHERE d.model = 'ir.ui.view'
  AND d.res_id = v.id
  AND v.active
  AND m.state != 'installed';

UPDATE ir_ui_menu u
SET active = false,
    write_date = now()
FROM ir_model_data d
JOIN ir_module_module m ON m.name = d.module
WHERE d.model = 'ir.ui.menu'
  AND d.res_id = u.id
  AND u.active
  AND m.state != 'installed';

COMMIT;
