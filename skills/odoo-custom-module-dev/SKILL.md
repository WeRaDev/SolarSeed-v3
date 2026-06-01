---
name: odoo-custom-module-dev
description: Develop or modify Odoo 19 custom modules with correct manifest, security, data files, and update/test flow. Use this whenever the user asks to create modules, add models/views/security, scaffold addons, or run module upgrades/tests.
---

# Odoo custom module development (19.0)

## Scope
Use this skill for:
- New addon/module creation
- Model, view, action, and menu changes
- Security (`ir.model.access.csv`) and data file loading
- Module update/test execution

## Odoo 19 references encoded in this workflow
- Module manifest is defined in `__manifest__.py`
- Module must include at least `__init__.py` and `__manifest__.py`
- Security access is data-driven (`security/ir.model.access.csv`)
- Data loading order in manifest matters

## Minimal module checklist
1. Create module directory under addons path.
2. Add `__manifest__.py` with:
   - `name`
   - `depends` (include `base`)
   - `data` entries in dependency-safe order
3. Add Python package files:
   - `__init__.py`
   - `models/__init__.py`
   - `models/<model_file>.py`
4. Add security file:
   - `security/ir.model.access.csv`
5. Add views/actions/menus:
   - `views/*.xml`

## Safe update cycle
1. Validate syntax and structure of changed XML/CSV/Python files.
2. Run module update in controlled mode on target DB:
   - `odoo -d <db> -u <module> --stop-after-init`
   - In containerized profile, run via `docker compose exec -T odoo ...`
3. Review logs for:
   - access rights warnings
   - missing external IDs
   - XML parse/load errors
4. Re-check module state in `ir_module_module`.

## Testing guidance
- Put tests under `tests/` with files named `test_*.py`.
- Ensure tests are imported in `tests/__init__.py`.
- Use `--test-enable` and optional `--test-tags` for targeted runs.
- Prefer targeted module tests first, then broader regression checks.

## Guardrails
- Never bypass access rules by default; implement proper access groups and rules.
- Avoid direct SQL writes for business logic when ORM methods exist.
- For production-like DBs, avoid risky flags intended for debugging only.

## Deliverable expectation
Return:
- Files created/changed
- Exact module update/test commands run
- Results and any remaining warnings
