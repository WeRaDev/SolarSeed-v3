import base64
import json
from pathlib import Path


TARGET_WEBSITE_NAME = "Fonseca Gardens"
TARGET_DOMAIN = "https://fonseca-gardens.wera-ss-pt-sn-1.tailfb390c.ts.net/"
LOGO_PATH = Path("/tmp/fonseca_logo.png")
CONTACT_URL = "/contactus?partner=fonseca-gardens"
CONSULTATION_URL = "/contactus?intent=consultation&amp;partner=fonseca-gardens"
WHATSAPP_URL = "https://wa.me/351000000000?text=Hello+Fonseca+Gardens"
LAYOUT_REFERENCE_IMAGE = "odoo-app/content/Fonseca Gardens/template.example.jpeg"
BUSINESS_SOURCE_OF_TRUTH = "odoo-app/content/fonseca_gardens_source_of_truth.json"

BRAND_NAME = "Fonseca Gardens"
BRAND_TAGLINE = "Above &amp; beyond. Every garden."
BRAND_POSITIONING = (
    "Finally, a gardener who actually shows up. Fonseca Gardens replaces no-shows and vague communication with accountable, subscription-first care."
)
SERVICE_AREA = "Sintra • Cascais • Lisbon region"
ANNUAL_DISCOUNT = "Save 10–15% with annual commitments."
RESPONSE_TIME_PROMISE = "Response within 4 hours via WhatsApp or email."
QUOTE_TIME_PROMISE = "Written quote in English within 24 hours."
PHOTO_REPORTING_PROMISE = "Before/after photo report after every scheduled visit."
LANGUAGE_SUPPORT = "English and Portuguese communication, with Russian support on request."
NO_SURPRISE_PRICING = "No surprise invoices. No hidden charges."
REMOTE_OWNER_CTA_URL = "/contactus?intent=remote-owner&amp;partner=fonseca-gardens"
RESEARCH_REPORT_PATH = "/Users/mikhailananyin/Documents/WeRa Global/Customers/Fonseca Gardens/Fonseca Gardens — Expat Pain Points & Website Content Guidelines.md"
SERVICE_TILES = [
    ("fa-calendar-check-o", "Scheduled visits you can rely on"),
    ("fa-commenting-o", "Fast communication"),
    ("fa-camera", "Photo proof every visit"),
    ("fa-file-text-o", "Written quote before work"),
    ("fa-language", "EN/PT + RU support on request"),
    ("fa-shield", "Accountable long-term care"),
]
PRICING_TIERS = [
    ("Essential", "€100–150/mo"),
    ("Standard", "€150–350/mo"),
    ("Premium", "€350–500/mo"),
    ("Estate", "€500–950+/mo"),
]
PROCESS_STEPS = [
    ("1. Contact us", "WhatsApp or email and get a reply within 4 hours."),
    ("2. Site visit", "We schedule a specific time and show up."),
    ("3. Written quote", "Clear scope and pricing in English within 24 hours."),
    ("4. Recurring service", "Same-day rhythm with predictable maintenance."),
    ("5. Photo report", "Before/after evidence sent after each visit."),
    ("6. Ongoing adjustments", "Request changes any time by WhatsApp."),
]
FAQ_SNIPPETS = [
    (
        "Will you actually show up when scheduled?",
        "Yes — visits are scheduled, confirmed, and followed by a post-visit report.",
    ),
    (
        "How do remote owners verify work?",
        "After every visit we send before/after photos and a short summary.",
    ),
    (
        "How do I avoid hidden charges?",
        "Pricing ranges are published and every quote is written before work starts.",
    ),
]
SOURCE_OF_TRUTH_MAPPING = {
    "layout_reference": LAYOUT_REFERENCE_IMAGE,
    "business_source": BUSINESS_SOURCE_OF_TRUTH,
    "expat_guidelines": RESEARCH_REPORT_PATH,
    "tagline": "brand_core.primary_tagline",
    "positioning": "brand_core.positioning_statement",
    "service_area": "brand_core.service_area_focus",
    "service_tiles": "service_offering_for_pages.core_services",
    "pricing_tiers": "service_offering_for_pages.pricing_tiers_reference",
    "copy_guardrails": "critical_analysis.copy_guardrails",
}


def _website(env):
    website = env["website"].sudo().search([("name", "=", TARGET_WEBSITE_NAME)], limit=1)
    if not website:
        raise Exception(f"Website '{TARGET_WEBSITE_NAME}' not found")
    return website


def _load_logo_b64():
    if not LOGO_PATH.exists():
        return None
    return base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")

def _service_tiles_markup():
    return "".join(
        f"""
          <div class="col-6 col-lg-4">
            <div class="fg-service-card">
              <span class="fg-service-icon"><i class="fa {icon}"></i></span>
              <h3>{label}</h3>
            </div>
          </div>
"""
        for icon, label in SERVICE_TILES
    )


def _pricing_tiers_markup():
    return "".join(
        f"""
            <div class="col-6 col-lg-3">
              <div class="fg-tier-card">
                <h4>{name}</h4>
                <p>{price}</p>
              </div>
            </div>
"""
        for name, price in PRICING_TIERS
    )
def _process_steps_markup():
    return "".join(
        f"""
            <div class="col-12 col-lg-4">
              <div class="fg-process-card">
                <h4>{title}</h4>
                <p>{body}</p>
              </div>
            </div>
"""
        for title, body in PROCESS_STEPS
    )


def _faq_snippets_markup():
    return "".join(
        f"""
            <div class="col-12 col-lg-4">
              <div class="fg-faq-card">
                <h4>{question}</h4>
                <p>{answer}</p>
              </div>
            </div>
"""
        for question, answer in FAQ_SNIPPETS
    )


def _homepage_arch():
    return f"""<t name="Fonseca Gardens Home" t-name="website.fonseca_home">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure fg-template">
      <style id="fonseca-template-style">
        .fg-template {{
          --fg-cream: #f7f1e6;
          --fg-green-dark: #123e33;
          --fg-green-mid: #1d5b47;
          --fg-green-soft: #2c6e58;
          --fg-accent: #c58945;
          --fg-text: #18211d;
          --fg-muted: #4f5e56;
        }}
        .fg-hero-shell {{
          border-radius: 22px;
          overflow: hidden;
          box-shadow: 0 20px 44px rgba(17, 34, 28, 0.16);
          border: 1px solid #d8e1d7;
          background: #fff;
        }}
        .fg-hero-copy {{
          background: linear-gradient(180deg, #f8f4eb 0%, #f5eedf 100%);
          padding: 3rem 2.25rem;
          color: var(--fg-text);
        }}
        .fg-logo-badge {{
          display: inline-flex;
          align-items: center;
          gap: .45rem;
          margin-bottom: 1rem;
          font-weight: 700;
          font-size: .85rem;
          letter-spacing: .06em;
          text-transform: uppercase;
          color: var(--fg-green-dark);
        }}
        .fg-logo-badge:before,
        .fg-logo-badge:after {{
          content: "";
          width: 32px;
          border-top: 2px solid #d2bb8b;
          opacity: .9;
        }}
        .fg-hero-copy h1 {{
          color: var(--fg-green-dark);
          font-size: clamp(2rem, 4vw, 3.2rem);
          line-height: 1.04;
          margin-bottom: .8rem;
          font-weight: 800;
        }}
        .fg-hero-copy h2 {{
          font-size: clamp(1.1rem, 2vw, 1.55rem);
          color: var(--fg-accent);
          margin-bottom: 1rem;
          font-weight: 700;
          letter-spacing: .02em;
        }}
        .fg-hero-copy p {{
          color: var(--fg-muted);
          font-size: 1.04rem;
          margin-bottom: 1.1rem;
        }}
        .fg-chip-list {{
          display: flex;
          flex-wrap: wrap;
          gap: .4rem;
          margin-bottom: 1.2rem;
        }}
        .fg-chip {{
          background: #e8eee7;
          color: #24493c;
          border-radius: 999px;
          border: 1px solid #d5dfd4;
          padding: .3rem .72rem;
          font-size: .82rem;
          font-weight: 600;
        }}
        .fg-cta-cluster {{
          display: flex;
          flex-wrap: wrap;
          gap: .65rem;
        }}
        .fg-btn-primary {{
          background: var(--fg-green-dark);
          color: #fff !important;
          border-radius: 999px;
          border: 1px solid var(--fg-green-dark);
          padding: .7rem 1.2rem;
          font-weight: 700;
        }}
        .fg-btn-secondary {{
          border-radius: 999px;
          border: 1px solid var(--fg-green-dark);
          color: var(--fg-green-dark) !important;
          background: transparent;
          padding: .7rem 1.2rem;
          font-weight: 700;
        }}
        .fg-btn-tertiary {{
          border-radius: 999px;
          border: 1px solid #9cb1a7;
          color: #2d4e41 !important;
          background: #fff;
          padding: .7rem 1.2rem;
          font-weight: 700;
        }}
        .fg-hero-visual {{
          position: relative;
          background: linear-gradient(140deg, #63b6ec 0%, #8fd4ff 32%, #9cdc80 95%);
          min-height: 460px;
          color: #ffffff;
          padding: 2.4rem 2.1rem;
          display: flex;
          align-items: flex-end;
        }}
        .fg-hero-visual:before {{
          content: "";
          position: absolute;
          inset: 0;
          background:
            radial-gradient(circle at 78% 22%, rgba(255, 255, 255, 0.78) 0 10%, transparent 11%),
            radial-gradient(circle at 64% 18%, rgba(255, 255, 255, 0.55) 0 8%, transparent 9%),
            linear-gradient(180deg, rgba(11, 62, 45, .1) 0%, rgba(11, 62, 45, .52) 92%);
          pointer-events: none;
        }}
        .fg-visual-card {{
          position: relative;
          z-index: 2;
          width: min(430px, 100%);
          background: rgba(12, 60, 47, .78);
          border: 1px solid rgba(255,255,255,.24);
          border-radius: 16px;
          backdrop-filter: blur(2px);
          padding: 1rem 1rem .95rem;
        }}
        .fg-visual-card h3 {{
          font-size: 1.05rem;
          margin-bottom: .5rem;
          font-weight: 700;
        }}
        .fg-visual-card ul {{
          list-style: none;
          margin: 0;
          padding: 0;
        }}
        .fg-visual-card li {{
          margin: .34rem 0;
          padding-left: 1.1rem;
          position: relative;
          font-size: .93rem;
          line-height: 1.36;
        }}
        .fg-visual-card li:before {{
          content: "•";
          position: absolute;
          left: 0;
          top: -.08rem;
          color: #ffd8aa;
          font-size: 1.1rem;
        }}
        .fg-services {{
          padding: 2.3rem 0 1.7rem;
        }}
        .fg-services h3 {{
          color: var(--fg-green-dark);
          text-transform: uppercase;
          letter-spacing: .07em;
          font-size: .92rem;
          text-align: center;
          margin-bottom: .3rem;
          font-weight: 800;
        }}
        .fg-services h2 {{
          color: var(--fg-green-dark);
          text-align: center;
          font-size: clamp(1.5rem, 3vw, 2.1rem);
          margin-bottom: 1.3rem;
          font-weight: 800;
        }}
        .fg-service-card {{
          height: 100%;
          background: #fff;
          border: 1px solid #dee8de;
          border-radius: 14px;
          padding: .95rem .75rem;
          text-align: center;
          box-shadow: 0 8px 20px rgba(11, 45, 33, .06);
        }}
        .fg-service-icon {{
          display: inline-flex;
          justify-content: center;
          align-items: center;
          width: 52px;
          height: 52px;
          border-radius: 999px;
          border: 1px solid #d5dfd5;
          color: var(--fg-green-mid);
          font-size: 1.35rem;
          margin-bottom: .55rem;
          background: #fbfdfb;
        }}
        .fg-service-card h3 {{
          font-size: .93rem;
          color: var(--fg-green-dark);
          margin: 0;
          line-height: 1.3;
          text-transform: none;
          letter-spacing: normal;
        }}
        .fg-tiers {{
          padding: .6rem 0 2rem;
        }}
        .fg-tier-card {{
          border: 1px solid #dee8de;
          border-radius: 14px;
          background: #fff;
          height: 100%;
          padding: .95rem .8rem;
          text-align: center;
        }}
        .fg-tier-card h4 {{
          color: var(--fg-green-dark);
          font-size: .96rem;
          margin-bottom: .28rem;
          font-weight: 700;
        }}
        .fg-tier-card p {{
          margin: 0;
          color: #8f5d25;
          font-weight: 700;
        }}
        .fg-tier-note {{
          text-align: center;
          color: var(--fg-muted);
          margin-top: .8rem;
          font-size: .97rem;
        }}
        .fg-process-card,
        .fg-faq-card {{
          border: 1px solid #dee8de;
          border-radius: 14px;
          background: #fff;
          height: 100%;
          padding: .95rem .95rem;
          box-shadow: 0 8px 20px rgba(11, 45, 33, .06);
        }}
        .fg-process-card h4,
        .fg-faq-card h4 {{
          color: var(--fg-green-dark);
          font-size: .98rem;
          font-weight: 700;
          margin-bottom: .35rem;
        }}
        .fg-process-card p,
        .fg-faq-card p {{
          margin: 0;
          color: var(--fg-muted);
          font-size: .93rem;
          line-height: 1.35;
        }}
        .fg-conversion-strip {{
          margin: .75rem auto 2.1rem;
          background: linear-gradient(135deg, #0f4538 0%, #185a47 100%);
          border-radius: 16px;
          color: #fff;
          box-shadow: 0 16px 34px rgba(10, 44, 33, .2);
        }}
        .fg-strip-item {{
          padding: 1rem 1.1rem;
          display: flex;
          align-items: center;
          gap: .72rem;
        }}
        .fg-strip-item + .fg-strip-item {{
          border-top: 1px solid rgba(255,255,255,.18);
        }}
        .fg-strip-icon {{
          width: 48px;
          height: 48px;
          border-radius: 999px;
          border: 1px solid rgba(255,255,255,.35);
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-size: 1.2rem;
          flex-shrink: 0;
        }}
        .fg-strip-copy strong {{
          display: block;
          font-size: .84rem;
          letter-spacing: .08em;
          text-transform: uppercase;
          opacity: .87;
          margin-bottom: .08rem;
        }}
        .fg-strip-copy span {{
          display: block;
          font-weight: 700;
          font-size: 1rem;
          line-height: 1.25;
        }}
        .fg-strip-cta {{
          margin-left: auto;
        }}
        .fg-strip-cta a {{
          border-radius: 999px;
          border: 1px solid rgba(255,255,255,.5);
          color: #fff !important;
          font-weight: 700;
          padding: .48rem .9rem;
        }}
        @media (min-width: 992px) {{
          .fg-strip-item + .fg-strip-item {{
            border-top: none;
            border-left: 1px solid rgba(255,255,255,.16);
          }}
          .fg-conversion-strip .row {{
            align-items: stretch;
          }}
          .fg-strip-item {{
            height: 100%;
          }}
        }}
      </style>
      <section class="pt40 pb26" data-snippet="s_text_block" data-name="Template Hero">
        <div class="container">
          <div class="fg-hero-shell">
            <div class="row g-0">
              <div class="col-lg-6">
                <div class="fg-hero-copy">
                  <span class="fg-logo-badge">{BRAND_NAME}</span>
                  <h1>Finally, a gardener who actually shows up.</h1>
                  <h2>Gardens that get looked after — even when you are not there.</h2>
                  <p>{BRAND_POSITIONING}</p>
                  <p class="mb-2"><strong>Service area:</strong> {SERVICE_AREA}</p>
                  <div class="fg-chip-list">
                    <span class="fg-chip">Response in 4h</span>
                    <span class="fg-chip">Written quote in 24h</span>
                    <span class="fg-chip">Photo report every visit</span>
                    <span class="fg-chip">EN/PT + RU support on request</span>
                  </div>
                  <div class="fg-cta-cluster">
                    <a class="btn fg-btn-primary" href="{WHATSAPP_URL}" target="_blank" rel="noopener">Send us a WhatsApp — no forms, no waiting</a>
                    <a class="btn fg-btn-secondary" href="{CONSULTATION_URL}">Get a free site visit</a>
                    <a class="btn fg-btn-tertiary" href="{REMOTE_OWNER_CTA_URL}">Managing property from abroad?</a>
                  </div>
                </div>
              </div>
              <div class="col-lg-6">
                <div class="fg-hero-visual">
                  <div class="fg-visual-card">
                    <h3>What expat clients care about most</h3>
                    <ul>
                      <li>{RESPONSE_TIME_PROMISE}</li>
                      <li>{QUOTE_TIME_PROMISE}</li>
                      <li>{PHOTO_REPORTING_PROMISE}</li>
                      <li>{NO_SURPRISE_PRICING}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <p class="fg-tier-note">{BRAND_TAGLINE}</p>
        </div>
      </section>
      <section class="fg-services" data-snippet="s_features" data-name="Services Grid">
        <div class="container">
          <h3>Trust signals</h3>
          <h2>Why expat homeowners switch to Fonseca Gardens</h2>
          <div class="row g-3">
{_service_tiles_markup()}
          </div>
        </div>
      </section>
      <section class="fg-tiers" data-snippet="s_features" data-name="Pricing Snapshot">
        <div class="container">
          <div class="row g-3">
{_pricing_tiers_markup()}
          </div>
          <p class="fg-tier-note">{NO_SURPRISE_PRICING} {ANNUAL_DISCOUNT}</p>
        </div>
      </section>
      <section class="pt8 pb20" data-snippet="s_features" data-name="How It Works">
        <div class="container">
          <h3 class="text-center mb-2">How it works</h3>
          <h2 class="text-center mb-4">A six-step process that removes uncertainty</h2>
          <div class="row g-3">
{_process_steps_markup()}
          </div>
        </div>
      </section>
      <section class="pt8 pb24" data-snippet="s_text_block" data-name="FAQ Preview">
        <div class="container">
          <h3 class="text-center mb-2">FAQ for sceptical homeowners</h3>
          <h2 class="text-center mb-4">Direct answers before any work starts</h2>
          <div class="row g-3">
{_faq_snippets_markup()}
          </div>
        </div>
      </section>
      <section class="pb42" data-snippet="s_text_block" data-name="Conversion Strip">
        <div class="container text-center">
          <div class="fg-conversion-strip">
            <div class="row g-0">
              <div class="col-lg-6">
                <div class="fg-strip-item">
                  <span class="fg-strip-icon"><i class="fa fa-calendar"></i></span>
                  <div class="fg-strip-copy text-start">
                    <strong>Fast response, no ghosting</strong>
                    <span>{RESPONSE_TIME_PROMISE} {QUOTE_TIME_PROMISE}</span>
                  </div>
                  <div class="fg-strip-cta">
                    <a class="btn btn-sm" href="{WHATSAPP_URL}" target="_blank" rel="noopener">Start on WhatsApp</a>
                  </div>
                </div>
              </div>
              <div class="col-lg-6">
                <div class="fg-strip-item">
                  <span class="fg-strip-icon"><i class="fa fa-phone"></i></span>
                  <div class="fg-strip-copy text-start">
                    <strong>Built for expat and remote owners</strong>
                    <span>{PHOTO_REPORTING_PROMISE} {LANGUAGE_SUPPORT}</span>
                  </div>
                  <div class="fg-strip-cta">
                    <a class="btn btn-sm" href="{CONSULTATION_URL}">Request site visit</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>"""


def run(env):
    website = _website(env)
    logo_b64 = _load_logo_b64()
    updates = {
        "domain": TARGET_DOMAIN,
    }
    if logo_b64:
        updates["logo"] = logo_b64
    website.write(updates)

    page = env["website.page"].sudo().search([("website_id", "=", website.id), ("url", "=", "/")], limit=1)
    if not page:
        created = website.with_context(website_id=website.id).new_page(name="Fonseca Gardens", add_menu=False, page_title="Fonseca Gardens")
        page = env["website.page"].sudo().browse(created["page_id"])
        page.write({"url": "/"})

    page.write(
        {
            "name": "Fonseca Gardens",
            "is_published": True,
            "website_meta_title": "Expat Garden Maintenance Lisbon & Cascais | Fonseca Gardens",
            "website_meta_description": "Finally, a gardener who shows up: subscription-first maintenance with fast response, written quotes, and photo reports for expat and remote owners.",
        }
    )
    page.view_id.sudo().write(
        {
            "name": "Fonseca Gardens Home",
            "arch_db": _homepage_arch(),
        }
    )

    env.cr.commit()
    print(
        json.dumps(
            {
                "website_id": website.id,
                "website_name": website.name,
                "domain": website.domain or "",
                "logo_applied": bool(logo_b64),
                "homepage_page_id": page.id,
                "homepage_view_id": page.view_id.id,
                "published": page.is_published,
                "layout_reference_image": LAYOUT_REFERENCE_IMAGE,
                "business_source_of_truth": BUSINESS_SOURCE_OF_TRUTH,
                "source_of_truth_mapping": SOURCE_OF_TRUTH_MAPPING,
            },
            ensure_ascii=False,
        )
    )


run(env)
