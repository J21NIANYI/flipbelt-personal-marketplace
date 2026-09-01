#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "flipbelt-product-intelligence-personal"
PLUGIN = ROOT / "plugins" / PLUGIN_NAME
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
MCP = PLUGIN / ".mcp.json"
MCP_URL = "https://wiki.flipbeltchina.com/mcp"
EXPECTED_SKILLS = {
    "flipbelt-brand-advisor",
    "flipbelt-chief-advisor",
    "flipbelt-knowledge-foundation",
    "flipbelt-material-expert",
    "flipbelt-product-expert",
    "flipbelt-review-specialist",
    "flipbelt-running-expert",
    "flipbelt-sizing-expert",
}
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SECRET = re.compile(
    r"(?i)(access[_-]?key|client[_-]?secret|private[_-]?key|password)\s*[:=]\s*[\"']?[a-z0-9+/_.-]{12,}"
    r"|bearer\s+[a-z0-9._-]{20,}"
)
ABSOLUTE_PATH = re.compile(r"(?i)(?:[a-z]:\\users\\|/users/|/home/)")


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)}: root must be an object")
        return {}
    return value


def main() -> int:
    errors: list[str] = []
    marketplace = load_json(MARKETPLACE, errors)
    if marketplace.get("name") != "flipbelt-personal":
        errors.append("marketplace name must be flipbelt-personal")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        errors.append("marketplace must contain exactly one plugin")
        entries = []
    if entries:
        entry = entries[0]
        if entry.get("name") != PLUGIN_NAME:
            errors.append("marketplace plugin name mismatch")
        if entry.get("source") != {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"}:
            errors.append("marketplace source must point to the personal plugin")
        if entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
            errors.append("marketplace policy mismatch")
        if entry.get("category") != "Productivity":
            errors.append("marketplace category mismatch")

    manifest = load_json(MANIFEST, errors)
    if manifest.get("name") != PLUGIN_NAME:
        errors.append("plugin manifest name mismatch")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        errors.append("plugin version must be strict semver")
    if manifest.get("skills") != "./skills/":
        errors.append("plugin skills path must be ./skills/")
    if manifest.get("mcpServers") != "./.mcp.json":
        errors.append("plugin must reference ./.mcp.json")
    if "apps" in manifest or (PLUGIN / ".app.json").exists():
        errors.append("personal plugin must not contain a Workspace App reference")

    mcp = load_json(MCP, errors)
    if mcp != {
        "mcpServers": {
            "flipbelt-kb": {
                "type": "http",
                "url": MCP_URL,
                "oauth_resource": MCP_URL,
            }
        }
    }:
        errors.append("personal MCP configuration does not match the unique root contract")

    skill_root = PLUGIN / "skills"
    skills = {path.name for path in skill_root.iterdir() if path.is_dir()} if skill_root.is_dir() else set()
    if skills != EXPECTED_SKILLS:
        errors.append(f"expert Skill set mismatch: {sorted(skills)}")
    for skill_name in sorted(EXPECTED_SKILLS):
        skill_md = skill_root / skill_name / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{skill_name}: missing SKILL.md")
            continue
        text = skill_md.read_text(encoding="utf-8")
        if not re.search(rf"(?m)^name:\s*{re.escape(skill_name)}\s*$", text):
            errors.append(f"{skill_name}: frontmatter name mismatch")

    plugin_dirs = {path.name for path in (ROOT / "plugins").iterdir() if path.is_dir()}
    if plugin_dirs != {PLUGIN_NAME}:
        errors.append(f"unexpected plugin directories: {sorted(plugin_dirs)}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() == ".png":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{path.relative_to(ROOT)}: unexpected binary file")
            continue
        is_validator = path.resolve() == Path(__file__).resolve()
        if not is_validator:
            if SECRET.search(text):
                errors.append(f"{path.relative_to(ROOT)}: possible secret pattern")
            if ABSOLUTE_PATH.search(text):
                errors.append(f"{path.relative_to(ROOT)}: user-specific absolute path")
            if "asdk_app_" in text:
                errors.append(f"{path.relative_to(ROOT)}: Workspace App ID is forbidden")
        if any(line.endswith((" ", "\t")) for line in text.splitlines()):
            errors.append(f"{path.relative_to(ROOT)}: trailing whitespace")
        if re.search(r"(?m)^(<<<<<<< .+|=======|>>>>>>> .+)$", text):
            errors.append(f"{path.relative_to(ROOT)}: merge marker")

    if errors:
        print("PERSONAL MARKETPLACE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PERSONAL MARKETPLACE VALIDATION PASSED: plugins=1 skills=8 mcp=1 workspace_apps=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
