import base64
import difflib
import hashlib
import json
import os
from datetime import datetime, timezone

from lxml import etree


MODULE_NAME = "wera_fonseca_site"
TARGET_WEBSITE_NAME = "Fonseca Gardens"

PAGE_CONFIG = {
    "/": {
        "slug": "home",
        "xmlid": "page_fonseca_home",
        "slot_keys": [
            "home.hero_headline",
            "home.hero_subheadline",
            "global.service_area",
            "home.value_props[0]",
            "home.value_props[1]",
            "home.value_props[2]",
            "home.value_props[3]",
        ],
        "meta_title_template": "{brand_name} | {tagline}",
        "meta_description_template": "{positioning}",
    },
    "/about": {
        "slug": "about",
        "xmlid": "page_fonseca_about",
        "slot_keys": [
            "global.brand_name",
            "global.positioning",
            "global.tagline",
            "about.founder_trust_story",
        ],
        "meta_title_template": "About {brand_name}",
        "meta_description_template": "Founder trust narrative and operating model for {brand_name}.",
    },
    "/services": {
        "slug": "services",
        "xmlid": "page_fonseca_services",
        "slot_keys": [
            "services.core_services[0]",
            "services.core_services[1]",
            "services.core_services[2]",
            "services.core_services[3]",
        ],
        "meta_title_template": "{brand_name} Services",
        "meta_description_template": "Core service catalog for {brand_name} in {service_area}.",
    },
    "/pricing": {
        "slug": "pricing",
        "xmlid": "page_fonseca_pricing",
        "slot_keys": [
            "pricing.tiers[0]",
            "pricing.tiers[1]",
            "pricing.tiers[2]",
            "pricing.tiers[3]",
        ],
        "meta_title_template": "{brand_name} Pricing",
        "meta_description_template": "Subscription tier framework for {brand_name}.",
    },
    "/testimonials": {
        "slug": "testimonials",
        "xmlid": "page_fonseca_testimonials",
        "slot_keys": [],
        "meta_title_template": "{brand_name} Testimonials",
        "meta_description_template": "Service proof themes and trust outcomes for {brand_name}.",
    },
    "/faq": {
        "slug": "faq",
        "xmlid": "page_fonseca_faq",
        "slot_keys": [
            "faq.seed_questions[0]",
            "faq.seed_questions[1]",
            "faq.seed_questions[2]",
            "faq.seed_questions[3]",
        ],
        "meta_title_template": "{brand_name} FAQ",
        "meta_description_template": "Direct answers for expat and absentee-owner buyers considering {brand_name}.",
    },
}


def _now_utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _deep_get(data, dotted_key):
    node = data
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(dotted_key)
        node = node[part]
    return node


def _load_source_of_truth():
    source_b64 = os.environ.get("FONSECA_SOURCE_JSON_B64", "").strip()
    source_path = os.environ.get("FONSECA_SOURCE_JSON_PATH", "").strip()

    if source_b64:
        decoded = base64.b64decode(source_b64).decode("utf-8")
        return json.loads(decoded), {"mode": "base64_env", "source_hint": "FONSECA_SOURCE_JSON_B64"}

    if source_path:
        with open(source_path, "r", encoding="utf-8") as handle:
            return json.load(handle), {"mode": "file_path", "source_hint": source_path}

    raise ValueError(
        "Source-of-truth payload missing. Set FONSECA_SOURCE_JSON_B64 or FONSECA_SOURCE_JSON_PATH."
    )


def _validate_schema(source):
    errors = []
    required_scalar = [
        "brand_core.brand_name",
        "brand_core.primary_tagline",
        "brand_core.positioning_statement",
    ]
    for key in required_scalar:
        try:
            value = _deep_get(source, key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{key} must be a non-empty string")
        except KeyError:
            errors.append(f"{key} is missing")

    required_list = [
        ("brand_core.service_area_focus", 1),
        ("value_proposition", 4),
        ("service_offering_for_pages.core_services", 4),
        ("critical_analysis.copy_guardrails", 1),
        ("critical_analysis.high_confidence_public_claims", 1),
        ("customer_segments", 2),
        ("page_generation_blueprint.fonseca_partner_page.required_sections", 5),
    ]
    for key, min_items in required_list:
        try:
            value = _deep_get(source, key)
            if not isinstance(value, list) or len(value) < min_items:
                errors.append(f"{key} must be a list with at least {min_items} items")
        except KeyError:
            errors.append(f"{key} is missing")

    try:
        tiers = _deep_get(source, "service_offering_for_pages.pricing_tiers_reference")
        if not isinstance(tiers, list) or len(tiers) < 4:
            errors.append("service_offering_for_pages.pricing_tiers_reference must contain at least 4 tiers")
        else:
            for index, tier in enumerate(tiers[:4]):
                if not isinstance(tier, dict):
                    errors.append(f"pricing tier {index} must be an object")
                    continue
                if not tier.get("name"):
                    errors.append(f"pricing tier {index} missing name")
                if not tier.get("range_eur_month"):
                    errors.append(f"pricing tier {index} missing range_eur_month")
    except KeyError:
        errors.append("service_offering_for_pages.pricing_tiers_reference is missing")

    if errors:
        raise ValueError("Schema validation failed: " + "; ".join(errors))


def _build_faq_seed_questions(source):
    brand_name = _deep_get(source, "brand_core.brand_name")
    areas = _deep_get(source, "brand_core.service_area_focus")
    service_area = ", ".join(areas[:3])
    return [
        f"Do you cover expat-owned properties in {service_area}?",
        "How do you prove what was completed when I am not on-site?",
        "What is included in your written quote and timeline commitment?",
        f"How do I choose the correct subscription tier for my {brand_name} maintenance plan?",
    ]


def _compile_slot_values(source):
    brand_name = _deep_get(source, "brand_core.brand_name").strip()
    tagline = _deep_get(source, "brand_core.primary_tagline").strip()
    positioning = _deep_get(source, "brand_core.positioning_statement").strip()
    service_area = " • ".join(_deep_get(source, "brand_core.service_area_focus"))
    value_props = _deep_get(source, "value_proposition")
    core_services = _deep_get(source, "service_offering_for_pages.core_services")
    pricing_tiers = _deep_get(source, "service_offering_for_pages.pricing_tiers_reference")
    high_confidence = _deep_get(source, "critical_analysis.high_confidence_public_claims")
    copy_guardrails = _deep_get(source, "critical_analysis.copy_guardrails")
    customer_segments = _deep_get(source, "customer_segments")

    founder_claim = next((c for c in high_confidence if "founder" in c.lower()), high_confidence[0])
    founder_story = (
        f"{founder_claim} {positioning} "
        f"The operating promise is '{tagline}' with transparent communication and accountability."
    )

    slots = {
        "global.brand_name": brand_name,
        "global.tagline": tagline,
        "global.positioning": positioning,
        "global.service_area": service_area,
        "home.hero_headline": tagline,
        "home.hero_subheadline": positioning,
        "about.founder_trust_story": founder_story,
        "faq.seed_questions[0]": _build_faq_seed_questions(source)[0],
        "faq.seed_questions[1]": _build_faq_seed_questions(source)[1],
        "faq.seed_questions[2]": _build_faq_seed_questions(source)[2],
        "faq.seed_questions[3]": _build_faq_seed_questions(source)[3],
        "testimonials.points[0]": value_props[1],
        "testimonials.points[1]": value_props[0],
        "testimonials.points[2]": copy_guardrails[2] if len(copy_guardrails) > 2 else customer_segments[0],
    }

    for idx in range(4):
        slots[f"home.value_props[{idx}]"] = value_props[idx]
        slots[f"services.core_services[{idx}]"] = core_services[idx]
        tier = pricing_tiers[idx]
        slots[f"pricing.tiers[{idx}]"] = f"{tier['name']} — €{tier['range_eur_month']}/month"

    return slots


def _find_page(env, website, route, xmlid_name):
    imd = env["ir.model.data"].sudo().search(
        [("module", "=", MODULE_NAME), ("name", "=", xmlid_name), ("model", "=", "website.page")], limit=1
    )
    if imd:
        by_xmlid = env["website.page"].sudo().browse(imd.res_id).exists()
        if by_xmlid:
            return by_xmlid, "xmlid"

    by_url = env["website.page"].sudo().search(
        [("website_id", "=", website.id), ("url", "=", route)],
        limit=1,
    )
    if by_url:
        return by_url, "url"

    raise ValueError(f"Required route {route} is missing on website {website.name}")


def _replace_slot_comments(root, slot_values):
    replaced = []
    for comment in root.xpath("//comment()"):
        text = (comment.text or "").strip()
        if not text.startswith("SLOT:"):
            continue
        slot_key = text.split("SLOT:", 1)[1].strip()
        if slot_key in slot_values:
            comment.tail = slot_values[slot_key]
            replaced.append(slot_key)
    return replaced


def _replace_testimonial_points(root, points):
    nodes = root.xpath("//section[contains(@data-name, 'Suggested testimonial blocks')]//ul[contains(@class, 'fg-list')]")
    if not nodes:
        return False
    ul = nodes[0]
    for child in list(ul):
        ul.remove(child)
    for point in points:
        li = etree.Element("li")
        li.text = point
        ul.append(li)
    return True


def _render_arch(route, arch_before, slot_values):
    parser = etree.XMLParser(remove_blank_text=False, recover=False)
    root = etree.fromstring(arch_before.encode("utf-8"), parser=parser)
    replaced_slots = _replace_slot_comments(root, slot_values)

    extra = {}
    if route == "/testimonials":
        testimonials_ok = _replace_testimonial_points(
            root,
            [
                slot_values["testimonials.points[0]"],
                slot_values["testimonials.points[1]"],
                slot_values["testimonials.points[2]"],
            ],
        )
        extra["testimonials_points_replaced"] = testimonials_ok

    arch_after = etree.tostring(root, encoding="unicode")
    return arch_after, replaced_slots, extra


def _make_diff(route, before, after):
    return "".join(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=f"{route}:before",
            tofile=f"{route}:after",
            lineterm="",
        )
    )


def run(env):
    dry_run = os.environ.get("FONSECA_PHASE3_DRY_RUN", "1").strip().lower() not in {"0", "false", "no"}

    source, source_meta = _load_source_of_truth()
    _validate_schema(source)
    slots = _compile_slot_values(source)

    website = env["website"].sudo().search([("name", "=", TARGET_WEBSITE_NAME)], limit=1)
    if not website:
        raise ValueError(f"Website '{TARGET_WEBSITE_NAME}' not found")

    result = {
        "captured_at_utc": _now_utc(),
        "dry_run": dry_run,
        "source_meta": source_meta,
        "source_sha256": hashlib.sha256(json.dumps(source, sort_keys=True).encode("utf-8")).hexdigest(),
        "website": {"id": website.id, "name": website.name, "domain": website.domain or ""},
        "pages": [],
    }

    changed_count = 0
    for route, cfg in PAGE_CONFIG.items():
        page, lookup_mode = _find_page(env, website, route, cfg["xmlid"])
        view = page.view_id.sudo()
        before_arch = view.arch_db or ""

        route_slots = {k: slots[k] for k in cfg["slot_keys"]}
        after_arch, replaced_slots, extra = _render_arch(route, before_arch, route_slots | slots)

        expected_slots = set(cfg["slot_keys"])
        missing_slots = sorted(expected_slots - set(replaced_slots))
        if missing_slots:
            raise ValueError(f"Route {route} missing expected slot comments: {missing_slots}")

        meta_title = cfg["meta_title_template"].format(
            brand_name=slots["global.brand_name"],
            tagline=slots["global.tagline"],
            positioning=slots["global.positioning"],
            service_area=slots["global.service_area"],
        )
        meta_description = cfg["meta_description_template"].format(
            brand_name=slots["global.brand_name"],
            tagline=slots["global.tagline"],
            positioning=slots["global.positioning"],
            service_area=slots["global.service_area"],
        )

        arch_changed = before_arch != after_arch
        meta_changed = (
            (page.website_meta_title or "") != meta_title
            or (page.website_meta_description or "") != meta_description
        )

        if not dry_run and (arch_changed or meta_changed):
            if arch_changed:
                view.write({"arch_db": after_arch})
            page.write(
                {
                    "website_meta_title": meta_title,
                    "website_meta_description": meta_description,
                    "is_published": True,
                }
            )
            changed_count += 1

        diff_text = _make_diff(route, before_arch, after_arch)
        result["pages"].append(
            {
                "route": route,
                "slug": cfg["slug"],
                "lookup_mode": lookup_mode,
                "page_id": page.id,
                "view_id": view.id,
                "slot_keys_expected": cfg["slot_keys"],
                "slot_keys_replaced": replaced_slots,
                "arch_changed": arch_changed,
                "meta_changed": meta_changed,
                "meta_after": {"title": meta_title, "description": meta_description},
                "diff_line_count": len(diff_text.splitlines()),
                "diff": diff_text,
                "extra": extra,
            }
        )

    if not dry_run:
        env.cr.commit()

    result["summary"] = {
        "page_count": len(result["pages"]),
        "changed_pages": changed_count,
        "dry_run": dry_run,
    }

    print("PHASE3_COMPILER_RESULT_BEGIN")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("PHASE3_COMPILER_RESULT_END")


run(env)
