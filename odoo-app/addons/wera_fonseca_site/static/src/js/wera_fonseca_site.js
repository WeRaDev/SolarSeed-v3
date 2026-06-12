/** @odoo-module **/

(function () {
  "use strict";

  const INTAKE_ACTION = "/fonseca/intake";
  const PARTNER_SLUG = "fonseca-gardens";
  const QUOTE_DIRECT_URL = `/contactus?partner=${PARTNER_SLUG}&intent=quote`;
  const CONSULT_DIRECT_URL = `/contactus?partner=${PARTNER_SLUG}&intent=consultation`;
  const RUNTIME_STYLE_ID = "fg-phase5-runtime-style";

  const RUNTIME_STYLE_CSS = `
#wrap.fg-skeleton .fg-interactive-section{background:linear-gradient(180deg,#f7fbf8 0%,#f2f8f4 100%);border-top:1px solid #d9e7dc;}
#wrap.fg-skeleton .fg-interactive-shell{border:1px solid #d9e7dc;border-radius:14px;padding:1rem;background:#fff;box-shadow:0 10px 28px rgba(18,62,51,.08);}
#wrap.fg-skeleton .fg-interactive-eyebrow{margin:0 0 .45rem 0;text-transform:uppercase;letter-spacing:.08em;color:#1f5d48;font-size:.78rem;font-weight:700;}
#wrap.fg-skeleton .fg-form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.72rem;margin-top:.9rem;}
#wrap.fg-skeleton .fg-form-field{display:flex;flex-direction:column;gap:.32rem;}
#wrap.fg-skeleton .fg-form-field label{font-size:.86rem;font-weight:600;color:#315346;}
#wrap.fg-skeleton .fg-form-field input,#wrap.fg-skeleton .fg-form-field select,#wrap.fg-skeleton .fg-form-field textarea{border:1px solid #bfd4c6;border-radius:10px;padding:.62rem .72rem;font-size:.93rem;line-height:1.4;background:#fff;color:#20352d;}
#wrap.fg-skeleton .fg-form-actions{margin-top:.9rem;display:flex;flex-wrap:wrap;gap:.66rem;}
#wrap.fg-skeleton .fg-form-hint,#wrap.fg-skeleton .fg-tier-guidance{margin-top:.7rem;margin-bottom:0;font-size:.86rem;color:#496457;}
#wrap.fg-skeleton .fg-faq-accordion{display:grid;gap:.72rem;}
#wrap.fg-skeleton .fg-faq-item{border:1px solid #d9e7dc;border-radius:12px;background:#fff;overflow:hidden;}
#wrap.fg-skeleton .fg-faq-item summary{cursor:pointer;list-style:none;padding:.85rem 1rem;color:#123e33;font-weight:650;position:relative;}
#wrap.fg-skeleton .fg-faq-item summary::-webkit-details-marker{display:none;}
#wrap.fg-skeleton .fg-faq-item summary::after{content:"+";position:absolute;right:1rem;top:.7rem;color:#1f5d48;font-size:1.1rem;font-weight:700;}
#wrap.fg-skeleton .fg-faq-item[open] summary::after{content:"−";}
#wrap.fg-skeleton .fg-faq-answer{margin:0;padding:0 1rem .95rem 1rem;color:#4f5f57;}
#wrap.fg-skeleton .fg-rotator{border:1px solid #d9e7dc;border-radius:14px;background:#fff;padding:1rem;box-shadow:0 10px 28px rgba(18,62,51,.08);}
#wrap.fg-skeleton .fg-rotator-quote{margin:0;color:#234337;font-weight:620;line-height:1.5;}
#wrap.fg-skeleton .fg-rotator-controls{margin-top:.8rem;display:flex;gap:.5rem;}
@media (max-width: 991.98px){#wrap.fg-skeleton .fg-form-grid{grid-template-columns:1fr;}}
@media (max-width: 767.98px){#wrap.fg-skeleton .fg-form-actions{flex-direction:column;align-items:stretch;}#wrap.fg-skeleton .fg-form-actions .btn{width:100%;}}
  `;

  const FAQ_DEFAULT_ANSWERS = [
    "Yes. We confirm visits in advance and share after-visit proof-of-work updates so scheduling stays visible.",
    "After every visit we send structured updates with visual evidence and a concise summary of completed tasks.",
    "Quotes are shared in writing with clear scope, frequency, and pricing details before recurring service begins.",
    "We start with your priorities, recommend a tier, and adapt the cadence after the first operational cycle.",
  ];

  const ROUTE_COPY = {
    "/": {
      eyebrow: "Quick request",
      title: "Tell us what your garden needs",
      body: "Share your property details and we will continue the quote flow with Fonseca context prefilled.",
    },
    "/about": {
      eyebrow: "Start a conversation",
      title: "Request your first assessment",
      body: "Use this form to route directly into the Fonseca partner intake path.",
    },
    "/services": {
      eyebrow: "Service intake",
      title: "Request a scoped services quote",
      body: "Describe your property and preferred scope so the services quote can be prepared in context.",
    },
    "/pricing": {
      eyebrow: "Pricing handoff",
      title: "Check your likely starting tier",
      body: "Submit your profile and receive a quote path tuned to your garden size and visit cadence.",
    },
    "/testimonials": {
      eyebrow: "Request your own plan",
      title: "Turn trust signals into your next step",
      body: "Move from testimonial proof to a concrete quote or consultation request.",
    },
    "/faq": {
      eyebrow: "FAQ follow-up",
      title: "Ask your specific property question",
      body: "If your scenario is not covered above, send details and we route you to the right next action.",
    },
  };

  function whenReady(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
      return;
    }
    callback();
  }

  function getCsrfToken() {
    if (window.odoo && typeof window.odoo.csrf_token === "string") {
      return window.odoo.csrf_token;
    }
    return "";
  }

  function ensureRuntimeStyles() {
    if (document.getElementById(RUNTIME_STYLE_ID)) {
      return;
    }
    const styleTag = document.createElement("style");
    styleTag.id = RUNTIME_STYLE_ID;
    styleTag.textContent = RUNTIME_STYLE_CSS;
    document.head.appendChild(styleTag);
  }

  function getRoutePath() {
    const path = window.location.pathname || "/";
    if (path.length > 1 && path.endsWith("/")) {
      return path.slice(0, -1);
    }
    return path;
  }

  function buildQuoteForm(routePath) {
    const form = document.createElement("form");
    form.className = "fg-mini-form fg-mini-form--quote";
    form.method = "post";
    form.action = INTAKE_ACTION;
    form.setAttribute("data-fg-quote-form", "1");
    form.innerHTML = `
      <input type="hidden" name="csrf_token" value="${getCsrfToken()}"/>
      <input type="hidden" name="partner" value="${PARTNER_SLUG}"/>
      <input type="hidden" name="intent" value="quote"/>
      <input type="hidden" name="source" value="phase5-inline-quote"/>
      <input type="hidden" name="route" value="${routePath}"/>
      <div class="fg-form-grid">
        <div class="fg-form-field">
          <label for="fg_quote_name">Full name</label>
          <input id="fg_quote_name" name="contact_name" type="text" required autocomplete="name"/>
        </div>
        <div class="fg-form-field">
          <label for="fg_quote_email">Email</label>
          <input id="fg_quote_email" name="email_from" type="email" required autocomplete="email"/>
        </div>
        <div class="fg-form-field">
          <label for="fg_quote_phone">Phone</label>
          <input id="fg_quote_phone" name="phone" type="tel" autocomplete="tel"/>
        </div>
        <div class="fg-form-field">
          <label for="fg_quote_area">Service area</label>
          <select id="fg_quote_area" name="service_area">
            <option value="Sintra">Sintra</option>
            <option value="Cascais">Cascais</option>
            <option value="Lisbon region">Lisbon region</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div class="fg-form-field fg-form-field--full">
          <label for="fg_quote_details">Property details</label>
          <textarea id="fg_quote_details" name="description" rows="3" placeholder="Garden size, maintenance cadence, and key priorities"></textarea>
        </div>
      </div>
      <div class="fg-form-actions">
        <button type="submit" class="btn btn-primary">Submit quote request</button>
        <a class="btn btn-outline-primary" href="${QUOTE_DIRECT_URL}">Open full contact form</a>
      </div>
      <p class="fg-form-hint"><strong>Integration:</strong> posts directly to Fonseca CRM intake and then redirects to the contact flow.</p>
    `;
    return form;
  }

  function buildConsultationForm(routePath, includeTierInputs) {
    const form = document.createElement("form");
    form.className = "fg-mini-form fg-mini-form--consult";
    form.method = "post";
    form.action = INTAKE_ACTION;
    form.setAttribute("data-fg-consult-form", "1");
    form.innerHTML = `
      <input type="hidden" name="csrf_token" value="${getCsrfToken()}"/>
      <input type="hidden" name="partner" value="${PARTNER_SLUG}"/>
      <input type="hidden" name="intent" value="consultation"/>
      <input type="hidden" name="source" value="phase5-inline-consult"/>
      <input type="hidden" name="route" value="${routePath}"/>
      <div class="fg-form-grid">
        <div class="fg-form-field">
          <label for="fg_consult_name">Contact name</label>
          <input id="fg_consult_name" name="contact_name" type="text" required autocomplete="name"/>
        </div>
        <div class="fg-form-field">
          <label for="fg_consult_email">Email</label>
          <input id="fg_consult_email" name="email_from" type="email" required autocomplete="email"/>
        </div>
        <div class="fg-form-field">
          <label for="fg_consult_phone">Phone</label>
          <input id="fg_consult_phone" name="phone" type="tel" autocomplete="tel"/>
        </div>
        <div class="fg-form-field">
          <label for="fg_consult_timing">Preferred timing</label>
          <select id="fg_consult_timing" name="preferred_timing">
            <option value="weekdays">Weekdays</option>
            <option value="weekend">Weekend</option>
            <option value="asap">ASAP</option>
          </select>
        </div>
        <div class="fg-form-field fg-form-field--full">
          <label for="fg_consult_notes">Consultation notes</label>
          <textarea id="fg_consult_notes" name="description" rows="3" placeholder="Goals, constraints, and preferred start date"></textarea>
        </div>
      </div>
      <div class="fg-form-actions">
        <button type="submit" class="btn btn-primary" data-fg-consult-submit>Request consultation call-back</button>
        <a class="btn btn-outline-primary" href="${CONSULT_DIRECT_URL}" data-fg-consult-direct>Open callback details form</a>
      </div>
      <p class="fg-form-hint" data-fg-consult-hint><strong>Scheduling:</strong> consultation requests are handled as CRM callbacks (target reply within 4 business hours).</p>
    `;

    if (!includeTierInputs) {
      return form;
    }

    const tierFields = document.createElement("div");
    tierFields.className = "fg-form-grid";
    tierFields.innerHTML = `
      <div class="fg-form-field">
        <label for="fg_property_size">Property size</label>
        <select id="fg_property_size" name="property_size" data-fg-tier-size>
          <option value="small">Small garden</option>
          <option value="medium">Medium garden</option>
          <option value="large">Large garden</option>
          <option value="estate">Estate / multi-zone</option>
        </select>
      </div>
      <div class="fg-form-field">
        <label for="fg_visit_frequency">Visit frequency</label>
        <select id="fg_visit_frequency" name="visit_frequency" data-fg-tier-frequency>
          <option value="monthly">Monthly</option>
          <option value="fortnightly">Fortnightly</option>
          <option value="weekly">Weekly</option>
        </select>
      </div>
    `;
    form.insertBefore(tierFields, form.querySelector(".fg-form-actions"));

    const guidance = document.createElement("p");
    guidance.className = "fg-tier-guidance";
    guidance.setAttribute("data-fg-tier-guidance", "1");
    guidance.textContent = "Recommended starting tier: Standard (refine after first site visit).";
    form.insertBefore(guidance, form.querySelector(".fg-form-actions"));

    return form;
  }

  function buildInteractiveSection(routePath) {
    const copy = ROUTE_COPY[routePath] || ROUTE_COPY["/"];
    const section = document.createElement("section");
    section.className = "s_text_block fg-interactive-section py-4";
    section.setAttribute("data-fg-phase5-section", "1");

    const includeTierInputs = routePath === "/pricing";
    const quoteForm = buildQuoteForm(routePath);
    const consultationForm = buildConsultationForm(routePath, includeTierInputs);

    section.innerHTML = `
      <div class="container">
        <p class="fg-interactive-eyebrow">${copy.eyebrow}</p>
        <h2>${copy.title}</h2>
        <p class="lead">${copy.body}</p>
        <div class="row g-3">
          <div class="col-12 col-lg-6">
            <div class="fg-interactive-shell" data-fg-quote-shell>
              <h3>Quote request handoff</h3>
            </div>
          </div>
          <div class="col-12 col-lg-6">
            <div class="fg-interactive-shell" data-fg-consult-shell>
              <h3>Consultation callback request</h3>
            </div>
          </div>
        </div>
      </div>
    `;

    section.querySelector("[data-fg-quote-shell]").appendChild(quoteForm);
    section.querySelector("[data-fg-consult-shell]").appendChild(consultationForm);
    return section;
  }

  function injectInteractiveForms(root, routePath) {
    if (root.querySelector("[data-fg-phase5-section='1']")) {
      return;
    }
    const section = buildInteractiveSection(routePath);
    root.appendChild(section);
  }

  function inferFaqAnswer(question, index) {
    const q = (question || "").toLowerCase();
    if (q.includes("schedule") || q.includes("reliability")) {
      return FAQ_DEFAULT_ANSWERS[0];
    }
    if (q.includes("prove") || q.includes("on-site") || q.includes("verify")) {
      return FAQ_DEFAULT_ANSWERS[1];
    }
    if (q.includes("quote") || q.includes("written")) {
      return FAQ_DEFAULT_ANSWERS[2];
    }
    if (q.includes("tier") || q.includes("plan")) {
      return FAQ_DEFAULT_ANSWERS[3];
    }
    return FAQ_DEFAULT_ANSWERS[index % FAQ_DEFAULT_ANSWERS.length];
  }

  function enhanceFaq(routePath, root) {
    if (routePath !== "/faq") {
      return;
    }
    const list = root.querySelector("ul.fg-list");
    if (!list || list.dataset.fgFaqEnhanced === "1") {
      return;
    }
    const items = Array.from(list.querySelectorAll("li"))
      .map((item) => item.textContent.trim())
      .filter(Boolean);
    if (!items.length) {
      return;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "fg-faq-accordion";
    items.forEach((question, index) => {
      const details = document.createElement("details");
      details.className = "fg-faq-item";
      if (index === 0) {
        details.open = true;
      }
      const summary = document.createElement("summary");
      summary.textContent = question;
      const answer = document.createElement("p");
      answer.className = "fg-faq-answer";
      answer.textContent = inferFaqAnswer(question, index);
      details.appendChild(summary);
      details.appendChild(answer);
      wrapper.appendChild(details);
    });

    list.dataset.fgFaqEnhanced = "1";
    list.replaceWith(wrapper);
  }

  function enhanceTestimonials(routePath, root) {
    if (routePath !== "/testimonials") {
      return;
    }
    const list = root.querySelector("ul.fg-list");
    if (!list || list.dataset.fgRotatorEnhanced === "1") {
      return;
    }
    const points = Array.from(list.querySelectorAll("li"))
      .map((item) => item.textContent.trim())
      .filter(Boolean);
    if (!points.length) {
      return;
    }

    let index = 0;
    const rotator = document.createElement("div");
    rotator.className = "fg-rotator";
    rotator.innerHTML = `
      <p class="fg-rotator-quote"></p>
      <div class="fg-rotator-controls">
        <button type="button" class="btn btn-outline-primary" data-fg-rotator-prev>Previous</button>
        <button type="button" class="btn btn-outline-primary" data-fg-rotator-next>Next</button>
      </div>
    `;

    function render() {
      const quote = rotator.querySelector(".fg-rotator-quote");
      if (!quote) {
        return;
      }
      quote.textContent = points[index];
    }

    const prevButton = rotator.querySelector("[data-fg-rotator-prev]");
    const nextButton = rotator.querySelector("[data-fg-rotator-next]");
    if (prevButton) {
      prevButton.addEventListener("click", function () {
        index = (index - 1 + points.length) % points.length;
        render();
      });
    }
    if (nextButton) {
      nextButton.addEventListener("click", function () {
        index = (index + 1) % points.length;
        render();
      });
    }

    render();
    list.dataset.fgRotatorEnhanced = "1";
    list.replaceWith(rotator);
  }

  function bindTierGuidance(root) {
    const sizeSelect = root.querySelector("[data-fg-tier-size]");
    const frequencySelect = root.querySelector("[data-fg-tier-frequency]");
    const guidance = root.querySelector("[data-fg-tier-guidance]");
    if (!sizeSelect || !frequencySelect || !guidance) {
      return;
    }

    const scoreMap = { small: 0, medium: 1, large: 2, estate: 3 };
    const frequencyMap = { monthly: 0, fortnightly: 1, weekly: 2 };
    const labels = ["Essential", "Standard", "Premium", "Estate"];

    function updateGuidance() {
      const sizeScore = scoreMap[sizeSelect.value] || 0;
      const frequencyScore = frequencyMap[frequencySelect.value] || 0;
      const index = Math.min(3, sizeScore + frequencyScore);
      guidance.textContent = `Recommended starting tier: ${labels[index]} (finalized during site visit).`;
    }

    sizeSelect.addEventListener("change", updateGuidance);
    frequencySelect.addEventListener("change", updateGuidance);
    updateGuidance();
  }

  function wireConsultationAction(root) {
    const forms = root.querySelectorAll("[data-fg-consult-form]");
    if (!forms.length) {
      return;
    }

    forms.forEach((form) => {
      const hint = form.querySelector("[data-fg-consult-hint]");
      const submitButton = form.querySelector("[data-fg-consult-submit]");
      const directLink = form.querySelector("[data-fg-consult-direct]");
      form.action = INTAKE_ACTION;
      if (submitButton) {
        submitButton.textContent = "Request consultation call-back";
      }
      if (directLink) {
        directLink.setAttribute("href", CONSULT_DIRECT_URL);
      }
      if (hint) {
        hint.innerHTML =
          "<strong>Scheduling:</strong> consultation submissions create CRM leads and a manual callback task for follow-up.";
      }
    });
  }

  function bootstrap() {
    const root = document.querySelector("#wrap.fg-skeleton, #wrap.fg-shell");
    if (!root) {
      return;
    }
    ensureRuntimeStyles();
    const routePath = getRoutePath();

    injectInteractiveForms(root, routePath);
    enhanceFaq(routePath, root);
    enhanceTestimonials(routePath, root);
    bindTierGuidance(root);
    wireConsultationAction(root);
  }

  whenReady(bootstrap);
})();
