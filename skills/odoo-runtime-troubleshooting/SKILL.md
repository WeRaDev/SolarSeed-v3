---
name: odoo-runtime-troubleshooting
description: Diagnose and recover Odoo 19 runtime failures in SolarSeed with evidence-first playbooks. Use for Internal Server Error, pool saturation, wrong website/branding, double header/footer after restore, rewrite 404s, Settings crashes, CSS fallback, or post-restore instability.
---

# Odoo runtime troubleshooting

## Scope
- Login failures / **403 unauthorized companies**
- Odoo up but web failing; module drift; missing filestore
- Settings Owl errors; connection pool full
- Wrong website for Host; cross-brand bleed
- **Double header/footer** or dump site “looks wrong” after restore
- Menu 404s / bad redirects
- CSS fallback banner
- Public **530** (tunnel) while Odoo may be healthy

## Baseline triage
1. Containers, ports (`8070` multi-site vs `8069` parked), logs.
2. DB + dbfilter.
3. Local `Host:` probes per brand **and** public HTTPS if edge expected.
4. Module states.
5. Filestore.
6. Branch playbook.

**530 first:** tunnel container before deep Odoo.

## Playbooks

### A) Pool / ISE
Confirm `PoolError`; recycle Odoo; clear module queues; burst-probe.

### B) Wrong website / domain
`website` domain/homepage/company; Host probes; `website_rewrite` including **NULL website_id**; bare-host aliases; fix and re-probe.

### C) Settings / registry
Quarantine bad settings inherits; restart; evidence XMLIDs.

### D) Restore drift / attachments
Filestore re-copy; marker routes; classify SQL warnings.

### E) CSS fallback
Debug bundle per website_id; stale `ir.asset` vs uninstalled modules; purge `/web/assets/%`; reload; re-probe.

### F) Double header/footer / outdated dump site
1. Split **page body** vs **chrome** (templates + branding inherits).
2. If dump `website.homepage` arch >> `/` page view → rebind `/`; unpublish stubs.
3. Inventory active header/footer keys + `wera_sites_branding.header_brand_bar` / `brand_footer_company`.
4. Live HTML: brand topbar + theme nav = dual header; dump footer contact + branding copyright + `#` Products = dual/messy footer.
5. Fix chrome/menus; do not only edit homepage arch.
6. Cross-check restore skill Phase 3.

### G) Rewrite / contact 404
List rewrites; scope WeRa globals to website_id=2; disable dead targets; probe per brand.

### H) 403 unauthorized companies
Company `active`; public user company rels; re-probe `/`.

### I) Public 530 / edge
Tunnel status/logs; origin port 8070 vs 8069; `unless-stopped` + compose recreate; local 200 then public.

## Guardrails
- `env.cr.commit()` after shell writes.
- Compose apply when env/image change.
- After website module install, re-audit homepage/menus/rewrites.
- Scoped fixes before mass upgrades.

## Reporting
Cause; evidence (SQL, Host probes, active chrome keys, rewrites); stabilize→remediate→verify; residual risk.
