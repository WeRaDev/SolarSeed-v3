# CLAUDE.md
Compatibility shim for tools that still read `CLAUDE.md`.

## Canonical local instruction file
- Local source of truth: `AGENTS.md`.
- Governance source: `WARP.md`.
- Constitutional source: `SOUL.md`.

## Compatibility rule
- If a tool only reads `CLAUDE.md`, apply all instructions from `AGENTS.md`.
- If any guidance differs, `AGENTS.md` takes precedence.
