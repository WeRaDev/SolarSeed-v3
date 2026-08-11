import logging
from datetime import timedelta
from urllib.parse import urlencode

from odoo import fields, http
from odoo.http import request


_logger = logging.getLogger(__name__)

DEFAULT_PARTNER_SLUG = "fonseca-gardens"
DEFAULT_INTENT = "quote"
ALLOWED_INTENTS = {"quote", "consultation", "remote-owner"}
DIRECT_FALLBACK_ROUTE = "/contactus"
CONSULTATION_INTENT = "consultation"
CONSULTATION_ACTIVITY_XMLIDS = ("mail.mail_activity_data_call", "mail.mail_activity_data_todo")
CONSULTATION_ACTIVITY_SUMMARY = "Fonseca consultation callback scheduling"
CONSULTATION_CALLBACK_SLA_HOURS = 4
CONSULTATION_CALLBACK_DEADLINE_DAYS = 1


def _clean(value):
    return (value or "").strip()


def _safe_intent(raw_intent):
    value = _clean(raw_intent).lower()
    return value if value in ALLOWED_INTENTS else DEFAULT_INTENT


def _build_contact_redirect(intent, partner, *, submitted=False, error=False):
    query = {
        "partner": partner or DEFAULT_PARTNER_SLUG,
        "intent": intent,
    }
    if submitted:
        query["submitted"] = "1"
    if error:
        query["submission_error"] = "1"
    return f"{DIRECT_FALLBACK_ROUTE}?{urlencode(query)}"


def _build_description(intent, payload):
    details = []
    if payload.get("route"):
        details.append(f"Route: {payload['route']}")
    if payload.get("service_area"):
        details.append(f"Service area: {payload['service_area']}")
    if payload.get("preferred_timing"):
        details.append(f"Preferred timing: {payload['preferred_timing']}")
    if payload.get("property_size"):
        details.append(f"Property size: {payload['property_size']}")
    if payload.get("visit_frequency"):
        details.append(f"Visit frequency: {payload['visit_frequency']}")
    if payload.get("source"):
        details.append(f"Source: {payload['source']}")
    if intent == CONSULTATION_INTENT:
        details.append("Scheduling mode: manual CRM callback queue")
        details.append(f"Callback SLA target: <= {CONSULTATION_CALLBACK_SLA_HOURS} business hours")

    summary = payload.get("description") or "Website intake submitted without additional notes."
    intent_line = f"Intent: {intent}"
    return "\n".join([intent_line, summary, *details])


def _resolve_activity_type():
    for xmlid in CONSULTATION_ACTIVITY_XMLIDS:
        activity_type = request.env.ref(xmlid, raise_if_not_found=False)
        if activity_type:
            return activity_type.sudo()
    return request.env["mail.activity.type"].sudo().search([], limit=1)


def _resolve_activity_owner(lead):
    if "user_id" in lead._fields and lead.user_id:
        return lead.user_id.id
    if "team_id" in lead._fields and lead.team_id and lead.team_id.user_id:
        return lead.team_id.user_id.id
    admin_user = request.env.ref("base.user_admin", raise_if_not_found=False) or request.env.user
    return admin_user.id


def _schedule_manual_consultation_callback(lead, payload):
    activity_type = _resolve_activity_type()
    if not activity_type:
        return request.env["mail.activity"].sudo().browse()

    model = request.env["ir.model"].sudo().search([("model", "=", "crm.lead")], limit=1)
    if not model:
        return request.env["mail.activity"].sudo().browse()

    note_lines = [
        "Lead submitted via Fonseca website consultation flow.",
        f"Target callback SLA: <= {CONSULTATION_CALLBACK_SLA_HOURS} business hours.",
    ]
    if payload.get("preferred_timing"):
        note_lines.append(f"Preferred timing: {payload['preferred_timing']}")
    if payload.get("service_area"):
        note_lines.append(f"Service area: {payload['service_area']}")
    if payload.get("phone"):
        note_lines.append(f"Phone: {payload['phone']}")
    if payload.get("route"):
        note_lines.append(f"Origin route: {payload['route']}")

    deadline = fields.Date.context_today(lead) + timedelta(days=CONSULTATION_CALLBACK_DEADLINE_DAYS)
    return request.env["mail.activity"].sudo().create(
        {
            "activity_type_id": activity_type.id,
            "res_model_id": model.id,
            "res_id": lead.id,
            "user_id": _resolve_activity_owner(lead),
            "summary": CONSULTATION_ACTIVITY_SUMMARY,
            "note": "\n".join(note_lines),
            "date_deadline": deadline,
        }
    )


def _ensure_tags(tag_names):
    lead_model = request.env["crm.lead"]
    if "tag_ids" not in lead_model._fields:
        return request.env["crm.tag"].sudo().browse()

    tag_model = request.env["crm.tag"].sudo()
    unique_names = [name for name in dict.fromkeys([n for n in tag_names if n])]
    if not unique_names:
        return tag_model.browse()

    existing = tag_model.search([("name", "in", unique_names)])
    existing_names = set(existing.mapped("name"))
    for name in unique_names:
        if name not in existing_names:
            existing |= tag_model.create({"name": name})
    return existing


class FonsecaIntakeController(http.Controller):
    @http.route(
        "/fonseca/intake",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def fonseca_intake(self, **post):
        intent = _safe_intent(post.get("intent"))
        partner = _clean(post.get("partner")) or DEFAULT_PARTNER_SLUG

        payload = {
            "contact_name": _clean(post.get("contact_name")),
            "email_from": _clean(post.get("email_from")),
            "phone": _clean(post.get("phone")),
            "service_area": _clean(post.get("service_area")),
            "preferred_timing": _clean(post.get("preferred_timing")),
            "property_size": _clean(post.get("property_size")),
            "visit_frequency": _clean(post.get("visit_frequency")),
            "route": _clean(post.get("route")),
            "source": _clean(post.get("source")),
            "description": _clean(post.get("description")),
        }

        if not payload["contact_name"] or not payload["email_from"]:
            return request.redirect(_build_contact_redirect(intent, partner, error=True))

        try:
            website = request.website.sudo()
            lead_model = request.env["crm.lead"].sudo()
            lead_values = {
                "name": f"Fonseca {intent.title()} — {payload['contact_name']}",
                "type": "lead",
                "contact_name": payload["contact_name"],
                "email_from": payload["email_from"],
                "phone": payload["phone"],
                "description": _build_description(intent, payload),
            }
            if "partner_name" in lead_model._fields:
                lead_values["partner_name"] = payload["contact_name"]
            if "website" in lead_model._fields:
                lead_values["website"] = website.domain or ""
            if "company_id" in lead_model._fields and website.company_id:
                lead_values["company_id"] = website.company_id.id

            lead = lead_model.create(lead_values)
            tag_names = ["fonseca-gardens", f"intent:{intent}"]
            if intent == CONSULTATION_INTENT:
                tag_names.append("manual-callback-queue")
            tags = _ensure_tags(tag_names)
            if tags:
                lead.write({"tag_ids": [(6, 0, tags.ids)]})
            if intent == CONSULTATION_INTENT:
                try:
                    _schedule_manual_consultation_callback(lead, payload)
                except Exception:  # pylint: disable=broad-except
                    _logger.exception("Failed to create manual callback activity for lead %s", lead.id)
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Failed to create Fonseca CRM lead")
            return request.redirect(_build_contact_redirect(intent, partner, error=True))

        return request.redirect(_build_contact_redirect(intent, partner, submitted=True))
