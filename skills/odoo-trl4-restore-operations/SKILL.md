---
name: odoo-trl4-restore-operations
description: Execute the SolarSeed Odoo restore protocol from local dry-run through TRL replay, including multi-website dump restore (pages, menus, header/footer chrome, rewrites). Use whenever installing/configuring Odoo, restoring a backup, verifying websites, or publishing via Tailscale/Cloudflare tunnel.
---

# Odoo TRL4 restore operations (local -> TRL)

## Scope
Use this skill for:
- Local Odoo stack setup and validation before touching TRL.
- Restoring `dump.sql` + `filestore/` backups (single- or multi-website).
- Functional checks after restore (modules, website chrome, login, assets).
- Replaying the same procedure on TRL from a synchronized branch.
- Tailnet / Cloudflare Tunnel exposure using loopback-only Odoo binding.

## Safety rules
- Treat `down -v`, volume deletion, and DB overwrite as destructive.
- Require explicit `CONFIRM DESTRUCTIVE` before destructive actions.
- Keep Odoo ports loopback-bound (`127.0.0.1`) unless explicitly approved otherwise.
- Use batched SSH sessions for TRL execution; avoid one-command-per-connection loops.
- **Never** restore over or delete a live production DB (e.g. `filantropia_public` on 8069) when the target is a multi-site stack.
- SSH to Frank/TRL4 as user **`wera`**, not `wera-admin` (Tailscale policy).

## Canonical paths and defaults (Frank multi-site reference)
| Item | Value |
|------|--------|
| Isolated stack | `/data/wera-sites` |
| DB | `wera_sites` |
| Odoo HTTP | `127.0.0.1:8070` → container 8069 |
| Parked Filantropia | still 8069 stack; do not conflate |
| Tunnel compose | `/home/wera-admin/cloudflared-frank/` |
| Tunnel container | `filantropia-cloudflared-frank` |
| Custom addons | `/data/wera-sites/addons/` (`wera_website`, `wera_sites_branding`, `wera_fonseca_site`) |
| Brand website IDs | WeRa **2**, Fonseca **5**, Inteligente/HCB2B **11** |

Local single-DB defaults (non-Frank): compose `odoo-app/docker-compose.yml`, DB `wera`, login `http://127.0.0.1:8069/web/login?db=wera`.

## Mandatory execution order
1. **Repository sync gate** — branch + commit pin.
2. **Preflight gate** — compose, env, backup artifacts, disk, LUKS mounts if on TRL.
3. **Apply gate** — start stack; restore SQL then filestore; prune/block enterprise-only modules as required for community image.
4. **Upgrade/unblock gate** — resolve schema/module blockers; never leave modules stuck in `to upgrade`/`to install` without a plan.
5. **Website restore gate** — **Multi-website dump restore playbook** (mandatory when dump has websites).
6. **Verification gate** — auth, Host-header routes, chrome, assets, CTA links.
7. **Edge gate** — tunnel/DNS; `restart: unless-stopped` on cloudflared; public HTTPS.
8. **Learning gate** — update skills/docs; evidence pack.
9. **Handoff** — manual test list.

## Multi-website dump restore playbook (flawless path)

Treat **page body**, **layout chrome** (header/footer templates), **menus**, and **rewrites** as four separate restore surfaces. Restoring only homepage QWeb is **not** a full website restore.

### Phase 0 — Inventory dump before mutating chrome
For each brand website_id `W`:
1. List pages: `website_page` for `W` with `url`, `is_published`, `view_id`, arch length, owning module (`ir_model_data`).
2. Locate dump homepage candidates:
   - `ir_ui_view` where `key='website.homepage' AND website_id=W` (often large arch; may be **orphaned**).
   - Published `website_page` `url='/'` and its `view_id` (may point at a **thin module stub**).
3. List header/footer option views: `template_header_*` / `template_footer_*` for `W` or global; note `active=true`.
4. List `website_menu` for `W`.
5. List `website_rewrite` (`url_from`, `url_to`, `website_id`, `active`). **Global (`website_id IS NULL`) rewrites are high risk.**
6. Record `website.domain`, `homepage_url`, `company_id`, company `active`.

### Phase 1 — Wire dump homepage (not module stubs)
1. Prefer dump `website.homepage` for `W` when arch is clearly richer than module stubs (order-of-magnitude `arch_len`).
2. Point published `website_page` `url='/'` at that dump `view_id`.
3. Set `website.homepage_url='/'` when dump home is `/`.
4. **Unpublish** thin module stubs that collide with dump IA (e.g. module `/services` vs dump `/our-services`) unless owner wants stubs.
5. Module `post_init` pages like `website.fonseca-gardens-home` must **not** silently own `/`.

### Phase 2 — Menus from dump IA
1. Menus must target **dump URLs that exist and are published** on `W`.
2. Never point menus at unpublished stubs or other brands' URLs.
3. Probe every menu URL with `Host: <brand-domain>`.
4. If `wera_sites_branding` (or similar) rebuilds menus in `post_init`, either fix hook defaults to dump URLs or **re-apply dump menus after module install** and document order.

### Phase 3 — Header/footer chrome (prevent double chrome)
**Failure symptom:** two header bars and/or two footer bands, or generic `Products`/`About us` → `#`.

Rules:
1. Chrome lives in `website.layout` + `template_header_*` / `template_footer_*` + inherits — **not** only homepage arch.
2. Pick **one** active header template and **one** active footer template per website (prefer dump-era options, e.g. `template_footer_contact`).
3. Branding injects (`wera_sites_branding.header_brand_bar`, `brand_footer_company`):
   - Scope by `website_id` or `t-if="website.id == …"`.
   - For dump-faithful brands (Fonseca): **disable brand topbar**; keep dump header only.
4. Clean placeholder footer links (`href="#"`) inside active footer templates.
5. Desktop + mobile nav in one header is normal; **extra brand topbar + theme header is not**.

### Phase 4 — Rewrites
1. After installing modules that ship redirects (`wera_website`), audit **all** `website_rewrite`.
2. Scope WeRa-only redirects (`/about`→`/sobre`, `/contactus`→`/contacto`, `/products`→`/solarseed`, token→`/vision`) to **`website_id=2`**.
3. Disable harmful globals (e.g. `/contactus`→`/contact` when `/contact` 404s).
4. Probe `/contactus`, `/about`, `/` per brand Host.

### Phase 5 — Companies, public access, visibility
1. `website.company_id` → `res_company.active=true`.
2. Public user needs company access (`res_company_users_rel`) or **403 unauthorized companies**.
3. Visibility: empty/NULL is public; string `'public'` can 403 — normalize dump rows.
4. De-neutralize only when intended.

### Phase 6 — Modules and assets
1. Order: core website → content modules → branding **only if** chrome policy agreed.
2. After any `-i/-u` of website modules, **re-run Phases 1–2** (modules overwrite `/` and menus).
3. CSS debug bundle per website_id; clean stale `ir.asset` on fallback errors.
4. Filestore must include dump logos/attachments.

### Phase 7 — Edge
1. Tunnel origin = multi-site port (Frank **8070**, not parked 8069).
2. `restart: unless-stopped` **and** `docker compose up -d --force-recreate` so policy sticks.
3. Bare→www via tunnel `httpHostHeader` and/or website aliases.
4. Public 530 ⇒ check tunnel first; local Host 200 before DNS blame.

### Acceptance checklist (all brands)
- [ ] Host `/` 200 with dump marker copy (not accidental stub).
- [ ] `/` `view_id` = dump homepage (arch_len sanity).
- [ ] Single intentional header chrome.
- [ ] Single intentional footer chrome; no `#` primary placeholders.
- [ ] Menu URLs in-brand 200/301.
- [ ] Rewrites scoped; no cross-brand 404 loops.
- [ ] Company active; no public company 403.
- [ ] Assets OK.
- [ ] Public HTTPS 200 when edge in scope.
- [ ] Evidence under `SolarCity/ops/evidence/`.

## Consistency gate fail criteria
- Step without post-check.
- `/` on thin stub while richer dump `website.homepage` exists for that website_id.
- Double header/footer without product sign-off.
- Global rewrites breaking non-WeRa brands.
- Wrong website for Host; route/asset/CTA fail.
- Tunnel `RestartPolicy=no` on production edge.

## Known restore caveats
- SQL IMMUTABLE/gist warnings can be non-blocking if runtime healthy.
- Enterprise dump on community: prune enterprise modules; fix schema blockers.
- Dump `/` vs commercial `/home` — do not flip without owner intent.
- Booking routes 404 without appointment modules — remap CTAs or reinstall.

## Response template
Branch/commit; DB/ports; per-brand home/chrome/rewrites/probes; edge status; blockers + manual tests.

## High-impact checkpoints
Approval before: DNS cutover; firewall/listeners; TLS/edge secrets; public exposure; destructive wipe; disabling branding chrome on live brand without backup note.
