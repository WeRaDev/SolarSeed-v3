import os
from urllib.parse import urlsplit
from odoo import SUPERUSER_ID, api

MODULE_NAME = "wera_fonseca_site"
TARGET_WEBSITE_NAME = "Fonseca Gardens"
CONTACT_URL = "/contactus?partner=fonseca-gardens"
CONSULTATION_URL = "/contactus?partner=fonseca-gardens&intent=consultation"
FONSECA_WEBSITE_DOMAIN = os.environ.get(
    "FONSECA_WEBSITE_DOMAIN",
    "https://fonseca-gardens.wera-ss-pt-sn-1.tailfb390c.ts.net",
).strip()

PAGE_SPECS = (
    {
        "slug": "home",
        "page_name": "Fonseca Gardens Home",
        "menu_name": "Home",
        "url": "/",
        "sequence": 10,
        "meta_title": "Fonseca Gardens | Above & beyond. Every garden.",
        "meta_description": "Subscription-first garden maintenance in Sintra, Cascais, and Lisbon.",
        "arch_db": """<t name="Fonseca Home Skeleton" t-name="wera_fonseca_site.fonseca_home">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-skeleton">
      <section class="s_text_block fg-hero py-5">
        <div class="container">
          <p class="fg-kicker">Home</p>
          <h1><!-- SLOT: home.hero_headline -->Above &amp; beyond. Every garden.</h1>
          <p class="lead"><!-- SLOT: home.hero_subheadline -->Subscription-first garden care for expat and absentee owners with verifiable delivery.</p>
          <p class="fg-meta"><!-- SLOT: global.service_area -->Sintra • Cascais • Lisbon</p>
          <div class="fg-cta-row">
            <a class="btn btn-primary" href="/contactus?partner=fonseca-gardens&intent=quote">Request Quote</a>
            <a class="btn btn-outline-primary" href="/contactus?partner=fonseca-gardens&intent=consultation">Request Consultation Call-back</a>
          </div>
          <p class="fg-meta">Still unsure? Share your property specifics and we will reply with the right next step.</p>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>Delivery protocol for remote owners</h2>
          <ul class="fg-list">
            <li>Visit confirmation before each scheduled operation</li>
            <li>Before/after visual evidence after every visit</li>
            <li>Clear follow-up actions for issues discovered on-site</li>
          </ul>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>Why clients choose Fonseca</h2>
          <ul class="fg-list">
            <li><!-- SLOT: home.value_props[0] -->Recurring maintenance subscriptions</li>
            <li><!-- SLOT: home.value_props[1] -->Proof-of-work photo reporting after each visit</li>
            <li><!-- SLOT: home.value_props[2] -->Single accountable point of contact</li>
            <li><!-- SLOT: home.value_props[3] -->Annual contract discount options</li>
          </ul>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>What happens after your first request</h2>
          <ul class="fg-list">
            <li>Response within 4 hours with a confirmed next step</li>
            <li>On-site assessment with clear scope boundaries</li>
            <li>Written quote in English within 24 hours</li>
            <li>Recurring visits with before/after evidence reporting</li>
          </ul>
        </div>
      </section>
    </div>
  </t>
</t>""",
    },
    {
        "slug": "about",
        "page_name": "About Fonseca Gardens",
        "menu_name": "About",
        "url": "/about",
        "sequence": 20,
        "meta_title": "About Fonseca Gardens",
        "meta_description": "Founder story and trust model behind Fonseca Gardens.",
        "arch_db": """<t name="Fonseca About Skeleton" t-name="wera_fonseca_site.fonseca_about">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-skeleton">
      <section class="s_text_block fg-hero py-5">
        <div class="container">
          <p class="fg-kicker">About</p>
          <h1><!-- SLOT: global.brand_name -->Fonseca Gardens</h1>
          <p class="lead"><!-- SLOT: global.positioning -->Reliable, subscription-first garden care for clients who value trust and clarity.</p>
          <p class="fg-meta"><!-- SLOT: global.tagline -->Above &amp; beyond. Every garden.</p>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>Founder trust story</h2>
          <p><!-- SLOT: about.founder_trust_story -->Founder-led operations with international field experience and weekly accountability for every property.</p>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>How we work</h2>
          <ul class="fg-list">
            <li>Written scope before work starts</li>
            <li>Recurring schedule and confirmation flow</li>
            <li>Post-visit report with before/after evidence</li>
          </ul>
          <div class="fg-cta-row">
            <a class="btn btn-primary" href="/contactus?partner=fonseca-gardens&intent=quote">Request Quote</a>
            <a class="btn btn-outline-primary" href="/contactus?partner=fonseca-gardens&intent=consultation">Request Consultation Call-back</a>
          </div>
          <p class="fg-meta">Still unsure? Share your property specifics and we will reply with the right next step.</p>
        </div>
      </section>
    </div>
  </t>
</t>""",
    },
    {
        "slug": "services",
        "page_name": "Fonseca Gardens Services",
        "menu_name": "Services",
        "url": "/services",
        "sequence": 30,
        "meta_title": "Fonseca Gardens Services",
        "meta_description": "Core services and operating model for Fonseca Gardens.",
        "arch_db": """<t name="Fonseca Services Skeleton" t-name="wera_fonseca_site.fonseca_services">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-skeleton">
      <section class="s_text_block fg-hero py-5">
        <div class="container">
          <p class="fg-kicker">Services</p>
          <h1>Reliable service model for real properties</h1>
          <p class="lead">Structured delivery for owners who need punctual execution, clear communication, and accountable results.</p>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>Core services</h2>
          <ul class="fg-list">
            <li><!-- SLOT: services.core_services[0] -->Garden maintenance subscriptions</li>
            <li><!-- SLOT: services.core_services[1] -->Pruning and seasonal bed care</li>
            <li><!-- SLOT: services.core_services[2] -->Irrigation checks and adjustments</li>
            <li><!-- SLOT: services.core_services[3] -->One-time intensive garden reset</li>
          </ul>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>Next step</h2>
          <div class="fg-cta-row">
            <a class="btn btn-primary" href="/contactus?partner=fonseca-gardens&intent=quote">Request Quote</a>
            <a class="btn btn-outline-primary" href="/contactus?partner=fonseca-gardens&intent=consultation">Request Consultation Call-back</a>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>""",
    },
    {
        "slug": "pricing",
        "page_name": "Fonseca Gardens Pricing",
        "menu_name": "Pricing",
        "url": "/pricing",
        "sequence": 40,
        "meta_title": "Fonseca Gardens Pricing",
        "meta_description": "Pricing tiers for Fonseca subscription-first services.",
        "arch_db": """<t name="Fonseca Pricing Skeleton" t-name="wera_fonseca_site.fonseca_pricing">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-skeleton">
      <section class="s_text_block fg-hero py-5">
        <div class="container">
          <p class="fg-kicker">Pricing</p>
          <h1>Transparent pricing architecture</h1>
          <p class="lead">Clear pricing ranges and qualification flow designed to reduce uncertainty before work begins.</p>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>Pricing tiers</h2>
          <ul class="fg-list">
            <li><!-- SLOT: pricing.tiers[0] -->Essential — €100-150/month</li>
            <li><!-- SLOT: pricing.tiers[1] -->Standard — €150-350/month</li>
            <li><!-- SLOT: pricing.tiers[2] -->Premium — €350-500/month</li>
            <li><!-- SLOT: pricing.tiers[3] -->Estate — €500-950+/month</li>
          </ul>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>What every quote includes</h2>
          <ul class="fg-list">
            <li>Visit cadence and operational scope by zone</li>
            <li>Included services and optional add-ons</li>
            <li>Reporting expectations and communication channel</li>
            <li>Total monthly pricing before work starts</li>
          </ul>
          <div class="fg-cta-row">
            <a class="btn btn-primary" href="/contactus?partner=fonseca-gardens&intent=quote">Request Quote</a>
            <a class="btn btn-outline-primary" href="/contactus?partner=fonseca-gardens&intent=consultation">Request Consultation Call-back</a>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>""",
    },
    {
        "slug": "testimonials",
        "page_name": "Fonseca Gardens Testimonials",
        "menu_name": "Testimonials",
        "url": "/testimonials",
        "sequence": 55,
        "meta_title": "Fonseca Gardens Testimonials",
        "meta_description": "Client testimonial framework for Fonseca Gardens.",
        "arch_db": """<t name="Fonseca Testimonials Skeleton" t-name="wera_fonseca_site.fonseca_testimonials">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-skeleton">
      <section class="s_text_block fg-hero py-5">
        <div class="container">
          <p class="fg-kicker">Testimonials</p>
          <h1>Evidence of reliability</h1>
          <p class="lead">Client feedback focused on concrete outcomes: punctuality, communication clarity, and visible proof of work.</p>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>Suggested testimonial blocks</h2>
          <ul class="fg-list">
            <li>Communication speed and clarity</li>
            <li>Punctuality and schedule adherence</li>
            <li>Before/after reporting confidence for absentee owners</li>
          </ul>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>Use these checks before choosing any provider</h2>
          <ul class="fg-list">
            <li>Ask for written scope and pricing before the first visit</li>
            <li>Request proof-of-work workflow details in advance</li>
            <li>Confirm who owns communication and accountability</li>
          </ul>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <div class="fg-cta-row">
            <a class="btn btn-primary" href="/contactus?partner=fonseca-gardens&intent=quote">Request Quote</a>
            <a class="btn btn-outline-primary" href="/contactus?partner=fonseca-gardens&intent=consultation">Request Consultation Call-back</a>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>""",
    },
    {
        "slug": "faq",
        "page_name": "Fonseca Gardens FAQ",
        "menu_name": "FAQ",
        "url": "/faq",
        "sequence": 58,
        "meta_title": "Fonseca Gardens FAQ",
        "meta_description": "FAQ skeleton aligned to Fonseca trust and conversion guardrails.",
        "arch_db": """<t name="Fonseca FAQ Skeleton" t-name="wera_fonseca_site.fonseca_faq">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-skeleton">
      <section class="s_text_block fg-hero py-5">
        <div class="container">
          <p class="fg-kicker">FAQ</p>
          <h1>Questions sceptical buyers ask first</h1>
          <p class="lead">Direct answers designed to reduce trust gaps and speed qualified conversion.</p>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <h2>FAQ seeds</h2>
          <ul class="fg-list">
            <li><!-- SLOT: faq.seed_questions[0] -->How do you guarantee schedule reliability?</li>
            <li><!-- SLOT: faq.seed_questions[1] -->How is work verified when I am not on-site?</li>
            <li><!-- SLOT: faq.seed_questions[2] -->Do you provide transparent written quotes?</li>
            <li><!-- SLOT: faq.seed_questions[3] -->How do consultation callbacks and lead follow-up work?</li>
          </ul>
        </div>
      </section>
      <section class="s_text_block py-4">
        <div class="container">
          <div class="fg-cta-row">
            <a class="btn btn-primary" href="/contactus?partner=fonseca-gardens&intent=quote">Request Quote</a>
            <a class="btn btn-outline-primary" href="/contactus?partner=fonseca-gardens&intent=consultation">Request Consultation Call-back</a>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>""",
    },
)


def _upsert_xmlid(env, xml_name, model, res_id):
    imd = env["ir.model.data"].sudo()
    existing = imd.search([("module", "=", MODULE_NAME), ("name", "=", xml_name)], limit=1)
    if existing:
        values = {}
        if existing.model != model:
            values["model"] = model
        if existing.res_id != res_id:
            values["res_id"] = res_id
        if not existing.noupdate:
            values["noupdate"] = True
        if values:
            existing.write(values)
        return existing
    return imd.create(
        {
            "module": MODULE_NAME,
            "name": xml_name,
            "model": model,
            "res_id": res_id,
            "noupdate": True,
        }
    )


def _get_record_by_xmlid(env, xml_name, model):
    imd = env["ir.model.data"].sudo().search([("module", "=", MODULE_NAME), ("name", "=", xml_name)], limit=1)
    if not imd or imd.model != model:
        return env[model].sudo().browse()
    return env[model].sudo().browse(imd.res_id).exists()


def _target_website(env):
    website_model = env["website"].sudo()
    website = website_model.search([("name", "=", TARGET_WEBSITE_NAME)], limit=1)
    if website:
        return website
    website = website_model.search([("domain", "ilike", "fonseca")], limit=1)
    if website:
        return website
    raise ValueError("Unable to locate target website for Fonseca skeleton rollout.")


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


def _ensure_view(env, website, spec):
    view_model = env["ir.ui.view"].sudo()
    xml_name = f"view_fonseca_{spec['slug']}"
    key = f"{MODULE_NAME}.fonseca_{spec['slug']}"
    view = _get_record_by_xmlid(env, xml_name, "ir.ui.view")
    if not view:
        view = view_model.search([("key", "=", key), ("website_id", "=", website.id)], limit=1)
    if not view:
        view = view_model.create(
            {
                "name": spec["page_name"],
                "type": "qweb",
                "website_id": website.id,
                "key": key,
                "arch_db": spec["arch_db"],
            }
        )
    else:
        view.write(
            {
                "name": spec["page_name"],
                "type": "qweb",
                "website_id": website.id,
                "key": key,
                "arch_db": spec["arch_db"],
            }
        )
    _upsert_xmlid(env, xml_name, "ir.ui.view", view.id)
    return view


def _ensure_page(env, website, view, spec):
    page_model = env["website.page"].sudo()
    xml_name = f"page_fonseca_{spec['slug']}"
    page = _get_record_by_xmlid(env, xml_name, "website.page")
    if not page:
        page = page_model.search([("website_id", "=", website.id), ("url", "=", spec["url"])], limit=1)
    if not page:
        page = page_model.create(
            {
                "name": spec["page_name"],
                "website_id": website.id,
                "url": spec["url"],
                "view_id": view.id,
                "is_published": True,
                "website_meta_title": spec["meta_title"],
                "website_meta_description": spec["meta_description"],
            }
        )
    else:
        page.write(
            {
                "name": spec["page_name"],
                "website_id": website.id,
                "url": spec["url"],
                "view_id": view.id,
                "is_published": True,
                "website_meta_title": spec["meta_title"],
                "website_meta_description": spec["meta_description"],
            }
        )
    _upsert_xmlid(env, xml_name, "website.page", page.id)
    return page


def _ensure_menu(env, website, spec):
    menu_model = env["website.menu"].sudo()
    xml_name = f"menu_fonseca_{spec['slug']}"
    menu = _get_record_by_xmlid(env, xml_name, "website.menu")
    root = website.menu_id.sudo()
    if not menu:
        menu = menu_model.search(
            [("website_id", "=", website.id), ("parent_id", "=", root.id), ("url", "=", spec["url"])],
            limit=1,
        )
    values = {
        "name": spec["menu_name"],
        "url": spec["url"],
        "sequence": spec["sequence"],
        "parent_id": root.id,
        "website_id": website.id,
    }
    if not menu:
        menu = menu_model.create(values)
    else:
        menu.write(values)
    _upsert_xmlid(env, xml_name, "website.menu", menu.id)
    return menu

def _cleanup_broken_cta_routes(env, website):
    menu_model = env["website.menu"].sudo()
    stale_menus = menu_model.search(
        [
            ("url", "=", "/appointment"),
            "|",
            ("website_id", "=", website.id),
            "&",
            ("website_id", "=", False),
            ("parent_id", "=", website.menu_id.id),
        ]
    )
    count = len(stale_menus)
    if stale_menus:
        stale_menus.unlink()
    return count
def _patch_header_cta_view(env, website):
    view_model = env["ir.ui.view"].sudo()
    views = view_model.search(
        [
            ("website_id", "=", website.id),
            ("key", "=", "website.header_call_to_action"),
            ("arch_db", "ilike", "/appointment"),
        ]
    )
    updated = 0
    for view in views:
        patched_arch = (view.arch_db or "").replace(
            'href="/appointment"',
            'href="/contactus?partner=fonseca-gardens&intent=consultation"',
        )
        if patched_arch != (view.arch_db or ""):
            view.write({"arch_db": patched_arch})
            updated += 1
    return updated


def _apply_phase2(env):
    website = _target_website(env)
    domain_normalization = _normalize_website_domain(website)
    results = []
    for spec in PAGE_SPECS:
        view = _ensure_view(env, website, spec)
        page = _ensure_page(env, website, view, spec)
        menu = _ensure_menu(env, website, spec)
        results.append(
            {
                "slug": spec["slug"],
                "url": page.url,
                "page_id": page.id,
                "view_id": view.id,
                "menu_id": menu.id,
            }
        )
    stale_menu_count = _cleanup_broken_cta_routes(env, website)
    header_cta_patched = _patch_header_cta_view(env, website)
    return {
        "website_id": website.id,
        "website_name": website.name,
        "website_domain_normalization": domain_normalization,
        "pages": results,
        "stale_appointment_menus_removed": stale_menu_count,
        "header_cta_views_patched": header_cta_patched,
    }


def post_init_hook(env):
    if not isinstance(env, api.Environment):
        env = api.Environment(env, SUPERUSER_ID, {})
    _apply_phase2(env)
    env.cr.commit()
