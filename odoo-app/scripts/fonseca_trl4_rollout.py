import json
import os
from urllib.parse import urlsplit


ENTERPRISE_CODE = os.environ.get("ODOO_ENTERPRISE_CODE", "M240830172487565")
APPOINTMENT_MODE = os.environ.get("FONSECA_APPOINTMENT_MODE", "manual_callback").strip().lower()
SUPPORTED_APPOINTMENT_MODE = "self_booking"
MANUAL_CONSULTATION_URL = "/contactus?intent=consultation&amp;partner=fonseca-gardens"
FONSECA_WEBSITE_DOMAIN = os.environ.get(
    "FONSECA_WEBSITE_DOMAIN",
    "https://fonseca-gardens.wera-ss-pt-sn-1.tailfb390c.ts.net",
).strip()
UNSUPPORTED_APPOINTMENT_MODULES = [
    "appointment",
    "appointment_account_payment",
    "appointment_crm",
    "appointment_hr",
    "appointment_hr_recruitment",
    "appointment_sms",
    "website_appointment_crm",
    "web_gantt",
    "hr_gantt",
]


def _filter_vals(model, vals):
    return {k: v for k, v in vals.items() if k in model._fields and v is not None}


def _ensure_module_installed(env, module_name):
    module = env["ir.module.module"].sudo().search([("name", "=", module_name)], limit=1)
    if not module:
        return {"module": module_name, "state": "missing", "changed": False}

    initial_state = module.state
    if initial_state != "installed":
        module.button_immediate_install()
        env.cr.commit()
        module = env["ir.module.module"].sudo().browse(module.id)
        if module.state == "to install" and hasattr(module, "button_install_cancel"):
            module.button_install_cancel()
            env.cr.commit()
            module = env["ir.module.module"].sudo().browse(module.id)

    return {
        "module": module_name,
        "state": module.state,
        "changed": initial_state != module.state,
    }


def _probe_module_state(env, module_name):
    module = env["ir.module.module"].sudo().search([("name", "=", module_name)], limit=1)
    if not module:
        return {"module": module_name, "state": "missing", "changed": False}
    return {"module": module_name, "state": module.state, "changed": False}


def _normalize_unsupported_appointment_modules(env):
    module_model = env["ir.module.module"].sudo()
    modules = module_model.search([("name", "in", UNSUPPORTED_APPOINTMENT_MODULES)])
    normalized = []
    for module in modules:
        if module.state in {"to install", "to upgrade", "to remove"}:
            before = module.state
            module.write({"state": "uninstalled"})
            normalized.append({"module": module.name, "from": before, "to": "uninstalled"})
    if normalized:
        env.cr.commit()
    return normalized


def _ensure_enterprise_subscription(env):
    params = env["ir.config_parameter"].sudo()
    key = "database.enterprise_code"
    current = params.get_param(key)
    changed = current != ENTERPRISE_CODE
    if changed:
        params.set_param(key, ENTERPRISE_CODE)
    return {"key": key, "previous_value": current, "current_value": ENTERPRISE_CODE, "changed": changed}


def _normalize_website_domain(website):
    raw_domain = (website.domain or "").strip()
    if not raw_domain:
        return {"previous_value": raw_domain, "current_value": raw_domain, "changed": False}

    candidate = raw_domain if "://" in raw_domain else f"https://{raw_domain}"
    parsed = urlsplit(candidate)
    if not parsed.netloc:
        return {"previous_value": raw_domain, "current_value": raw_domain, "changed": False}
    website_model = website.env["website"].sudo()
    candidates = []
    preferred_candidate = FONSECA_WEBSITE_DOMAIN if "://" in FONSECA_WEBSITE_DOMAIN else f"https://{FONSECA_WEBSITE_DOMAIN}"
    preferred_parsed = urlsplit(preferred_candidate)
    if preferred_parsed.netloc:
        candidates.append(f"{preferred_parsed.scheme}://{preferred_parsed.netloc}")

    host_only = f"{parsed.scheme}://{parsed.netloc}"
    candidates.append(host_only)
    if parsed.hostname and parsed.port is None:
        default_port = 443 if parsed.scheme == "https" else 80
        candidates.append(f"{parsed.scheme}://{parsed.hostname}:{default_port}")
    deduped_candidates = []
    seen = set()
    for domain_candidate in candidates:
        if domain_candidate in seen:
            continue
        seen.add(domain_candidate)
        deduped_candidates.append(domain_candidate)

    normalized = raw_domain
    for domain_candidate in deduped_candidates:
        conflict = website_model.search_count([("id", "!=", website.id), ("domain", "=", domain_candidate)])
        if not conflict:
            normalized = domain_candidate
            break

    changed = normalized != raw_domain
    if changed:
        website.write({"domain": normalized})
    return {"previous_value": raw_domain, "current_value": normalized, "changed": changed}


def _upsert_fonseca_company(env):
    company_model = env["res.company"].sudo()
    partner_model = env["res.partner"].sudo()
    country = env["res.country"].sudo().search([("code", "=", "PT")], limit=1)
    currency = env.ref("base.EUR", raise_if_not_found=False)
    company = company_model.search([("name", "=", "Fonseca Gardens")], limit=1)

    company_vals = _filter_vals(
        company_model,
        {
            "name": "Fonseca Gardens",
            "country_id": country.id if country else None,
            "currency_id": currency.id if currency else None,
            "generate_deferred_expense_entries_method": "on_validation",
            "generate_deferred_revenue_entries_method": "on_validation",
        },
    )

    changed = False
    if company:
        write_vals = {}
        for field_name, value in company_vals.items():
            current = company[field_name]
            current_value = current.id if hasattr(current, "id") else current
            if current_value != value:
                write_vals[field_name] = value
        if write_vals:
            company.write(write_vals)
            changed = True
    else:
        template_company = env.company.sudo()
        create_vals = dict(company_vals)
        for field_name, field in company_model._fields.items():
            if field_name in create_vals:
                continue
            if not field.required:
                continue
            if field.compute or field.related or not field.store:
                continue
            if field_name in {"id", "display_name", "__last_update", "partner_id"}:
                continue
            if field.type == "many2one":
                create_vals[field_name] = template_company[field_name].id or False
            elif field.type == "many2many":
                create_vals[field_name] = [(6, 0, template_company[field_name].ids)]
            elif field.type == "selection":
                allowed_values = field.get_values(env)
                current_value = template_company[field_name]
                create_vals[field_name] = current_value if current_value in allowed_values else (allowed_values[0] if allowed_values else False)
            elif field.type in {"char", "text", "selection", "boolean", "integer", "float", "monetary", "date", "datetime"}:
                create_vals[field_name] = template_company[field_name]
            # One2many and binary fields are intentionally skipped.
        try:
            company = company_model.with_context(install_mode=True).create(create_vals)
            changed = True
        except Exception as exc:
            env.cr.rollback()
            profile = partner_model.search([("name", "=", "Fonseca Gardens"), ("is_company", "=", True)], limit=1)
            if not profile:
                profile = partner_model.create(
                    _filter_vals(
                        partner_model,
                        {
                            "name": "Fonseca Gardens",
                            "is_company": True,
                            "country_id": country.id if country else None,
                        },
                    )
                )
                changed = True
            profile_vals = _filter_vals(
                profile,
                {
                    "comment": (
                        "Company-profile fallback created because res.company creation is blocked by "
                        "runtime schema constraints on this TRL4 database. "
                        "Use this partner profile for website identity and CRM linkage."
                    )
                },
            )
            if profile_vals:
                profile.write(profile_vals)
                changed = True
            return {
                "id": None,
                "partner_id": profile.id,
                "changed": changed,
                "mode": "partner_profile_fallback",
                "error": str(exc),
            }

    partner = company.partner_id.sudo()
    partner_vals = _filter_vals(
        partner,
        {
            "name": "Fonseca Gardens",
            "is_company": True,
            "country_id": country.id if country else None,
            "comment": (
                "Subscription-first garden maintenance partner profile for WeRa Global. "
                "Positioning: Above & beyond. Every garden. "
                "Service area focus: Sintra, Cascais, Lisbon region."
            ),
        },
    )
    if partner_vals:
        dirty = {}
        for field_name, value in partner_vals.items():
            current = partner[field_name]
            current_value = current.id if hasattr(current, "id") else current
            if current_value != value:
                dirty[field_name] = value
        if dirty:
            partner.write(dirty)
            changed = True

    return {"id": company.id, "partner_id": partner.id, "changed": changed, "mode": "res_company"}


def _upsert_appointment_type(env):
    if "appointment.type" not in env:
        return {"present": False, "id": None, "changed": False}

    model = env["appointment.type"].sudo()
    fields = model._fields
    admin_user = env.ref("base.user_admin", raise_if_not_found=False) or env.user
    record = model.search([("name", "=", "Fonseca Gardens Consultation")], limit=1)
    changed = False

    create_vals = {"name": "Fonseca Gardens Consultation"}
    if "appointment_duration" in fields:
        create_vals["appointment_duration"] = 1.0
    if "appointment_tz" in fields:
        create_vals["appointment_tz"] = "Europe/Lisbon"
    if "staff_user_ids" in fields:
        create_vals["staff_user_ids"] = [(6, 0, [admin_user.id])]
    if "is_published" in fields:
        create_vals["is_published"] = True
    if "website_published" in fields:
        create_vals["website_published"] = True
    if "appointment_option_ids" in fields:
        create_vals["appointment_option_ids"] = []

    if not record:
        record = model.create(_filter_vals(model, create_vals))
        changed = True

    update_vals = {}
    if "staff_user_ids" in fields and not record.staff_user_ids:
        update_vals["staff_user_ids"] = [(6, 0, [admin_user.id])]
    if "is_published" in fields and not record.is_published:
        update_vals["is_published"] = True
    if "website_published" in fields and not record.website_published:
        update_vals["website_published"] = True
    if "assign_method" in fields:
        options = [item[0] for item in (fields["assign_method"].selection or [])]
        if "chosen" in options and record.assign_method != "chosen":
            update_vals["assign_method"] = "chosen"
    if "appointment_duration" in fields and record.appointment_duration <= 0:
        update_vals["appointment_duration"] = 1.0

    if update_vals:
        record.write(update_vals)
        changed = True

    return {
        "present": True,
        "id": record.id,
        "changed": changed,
        "website_url": getattr(record, "website_url", None),
    }


def _get_target_website(env):
    website_model = env["website"].sudo()
    website = website_model.search([("domain", "ilike", "fonseca-gardens")], limit=1)
    if not website:
        website = website_model.search([("name", "=", "Fonseca Gardens")], limit=1)
    if not website:
        website = website_model.search([], order="id desc", limit=1)
    return website


def _get_target_page(env, website, url):
    page_model = env["website.page"].sudo()
    page = page_model.search([("website_id", "=", website.id), ("url", "=", url)], limit=1)
    if page:
        return page
    return page_model.search([("website_id", "=", False), ("url", "=", url)], limit=1)


def _ensure_missing_partner_pages(env, website):
    view_model = env["ir.ui.view"].sudo()
    page_model = env["website.page"].sudo()

    def _ensure(url, page_name, view_key):
        page = _get_target_page(env, website, url)
        if page and page.view_id:
            return page

        view = view_model.search([("website_id", "=", website.id), ("key", "=", view_key)], limit=1)
        if not view:
            view = view_model.create(
                {
                    "name": page_name,
                    "type": "qweb",
                    "key": view_key,
                    "website_id": website.id,
                    "arch_db": f"""<t t-name="{view_key}" name="{page_name}">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure">
      <section class="s_text_block pt32 pb32" data-snippet="s_text_block" data-name="Text">
        <div class="container">
          <h1>{page_name}</h1>
        </div>
      </section>
    </div>
  </t>
</t>""",
                }
            )

        if not page:
            page = page_model.create(
                {
                    "name": page_name,
                    "url": url,
                    "website_id": website.id,
                    "view_id": view.id,
                    "is_published": True,
                }
            )
        elif not page.view_id:
            page.write({"view_id": view.id})
        return page

    partners_page = _ensure("/partners", "Partners Network", "website.partners_network")
    fonseca_page = _ensure("/partners/fonseca-gardens", "Fonseca Gardens", "website.partners_fonseca_gardens")
    return partners_page, fonseca_page


def _upsert_partner_pages(env, website, consultation_url):
    partners_page = _get_target_page(env, website, "/partners")
    fonseca_page = _get_target_page(env, website, "/partners/fonseca-gardens")
    if not partners_page or not fonseca_page:
        partners_page, fonseca_page = _ensure_missing_partner_pages(env, website)
    if not partners_page or not fonseca_page:
        raise Exception("Required partner pages are missing; expected /partners and /partners/fonseca-gardens")


    partners_arch = """<t name="Partners Network" t-name="website.partners_network">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure">
      <section class="s_title pt32 pb16" data-snippet="s_title" data-name="Title">
        <div class="container">
          <h1 class="display-4">Partners Network</h1>
          <p class="lead">WeRa Global develops an AI-native partner ecosystem where operational businesses gain reliable digital workflows for lead generation, qualification, and conversion.</p>
        </div>
      </section>
      <section class="s_text_block pt16 pb24" data-snippet="s_text_block" data-name="Text">
        <div class="container">
          <h2 class="mb-3">Featured operational partner</h2>
          <div class="row">
            <div class="col-lg-8">
              <h3>Fonseca Gardens</h3>
              <p><strong>Above &amp; beyond. Every garden.</strong></p>
              <p>Subscription-first garden maintenance focused on Sintra, Cascais, and the Lisbon region, with transparent communication and accountable service delivery.</p>
            </div>
            <div class="col-lg-4">
              <div class="d-grid gap-2">
                <a class="btn btn-primary btn-lg" href="/partners/fonseca-gardens">View partner profile</a>
                <a class="btn btn-outline-primary" href="__CONSULTATION_URL__">Request consultation call-back</a>
                <a class="btn btn-outline-secondary" href="/contactus?partner=fonseca-gardens">Request quote</a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>""".replace("__CONSULTATION_URL__", consultation_url)

    fonseca_arch = """<t name="Fonseca Gardens" t-name="website.partners_fonseca_gardens">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure">
      <section class="s_cover pt96 pb96" data-snippet="s_cover" data-name="Cover">
        <div class="container">
          <h1 class="display-4">Fonseca Gardens</h1>
          <p class="lead">Above &amp; beyond. Every garden.</p>
          <p class="mb-0">Internationally experienced, subscription-first garden maintenance for Sintra, Cascais, and the Lisbon region.</p>
        </div>
      </section>
      <section class="s_text_block pt24 pb16" data-snippet="s_text_block" data-name="Text">
        <div class="container">
          <h2>Operational profile</h2>
          <p>Fonseca Gardens is WeRa's first field-services partner profile. The operating model prioritizes recurring maintenance quality, transparent proof-of-work communication, and a single accountable point of contact.</p>
          <p>The conversion objective is qualified demand through quote requests and consultation callback requests.</p>
        </div>
      </section>
      <section class="s_features pt16 pb24" data-snippet="s_features" data-name="Features">
        <div class="container">
          <div class="row">
            <div class="col-lg-6">
              <h3>Core services</h3>
              <ul>
                <li>Garden maintenance subscriptions</li>
                <li>Pruning and seasonal care</li>
                <li>Irrigation checks and adjustments</li>
                <li>One-time intensive garden reset</li>
              </ul>
            </div>
            <div class="col-lg-6">
              <h3>Service tiers (reference)</h3>
              <ul>
                <li>Essential: €100-150/month</li>
                <li>Standard: €150-350/month</li>
                <li>Premium: €350-500/month</li>
                <li>Estate: €500-950+/month</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
      <section class="s_text_block pt16 pb24" data-snippet="s_text_block" data-name="Text">
        <div class="container">
          <h3>Customer segments</h3>
          <p>Expat homeowners, absentee owners, and property managers who need dependable service, multilingual communication, and verifiable outcomes.</p>
          <div class="mt-3 d-flex gap-2 flex-wrap">
            <a class="btn btn-primary" href="__CONSULTATION_URL__">Request consultation call-back</a>
            <a class="btn btn-outline-primary" href="/contactus?partner=fonseca-gardens">Request quote</a>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>""".replace("__CONSULTATION_URL__", consultation_url)

    page_updates = {
        partners_page.id: {
            "name": "Partners Network",
            "meta_title": "Partners Network | WeRa Global",
            "meta_description": "WeRa Global partner network for AI-native operational growth, featuring Fonseca Gardens.",
            "arch_db": partners_arch,
        },
        fonseca_page.id: {
            "name": "Fonseca Gardens",
            "meta_title": "Fonseca Gardens | WeRa Partners",
            "meta_description": "Fonseca Gardens partner profile: subscription-first garden maintenance in Sintra, Cascais, and Lisbon.",
            "arch_db": fonseca_arch,
        },
    }

    touched = []
    for page in (partners_page, fonseca_page):
        update = page_updates[page.id]
        page.write(
            {
                "name": update["name"],
                "website_meta_title": update["meta_title"],
                "website_meta_description": update["meta_description"],
                "is_published": True,
            }
        )
        page.view_id.write({"name": update["name"], "arch_db": update["arch_db"]})
        touched.append(page.id)

    return {"updated_page_ids": touched}


def run(env):
    results = {
        "enterprise_subscription": _ensure_enterprise_subscription(env),
        "modules": [
            _ensure_module_installed(env, "website"),
            _ensure_module_installed(env, "crm"),
            _probe_module_state(env, "appointment"),
        ]
    }
    results["unsupported_module_normalization"] = _normalize_unsupported_appointment_modules(env)
    appointment_module_installed = any(
        item.get("module") == "appointment" and item.get("state") == "installed"
        for item in results["modules"]
    )
    appointment_mode = "manual_callback"
    appointment_ready = (
        APPOINTMENT_MODE == SUPPORTED_APPOINTMENT_MODE
        and appointment_module_installed
        and ("appointment.type" in env)
    )
    if appointment_ready:
        appointment_mode = SUPPORTED_APPOINTMENT_MODE
    results["company"] = _upsert_fonseca_company(env)
    website = _get_target_website(env)
    results["website"] = {
        "id": website.id,
        "name": website.name,
        "domain_normalization": _normalize_website_domain(website),
    }
    if appointment_mode == SUPPORTED_APPOINTMENT_MODE:
        results["appointment"] = _upsert_appointment_type(env)
    else:
        results["appointment"] = {
            "present": "appointment.type" in env,
            "id": None,
            "changed": False,
            "mode": "manual_callback",
        }
    consultation_url = "/appointment" if appointment_mode == SUPPORTED_APPOINTMENT_MODE else MANUAL_CONSULTATION_URL
    results["pages"] = _upsert_partner_pages(env, website, consultation_url)
    results["appointment_mode"] = appointment_mode
    results["appointment_ready"] = appointment_ready
    env.cr.commit()
    print(json.dumps(results, ensure_ascii=False))


if "env" not in globals():
    raise RuntimeError(
        "fonseca_trl4_rollout.py must be executed via Odoo shell so `env` is injected "
        "(example: odoo shell -d <db> < fonseca_trl4_rollout.py)."
    )

run(env)
