# FlipBelt personal plugin marketplace rules

- This repository is public. Never add credentials, tokens, cookies, private keys, employee data, production configuration, deployment scripts, or product knowledge content.
- Keep exactly one distributed plugin: `flipbelt-product-intelligence-personal`.
- Product and brand facts must come from the authenticated read-only FlipBelt Knowledge MCP.
- The personal plugin must use `.mcp.json` with the unique root `https://wiki.flipbeltchina.com/mcp`; do not add `.app.json` or a Workspace App ID.
- Keep `.agents/plugins/marketplace.json` as the Marketplace source of truth.
- Every plugin must retain `.codex-plugin/plugin.json`; every Skill must retain `SKILL.md`.
- Treat the local-only `flipbelt-product-intelligence` repository as the sole editable source for Product Intelligence `shared/` and `skills/`. This public repository is a downstream distribution and must record the canonical source commit in `SOURCE-PROVENANCE.json`.
- Preserve the personal plugin name, semantic version, root `.mcp.json`, Marketplace manifest, public documentation, and validation adapters. Do not copy from the team Marketplace or develop expert behavior directly here.
- Run `python scripts/validate_marketplace.py`, the official plugin validator, and Skill validation before pushing.
- Real employee OAuth and tool acceptance are performed by the user; automated checks are supporting evidence only.
