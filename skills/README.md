# SolarSeed-v3 Skills
This directory contains project-local skills and the project skills registry.

## Inheritance model
- Umbrella skills are defined at `/Users/mikhailananyin/Documents/WeRa Global/skills/`.
- Local registry `skills/registry.yaml` references umbrella skills and may add project-specific extensions.
- Local overrides must not weaken umbrella quality or security guardrails.

## Recommended default flow
1. `repo-orientation`
2. `task-intake`
3. `implementation-plan` (for non-trivial changes)
4. `quality-gate`
5. `release-readiness`
6. `retro-capture`

## Project-specific skill
- `trl-machine-change`: safety-first procedure for TRL machine configuration changes.
