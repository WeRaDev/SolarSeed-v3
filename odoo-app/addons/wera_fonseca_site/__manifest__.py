{
  "name": "WeRa Fonseca Site Skeleton",
  "summary": "Canonical page skeletons for Fonseca Gardens website rollout",
  "version": "19.0.1.1.0",
  "category": "Website",
  "author": "WeRa Global",
  "license": "LGPL-3",
  "depends": [
    "website",
    "crm"
  ],
  "data": [],
  "assets": {
    "web.assets_frontend": [
      "wera_fonseca_site/static/src/scss/wera_fonseca_site.scss",
      "wera_fonseca_site/static/src/js/wera_fonseca_site.js"
    ]
  },
  "post_init_hook": "post_init_hook",
  "installable": True,
  "application": False
}
