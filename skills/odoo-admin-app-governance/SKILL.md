---
name: odoo-admin-app-governance
description: Verify and govern Odoo 19 admin identity, module state, enterprise addon parity, and multi-website routing/chrome. Use for admin/login checks, installed app consistency, enterprise drift, wrong-website rendering, or post-restore header/footer/menu governance.
---

# Odoo admin and app governance

## Scope
Admin identity, module lifecycle, enterprise parity (when in scope), multi-website routing, **menus, rewrites, and layout chrome** after dump restore.

## Concepts
- `admin_passwd` ≠ web user password.
- Page body ≠ header/footer chrome.
- Global `website_rewrite` hits every brand unless `website_id` set.
- Shell writes need `env.cr.commit()`.

## Procedure
1. Target DB/profile (Frank `wera_sites` vs Filantropia).
2. Admin users + `/web/session/authenticate` with explicit DB.
3. Module state counts including queues.
4. Addon path consistency for installed modules.
5. Enterprise parity only if enterprise is actually required (community multi-site often is not).
6. Routing: domain, homepage_url, company active, Host probes.
7. **Dump fidelity** per brand website_id:
   - `/` view_id vs dump `website.homepage` arch_len.
   - Active `template_header_*` / `template_footer_*`.
   - Branding inherits adding extra header/footer.
   - Menus vs published pages.
   - Rewrite globals count.
8. Assets if CSS broken.
9. Correct → commit → re-check.

## Chrome policy
| Intent | Header | Footer | Branding topbar/copyright |
|--------|--------|--------|---------------------------|
| Dump-faithful (Fonseca) | One dump/theme header | One dump footer; no `#` placeholders | Prefer **off** |
| Sanitized commercial (WeRa IA) | As designed | Matching | May inject **once** |
| Forbidden without waiver | Theme header + brand topbar duplicating menus | Dump footer + stub strip + conflicting copyright | |

## Output
Admin/auth; modules; catalog/enterprise; per-brand fidelity table; actions by urgency.
