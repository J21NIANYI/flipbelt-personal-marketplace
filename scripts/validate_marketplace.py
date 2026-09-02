#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "flipbelt-product-intelligence-personal"
PLUGIN = ROOT / "plugins" / PLUGIN_NAME
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
GROK_MARKETPLACE = ROOT / ".grok-plugin" / "marketplace.json"
GROK_MANIFEST = PLUGIN / "plugin.json"
PROVENANCE = ROOT / "SOURCE-PROVENANCE.json"
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


def synced_tree_sha256(plugin: Path) -> tuple[int, str]:
    files = sorted(
        (path for area in ("shared", "skills") for path in (plugin / area).rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(plugin).as_posix(),
    )
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(plugin).as_posix()
        file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        digest.update(f"{relative}\0{file_hash}\n".encode())
    return len(files), digest.hexdigest()


def main() -> int:
    errors: list[str] = []
    marketplace = load_json(MARKETPLACE, errors)
    grok_marketplace = load_json(GROK_MARKETPLACE, errors)
    provenance = load_json(PROVENANCE, errors)
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
        if entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_USE"}:
            errors.append("marketplace policy mismatch")
        if entry.get("category") != "Productivity":
            errors.append("marketplace category mismatch")

    manifest = load_json(MANIFEST, errors)
    grok_manifest = load_json(GROK_MANIFEST, errors)
    source_commit = provenance.get("canonical_commit")
    if provenance.get("role") != "downstream-public-distribution":
        errors.append("SOURCE-PROVENANCE.json: invalid distribution role")
    if provenance.get("canonical_repository") != "flipbelt-product-intelligence (local-only)":
        errors.append("SOURCE-PROVENANCE.json: invalid canonical repository")
    if not isinstance(source_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        errors.append("SOURCE-PROVENANCE.json: canonical_commit must be a full Git SHA")
    if provenance.get("canonical_version") != "0.2.1":
        errors.append("SOURCE-PROVENANCE.json: unexpected canonical version")
    if provenance.get("target_plugin") != PLUGIN_NAME:
        errors.append("SOURCE-PROVENANCE.json: target plugin mismatch")
    if provenance.get("synced_paths") != ["shared", "skills"]:
        errors.append("SOURCE-PROVENANCE.json: synced paths mismatch")
    file_count, tree_hash = synced_tree_sha256(PLUGIN)
    if provenance.get("synced_file_count") != file_count:
        errors.append("SOURCE-PROVENANCE.json: synced file count mismatch")
    if provenance.get("synced_tree_sha256") != tree_hash:
        errors.append("SOURCE-PROVENANCE.json: synced tree SHA-256 mismatch")
    if manifest.get("name") != PLUGIN_NAME:
        errors.append("plugin manifest name mismatch")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        errors.append("plugin version must be strict semver")
    if manifest.get("skills") != "./skills/":
        errors.append("plugin skills path must be ./skills/")
    if "mcpServers" in manifest or (PLUGIN / ".mcp.json").exists():
        errors.append("personal plugin must be Skills-only without bundled MCP configuration")
    if "apps" in manifest or (PLUGIN / ".app.json").exists():
        errors.append("personal plugin must not contain a Workspace App reference")

    if grok_marketplace.get("name") != "flipbelt-personal":
        errors.append("Grok marketplace name must be flipbelt-personal")
    if grok_marketplace.get("owner") != {"name": "FlipBelt"}:
        errors.append("Grok marketplace owner mismatch")
    grok_entries = grok_marketplace.get("plugins")
    if not isinstance(grok_entries, list) or len(grok_entries) != 1:
        errors.append("Grok marketplace must contain exactly one plugin")
        grok_entries = []
    if grok_entries:
        grok_entry = grok_entries[0]
        if grok_entry.get("name") != PLUGIN_NAME:
            errors.append("Grok marketplace plugin name mismatch")
        if grok_entry.get("source") != {
            "type": "local",
            "path": f"./plugins/{PLUGIN_NAME}",
        }:
            errors.append("Grok marketplace source must point to the personal plugin")
        if grok_entry.get("category") != "productivity":
            errors.append("Grok marketplace category mismatch")
        if grok_entry.get("version") != version:
            errors.append("Grok marketplace version must match the Codex manifest")
        if grok_entry.get("homepage") != "https://wiki.flipbeltchina.com/mcp-guide":
            errors.append("Grok marketplace homepage mismatch")
        if grok_entry.get("domains") != ["wiki.flipbeltchina.com"]:
            errors.append("Grok marketplace domains mismatch")

    if grok_manifest.get("name") != PLUGIN_NAME:
        errors.append("Grok plugin manifest name mismatch")
    if grok_manifest.get("version") != version:
        errors.append("Grok plugin manifest version must match the Codex manifest")
    if grok_manifest.get("homepage") != "https://wiki.flipbeltchina.com/mcp-guide":
        errors.append("Grok plugin manifest homepage mismatch")
    if any(key in grok_manifest for key in ("skills", "mcpServers", "apps", "interface", "policy")):
        errors.append("Grok plugin manifest must rely on standard discovery without Codex-only fields")

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

    review = PLUGIN / "skills" / "flipbelt-review-specialist"
    for relative in [
        "references/document-review-contract.md",
        "scripts/compare_size_chart.ps1",
        "evals/cases.json",
    ]:
        if not (review / relative).is_file():
            errors.append(f"{PLUGIN_NAME}: missing review parity asset {relative}")
    review_text = (review / "SKILL.md").read_text(encoding="utf-8") if (review / "SKILL.md").is_file() else ""
    for marker in ["PASS", "FAIL", "MISSING", "NO-SOURCE", "search_flipbelt_kb", "get_flipbelt_page", "get_flipbelt_asset"]:
        if marker not in review_text:
            errors.append(f"{PLUGIN_NAME}: Review Specialist missing contract marker {marker}")

    plugin_dirs = {path.name for path in (ROOT / "plugins").iterdir() if path.is_dir()}
    if plugin_dirs != {PLUGIN_NAME}:
        errors.append(f"unexpected plugin directories: {sorted(plugin_dirs)}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", ".tmp"} for part in path.parts) or path.suffix.lower() == ".png":
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

    print("PERSONAL MARKETPLACE VALIDATION PASSED: plugins=1 skills=8 mcp=0 workspace_apps=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
