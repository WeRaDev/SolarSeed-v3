---
name: odoo-custom-module-dev
description: Develop or modify Odoo 19 custom modules with correct manifest, security, data files, and update/test flow. Use when creating modules, adding models/views/security, scaffolding addons, or running module upgrades/tests—especially multi-website brand modules.
---

# Odoo custom module development

## Scope
Manifests, models, views/QWeb, security, data XML, install/upgrade/test on Odoo 19 (community or enterprise as declared).

## Multi-website brand modules (critical)
When shipping website pages/menus/rewrites for one brand:
1. **Scope every `website.page` to the correct `website_id`** (never leave NULL if multi-site).
2. **Do not bind thin stub pages to `url='/'`** if a dump homepage must remain canonical — use alternate URLs or only create `/` when intentionally replacing dump.
3. **`website.rewrite` must set `website_id`** for brand-specific redirects; never ship global rewrites that steal other brands' `/about` or `/contactus`.
4. **Header/footer:** prefer not to inject a second topbar/copyright on brands that use full dump chrome; if injecting, use `website_id` or `t-if` and document UX intent.
5. **`post_init_hook` menu rebuilds** must use real published dump URLs, or run after dump wiring and be idempotent without destroying dump IA.
6. After `-i/-u`, verify Host probes for **all** brands, not only the brand you touched.

## Standard practice
- Depend only on needed modules; pin Odoo series in version (`19.0.x`).
- Security: `ir.model.access.csv` + record rules as required.
- Data: `noupdate` where operator edits must survive upgrades.
- Test: install on clean DB and upgrade path from previous version.
- Never print secrets; use env/files.

## Upgrade/test flow
1. Copy module to addons path.
2. Update apps list; `-i` or `-u MODULE --stop-after-init`.
3. Restart HTTP process/compose service.
4. Probe routes + multi-website Host matrix if website module.
5. Commit module + skill/doc notes if behavior changed.

## Output
Files touched; install/upgrade commands; probe evidence; multi-website impact statement.
