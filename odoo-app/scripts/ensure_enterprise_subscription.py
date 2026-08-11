import json
import os


ENTERPRISE_CODE = os.environ.get("ODOO_ENTERPRISE_CODE", "M240830172487565")


def run(env):
    params = env["ir.config_parameter"].sudo()
    key = "database.enterprise_code"
    current = params.get_param(key)
    changed = current != ENTERPRISE_CODE
    if changed:
        params.set_param(key, ENTERPRISE_CODE)

    module_model = env["ir.module.module"].sudo()
    markers = {}
    for module_name in ("web_enterprise", "account_accountant", "web_studio"):
        module = module_model.search([("name", "=", module_name)], limit=1)
        markers[module_name] = {
            "exists": bool(module),
            "state": module.state if module else "missing",
            "latest_version": module.latest_version if module else None,
        }

    env.cr.commit()
    print(
        json.dumps(
            {
                "key": key,
                "previous_value": current,
                "current_value": ENTERPRISE_CODE,
                "changed": changed,
                "module_markers": markers,
            },
            ensure_ascii=False,
        )
    )


run(env)
