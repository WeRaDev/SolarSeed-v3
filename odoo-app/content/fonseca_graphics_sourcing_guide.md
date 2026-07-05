# Fonseca Gardens graphics sourcing guide
## Purpose
This guide defines how to source, validate, and prepare visual assets for the Fonseca Gardens website rollout in `wera`, aligned with the source-of-truth model in `odoo-app/content/fonseca_gardens_source_of_truth.json`.
## 1) Asset classes required for launch
1. Brand identity assets
- Primary logo (horizontal lockup)
- Secondary logo (icon/mark only)
- Monochrome variants (dark-on-light, light-on-dark)
2. Portfolio assets
- Before/after project pairs (minimum 5 launch-ready pairs)
- Service-in-action shots (crew, tools, pruning, irrigation checks)
- Garden detail shots (beds, edges, seasonal maintenance outcomes)
3. Trust and conversion assets
- Founder portrait (professional, natural-light)
- Team/operations visual (if available)
- Optional short clips for hero/background and social cross-linking
## 2) File and format standards
### 2.1 Logo assets
- Preferred source format: SVG (master vector)
- Required delivery variants:
  - `logo-primary.svg`
  - `logo-primary-dark.png` (transparent, 2400px wide)
  - `logo-primary-light.png` (transparent, 2400px wide)
  - `logo-mark.svg`
- Exclusion: no raster-only logo as the single source of truth.
### 2.2 Website images
- Master format: JPG (quality 82-88) for photos, PNG only when transparency is required.
- Minimum resolution for hero/cover usage: 2400px on the longest edge.
- Recommended aspect ratios:
  - Hero: 16:9
  - Portfolio card: 4:3
  - Before/after pair: identical framing and ratio
- Color profile: sRGB.
## 3) Portfolio sourcing protocol
### 3.1 Before/after capture requirements
- Capture the “before” image immediately upon arrival.
- Capture the “after” image from the same physical position and focal length.
- Maintain matched framing (same anchor points in scene).
- Keep tools/clutter out of final “after” frame unless intentionally documented.
### 3.2 Required metadata per portfolio pair
Each pair must include:
- `asset_id`
- `location_area` (neighborhood/municipality, not full address)
- `service_type` (maintenance, pruning, irrigation, reset, etc.)
- `capture_date_before`
- `capture_date_after`
- `consent_status` (`granted`, `granted_with_limits`, `denied`)
- `consent_reference` (document/message identifier)
- `photographer`
- `notes` (optional)
### 3.3 Rights and consent policy
- Only publish assets with explicit client permission.
- Never expose full addresses, gate codes, license plates, or personally identifying details.
- If consent is limited, comply with constraints (crop/redact/area-only attribution).
- Do not use stock images as portfolio evidence of completed Fonseca work.
## 4) Sourcing channels by asset class
### 4.1 Logo and brand assets
- Source priority:
  1. Founder-approved vector design files
  2. Professionally commissioned brand package
  3. Temporary text-only lockup (if logo is delayed)
- Launch fallback rule: if final logo is not ready, use a clean wordmark and avoid low-quality placeholders.
### 4.2 Portfolio and examples of gardens
- Primary source: real Fonseca work output with consent.
- Secondary source (for non-portfolio illustrative blocks only): licensed examples with clear attribution and separate labeling as “illustrative.”
- Prohibited: unlabeled third-party gardens presented as Fonseca outcomes.
## 5) Website mapping requirements
Minimum mapping for launch pages:
- `/partners`: one partner spotlight visual + one conversion-supporting visual
- `/partners/fonseca-gardens`:
  - hero image aligned with premium maintenance positioning
  - at least 3 supporting service visuals
  - at least 2 before/after pairs
  - founder/credibility visual section
Each mapped asset must include metadata and consent state before publication.
## 6) Quality control checklist before publish
- Visual quality: sharp focus, exposure balanced, no watermark.
- Brand alignment: professional, practical, trust-building tone.
- Consistency: color/lighting style coherent across page sections.
- Compliance: consent confirmed and sensitive details removed.
- Performance: optimized file sizes (target under 500 KB for standard section images when possible).
## 7) Repository layout recommendation
Use this structure for managed assets:
- `odoo-app/content/fonseca-assets/logo/`
- `odoo-app/content/fonseca-assets/portfolio/before-after/`
- `odoo-app/content/fonseca-assets/portfolio/service/`
- `odoo-app/content/fonseca-assets/founder/`
- `odoo-app/content/fonseca-assets/metadata/portfolio_assets.json`
## 8) Governance and ownership
- Content owner: Fonseca business owner / authorized operator.
- Publish approver: WeRa operator managing TRL rollout.
- Audit requirement: keep metadata and consent references for each published asset revision.
