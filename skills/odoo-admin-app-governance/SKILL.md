---
name: odoo-admin-app-governance
description: Verify and manage Odoo admin access and installed app/module state in Odoo 19. Use this whenever the user asks about admin account identity, login verification, app installation status, or module governance after restore.
---

# Odoo admin and app governance

## Scope
Use this skill to:
- Distinguish Odoo master password vs application user credentials
- Verify admin-capable users
- Validate login by API
- Audit installed modules and app state

## Important concepts
- `admin_passwd` in `odoo.conf` is the database manager/master password, not always a web user password.
- Web login uses `res_users` credentials (login/email + password).
- Admin-capable application users are typically members of `base.group_system`.

## Procedure
1. Confirm target database name (default `wera`).
2. Identify admin-capable users via SQL:
   - Join `res_users`, `res_groups_users_rel`, and `res_groups` where group is `base.group_system`.
3. Attempt non-destructive login verification using JSON-RPC:
   - POST `/web/session/authenticate` with candidate login/password.
4. Audit installed module set:
   - Query `ir_module_module` for `state='installed'`.
   - Check critical modules for the requested scope (e.g., `website`, `sale`, `account`, `crm`).
5. If login fails, report clearly that module state can still be validated independently of password knowledge.

## Guardrails
- Do not claim an admin login is verified unless authentication call succeeds.
- Do not expose plaintext secrets in output.
- If password reset is requested, treat as high-impact and provide exact reset command before executing.

## Output format
Always include:
- Admin identity finding (user(s) in `base.group_system`)
- Authentication check result (success/failure, with exact endpoint used)
- Installed module count and key module states
- Next action if credentials are missing (e.g., password reset workflow)
