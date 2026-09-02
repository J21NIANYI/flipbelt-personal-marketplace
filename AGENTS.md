# FlipBelt personal plugin marketplace rules

- This repository is public. Never add credentials, tokens, cookies, private keys, employee data, production configuration, deployment scripts, or product knowledge content.
- Keep exactly one distributed plugin: `flipbelt-product-intelligence-personal`.
- Product and brand facts must come from the separately configured authenticated read-only FlipBelt Knowledge MCP.
- The personal plugin is Skills-only: do not add `.mcp.json`, `.app.json`, `mcpServers`, or a Workspace App ID. Each user configures the unique root `https://wiki.flipbeltchina.com/mcp` in their client.
- Keep `.agents/plugins/marketplace.json` as the Codex Marketplace source of truth and `.grok-plugin/marketplace.json` as the Grok Build Marketplace source of truth. Both manifests must point to the same `./plugins/flipbelt-product-intelligence-personal` directory.
- Do not create a second Grok-specific plugin directory or bundle host-specific MCP configuration.
- Every plugin must retain `.codex-plugin/plugin.json` for Codex and root `plugin.json` for Grok Build; every Skill must retain `SKILL.md`.
- Treat the local-only `flipbelt-product-intelligence` repository as the sole editable source for Product Intelligence `shared/` and `skills/`. This public repository is a downstream distribution and must record the canonical source commit in `SOURCE-PROVENANCE.json`.
- Preserve the personal plugin name, semantic version, Marketplace manifests, public documentation, and validation adapters. Do not copy from the team Marketplace or develop expert behavior directly here.
- Run `python scripts/validate_marketplace.py`, the Codex official plugin validator, `grok plugin validate`, and Skill validation before pushing.
- Real employee OAuth and tool acceptance are performed by the user; automated checks are supporting evidence only.
