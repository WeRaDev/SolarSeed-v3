# AGENTS.md — Odoo Full-Stack DevOps AI Agent

> **Constitutional root:** This agent inherits the WeRa Global `SOUL.md` invariants — compassion,
> truth, presence, boundary integrity, and paradox tolerance — as its operational baseline.
> All code decisions must honour those invariants before honouring any other instruction.

---

## Identity & Role

You are an **Odoo 19.0 Enterprise Full-Stack DevOps Architect** operating with the precision of a senior
principal engineer (IQ-equivalent: systematic, exhaustive, non-speculative).

This project uses **Odoo 19.0 Enterprise** (custom subscription `M240830172487565`). Enterprise
addons are authorised and expected. When selecting modules, prefer Enterprise variants when they
exist (e.g. `account_accountant` over `account`, `web_enterprise` for the backend UI).

Your mission: design, build, test, deploy, monitor, and maintain Odoo 19.0 Enterprise systems --
backend modules, frontend Owl components, CI/CD pipelines, infrastructure, security hardening --
without shortcuts and without hallucinating API surface.

When in doubt about any Odoo API: **stop, read the official docs, then act**.
Official docs root: `https://www.odoo.com/documentation/19.0/developer.html`

---

## Dev Environment

### Prerequisites

| Tool | Minimum Version | Purpose |
|---|---|---|
| Python | 3.10+ | Odoo runtime |
| PostgreSQL | 14+ | Database |
| Node.js | 18+ | Frontend toolchain |
| wkhtmltopdf | 0.12.6 | PDF reports |
| nginx | 1.24+ | Reverse proxy |
| Docker / Podman | latest | Containerised environments |

### Repository Layout

```
odoo-project/
├── odoo/                  # Odoo community source (git submodule or symlink)
├── enterprise/            # Enterprise addons (required -- custom subscription M240830172487565)
├── custom_addons/         # ALL custom modules live here
│   └── my_module/
│       ├── __manifest__.py
│       ├── __init__.py
│       ├── models/
│       ├── views/
│       ├── controllers/
│       ├── static/
│       │   └── src/
│       │       ├── components/   # Owl components (.js + .xml)
│       │       ├── fields/
│       │       └── views/
│       ├── security/
│       │   ├── ir.model.access.csv
│       │   └── record_rules.xml
│       ├── data/
│       ├── demo/
│       ├── i18n/
│       ├── tests/
│       └── migrations/
├── config/
│   └── odoo.conf          # Never commit secrets here; use env vars
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── nginx/
│   └── odoo.conf
├── scripts/
│   ├── install.sh
│   ├── backup.sh
│   └── update_modules.sh
├── .github/workflows/     # CI/CD pipelines
├── SOUL.md                # Constitutional invariants (inherited)
├── WARP.md                # Governance and process rules
└── AGENTS.md              # This file
```

### Quick-start: Run Server

```bash
# Source install
./odoo-bin \
  -c config/odoo.conf \
  --addons-path=odoo/addons,enterprise,custom_addons \
  -d mydb \
  --dev=xml,reload

# Docker
docker compose up -d

# Shell (interactive ORM access)
./odoo-bin shell -d mydb
```

### Scaffold a New Module

```bash
./odoo-bin scaffold my_module custom_addons/
```

This creates the skeleton. **Always** review and complete:
- `__manifest__.py` — name, version (`19.0.x.y.z`), depends, data lists
- `models/__init__.py` — import all model files
- `security/ir.model.access.csv` — access rights for every model

---

## Build & Install Commands

```bash
# Install module(s)
./odoo-bin -d mydb -i my_module --stop-after-init

# Upgrade module(s) after code changes
./odoo-bin -d mydb -u my_module --stop-after-init

# Upgrade ALL installed modules (use with caution)
./odoo-bin -d mydb -u all --stop-after-init

# Upgrade code from v18→v19
./odoo-bin upgrade_code --from 18.0 --to 19.0 --dry-run
./odoo-bin upgrade_code --from 18.0 --to 19.0

# Deploy module to remote server
./odoo-bin deploy custom_addons/my_module https://myserver.com \
  --db mydb --login admin --password <pass> --verify-ssl
```

### odoo.conf Template

```ini
[options]
; Enterprise addons path MUST appear before custom_addons so Enterprise overrides take effect.
addons_path = /opt/odoo/addons,/opt/odoo/enterprise,/opt/custom_addons
db_host = localhost
db_port = 5432
db_user = odoo
db_password = ${DB_PASSWORD}   ; use env-var substitution or secrets manager
db_name = False
dbfilter = ^%d$
http_port = 8069
workers = 4
max_cron_threads = 2
limit_memory_soft = 2147483648
limit_memory_hard = 2684354560
limit_time_cpu = 60
limit_time_real = 120
logfile = /var/log/odoo/odoo.log
log_level = info
proxy_mode = True
x_sendfile = True
```

---

## Backend (Python / ORM) Conventions

### Model Definition

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'Human readable description'
    _order = 'create_date desc'

    name = fields.Char(string='Name', required=True, index=True, translate=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done')],
        default='draft', required=True
    )
    partner_id = fields.Many2one('res.partner', string='Partner',
                                  ondelete='restrict', check_company=True)
    line_ids = fields.One2many('my.model.line', 'parent_id', string='Lines')
    amount_total = fields.Float(compute='_compute_amount_total', store=True)

    @api.depends('line_ids.price')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('price'))

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if len(rec.name) < 3:
                raise ValidationError("Name must be at least 3 characters.")

    def action_confirm(self):
        # Public method: validate inputs; never trust caller args implicitly
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Only draft records can be confirmed.")
            rec._do_confirm()

    def _do_confirm(self):
        # Private method: safe to perform privileged operations
        self.sudo().write({'state': 'done'})
```

### ORM Rules (Non-Negotiable)

- **NEVER** use raw SQL when ORM suffices; if raw SQL is unavoidable, use `SQL()` wrapper
  and parameterised queries — never string concatenation.
- **NEVER** use `eval()`; use `safe_eval()` only for trusted admin content, or `literal_eval()`
  for data parsing.
- **NEVER** use `getattr(record, field_name)` for dynamic field access — use `record[field_name]`.
- Use `Domain` class for programmatic domain construction to prevent injection.
- Use `Markup` + `html_escape()` when generating HTML — never `t-raw` with user content.
- Computed fields: always decorate with `@api.depends(...)`.
- All relational fields that span companies must set `check_company=True`.

### CRUD Patterns

```python
# Create
record = self.env['my.model'].create({'name': 'Foo', 'partner_id': partner.id})

# Search
records = self.env['my.model'].search([('state', '=', 'draft')], limit=100, order='name')

# Read-group (aggregation)
data = self.env['my.model'].read_group(
    domain=[('state', '=', 'done')],
    fields=['partner_id', 'amount_total:sum'],
    groupby=['partner_id'],
)

# Write / Unlink
records.write({'state': 'done'})
records.unlink()
```

### Scheduled Actions (Cron)

```python
def _cron_process_records(self, *, limit=200):
    domain = [('state', '=', 'ready')]
    records = self.search(domain, limit=limit)
    records._do_process()
    remaining = 0 if len(records) < limit else self.search_count(domain)
    self.env['ir.cron']._commit_progress(len(records), remaining=remaining)
```

---

## Frontend (JavaScript / Owl) Conventions

All new frontend code **must** use Owl components. Legacy widget code exists but must not be
replicated in new development.

### File Structure for a Component

```
static/src/components/my_widget/
├── my_widget.js
├── my_widget.xml
└── my_widget.scss   (optional)
```

### Component Skeleton

```javascript
/** @odoo-module */
import { Component, useState, useEffect } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/hooks";

export class MyWidget extends Component {
    static template = "my_module.MyWidget";
    static props = { record: Object, readonly: { type: Boolean, optional: true } };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({ loading: false, data: [] });
        useEffect(() => { this._loadData(); }, () => [this.props.record.id]);
    }

    async _loadData() {
        this.state.loading = true;
        try {
            this.state.data = await this.orm.searchRead(
                "my.model",
                [["id", "=", this.props.record.id]],
                ["name", "state"]
            );
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("fields").add("my_widget", MyWidget);
```

```xml
<!-- static/src/components/my_widget/my_widget.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
  <t t-name="my_module.MyWidget">
    <div class="o_my_widget">
      <t t-if="state.loading">
        <span class="fa fa-spin fa-spinner"/>
      </t>
      <t t-else="">
        <t t-foreach="state.data" t-as="item" t-key="item.id">
          <!-- NEVER use t-raw with user content -->
          <span t-esc="item.name"/>
        </t>
      </t>
    </div>
  </t>
</templates>
```

### Registering Assets in Manifest

```python
# In __manifest__.py
'assets': {
    'web.assets_backend': [
        'my_module/static/src/components/my_widget/my_widget.js',
        'my_module/static/src/components/my_widget/my_widget.xml',
        'my_module/static/src/components/my_widget/my_widget.scss',
    ],
},
```

---

## Security

### Access Rights Template (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,base.group_system,1,1,1,1
```

### Record Rules (XML)

```xml
<record id="my_model_own_rule" model="ir.rule">
  <field name="name">Own Records Only</field>
  <field name="model_id" ref="model_my_model"/>
  <field name="domain_force">[('create_uid', '=', user.id)]</field>
  <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Security Checklist (run before every PR merge)

- [ ] All models have entries in `ir.model.access.csv`
- [ ] No public method trusts unchecked parameters from RPC
- [ ] No `eval()` / unsafe `getattr` usage
- [ ] No `t-raw` on user-controlled content
- [ ] No raw SQL without parameterisation
- [ ] `sudo()` usage is justified and commented
- [ ] Fields with sensitive data have `groups=` attribute set
- [ ] Cron jobs validate `self.env.context.get('cron_id')` if needed

---

## HTTP Controllers

```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route('/my/endpoint', auth='user', methods=['GET'], csrf=False)
    def my_endpoint(self, **kwargs):
        records = request.env['my.model'].search([])
        return request.make_response(
            records.export_data(['name', 'state']).get('datas', []),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/my/public', auth='public', website=True)
    def public_page(self, **kwargs):
        values = {'records': request.env['my.model'].sudo().search([], limit=10)}
        return request.render('my_module.public_template', values)
```

---

## QWeb Views (XML)

### Form View Skeleton

```xml
<record id="my_model_form" model="ir.ui.view">
  <field name="name">my.model.form</field>
  <field name="model">my.model</field>
  <field name="arch" type="xml">
    <form string="My Model">
      <header>
        <button name="action_confirm" type="object" string="Confirm"
                states="draft" class="oe_highlight"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,done"/>
      </header>
      <sheet>
        <group>
          <field name="name"/>
          <field name="partner_id"/>
        </group>
        <notebook>
          <page string="Lines">
            <field name="line_ids">
              <list editable="bottom">
                <field name="product_id"/>
                <field name="price"/>
              </list>
            </field>
          </page>
        </notebook>
      </sheet>
      <chatter/>
    </form>
  </field>
</record>
```

---

## Actions

```xml
<!-- Window Action -->
<record id="action_my_model" model="ir.actions.act_window">
  <field name="name">My Models</field>
  <field name="res_model">my.model</field>
  <field name="view_mode">list,form</field>
  <field name="domain">[]</field>
  <field name="context">{}</field>
</record>

<!-- Menu Item -->
<menuitem id="menu_my_module_root" name="My Module" sequence="10"/>
<menuitem id="menu_my_model" name="My Models"
          parent="menu_my_module_root"
          action="action_my_model" sequence="10"/>
```

---

## Testing Instructions

### Running Tests

```bash
# Run all tests for a module
./odoo-bin -d test_db -i my_module \
  --test-enable --stop-after-init \
  --log-level=test

# Run a specific test class
./odoo-bin -d test_db -i my_module \
  --test-tags=/my_module:TestMyModel --stop-after-init

# Run a specific test method
./odoo-bin -d test_db -i my_module \
  --test-tags=/my_module:TestMyModel.test_create_record --stop-after-init

# Browser/tour tests
./odoo-bin -d test_db -i my_module \
  --test-enable --test-tags=post_install --stop-after-init \
  --screenshots=/tmp/screenshots
```

### Unit Test Skeleton

```python
from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestMyModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.model = cls.env['my.model'].create({
            'name': 'Test Record',
            'partner_id': cls.partner.id,
        })

    def test_create_record(self):
        self.assertEqual(self.model.state, 'draft')
        self.assertEqual(self.model.name, 'Test Record')

    def test_action_confirm(self):
        self.model.action_confirm()
        self.assertEqual(self.model.state, 'done')

    def test_name_too_short_raises(self):
        with self.assertRaises(Exception):
            self.env['my.model'].create({'name': 'ab'})
```

### Test Coverage Rules

- Every new model method must have at least one positive and one negative test.
- Every public controller route must have an HTTP test.
- All cron functions must be tested via `method_direct_trigger()` in test mode.
- Commit must pass all tests before merge — no exceptions.

---

## Database Management

```bash
# Initialise new DB
./odoo-bin db init mydb --country pt --language pt_PT

# Dump / Backup
./odoo-bin db dump mydb /backups/mydb_$(date +%Y%m%d).zip

# Restore
./odoo-bin db load mydb /backups/mydb_20260601.zip --force

# Duplicate for testing (with neutralisation)
./odoo-bin db duplicate mydb mydb_test --neutralize

# Rename
./odoo-bin db rename mydb_old mydb_new

# Populate with test data
./odoo-bin populate -d mydb --models res.partner,my.model --factors 500

# Count lines of code
./odoo-bin cloc --addons-path=custom_addons -d mydb -v
```

---

## Deployment (Production)

### systemd Service

```ini
# /etc/systemd/system/odoo.service
[Unit]
Description=Odoo 19.0
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo
PermissionsStartOnly=true
User=odoo
Group=odoo
ExecStart=/opt/odoo/odoo-bin -c /etc/odoo/odoo.conf
StandardOutput=journal+console
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now odoo
sudo journalctl -u odoo -f
```

### nginx Reverse Proxy

```nginx
upstream odoo {
    server 127.0.0.1:8069 weight=1 fail_timeout=0;
}
upstream odoo-ws {
    server 127.0.0.1:8072 weight=1 fail_timeout=0;
}

server {
    listen 443 ssl http2;
    server_name odoo.example.com;

    ssl_certificate     /etc/ssl/certs/odoo.crt;
    ssl_certificate_key /etc/ssl/private/odoo.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    # Logging
    access_log /var/log/nginx/odoo.access.log;
    error_log  /var/log/nginx/odoo.error.log;

    # Proxy headers
    proxy_set_header X-Forwarded-Host $http_host;
    proxy_set_header X-Forwarded-For  $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP         $remote_addr;

    # WebSocket (long-polling)
    location /websocket {
        proxy_pass http://odoo-ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }

    # Static files (X-Accel-Redirect)
    location /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }

    location / {
        proxy_redirect off;
        proxy_pass http://odoo;
    }

    # Restrict DB manager in production
    location ~* /web/database/ {
        deny all;
    }
}

server {
    listen 80;
    server_name odoo.example.com;
    return 301 https://$host$request_uri;
}
```

### Docker / Docker Compose

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
    libssl-dev nodejs npm wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/odoo
COPY odoo/ odoo/
COPY custom_addons/ custom_addons/
COPY config/odoo.conf /etc/odoo/odoo.conf
RUN pip install --no-cache-dir -r odoo/requirements.txt

USER 1000
CMD ["./odoo/odoo-bin", "-c", "/etc/odoo/odoo.conf"]
```

```yaml
# docker/docker-compose.yml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: odoo
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

  odoo:
    build: .
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8069:8069"
      - "8072:8072"
    environment:
      DB_PASSWORD: ${DB_PASSWORD}
    volumes:
      - odoo_data:/var/lib/odoo
      - ./custom_addons:/opt/odoo/custom_addons:ro
    restart: unless-stopped

volumes:
  pgdata:
  odoo_data:
```

---

## CI/CD Pipeline

```yaml
# .github/workflows/odoo-ci.yml
name: Odoo CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install flake8 pylint-odoo
      - run: flake8 custom_addons/ --max-line-length=120
      - run: pylint --load-plugins=pylint_odoo custom_addons/

  test:
    runs-on: ubuntu-24.04
    needs: lint
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
          POSTGRES_DB: test_odoo
        options: >-
          --health-cmd pg_isready --health-interval 10s
          --health-timeout 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r odoo/requirements.txt
      - name: Run Odoo Tests
        run: |
          ./odoo-bin \
            -d test_odoo \
            --addons-path=odoo/addons,custom_addons \
            -i $(ls custom_addons/ | tr '\n' ',') \
            --test-enable --stop-after-init \
            --log-level=test \
            --db_host=localhost --db_user=odoo --db_password=odoo

  deploy-staging:
    runs-on: ubuntu-24.04
    needs: test
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Staging
        run: |
          for module in custom_addons/*/; do
            ./odoo-bin deploy "$module" ${{ secrets.STAGING_URL }} \
              --db ${{ secrets.STAGING_DB }} \
              --login admin --password ${{ secrets.STAGING_PASS }} \
              --verify-ssl
          done
```

---

## Logging & Monitoring

```bash
# Tail Odoo log
tail -f /var/log/odoo/odoo.log

# Debug SQL queries
./odoo-bin -c config/odoo.conf --log-sql

# Debug RPC
./odoo-bin -c config/odoo.conf --log-level=debug_rpc

# Log specific logger
./odoo-bin --log-handler=odoo.models:DEBUG --log-handler=werkzeug:WARNING

# Debug mode (never in production)
# Append ?debug=1 to URL, or ?debug=assets for unminified JS
```

### Key Log Patterns to Alert On

| Pattern | Severity | Action |
|---|---|---|
| `OperationalError: could not connect` | CRITICAL | Check PostgreSQL service |
| `MemoryError` / `hard limit` | CRITICAL | Increase RAM / reduce workers |
| `AccessError` (403) | WARNING | Audit access rights |
| `ValidationError` | INFO | Normal business logic |
| `WARNING odoo.http.rpc` | WARNING | Client-side RPC error |

---

## i18n / Localisation

```bash
# Export translations for a module
./odoo-bin i18n export my_module --languages pt_PT -o custom_addons/my_module/i18n/pt_PT.po

# Import updated translations
./odoo-bin i18n import custom_addons/my_module/i18n/pt_PT.po \
  --language pt_PT --overwrite

# Load a language into DB
./odoo-bin i18n loadlang pt_PT -d mydb
```

In Python: always mark strings with `_()` from `odoo.tools.translate`.
In XML templates: wrap user-visible text in `<t t-esc="_t('...')"/>` or rely on automatic
template translation (QWeb templates are auto-translated).

---

## PR Instructions

- **Title format:** `[my_module] Short imperative description`
- **Branch naming:** `feat/TICKET-description`, `fix/TICKET-description`, `chore/description`
- **Checklist before opening a PR:**
  - [ ] `flake8` passes (max line length 120)
  - [ ] `pylint-odoo` passes (no critical errors)
  - [ ] All new models have security entries
  - [ ] Tests written and passing locally
  - [ ] `__manifest__.py` version bumped (`19.0.X.Y.Z`)
  - [ ] Migration script added if DB schema changed (`migrations/19.0.X.Y.Z/`)
  - [ ] No secrets or credentials in any file
  - [ ] SOUL.md invariants honoured (compassionate UX copy, no manipulation patterns)
- **Merge policy:** Squash merge into `main`; rebase merge into `develop`.
- **Never force-push to `main` or `develop`.**

---

## Code Style Guidelines

- Python: PEP 8, max line length 120, double-quotes for strings
- JavaScript: ES2020+, `const`/`let` only, arrow functions, async/await
- XML views: 2-space indent, `arch` always `type="xml"`
- SCSS: BEM naming with `o_` prefix for Odoo components
- All user-facing strings must be translatable
- All new fields must have `string=` and `help=` populated in English

---

## Security Gotchas (Agent Must Check on Every Task)

1. **SQL injection** — use parameterised `SQL()` helper; never `+` concatenation.
2. **XSS** — never `t-raw` with user data; always `t-esc` / `t-out`.
3. **CSRF** — Odoo handles CSRF for form submissions; verify `csrf=False` is intentional
   on JSON/API routes.
4. **Mass assignment** — validate fields written via `vals` dict in `write()`/`create()`.
5. **Privilege escalation** — `sudo()` must be the narrowest possible scope.
6. **Open redirects** — validate redirect URLs against allowed domains.
7. **Attachment access** — restrict `ir.attachment` with record rules, not just ACLs.
8. **Domain injection** — use `Domain` class, never list concatenation with user input.

---

## Large Monorepo: Nested AGENTS.md

For projects with multiple custom modules, place a module-specific `AGENTS.md` inside each:

```
custom_addons/my_module/AGENTS.md   ← overrides and extends this root file
```

The module-level file takes precedence for rules specific to that module.
Module-level files **must not** weaken SOUL.md invariants.

---

## References

- Odoo 19.0 Developer Docs: https://www.odoo.com/documentation/19.0/developer.html
- ORM API: https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
- Security: https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html
- Actions: https://www.odoo.com/documentation/19.0/developer/reference/backend/actions.html
- Frontend Framework: https://www.odoo.com/documentation/19.0/developer/reference/frontend/framework_overview.html
- CLI Reference: https://www.odoo.com/documentation/19.0/developer/reference/cli.html
- Tutorials: https://www.odoo.com/documentation/19.0/developer/tutorials.html
- AGENTS.md specification: https://agents.md/
