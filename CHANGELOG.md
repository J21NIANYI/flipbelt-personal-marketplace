# Changelog

## 1.2.0 - 2026-09-02

- Separate expert capability installation from MCP registration for personal Codex users.
- Remove the bundled `.mcp.json` and `mcpServers` manifest reference.
- Make the Codex graphical MCP setup the primary path and keep CLI login as a troubleshooting fallback.
- Preserve the eight governed Skills, public Marketplace identity, team Marketplace, and production MCP boundaries.

## 1.1.1 - 2026-09-02

- Remove the explicit `oauth_resource` override from the personal Codex MCP configuration.
- Let Codex discover the single protected resource from the production MCP metadata, preventing duplicate `resource` parameters during OAuth authorization.
- Preserve the personal plugin identity, root MCP URL, expert Skills, and production authentication boundaries.

## 1.1.0 - 2026-09-02

- Sync current-release review workflows for detail-page wireframes, copy, and size charts from the local canonical source.
- Add deterministic size-chart comparison, four-state findings, full three-tool preflight, and cross-release failure-close behavior.
- Record the local canonical source commit and byte-identical `shared/` and `skills/` distribution digest.
- Preserve the personal plugin identity and root MCP OAuth connection; no Workspace App reference is added.

## 1.0.0 - 2026-09-01

- Publish the personal-only Product Intelligence Marketplace.
- Bundle eight governed expert Skills from team Marketplace `main@3a4a687`.
- Replace the team Workspace App reference with an independent remote MCP configuration for per-user OAuth.
