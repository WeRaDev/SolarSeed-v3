import json


TARGET_WEBSITE_NAME = "Fonseca Gardens"
CONTACT_URL = "/contactus?partner=fonseca-gardens"
CONSULTATION_URL = "/contactus?intent=consultation&amp;partner=fonseca-gardens"
WHATSAPP_URL = "https://wa.me/351000000000?text=Hello+Fonseca+Gardens"
LAYOUT_REFERENCE_IMAGE = "odoo-app/content/Fonseca Gardens/template.example.jpeg"
BUSINESS_SOURCE_OF_TRUTH = "odoo-app/content/fonseca_gardens_source_of_truth.json"

BRAND_TAGLINE = "Above &amp; beyond. Every garden."
BRAND_POSITIONING = (
    "Fonseca Gardens delivers subscription-first garden care for Sintra, Cascais, and Lisbon "
    "clients who value reliability, communication, and accountable results."
)
SERVICE_AREA = "Sintra • Cascais • Lisbon • Oeiras (by arrangement)"
ANNUAL_DISCOUNT = "10–15% savings available for annual commitments."
RESPONSE_TIME_PROMISE = "Response within 4 hours on WhatsApp or email."
QUOTE_TIME_PROMISE = "Written quote in English within 24 hours."
LANGUAGE_SUPPORT = "English and Portuguese communication, with Russian support on request."
NO_SURPRISE_PRICING = "No surprise invoices. No hidden charges."
PHOTO_REPORTING_PROMISE = "Before/after photo report after every scheduled visit."
REMOTE_OWNER_CTA_URL = "/contactus?intent=remote-owner&amp;partner=fonseca-gardens"
RESEARCH_REPORT_PATH = "/Users/mikhailananyin/Documents/WeRa Global/Customers/Fonseca Gardens/Fonseca Gardens — Expat Pain Points & Website Content Guidelines.md"
SERVICE_BADGES = [
    "Response within 4 hours",
    "Written quote in English in 24h",
    "Before/after photo report every visit",
    "English/PT + Russian support on request",
]
CORE_SERVICES = [
    ("fa-leaf", "Garden maintenance subscriptions", "Weekly or fortnightly recurring care with accountable scheduling."),
    ("fa-scissors", "Pruning and seasonal bed care", "Correct timing and structure management for healthier growth."),
    ("fa-tint", "Irrigation checks and adjustments", "Inspection and optimisation to reduce stress and water waste."),
    ("fa-bug", "Plant health checks", "Preventive monitoring with practical corrective recommendations."),
    ("fa-refresh", "One-time intensive garden reset", "Recovery option for neglected gardens before subscription start."),
    ("fa-camera", "Proof-of-work reporting", "Before/after photos sent after every visit for full visibility."),
]
ADD_ON_SERVICES = [
    "Pool and pond surroundings maintenance",
    "One-time intensive reset and recovery",
    "Gutter and hardscape seasonal cleaning",
    "Tree shaping and hedge structuring (quoted separately)",
]
PRICING_TIERS = [
    ("Essential", "€100–150/mo", "Small gardens with recurring essentials and photo report."),
    ("Standard", "€150–350/mo", "All essentials plus pruning, irrigation checks, and WhatsApp updates."),
    ("Premium", "€350–500/mo", "Larger properties with layered maintenance and higher visit complexity."),
    ("Estate", "€500–950+/mo", "Full multi-zone management for estates and absentee-owner needs."),
]
TRUST_PILLARS = [
    ("We show up when scheduled", "Visits are planned, confirmed, and executed with clear follow-up."),
    ("You see exactly what was done", "Every visit includes a before/after photo report and short summary."),
    ("Clear written pricing", "Quotes are delivered in writing in English before work begins."),
]
PROCESS_STEPS = [
    ("1. Contact us", "WhatsApp, email, or form — response within 4 hours."),
    ("2. Free site visit", "Scheduled assessment with clear arrival window and no guesswork."),
    ("3. Written quote in 24h", "Transparent scope and pricing in English before work starts."),
    ("4. Subscription starts", "Consistent recurring schedule agreed and followed."),
    ("5. Photo report after each visit", "Before/after evidence with short summary to your phone."),
    ("6. Monthly adjustment on request", "Need changes before guests arrive? We adapt quickly."),
]
PORTFOLIO_CASE_TEMPLATES = [
    ("Residential consistency programme", "Cascais", "Maintenance reliability and visual quality over 90 days."),
    ("Seasonal reset project", "Sintra", "Recovery after missed cycles and irrigation imbalance."),
    ("Absentee-owner care plan", "Lisbon region", "Predictable upkeep with remote reporting."),
]
FEEDBACK_THEMES = [
    "Reliability and punctuality after repeated no-show experiences",
    "Clarity of communication in English",
    "Visible proof-of-work for remote homeowners",
]
SEASONAL_TOPICS = [
    ("Spring reset checklist", "Restore growth rhythm after winter with sequencing that prevents overwork."),
    ("Summer irrigation tuning", "Water-efficient adjustments for heat resilience and healthier roots."),
    ("Autumn pruning priorities", "Structural pruning decisions that protect the next growth cycle."),
]
FAQ_ITEMS = [
    (
        "Will you actually show up when you say you will?",
        "Yes. Visits are scheduled, confirmed by WhatsApp the day before, and followed by a photo report. If weather or emergencies force changes, we communicate in advance and reschedule quickly.",
    ),
    (
        "I am abroad most of the year. How do I verify work is done?",
        "After each visit we send before/after photos with a short summary, so you can track your garden from anywhere without chasing updates.",
    ),
    (
        "Do you communicate in English? Is Russian support possible?",
        "All quotes and updates are provided in English and Portuguese. Russian support is available on request for clients who need it.",
    ),
    (
        "How do I know pricing is fair and transparent?",
        "Pricing tiers are published, quotes are written before work starts, and no extra charge is added without prior approval.",
    ),
    (
        "What if I am not satisfied with a visit?",
        "Tell us directly and we return to correct it. Accountability and long-term trust are core to the service model.",
    ),
    (
        "Can I start with a one-time tidy-up before committing?",
        "Yes. One-time intensive reset visits are available and can transition into a recurring subscription if you choose.",
    ),
]
TESTIMONIAL_SNIPPETS = [
    (
        "After three companies that never responded, Fonseca finally gave us reliability. We live in London and still feel fully in control thanks to weekly photo reports.",
        "D.H., British homeowner — Cascais",
    ),
    (
        "We needed clear English communication and someone who actually follows through. The monthly plan has been consistent and transparent from day one.",
        "M.R., American resident — Sintra",
    ),
    (
        "As absentee owners, proof of work matters more than promises. The before/after updates and quick WhatsApp responses are exactly what we needed.",
        "L.K., international property owner — Lisbon region",
    ),
]
PHOTO_REPORTING_POINTS = [
    "Before/after photos after every scheduled visit",
    "Short summary of completed tasks and observations",
    "Direct WhatsApp or email delivery for remote owners",
]
SOURCE_OF_TRUTH_MAPPING = {
    "layout_reference": LAYOUT_REFERENCE_IMAGE,
    "business_source": BUSINESS_SOURCE_OF_TRUTH,
    "expat_guidelines": RESEARCH_REPORT_PATH,
    "tagline": "brand_core.primary_tagline",
    "positioning": "brand_core.positioning_statement",
    "service_area": "brand_core.service_area_focus",
    "pricing_tiers": "service_offering_for_pages.pricing_tiers_reference",
    "core_services": "service_offering_for_pages.core_services",
    "copy_guardrails": "critical_analysis.copy_guardrails",
}

STYLE_BLOCK = """
<style id="fonseca-shared-style">
  .fg-shell {
    --fg-green-dark: #123e33;
    --fg-green-mid: #1f5d48;
    --fg-green-soft: #2f6f58;
    --fg-cream: #f7f1e6;
    --fg-gold: #b98245;
    --fg-text: #1f2a26;
    --fg-muted: #4f5f57;
  }
  .fg-hero-shell {
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid #d6e0d6;
    box-shadow: 0 16px 36px rgba(12, 36, 28, 0.14);
    background: #fff;
  }
  .fg-hero-copy {
    background: linear-gradient(180deg, #f8f3e9 0%, #f5eddd 100%);
    color: var(--fg-text);
    padding: 2.6rem 2.1rem;
  }
  .fg-kicker {
    display: inline-block;
    margin-bottom: .8rem;
    text-transform: uppercase;
    font-size: .78rem;
    letter-spacing: .08em;
    color: var(--fg-green-mid);
    font-weight: 800;
  }
  .fg-hero-copy h1 {
    font-size: clamp(1.95rem, 4vw, 3rem);
    color: var(--fg-green-dark);
    line-height: 1.06;
    margin-bottom: .75rem;
    font-weight: 800;
  }
  .fg-hero-copy h2 {
    font-size: clamp(1rem, 2vw, 1.45rem);
    color: var(--fg-gold);
    margin-bottom: .8rem;
    font-weight: 700;
  }
  .fg-hero-copy p {
    color: var(--fg-muted);
    font-size: 1.02rem;
    margin-bottom: 1rem;
  }
  .fg-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: .42rem;
    margin-bottom: 1.1rem;
  }
  .fg-badge {
    display: inline-block;
    padding: .28rem .7rem;
    border-radius: 999px;
    border: 1px solid #d2ddd3;
    background: #e8eee8;
    color: #275041;
    font-size: .81rem;
    font-weight: 700;
  }
  .fg-cta-row {
    display: flex;
    flex-wrap: wrap;
    gap: .58rem;
  }
  .fg-btn-primary {
    background: var(--fg-green-dark);
    border: 1px solid var(--fg-green-dark);
    color: #fff !important;
    border-radius: 999px;
    font-weight: 700;
    padding: .66rem 1.16rem;
  }
  .fg-btn-secondary {
    border: 1px solid var(--fg-green-dark);
    color: var(--fg-green-dark) !important;
    border-radius: 999px;
    font-weight: 700;
    padding: .66rem 1.16rem;
    background: transparent;
  }
  .fg-btn-tertiary {
    border: 1px solid #a4b4ab;
    color: #2e4f43 !important;
    border-radius: 999px;
    font-weight: 700;
    padding: .66rem 1.16rem;
    background: #ffffff;
  }
  .fg-hero-visual {
    min-height: 420px;
    background: linear-gradient(145deg, #65b8ee 0%, #8dd7ff 35%, #96d972 100%);
    padding: 2rem;
    position: relative;
    color: #fff;
    display: flex;
    align-items: flex-end;
  }
  .fg-hero-visual:before {
    content: "";
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 79% 22%, rgba(255, 255, 255, .76) 0 10%, transparent 11%),
      radial-gradient(circle at 66% 18%, rgba(255, 255, 255, .5) 0 8%, transparent 9%),
      linear-gradient(180deg, rgba(13, 50, 40, .08) 0%, rgba(13, 50, 40, .55) 95%);
    pointer-events: none;
  }
  .fg-hero-note {
    position: relative;
    z-index: 2;
    background: rgba(13, 55, 44, .78);
    border: 1px solid rgba(255,255,255,.26);
    border-radius: 14px;
    padding: .9rem .95rem;
    width: min(420px, 100%);
    backdrop-filter: blur(2px);
  }
  .fg-hero-note h3 {
    font-size: 1rem;
    margin-bottom: .45rem;
    font-weight: 700;
  }
  .fg-hero-note ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  .fg-hero-note li {
    margin: .32rem 0;
    padding-left: 1.02rem;
    position: relative;
    line-height: 1.35;
    font-size: .91rem;
  }
  .fg-hero-note li:before {
    content: "•";
    position: absolute;
    left: 0;
    top: -.08rem;
    color: #ffd8aa;
    font-size: 1.1rem;
  }
  .fg-section-kicker {
    margin-bottom: .2rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 800;
    font-size: .8rem;
    color: var(--fg-green-mid);
  }
  .fg-section-title {
    color: var(--fg-green-dark);
    font-weight: 800;
    margin-bottom: 1rem;
    font-size: clamp(1.4rem, 2.8vw, 2.1rem);
  }
  .fg-card {
    height: 100%;
    border: 1px solid #dde8dd;
    border-radius: 14px;
    padding: .95rem .9rem;
    background: #fff;
    box-shadow: 0 8px 20px rgba(11, 45, 33, .05);
  }
  .fg-card-icon {
    width: 48px;
    height: 48px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #d2ded4;
    color: var(--fg-green-mid);
    margin-bottom: .55rem;
    font-size: 1.2rem;
    background: #fbfdfb;
  }
  .fg-card h3 {
    color: var(--fg-green-dark);
    font-size: 1rem;
    margin-bottom: .35rem;
    font-weight: 700;
  }
  .fg-card p {
    margin: 0;
    color: var(--fg-muted);
    font-size: .95rem;
  }
  .fg-list-clean {
    margin: 0;
    padding-left: 1.1rem;
    color: var(--fg-muted);
  }
  .fg-list-clean li {
    margin-bottom: .35rem;
  }
  .fg-strip {
    background: linear-gradient(135deg, #0f4639 0%, #1a5c48 100%);
    border-radius: 16px;
    color: #fff;
    box-shadow: 0 14px 30px rgba(10, 43, 33, .2);
  }
  .fg-strip-item {
    display: flex;
    align-items: center;
    gap: .7rem;
    padding: 1rem 1.1rem;
  }
  .fg-strip-item + .fg-strip-item {
    border-top: 1px solid rgba(255,255,255,.16);
  }
  .fg-strip-icon {
    width: 45px;
    height: 45px;
    border: 1px solid rgba(255,255,255,.34);
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
  }
  .fg-strip-copy strong {
    display: block;
    font-size: .8rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    opacity: .84;
    margin-bottom: .1rem;
  }
  .fg-strip-copy span {
    display: block;
    font-size: .98rem;
    font-weight: 700;
    line-height: 1.25;
  }
  .fg-strip-action {
    margin-left: auto;
  }
  .fg-strip-action a {
    color: #fff !important;
    border: 1px solid rgba(255,255,255,.5);
    border-radius: 999px;
    padding: .42rem .88rem;
    font-weight: 700;
  }
  .fg-muted-note {
    color: var(--fg-muted);
    margin-top: .8rem;
    font-size: .95rem;
  }
  @media (min-width: 992px) {
    .fg-strip-item + .fg-strip-item {
      border-top: none;
      border-left: 1px solid rgba(255,255,255,.16);
    }
    .fg-strip .row {
      align-items: stretch;
    }
    .fg-strip-item {
      height: 100%;
    }
  }
</style>
"""


def _get_website(env):
    website = env["website"].sudo().search([("name", "=", TARGET_WEBSITE_NAME)], limit=1)
    if not website:
        raise Exception(f"Website '{TARGET_WEBSITE_NAME}' not found.")
    return website


def _ensure_page(env, website, spec):
    page_model = env["website.page"].sudo()
    page = page_model.search([("website_id", "=", website.id), ("url", "=", spec["url"])], limit=1)
    created = False
    if not page:
        created_info = website.with_context(website_id=website.id).new_page(
            name=spec["name"],
            add_menu=False,
            page_title=spec["name"],
        )
        page = page_model.browse(created_info["page_id"]).sudo()
        page.write({"url": spec["url"]})
        created = True

    page.write(
        {
            "name": spec["name"],
            "is_published": True,
            "website_meta_title": spec["meta_title"],
            "website_meta_description": spec["meta_description"],
        }
    )
    page.view_id.sudo().write({"name": spec["name"], "arch_db": spec["arch"]})
    return {
        "url": spec["url"],
        "id": page.id,
        "view_id": page.view_id.id,
        "created": created,
        "published": page.is_published,
    }


def _ensure_menu(env, website, targets):
    menu_model = env["website.menu"].sudo()
    root = website.menu_id.sudo()
    current_children = menu_model.search([("website_id", "=", website.id), ("parent_id", "=", root.id)], order="sequence, id")
    children_by_sequence = {m.sequence: m for m in current_children}
    touched = []

    for target in targets:
        menu = menu_model.search(
            [("website_id", "=", website.id), ("parent_id", "=", root.id), ("url", "=", target["url"])],
            limit=1,
        )
        created = False
        if not menu:
            menu = children_by_sequence.get(target["sequence"])
        if menu:
            menu.write(
                {
                    "name": target["name"],
                    "url": target["url"],
                    "sequence": target["sequence"],
                    "parent_id": root.id,
                    "website_id": website.id,
                }
            )
        else:
            menu = menu_model.create(
                {
                    "name": target["name"],
                    "url": target["url"],
                    "sequence": target["sequence"],
                    "parent_id": root.id,
                    "website_id": website.id,
                }
            )
            created = True
        touched.append(
            {
                "id": menu.id,
                "name": menu.name,
                "url": menu.url or "",
                "sequence": menu.sequence,
                "created": created,
            }
        )
    return touched


def _chips_markup(chips):
    return "".join(f"<span class=\"fg-badge\">{chip}</span>" for chip in chips)


def _bullet_list(items):
    return "".join(f"<li>{item}</li>" for item in items)


def _service_cards(cards):
    return "".join(
        f"""
          <div class="col-12 col-md-6 col-lg-4">
            <div class="fg-card">
              <span class="fg-card-icon"><i class="fa {icon}"></i></span>
              <h3>{title}</h3>
              <p>{description}</p>
            </div>
          </div>
"""
        for icon, title, description in cards
    )


def _trust_cards(cards):
    return "".join(
        f"""
          <div class="col-12 col-lg-4">
            <div class="fg-card">
              <h3>{title}</h3>
              <p>{description}</p>
            </div>
          </div>
"""
        for title, description in cards
    )


def _pricing_cards(cards):
    return "".join(
        f"""
          <div class="col-12 col-md-6 col-lg-3">
            <div class="fg-card">
              <h3>{name}</h3>
              <p><strong>{price}</strong></p>
              <p class="mt-2">{description}</p>
            </div>
          </div>
"""
        for name, price, description in cards
    )


def _process_cards(steps):
    return "".join(
        f"""
          <div class="col-12 col-lg-4">
            <div class="fg-card">
              <h3>{title}</h3>
              <p>{description}</p>
            </div>
          </div>
"""
        for title, description in steps
    )


def _portfolio_cards(entries):
    return "".join(
        f"""
          <div class="col-12 col-lg-4">
            <div class="fg-card">
              <h3>{name}</h3>
              <p><strong>Area:</strong> {area}</p>
              <p class="mt-2">{outcome}</p>
            </div>
          </div>
"""
        for name, area, outcome in entries
    )


def _seasonal_cards(entries):
    return "".join(
        f"""
          <div class="col-12 col-lg-4">
            <div class="fg-card">
              <h3>{title}</h3>
              <p>{description}</p>
            </div>
          </div>
"""
        for title, description in entries
    )

def _testimonial_cards(entries):
    return "".join(
        f"""
          <div class="col-12 col-lg-4">
            <div class="fg-card">
              <p>"{quote}"</p>
              <p class="fg-muted-note"><strong>{byline}</strong></p>
            </div>
          </div>
"""
        for quote, byline in entries
    )


def _faq_cards(entries):
    return "".join(
        f"""
          <div class="col-12">
            <div class="fg-card">
              <h3>{question}</h3>
              <p>{answer}</p>
            </div>
          </div>
"""
        for question, answer in entries
    )


def _hero_section(kicker, title, subtitle, body, right_title, right_points, chips):
    return f"""
      <section class="pt36 pb24" data-snippet="s_text_block" data-name="Template Hero">
        <div class="container">
          <div class="fg-hero-shell">
            <div class="row g-0">
              <div class="col-lg-6">
                <div class="fg-hero-copy">
                  <span class="fg-kicker">{kicker}</span>
                  <h1>{title}</h1>
                  <h2>{subtitle}</h2>
                  <p>{body}</p>
                  <p class="mb-2"><strong>Service area:</strong> {SERVICE_AREA}</p>
                  <div class="fg-chip-row">
                    {_chips_markup(chips)}
                  </div>
                  <div class="fg-cta-row">
                    <a class="btn fg-btn-primary" href="{WHATSAPP_URL}" target="_blank" rel="noopener">Send us a WhatsApp — no forms, no waiting</a>
                    <a class="btn fg-btn-secondary" href="{CONSULTATION_URL}">Get a free site visit</a>
                    <a class="btn fg-btn-tertiary" href="{REMOTE_OWNER_CTA_URL}">Managing your property from abroad?</a>
                  </div>
                </div>
              </div>
              <div class="col-lg-6">
                <div class="fg-hero-visual">
                  <div class="fg-hero-note">
                    <h3>{right_title}</h3>
                    <ul>
                      {_bullet_list(right_points)}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
"""


def _conversion_strip():
    return f"""
      <section class="pt8 pb36" data-snippet="s_text_block" data-name="Conversion Strip">
        <div class="container">
          <div class="fg-strip">
            <div class="row g-0">
              <div class="col-lg-6">
                <div class="fg-strip-item">
                  <span class="fg-strip-icon"><i class="fa fa-calendar"></i></span>
                  <div class="fg-strip-copy">
                    <strong>Fast response, no ghosting</strong>
                    <span>{RESPONSE_TIME_PROMISE} {QUOTE_TIME_PROMISE}</span>
                  </div>
                  <div class="fg-strip-action">
                    <a class="btn btn-sm" href="{WHATSAPP_URL}" target="_blank" rel="noopener">Start on WhatsApp</a>
                  </div>
                </div>
              </div>
              <div class="col-lg-6">
                <div class="fg-strip-item">
                  <span class="fg-strip-icon"><i class="fa fa-phone"></i></span>
                  <div class="fg-strip-copy">
                    <strong>Built for expat and remote owners</strong>
                    <span>{PHOTO_REPORTING_PROMISE} {LANGUAGE_SUPPORT}</span>
                  </div>
                  <div class="fg-strip-action">
                    <a class="btn btn-sm" href="{CONSULTATION_URL}">Request site visit</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
"""


def _home_arch():
    return f"""<t name="Fonseca Gardens Home" t-name="website.fonseca_home">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-shell">
      {STYLE_BLOCK}
      {_hero_section(
        "Fonseca Gardens",
        "Finally, a gardener who actually shows up.",
        "Gardens that get looked after — even when you're not there.",
        "We know the pattern expats face: requests ignored, promised visits missed, and no proof when work is supposedly done. Fonseca Gardens was built to replace that uncertainty with accountable, subscription-based care.",
        "Why expat clients switch to Fonseca",
        [
          RESPONSE_TIME_PROMISE,
          QUOTE_TIME_PROMISE,
          PHOTO_REPORTING_PROMISE,
          NO_SURPRISE_PRICING,
        ],
        SERVICE_BADGES,
      )}
      <section class="pt16 pb8" data-snippet="s_features" data-name="Core Services">
        <div class="container">
          <p class="fg-section-kicker">Core services</p>
          <h2 class="fg-section-title">Garden care system built for reliability</h2>
          <div class="row g-3">
            {_service_cards(CORE_SERVICES)}
          </div>
        </div>
      </section>
      <section class="pt12 pb8" data-snippet="s_features" data-name="How It Works">
        <div class="container">
          <p class="fg-section-kicker">How it works</p>
          <h2 class="fg-section-title">A process built to remove uncertainty</h2>
          <div class="row g-3">
            {_process_cards(PROCESS_STEPS)}
          </div>
        </div>
      </section>
      <section class="pt12 pb8" data-snippet="s_text_block" data-name="Photo Reporting">
        <div class="container">
          <div class="row g-3">
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>Your garden stays visible from anywhere</h3>
                <p>Whether you live in Cascais full-time or visit twice a year, each scheduled visit is documented so you always know what happened on site.</p>
                <ul class="fg-list-clean mt-2">
                  {_bullet_list(PHOTO_REPORTING_POINTS)}
                </ul>
              </div>
            </div>
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>Built for remote ownership reality</h3>
                <p>Absentee owners, property managers, and expat families use the same workflow: predictable schedule, written communication, and verifiable outcomes.</p>
                <p class="fg-muted-note">{LANGUAGE_SUPPORT}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section class="pt12 pb8" data-snippet="s_features" data-name="Trust Pillars">
        <div class="container">
          <p class="fg-section-kicker">Why clients choose us</p>
          <h2 class="fg-section-title">Trust signals designed for sceptical expat clients</h2>
          <div class="row g-3">
            {_trust_cards(TRUST_PILLARS)}
          </div>
          <p class="fg-muted-note">{NO_SURPRISE_PRICING} {ANNUAL_DISCOUNT}</p>
        </div>
      </section>
      <section class="pt12 pb8" data-snippet="s_text_block" data-name="Expat Testimonials">
        <div class="container">
          <p class="fg-section-kicker">Expat testimonials</p>
          <h2 class="fg-section-title">Specific feedback from clients who were previously let down</h2>
          <div class="row g-3">
            {_testimonial_cards(TESTIMONIAL_SNIPPETS)}
          </div>
          <p class="fg-muted-note">{ANNUAL_DISCOUNT}</p>
        </div>
      </section>
      {_conversion_strip()}
    </div>
  </t>
</t>"""


def _about_arch():
    return f"""<t name="About Fonseca Gardens" t-name="website.fonseca_about">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-shell">
      {STYLE_BLOCK}
      {_hero_section(
        "About",
        "Before you let anyone near your garden, know who you are hiring.",
        "Founder-led service with international standards and local accountability.",
        "Fonseca Gardens is built on hands-on work across South Africa, Israel, France, UK, and Portugal — created for homeowners who are tired of inconsistent communication and missed commitments.",
        "Founder credibility snapshot",
        [
          "Formal farm-school and horticulture foundation",
          "10+ years of practical cross-country field experience",
          "Direct client communication from assessment to reporting",
          "Quality baseline: above and beyond on every visit",
        ],
        ["Founder-led", "International experience", "Trust-first execution"],
      )}
      <section class="pt16 pb8" data-snippet="s_text_block" data-name="Founder Statement">
        <div class="container">
          <div class="row g-3">
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>Why this company exists</h3>
                <p>Fonseca Gardens was built to solve the reliability gap many expat homeowners experience in Portugal: no-shows, unclear communication, and unpredictable outcomes.</p>
                <p class="fg-muted-note">“This is not a side business. It is what I do — every client, every visit, every week.”</p>
              </div>
            </div>
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>Communication standard</h3>
                <p>{LANGUAGE_SUPPORT}</p>
                <p>{RESPONSE_TIME_PROMISE}</p>
                <p>{QUOTE_TIME_PROMISE}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section class="pt12 pb8" data-snippet="s_features" data-name="Trust Pillars">
        <div class="container">
          <p class="fg-section-kicker">Positioning</p>
          <h2 class="fg-section-title">Premium care without corporate distance</h2>
          <div class="row g-3">
            {_trust_cards(TRUST_PILLARS)}
          </div>
        </div>
      </section>
      <section class="pt12 pb8" data-snippet="s_features" data-name="Process">
        <div class="container">
          <p class="fg-section-kicker">How we work</p>
          <h2 class="fg-section-title">Structured onboarding and recurring accountability</h2>
          <div class="row g-3">
            {_process_cards(PROCESS_STEPS)}
          </div>
        </div>
      </section>
      {_conversion_strip()}
    </div>
  </t>
</t>"""


def _services_arch():
    return f"""<t name="Fonseca Gardens Services" t-name="website.fonseca_services">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-shell">
      {STYLE_BLOCK}
      {_hero_section(
        "Services",
        "Services designed for expat homeowners and absentee owners.",
        "Clear scope. Clear pricing. Clear accountability.",
        "Every plan is subscription-first, documented in writing, and supported by post-visit proof-of-work reporting so you never need to chase updates.",
        "Service model commitments",
        [
          RESPONSE_TIME_PROMISE,
          QUOTE_TIME_PROMISE,
          PHOTO_REPORTING_PROMISE,
          NO_SURPRISE_PRICING,
        ],
        ["Subscription-first", "Written scope", "Proof-of-work workflow"],
      )}
      <section class="pt16 pb8" data-snippet="s_features" data-name="Core Service Cards">
        <div class="container">
          <p class="fg-section-kicker">Core scope</p>
          <h2 class="fg-section-title">Included in recurring maintenance plans</h2>
          <div class="row g-3">
            {_service_cards(CORE_SERVICES)}
          </div>
        </div>
      </section>
      <section class="pt12 pb8" data-snippet="s_text_block" data-name="Add-ons">
        <div class="container">
          <div class="row g-3">
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>Add-on services</h3>
                <ul class="fg-list-clean">
                  {_bullet_list(ADD_ON_SERVICES)}
                </ul>
              </div>
            </div>
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>Coverage and planning</h3>
                <p><strong>Service area:</strong> {SERVICE_AREA}</p>
                <p class="mt-2">Scope is finalised after assessment so every property receives a realistic schedule and measurable quality target.</p>
                <p class="mt-2">{NO_SURPRISE_PRICING} {QUOTE_TIME_PROMISE}</p>
                <p class="fg-muted-note">{ANNUAL_DISCOUNT}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section class="pt12 pb8" data-snippet="s_text_block" data-name="Proof Of Work">
        <div class="container">
          <div class="row g-3">
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>Proof-of-work is a core feature, not an add-on</h3>
                <ul class="fg-list-clean">
                  {_bullet_list(PHOTO_REPORTING_POINTS)}
                </ul>
              </div>
            </div>
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>Ideal for remote ownership</h3>
                <p>Many clients are not on-site weekly. The reporting workflow keeps property managers and owners aligned without extra coordination overhead.</p>
                <p class="fg-muted-note">{LANGUAGE_SUPPORT}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      {_conversion_strip()}
    </div>
  </t>
</t>"""


def _pricing_arch():
    return f"""<t name="Fonseca Gardens Pricing" t-name="website.fonseca_pricing">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-shell">
      {STYLE_BLOCK}
      {_hero_section(
        "Pricing",
        "Transparent pricing for expat homeowners",
        "Know what you pay for before any work starts.",
        "Pricing is published in clear ranges to prevent the uncertainty and overcharging many expat owners report in local service markets.",
        "Pricing trust commitments",
        [
          "Published monthly ranges from €100",
          QUOTE_TIME_PROMISE,
          NO_SURPRISE_PRICING,
          "Annual commitments reduce total cost",
        ],
        ["Transparent tiers", "Written quotes", "No hidden fees"],
      )}
      <section class="pt16 pb8" data-snippet="s_features" data-name="Pricing Cards">
        <div class="container">
          <p class="fg-section-kicker">Subscription tiers</p>
          <h2 class="fg-section-title">Choose the level that fits your property</h2>
          <div class="row g-3">
            {_pricing_cards(PRICING_TIERS)}
          </div>
          <p class="fg-muted-note">{NO_SURPRISE_PRICING} {ANNUAL_DISCOUNT}</p>
        </div>
      </section>
      <section class="pt12 pb8" data-snippet="s_text_block" data-name="Quote Standards">
        <div class="container">
          <div class="row g-3">
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>What every written quote includes</h3>
                <ul class="fg-list-clean">
                  {_bullet_list([
                    "Visit frequency and scope by area",
                    "Included services and optional add-ons",
                    "Expected response and reporting workflow",
                    "Total monthly price before work starts",
                  ])}
                </ul>
              </div>
            </div>
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>Designed for peace of mind</h3>
                <p>If you have been burned by vague quotes, this model is designed to remove ambiguity: clear scope, clear price, clear accountability.</p>
                <p class="fg-muted-note">{PHOTO_REPORTING_PROMISE}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      {_conversion_strip()}
    </div>
  </t>
</t>"""


def _portfolio_arch():
    return f"""<t name="Fonseca Gardens Portfolio" t-name="website.fonseca_portfolio">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-shell">
      {STYLE_BLOCK}
      {_hero_section(
        "Portfolio",
        "Before/after evidence of recurring quality",
        "Real project proof for homeowners who need certainty.",
        "This portfolio format is designed for sceptical clients: documented challenge, clear intervention, and visible result over time.",
        "Case-study documentation standard",
        [
          "Show before/after visual progression",
          "Describe challenge and intervention",
          "Keep location to municipality level only",
          "Add dates and maintenance duration",
        ],
        ["Before/after evidence", "Outcome-driven", "Client-safe privacy"],
      )}
      <section class="pt16 pb8" data-snippet="s_features" data-name="Portfolio Grid">
        <div class="container">
          <p class="fg-section-kicker">Portfolio structure</p>
          <h2 class="fg-section-title">Suggested case-study formats</h2>
          <div class="row g-3">
            {_portfolio_cards(PORTFOLIO_CASE_TEMPLATES)}
          </div>
        </div>
      </section>
      {_conversion_strip()}
    </div>
  </t>
</t>"""


def _testimonials_arch():
    return f"""<t name="Fonseca Gardens Testimonials" t-name="website.fonseca_testimonials">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-shell">
      {STYLE_BLOCK}
      {_hero_section(
        "Testimonials",
        "Specific feedback from expat clients",
        "Outstanding. Guaranteed.",
        "Clients in this market often distrust generic five-star claims. These testimonials focus on concrete reliability outcomes: response speed, punctuality, and visible proof-of-work.",
        "What these testimonials prove",
        FEEDBACK_THEMES,
        ["Named initials", "Location context", "Outcome-specific details"],
      )}
      <section class="pt16 pb8" data-snippet="s_text_block" data-name="Testimonial Quotes">
        <div class="container">
          <p class="fg-section-kicker">Client voices</p>
          <h2 class="fg-section-title">Trust built through specific lived experiences</h2>
          <div class="row g-3">
            {_testimonial_cards(TESTIMONIAL_SNIPPETS)}
          </div>
        </div>
      </section>
      <section class="pt12 pb8" data-snippet="s_text_block" data-name="Review Guidance">
        <div class="container">
          <div class="row g-3">
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>How to keep this page credible</h3>
                <ul class="fg-list-clean">
                  {_bullet_list([
                    "Use real client initials and municipality only",
                    "Keep references to specific outcomes, not generic praise",
                    "Prefer WhatsApp-style language over polished ad copy",
                    "Link to verified Google Business feedback where possible",
                  ])}
                </ul>
              </div>
            </div>
            <div class="col-12 col-lg-6">
              <div class="fg-card">
                <h3>Review collection workflow</h3>
                <p>Request testimonials after the second or third successful visit, when clients already received multiple photo reports and can describe concrete service consistency.</p>
                <p class="fg-muted-note">{RESPONSE_TIME_PROMISE}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      {_conversion_strip()}
    </div>
  </t>
</t>"""


def _faq_arch():
    return f"""<t name="Fonseca Gardens FAQ" t-name="website.fonseca_faq">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-shell">
      {STYLE_BLOCK}
      {_hero_section(
        "FAQ",
        "Questions sceptical expat homeowners actually ask",
        "Direct answers, no vague promises.",
        "This page is written for clients who have already been let down by no-shows, unclear pricing, and weak communication.",
        "Core concerns we address",
        [
          "Punctuality and confirmation workflow",
          "Proof-of-work for remote owners",
          "Language clarity and response speed",
          "Transparent pricing without hidden extras",
        ],
        ["No-show prevention", "Remote-owner visibility", "Pricing clarity"],
      )}
      <section class="pt16 pb8" data-snippet="s_text_block" data-name="FAQ Entries">
        <div class="container">
          <p class="fg-section-kicker">Frequently asked questions</p>
          <h2 class="fg-section-title">Clear commitments before any work starts</h2>
          <div class="row g-3">
            {_faq_cards(FAQ_ITEMS)}
          </div>
        </div>
      </section>
      {_conversion_strip()}
    </div>
  </t>
</t>"""


def _seasonal_tips_arch():
    return f"""<t name="Fonseca Gardens Seasonal Tips" t-name="website.fonseca_seasonal_tips">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-shell">
      {STYLE_BLOCK}
      {_hero_section(
        "Seasonal Tips",
        "Practical guidance for resilient gardens",
        "Educational content aligned with Lisbon-region conditions.",
        "This section supports SEO and client education with concise, useful seasonal checklists.",
        "Editorial principles",
        [
          "Actionable steps over generic advice",
          "Season-specific timing and maintenance logic",
          "Clear owner decisions and expected outcomes",
          "Link each article to service options when relevant",
        ],
        ["Seasonal planning", "SEO content", "Client education"],
      )}
      <section class="pt16 pb8" data-snippet="s_features" data-name="Seasonal Topics">
        <div class="container">
          <p class="fg-section-kicker">Article roadmap</p>
          <h2 class="fg-section-title">Planned seasonal topics</h2>
          <div class="row g-3">
            {_seasonal_cards(SEASONAL_TOPICS)}
          </div>
        </div>
      </section>
      {_conversion_strip()}
    </div>
  </t>
</t>"""


def run(env):
    website = _get_website(env)

    page_specs = [
        {
            "url": "/",
            "name": "Fonseca Gardens",
            "meta_title": "Expat Garden Maintenance Lisbon & Cascais | Fonseca Gardens",
            "meta_description": "Finally, a gardener who shows up: subscription-first maintenance with 4-hour response, written quotes, and photo reports for expat and remote owners.",
            "arch": _home_arch(),
        },
        {
            "url": "/about",
            "name": "About Fonseca Gardens",
            "meta_title": "About Fonseca Gardens | Founder-Led Garden Care for Expats",
            "meta_description": "Meet the founder behind Fonseca Gardens and the trust-first service model designed for expat homeowners in Lisbon, Cascais, and Sintra.",
            "arch": _about_arch(),
        },
        {
            "url": "/services",
            "name": "Fonseca Gardens Services",
            "meta_title": "Reliable Garden Maintenance Services for Expats | Fonseca Gardens",
            "meta_description": "Recurring maintenance, irrigation checks, one-time reset, and proof-of-work reporting for expat and absentee owners.",
            "arch": _services_arch(),
        },
        {
            "url": "/pricing",
            "name": "Fonseca Gardens Pricing",
            "meta_title": "Transparent Expat Garden Maintenance Pricing | Fonseca Gardens",
            "meta_description": "Published monthly tiers from €100 with written quotes in 24h, no hidden charges, and annual commitment savings.",
            "arch": _pricing_arch(),
        },
        {
            "url": "/portfolio",
            "name": "Fonseca Gardens Portfolio",
            "meta_title": "Garden Project Portfolio | Fonseca Gardens",
            "meta_description": "Case-study structure for before/after outcomes and recurring maintenance results.",
            "arch": _portfolio_arch(),
        },
        {
            "url": "/testimonials",
            "name": "Fonseca Gardens Testimonials",
            "meta_title": "Expat Client Testimonials | Fonseca Gardens",
            "meta_description": "Specific expat homeowner feedback focused on punctuality, communication clarity, and visible before/after proof.",
            "arch": _testimonials_arch(),
        },
        {
            "url": "/faq",
            "name": "Fonseca Gardens FAQ",
            "meta_title": "FAQ for Expat Garden Maintenance Clients | Fonseca Gardens",
            "meta_description": "Direct answers on punctuality, pricing transparency, language support, and photo-reporting workflow.",
            "arch": _faq_arch(),
        },
        {
            "url": "/seasonal-tips",
            "name": "Fonseca Gardens Seasonal Tips",
            "meta_title": "Seasonal Garden Tips Lisbon | Fonseca Gardens",
            "meta_description": "Practical seasonal guidance for resilient gardens in Portugal's Atlantic climate.",
            "arch": _seasonal_tips_arch(),
        },
    ]

    menu_targets = [
        {"name": "Home", "url": "/", "sequence": 10},
        {"name": "About", "url": "/about", "sequence": 20},
        {"name": "Services", "url": "/services", "sequence": 30},
        {"name": "Pricing", "url": "/pricing", "sequence": 40},
        {"name": "Portfolio", "url": "/portfolio", "sequence": 50},
        {"name": "Testimonials", "url": "/testimonials", "sequence": 55},
        {"name": "FAQ", "url": "/faq", "sequence": 58},
        {"name": "Seasonal Tips", "url": "/seasonal-tips", "sequence": 59},
        {"name": "Request Quote", "url": CONTACT_URL, "sequence": 60},
    ]

    results = {
        "website": {"id": website.id, "name": website.name, "domain": website.domain or ""},
        "pages": [_ensure_page(env, website, spec) for spec in page_specs],
        "menus": _ensure_menu(env, website, menu_targets),
        "layout_reference_image": LAYOUT_REFERENCE_IMAGE,
        "business_source_of_truth": BUSINESS_SOURCE_OF_TRUTH,
        "source_of_truth_mapping": SOURCE_OF_TRUTH_MAPPING,
    }

    env.cr.commit()
    print(json.dumps(results, ensure_ascii=False))


run(env)
